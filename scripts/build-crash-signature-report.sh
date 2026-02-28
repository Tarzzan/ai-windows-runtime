#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.crash_signatures.cli \
  --trace "${OUT_DIR}/trace.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/crash-signature-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/crash-signature-report.json" \
  --schema schemas/crash-signature-report.schema.json \
  --report "${VALIDATION_DIR}/crash-signature-report-validation.json"

echo "crash signature report: ok"

