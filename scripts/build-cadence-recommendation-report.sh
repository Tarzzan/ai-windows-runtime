#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.cadence_recommendation.cli \
  --governance-friction-report "${OUT_DIR}/governance-friction-report.json" \
  --delivery-temperature-report "${OUT_DIR}/delivery-temperature-report.json" \
  --control-recommendation-report "${OUT_DIR}/control-recommendation-report.json" \
  --output "${OUT_DIR}/cadence-recommendation-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/cadence-recommendation-report.json" \
  --schema schemas/cadence-recommendation-report.schema.json \
  --report "${VALIDATION_DIR}/cadence-recommendation-report-validation.json"

echo "cadence recommendation report: ok"
