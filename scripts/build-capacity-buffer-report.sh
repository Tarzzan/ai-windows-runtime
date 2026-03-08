#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.capacity_buffer.cli \
  --execution-reserve-report "${OUT_DIR}/execution-reserve-report.json" \
  --owner-load-report "${OUT_DIR}/owner-load-report.json" \
  --backlog-refresh-report "${OUT_DIR}/backlog-refresh-report.json" \
  --output "${OUT_DIR}/capacity-buffer-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/capacity-buffer-report.json" \
  --schema schemas/capacity-buffer-report.schema.json \
  --report "${VALIDATION_DIR}/capacity-buffer-report-validation.json"

echo "capacity buffer report: ok"
