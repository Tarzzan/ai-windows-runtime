#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"
export OUT_DIR

"${PYTHON_BIN}" - <<'PY'
import os
from pathlib import Path

from compat_runtime.common.io import write_json
from compat_runtime.common.policy import load_alpha_gating_policy

out_dir = Path(os.environ["OUT_DIR"])
profile = os.environ.get("COMPAT_POLICY_PROFILE", "alpha")

artifact = {
    "artifact_version": "1.0",
    "policy_profile": profile,
    "policy": load_alpha_gating_policy(),
}
write_json(str(out_dir / "active-policy.json"), artifact)
PY

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/active-policy.json" \
  --schema schemas/active-policy.schema.json \
  --report "${VALIDATION_DIR}/active-policy-validation.json"

echo "active policy export: ok"
