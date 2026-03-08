#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_pacing_window.cli \
  --delivery-stress-index-report "${OUT_DIR}/delivery-stress-index-report.json" \
  --intake-slot-policy-report "${OUT_DIR}/intake-slot-policy-report.json" \
  --intake-release-window-report "${OUT_DIR}/intake-release-window-report.json" \
  --output "${OUT_DIR}/intake-pacing-window-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-pacing-window-report.json" \
  --schema schemas/intake-pacing-window-report.schema.json \
  --report "${VALIDATION_DIR}/intake-pacing-window-report-validation.json"

echo "intake pacing window report: ok"
