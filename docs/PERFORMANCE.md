# Performance investigation — 2026-10-22

Priority: improve app startup and interaction, not only the launcher. No TV contact
or changes were made for this research; the watching pause remains in effect.
DNS filtering remains paused.

## What is established

Quiet Home changes our UI. It does not rewrite Netflix, stop the stock shell's
background work, or establish faster app rendering. Root has worked on this TV,
but access does not establish that every service control works under its SMACK
label. No on-TV performance improvement has been measured yet.

## Relevant primary-source projects

- Vetro: https://github.com/andrearicci93/vetro
  Experimental manager with package/process/startup inspection and independent
  enable, process-stop and startup controls. Its published test platform is a
  Q80A, Tizen 6 ARMv7, T-NKM2DEUC-2301.1; this AU8000 has a different firmware
  family. It documents five disabled recognition/analysis components and protects
  adagent as a dependency. The exploratory A/B comparison reports resource and
  remote-request acknowledgement differences, explicitly not measured Netflix
  loading or visual response improvements. Repeated visual trials remain pending.
  Treat as an implementation reference, not a ready AU8000 disable list.
- https://github.com/DemonKingSwarn/samsung-tv-tizen-root
  Research on a 2026 Tizen 9 model documents package deactivation and service
  suppression through unit conditions and runtime masks. These are candidate
  mechanisms to inspect on our firmware. Its package/service-count reductions
  are not Netflix speed benchmarks. Do not execute its bulk removal script here.
- https://github.com/chris-ritsen/samsung-tv-root
  Privilege acquisition foundation already used locally. Root alone is not an
  app performance optimization.
- https://github.com/reisxd/TizenBrew
  Homebrew/module platform, useful for alternate app experiences. Not a system
  accelerator or a replacement Netflix implementation. Do not assume its web
  runtime is faster than an existing vendor-native app.

## Working hypotheses, not findings on this TV

Background CPU work and memory pressure can compete with foreground apps. Reducing
verified unused recognition/telemetry/promotional/assistant work may help if that
competition is present. Removing an inactive app generally frees storage rather
than CPU; package count is not a performance metric.

Separate slow local input/painting, slow cold startup, and network/content waits.
CPU-limited rendering inside a proprietary app may remain slow after debloating.
Wi-Fi improvements address network waits, not inherently local drawing speed.
Keeping every app alive can worsen memory pressure; do not force residency globally.
Repeated cache deletion can make subsequent loads slower; investigate storage or
corrupt app state before treating cache clearing as an optimization.

Netflix's troubleshooting identifies stale device data and network problems as
possible causes of loading failures, not proof of our current bottleneck:
https://help.netflix.com/en/node/100242
No verified AU8000 Netflix renderer upgrade or overclock procedure was established
by this research. Neither should be offered as a demonstrated solution.

## Next maintenance window

1. Record actual firmware and current routing/artifact state before new changes.
2. Take short, bounded samples of process CPU, available memory, swap/zram activity,
   storage availability and service state. Avoid a permanent dashboard or profiler.
   Check accessible CPU frequency/thermal indicators only to diagnose throttling;
   do not alter governors, thermal protections or compositor scheduling.
3. Establish repeated cold and warm launches of Netflix and one comparison app,
   plus Home return and a fixed navigation sequence. Cold means process absent;
   standby/resume is a separate test. Measure visible usable UI, not just launch
   acknowledgement or foreground ID. Use owner observation/video where needed.
4. Inspect dependencies and original enabled/running/startup state for a small
   candidate group. Start with unused recognition/analytics components verified
   on this firmware. Save exact rollback, disable rather than uninstall, and verify
   the processes actually stop without restart loops.
5. Repeat baseline/change/change/baseline trials under comparable network, content
   and thermal conditions. Report medians and ranges, including null results.
6. Validate streaming playback, accounts/DRM, store, news/TV Plus, inputs, sound and
   physical remote. Restore any group without a useful result or with regressions.

Preserve network/time, media/DRM, authentication, store, remote, accessibility,
TV viewer and the family's news route. Review unused voice/IoT extras separately
because family usage is not fully established. No bulk uninstall target.

## Decision boundary

If measured gains are insufficient and Netflix remains limited by its own UI on
this hardware, an external streaming device is the practical way to move that
work onto a different processor. No product selection or purchase is proposed
here. First determine what this TV can achieve with measured reversible changes.

## First authorized device baseline — 2026-10-22, approximately 18:47 EDT

Owner confirmed the TV was free. Connected through SDB and took bounded SDK
samples; no root session, service changes, cache deletion or reboot in this pass.
Firmware file still reports T-KSU2EAKUC-2301.1; keep the earlier owner-reported
2391.1 discrepancy open. Quiet Home was the initial foreground app.

Initial resources: MemTotal 1,112,840 kB, MemAvailable 284,424 kB; swap used
674,044 kB of 788,716 kB. The main zram device reported 641,380 kB original data,
203,616 kB compressed data and 210,296 kB actual memory used. Swap allocation
alone does not prove current thrashing. /opt was 58% used, with 1,716,000 kB
available. No storage cleanup justified by this snapshot.

The initial load average was about 35, but a following interval was only 18.6%
busy across four CPUs, excluding I/O wait. Many vendor kernel tasks were in
D state; do not interpret load as runnable CPU demand. This does not establish
why those tasks wait. Lifetime CPU rankings included kswapd0 and bgrecompd;
those rankings are not current interval utilization. The exposed vmstat has
limited counters and did not include the usual pswpin/pswpout/pgmajfault fields.
One frequency reading was 1,350,000 kHz, equal to exposed scaling_max_freq;
thermal_zone0 read 69,724. Neither isolated reading proves thermal throttling.

122 service units were running. Unit definitions for analysis/recognition
services were readable; no service was selected for disabling yet.
Netflix was already running as PID 3263. Normal SDK execute brought that same
process forward; native foreground read confirmed org.tizen.netflix-app. The
next bounded interval was 41.8% busy, with roughly 302,000 kB available memory.
This sampled foreground CPU, not a controlled navigation benchmark or per-core
saturation test. Owner visual/input feedback is pending. No cold-start, visible
readiness time or performance improvement is established.

Raw samples remain in ignored backup/performance-*-sdk.txt. No permanent monitor
was deployed. Next: confirm visible Netflix state and navigation response,
then gather comparable cold/warm trials before testing reversible service groups.
