#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_resumption_policy.cli \
  --scope-reentry-readiness-report "${OUT_DIR}/scope-reentry-readiness-report.json" \
  --intake-transition-policy-report "${OUT_DIR}/intake-transition-policy-report.json" \
  --delivery-temperature-report "${OUT_DIR}/delivery-temperature-report.json" \
  --output "${OUT_DIR}/intake-resumption-policy-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-resumption-policy-report.json" \
  --schema schemas/intake-resumption-policy-report.schema.json \
  --report "${VALIDATION_DIR}/intake-resumption-policy-report-validation.json"

echo "intake resumption policy report: ok"
