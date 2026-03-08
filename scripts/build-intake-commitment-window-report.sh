#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_commitment_window.cli \
  --delivery-safety-margin-report "${OUT_DIR}/delivery-safety-margin-report.json" \
  --intake-release-window-report "${OUT_DIR}/intake-release-window-report.json" \
  --execution-stability-guard-report "${OUT_DIR}/execution-stability-guard-report.json" \
  --output "${OUT_DIR}/intake-commitment-window-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-commitment-window-report.json" \
  --schema schemas/intake-commitment-window-report.schema.json \
  --report "${VALIDATION_DIR}/intake-commitment-window-report-validation.json"

echo "intake commitment window report: ok"
