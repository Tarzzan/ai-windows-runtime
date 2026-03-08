#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_lock_state.cli \
  --intake-commitment-window-report "${OUT_DIR}/intake-commitment-window-report.json" \
  --scope-rebalance-report "${OUT_DIR}/scope-rebalance-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/scope-lock-state-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-lock-state-report.json" \
  --schema schemas/scope-lock-state-report.schema.json \
  --report "${VALIDATION_DIR}/scope-lock-state-report-validation.json"

echo "scope lock state report: ok"
