from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _gate(acceleration_policy: str, expansion_gate: str, release_policy_status: str) -> str:
    if acceleration_policy == "hold" or expansion_gate == "closed" or release_policy_status != "pass":
        return "closed"
    if acceleration_policy == "stage" or expansion_gate == "guarded":
        return "guarded"
    return "open"


def build_scope_acceleration_gate_report(
    *, intake_acceleration_policy_report: dict, scope_expansion_gate_report: dict, release_policy_report: dict
) -> dict:
    acceleration = intake_acceleration_policy_report.get("summary", {})
    expansion = scope_expansion_gate_report.get("summary", {})

    acceleration_policy = str(acceleration.get("intake_acceleration_policy", "hold"))
    expansion_gate = str(expansion.get("scope_expansion_gate", "closed"))
    release_policy_status = str(release_policy_report.get("status", "missing"))

    gate = _gate(acceleration_policy, expansion_gate, release_policy_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_acceleration_gate": gate,
            "intake_acceleration_policy": acceleration_policy,
            "scope_expansion_gate": expansion_gate,
            "release_policy_status": release_policy_status,
        },
        "actions": [
            "Garder le gate d'acceleration scope ferme tant que les preconditions ne sont pas satisfaites."
            if gate == "closed"
            else "Verifier le gate d'acceleration scope avant toute acceleration de perimetre."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope acceleration gate report")
    p.add_argument("--intake-acceleration-policy-report", required=True)
    p.add_argument("--scope-expansion-gate-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_acceleration_gate_report(
        intake_acceleration_policy_report=read_json(a.intake_acceleration_policy_report),
        scope_expansion_gate_report=read_json(a.scope_expansion_gate_report),
        release_policy_report=read_json(a.release_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
