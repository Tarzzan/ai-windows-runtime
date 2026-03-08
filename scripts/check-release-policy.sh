#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
REPORT_FILE="${OUT_DIR}/release-policy-report.json"
REPORT_VALIDATION_FILE="${VALIDATION_DIR}/release-policy-report-validation.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "release policy check: missing dependency 'jq'" >&2
  exit 2
fi

mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

QUALITY_GATE_FILE="${OUT_DIR}/quality-gate-report.json"
RELEASE_DECISION_FILE="${OUT_DIR}/release-decision-report.json"
LAUNCH_READINESS_FILE="${OUT_DIR}/launch-readiness-report.json"
POLICY_HEALTH_FILE="${OUT_DIR}/policy-health-report.json"

FAILURES=()
for f in "$QUALITY_GATE_FILE" "$RELEASE_DECISION_FILE" "$LAUNCH_READINESS_FILE" "$POLICY_HEALTH_FILE"; do
  if [[ ! -f "$f" ]]; then
    FAILURES+=("missing artifact $f")
  fi
done

QUALITY_GATE="missing"
RELEASE_DECISION="missing"
LAUNCH_STATUS="missing"
POLICY_CONFIG_VALID="false"
LOCKFILE_SYNC="false"
POLICY_COMPLIANCE_LEVEL="missing"

if [[ -f "$QUALITY_GATE_FILE" ]]; then
  QUALITY_GATE="$(jq -r '.gate // "missing"' "$QUALITY_GATE_FILE")"
fi
if [[ -f "$RELEASE_DECISION_FILE" ]]; then
  RELEASE_DECISION="$(jq -r '.decision // "missing"' "$RELEASE_DECISION_FILE")"
fi
if [[ -f "$LAUNCH_READINESS_FILE" ]]; then
  LAUNCH_STATUS="$(jq -r '.status // "missing"' "$LAUNCH_READINESS_FILE")"
fi
if [[ -f "$POLICY_HEALTH_FILE" ]]; then
  POLICY_CONFIG_VALID="$(jq -r '.config_valid // false' "$POLICY_HEALTH_FILE")"
  LOCKFILE_SYNC="$(jq -r '.lockfile_sync // false' "$POLICY_HEALTH_FILE")"
  POLICY_COMPLIANCE_LEVEL="$(jq -r '.policy_compliance_level // "missing"' "$POLICY_HEALTH_FILE")"
fi

if [[ "$POLICY_COMPLIANCE_LEVEL" == "missing" ]]; then
  if [[ "$POLICY_CONFIG_VALID" == "true" && "$LOCKFILE_SYNC" == "true" ]]; then
    POLICY_COMPLIANCE_LEVEL="compliant"
  elif [[ "$POLICY_CONFIG_VALID" == "true" || "$LOCKFILE_SYNC" == "true" ]]; then
    POLICY_COMPLIANCE_LEVEL="degraded"
  else
    POLICY_COMPLIANCE_LEVEL="non_compliant"
  fi
fi

CHECK_QUALITY_GATE=false
CHECK_RELEASE_DECISION=false
CHECK_LAUNCH_READY=false
CHECK_POLICY_COMPLIANT=false

if [[ "$QUALITY_GATE" != "pass" ]]; then
  FAILURES+=("expected quality gate 'pass', got '$QUALITY_GATE'")
else
  CHECK_QUALITY_GATE=true
fi
if [[ "$RELEASE_DECISION" != "go" ]]; then
  FAILURES+=("expected release decision 'go', got '$RELEASE_DECISION'")
else
  CHECK_RELEASE_DECISION=true
fi
if [[ "$LAUNCH_STATUS" != "ready" ]]; then
  FAILURES+=("expected launch readiness 'ready', got '$LAUNCH_STATUS'")
else
  CHECK_LAUNCH_READY=true
fi
if [[ "$POLICY_COMPLIANCE_LEVEL" != "compliant" ]]; then
  FAILURES+=("expected policy_compliance_level='compliant', got '$POLICY_COMPLIANCE_LEVEL'")
else
  CHECK_POLICY_COMPLIANT=true
fi

FAILURES_JSON="$(printf '%s\n' "${FAILURES[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')"
STATUS="pass"
if [[ "${#FAILURES[@]}" -gt 0 ]]; then
  STATUS="fail"
fi

jq -n \
  --arg generated_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  --arg status "$STATUS" \
  --arg quality_gate "$QUALITY_GATE" \
  --arg release_decision "$RELEASE_DECISION" \
  --arg launch_readiness "$LAUNCH_STATUS" \
  --arg policy_compliance_level "$POLICY_COMPLIANCE_LEVEL" \
  --argjson policy_config_valid "$POLICY_CONFIG_VALID" \
  --argjson policy_lockfile_sync "$LOCKFILE_SYNC" \
  --argjson quality_gate_ok "$CHECK_QUALITY_GATE" \
  --argjson release_decision_ok "$CHECK_RELEASE_DECISION" \
  --argjson launch_ready_ok "$CHECK_LAUNCH_READY" \
  --argjson policy_compliant_ok "$CHECK_POLICY_COMPLIANT" \
  --argjson failures "$FAILURES_JSON" \
  '{
    artifact_version: "1.0",
    generated_at: $generated_at,
    status: $status,
    summary: {
      quality_gate: $quality_gate,
      release_decision: $release_decision,
      launch_readiness: $launch_readiness,
      policy_config_valid: $policy_config_valid,
      policy_lockfile_sync: $policy_lockfile_sync,
      policy_compliance_level: $policy_compliance_level
    },
    checks: {
      quality_gate: $quality_gate_ok,
      release_decision: $release_decision_ok,
      launch_readiness: $launch_ready_ok,
      policy_compliance: $policy_compliant_ok
    },
    failures: $failures
  }' >"$REPORT_FILE"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "$REPORT_FILE" \
  --schema schemas/release-policy-report.schema.json \
  --report "$REPORT_VALIDATION_FILE"

if [[ "$STATUS" != "pass" ]]; then
  for failure in "${FAILURES[@]}"; do
    echo "release policy check: ${failure}" >&2
  done
  exit 1
fi

echo "release policy check: ok"
