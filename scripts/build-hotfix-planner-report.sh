#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.hotfix_planner.cli \
  --stability-window-report "${OUT_DIR}/stability-window-report.json" \
  --incident-feedback-report "${OUT_DIR}/incident-feedback-report.json" \
  --rollback-hints-report "${OUT_DIR}/rollback-hints.json" \
  --output "${OUT_DIR}/hotfix-planner-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/hotfix-planner-report.json" \
  --schema schemas/hotfix-planner-report.schema.json \
  --report "${VALIDATION_DIR}/hotfix-planner-report-validation.json"

echo "hotfix planner report: ok"
