#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.delivery_bandwidth.cli \
  --queue-pressure-report "${OUT_DIR}/queue-pressure-report.json" \
  --cadence-recommendation-report "${OUT_DIR}/cadence-recommendation-report.json" \
  --owner-load-report "${OUT_DIR}/owner-load-report.json" \
  --output "${OUT_DIR}/delivery-bandwidth-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-bandwidth-report.json" \
  --schema schemas/delivery-bandwidth-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-bandwidth-report-validation.json"

echo "delivery bandwidth report: ok"
