#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.delivery_stress_index.cli \
  --scope-freeze-guard-report "${OUT_DIR}/scope-freeze-guard-report.json" \
  --throughput-guard-band-report "${OUT_DIR}/throughput-guard-band-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/delivery-stress-index-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-stress-index-report.json" \
  --schema schemas/delivery-stress-index-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-stress-index-report-validation.json"

echo "delivery stress index report: ok"
