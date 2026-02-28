#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.stakeholder_update.cli \
  --delivery-cockpit-report "${OUT_DIR}/delivery-cockpit-report.json" \
  --release-brief-report "${OUT_DIR}/release-brief-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/stakeholder-update-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/stakeholder-update-report.json" \
  --schema schemas/stakeholder-update-report.schema.json \
  --report "${VALIDATION_DIR}/stakeholder-update-report-validation.json"

echo "stakeholder update report: ok"
