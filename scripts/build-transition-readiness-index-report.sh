#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.transition_readiness_index.cli \
  --scope-transition-gate-report "${OUT_DIR}/scope-transition-gate-report.json" \
  --delivery-stress-index-report "${OUT_DIR}/delivery-stress-index-report.json" \
  --policy-health-report "${OUT_DIR}/policy-health-report.json" \
  --output "${OUT_DIR}/transition-readiness-index-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/transition-readiness-index-report.json" \
  --schema schemas/transition-readiness-index-report.schema.json \
  --report "${VALIDATION_DIR}/transition-readiness-index-report-validation.json"

echo "transition readiness index report: ok"
