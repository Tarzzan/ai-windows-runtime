#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.rollback_hints.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --output "${OUT_DIR}/rollback-hints.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/rollback-hints.json" \
  --schema schemas/rollback-hints.schema.json \
  --report "${VALIDATION_DIR}/rollback-hints-validation.json"

echo "rollback hints: ok"

