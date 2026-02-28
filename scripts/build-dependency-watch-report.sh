#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.dependency_watch.cli \
  --productization-readiness "${OUT_DIR}/productization-readiness.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --execution-report "${OUT_DIR}/execution-report.json" \
  --output "${OUT_DIR}/dependency-watch-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/dependency-watch-report.json" \
  --schema schemas/dependency-watch-report.schema.json \
  --report "${VALIDATION_DIR}/dependency-watch-report-validation.json"

echo "dependency watch report: ok"
