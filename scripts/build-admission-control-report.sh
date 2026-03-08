#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.admission_control.cli \
  --intake-capacity-report "${OUT_DIR}/intake-capacity-report.json" \
  --release-policy-report "${OUT_DIR}/release-policy-report.json" \
  --priority-corridor-report "${OUT_DIR}/priority-corridor-report.json" \
  --output "${OUT_DIR}/admission-control-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/admission-control-report.json" \
  --schema schemas/admission-control-report.schema.json \
  --report "${VALIDATION_DIR}/admission-control-report-validation.json"

echo "admission control report: ok"
