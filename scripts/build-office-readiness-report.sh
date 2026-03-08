#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/out}"
VALIDATION_DIR="${OUT_DIR}/validation"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "${OUT_DIR}" "${VALIDATION_DIR}"

"${PYTHON_BIN}" -m compat_runtime.office_readiness.cli \
  --runtime-signal-report "${OUT_DIR}/runtime-signal-report.json" \
  --hook-backlog-report "${OUT_DIR}/hook-backlog-report.json" \
  --stability-window-report "${OUT_DIR}/stability-window-report.json" \
  --installer-phase-report "${OUT_DIR}/installer-phase-report.json" \
  --output "${OUT_DIR}/office-readiness-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/office-readiness-report.json" \
  --schema schemas/office-readiness-report.schema.json \
  --report "${VALIDATION_DIR}/office-readiness-report-validation.json"

echo "office readiness report: ok"

