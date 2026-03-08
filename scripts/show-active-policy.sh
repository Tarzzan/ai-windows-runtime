#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

"${PYTHON_BIN}" - <<'PY'
import json
import os
from pathlib import Path

from compat_runtime.common.policy import load_alpha_gating_policy

repo_root = Path.cwd()
policy_path = Path(
    os.environ.get(
        "COMPAT_POLICY_PATH",
        str(repo_root / "config" / "alpha-gating-policy.json"),
    )
)
profile = os.environ.get("COMPAT_POLICY_PROFILE", "alpha")

payload = {
    "policy_path": str(policy_path),
    "policy_profile": profile,
    "policy": load_alpha_gating_policy(),
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
PY
