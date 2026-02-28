#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.release_retrospective.cli \
  --delivery-signoff-report "${OUT_DIR}/delivery-signoff-report.json" \
  --readiness-delta-report "${OUT_DIR}/readiness-delta-report.json" \
  --release-gate-history-report "${OUT_DIR}/release-gate-history-report.json" \
  --output "${OUT_DIR}/release-retrospective-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-retrospective-report.json" \
  --schema schemas/release-retrospective-report.schema.json \
  --report "${VALIDATION_DIR}/release-retrospective-report-validation.json"

echo "release retrospective report: ok"
