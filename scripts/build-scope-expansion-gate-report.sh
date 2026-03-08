#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.scope_expansion_gate.cli \
  --intake-expansion-policy-report "${OUT_DIR}/intake-expansion-policy-report.json" \
  --scope-unlock-gate-report "${OUT_DIR}/scope-unlock-gate-report.json" \
  --release-policy-report "${OUT_DIR}/release-policy-report.json" \
  --output "${OUT_DIR}/scope-expansion-gate-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/scope-expansion-gate-report.json" \
  --schema schemas/scope-expansion-gate-report.schema.json \
  --report "${VALIDATION_DIR}/scope-expansion-gate-report-validation.json"

echo "scope expansion gate report: ok"
