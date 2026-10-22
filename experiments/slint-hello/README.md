# Slint hello: can a Rust/Slint UI run on the AU8000?

**Status: built and checked on the desktop only. Never deployed or run on the TV.**

This tiny probe answers one question before anyone writes a Slint launcher:
*will this TV run a native Rust/Slint program and give it a window?* It shows a
seven-item list in the chosen "The List" design (serif items, focused item at
full opacity and the rest at 28%, amber dot, large clock). It launches nothing.
OK only reports the selection, and Back/Escape quits.

![Offscreen render of the probe](snapshot.png)

## Build

```sh
./build.sh          # → bin/quiet-slint-hello-armv7 (git-ignored)
```

Requires `rustup target add armv7-unknown-linux-gnueabi`, Zig 0.13,
`cargo install cargo-zigbuild`, DejaVu fonts and `readelf`. On the Debian
server, keep toolchains and `TMPDIR` under `/home`, because `/` is a small partition.
The build doesn't use Docker for the same reason.

`build.sh` fails unless the ELF matches what this TV loads:

| Check | Result (2026-10-22) |
|---|---|
| ABI | ELF32 ARM, flags `0x5000200` (EABI5, soft-float ABI): the same as the native code that already runs on these TVs |
| glibc | Newest required symbol 2.17; the TV has 2.30 |
| Linked libs | `libc`, `libm`, `libpthread`, `libdl` only |
| Wayland, xkbcommon, fontconfig | Loaded at runtime with `dlopen`, not linked, so a missing library is a clear runtime error rather than a loader failure |
| Fonts | DejaVu Sans/Serif are embedded at build time; the TV's fontconfig isn't needed |
| Size | ~10.5 MB, mostly the two embedded fonts and the winit/Wayland stack |

## Desktop checks done

- `cargo build --release --features snapshot`, then
  `quiet-slint-hello --snapshot out.ppm` renders one 1920×1080 frame offscreen
  through **the same software renderer** the TV build uses: 5 ms on the
  server's x86 CPU. The result is `snapshot.png`.
- With no display server, the normal path exits with a clean
  `neither WAYLAND_DISPLAY nor WAYLAND_SOCKET nor DISPLAY is set` error. That
  is the first thing to look for on the TV.
- **Not done:** keyboard/remote input. The server has no Wayland compositor or
  `libxkbcommon-x11`, so the arrow/OK handling hasn't been run interactively.

## What a first TV run should find out (when the TV is free)

Run it in this order. Stop at the first failure and record the stderr.

1. **Will it execute at all?** The root tool's README says uploaded native ELF
   programs need its executable-protection step first (`uep_status`). Find
   out whether that's also true for a program inside a normally signed,
   normally installed package. **This is the deciding question:** a launcher
   must start at every boot without a root session.
2. **Does it get a window?** Samsung's TV UI runs on an Enlightenment Wayland
   compositor. The probe prints `WAYLAND_DISPLAY`/`XDG_RUNTIME_DIR`. Note whether a
   socket is reachable from the app's context and whether SMACK allows the connection.
3. **Does it receive remote keys?** Arrow/OK/Back should arrive through
   xkbcommon as normal key events. Samsung may route them differently.
4. **Numbers:** stderr prints the time to the first event-loop tick, then RSS,
   peak RSS and thread count every 2 s. Compare these with the web launcher's
   cold/warm Home timing and memory.

## Known limitations and next steps if it works

- Rust's `armv7-unknown-linux-gnueabi` target generates soft-float code. It's
  ABI-compatible with the TV, but floating-point math is slow. If the probe
  works, try `-C target-feature=+vfp3d16` (keeping the soft-float ABI) and
  check that the ELF flags are unchanged.
- The clock uses UTC because the probe avoids timezone data.
- A real launcher still needs Tizen app-lifecycle integration (`aul`/`appcore`)
  or a wrapper, so that the TV's app manager doesn't kill a process that
  never reports in. It also needs `tizen.application`-style launching of the other apps.
