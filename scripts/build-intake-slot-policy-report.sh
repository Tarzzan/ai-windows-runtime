#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_slot_policy.cli \
  --throughput-guard-band-report "${OUT_DIR}/throughput-guard-band-report.json" \
  --intake-commitment-window-report "${OUT_DIR}/intake-commitment-window-report.json" \
  --intake-queue-policy-report "${OUT_DIR}/intake-queue-policy-report.json" \
  --output "${OUT_DIR}/intake-slot-policy-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-slot-policy-report.json" \
  --schema schemas/intake-slot-policy-report.schema.json \
  --report "${VALIDATION_DIR}/intake-slot-policy-report-validation.json"

echo "intake slot policy report: ok"
