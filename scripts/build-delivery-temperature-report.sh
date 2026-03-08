#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.delivery_temperature.cli \
  --execution-pressure-report "${OUT_DIR}/execution-pressure-report.json" \
  --launch-readiness-report "${OUT_DIR}/launch-readiness-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --output "${OUT_DIR}/delivery-temperature-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-temperature-report.json" \
  --schema schemas/delivery-temperature-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-temperature-report-validation.json"

echo "delivery temperature report: ok"
