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

## Netflix navigation investigation — same maintenance window

Owner confirmed Netflix was visible and navigation felt delayed. A requested
navigation sampling command timed out through SDB with no saved output. A small
read confirmed Netflix remained foregrounded. A shorter two-snapshot sample then
completed: aggregate CPU busy excluding I/O wait was 85.8%, with per-core values
82.7–87.9%. Netflix GIBBON_MAIN accrued seven CPU seconds and was the largest
user-space process delta. This is an exploratory sample, with diagnostic overhead
and no synchronized remote-key/video timeline; it does not establish causality,
FPS or a repeatable launch baseline.

Two read-only root sessions authenticated as UID 0, SMACK User, and confirmed
cleanup and unchanged passwd/public.pem hashes. Read-only package queries found
ACR, canalysis and two recognition database/vision app records enabled. The queried
registry dependency subset returned no rows; that is not a full runtime dependency
map. No nvision-analysis-dbmgr row matched on this TV. Both canalysis-service and
contents-recognition-service were active, with no declared RequiredBy/BoundBy/
PartOf dependencies and manual stopping permitted. UnitFileState was already
'disabled' despite both running: unit enable state is not actual process state.

A first temporary stop test targets only those two systemd services. Their original
active states and unit definitions are in ignored private evidence. No package
uninstall, package-disable flag, startup database or unit enable flag is changed.
Exact runtime rollback is:

```
systemctl start canalysis-service.service contents-recognition-service.service
```

Run rollback in the same authorized root context and verify both ActiveState=active.
Do not call this a complete ACR shutdown: the separate ACR app is outside this test.
Final stop result and follow-up acceptance are recorded below after verification.

The temporary-stop command timed out after 30 seconds (exit 124). Immediate SDK
readback showed contents-recognition-service inactive/dead with MainPID=0, and
canalysis-service still deactivating/stop-sigterm with PID 1726 and a pending stop
job. Thus no clean disabled-group performance comparison was possible. Requested
nonblocking start of both units to restore original running state; verify actual
state before any further experiment. Root session cleanup and baseline hash checks
passed even though the inner service command timed out. No speed/privacy gain
is claimed from this partial transition.

Final SDK readback confirmed successful restoration: canalysis-service active/
running, new PID 3241; contents-recognition-service active/running, PID 2851;
both Job fields empty. Its configured stop timeout is 90 seconds, longer than
the command deadline. The stopped canalysis process was eventually replaced.
No permanent change remains from this experiment. Future service tests must
account for shutdown deadlines and verify state independently after timeouts.

After restoration, a requested hands-off Netflix sample measured 34.4% aggregate
CPU busy, compared with 85.8% in the earlier requested-navigation sample. Netflix
accrued no whole CPU second in the idle interval; reclamation/recompression,
adagent and vendor tasks accrued some CPU time. The coarse process timer and
unsynchronized human input prevent a precise foreground/background attribution.
These are workload observations, not before/after optimization results. Next
priority: repeat controlled navigation and identify interval background CPU,
including dependencies of adagent before considering any related control.
