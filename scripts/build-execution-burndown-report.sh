#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.execution_burndown.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --output "${OUT_DIR}/execution-burndown-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-burndown-report.json" \
  --schema schemas/execution-burndown-report.schema.json \
  --report "${VALIDATION_DIR}/execution-burndown-report-validation.json"

echo "execution burndown report: ok"
