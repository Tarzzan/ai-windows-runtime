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

"${PYTHON_BIN}" -m compat_runtime.risk_watchlist.cli \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --hook-backlog-report "${OUT_DIR}/hook-backlog-report.json" \
  --runtime-signal-report "${OUT_DIR}/runtime-signal-report.json" \
  "${RELEASE_POLICY_ARGS[@]}" \
  --output "${OUT_DIR}/risk-watchlist-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/risk-watchlist-report.json" \
  --schema schemas/risk-watchlist-report.schema.json \
  --report "${VALIDATION_DIR}/risk-watchlist-report-validation.json"

echo "risk watchlist report: ok"
