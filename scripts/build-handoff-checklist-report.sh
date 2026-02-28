#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.handoff_checklist.cli \
  --stakeholder-update-report "${OUT_DIR}/stakeholder-update-report.json" \
  --ownership-assignment-report "${OUT_DIR}/ownership-assignment-report.json" \
  --rollout-guardrails-report "${OUT_DIR}/rollout-guardrails-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --output "${OUT_DIR}/handoff-checklist-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/handoff-checklist-report.json" \
  --schema schemas/handoff-checklist-report.schema.json \
  --report "${VALIDATION_DIR}/handoff-checklist-report-validation.json"

echo "handoff checklist report: ok"
