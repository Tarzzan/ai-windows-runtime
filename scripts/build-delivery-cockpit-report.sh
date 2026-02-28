#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.delivery_cockpit.cli \
  --release-brief-report "${OUT_DIR}/release-brief-report.json" \
  --remediation-sprint-report "${OUT_DIR}/remediation-sprint-report.json" \
  --artifact-health-report "${OUT_DIR}/artifact-health-report.json" \
  --output "${OUT_DIR}/delivery-cockpit-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-cockpit-report.json" \
  --schema schemas/delivery-cockpit-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-cockpit-report-validation.json"

echo "delivery cockpit report: ok"
