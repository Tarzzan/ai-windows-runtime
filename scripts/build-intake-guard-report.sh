#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_guard.cli \
  --delivery-bandwidth-report "${OUT_DIR}/delivery-bandwidth-report.json" \
  --release-policy-report "${OUT_DIR}/release-policy-report.json" \
  --priority-corridor-report "${OUT_DIR}/priority-corridor-report.json" \
  --output "${OUT_DIR}/intake-guard-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-guard-report.json" \
  --schema schemas/intake-guard-report.schema.json \
  --report "${VALIDATION_DIR}/intake-guard-report-validation.json"

echo "intake guard report: ok"
