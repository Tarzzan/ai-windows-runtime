#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.artifact_health.cli \
  --validation-dir "${VALIDATION_DIR}" \
  --output "${OUT_DIR}/artifact-health-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/artifact-health-report.json" \
  --schema schemas/artifact-health-report.schema.json \
  --report "${VALIDATION_DIR}/artifact-health-report-validation.json"

echo "artifact health report: ok"
