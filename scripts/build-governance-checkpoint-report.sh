#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.governance_checkpoint.cli \
  --stability-window-report "${OUT_DIR}/stability-window-report.json" \
  --hotfix-planner-report "${OUT_DIR}/hotfix-planner-report.json" \
  --verification-snapshot-report "${OUT_DIR}/verification-snapshot-report.json" \
  --evidence-catalog-report "${OUT_DIR}/evidence-catalog-report.json" \
  --output "${OUT_DIR}/governance-checkpoint-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/governance-checkpoint-report.json" \
  --schema schemas/governance-checkpoint-report.schema.json \
  --report "${VALIDATION_DIR}/governance-checkpoint-report-validation.json"

echo "governance checkpoint report: ok"
