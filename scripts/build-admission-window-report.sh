#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.admission_window.cli \
  --scope-budget-report "${OUT_DIR}/scope-budget-report.json" \
  --admission-control-report "${OUT_DIR}/admission-control-report.json" \
  --execution-focus-report "${OUT_DIR}/execution-focus-report.json" \
  --output "${OUT_DIR}/admission-window-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/admission-window-report.json" \
  --schema schemas/admission-window-report.schema.json \
  --report "${VALIDATION_DIR}/admission-window-report-validation.json"

echo "admission window report: ok"
