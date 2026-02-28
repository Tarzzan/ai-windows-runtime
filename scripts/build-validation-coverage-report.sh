#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.validation_coverage.cli \
  --validation-dir "${VALIDATION_DIR}" \
  --output "${OUT_DIR}/validation-coverage-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/validation-coverage-report.json" \
  --schema schemas/validation-coverage-report.schema.json \
  --report "${VALIDATION_DIR}/validation-coverage-report-validation.json"

echo "validation coverage report: ok"
