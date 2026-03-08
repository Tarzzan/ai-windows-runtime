#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_queue_policy.cli \
  --capacity-buffer-report "${OUT_DIR}/capacity-buffer-report.json" \
  --delivery-intake-sync-report "${OUT_DIR}/delivery-intake-sync-report.json" \
  --commitment-guard-report "${OUT_DIR}/commitment-guard-report.json" \
  --output "${OUT_DIR}/intake-queue-policy-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-queue-policy-report.json" \
  --schema schemas/intake-queue-policy-report.schema.json \
  --report "${VALIDATION_DIR}/intake-queue-policy-report-validation.json"

echo "intake queue policy report: ok"
