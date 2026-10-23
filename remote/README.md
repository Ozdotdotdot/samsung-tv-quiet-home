# Quiet Remote

A small LAN web remote for the AU8000, built on the TV's own IP remote API. See
[`../docs/REMOTE-WEB.md`](../docs/REMOTE-WEB.md) for the full picture.

```sh
python3 server.py --check    # read-only status (safe; no pairing, no TV contact)
python3 server.py --pair     # one-time: choose "Allow" on the TV, token is saved
python3 server.py            # serve the web remote on 0.0.0.0:8099
```

No root, no TV-side changes, no SDB. The page and API are unauthenticated —
keep them on the home LAN.
