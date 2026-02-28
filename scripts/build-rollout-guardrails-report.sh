#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.rollout_guardrails.cli \
  --pilot-readiness-report "${OUT_DIR}/pilot-readiness-report.json" \
  --rollback-hints-report "${OUT_DIR}/rollback-hints.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --crash-signature-report "${OUT_DIR}/crash-signature-report.json" \
  --output "${OUT_DIR}/rollout-guardrails-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/rollout-guardrails-report.json" \
  --schema schemas/rollout-guardrails-report.schema.json \
  --report "${VALIDATION_DIR}/rollout-guardrails-report-validation.json"

echo "rollout guardrails report: ok"
