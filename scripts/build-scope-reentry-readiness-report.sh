#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_reentry_readiness.cli \
  --scope-admission-gate-report "${OUT_DIR}/scope-admission-gate-report.json" \
  --transition-readiness-index-report "${OUT_DIR}/transition-readiness-index-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/scope-reentry-readiness-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-reentry-readiness-report.json" \
  --schema schemas/scope-reentry-readiness-report.schema.json \
  --report "${VALIDATION_DIR}/scope-reentry-readiness-report-validation.json"

echo "scope reentry readiness report: ok"
