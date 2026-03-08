from __future__ import annotations

import json

from compat_runtime.common.policy import load_alpha_gating_policy
from compat_runtime.release_decision.cli import build_release_decision_report


def _quality(gate: str, warn_items: int) -> dict:
    return {"gate": gate, "summary": {"warn_items": warn_items}}


def _checklist(release_ready: bool, warn_items: int) -> dict:
    return {"release_ready": release_ready, "summary": {"warn_items": warn_items}}


def _matrix(release_ready: bool) -> dict:
    return {"release_ready": release_ready}


def _productization(ready: bool) -> dict:
    return {"ready": ready}


def test_alpha_policy_loads_defaults():
    load_alpha_gating_policy.cache_clear()
    policy = load_alpha_gating_policy()
    assert policy["release_decision"]["warning_budget"] == 2
    assert policy["quality_gate"]["office_limited_as_pass"] is True


def test_alpha_policy_can_override_warning_budget(monkeypatch, tmp_path):
    policy_path = tmp_path / "alpha-policy.json"
    policy_path.write_text(
        json.dumps({"release_decision": {"warning_budget": 0}}),
        encoding="utf-8",
    )

    load_alpha_gating_policy.cache_clear()
    monkeypatch.setenv("COMPAT_POLICY_PATH", str(policy_path))
    try:
        report = build_release_decision_report(
            quality_gate_report=_quality("warn", 1),
            alpha_release_checklist=_checklist(True, 0),
            compatibility_matrix=_matrix(True),
            productization_readiness=_productization(True),
        )
    finally:
        load_alpha_gating_policy.cache_clear()

    assert report["summary"]["budget_warnings"] == 1
    assert report["decision"] == "hold"


def test_alpha_policy_can_select_profile(monkeypatch, tmp_path):
    policy_path = tmp_path / "alpha-policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "default_profile": "alpha",
                "profiles": {
                    "alpha": {"release_decision": {"warning_budget": 2}},
                    "prod": {"release_decision": {"warning_budget": 0}},
                },
            }
        ),
        encoding="utf-8",
    )

    load_alpha_gating_policy.cache_clear()
    monkeypatch.setenv("COMPAT_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("COMPAT_POLICY_PROFILE", "prod")
    try:
        policy = load_alpha_gating_policy()
    finally:
        load_alpha_gating_policy.cache_clear()

    assert policy["release_decision"]["warning_budget"] == 0
