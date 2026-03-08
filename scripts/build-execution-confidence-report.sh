#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

POLICY_HEALTH_ARGS=()
if [[ -f "${OUT_DIR}/policy-health-report.json" ]]; then
  POLICY_HEALTH_ARGS=(--policy-health-report "${OUT_DIR}/policy-health-report.json")
fi

"${PYTHON_BIN}" -m compat_runtime.execution_confidence.cli \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  "${POLICY_HEALTH_ARGS[@]}" \
  --output "${OUT_DIR}/execution-confidence-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-confidence-report.json" \
  --schema schemas/execution-confidence-report.schema.json \
  --report "${VALIDATION_DIR}/execution-confidence-report-validation.json"

echo "execution confidence report: ok"
