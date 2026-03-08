#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.execution_pressure.cli \
  --execution-momentum-report "${OUT_DIR}/execution-momentum-report.json" \
  --dependency-watch-report "${OUT_DIR}/dependency-watch-report.json" \
  --validation-coverage-report "${OUT_DIR}/validation-coverage-report.json" \
  --output "${OUT_DIR}/execution-pressure-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-pressure-report.json" \
  --schema schemas/execution-pressure-report.schema.json \
  --report "${VALIDATION_DIR}/execution-pressure-report-validation.json"

echo "execution pressure report: ok"
