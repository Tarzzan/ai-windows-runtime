#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.execution_throttle.cli \
  --cadence-recommendation-report "${OUT_DIR}/cadence-recommendation-report.json" \
  --governance-friction-report "${OUT_DIR}/governance-friction-report.json" \
  --owner-load-report "${OUT_DIR}/owner-load-report.json" \
  --output "${OUT_DIR}/execution-throttle-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-throttle-report.json" \
  --schema schemas/execution-throttle-report.schema.json \
  --report "${VALIDATION_DIR}/execution-throttle-report-validation.json"

echo "execution throttle report: ok"
