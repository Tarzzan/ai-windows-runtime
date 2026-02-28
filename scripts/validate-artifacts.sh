#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
REPORT_DIR="${OUT_DIR}/validation"
mkdir -p "$REPORT_DIR"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/trace.json" \
  --schema schemas/trace.schema.json \
  --report "${REPORT_DIR}/trace-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/gaps.json" \
  --schema schemas/gaps.schema.json \
  --report "${REPORT_DIR}/gaps-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/patch-plan.json" \
  --schema schemas/patch-plan.schema.json \
  --report "${REPORT_DIR}/patch-plan-validation.json"

if [[ -f "${OUT_DIR}/runtime-trace.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/runtime-trace.json" \
    --schema schemas/trace.schema.json \
    --report "${REPORT_DIR}/runtime-trace-validation.json"
fi

if [[ -f "${OUT_DIR}/execution-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/execution-report.json" \
    --schema schemas/execution-report.schema.json \
    --report "${REPORT_DIR}/execution-report-validation.json"
fi

if [[ -f "${OUT_DIR}/trend-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/trend-report.json" \
    --schema schemas/trend-report.schema.json \
    --report "${REPORT_DIR}/trend-report-validation.json"
fi

if [[ -f "${OUT_DIR}/kpi-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/kpi-report.json" \
    --schema schemas/kpi-report.schema.json \
    --report "${REPORT_DIR}/kpi-report-validation.json"
fi

if [[ -f "${OUT_DIR}/dashboard-timeseries.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/dashboard-timeseries.json" \
    --schema schemas/dashboard-timeseries.schema.json \
    --report "${REPORT_DIR}/dashboard-timeseries-validation.json"
fi

echo "artifact validation: ok"
