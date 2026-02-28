#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.release_forecast.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --kpi-report "${OUT_DIR}/kpi-report.json" \
  --trend-report "${OUT_DIR}/trend-report.json" \
  --output "${OUT_DIR}/release-forecast-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-forecast-report.json" \
  --schema schemas/release-forecast-report.schema.json \
  --report "${VALIDATION_DIR}/release-forecast-report-validation.json"

echo "release forecast report: ok"
