#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.control_recommendation.cli \
  --delivery-temperature-report "${OUT_DIR}/delivery-temperature-report.json" \
  --execution-confidence-report "${OUT_DIR}/execution-confidence-report.json" \
  --execution-pressure-report "${OUT_DIR}/execution-pressure-report.json" \
  --release-policy-report "${OUT_DIR}/release-policy-report.json" \
  --output "${OUT_DIR}/control-recommendation-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/control-recommendation-report.json" \
  --schema schemas/control-recommendation-report.schema.json \
  --report "${VALIDATION_DIR}/control-recommendation-report-validation.json"

echo "control recommendation report: ok"
