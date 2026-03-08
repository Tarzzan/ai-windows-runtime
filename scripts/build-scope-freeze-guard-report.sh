#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_freeze_guard.cli \
  --intake-slot-policy-report "${OUT_DIR}/intake-slot-policy-report.json" \
  --scope-lock-state-report "${OUT_DIR}/scope-lock-state-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/scope-freeze-guard-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-freeze-guard-report.json" \
  --schema schemas/scope-freeze-guard-report.schema.json \
  --report "${VALIDATION_DIR}/scope-freeze-guard-report-validation.json"

echo "scope freeze guard report: ok"
