#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
BASELINE_EXECUTION_REPORT="${BASELINE_EXECUTION_REPORT:-}"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.trace_collector.cli \
  --input examples/sample-trace.log \
  --output "${OUT_DIR}/trace.json"

"${PYTHON_BIN}" -m compat_runtime.gap_detector.cli \
  --trace "${OUT_DIR}/trace.json" \
  --output "${OUT_DIR}/gaps.json"

"${PYTHON_BIN}" -m compat_runtime.patch_orchestrator.cli \
  --gaps "${OUT_DIR}/gaps.json" \
  --output "${OUT_DIR}/patch-plan.json"

"${PYTHON_BIN}" -m compat_runtime.telemetry_adapter.cli \
  --telemetry examples/sample-runtime-telemetry.json \
  --output "${OUT_DIR}/runtime-trace.json"

"${PYTHON_BIN}" -m compat_runtime.gap_detector.cli \
  --trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/runtime-gaps.json"

"${PYTHON_BIN}" -m compat_runtime.patch_orchestrator.cli \
  --gaps "${OUT_DIR}/runtime-gaps.json" \
  --output "${OUT_DIR}/runtime-patch-plan.json"

scripts/validate-artifacts.sh "$OUT_DIR"

"${PYTHON_BIN}" -m compat_runtime.reporting.cli \
  --trace "${OUT_DIR}/trace.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --trace-validation "${VALIDATION_DIR}/trace-validation.json" \
  --gaps-validation "${VALIDATION_DIR}/gaps-validation.json" \
  --patch-plan-validation "${VALIDATION_DIR}/patch-plan-validation.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --runtime-gaps "${OUT_DIR}/runtime-gaps.json" \
  --runtime-patch-plan "${OUT_DIR}/runtime-patch-plan.json" \
  --runtime-trace-validation "${VALIDATION_DIR}/runtime-trace-validation.json" \
  --output "${OUT_DIR}/execution-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-report.json" \
  --schema schemas/execution-report.schema.json \
  --report "${VALIDATION_DIR}/execution-report-validation.json"

if [[ -n "${BASELINE_EXECUTION_REPORT}" && -f "${BASELINE_EXECUTION_REPORT}" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.trend_report.cli \
    --current "${OUT_DIR}/execution-report.json" \
    --baseline "${BASELINE_EXECUTION_REPORT}" \
    --history "${BASELINE_EXECUTION_REPORT}" "${OUT_DIR}/execution-report.json" \
    --output "${OUT_DIR}/trend-report.json"
else
  "${PYTHON_BIN}" -m compat_runtime.trend_report.cli \
    --current "${OUT_DIR}/execution-report.json" \
    --history "${OUT_DIR}/execution-report.json" \
    --output "${OUT_DIR}/trend-report.json"
fi

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/trend-report.json" \
  --schema schemas/trend-report.schema.json \
  --report "${VALIDATION_DIR}/trend-report-validation.json"

REPORT_LIST=("${OUT_DIR}/execution-report.json")
if [[ -n "${BASELINE_EXECUTION_REPORT}" && -f "${BASELINE_EXECUTION_REPORT}" ]]; then
  REPORT_LIST=("${BASELINE_EXECUTION_REPORT}" "${OUT_DIR}/execution-report.json")
fi

"${PYTHON_BIN}" -m compat_runtime.kpi_tracker.cli \
  --reports "${REPORT_LIST[@]}" \
  --trend "${OUT_DIR}/trend-report.json" \
  --output "${OUT_DIR}/kpi-report.json" \
  --dashboard-output "${OUT_DIR}/dashboard-timeseries.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/kpi-report.json" \
  --schema schemas/kpi-report.schema.json \
  --report "${VALIDATION_DIR}/kpi-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/dashboard-timeseries.json" \
  --schema schemas/dashboard-timeseries.schema.json \
  --report "${VALIDATION_DIR}/dashboard-timeseries-validation.json"

echo "full pipeline: ok"
