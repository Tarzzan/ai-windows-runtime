#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

cargo test --manifest-path runtime-core/Cargo.toml

TMP_IMPORT="$(mktemp /tmp/aiwr-import-pe.XXXXXX.exe)"
python3 - <<'PY' > "$TMP_IMPORT"
import sys
b = bytearray(0x700)
b[0:2] = b"MZ"
b[0x3C:0x40] = (0x80).to_bytes(4, "little")
b[0x80:0x84] = (0x00004550).to_bytes(4, "little")
b[0x84:0x86] = (0x8664).to_bytes(2, "little")
b[0x86:0x88] = (2).to_bytes(2, "little")
b[0x94:0x96] = (0xF0).to_bytes(2, "little")
o = 0x98
b[o:o+2] = (0x20B).to_bytes(2, "little")
b[o+16:o+20] = (0x1000).to_bytes(4, "little")
b[o+56:o+60] = (0x4000).to_bytes(4, "little")
b[o+60:o+64] = (0x200).to_bytes(4, "little")
b[o+108:o+112] = (16).to_bytes(4, "little")
b[o+120:o+124] = (0x3000).to_bytes(4, "little")
b[o+124:o+128] = (40).to_bytes(4, "little")
sh = o + 0xF0
b[sh:sh+8] = b".text\0\0\0"
b[sh+8:sh+12] = (0x100).to_bytes(4, "little")
b[sh+12:sh+16] = (0x1000).to_bytes(4, "little")
b[sh+16:sh+20] = (0x200).to_bytes(4, "little")
b[sh+20:sh+24] = (0x200).to_bytes(4, "little")
sh2 = sh + 40
b[sh2:sh2+8] = b".rdata\0\0"
b[sh2+8:sh2+12] = (0x300).to_bytes(4, "little")
b[sh2+12:sh2+16] = (0x3000).to_bytes(4, "little")
b[sh2+16:sh2+20] = (0x300).to_bytes(4, "little")
b[sh2+20:sh2+24] = (0x400).to_bytes(4, "little")
b[0x400:0x404] = (0x3050).to_bytes(4, "little")
b[0x400+12:0x400+16] = (0x3030).to_bytes(4, "little")
b[0x400+16:0x400+20] = (0x3070).to_bytes(4, "little")
name = b"KERNEL32.dll\0"
b[0x430:0x430+len(name)] = name
b[0x450:0x458] = (0x3080).to_bytes(8, "little")
b[0x458:0x460] = (0x8000000000000123).to_bytes(8, "little")
b[0x460:0x468] = (0).to_bytes(8, "little")
b[0x480:0x482] = (7).to_bytes(2, "little")
fn = b"Sleep\0"
b[0x482:0x482+len(fn)] = fn
sys.stdout.buffer.write(b)
PY

TMP_EXPORT="$(mktemp /tmp/aiwr-export-pe.XXXXXX.dll)"
python3 - <<'PY' > "$TMP_EXPORT"
import sys
b = bytearray(0x800)
b[0:2] = b"MZ"
b[0x3C:0x40] = (0x80).to_bytes(4, "little")
b[0x80:0x84] = (0x00004550).to_bytes(4, "little")
b[0x84:0x86] = (0x8664).to_bytes(2, "little")
b[0x86:0x88] = (2).to_bytes(2, "little")
b[0x94:0x96] = (0xF0).to_bytes(2, "little")
o = 0x98
b[o:o+2] = (0x20B).to_bytes(2, "little")
b[o+16:o+20] = (0x1000).to_bytes(4, "little")
b[o+56:o+60] = (0x5000).to_bytes(4, "little")
b[o+60:o+64] = (0x200).to_bytes(4, "little")
b[o+108:o+112] = (16).to_bytes(4, "little")
b[o+112:o+116] = (0x3000).to_bytes(4, "little")
b[o+116:o+120] = (40).to_bytes(4, "little")
sh = o + 0xF0
b[sh:sh+8] = b".text\0\0\0"
b[sh+8:sh+12] = (0x100).to_bytes(4, "little")
b[sh+12:sh+16] = (0x1000).to_bytes(4, "little")
b[sh+16:sh+20] = (0x200).to_bytes(4, "little")
b[sh+20:sh+24] = (0x200).to_bytes(4, "little")
sh2 = sh + 40
b[sh2:sh2+8] = b".edata\0\0"
b[sh2+8:sh2+12] = (0x300).to_bytes(4, "little")
b[sh2+12:sh2+16] = (0x3000).to_bytes(4, "little")
b[sh2+16:sh2+20] = (0x300).to_bytes(4, "little")
b[sh2+20:sh2+24] = (0x400).to_bytes(4, "little")
b[0x400+12:0x400+16] = (0x3040).to_bytes(4, "little")
b[0x400+16:0x400+20] = (0x120).to_bytes(4, "little")
b[0x400+20:0x400+24] = (4).to_bytes(4, "little")
b[0x400+24:0x400+28] = (1).to_bytes(4, "little")
b[0x400+28:0x400+32] = (0x3050).to_bytes(4, "little")
b[0x400+32:0x400+36] = (0x3060).to_bytes(4, "little")
b[0x400+36:0x400+40] = (0x3064).to_bytes(4, "little")
b[0x45C:0x460] = (0x2222).to_bytes(4, "little")
b[0x460:0x464] = (0x3068).to_bytes(4, "little")
b[0x464:0x466] = (3).to_bytes(2, "little")
name = b"KERNEL32.dll\0"
b[0x440:0x440+len(name)] = name
fn = b"Sleep\0"
b[0x468:0x468+len(fn)] = fn
sys.stdout.buffer.write(b)
PY

OUT_IMPORT="$(cargo run --manifest-path runtime-core/Cargo.toml --bin runtime_probe -- "$TMP_IMPORT")"
printf '%s\n' "$OUT_IMPORT"
echo "$OUT_IMPORT" | rg -q "imports: 1"
echo "$OUT_IMPORT" | rg -q -- "- Sleep \\(hint 7\\)"
echo "$OUT_IMPORT" | rg -q -- "- ordinal #291"

OUT_EXPORT="$(cargo run --manifest-path runtime-core/Cargo.toml --bin runtime_probe -- "$TMP_EXPORT")"
printf '%s\n' "$OUT_EXPORT"
echo "$OUT_EXPORT" | rg -q "exports: 1"
echo "$OUT_EXPORT" | rg -q "export dll: KERNEL32.dll"
echo "$OUT_EXPORT" | rg -q "export: Sleep \(ord #291\) -> 0x00002222"

rm -f "$TMP_IMPORT" "$TMP_EXPORT"
