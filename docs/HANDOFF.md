# Handoff — 2026-10-22 ~20:50 (TV local time)

Read this first, then `LEAN-PROFILE.md` (applied changes + rollback) and
`RECOVERY.md` (Home routing / launcher recovery). `docs/design/NBC-ROUTING.md`
now contains the verified TV Plus launch contract.

## Stop-point state

- **Firmware `T-KSU2EAKUC-2310.0`** (build TIZEN-TRUNK2021-KantSU2e-HOTFIX-
  RELEASE_20260721.1). Everything before 19:35 today was done on `2301.1`.
- **Root re-verified on 2310.0**: `scripts/tv-root.py` `id` → uid 0,
  `system_files_unchanged: true`. The helper works unchanged.
- **Native pins moved to 2310.0**: `native/OwnerPackageControl/Program.cs` and
  `boot/Program.cs` now accept `Version=T-KSU2EAKUC-2310.0;`; helper
  `WaitForExit` raised to 60 s because this firmware is much slower. Helper DLL
  rebuilt and staged in `backup/` (sha256 `6398ddfc…9fdb`). The **boot tpk was
  not rebuilt**; `boot/Program.cs` change is source-only until then.
- **Quiet Home 1.1.0 is installed and working** (`OzQuiet001.Home`,
  `/opt/usr/apps/OzQuiet001/res/wgt/index.html` 12 882 B). It is the "The List"
  + ambient clock build. `Quiet-Home-1.0.0.wgt` in `backup/` is the six-tile
  rollback.
- **Automatic firmware updates are blocked** by `/mnt/backup/OS_UPGRADE_FLAG`
  plus `swu-auto-upgrade.service`/`.timer` stopped and disabled. The flag is a
  blunt instrument: it may also block a deliberate USB update until removed.
- **Remote reboot works**: `systemctl reboot` fails (`reboot.target` not
  found); the direct `reboot` syscall through `scripts/tv-root.py` works.
  Reboot tested at 19:57 → boot id `df6d576e-4f4d-4d07-ae1e-82fedd281fe2`.

## Post-reboot verification (read-only, 20:50, uptime ~49 min)

| Check | Result |
|---|---|
| Reconciler applied new boot | yes — `state.json` `df6d576e…`, 20:01:37 |
| `contents-recognition-service` | inactive; runtime-mask symlink present |
| `media-analytics-service` | `failed`/`masked-runtime`, no process (see note) |
| context-aware service + agent | inactive; boot markers present |
| 10 cleanup `app_disable` flags | all `true` |
| cleanup processes | none running |
| `/mnt/backup/OS_UPGRADE_FLAG` | present |
| `swu-auto-upgrade` | inactive, `disabled` |
| Quiet Home 1.1.0 files | present (index 12 882 B, config 960 B) |

`media-analytics-service` reports `failed` because it starts at boot and the
reconciler only masks/stops it ~2–5 min later. `masked-runtime` prevents any
restart; no process is running. This is the designed behaviour, not a leak.

The user-level reconciler lives on the server (192.168.86.148):
`/home/ozair/services/samsung-tv-maintenance/reconcile.py`,
`samsung-tv-reconcile.timer` (`OnBootSec=2min`, then every 5 min). It logged
`boot id unavailable` at 20:29 and 20:35 while SDB was saturated by capture
work, then retried successfully; transient contention is expected.

Load average is still ~33–38. On this kernel that is mostly blocked tasks, not
CPU saturation; the TV is usable.

## Launcher buttons — owner-reported defect (open)

Owner reports, from the installed 1.1.0 launcher:

- YouTube / Netflix / Prime / Disney+ / Jellyfin: work.
- **Samsung Home** and **Samsung Apps**: work (owner confirmed).
- **TV Settings**: nothing happens.
- **NBC News** and **Live news channels**: nothing happens.

### TV Settings root cause

`com.samsung.tv.coba.setting` is **not a launchable UI app**. Its manifest exec
is `Com.Samsung.TV.CoBA.Setting.dll`, but that assembly is a 3.5 KB stub with
only assembly metadata and **no entry point**, and the manifest declares
`support-fs-external-component=true`. It is a CoBA component loaded into a host,
not a screen. The launch is accepted and the process exits immediately, which is
why the UI shows no error.

The actual menu/settings UI is **`org.tizen.menu`**
(`/usr/apps/org.tizen.menu/bin/menu`, capp, `nodisplay=true`). It is a
long-running process (pid 336) and `org.tizen.homesetting` logs
`launch menu app_control` before opening it. A plain
`tizen.application.launch('org.tizen.menu')` is the candidate fix and still
needs an on-device confirmation.

Do **not** use `com.samsung.tv.coba.setting`.

### NBC / live news root cause

Both buttons currently call `tizen.application.launch` on
`com.samsung.tv.tvPlusDeeplinker`. That app is `nodisplay=true` and its
`OnAppControlReceived` **exits unless the app-control carries a `PAYLOAD`
extra**; an ordinary launch therefore does nothing.

Decompiled contract (ILSpy 8.2 in the dotnet/sdk:6.0 container;
sources in ignored `backup/re/deeplinker-src`):

1. Extra `PAYLOAD` is mandatory. `type=CH` means PAYLOAD is
   `"<provider_id>_<service_id>"` (split on the first `_`).
2. Otherwise PAYLOAD is JSON with
   `values.tune_data.{provider_id,service_id}` or `values.deeplink_data`,
   plus optional `type` (`detail`/`CH`), `request_ready`, `callerid`.
