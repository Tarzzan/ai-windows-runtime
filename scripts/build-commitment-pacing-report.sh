#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.commitment_pacing.cli \
  --admission-control-report "${OUT_DIR}/admission-control-report.json" \
  --backlog-refresh-report "${OUT_DIR}/backlog-refresh-report.json" \
  --delivery-bandwidth-report "${OUT_DIR}/delivery-bandwidth-report.json" \
  --output "${OUT_DIR}/commitment-pacing-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/commitment-pacing-report.json" \
  --schema schemas/commitment-pacing-report.schema.json \
  --report "${VALIDATION_DIR}/commitment-pacing-report-validation.json"

echo "commitment pacing report: ok"
