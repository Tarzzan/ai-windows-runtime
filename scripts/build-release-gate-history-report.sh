#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.release_gate_history.cli \
  --dashboard-timeseries "${OUT_DIR}/dashboard-timeseries.json" \
  --trend-report "${OUT_DIR}/trend-report.json" \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --output "${OUT_DIR}/release-gate-history-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-gate-history-report.json" \
  --schema schemas/release-gate-history-report.schema.json \
  --report "${VALIDATION_DIR}/release-gate-history-report-validation.json"

echo "release gate history report: ok"
