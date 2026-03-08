#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

RELEASE_POLICY_ARGS=()
if [[ -f "${OUT_DIR}/release-policy-report.json" ]]; then
  RELEASE_POLICY_ARGS=(--release-policy-report "${OUT_DIR}/release-policy-report.json")
fi

"${PYTHON_BIN}" -m compat_runtime.release_brief.cli \
  --pilot-readiness-report "${OUT_DIR}/pilot-readiness-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --release-gate-history-report "${OUT_DIR}/release-gate-history-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  "${RELEASE_POLICY_ARGS[@]}" \
  --output "${OUT_DIR}/release-brief-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-brief-report.json" \
  --schema schemas/release-brief-report.schema.json \
  --report "${VALIDATION_DIR}/release-brief-report-validation.json"

echo "release brief report: ok"
