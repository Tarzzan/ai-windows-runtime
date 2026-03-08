#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "${OUT_DIR}" "${VALIDATION_DIR}"

ACTIVE_POLICY_FILE="${OUT_DIR}/active-policy.json"
LOCKFILE_PATH="${COMPAT_POLICY_LOCKFILE:-${ROOT_DIR}/config/active-policy.lock.json}"
POLICY_PATH="${COMPAT_POLICY_PATH:-${ROOT_DIR}/config/alpha-gating-policy.json}"
POLICY_PROFILE="${COMPAT_POLICY_PROFILE:-alpha}"
CONFIG_VALIDATION_FILE="${VALIDATION_DIR}/alpha-gating-policy-config-validation.json"

if [[ ! -f "${ACTIVE_POLICY_FILE}" ]]; then
  echo "policy health report: missing active policy artifact ${ACTIVE_POLICY_FILE}" >&2
  exit 1
fi

export ACTIVE_POLICY_FILE LOCKFILE_PATH POLICY_PATH POLICY_PROFILE CONFIG_VALIDATION_FILE
"${PYTHON_BIN}" - <<'PY'
import hashlib
import json
import os
from pathlib import Path

from compat_runtime.common.io import write_json


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_json(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


active_policy = Path(os.environ["ACTIVE_POLICY_FILE"])
lockfile_path = Path(os.environ["LOCKFILE_PATH"])
config_validation = Path(os.environ["CONFIG_VALIDATION_FILE"])

lockfile_exists = lockfile_path.exists()
lockfile_sync = False
notes: list[str] = []

if lockfile_exists:
    lockfile_sync = _normalized_json(active_policy) == _normalized_json(lockfile_path)
    if not lockfile_sync:
        notes.append("active policy differs from lockfile")
else:
    notes.append("lockfile is missing")

config_valid = False
if config_validation.exists():
    try:
        config_valid = bool(
            json.loads(config_validation.read_text(encoding="utf-8")).get("valid", False)
        )
    except Exception:
        config_valid = False
if not config_valid:
    notes.append("policy config validation missing or invalid")

artifact = {
    "artifact_version": "1.0",
    "policy_path": os.environ["POLICY_PATH"],
    "policy_profile": os.environ["POLICY_PROFILE"],
    "active_policy_sha256": _sha256(active_policy),
    "lockfile_path": str(lockfile_path),
    "lockfile_exists": lockfile_exists,
    "lockfile_sync": lockfile_sync,
    "config_valid": config_valid,
    "notes": notes,
}
write_json(str(active_policy.parent / "policy-health-report.json"), artifact)
PY

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/policy-health-report.json" \
  --schema schemas/policy-health-report.schema.json \
  --report "${VALIDATION_DIR}/policy-health-report-validation.json"

echo "policy health report: ok"
