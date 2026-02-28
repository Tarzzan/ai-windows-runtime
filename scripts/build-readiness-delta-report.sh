#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.readiness_delta.cli \
  --launch-readiness-report "${OUT_DIR}/launch-readiness-report.json" \
  --delivery-cockpit-report "${OUT_DIR}/delivery-cockpit-report.json" \
  --release-gate-history-report "${OUT_DIR}/release-gate-history-report.json" \
  --output "${OUT_DIR}/readiness-delta-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/readiness-delta-report.json" \
  --schema schemas/readiness-delta-report.schema.json \
  --report "${VALIDATION_DIR}/readiness-delta-report-validation.json"

echo "readiness delta report: ok"
