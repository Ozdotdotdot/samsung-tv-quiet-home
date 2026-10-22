#!/usr/bin/env python3
"""Serve only desktop UI/check files. No TV connections or SDK use."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    '/': ('launcher/index.html', 'text/html'),
    '/candidate/': ('launcher/index.html', 'text/html'),
    '/candidate/index.html': ('launcher/index.html', 'text/html'),
    '/tests/desktop.html': ('tests/desktop.html', 'text/html'),
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = ROUTES.get(urlsplit(self.path).path)
        if route is None:
            self.send_error(404)
            return
        data = (ROOT / route[0]).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', route[1] + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', default='127.0.0.1', help='Listen address; defaults to loopback')
    parser.add_argument('--port', type=int, default=8796)
    args = parser.parse_args()
    print(f'UI: http://{args.bind}:{args.port}/candidate/\nChecks: /tests/desktop.html', flush=True)
    HTTPServer((args.bind, args.port), Handler).serve_forever()
