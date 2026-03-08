#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.delivery_safety_margin.cli \
  --execution-stability-guard-report "${OUT_DIR}/execution-stability-guard-report.json" \
  --flow-control-budget-report "${OUT_DIR}/flow-control-budget-report.json" \
  --capacity-buffer-report "${OUT_DIR}/capacity-buffer-report.json" \
  --output "${OUT_DIR}/delivery-safety-margin-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-safety-margin-report.json" \
  --schema schemas/delivery-safety-margin-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-safety-margin-report-validation.json"

echo "delivery safety margin report: ok"
