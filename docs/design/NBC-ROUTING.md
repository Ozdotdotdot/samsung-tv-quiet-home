# NBC News direct launch investigation

Investigated online/offline only, 2026-10-22. No TV queries, tracing, app launches
or settings changes were made during this design work.

## There is a real Samsung mechanism

Samsung Ads' own [Native TV Ads documentation](https://help.dsp.samsungads.com/docs/samsung-tv-native-ads#virtual-tune-in)
describes Virtual Tune-In: opening TV Plus on a specific channel using its Provider
ID and Service ID. This is primary evidence that Samsung supports channel-specific
launches inside its own interface. The page does not publish the actual Tizen
appcontrol operation, bundle format or NBC identifiers. Do not equate the visible
channel number with a service/provider identifier.

Samsung's [US TV Plus lineup](https://www.samsungtvplus.com/assets/STVP_Channel-List.pdf)
lists NBC News NOW as 1114 at research time. That is a lead for later verification,
not an internal-ID mapping or proof the same number applies to this TV's lineup.

## Other implementations / research

The maintained [TheFab21 Home Assistant fork](https://github.com/TheFab21/ha-samsungtv-smart)
includes a local IP Control `directChannelControl` getter, and its
[firmware research notes](https://github.com/TheFab21/ha-samsungtv-smart/blob/6407d60b600258fbe9cae84650dc6809d205f85e/notes/QN55LS03FAFXZA/IPCONTROL_DECOMPILED.md)
document setter fields `atvDtv`, `airCable`, `channelNum`. Its newer Frame
returned TV Plus channel state (`atvDtv=tvplus`, channel 1001). The notes do not
establish a successful NBC-specific setter or support on this AU8000. The current
integration exposes channel readback; a fabricated setter payload is not deployed.

The older [ollo69 integration](https://github.com/ollo69/ha-samsungtv-smart)
supports named channel sources, but this alone does not prove a direct TV Plus
appcontrol contract. An exact GitHub code search found a few uses of
`com.samsung.tv.tvPlusDeeplinker`, chiefly as a generic app ID; none of the inspected
results supplied a verified NBC tune payload. Android `tvplus://` activity links
must not be assumed to work on Tizen.

## Current launcher behavior

Both NBC News and Live news channels request `com.samsung.tv.tvPlusDeeplinker`
through ordinary `tizen.application.launch`. This app was present in the saved
inventory. It is the permitted generic TV Plus fallback, **not a promise to tune
NBC**. The new launcher has not been installed or tested on the TV.

## Proposed bounded capture — only once Ozair says the TV is free

1. Inspect the current device/route state and existing diagnostic facilities,
   without launching anything. Normal SDB advertises logs disabled; don't assume
   `dlog` contains the answer. Save current source/channel state if available.
2. Prefer a short existing app-framework diagnostic/event stream or inspect the
   exact TV Plus/CSFS appcontrol handlers copied read-only for offline REA analysis.
   The capture target is launch/tune metadata, not video/audio or ongoing viewing.
3. Ozair opens Home and presses the existing NBC tile once. Collect just that
   event interval, then stop the capture immediately. Inspect any operation,
   destination app, URI, bundle/action_data, provider/service IDs or channel tuple.
4. A foreground-app change alone is insufficient: it previously showed only
   `org.tizen.tv-viewer`. The action may be native IPC/channel tuning rather than
   an HTTP request. A packet capture alone may reveal nothing useful.
5. Resolve the observed identifiers against read-only channel metadata if exposed.
   Redact account tokens, device IDs and unrelated events; keep raw evidence local.
6. Prepare one exact replay and test it once with panel confirmation. Verify it
   opens NBC from another app and returns with Home. Do not guess IDs, replay a
   whole recorded session, install a permanent logger or change the channel
   while someone else is watching.

Capturing the payload is a feasible investigation, not a guarantee: normal logs
may omit it and SMACK can restrict observation even with UID 0. If native tracing
or injected hooks become necessary, assess that concrete method before using it.

## Verified on 2026-10-22 — decompiled deeplinker + one live capture

The TV was free for one short capture. The findings below supersede the earlier
"Proposed bounded capture" assumptions where they conflict.

### What the installed deeplinker actually requires

`com.samsung.tv.tvPlusDeeplinker` (v0.1.86, `nodisplay=true`) was copied
read-only and decompiled with ILSpy. Its entry point does not accept a bare
launch: `OnAppControlReceived` calls `OnExitApp()` unless the app-control
carries a `PAYLOAD` extra.

- `type=CH`: `PAYLOAD` is `"<provider_id>_<service_id>"`; the code splits on the
  first `_`.
- Otherwise `PAYLOAD` is JSON with `values.tune_data.provider_id` +
  `values.tune_data.service_id`, or `values.deeplink_data`, plus optional
  `type` (`detail`/`CH`), `request_ready` and `callerid`.
- It maps provider/service to a `TCServiceId` via the TV Plus API, then launches
  `org.tizen.tv-viewer` with operation `http://tizen.org/appcontrol/operation/view`
  and extra `svcid=<TCServiceId>`.
- `HEPsqFNie0.tvplusstandalone` is not installed, so the standalone path is off;
  the TV-service/HbbTV path is used.

That means the deeplinker is optional for our launcher: a direct app-control to
`org.tizen.tv-viewer` with `svcid` is the real tune primitive. The missing piece
is the `TCServiceId` for NBC News NOW on this TV.

### Why the first capture did not reveal the ID

While the owner selected NBC News in Samsung Home, a 150 s watcher sampled
`/proc` for new `tvPlusDeeplinker` / `tvplus` / `tv-viewer` processes and polled
the foreground app. Results:

- Foreground changed to `org.tizen.tv-viewer` and NBC played.
- No new deeplinker or TV Plus process appeared. The stock Home tunes through
  the already-running native TV service, not via an app launch.
- `dlogutil` produced only its startup banner (2 lines). TV logging is compiled
  out, so the deeplinker's own `TCServiceId : …` log is unavailable.
- The menu capture was equally opaque: `org.tizen.menu` is long-running
  (pid 336), so opening Settings reuses it.

### Consequence

Do not infer the ID from the visible channel number. `1114` is the public US
lineup number, not a verified `TCServiceId`. The next bounded step is to read
the current channel through Samsung's TV web API
(`webapis.tv.channel.getCurrentChannel()`) from our own app after NBC is opened,
then replay `svcid` once with panel confirmation. The D-Bus
`com.samsung.IServiceNavigation` `MethodCall(functionCode, size, buffer)` surface
is the fallback for querying the current service.
