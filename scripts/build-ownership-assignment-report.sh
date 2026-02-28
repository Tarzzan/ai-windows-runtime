#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.ownership_assignment.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --output "${OUT_DIR}/ownership-assignment-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/ownership-assignment-report.json" \
  --schema schemas/ownership-assignment-report.schema.json \
  --report "${VALIDATION_DIR}/ownership-assignment-report-validation.json"

echo "ownership assignment report: ok"
