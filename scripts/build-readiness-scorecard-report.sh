#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.readiness_scorecard.cli \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --kpi-report "${OUT_DIR}/kpi-report.json" \
  --output "${OUT_DIR}/readiness-scorecard-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/readiness-scorecard-report.json" \
  --schema schemas/readiness-scorecard-report.schema.json \
  --report "${VALIDATION_DIR}/readiness-scorecard-report-validation.json"

echo "readiness scorecard report: ok"
