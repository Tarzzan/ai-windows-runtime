#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.next_cycle_bootstrap.cli \
  --release-retrospective-report "${OUT_DIR}/release-retrospective-report.json" \
  --backlog-refresh-report "${OUT_DIR}/backlog-refresh-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --delivery-signoff-report "${OUT_DIR}/delivery-signoff-report.json" \
  --output "${OUT_DIR}/next-cycle-bootstrap-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/next-cycle-bootstrap-report.json" \
  --schema schemas/next-cycle-bootstrap-report.schema.json \
  --report "${VALIDATION_DIR}/next-cycle-bootstrap-report-validation.json"

echo "next-cycle bootstrap report: ok"
