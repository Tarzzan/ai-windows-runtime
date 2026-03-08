#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.owner_load.cli \
  --ownership-assignment-report "${OUT_DIR}/ownership-assignment-report.json" \
  --output "${OUT_DIR}/owner-load-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/owner-load-report.json" \
  --schema schemas/owner-load-report.schema.json \
  --report "${VALIDATION_DIR}/owner-load-report-validation.json"

echo "owner load report: ok"
