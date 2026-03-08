#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.priority_corridor.cli \
  --execution-throttle-report "${OUT_DIR}/execution-throttle-report.json" \
  --execution-focus-report "${OUT_DIR}/execution-focus-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/priority-corridor-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/priority-corridor-report.json" \
  --schema schemas/priority-corridor-report.schema.json \
  --report "${VALIDATION_DIR}/priority-corridor-report-validation.json"

echo "priority corridor report: ok"
