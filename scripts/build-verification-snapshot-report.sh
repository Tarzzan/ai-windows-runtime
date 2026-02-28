#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.verification_snapshot.cli \
  --validation-coverage-report "${OUT_DIR}/validation-coverage-report.json" \
  --next-cycle-bootstrap-report "${OUT_DIR}/next-cycle-bootstrap-report.json" \
  --delivery-signoff-report "${OUT_DIR}/delivery-signoff-report.json" \
  --output "${OUT_DIR}/verification-snapshot-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/verification-snapshot-report.json" \
  --schema schemas/verification-snapshot-report.schema.json \
  --report "${VALIDATION_DIR}/verification-snapshot-report-validation.json"

echo "verification snapshot report: ok"
