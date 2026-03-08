from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _gate(pacing_window: str, freeze_guard: str, policy_status: str) -> str:
    if pacing_window == "slow" or freeze_guard == "freeze" or policy_status != "pass":
        return "blocked"
    if pacing_window == "moderate" or freeze_guard == "guarded":
        return "conditional"
    return "open"


def build_scope_transition_gate_report(
    *, intake_pacing_window_report: dict, scope_freeze_guard_report: dict, release_policy_report: dict
) -> dict:
    pacing = intake_pacing_window_report.get("summary", {})
    freeze = scope_freeze_guard_report.get("summary", {})

    pacing_window = str(pacing.get("intake_pacing_window", "slow"))
    freeze_guard = str(freeze.get("scope_freeze_guard", "freeze"))
    policy_status = str(release_policy_report.get("status", "missing"))

    gate = _gate(pacing_window, freeze_guard, policy_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_transition_gate": gate,
            "intake_pacing_window": pacing_window,
            "scope_freeze_guard": freeze_guard,
            "policy_status": policy_status,
        },
        "actions": [
            "Bloquer les transitions de scope tant que le gate reste bloque."
            if gate == "blocked"
            else "Verifier le gate de transition de scope avant chaque changement de perimetre."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope transition gate report")
    p.add_argument("--intake-pacing-window-report", required=True)
    p.add_argument("--scope-freeze-guard-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_transition_gate_report(
        intake_pacing_window_report=read_json(a.intake_pacing_window_report),
        scope_freeze_guard_report=read_json(a.scope_freeze_guard_report),
        release_policy_report=read_json(a.release_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
