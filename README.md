# Samsung AU8000: quiet, minimal and reliable

Work in progress on a privately owned Samsung UN75AU8000BXZA (2021, Tizen 6.0,
ARMv7). The primary goal is a quiet, responsive TV that the family can use easily,
with less viewing-data collection and no unsolicited playback. A replacement
launcher is one component, not the definition of success.

**Current operating boundary:** all TV interaction is paused while it is being
used. Agree on the keep/disable/remove list before further UI or cleanup changes.
DNS filtering is also paused.

## Desktop design candidate — 1.1

Ozair selected **The List** with an ambient clock. The candidate source is now
single-file HTML with five WATCH items and two NEWS entries, hidden TV controls,
remembered focus and timed clock/black idle states. It is **not deployed**.
See [design, checks and measurement limits](docs/design/README.md) and
[NBC direct-channel research](docs/design/NBC-ROUTING.md). The saved concepts
and desktop screenshots are in `docs/design/`.

## Preserve

YouTube, Netflix, Prime Video, Disney+, HBO Max, Jellyfin and Samsung Apps.
Preserve live TV, inputs, channel guide and existing news routes until the family
identifies how NBC news is currently watched. Samsung TV Plus may be that route.

## Actual progress

- Normal SDB connection and application inventory succeeded.
- Temporary authenticated UID/GID 0 access succeeded through the archive-launcher
  route after adapting runtime discovery to the verified .NET 3.1.3 layout.
- Successful completed root runs verified unchanged `/etc/passwd` and Samsung
  verification-key hashes, plus cleanup of their own temporary root payloads.
- A consistent native routing-database backup was saved privately and passed
  SQLite integrity checking.
- Quiet Home 1.0.0 was signed with a fresh local author key and installed.
  The owner confirmed six app tiles on a dark background.
- The short Home-key route was redirected to Quiet Home through a transaction
  changing one existing routing row and adding one managed-app row. The separate
  long-press support route was preserved. A native key test reported Quiet Home
  fullscreen, with no partial overlay.
- SQL apply/restore round-trip testing on the actual backup preserved every
  original row and row ID. Live restore/reapply commands succeeded, but their
  short foreground observations did not establish reliable return behavior.
- A normally signed no-window boot-helper package was installed. **No boot
  task rule was added. Automatic startup is not implemented/verified.**
- AdGuard Home was prepared separately, then stopped at the owner's request.
  No TV DNS cutover was performed by the agent.

## Incomplete and unresolved

A later native launch request reported acceptance, while REST and native state
reported Quiet Home not running and TV Viewer in front. The last Home-key recheck
was interrupted with empty result files, so it has no usable success/failure
record. App launch callbacks alone are not proof of rendering or playback.

No streaming-app launch/playback acceptance suite has passed. No full cold-boot,
standby/resume or physical Home-button acceptance suite has passed. The owner did
confirm the initial launcher rendered. No tracker, ACR, voice, news or other
preinstalled package has been disabled or uninstalled. No privacy-consent setting
has been changed. No firmware or system boot script has been flashed/patched.

The About screen was reported as `T-KSU2EAKUC-2391.1, BT-S`; direct device
`/etc/prd_info.ini` reads reported `T-KSU2EAKUC-2301.1` and build
`TIZEN-TRUNK2021-KantSU2e-RELEASE_20251112.1`. Preserve both observations; the
helper is guarded against the observed on-device string, not a guessed version.

## Repository contents

- `launcher/`: undeployed 1.1 list candidate (installed 1.0 baseline is in Git history); no analytics, external fonts,
  autoplay player or remote image dependency. It uses normal Tizen app launching.
- `helper/`: firmware-guarded one-shot Home route/restore helper and exact SQL.
- `boot/`: adapted short-lived boot relay; installed package, inactive integration.
- `scripts/`: SDK capture/root adapter and packaging command; never run implicitly.
- `docs/PROGRESS.md`: evidence ledger and current limitations.
- `docs/SCOPE.md`: proposed keep/disable/remove decisions and news research.
- `docs/RECOVERY.md`: private recovery-material locations and recovery order.

Downloaded tools, raw device logs/databases, signing passwords/keys, local profiles
and signed installers are excluded. GitHub is a source/documentation backup,
**not** a complete firmware, app-data or device backup.

Root controls are owner-authorized device operations. Python scripts require
explicit local `TV_HOST`, `TV_CALLBACK_HOST` (root) and `TIZEN_SDB` environment
values, plus the pinned upstream tools under `tools/`. There is no automatic
startup service or scheduled TV-control task on the server.

Native adaptations and license: [THIRD-PARTY.md](docs/THIRD-PARTY.md).
