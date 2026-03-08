#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.commitment_guard.cli \
  --admission-window-report "${OUT_DIR}/admission-window-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --release-policy-report "${OUT_DIR}/release-policy-report.json" \
  --output "${OUT_DIR}/commitment-guard-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/commitment-guard-report.json" \
  --schema schemas/commitment-guard-report.schema.json \
  --report "${VALIDATION_DIR}/commitment-guard-report-validation.json"

echo "commitment guard report: ok"
