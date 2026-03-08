#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intervention_plan.cli \
  --control-efficiency-report "${OUT_DIR}/control-efficiency-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --dependency-watch-report "${OUT_DIR}/dependency-watch-report.json" \
  --output "${OUT_DIR}/intervention-plan-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intervention-plan-report.json" \
  --schema schemas/intervention-plan-report.schema.json \
  --report "${VALIDATION_DIR}/intervention-plan-report-validation.json"

echo "intervention plan report: ok"
