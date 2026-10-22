# Owner package control

A short-lived, fixed-target helper for this AU8000's T-KSU2EAKUC-2301.1 firmware.
It is not an installed service, launcher or root exploit. It invokes the TV's own
`pkgcmd` after changing its process identity to owner UID 5001/GID 100. Target IDs
are explicitly allowed in source; core streaming, viewer, store, network and
account apps are excluded.

The TV's CLI validates explicit user IDs against the caller. Root UID 0's default
`pkgcmd --global` activation/deactivation failed, while an owner process succeeded.
The root bootstrap also overlays /etc/passwd in a private mount namespace. The
host maintenance commands verify the namespace differs from PID 1's namespace,
then unmount only that private overlay before owner-scoped operations. The real
/etc/passwd is neither edited nor replaced. Upstream root cleanup and original
system-file hash checks remain enabled.

Build in the existing SDK container:

```
docker run --rm -v "$PWD:/project" -w /project mcr.microsoft.com/dotnet/sdk:6.0 \
  dotnet build native/OwnerPackageControl -c Release -o native/OwnerPackageControl/out
```

DLL, runtimeconfig and deps files are staged privately under
`/home/owner/share/tmp/sdk_tools/quiet-home-owner-control/`. They are not packaged
as a TV app or included in Git. A verified root session can invoke:

```
/usr/bin/dotnet /home/owner/share/tmp/sdk_tools/quiet-home-owner-control/OwnerPackageControl.dll disable APP_ID
/usr/bin/dotnet /home/owner/share/tmp/sdk_tools/quiet-home-owner-control/OwnerPackageControl.dll enable APP_ID
```

Select only a source-allowed target, capture its original state before disabling,
and read the registry AND running processes afterward. Boot and autorestart
fields are independent of app disabled state. This helper does not change them.
Do not interpret its successful return as a complete service/dependency or
playback acceptance test. Enable is rollback only for targets originally enabled.

Current state and recovery details belong in docs/LEAN-PROFILE.md.
