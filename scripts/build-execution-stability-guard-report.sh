#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.execution_stability_guard.cli \
  --intake-release-window-report "${OUT_DIR}/intake-release-window-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --post-release-monitor-report "${OUT_DIR}/post-release-monitor-report.json" \
  --output "${OUT_DIR}/execution-stability-guard-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-stability-guard-report.json" \
  --schema schemas/execution-stability-guard-report.schema.json \
  --report "${VALIDATION_DIR}/execution-stability-guard-report-validation.json"

echo "execution stability guard report: ok"
