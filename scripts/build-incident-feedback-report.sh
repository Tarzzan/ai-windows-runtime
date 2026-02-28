#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.incident_feedback.cli \
  --post-release-monitor-report "${OUT_DIR}/post-release-monitor-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --hook-backlog-report "${OUT_DIR}/hook-backlog-report.json" \
  --output "${OUT_DIR}/incident-feedback-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/incident-feedback-report.json" \
  --schema schemas/incident-feedback-report.schema.json \
  --report "${VALIDATION_DIR}/incident-feedback-report-validation.json"

echo "incident feedback report: ok"
