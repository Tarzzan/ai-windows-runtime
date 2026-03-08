#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_acceleration_readiness.cli \
  --scope-expansion-gate-report "${OUT_DIR}/scope-expansion-gate-report.json" \
  --scope-expansion-readiness-report "${OUT_DIR}/scope-expansion-readiness-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/scope-acceleration-readiness-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-acceleration-readiness-report.json" \
  --schema schemas/scope-acceleration-readiness-report.schema.json \
  --report "${VALIDATION_DIR}/scope-acceleration-readiness-report-validation.json"

echo "scope acceleration readiness report: ok"
