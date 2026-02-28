#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

CURRENT_REPORT="${1:-out/execution-report.json}"
TREND_REPORT="${2:-out/trend-report.json}"
OUTPUT_PATH="${3:-out/kpi-report.json}"
DASHBOARD_PATH="${4:-out/dashboard-timeseries.json}"
VALIDATION_DIR="${5:-out/validation}"
BASELINE_REPORT="${BASELINE_EXECUTION_REPORT:-}"

mkdir -p "$(dirname "$OUTPUT_PATH")" "$(dirname "$DASHBOARD_PATH")" "${VALIDATION_DIR}"

REPORT_LIST=("${CURRENT_REPORT}")
if [[ -n "${BASELINE_REPORT}" && -f "${BASELINE_REPORT}" ]]; then
  REPORT_LIST=("${BASELINE_REPORT}" "${CURRENT_REPORT}")
fi

"${PYTHON_BIN}" -m compat_runtime.kpi_tracker.cli \
  --reports "${REPORT_LIST[@]}" \
  --trend "${TREND_REPORT}" \
  --output "${OUTPUT_PATH}" \
  --dashboard-output "${DASHBOARD_PATH}"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUTPUT_PATH}" \
  --schema schemas/kpi-report.schema.json \
  --report "${VALIDATION_DIR}/kpi-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${DASHBOARD_PATH}" \
  --schema schemas/dashboard-timeseries.schema.json \
  --report "${VALIDATION_DIR}/dashboard-timeseries-validation.json"

echo "kpi report: ok"
