# Progress ledger — 2026-10-22

## Evidence retained privately

Files are in the workspace's ignored `backup/` directory.

- `sdb-inventory-2026-10-22.txt`: normal SDB capabilities and full app inventory.
- `native-sdk-baseline.txt`: UID 901/System foothold, runtime layout, exact device
  firmware/build, kernel 4.1.10, ARMv7 and signed host/launcher hashes.
- `root-attempt-01.stderr`: stock v0.0.9 stopped on unsupported `dotnet --list-runtimes`.
- `root-attempt-02.json`: authenticated UID/GID 0, SMACK User, unchanged original
  account/key files, root staging cleaned. Root retains SMACK restrictions.
- `app-context-original.db`: consistent routing backup, integrity `ok`, SHA-256
  `439ca5e3f7baa7ccc92ebafae3577c636a759d72b2cf0a16a830363eb7051481`.
- `home-route-baseline.json`: stock short Home is row 78, Samsung CSFS;
  separate long-press remote-support shortcut is row 49.
- `launcher-install.log`: normal install completed for package OzQuiet001.
- `home-route-apply.json`: Home target changed and native reload accepted;
  integrity `ok`; root session cleanup/original-hash checks passed.
- `home-key-first-test.json`: native Home event followed by Quiet Home fullscreen
  and empty partial-app ID. Owner then confirmed the six tiles were visible.
- `home-live-rollback-test.json`: native restore/reapply completed; its 3-second
  checks both saw TV Viewer. This does not prove the UI destinations of rollback
  or reapply worked. Report it as an incomplete acceptance test.
- `launcher-diagnostics.json`: later Quiet Home absent, TV Viewer foreground.
- `home-key-recheck.json` and `.stderr`: empty after interruption. Unknown result.
- `boot-install.log`: normal install completed for OzQuietBoot. Its event-routing
  integration was never applied and it was never tested at real boot.

The helper DLL and signed boot package remain installed/staged as described in
RECOVERY.md. Upstream root session cleanup covers its own temporary payloads,
not these explicitly staged project helpers.

## Offline validation completed

- JavaScript syntax check.
- Desktop browser: all six app labels and three Samsung controls; arrow and Back
  focus transitions; no viewport overflow in the checked viewport.
- .NET Core 3.1 native helper/boot relay builds: zero errors/warnings.
- Signed launcher and boot packages installed through normal package paths.
- Transaction apply/restore on the actual database backup reproduced all original
  rows and row IDs in key_filter, managed_app and task_filter.

Desktop tests do not validate Tizen runtime, native key delivery, startup,
streaming playback, DRM/account state or performance.

## Current pause

No TV commands, API queries, remote keys, package operations or reboots while the
owner's father watches. Local process inspection found no outstanding TV-control
commands at the time this ledger was written. Do not retry an interrupted device
operation without inspecting current state in the next authorized maintenance window.

## Narrow diagnostic after the pause

The owner explicitly requested checking the current app to understand NBC access.
One SDK capture read only current fullscreen/partial IDs: TV Viewer, empty overlay.
No keys, launches, installs, reboot or ongoing viewing logger were used. The local
private record is `news-current-app.txt`. This does not identify the channel or
prove how it was opened. All other device interaction remains paused.

## Desktop design pass — no TV contact

Saved the supplied concepts verbatim and implemented the 1.1 list/ambient candidate.
Thirty desktop checks pass; ES5 parsing and two viewport layout checks pass.
No candidate package was installed, no native routing or boot integration changed,
and no device tracing was enabled. On-TV before/after timings remain pending.
Samsung's Virtual Tune-In documentation confirms provider/service-ID targeting
inside its TV UI; no AU8000 NBC appcontrol payload has been verified. See
`design/README.md` and `design/NBC-ROUTING.md`.
