#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.control_efficiency.cli \
  --execution-confidence-report "${OUT_DIR}/execution-confidence-report.json" \
  --execution-momentum-report "${OUT_DIR}/execution-momentum-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --output "${OUT_DIR}/control-efficiency-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/control-efficiency-report.json" \
  --schema schemas/control-efficiency-report.schema.json \
  --report "${VALIDATION_DIR}/control-efficiency-report-validation.json"

echo "control efficiency report: ok"
