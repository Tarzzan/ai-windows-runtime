#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.delivery_intake_sync.cli \
  --portfolio-risk-budget-report "${OUT_DIR}/portfolio-risk-budget-report.json" \
  --admission-window-report "${OUT_DIR}/admission-window-report.json" \
  --cadence-recommendation-report "${OUT_DIR}/cadence-recommendation-report.json" \
  --output "${OUT_DIR}/delivery-intake-sync-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-intake-sync-report.json" \
  --schema schemas/delivery-intake-sync-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-intake-sync-report-validation.json"

echo "delivery intake sync report: ok"
