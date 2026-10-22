#!/bin/sh
# Builds the probe for the AU8000 (ARMv7, softfp ABI) with cargo-zigbuild and
# checks the ELF is loadable there: ARM EABI5 soft-float-ABI flags, glibc symbol
# versions pinned to 2.17 (the TV has 2.30), and no hard link against
# wayland/xkbcommon/GL (those are dlopen'ed). Output goes to ./bin (git-ignored).
# Builds only. It does not contact or deploy to the TV.
#
# Needs: rustup target armv7-unknown-linux-gnueabi, zig 0.13, cargo-zigbuild,
# DejaVu fonts (fonts-dejavu-core) and binutils' readelf on the build host.
set -eu
here=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
target=armv7-unknown-linux-gnueabi
fonts=${DEJAVU_DIR:-/usr/share/fonts/truetype/dejavu}
mkdir -p "$here/ui/fonts" "$here/bin"
cp "$fonts/DejaVuSans.ttf" "$fonts/DejaVuSerif.ttf" "$here/ui/fonts/"
cd "$here"
cargo zigbuild --release --locked --target "$target.2.17"
elf="$here/target/$target/release/quiet-slint-hello"
cp "$elf" "$here/bin/quiet-slint-hello-armv7"
elf="$here/bin/quiet-slint-hello-armv7"
readelf -h "$elf" | grep -E 'Class|Machine|Flags'
readelf -d "$elf" | grep NEEDED
readelf -V "$elf" | python3 -c '
import re, sys
v = {tuple(map(int, m)) for m in re.findall(r"GLIBC_(\d+)\.(\d+)", sys.stdin.read())}
newest = max(v)
if newest > (2, 30):
    raise SystemExit("Requires GLIBC %d.%d; the TV has 2.30" % newest)
print("glibc: newest required symbol version %d.%d (TV has 2.30)" % newest)'
readelf -d "$elf" | python3 -c '
import sys
d = sys.stdin.read()
bad = [l for l in ("wayland", "xkbcommon", "EGL", "GLES", "fontconfig") if l in d]
if bad:
    raise SystemExit("Hard-linked against " + ", ".join(bad))
print("dynamic deps: glibc libraries only; wayland, xkbcommon and fontconfig are dlopen-ed")'
ls -l "$elf"
