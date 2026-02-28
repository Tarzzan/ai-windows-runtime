#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.test_impact.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --root-cause "${OUT_DIR}/root-cause-summary.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --output "${OUT_DIR}/test-impact-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/test-impact-report.json" \
  --schema schemas/test-impact-report.schema.json \
  --report "${VALIDATION_DIR}/test-impact-report-validation.json"

echo "test impact report: ok"

