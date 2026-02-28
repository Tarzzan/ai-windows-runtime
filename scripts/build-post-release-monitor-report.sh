#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.post_release_monitor.cli \
  --delivery-signoff-report "${OUT_DIR}/delivery-signoff-report.json" \
  --runtime-signal-report "${OUT_DIR}/runtime-signal-report.json" \
  --crash-signature-report "${OUT_DIR}/crash-signature-report.json" \
  --output "${OUT_DIR}/post-release-monitor-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/post-release-monitor-report.json" \
  --schema schemas/post-release-monitor-report.schema.json \
  --report "${VALIDATION_DIR}/post-release-monitor-report-validation.json"

echo "post-release monitor report: ok"
