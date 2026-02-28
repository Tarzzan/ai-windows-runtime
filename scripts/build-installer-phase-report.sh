#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.installer_phases.cli \
  --trace "${OUT_DIR}/trace.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/installer-phase-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/installer-phase-report.json" \
  --schema schemas/installer-phase-report.schema.json \
  --report "${VALIDATION_DIR}/installer-phase-report-validation.json"

echo "installer phase report: ok"

