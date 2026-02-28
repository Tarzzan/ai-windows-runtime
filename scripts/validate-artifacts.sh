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

if [[ -f "${OUT_DIR}/root-cause-summary.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/root-cause-summary.json" \
    --schema schemas/root-cause-summary.schema.json \
    --report "${REPORT_DIR}/root-cause-summary-validation.json"
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

if [[ -f "${OUT_DIR}/compatibility-matrix.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/compatibility-matrix.json" \
    --schema schemas/compatibility-matrix.schema.json \
    --report "${REPORT_DIR}/compatibility-matrix-validation.json"
fi

if [[ -f "${OUT_DIR}/alpha-release-checklist.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/alpha-release-checklist.json" \
    --schema schemas/alpha-release-checklist.schema.json \
    --report "${REPORT_DIR}/alpha-release-checklist-validation.json"
fi

if [[ -f "${OUT_DIR}/release-bundle-manifest.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-bundle-manifest.json" \
    --schema schemas/release-bundle-manifest.schema.json \
    --report "${REPORT_DIR}/release-bundle-manifest-validation.json"
fi

if [[ -f "${OUT_DIR}/productization-readiness.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/productization-readiness.json" \
    --schema schemas/productization-readiness.schema.json \
    --report "${REPORT_DIR}/productization-readiness-validation.json"
fi

if [[ -f "${OUT_DIR}/repro-package.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/repro-package.json" \
    --schema schemas/repro-package.schema.json \
    --report "${REPORT_DIR}/repro-package-validation.json"
fi

echo "artifact validation: ok"
