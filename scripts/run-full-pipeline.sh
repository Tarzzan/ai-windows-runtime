#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
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

echo "full pipeline: ok"
