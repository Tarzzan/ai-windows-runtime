#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="${1:-out}"
REPORT_DIR="${OUT_DIR}/validation"
mkdir -p "$REPORT_DIR"

python -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/trace.json" \
  --schema schemas/trace.schema.json \
  --report "${REPORT_DIR}/trace-validation.json"

python -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/gaps.json" \
  --schema schemas/gaps.schema.json \
  --report "${REPORT_DIR}/gaps-validation.json"

python -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/patch-plan.json" \
  --schema schemas/patch-plan.schema.json \
  --report "${REPORT_DIR}/patch-plan-validation.json"

if [[ -f "${OUT_DIR}/runtime-trace.json" ]]; then
  python -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/runtime-trace.json" \
    --schema schemas/trace.schema.json \
    --report "${REPORT_DIR}/runtime-trace-validation.json"
fi

echo "artifact validation: ok"
