#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.portfolio_risk_budget.cli \
  --commitment-guard-report "${OUT_DIR}/commitment-guard-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --output "${OUT_DIR}/portfolio-risk-budget-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/portfolio-risk-budget-report.json" \
  --schema schemas/portfolio-risk-budget-report.schema.json \
  --report "${VALIDATION_DIR}/portfolio-risk-budget-report-validation.json"

echo "portfolio risk budget report: ok"
