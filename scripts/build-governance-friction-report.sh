#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.governance_friction.cli \
  --control-efficiency-report "${OUT_DIR}/control-efficiency-report.json" \
  --intervention-plan-report "${OUT_DIR}/intervention-plan-report.json" \
  --validation-coverage-report "${OUT_DIR}/validation-coverage-report.json" \
  --output "${OUT_DIR}/governance-friction-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/governance-friction-report.json" \
  --schema schemas/governance-friction-report.schema.json \
  --report "${VALIDATION_DIR}/governance-friction-report-validation.json"

echo "governance friction report: ok"
