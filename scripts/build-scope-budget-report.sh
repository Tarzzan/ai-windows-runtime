#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_budget.cli \
  --commitment-pacing-report "${OUT_DIR}/commitment-pacing-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --output "${OUT_DIR}/scope-budget-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-budget-report.json" \
  --schema schemas/scope-budget-report.schema.json \
  --report "${VALIDATION_DIR}/scope-budget-report-validation.json"

echo "scope budget report: ok"
