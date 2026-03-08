#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_capacity.cli \
  --intake-guard-report "${OUT_DIR}/intake-guard-report.json" \
  --delivery-bandwidth-report "${OUT_DIR}/delivery-bandwidth-report.json" \
  --queue-pressure-report "${OUT_DIR}/queue-pressure-report.json" \
  --output "${OUT_DIR}/intake-capacity-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-capacity-report.json" \
  --schema schemas/intake-capacity-report.schema.json \
  --report "${VALIDATION_DIR}/intake-capacity-report-validation.json"

echo "intake capacity report: ok"
