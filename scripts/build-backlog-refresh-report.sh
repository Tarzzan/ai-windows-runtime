#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.backlog_refresh.cli \
  --incident-feedback-report "${OUT_DIR}/incident-feedback-report.json" \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --remediation-sprint-report "${OUT_DIR}/remediation-sprint-report.json" \
  --output "${OUT_DIR}/backlog-refresh-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/backlog-refresh-report.json" \
  --schema schemas/backlog-refresh-report.schema.json \
  --report "${VALIDATION_DIR}/backlog-refresh-report-validation.json"

echo "backlog refresh report: ok"
