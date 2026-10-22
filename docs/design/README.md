# Quiet Home 1.1 — The List / Ambient clock

Desktop-only candidate, 2026-10-22. **Not installed. No TV contact during this work.**
The installed 1.0 tile UI and its existing routing/boot state were not modified.

`concepts.html` is an exact copy of Ozair's supplied design reference. Concept B
is the active list, concept D informs the clock-only idle screen. The two PNGs
are actual desktop captures, not on-TV observations.

## Implemented

- WATCH: YouTube, Netflix, Prime Video, Disney+, Jellyfin. HBO Max removed only
  from the candidate visible list; no package changes.
- NEWS: NBC News and Live news channels. Both use the generic TV Plus fallback;
  see [NBC-ROUTING.md](NBC-ROUTING.md) for the direct-channel investigation.
- System Georgia/serif text, the supplied colors, an accent dot, 28% unfocused
  opacity, and only 100 ms opacity transitions. No external fonts/artwork/media.
- Large clock/date at right; larger left clock/date in ambient. No weather.
- Up/Down navigation, no Left/Right action, Back does nothing on Home.
- Last successfully requested item retained in localStorage and restored on
  return/reload. Storage denial or stale item IDs cannot prevent operation.
- Short OK activates on release, once. 700 ms hold opens small TV controls;
  Down past the final news item opens the same menu as a slim-remote fallback.
  Back closes that menu without launching Samsung Home.
- Fresh document starts ambient; 30 idle seconds hide the list; ten idle minutes
  render black. Wake input is consumed. Timers pause while hidden and clock work
  stops in black. Return to an existing instance shows the list at remembered focus.
- Plain transient failure messages without native errors/codes; pending launch
  requests time out after six seconds and ignore late callbacks.
- One self-contained `launcher/index.html`; removed WEBAPIS script and separate
  CSS/JS. CSP forbids network, image, font and media requests. The package icon is
  installer metadata and is not loaded by the runtime UI.

## Residence / launch behavior

The candidate never calls exit, reload, kill or starts a background watchdog.
The default appcontrol declares `reload=disable` and handles resume/appcontrol
in memory after backgrounding. `background-support=disable` remains: the OS can
suspend JavaScript rather than running timers behind streaming apps.
This does not force retention under memory pressure. Native PID/document-lifetime
and actual Home behavior must be measured later.

Samsung explicitly says [prelaunching is unsupported since 2019 TVs](https://developer.samsung.com/smarttv/develop/guides/fundamentals/prelaunching-applications.html).
The ineffective prelaunch metadata was removed. See Samsung's
[multitasking guide](https://developer.samsung.com/smarttv/develop/guides/fundamentals/multitasking.html)
and [reload handling example](https://developer.samsung.com/smarttv/develop/guides/smart-hub-preview/implementing-public-preview.html).
The new manifest/native integration is untested on this AU8000.

## Desktop checks and timings

`desktop-checks.json`: 30 passing interaction/lifecycle checks using a desktop-only
mock native API and deterministic timers. Layout checked at 1920×1080 and
1280×720. Inline runtime parses as ECMAScript 5 with Acorn 8.15.0. Modern browser
checks are not a Chromium 76 emulator; no unsupported flex gap, aspect-ratio,
focus-visible or live blur is used. Accessibility uses roving tabindex and ARIA;
`inert` is supplemental and is not required for old-browser key navigation.

`desktop-timings.json`: five alternating fresh-document loads per variant,
Chromium 154 on this Debian server, localhost, cache uncontrolled. The baseline
is commit efd06e4. Median DCL: 16.6 ms before / 13.1 ms candidate; median FCP:
36 ms before / 28 ms candidate. FCP ranges: 32–44 ms / 24–32 ms.
Secondary resource requests: 3 / 0. Baseline's WEBAPIS request returns a desktop
404; it is a device-provided resource on TV, so these timings cannot quantify
TV performance or the exact value of removing that library there.

The sampled candidate preceded the final small appcontrol/diagnostic additions;
final interaction and ES5 checks cover those additions. Do not claim the sample
as a final-build or TV benchmark. The file grows from 4,753 combined baseline
HTML/CSS/JS bytes to about 13 KB raw (~4.5 KB gzip), reflecting idle/lifecycle/error
handling. Reducing requests does not mean the new source is smaller.

## Required TV baseline, then candidate measurements

These are **not yet measured**: cold Home-to-visible, warm Home-to-visible,
residency/eviction frequency, TV paint cost, standby/resume and physical long-OK.
Ozair must say the TV is free before any device step.

1. Inspect the interrupted prior route/app state. Keep current installers and exact
   rollback. Measure the installed baseline before deploying 1.1.
2. Warm trials: same preceding streaming app/state, already-running launcher;
   record native PID, documentStartedAt, ten Home returns and medians/ranges.
3. Cold trials: deliberately absent launcher process in an agreed maintenance
   window, five Home launches. Keep process start, foreground acknowledgement and
   visible first-frame measurements separate. Exclude root/SDB session setup from
   the Home timer. Use a shared monotonic clock or panel recording; desktop FCP
   and native foreground ID alone do not establish visible frame latency.
4. Repeat against 1.1 with the same conditions. Confirm no reload on warm returns;
   record native PID and in-memory resume counter. Validate the six existing
   services, news route, store escape, idle, actual remote and power cycles.
5. The current doc always starts ambient when a new document is created. Without
   verified boot context it cannot distinguish power-on from an OS-evicted app
   cold launch. Both will show the clock initially. Warm return shows the list.
6. Platform screensavers may supersede the app; black pixels do not switch off
   the panel/backlight. Volume/Power may be consumed by the system and cannot be
   promised as app wake keys. No screensaver or power settings were changed.

## Native alternative decision

No native launcher was built. The existing .NET root/boot helper timings are not
comparable UI render benchmarks. EFL can avoid web-engine startup, but a .NET UI
still initializes its managed runtime, and a webview wrapper still loads Chromium.
If TV measurements show warm web-runtime startup dominates, report that evidence
and propose a small comparable native benchmark before building a replacement.

## Reproduce locally, without TV access

Run `python3 scripts/desktop-preview.py`. Open the printed `/candidate/` URL.
`/tests/desktop.html` exposes `runChecks()` in the desktop browser console and
renders the result list. The server only serves explicit UI/test routes on
loopback; it does not expose credentials, backups or device tools. Tests use a
fake Tizen launch API in isolated iframes; the packaged launcher contains no mock.
