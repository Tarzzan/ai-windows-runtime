#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.intake_release_window.cli \
  --flow-control-budget-report "${OUT_DIR}/flow-control-budget-report.json" \
  --intake-queue-policy-report "${OUT_DIR}/intake-queue-policy-report.json" \
  --admission-window-report "${OUT_DIR}/admission-window-report.json" \
  --output "${OUT_DIR}/intake-release-window-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/intake-release-window-report.json" \
  --schema schemas/intake-release-window-report.schema.json \
  --report "${VALIDATION_DIR}/intake-release-window-report-validation.json"

echo "intake release window report: ok"
