#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

LOCKFILE_PATH="${COMPAT_POLICY_LOCKFILE:-${ROOT_DIR}/config/active-policy.lock.json}"
FIX_MODE=0
if [[ "${1:-}" == "--fix" ]]; then
  FIX_MODE=1
fi
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

scripts/check-policy-config.sh "${TMP_DIR}" >/dev/null
scripts/export-active-policy.sh "${TMP_DIR}" >/dev/null

set +e
COMPAT_POLICY_LOCKFILE="${LOCKFILE_PATH}" scripts/check-policy-drift.sh "${TMP_DIR}" >/dev/null
STATUS=$?
set -e

if [[ ${STATUS} -ne 0 ]]; then
  if [[ ${FIX_MODE} -eq 1 ]]; then
    COMPAT_POLICY_LOCKFILE="${LOCKFILE_PATH}" scripts/refresh-policy-lockfile.sh >/dev/null
    echo "policy lockfile sync: fixed (${LOCKFILE_PATH})"
    exit 0
  fi

  echo "policy lockfile sync: drift detected" >&2
  echo "policy lockfile sync: run 'scripts/refresh-policy-lockfile.sh' to update lockfile" >&2
  exit ${STATUS}
fi

echo "policy lockfile sync: ok"