3. It resolves provider/service to a **TCServiceId** through the TV Plus API,
   then launches `org.tizen.tv-viewer` with operation
   `http://tizen.org/appcontrol/operation/view` and extra `svcid=<TCServiceId>`.
4. The standalone TV Plus app `HEPsqFNie0.tvplusstandalone` is **not installed**,
   so `IsTVPlusStandaloneSupported()` is false and the TV-service/HbbTV path is
   used.

So the launcher can bypass the deeplinker entirely and call
`tizen.application.launchAppControl` on `org.tizen.tv-viewer` with
`svcid=<TCServiceId>` — once the blueprint has that ID.

### Capture attempt and result

While the owner tapped NBC News in Samsung Home, we ran a 150 s `/proc` watcher
plus foreground polling. The foreground changed to `org.tizen.tv-viewer` and NBC
played, but **no new deeplinker/TV Plus process was created**: the stock Home
tunes through the already-running native TV service. `dlogutil` yields only its
2-line banner — logging is compiled out. Settings likewise reused the
long-running `org.tizen.menu` (pid 336). No app-control extras were observable
from process command lines.

## Next step for NBC (ranked, bounded)

1. **Read the current channel from the launcher.** Add a one-shot diagnostic to
   Quiet Home: on `visibilitychange`/resume call Samsung's TV web API
   `webapis.tv.channel.getCurrentChannel()`, store
   `{name, number, serviceId}` in `localStorage`, read it back over SDB from
   `/opt/usr/home/owner/apps_rw/OzQuiet001/data/Local Storage`. The owner then
   opens NBC once and returns Home. Confirm whether `tv.channel` privilege is
   needed in `launcher/config.xml`. Then test `svcid=<serviceId>` with
   `launchAppControl` to `org.tizen.tv-viewer`.
2. **D-Bus TV service**: `com.samsung.IServiceNavigation` exposes
   `MethodCall(int functionCode, int inDataSize, byte[] inDataBuffer)`.
   Function codes and struct layout are in `Tizen.TV.Broadcast.TVService.dll`
   on the TV; decompile to query the current service (and possibly set it).
3. **`svcid=1114`** is only a public US TV Plus lineup *channel number*, not a
   verified `TCServiceId`. Do not ship it without a panel test.
4. Frida/ptrace on `tv-viewer` is a last resort; ask the owner first. REA's
   Frida tools are available but have not been used on this TV.

Do not ship guessed IDs. Keep the menu label honest if a route cannot be
verified.

## Other open items

1. **Startup app** — Quiet Home is still not wired to boot. `boot/Program.cs`
   is pinned to 2310.0 but the tpk was not rebuilt; the previously installed
   `OzQuietBoot.Start` was never integrated or tested at cold boot. Lead:
   owner `systemd --user` units under `/opt/usr/home/owner/.config/systemd/user`
   or `memory/system/boot_done`.
2. **Slint test** (`experiments/slint-hello/README.md`) — never run on the TV.
3. **TV Plus / NBC visual re-check after cleanup** — owner reached NBC through
   Samsung Home today and it played, so disabling `content-tiles-provider` did
   not remove that tile. Treat this as a functional observation, not a full
   acceptance pass.
4. **Home key after reboot** — re-verify `input_keyevent XF86Home` routes to
   `OzQuiet001.Home`; the pre-reboot test passed.
5. Reconciler transient `boot id unavailable` under heavy SDB — retries; no
   action unless it becomes persistent.
6. `backup/signing-password` does **not** open `quiet-home.p12`; the working
   credential is `backup/profiles.xml`. Do not print secrets.

## Safety rules carried forward

- Check `vconftool get -t string memory/appfw/current_fullscreen_appid`
  (read-only) before acting; don't touch the TV while the owner's father watches.
- Preserve streaming, TV Plus / Live TV / NBC News, app store, accounts, DRM,
  network, remote input, TTS. DNS filtering stays paused. No package uninstalls.
- Save original state before each change; verify by readback; commit results.
- The owner's father is watching TV as of this handoff. No launches, reboots or
  writes without a new go-ahead.

## Reference

- TV `192.168.86.208`, SDB `192.168.86.208:26101`; server `192.168.86.148`.
- Root wrapper: `TV_HOST=192.168.86.208 TV_CALLBACK_HOST=192.168.86.148
  TIZEN_SDB=$PWD/tools/tizen-tools/sdb python3 scripts/tv-root.py '<cmd>'`.
- Read-only SDB helper with a long capture window: `/tmp/tvsdk-long.py`
  (`TV_HOST`, `CAPTURE_TIMEOUT`, dot-source a pushed script under
  `/home/owner/share/tmp/sdk_tools/`). Executing pushed scripts directly is
  blocked ("file is NOT signed"); dot-source them instead.
- Reboot: `reboot` syscall via the root wrapper.
- App flags: `sqlite3 -readonly -csv /opt/dbspace/.pkgmgr_parser.db
  "SELECT app_id,app_disable FROM package_app_info WHERE app_id IN (...);"`.
- Packaging: delete stale `launcher/author-signature.xml`/`signature1.xml`, run
  `scripts/package.sh` in the `ghcr.io/georift/install-jellyfin-tizen` container,
  push the wgt to `/home/owner/share/tmp/sdk_tools/`, then
  `0 appinstall wgt <file>` (SDB `install` alone does not install).
- Decompile TV .NET: `dotnet tool install -g ilspycmd --version 8.2.0.7535` in
  `mcr.microsoft.com/dotnet/sdk:6.0`, `ilspycmd -p -o <out> <dll>`.
- REA is available and is the preferred tool for native binaries; the .NET work
  above was done with ILSpy before REA was exercised.
