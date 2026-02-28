#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

CURRENT_REPORT="${1:-out/execution-report.json}"
BASELINE_REPORT="${2:-}"
OUTPUT_PATH="${3:-out/trend-report.json}"
VALIDATION_PATH="${4:-out/validation/trend-report-validation.json}"

mkdir -p "$(dirname "$OUTPUT_PATH")" "$(dirname "$VALIDATION_PATH")"

if [[ -n "${BASELINE_REPORT}" && -f "${BASELINE_REPORT}" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.trend_report.cli \
    --current "${CURRENT_REPORT}" \
    --baseline "${BASELINE_REPORT}" \
    --history "${BASELINE_REPORT}" "${CURRENT_REPORT}" \
    --output "${OUTPUT_PATH}"
else
  "${PYTHON_BIN}" -m compat_runtime.trend_report.cli \
    --current "${CURRENT_REPORT}" \
    --history "${CURRENT_REPORT}" \
    --output "${OUTPUT_PATH}"
fi

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUTPUT_PATH}" \
  --schema schemas/trend-report.schema.json \
  --report "${VALIDATION_PATH}"

echo "trend report: ok"
