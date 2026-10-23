#!/usr/bin/env python3
"""Local web remote for the Samsung AU8000, over the TV's own LAN remote API.

Serves a small mobile web page on the server (192.168.86.148) and forwards button
presses to the TV's IP remote channel on :8001 (falling back to the self-signed
TLS channel on :8002). This is the same API SmartThings-style controllers use.
It needs no root, makes no TV-side changes and does not use SDB.

The first connection makes the TV show a one-time "Allow" prompt and returns a
token, which is stored so later presses do not prompt again. Nothing connects
until you either run `--pair` or press a button, so starting the server is inert.

Usage:
  python3 server.py --check     # read-only reachability + pairing state, then exit
  python3 server.py --pair      # prompt on the TV now, store the token, then exit
  python3 server.py             # serve the web remote on 0.0.0.0:8099

The page and API are unauthenticated. Keep this on the home LAN; do not port
forward it or expose it publicly.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import socket
import ssl
import struct
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TV_HOST = os.environ.get("TV_HOST", "192.168.86.208")
APP_NAME = os.environ.get("REMOTE_APP_NAME", "Quiet Remote")
BIND_HOST = os.environ.get("REMOTE_BIND", "0.0.0.0")
BIND_PORT = int(os.environ.get("REMOTE_PORT", "8099"))
STATE_DIR = pathlib.Path(
    os.environ.get("REMOTE_STATE_DIR", "/home/ozair/services/samsung-tv-remote")
)
TOKEN_FILE = STATE_DIR / "token"
HERE = pathlib.Path(__file__).resolve().parent

WS_PATH = "/api/v2/channels/samsung.remote.control"

# Button alias -> LAN remote key name (see docs/REMOTE-WEB.md).
KEYS = {
    "power": "KEY_POWER",
    "vol_up": "KEY_VOLUP",
    "vol_down": "KEY_VOLDOWN",
    "mute": "KEY_MUTE",
    "up": "KEY_UP",
    "down": "KEY_DOWN",
    "left": "KEY_LEFT",
    "right": "KEY_RIGHT",
    "enter": "KEY_ENTER",
    "back": "KEY_RETURN",
    "home": "KEY_HOME",
    "exit": "KEY_EXIT",
    "menu": "KEY_MENU",
    "guide": "KEY_GUIDE",
    "info": "KEY_INFO",
    "source": "KEY_SOURCE",
    "ch_up": "KEY_CHUP",
    "ch_down": "KEY_CHDOWN",
    "play": "KEY_PLAY",
    "pause": "KEY_PAUSE",
}


# --- minimal RFC 6455 client (stdout-free, stdlib only) ---------------------


def _recv_exact(sock: socket.socket, count: int) -> bytes:
    data = b""
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise ConnectionError("socket closed by the TV")
        data += chunk
    return data


def _read_frame(sock: socket.socket) -> tuple[int, bytes]:
    header = _recv_exact(sock, 2)
    opcode = header[0] & 0x0F
    length = header[1] & 0x7F
    if length == 126:
        length = struct.unpack(">H", _recv_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack(">Q", _recv_exact(sock, 8))[0]
    masked = bool(header[1] & 0x80)
    mask = _recv_exact(sock, 4) if masked else b""
    payload = _recv_exact(sock, length) if length else b""
    if masked:
        payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
    return opcode, payload


def _encode_frame(payload: bytes, opcode: int = 0x1) -> bytes:
    header = bytearray([0x80 | opcode])
    length = len(payload)
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header += struct.pack(">H", length)
    else:
        header.append(0x80 | 127)
        header += struct.pack(">Q", length)
    mask = os.urandom(4)
    header += mask
    return bytes(header) + bytes(b ^ mask[i % 4] for i, b in enumerate(payload))


class TVRemote:
    """One press per connection: upgrade, wait for ms.channel.connect, send, close."""

    def __init__(self, host: str = TV_HOST, token_file: pathlib.Path = TOKEN_FILE):
        self.host = host
        self.token_file = pathlib.Path(token_file)
        self._lock = threading.Lock()

    def paired(self) -> bool:
        try:
            return bool(self.token_file.read_text(encoding="utf-8").strip())
        except OSError:
            return False

    def _read_token(self) -> str | None:
        try:
            return self.token_file.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None

    def _write_token(self, token: str) -> None:
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(self.token_file.parent, 0o700)
        temporary = self.token_file.with_name(self.token_file.name + ".tmp")
        temporary.write_text(token, encoding="utf-8")
        os.chmod(temporary, 0o600)
        temporary.replace(self.token_file)

    def _forget_token(self) -> None:
        try:
            self.token_file.unlink()
        except OSError:
            pass

    def _open(self, secure: bool, timeout: float) -> socket.socket:
        port = 8002 if secure else 8001
        raw = socket.create_connection((self.host, port), timeout=timeout)
        if not secure:
            return raw
        context = ssl._create_unverified_context()
        return context.wrap_socket(raw, server_hostname=self.host)

    def _handshake(self, sock: socket.socket, port: int, token: str | None) -> None:
        path = WS_PATH + "?name=" + base64.b64encode(APP_NAME.encode()).decode()
        if token:
            path += "&token=" + urllib.parse.quote(token)
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {self.host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            f"Sec-WebSocket-Key: {key}\r\n\r\n"
        )
        sock.sendall(request.encode())
        head = b""
        while not head.endswith(b"\r\n\r\n"):
            chunk = sock.recv(1)
            if not chunk:
                raise ConnectionError("websocket handshake closed early")
            head += chunk
            if len(head) > 8192:
                raise ConnectionError("websocket handshake too large")
        status = head.split(b"\r\n", 1)[0].decode("latin1")
        if " 101" not in status:
            raise ConnectionError("websocket upgrade refused: " + status)

    @staticmethod
    def _frame(key: str) -> str:
        return json.dumps(
            {
                "method": "ms.remote.control",
                "params": {
                    "Cmd": "Click",
                    "DataOfCmd": key,
                    "Option": "false",
                    "TypeOfRemote": "SendRemoteKey",
                },
            }
        )

    def exchange(self, aliases: list[str], timeout: float = 12.0) -> dict:
        """Send one press per alias. Raises on failure. Returns pairing state."""
        frames = [self._frame(KEYS[alias]) for alias in aliases]
        token = self._read_token()
        last_error: Exception | None = None
        with self._lock:
            for secure in (False, True):
                try:
                    sock = self._open(secure, timeout)
                except OSError as error:
                    last_error = error
                    continue
                try:
                    self._handshake(sock, 8002 if secure else 8001, token)
                    sock.settimeout(timeout)
                    connected = False
                    deadline = time.monotonic() + timeout
                    while time.monotonic() < deadline:
                        opcode, payload = _read_frame(sock)
                        if opcode == 0x8:
                            break
                        if opcode == 0x9:
                            sock.sendall(_encode_frame(payload, 0x0A))
                            continue
                        if opcode != 0x1:
                            continue
                        try:
                            message = json.loads(payload)
                        except ValueError:
                            continue
                        event = message.get("event")
                        if event == "ms.channel.connect":
                            new_token = (message.get("data") or {}).get("token")
                            if new_token and new_token != token:
                                token = str(new_token)
                                self._write_token(token)
                            connected = True
                            break
                        if event == "ms.channel.unauthorized":
                            if token:
                                self._forget_token()
                                raise PermissionError(
                                    "stored token rejected; pair again from the page"
                                )
                            raise PermissionError("TV denied the pairing request")
                    if not connected:
                        raise TimeoutError("no connect event from the TV")
                    for frame in frames:
                        sock.sendall(_encode_frame(frame.encode()))
                    if frames:
                        time.sleep(0.25)
                    sock.sendall(_encode_frame(b"", 0x8))
                    return {"ok": True, "paired": bool(token), "secure": secure}
                except (ConnectionError, OSError, TimeoutError, PermissionError) as error:
                    last_error = error
                    if isinstance(error, PermissionError):
                        raise
                    continue
                finally:
                    try:
                        sock.close()
                    except OSError:
                        pass
        raise last_error or ConnectionError("remote API unavailable")


# --- HTTP surface ------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):
    server_version = "QuietRemote/1.0"
    protocol_version = "HTTP/1.1"
    remote: TVRemote

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body, content_type: str = "application/json") -> None:
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _status(self) -> dict:
        result = {"reachable": False, "paired": self.remote.paired()}
        try:
            with urllib.request.urlopen(
                f"http://{TV_HOST}:8001/api/v2/", timeout=3
            ) as response:
                device = json.loads(response.read()).get("device", {})
            result.update(
                reachable=True,
                power=device.get("PowerState"),
                name=device.get("name"),
                model=device.get("modelName"),
                ip=device.get("ip"),
            )
        except Exception as error:  # noqa: BLE001 - surfaced to the page
            result["error"] = str(error)
        return result

    def do_GET(self) -> None:  # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/api/status":
            self._send(200, self._status())
        elif path == "/api/keys":
            self._send(200, {"keys": sorted(KEYS)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, TypeError):
            self._send(400, {"error": "invalid request body"})
            return
        if path == "/api/key":
            alias = payload.get("key")
            if alias not in KEYS:
                self._send(400, {"error": "unknown key"})
                return
            try:
                self._send(200, self.remote.exchange([alias], timeout=12.0))
            except PermissionError as error:
                self._send(403, {"error": str(error), "paired": self.remote.paired()})
            except Exception as error:  # noqa: BLE001
                self._send(502, {"error": str(error), "paired": self.remote.paired()})
        elif path == "/api/pair":
            try:
                self._send(200, self.remote.exchange([], timeout=90.0))
            except PermissionError as error:
                self._send(403, {"error": str(error)})
            except Exception as error:  # noqa: BLE001
                self._send(502, {"error": str(error)})
        else:
            self._send(404, {"error": "not found"})


def main() -> int:
    parser = argparse.ArgumentParser(description="Samsung AU8000 LAN web remote")
    parser.add_argument("--pair", action="store_true", help="pair now and store the token")
    parser.add_argument("--check", action="store_true", help="read-only status, then exit")
    parser.add_argument("--host", default=BIND_HOST)
    parser.add_argument("--port", type=int, default=BIND_PORT)
    args = parser.parse_args()

    remote = TVRemote()

    if args.check:
        status = {
            "paired": remote.paired(),
            "token_file": str(remote.token_file),
        }
        try:
            with urllib.request.urlopen(f"http://{TV_HOST}:8001/api/v2/", timeout=3) as response:
                status["device"] = json.loads(response.read()).get("device", {})
            status["reachable"] = True
        except Exception as error:  # noqa: BLE001
            status["reachable"] = False
            status["error"] = str(error)
        print(json.dumps(status, indent=2))
        return 0

    if args.pair:
        print("Waiting for the TV to show an Allow prompt ...")
        try:
            result = remote.exchange([], timeout=90.0)
        except Exception as error:  # noqa: BLE001
            print("Pairing failed:", error)
            return 1
        print("Paired:", json.dumps(result))
        return 0

    Handler.remote = remote
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    print(f"Quiet Remote serving on http://{args.host}:{args.port}/  (TV {TV_HOST})")
    print(f"paired={remote.paired()}  token={remote.token_file}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
