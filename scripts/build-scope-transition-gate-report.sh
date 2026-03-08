#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_transition_gate.cli \
  --intake-pacing-window-report "${OUT_DIR}/intake-pacing-window-report.json" \
  --scope-freeze-guard-report "${OUT_DIR}/scope-freeze-guard-report.json" \
  --release-policy-report "${OUT_DIR}/release-policy-report.json" \
  --output "${OUT_DIR}/scope-transition-gate-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-transition-gate-report.json" \
  --schema schemas/scope-transition-gate-report.schema.json \
  --report "${VALIDATION_DIR}/scope-transition-gate-report-validation.json"

echo "scope transition gate report: ok"
