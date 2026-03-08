#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_admission_gate.cli \
  --intake-transition-policy-report "${OUT_DIR}/intake-transition-policy-report.json" \
  --scope-freeze-guard-report "${OUT_DIR}/scope-freeze-guard-report.json" \
  --release-policy-report "${OUT_DIR}/release-policy-report.json" \
  --output "${OUT_DIR}/scope-admission-gate-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-admission-gate-report.json" \
  --schema schemas/scope-admission-gate-report.schema.json \
  --report "${VALIDATION_DIR}/scope-admission-gate-report-validation.json"

echo "scope admission gate report: ok"
