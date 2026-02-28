#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.remediation_sprint.cli \
  --ownership-assignment-report "${OUT_DIR}/ownership-assignment-report.json" \
  --execution-burndown-report "${OUT_DIR}/execution-burndown-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --output "${OUT_DIR}/remediation-sprint-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/remediation-sprint-report.json" \
  --schema schemas/remediation-sprint-report.schema.json \
  --report "${VALIDATION_DIR}/remediation-sprint-report-validation.json"

echo "remediation sprint report: ok"
