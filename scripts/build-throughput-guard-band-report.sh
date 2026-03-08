#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.throughput_guard_band.cli \
  --scope-lock-state-report "${OUT_DIR}/scope-lock-state-report.json" \
  --delivery-safety-margin-report "${OUT_DIR}/delivery-safety-margin-report.json" \
  --execution-reserve-report "${OUT_DIR}/execution-reserve-report.json" \
  --output "${OUT_DIR}/throughput-guard-band-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/throughput-guard-band-report.json" \
  --schema schemas/throughput-guard-band-report.schema.json \
  --report "${VALIDATION_DIR}/throughput-guard-band-report-validation.json"

echo "throughput guard band report: ok"
