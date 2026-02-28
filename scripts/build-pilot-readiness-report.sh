#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.pilot_readiness.cli \
  --productization-readiness "${OUT_DIR}/productization-readiness.json" \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/pilot-readiness-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/pilot-readiness-report.json" \
  --schema schemas/pilot-readiness-report.schema.json \
  --report "${VALIDATION_DIR}/pilot-readiness-report-validation.json"

echo "pilot readiness report: ok"
