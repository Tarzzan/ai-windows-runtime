#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.launch_readiness.cli \
  --handoff-checklist-report "${OUT_DIR}/handoff-checklist-report.json" \
  --validation-coverage-report "${OUT_DIR}/validation-coverage-report.json" \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --pilot-readiness-report "${OUT_DIR}/pilot-readiness-report.json" \
  --output "${OUT_DIR}/launch-readiness-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/launch-readiness-report.json" \
  --schema schemas/launch-readiness-report.schema.json \
  --report "${VALIDATION_DIR}/launch-readiness-report-validation.json"

echo "launch readiness report: ok"
