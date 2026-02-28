#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

cargo test --manifest-path runtime-core/Cargo.toml

TMP_PE="$(mktemp /tmp/aiwr-minimal-pe.XXXXXX.exe)"
python3 - <<'PY' > "$TMP_PE"
import sys
b = bytearray(512)
b[0:2] = b"MZ"
b[0x3C:0x40] = (0x80).to_bytes(4, "little")
b[0x80:0x84] = (0x00004550).to_bytes(4, "little")
b[0x84:0x86] = (0x8664).to_bytes(2, "little")
b[0x86:0x88] = (4).to_bytes(2, "little")
b[0x94:0x96] = (0xF0).to_bytes(2, "little")
o = 0x98
b[o+16:o+20] = (0x1000).to_bytes(4, "little")
b[o+56:o+60] = (0x7000).to_bytes(4, "little")
sys.stdout.buffer.write(b)
PY

cargo run --manifest-path runtime-core/Cargo.toml --bin runtime_probe -- "$TMP_PE"
rm -f "$TMP_PE"
