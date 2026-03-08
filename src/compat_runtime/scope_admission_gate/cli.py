from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _gate(transition_policy: str, scope_freeze_guard: str, release_policy_status: str) -> str:
    if transition_policy == "hold" or scope_freeze_guard == "freeze" or release_policy_status != "pass":
        return "closed"
    if transition_policy == "stage" or scope_freeze_guard == "guarded":
        return "guarded"
    return "open"


def build_scope_admission_gate_report(
    *, intake_transition_policy_report: dict, scope_freeze_guard_report: dict, release_policy_report: dict
) -> dict:
    transition = intake_transition_policy_report.get("summary", {})
    freeze = scope_freeze_guard_report.get("summary", {})

    transition_policy = str(transition.get("intake_transition_policy", "hold"))
    freeze_guard = str(freeze.get("scope_freeze_guard", "freeze"))
    release_policy_status = str(release_policy_report.get("status", "missing"))

    gate = _gate(transition_policy, freeze_guard, release_policy_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_admission_gate": gate,
            "intake_transition_policy": transition_policy,
            "scope_freeze_guard": freeze_guard,
            "release_policy_status": release_policy_status,
        },
        "actions": [
            "Garder le gate d'admission scope ferme tant que les conditions ne sont pas reunies."
            if gate == "closed"
            else "Verifier le gate d'admission scope avant chaque extension de perimetre."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope admission gate report")
    p.add_argument("--intake-transition-policy-report", required=True)
    p.add_argument("--scope-freeze-guard-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_admission_gate_report(
        intake_transition_policy_report=read_json(a.intake_transition_policy_report),
        scope_freeze_guard_report=read_json(a.scope_freeze_guard_report),
        release_policy_report=read_json(a.release_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
