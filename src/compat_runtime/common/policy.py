from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any


DEFAULT_ALPHA_GATING_POLICY: dict[str, Any] = {
    "quality_gate": {
        "kpi_high_without_failed_runs_pass": True,
        "trend_regression_warn_threshold": 4,
        "proposal_high_risk_warn_threshold": 3,
        "installer_error_warn_threshold": 5,
        "office_limited_as_pass": True,
    },
    "release_decision": {
        "warning_budget": 2,
    },
    "release_readiness": {
        "kpi_high_without_failed_runs_pass": True,
        "regression_warn_threshold": 4,
    },
    "pilot_readiness": {
        "limited_pilot_min_score": 60,
        "limited_pilot_max_blocking_tasks": 4,
        "limited_pilot_max_iterations_to_go": 4,
        "limited_pilot_allowed_gates": ["pass", "warn"],
        "limited_pilot_allowed_decisions": ["go", "hold"],
    },
    "launch_readiness": {
        "ready_allowed_gates": ["pass", "warn"],
        "ready_allowed_office_statuses": ["ready", "limited", "not_provided"],
        "ready_allowed_pilot_recommendations": ["ready", "limited_pilot"],
    },
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key, value in base.items():
        merged[key] = value

    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = value
    return merged


@lru_cache(maxsize=1)
def load_alpha_gating_policy() -> dict[str, Any]:
    policy_path = Path(
        os.environ.get(
            "COMPAT_POLICY_PATH",
            str(_repo_root() / "config" / "alpha-gating-policy.json"),
        )
    )
    if not policy_path.exists():
        return DEFAULT_ALPHA_GATING_POLICY

    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive path
        raise RuntimeError(f"invalid alpha gating policy file: {policy_path}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"invalid alpha gating policy format: {policy_path}")

    policy_override: dict[str, Any]
    profiles = payload.get("profiles")
    if isinstance(profiles, dict):
        selected_profile = os.environ.get(
            "COMPAT_POLICY_PROFILE",
            str(payload.get("default_profile", "alpha")),
        )
        profile_override = profiles.get(selected_profile)
        if not isinstance(profile_override, dict):
            available = ", ".join(sorted(str(key) for key in profiles.keys()))
            raise RuntimeError(
                f"unknown policy profile '{selected_profile}' in {policy_path} (available: {available})"
            )
        policy_override = profile_override
    else:
        # Backward compatibility with the flat policy format.
        policy_override = payload

    return _deep_merge(DEFAULT_ALPHA_GATING_POLICY, policy_override)
