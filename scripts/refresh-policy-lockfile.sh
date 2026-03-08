#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

LOCKFILE_PATH="${COMPAT_POLICY_LOCKFILE:-${ROOT_DIR}/config/active-policy.lock.json}"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

scripts/export-active-policy.sh "${TMP_DIR}" >/dev/null
mkdir -p "$(dirname "${LOCKFILE_PATH}")"
cp "${TMP_DIR}/active-policy.json" "${LOCKFILE_PATH}"

echo "policy lockfile refresh: ok (${LOCKFILE_PATH})"
