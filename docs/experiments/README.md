# Voice startup experiment — not a recommended debloat recipe

Owner confirmed no microphone searches, voice assistants or spoken accessibility
features are used. Text-to-speech, ordinary remote input and streaming/news
components were excluded from the test.

## Observed results on AU8000 T-KSU2EAKUC-2301.1

- Saved app-disable, onboot and autorestart fields and declared dependency rows.
  The registry has only seven dependency rows overall; empty reverse dependency
  results are weak evidence, not a complete runtime dependency analysis.
- `pkgcmd -D -t app -n APP_ID --global` rejected all three targets with exit 25,
  output mentioning error -2/-999. The affected IDs were ondevice-voice,
  bixby-prov and bixbycapsuleviewer under com.samsung.tv. Their app_support_disable
  fields are false. That might relate to rejection; it is not a proven explanation.
- Activation attempts also returned errors. Independent readback confirmed the
  original app-disable fields stayed false. The local harness's generic 'restore
  not confirmed' message refers to rejected activation command returns; the
  original flag values themselves were subsequently confirmed.
- Native `app_launcher -k com.samsung.tv.bixbycapsuleviewer` returned success and
  subsequent running-app reads no longer listed that viewer. It remains installed
  and enabled. It can be launched again; no persistent suppression was installed.
- In a guarded SQLite transaction, changed only app_onboot and app_autorestart
  from true to false for com.samsung.tv.ondevice-voice and com.samsung.tv.bixby-prov.
  Readback confirmed the changes. Both native stop calls succeeded, but both apps
  immediately returned under new PIDs. Therefore changing those two registry
  fields does not establish runtime suppression on this firmware.
- Restored all four fields to true with a guarded transaction and verified them.
  No app-disable field or other package field was directly changed.
- Orderly `app_launcher -t` also returned success for both apps, but both returned.
  Process exit alone is not an effective optimization here.
- Copied four relevant systemd unit definitions. On-device voice has a path unit
  watching /tmp/voice_app_ready and a firmware-provided exclusion marker path.
  The voice-app path/service use their own trigger and exclusion marker. These
  are launch paths independent of the package flags. No markers, masks, unit
  enable states or trigger files were modified in this pass. The observations
  do not attribute each observed respawn to one specific caller; cached app
  metadata or other requesters remain possible.

The SQL files alongside this note preserve the exact narrow field changes for
review and rollback documentation. They are NOT a working disable solution and
must not be offered as a supported optimization. Local in-memory SQLite checks
verified apply/restore round-trip preservation and rejection/rollback when the
expected source state differed. Actual device readback verified restoration.

## Offline artifact investigation

Using the reverse-engineer-anything skill, copied /usr/bin/amd and
/usr/lib/libamd.so.1 to ignored .local/runtime-analysis. REA opened their ARM ELF
identities. The server is connected, but native analysis providers are unavailable:
Ghidra/Java unconfigured or missing, Hopper missing, IDA/Kuna unconfigured. No
software was installed or MCP configuration changed.

Artifact SHA-256 values:

- amd: 41305eca54cc8470c160b70110b4426cbc77abe611e087aa9cda58a60d743063
- libamd.so.1: de9f61982be445de51479d3c419dc8ca8236ed5a80385990b8380686af8cdb43

REA objdump static-symbol query evidence:
ev_9107c263b5bbbacd9dd686927cbd7d436e8769ada5dfce4aabc722be423454cf
reported no static symbols with its selected objdump operation. Separate ordinary
shell readelf inspection DID find dynamic symbols, including autorestart queries
and AppInfoManager interfaces. Shell strings found restart-related diagnostics.
Those are clues, not decompiled control flow or runtime caller attribution.
Native sessions were closed. Firmware files and raw evidence are not published.

## Current state and next question

All tested registry/startup flags restored. Bixby viewer closed; on-device voice
and Bixby provider running again. Netflix stayed running. No performance benefit
claimed, no reboot performed and no DNS changes made.

Before further suppression, establish a supported disable/control path and how
live app metadata is refreshed, inspect the actual relaunch triggers, and account
for firmware service-stop deadlines. Do not restart the central app manager or
blindly edit all matching package rows. Once a small group can actually stay
stopped, repeat performance and playback/store/news acceptance checks.
