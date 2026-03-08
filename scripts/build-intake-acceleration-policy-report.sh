#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_acceleration_policy.cli \
  --scope-acceleration-readiness-report "${OUT_DIR}/scope-acceleration-readiness-report.json" \
  --intake-expansion-policy-report "${OUT_DIR}/intake-expansion-policy-report.json" \
  --delivery-bandwidth-report "${OUT_DIR}/delivery-bandwidth-report.json" \
  --output "${OUT_DIR}/intake-acceleration-policy-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-acceleration-policy-report.json" \
  --schema schemas/intake-acceleration-policy-report.schema.json \
  --report "${VALIDATION_DIR}/intake-acceleration-policy-report-validation.json"

echo "intake acceleration policy report: ok"
