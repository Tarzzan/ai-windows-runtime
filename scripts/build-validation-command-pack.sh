#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.validation_command_pack.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --test-impact-report "${OUT_DIR}/test-impact-report.json" \
  --output "${OUT_DIR}/validation-command-pack.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/validation-command-pack.json" \
  --schema schemas/validation-command-pack.schema.json \
  --report "${VALIDATION_DIR}/validation-command-pack-validation.json"

echo "validation command pack: ok"
