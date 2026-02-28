#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.ops_runbook.cli \
  --rollout-guardrails-report "${OUT_DIR}/rollout-guardrails-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --handoff-checklist-report "${OUT_DIR}/handoff-checklist-report.json" \
  --output "${OUT_DIR}/ops-runbook-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/ops-runbook-report.json" \
  --schema schemas/ops-runbook-report.schema.json \
  --report "${VALIDATION_DIR}/ops-runbook-report-validation.json"

echo "ops runbook report: ok"
