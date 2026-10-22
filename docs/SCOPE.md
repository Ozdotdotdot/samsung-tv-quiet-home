# Scope to agree before more changes

## Goal and order

Optimize the experience: quiet startup, minimal navigation, dependable streaming
and news, less background work and reduced viewing-data collection. Establish
baselines and make small reversible changes. Replacing the UI alone does not
stop tracking or prove better performance.

No more TV interaction while it is in use. Do not deploy a revised UI or enable
boot integration before alignment with the owner.

## Preserve

- Six confirmed streaming/library apps: YouTube, Netflix, Prime Video, Disney+,
  HBO Max and Jellyfin.
- Samsung Apps, accounts/SSO, DRM/certificates, network/time, media playback,
  remote/input, accessibility and picture/sound configuration.
- Live TV, channel guide, inputs and Samsung TV Plus until the actual news path
  is known. No channel deletions or TV Plus removal based on the earlier list.
- Existing news-related apps pending family decisions.

## News observations from the saved inventory

The earlier device inventory lists CBS News: Live Breaking News
(`7zteowV8pB.CBSNews`), CNN (`0pElqIOcTv.CNN`), FOX One
(`799qlPniMH.FoxOne`), Peacock and Tubi, plus Samsung TV Plus/LiveTV.
The owner says his father opens Samsung Home, scrolls down and selects NBC News.
A subsequently authorized, one-shot foreground read reported
`org.tizen.tv-viewer`, with an empty partial-app ID. This is consistent with a
channel/live-TV route, but does not identify TV Plus versus another TV source,
the tuned channel, or the menu sequence. No navigation history was established.
A standalone app named NBC News was not found in that saved inventory. That
bounded name search does not establish that NBC content is unavailable or
identify how the father watches it. Listing an app does not prove login,
subscription, playback or whether the family wants it.

NBC's own help page lists NBC News NOW on Samsung TV Plus, Peacock, Tubi and
YouTube, among other platforms. NBC News NOW differs from a live local/network
NBC feed, so clarify which one matters before changing the current route.
Source checked 2026-10-22:
https://nbcnews.zendesk.com/hc/en-us/articles/45174657963155-Where-can-I-watch-NBC-News-NOW
Samsung TV Plus platform information:
https://www.samsung.com/us/tvs/smart-tv/samsung-tv-plus/

Proposed News section: NBC route first, then whichever of existing CBS News,
CNN, local news or other sources the family chooses. Avoid adding redundant apps
just to fill a section. Do not guess a deep-link/channel launch contract: confirm
supported app/channel controls before claiming a one-click NBC shortcut.

## First reversible changes to propose

- Stop unsolicited startup playback and promotional previews, while retaining
  intentional access to news and live TV.
- Decline optional ACR/viewing-data, interest-based advertising and unused voice
  consent through the proper APIs/settings where their semantics are established.
- Evaluate disabling verified ACR/analytics components through supported native
  controls, with exact original-state capture and explicit enable rollback.
- Hide unwanted Home entries before deciding whether to uninstall their packages.
- Consider unused assistant integrations only after confirming voice use and
  accessibility needs. Keep remote hardware/ordinary navigation working.

Root is available, but package names are not dependency analysis. For example,
Vetro explicitly protects `com.samsung.tv.coba.adagent` because Samsung Home
loads a resource from it. Do not disable every component matching 'ad'.

## Removal candidates, not an approved execution list

Saved inventory includes consumer extras such as TikTok, Instagram, Xbox,
Samsung GameBreaks, QVC/HSN, promotions and Glance. Review usage, install flags,
dependencies and reinstall availability before removing. Prefer disable/hide
when it has a clean rollback. Do not treat removal of 90% of packages as a target:
most inventory rows are platform components, not unwanted visible apps.

## Performance work

Once a maintenance window is available, measure Home response, launch latency,
RAM/swap, CPU and startup time. Attribute changes to measured before/after results.
No speed improvement is established yet. Keep desktop UI checks separate from
on-TV paint/input measurements. Avoid periodic flash logging and resident root
agents unless a concrete feature requires them.

## Privacy limits

The launcher makes no analytics or content-recognition requests. That does not
stop firmware or streaming-app telemetry. Root keeps SMACK restrictions, and
turning off ACR does not eliminate all service-side viewing records. DNS remains
paused. Packet capture/router enforcement are not configured and must not be
silently introduced. Preserve streaming account/DRM and store functionality.

## Later acceptance, when authorized to touch the TV again

Inspect interrupted state first; check installed artifacts and actual routes.
Then validate physical Home, Samsung fallback, News access, all six apps and
store use, followed separately by cold boot and standby/resume. Only after those
pass evaluate cleanup in small recorded groups. Keep an exact rollback and show
what changed, what was measured and what remains unknown.

## Owner clarification — 2026-10-22

No remote microphone searches, voice assistants or spoken accessibility features
are used. Unused assistant components can be investigated for reversible removal
from background work. Preserve ordinary remote controls and text-to-speech; do
not treat this as permission to remove shared media, input or account services.
