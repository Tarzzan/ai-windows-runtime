#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.patch_template_library.cli \
  --gaps "${OUT_DIR}/gaps.json" \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --output "${OUT_DIR}/patch-template-catalog.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/patch-template-catalog.json" \
  --schema schemas/patch-template-catalog.schema.json \
  --report "${VALIDATION_DIR}/patch-template-catalog-validation.json"

echo "patch template catalog: ok"

