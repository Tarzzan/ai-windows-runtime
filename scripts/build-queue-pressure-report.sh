#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.queue_pressure.cli \
  --owner-load-report "${OUT_DIR}/owner-load-report.json" \
  --execution-throttle-report "${OUT_DIR}/execution-throttle-report.json" \
  --priority-corridor-report "${OUT_DIR}/priority-corridor-report.json" \
  --output "${OUT_DIR}/queue-pressure-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/queue-pressure-report.json" \
  --schema schemas/queue-pressure-report.schema.json \
  --report "${VALIDATION_DIR}/queue-pressure-report-validation.json"

echo "queue pressure report: ok"
