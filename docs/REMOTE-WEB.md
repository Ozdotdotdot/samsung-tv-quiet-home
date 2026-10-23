# Quiet Remote — LAN web remote for the AU8000

Status: built 2026-10-22. **Not yet paired or exercised on the TV.** Starting
the service is inert; it makes no TV contact until you pair or press a button.

## What it is

A single Python 3 (stdlib-only) service on the server (`192.168.86.148`) that
serves a small mobile web page and forwards button presses to the TV's own IP
remote channel. This is the same API SmartThings-style controllers and the HA
`ha-samsungtv-smart` component use — not the root path.

Why this path first:

- **No root, no SDB, no TV-side change.** It runs entirely on the server and
  talks to the TV over the LAN.
- The TV advertises it: `backup/tv-api-2026-10-22.json` shows
  `TokenAuthSupport: true`, `remote_available: true`, `remote_fourDirections:
  true`, `remote_touchPad: true`, `uri: http://192.168.86.208:8001/api/v2/`.
- The websocket contract is already proven in the vendored upstream client
  `tools/vetro/app/service/samsung-remote.js` (Vetro, tested on a Q80A).

The root path (`/usr/bin/input_keyevent`, `scripts/tv-root.py`) remains available
as a fallback for keys the LAN API does not carry, and for remapping physical
buttons. It is not used by this service.

## Files

| Path | Role |
| --- | --- |
| `remote/server.py` | HTTP server + minimal RFC 6455 client for the TV channel |
| `remote/index.html` | The web remote UI |
| `remote/samsung-tv-remote.service` | systemd **user** unit (installed copy lives in `~/.config/systemd/user/`) |
| `/home/ozair/services/samsung-tv-remote/token` | Saved pairing token, mode `0600` (outside the repo) |

## Run

```sh
python3 remote/server.py --check          # read-only: reachable + paired + device info
python3 remote/server.py --pair           # one-time pairing (see below)
python3 remote/server.py                  # serve on 0.0.0.0:8099
```

Environment: `TV_HOST` (default `192.168.86.208`), `REMOTE_BIND` (default
`0.0.0.0`), `REMOTE_PORT` (default `8099`), `REMOTE_STATE_DIR`.

Installed as a user service:

```sh
systemctl --user enable --now samsung-tv-remote.service
systemctl --user status samsung-tv-remote.service
```

Then open `http://192.168.86.148:8099/` from a phone or computer on the LAN.

## Pairing (one time)

The first connection makes the TV show an **Allow** prompt. The TV returns a
token, which is stored so later presses do not prompt again.

- Run `--pair`, or just press a button on the page.
- The token is what makes this silent afterwards; deleting
  `/home/ozair/services/samsung-tv-remote/token` forces re-pairing.
- If the TV rejects a stored token, the server deletes it and reports
  `stored token rejected; pair again`.

Pairing pops a prompt on screen, so **do it when nobody is watching**.

## Key map

Presses go through `ms.remote.control` / `SendRemoteKey`, one connection per
press (~1 s on this TV). The UI exposes power, volume/mute, D-pad + OK, Back and
Home; the API also whitelists Exit, Menu, Guide, Info, Source, channel and
playback keys.

| UI control | LAN key | Verified on this AU8000 |
| --- | --- | --- |
| Power | `KEY_POWER` | ✗ candidate |
| Vol + / − | `KEY_VOLUP` / `KEY_VOLDOWN` | ✗ candidate |
| Mute | `KEY_MUTE` | ✗ candidate |
| Up / Down / Left / Right | `KEY_UP/DOWN/LEFT/RIGHT` | ✗ candidate |
| OK | `KEY_ENTER` | ✗ candidate |
| Back | `KEY_RETURN` | ✗ candidate |
| Home | `KEY_HOME` | ✗ candidate |
| Exit | `KEY_EXIT` | ✗ candidate |

The names come from `tools/ha-samsungtv-smart-fab/docs/Key_codes.md`; that
document warns the accepted set varies by model, so the first real session should
confirm each button before this is treated as done. On 2016+ sets `KEY_POWER` is
the on/off toggle (not `KEY_POWEROFF`).

## Security

Plain HTTP, **no authentication**. Anyone on the LAN can power the TV off or
press keys. Keep it on the home network; never port-forward it. To take it off
the LAN, run with `REMOTE_BIND=127.0.0.1` and reach it via
`ssh -L 8099:127.0.0.1:8099 ozair@192.168.86.148`.

## Wake from sleep (separate, still open)

Not part of this service yet, and **unproven on this TV**.

- The TV is on **Wi-Fi** (`networkType: wireless`) and its Wi-Fi MAC is
  `D0:C2:4E:57:34:74`, so a Wake-on-LAN magic packet is testable.
- WoL is much more reliable over Ethernet; Samsung Wi-Fi WoWLAN support is
  inconsistent. Samsung's LAN websocket `KEY_POWER` powers off while on, but
  waking a fully-asleep set is model-dependent (the 2024/2025 Frames dropped WoL
  entirely — see `tools/ha-samsungtv-smart-fab/`).
- There is likely a network-standby / "Wake on LAN" setting to enable first.
- Bounded test when the TV is free: enable that setting, put the TV into standby,
  send a magic packet to `D0:C2:4E:57:34:74`, and check whether
  `http://192.168.86.208:8001/api/v2/` still answers. If it does, the websocket
  may be able to power it on from standby.
- Fallbacks if WoL fails: HDMI-CEC from an always-on source, or SmartThings.

## Not done yet

- Real pairing + a button-by-button pass (needs the TV free).
- Longer-press (hold) and repeat behaviour, if wanted.
- One-tap app launch via `ms.channel.emit` `ed.apps.launch` (the frame format is
  in `tools/vetro/app/service/samsung-remote.js`).
