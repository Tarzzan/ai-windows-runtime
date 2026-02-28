#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
BASELINE_PATCH_PLAN="${BASELINE_PATCH_PLAN:-}"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

DIFF_ARGS=(
  --current "${OUT_DIR}/patch-plan.json"
  --current-label "current-base"
  --output "${OUT_DIR}/patch-plan-diff.json"
)
if [[ -n "${BASELINE_PATCH_PLAN}" && -f "${BASELINE_PATCH_PLAN}" ]]; then
  DIFF_ARGS+=(--baseline "${BASELINE_PATCH_PLAN}" --baseline-label "baseline-base")
fi

"${PYTHON_BIN}" -m compat_runtime.patch_plan_diff.cli "${DIFF_ARGS[@]}"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/patch-plan-diff.json" \
  --schema schemas/patch-plan-diff.schema.json \
  --report "${VALIDATION_DIR}/patch-plan-diff-validation.json"

echo "patch plan diff: ok"

