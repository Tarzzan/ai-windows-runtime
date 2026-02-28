#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.stability_window.cli \
  --post-release-monitor-report "${OUT_DIR}/post-release-monitor-report.json" \
  --release-gate-history-report "${OUT_DIR}/release-gate-history-report.json" \
  --readiness-delta-report "${OUT_DIR}/readiness-delta-report.json" \
  --output "${OUT_DIR}/stability-window-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/stability-window-report.json" \
  --schema schemas/stability-window-report.schema.json \
  --report "${VALIDATION_DIR}/stability-window-report-validation.json"

echo "stability window report: ok"
