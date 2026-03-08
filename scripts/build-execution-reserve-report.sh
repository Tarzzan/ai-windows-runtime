#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.execution_reserve.cli \
  --delivery-intake-sync-report "${OUT_DIR}/delivery-intake-sync-report.json" \
  --scope-budget-report "${OUT_DIR}/scope-budget-report.json" \
  --owner-load-report "${OUT_DIR}/owner-load-report.json" \
  --output "${OUT_DIR}/execution-reserve-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-reserve-report.json" \
  --schema schemas/execution-reserve-report.schema.json \
  --report "${VALIDATION_DIR}/execution-reserve-report-validation.json"

echo "execution reserve report: ok"
