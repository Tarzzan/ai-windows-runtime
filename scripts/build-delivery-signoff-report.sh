#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.delivery_signoff.cli \
  --release-packet-report "${OUT_DIR}/release-packet-report.json" \
  --ops-runbook-report "${OUT_DIR}/ops-runbook-report.json" \
  --dependency-watch-report "${OUT_DIR}/dependency-watch-report.json" \
  --readiness-delta-report "${OUT_DIR}/readiness-delta-report.json" \
  --launch-readiness-report "${OUT_DIR}/launch-readiness-report.json" \
  --output "${OUT_DIR}/delivery-signoff-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-signoff-report.json" \
  --schema schemas/delivery-signoff-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-signoff-report-validation.json"

echo "delivery signoff report: ok"
