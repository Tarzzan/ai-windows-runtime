#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.proposal_risk.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --patch-plan-diff "${OUT_DIR}/patch-plan-diff.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --rollback-hints "${OUT_DIR}/rollback-hints.json" \
  --output "${OUT_DIR}/proposal-risk-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/proposal-risk-report.json" \
  --schema schemas/proposal-risk-report.schema.json \
  --report "${VALIDATION_DIR}/proposal-risk-report-validation.json"

echo "proposal risk report: ok"

