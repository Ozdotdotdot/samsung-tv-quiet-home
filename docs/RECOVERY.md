# Recovery material and order

The original private device evidence, signing material and packages remain in
this workspace's ignored `backup/`. Keep it separately from GitHub and do not
publish it. The exact workspace path can be found from the active T3 thread.

Preserve `app-context-original.db`, both SQL files, compiled helper output,
`Quiet Home.wgt`, `OzQuietBoot.tpk`, `quiet-home.p12`, `signing-password` and
`profiles.xml`. The routing database is not a firmware or application-data backup.

Device identities:

- Launcher package `OzQuiet001`, app `OzQuiet001.Home`.
- Boot relay package `OzQuietBoot`, app `OzQuietBoot.Start`.
- Explicitly staged helper folder `/home/owner/share/tmp/sdk_tools/quiet-home-helper`.
- Home helper expects `apply.sql` and `restore.sql` beside its compiled DLL.

The stock short Home route is row 78 in `/opt/dbspace/.app-context.db`:
`com.samsung.tv.csfs`, key `XF86Home`, null longpress/override, empty on_selector,
request `launch`, target `package:com.samsung.tv.csfs`, args `entry_point:smarthub_key`.
The installed route changes only target to `package:OzQuiet001.Home` and clears
args, adding one null-ui_type/null-source managed_app row for the launcher.

In a future authorized maintenance window:

1. Inspect actual route, installed packages and native foreground first.
2. Re-stage the known helper and SQL if missing. Use the bounded root adapter to
   execute `dotnet .../quiet-home-helper/HomeControl.dll restore`.
3. Check the command result, native reload and current DB rows. Allow the context
   manager's reload debounce (at least six seconds), then test physical Home.
4. Restore Home routing before uninstalling the launcher. Do not overwrite the
   whole database: later unrelated registrations/settings may have changed.
5. Boot routing was not installed. Confirm no OzQuietBoot managed/task rows exist
   before removing that package through the normal native package-manager path.
6. Inspect and remove only this project's known staged files if retiring it.

The scripts perform device actions only when explicitly invoked. Do not run these
steps while someone is watching. Native reload/app-launch responses are not proof
of visible behavior. Retain logs and stop on an uncertain completion.

DNS service/config remains separately at `/home/ozair/services/samsung-tv-dns`.
It was stopped at the user's request. Its generated admin credential and query
logs are not in Git. If the TV was manually pointed there later, restore automatic
DNS before leaving that service stopped.

## Recovery notes after the 2310.0 update (2026-10-22)

- The root bootstrap was re-run on `T-KSU2EAKUC-2310.0` and still returns uid 0
  with unchanged original system-file hashes. The staged helper and the boot
  relay pin were moved to 2310.0; only the helper DLL was rebuilt. The boot tpk
  still needs a rebuild before it can run on this firmware.
- Launcher rollback: install `backup/Quiet-Home-1.0.0.wgt` (six-tile build) over
  1.1.0. The working signing profile is `backup/profiles.xml`; the saved
  `backup/signing-password` does not open `quiet-home.p12`.
- Remote reboot: `systemctl reboot` fails because `reboot.target` is absent.
  Use the `reboot` syscall through `scripts/tv-root.py`. SDB must be reconnected
  after the TV returns: `tools/tizen-tools/sdb connect 192.168.86.208:26101`.
- Firmware update rollback: remove `/mnt/backup/OS_UPGRADE_FLAG` and re-enable
  `swu-auto-upgrade.service`/`.timer` to allow updates again.
- Boot reconciler rollback: disable user timer `samsung-tv-reconcile.timer`,
  then `systemctl unmask --runtime contents-recognition-service.service
  media-analytics-service.service` on the TV and reboot.
