#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_rebalance.cli \
  --intake-queue-policy-report "${OUT_DIR}/intake-queue-policy-report.json" \
  --portfolio-risk-budget-report "${OUT_DIR}/portfolio-risk-budget-report.json" \
  --scope-budget-report "${OUT_DIR}/scope-budget-report.json" \
  --output "${OUT_DIR}/scope-rebalance-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-rebalance-report.json" \
  --schema schemas/scope-rebalance-report.schema.json \
  --report "${VALIDATION_DIR}/scope-rebalance-report-validation.json"

echo "scope rebalance report: ok"
