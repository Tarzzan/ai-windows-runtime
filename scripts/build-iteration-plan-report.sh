#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.iteration_plan.cli \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --hook-backlog-report "${OUT_DIR}/hook-backlog-report.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --test-impact-report "${OUT_DIR}/test-impact-report.json" \
  --output "${OUT_DIR}/iteration-plan-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/iteration-plan-report.json" \
  --schema schemas/iteration-plan-report.schema.json \
  --report "${VALIDATION_DIR}/iteration-plan-report-validation.json"

echo "iteration plan report: ok"
