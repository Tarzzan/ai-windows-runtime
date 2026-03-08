#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.execution_focus.cli \
  --cadence-recommendation-report "${OUT_DIR}/cadence-recommendation-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --ownership-assignment-report "${OUT_DIR}/ownership-assignment-report.json" \
  --output "${OUT_DIR}/execution-focus-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-focus-report.json" \
  --schema schemas/execution-focus-report.schema.json \
  --report "${VALIDATION_DIR}/execution-focus-report-validation.json"

echo "execution focus report: ok"
