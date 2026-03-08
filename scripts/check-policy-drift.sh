#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="${1:-out}"
ACTIVE_POLICY_FILE="${OUT_DIR}/active-policy.json"
LOCKFILE_PATH="${COMPAT_POLICY_LOCKFILE:-${ROOT_DIR}/config/active-policy.lock.json}"

if ! command -v jq >/dev/null 2>&1; then
  echo "policy drift check: missing dependency 'jq'" >&2
  exit 2
fi

if [[ ! -f "${ACTIVE_POLICY_FILE}" ]]; then
  echo "policy drift check: missing artifact ${ACTIVE_POLICY_FILE}" >&2
  exit 1
fi

if [[ ! -f "${LOCKFILE_PATH}" ]]; then
  echo "policy drift check: no lockfile (${LOCKFILE_PATH}), skipping"
  exit 0
fi

tmp_a="$(mktemp)"
tmp_b="$(mktemp)"
trap 'rm -f "${tmp_a}" "${tmp_b}"' EXIT

jq -S . "${ACTIVE_POLICY_FILE}" > "${tmp_a}"
jq -S . "${LOCKFILE_PATH}" > "${tmp_b}"

if ! cmp -s "${tmp_a}" "${tmp_b}"; then
  echo "policy drift check: active policy differs from lockfile ${LOCKFILE_PATH}" >&2
  diff -u "${tmp_b}" "${tmp_a}" >&2 || true
  exit 1
fi

echo "policy drift check: ok"
