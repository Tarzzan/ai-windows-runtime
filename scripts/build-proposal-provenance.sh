#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.proposal_provenance.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --trace "${OUT_DIR}/trace.json" \
  --output "${OUT_DIR}/proposal-provenance.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/proposal-provenance.json" \
  --schema schemas/proposal-provenance.schema.json \
  --report "${VALIDATION_DIR}/proposal-provenance-validation.json"

echo "proposal provenance: ok"

