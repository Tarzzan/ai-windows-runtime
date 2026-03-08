#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

RELEASE_DECISION_ARGS=(
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json"
  --alpha-release-checklist "${OUT_DIR}/alpha-release-checklist.json"
  --compatibility-matrix "${OUT_DIR}/compatibility-matrix.json"
  --productization-readiness "${OUT_DIR}/productization-readiness.json"
  --output "${OUT_DIR}/release-decision-report.json"
)
if [[ -f "${OUT_DIR}/office-readiness-report.json" ]]; then
  RELEASE_DECISION_ARGS+=(--office-readiness-report "${OUT_DIR}/office-readiness-report.json")
fi

"${PYTHON_BIN}" -m compat_runtime.release_decision.cli "${RELEASE_DECISION_ARGS[@]}"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-decision-report.json" \
  --schema schemas/release-decision-report.schema.json \
  --report "${VALIDATION_DIR}/release-decision-report-validation.json"

echo "release decision report: ok"
