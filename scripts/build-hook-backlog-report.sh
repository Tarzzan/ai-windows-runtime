#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.hook_backlog.cli \
  --runtime-signal-report "${OUT_DIR}/runtime-signal-report.json" \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --output "${OUT_DIR}/hook-backlog-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/hook-backlog-report.json" \
  --schema schemas/hook-backlog-report.schema.json \
  --report "${VALIDATION_DIR}/hook-backlog-report-validation.json"

echo "hook backlog report: ok"
