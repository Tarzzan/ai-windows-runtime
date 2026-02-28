#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.quality_gate.cli \
  --execution-report "${OUT_DIR}/execution-report.json" \
  --kpi-report "${OUT_DIR}/kpi-report.json" \
  --trend-report "${OUT_DIR}/trend-report.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --crash-signature-report "${OUT_DIR}/crash-signature-report.json" \
  --installer-phase-report "${OUT_DIR}/installer-phase-report.json" \
  --proposal-review-checklist "${OUT_DIR}/proposal-review-checklist.json" \
  --productization-readiness "${OUT_DIR}/productization-readiness.json" \
  --output "${OUT_DIR}/quality-gate-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/quality-gate-report.json" \
  --schema schemas/quality-gate-report.schema.json \
  --report "${VALIDATION_DIR}/quality-gate-report-validation.json"

echo "quality gate report: ok"

