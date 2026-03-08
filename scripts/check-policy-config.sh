#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "${VALIDATION_DIR}"

POLICY_PATH="${COMPAT_POLICY_PATH:-${ROOT_DIR}/config/alpha-gating-policy.json}"
if [[ ! -f "${POLICY_PATH}" ]]; then
  echo "policy config check: missing policy file ${POLICY_PATH}" >&2
  exit 1
fi

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${POLICY_PATH}" \
  --schema schemas/alpha-gating-policy-config.schema.json \
  --report "${VALIDATION_DIR}/alpha-gating-policy-config-validation.json"

export POLICY_PATH
"${PYTHON_BIN}" - <<'PY'
import json
import os
from pathlib import Path
from typing import Any

from compat_runtime.common.policy import load_alpha_gating_policy


def _expect_type(
    container: dict[str, Any],
    key: str,
    expected_type: type,
    context: str,
    allow_bool_for_int: bool = False,
) -> None:
    if key not in container:
        return
    value = container[key]
    if expected_type is int:
        if not isinstance(value, int) or (isinstance(value, bool) and not allow_bool_for_int):
            raise SystemExit(f"policy config check: {context}.{key} must be integer")
        if value < 0:
            raise SystemExit(f"policy config check: {context}.{key} must be >= 0")
        return
    if not isinstance(value, expected_type):
        raise SystemExit(
            f"policy config check: {context}.{key} must be {expected_type.__name__}"
        )


def _expect_string_array(container: dict[str, Any], key: str, context: str) -> None:
    if key not in container:
        return
    value = container[key]
    if not isinstance(value, list):
        raise SystemExit(f"policy config check: {context}.{key} must be array")
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise SystemExit(f"policy config check: {context}.{key}[{idx}] must be string")


def _validate_profile_config(profile_name: str, profile_config: dict[str, Any]) -> None:
    quality_gate = profile_config.get("quality_gate")
    if quality_gate is not None:
        if not isinstance(quality_gate, dict):
            raise SystemExit(
                f"policy config check: profiles.{profile_name}.quality_gate must be object"
            )
        _expect_type(
            quality_gate,
            "kpi_high_without_failed_runs_pass",
            bool,
            f"profiles.{profile_name}.quality_gate",
        )
        _expect_type(
            quality_gate,
            "office_limited_as_pass",
            bool,
            f"profiles.{profile_name}.quality_gate",
        )
        _expect_type(
            quality_gate,
            "trend_regression_warn_threshold",
            int,
            f"profiles.{profile_name}.quality_gate",
        )
        _expect_type(
            quality_gate,
            "proposal_high_risk_warn_threshold",
            int,
            f"profiles.{profile_name}.quality_gate",
        )
        _expect_type(
            quality_gate,
            "installer_error_warn_threshold",
            int,
            f"profiles.{profile_name}.quality_gate",
        )

    release_decision = profile_config.get("release_decision")
    if release_decision is not None:
        if not isinstance(release_decision, dict):
            raise SystemExit(
                f"policy config check: profiles.{profile_name}.release_decision must be object"
            )
        _expect_type(
            release_decision,
            "warning_budget",
            int,
            f"profiles.{profile_name}.release_decision",
        )

    release_readiness = profile_config.get("release_readiness")
    if release_readiness is not None:
        if not isinstance(release_readiness, dict):
            raise SystemExit(
                f"policy config check: profiles.{profile_name}.release_readiness must be object"
            )
        _expect_type(
            release_readiness,
            "kpi_high_without_failed_runs_pass",
            bool,
            f"profiles.{profile_name}.release_readiness",
        )
        _expect_type(
            release_readiness,
            "regression_warn_threshold",
            int,
            f"profiles.{profile_name}.release_readiness",
        )

    pilot_readiness = profile_config.get("pilot_readiness")
    if pilot_readiness is not None:
        if not isinstance(pilot_readiness, dict):
            raise SystemExit(
                f"policy config check: profiles.{profile_name}.pilot_readiness must be object"
            )
        _expect_type(
            pilot_readiness,
            "limited_pilot_min_score",
            int,
            f"profiles.{profile_name}.pilot_readiness",
        )
        _expect_type(
            pilot_readiness,
            "limited_pilot_max_blocking_tasks",
            int,
            f"profiles.{profile_name}.pilot_readiness",
        )
        _expect_type(
            pilot_readiness,
            "limited_pilot_max_iterations_to_go",
            int,
            f"profiles.{profile_name}.pilot_readiness",
        )
        _expect_string_array(
            pilot_readiness,
            "limited_pilot_allowed_gates",
            f"profiles.{profile_name}.pilot_readiness",
        )
        _expect_string_array(
            pilot_readiness,
            "limited_pilot_allowed_decisions",
            f"profiles.{profile_name}.pilot_readiness",
        )

    launch_readiness = profile_config.get("launch_readiness")
    if launch_readiness is not None:
        if not isinstance(launch_readiness, dict):
            raise SystemExit(
                f"policy config check: profiles.{profile_name}.launch_readiness must be object"
            )
        _expect_string_array(
            launch_readiness,
            "ready_allowed_gates",
            f"profiles.{profile_name}.launch_readiness",
        )
        _expect_string_array(
            launch_readiness,
            "ready_allowed_office_statuses",
            f"profiles.{profile_name}.launch_readiness",
        )
        _expect_string_array(
            launch_readiness,
            "ready_allowed_pilot_recommendations",
            f"profiles.{profile_name}.launch_readiness",
        )


policy_path = Path(os.environ["POLICY_PATH"])
payload = json.loads(policy_path.read_text(encoding="utf-8"))
profiles = payload.get("profiles", {})
default_profile = payload.get("default_profile")

if not isinstance(profiles, dict) or not profiles:
    raise SystemExit("policy config check: expected non-empty profiles map")

if default_profile not in profiles:
    raise SystemExit(
        f"policy config check: default_profile '{default_profile}' is missing from profiles"
    )

for profile_name in sorted(profiles.keys()):
    profile_config = profiles[profile_name]
    if not isinstance(profile_config, dict):
        raise SystemExit(f"policy config check: profiles.{profile_name} must be object")
    _validate_profile_config(str(profile_name), profile_config)

    os.environ["COMPAT_POLICY_PROFILE"] = str(profile_name)
    load_alpha_gating_policy.cache_clear()
    merged_policy = load_alpha_gating_policy()
    if not isinstance(merged_policy, dict) or not merged_policy:
        raise SystemExit(
            f"policy config check: profile '{profile_name}' produced invalid merged policy"
        )
PY

echo "policy config check: ok"
