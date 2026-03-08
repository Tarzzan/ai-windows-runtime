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

"${PYTHON_BIN}" -m compat_runtime.release_packet.cli \
  --launch-readiness-report "${OUT_DIR}/launch-readiness-report.json" \
  --release-bundle-manifest "${OUT_DIR}/release-bundle-manifest.json" \
  --stakeholder-update-report "${OUT_DIR}/stakeholder-update-report.json" \
  "${POLICY_HEALTH_ARGS[@]}" \
  --output "${OUT_DIR}/release-packet-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-packet-report.json" \
  --schema schemas/release-packet-report.schema.json \
  --report "${VALIDATION_DIR}/release-packet-report-validation.json"

echo "release packet report: ok"
