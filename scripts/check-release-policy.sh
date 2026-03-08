#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="${1:-out}"

if ! command -v jq >/dev/null 2>&1; then
  echo "release policy check: missing dependency 'jq'" >&2
  exit 2
fi

QUALITY_GATE_FILE="${OUT_DIR}/quality-gate-report.json"
RELEASE_DECISION_FILE="${OUT_DIR}/release-decision-report.json"
LAUNCH_READINESS_FILE="${OUT_DIR}/launch-readiness-report.json"
POLICY_HEALTH_FILE="${OUT_DIR}/policy-health-report.json"

for f in "$QUALITY_GATE_FILE" "$RELEASE_DECISION_FILE" "$LAUNCH_READINESS_FILE" "$POLICY_HEALTH_FILE"; do
  if [[ ! -f "$f" ]]; then
    echo "release policy check: missing artifact $f" >&2
    exit 1
  fi
done

QUALITY_GATE="$(jq -r '.gate // "missing"' "$QUALITY_GATE_FILE")"
RELEASE_DECISION="$(jq -r '.decision // "missing"' "$RELEASE_DECISION_FILE")"
LAUNCH_STATUS="$(jq -r '.status // "missing"' "$LAUNCH_READINESS_FILE")"
POLICY_CONFIG_VALID="$(jq -r '.config_valid // false' "$POLICY_HEALTH_FILE")"
LOCKFILE_SYNC="$(jq -r '.lockfile_sync // false' "$POLICY_HEALTH_FILE")"
POLICY_COMPLIANCE_LEVEL="$(jq -r '.policy_compliance_level // "missing"' "$POLICY_HEALTH_FILE")"

if [[ "$POLICY_COMPLIANCE_LEVEL" == "missing" ]]; then
  if [[ "$POLICY_CONFIG_VALID" == "true" && "$LOCKFILE_SYNC" == "true" ]]; then
    POLICY_COMPLIANCE_LEVEL="compliant"
  elif [[ "$POLICY_CONFIG_VALID" == "true" || "$LOCKFILE_SYNC" == "true" ]]; then
    POLICY_COMPLIANCE_LEVEL="degraded"
  else
    POLICY_COMPLIANCE_LEVEL="non_compliant"
  fi
fi

if [[ "$QUALITY_GATE" != "pass" ]]; then
  echo "release policy check: expected quality gate 'pass', got '$QUALITY_GATE'" >&2
  exit 1
fi
if [[ "$RELEASE_DECISION" != "go" ]]; then
  echo "release policy check: expected release decision 'go', got '$RELEASE_DECISION'" >&2
  exit 1
fi
if [[ "$LAUNCH_STATUS" != "ready" ]]; then
  echo "release policy check: expected launch readiness 'ready', got '$LAUNCH_STATUS'" >&2
  exit 1
fi
if [[ "$POLICY_COMPLIANCE_LEVEL" != "compliant" ]]; then
  echo "release policy check: expected policy_compliance_level='compliant', got '$POLICY_COMPLIANCE_LEVEL'" >&2
  exit 1
fi

echo "release policy check: ok"
