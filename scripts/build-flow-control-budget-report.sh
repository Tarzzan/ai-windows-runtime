#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.flow_control_budget.cli \
  --scope-rebalance-report "${OUT_DIR}/scope-rebalance-report.json" \
  --capacity-buffer-report "${OUT_DIR}/capacity-buffer-report.json" \
  --execution-reserve-report "${OUT_DIR}/execution-reserve-report.json" \
  --output "${OUT_DIR}/flow-control-budget-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/flow-control-budget-report.json" \
  --schema schemas/flow-control-budget-report.schema.json \
  --report "${VALIDATION_DIR}/flow-control-budget-report-validation.json"

echo "flow control budget report: ok"
