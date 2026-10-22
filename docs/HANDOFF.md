# Handoff — 2026-10-22 ~19:35 (TV local time)

Read this first, then `LEAN-PROFILE.md` (applied changes + rollback) and
`RECOVERY.md` (Home routing / launcher recovery).

## Stop-point state

- **Firmware changed.** The owner rebooted; a staged OTA installed during that boot.
  `/etc/prd_info.ini` now reads `Version=T-KSU2EAKUC-2310.0;`
  (build TIZEN-TRUNK2021-KantSU2e-HOTFIX-RELEASE_20260721.1). Everything before
  this was done on `2301.1`.
- **Root has NOT been re-tested on 2310.0.** No root session ran after the update.
- `OwnerPackageControl` (native/) and `boot/Program.cs` both hard-check
  `Version=T-KSU2EAKUC-2301.1;` and will refuse to run until that pin is
  revisited deliberately.
- The owner wants **automatic software updates disabled** going forward
  (`SWUAutoUpgrade`, `SWUService`, `SWUCoreTV` were running post-boot). Not done.
  Weigh against losing security/app-compat fixes; ask before acting.

## What survived the reboot + update (read-only check, uptime 2–5 min)

- All `/opt/usr/share/systemd/system/` markers persisted: canalysis-daemon,
  vision-data-recognition-service, com.samsung.tv.ondevice-voice,
  org.tizen.voice-app, pisa-service. pisa/adagent/canalysis/vision stayed inactive.
- Voice, recognition and advertising app-disable flags persisted (none of those
  apps appeared in `app_launcher -S`).
- Quiet Home (`OzQuiet001.Home`) installed and reachable via Home key.
- Came back as expected (runtime-only control): `contents-recognition-service`,
  `media-analytics-service`.
- Snapshot at boot: MemAvailable ~477 MB, SwapFree ~371 MB, load avg ~33–37.
  Process/CPU inventory: `backup/post-reboot-procs.txt` (local, not in git).
- SDB had to be reconnected after reboot: `tools/tizen-tools/sdb connect 192.168.86.208`.

## Owner acceptance so far

After voice + recognition + advertising groups: Netflix plays (scrolling "maybe
feels better"), NBC News via TV Plus works, Samsung app store works.

## Owner decisions / requests still open

1. **Cleanup round — owner said "kill all of them":**
   org.tizen.hbbtv, org.tizen.hbbtv-service, org.tizen.content-tiles-provider,
   org.tizen.multi-assistant-service, com.samsung.tv.utterance-recommender-core,
   com.samsung.tv.action-planner-service, com.samsung.tv.fuzzy-search-engine,
   org.tizen.welcome-mode, com.samsung.tv.context-aware-service,
   com.samsung.tv.context-aware-agent.
   These were added to the OwnerPackageControl allowlist, rebuilt and pushed
   (TV DLL sha256 cbc3002c…f376 matches local) but **NOT applied**.
   Watch: content-tiles-provider may feed the Samsung Home row the dad uses to
   reach NBC — re-check NBC after applying.
2. **Keep SmartThings / easysetup / mde-framework** (owner's call).
3. **contents-recognition and media-analytics must be gone persistently.** Neither
   unit has a `ConditionPathExists` marker; `/etc` and `/` are read-only (vdfs ro),
   `/opt` is rw. Owner suggested editing the package/registry DB directly if
   needed. Other runtime-only telemetry candidates (no marker): org.tizen.tv.sp-kpi,
   org.tizen.tv.tagpro-service-tv, issue_report_agent, devicetracker.
   context-aware-service *does* honor marker
   `/opt/usr/share/systemd/system/com.samsung.tv.context-aware-service`.
4. **Quiet Home should be the startup app; cold-boot launch is "unacceptably" slow.**
   Lead: owner's `systemd --user` (pid ~1070, UID 5001) loads units from
   `/opt/usr/home/owner/.config/systemd/user` (on writable /opt; `.config` is
   world-writable). Candidate: a user unit that starts `OzQuietBoot.Start` (already
   installed, never wired up; see boot/Program.cs) or the launcher after
   `memory/system/boot_done`. Not created/tested.
   Note Netflix pre-launches at boot (≈69 s CPU in first 4 min); csfs (Samsung
   Home) is the largest CPU/RSS consumer (≈181 s, 120 MB).
5. **Update Quiet Home on the TV** to the "The List" + ambient-clock build
   (`.local/desktop/candidate/`, design in docs/design). The TV still runs the
   earlier six-tile launcher.
6. **Slint test** (`experiments/slint-hello/README.md`) — never run on the TV.
   Owner wants it next; a native launcher may fix cold-start latency.
7. Owner asked whether the TV can be rebooted remotely — not answered/tested.

## Safety rules carried forward

- Check `vconftool get -t string memory/appfw/current_fullscreen_appid`
  (read-only) before acting; don't touch the TV while the owner's father watches.
- Preserve streaming, TV Plus / Live TV / NBC News, app store, accounts, DRM,
  network, remote input, TTS. DNS filtering stays paused.
- Save original state before each change; verify by readback; commit results.
