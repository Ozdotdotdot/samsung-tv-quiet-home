# AU8000 lean profile — maintenance in progress, 2026-10-22

Applies only to the inspected T-KSU2EAKUC-2301.1 firmware. The owner previously
reported 2391.1 from the UI; the firmware-file discrepancy remains documented.
No firmware flashing, overclocking, governor changes, cache wipes or DNS filtering.
No packages are uninstalled. Keep streaming, TV Plus/news/viewer, store, accounts,
DRM, media, network/time, ordinary remote/input and text-to-speech intact.

## Working control and recovery

Package commands now run as the actual TV owner UID 5001 using the fixed-target
OwnerPackageControl helper. Standard owner-scoped disable succeeded even though
app_support_disable fields were false. Earlier rejection cannot be attributed to
that field. Actual pkgcmd ARM instruction inspection found a comparison of the
requested UID against getuid before its Invalid uid path. The older upstream
Tizen source explains owner-scoped global-app operations but is not this firmware.

The helper drops its own supplementary groups and switches real/effective/saved
GID and UID before starting pkgcmd. Root agents are temporary and clean up after
each operation. No privileged daemon, background dashboard or poller was installed.
Original global passwd/public.pem hashes are checked by the existing root wrapper.
Native binary copies and raw logs remain ignored/private.

A Bixby viewer enable -> readback false -> disable -> readback true round trip
verified the package rollback mechanism. All listed app flags started false
(enabled) before this maintenance work. For those apps, exact flag rollback is
OwnerPackageControl enable APP_ID, followed by registry readback. Startup fields
have their original values; previous experimental startup edits were restored.

## Voice group — applied and owner accepted

15 app records disabled through pkgcmd:

- com.samsung.tv.bixbycapsuleviewer
- com.samsung.tv.ondevice-voice
- com.samsung.tv.bixby-prov
- com.samsung.tv.bixby-context-client
- com.samsung.tv.mybixby
- com.samsung.tv.wakeup-engine-bixby
- com.samsung.tv.wakeup-engine-alexa
- com.samsung.tv.alexa-client
- com.samsung.tv.alexa-fullscreen-app
- com.samsung.tv.voiceassistant-music
- com.samsung.tv.cnvoice-assistant
- org.tizen.voice-app-service
- org.tizen.voice-app
- org.tizen.voice-client
- com.samsung.tv.vif

Six previously running voice processes were absent after applying the group.
Owner confirmed Netflix navigation, video playback and volume still work, with
no explicitly noticeable speed improvement. This is a functional acceptance of
those operations, not a complete test of all preserved apps.

## Recognition group — app flags applied

- com.samsung.tv.acr
- com.samsung.tv.canalysis-service
- com.samsung.tv.vision-data-recognition-service
- com.samsung.tv.contents-recognition-dbmgr

All four disabled flags read back true; ACR process no longer listed.

Directly systemd-launched daemons were then handled with the firmware's own
`ConditionPathExists=!` exclusion markers (empty files, created only if absent):

- `/opt/usr/share/systemd/system/canalysis-daemon` (canalysis-service)
- `/opt/usr/share/systemd/system/vision-data-recognition-service`
- `/opt/usr/share/systemd/system/com.samsung.tv.ondevice-voice`
- `/opt/usr/share/systemd/system/org.tizen.voice-app`

`contents-recognition-service.service` has no marker condition, so it is masked
with `systemctl mask --runtime` (symlink in /run/systemd/system). **That mask is
lost on reboot**; the daemon may return after a power cycle.

The root command's callback timed out at 45 s because canalysis took its full
90 s stop window, so no JSON output was captured. A later read-only check confirmed
every step completed: four markers present, runtime mask present, canalysis and
media-analytics `failed` (killed after stop timeout, not restarting), the other
recognition units and the voice/recognition `.path` watchers inactive.

## Advertising group — applied

App flags disabled through OwnerPackageControl (helper restaged with the expanded
allowlist; TV DLL sha256 d0112dd9…e40 matches the local build):

- com.samsung.tv.targeted-ad-service
- com.samsung.tv.pisa-service
- com.samsung.tv.adagent-service
- org.tizen.pisa-control-service

All four read back `app_disable=true`; targeted-ad-service process no longer
listed. Created marker `/opt/usr/share/systemd/system/pisa-service`, which both
`adagent-service.service` and `pisa-service.service` check, then stopped both
units. Both are down; `pisa-service.path` can still trigger pisa, but the marker
condition blocks start. The Samsung Home advertising-resource package was not
touched.

## Snapshot after recognition + advertising groups (Quiet Home foreground)

| | Before privacy groups | After |
|---|---|---|
| MemAvailable | ~271 MB | ~343 MB |
| SwapFree (of 789 MB) | ~94 MB | ~151 MB |
| Tasks | 1543 | 1452 |

Single uncontrolled samples (Netflix still resident in background); not a speed
claim. Load average stays ~32, which on this kernel reflects blocked tasks rather
than CPU saturation.

## Owner acceptance after recognition + advertising groups

Owner confirmed: Netflix plays; scrolling "maybe feels better" (subjective, not
measured); NBC News via TV Plus works; Samsung app store opens. Ad-service
removal did not break TV Plus playback.

## Rollback for recognition + advertising groups

As root (via scripts/tv-root.py with the namespace prefix used in lean-voice-apply):

```
rm /opt/usr/share/systemd/system/{canalysis-daemon,vision-data-recognition-service,com.samsung.tv.ondevice-voice,org.tizen.voice-app,pisa-service}
systemctl unmask --runtime contents-recognition-service.service
OwnerPackageControl.dll enable APP_ID   # for each app listed above
```

then reboot (or `systemctl start` the units) and read back flags and unit states.

## Measurements and remaining acceptance

No on-TV app launch/paint speedup is established. Early CPU/resource samples were
exploratory and workloads differ. A resource snapshot taken during root preflight
is excluded from performance comparisons; overlapping SDB work also contaminated
that preflight's timing check, so it failed before staging and was rerun alone.
Do not run profilers/SDB jobs concurrently with root preflight or final samples.

Pending:
controlled idle samples, persistence verification and final recovery review.
