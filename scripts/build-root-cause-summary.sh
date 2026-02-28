#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.root_cause.cli \
  --gaps "${OUT_DIR}/gaps.json" "${OUT_DIR}/runtime-gaps.json" \
  --patch-plans "${OUT_DIR}/patch-plan.json" "${OUT_DIR}/runtime-patch-plan.json" \
  --labels "base" "runtime" \
  --output "${OUT_DIR}/root-cause-summary.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/root-cause-summary.json" \
  --schema schemas/root-cause-summary.schema.json \
  --report "${VALIDATION_DIR}/root-cause-summary-validation.json"

echo "root cause summary: ok"

