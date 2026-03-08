from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _gate(expansion_policy: str, unlock_gate: str, release_policy_status: str) -> str:
    if expansion_policy == "hold" or unlock_gate == "locked" or release_policy_status != "pass":
        return "closed"
    if expansion_policy == "stage" or unlock_gate == "guarded":
        return "guarded"
    return "open"


def build_scope_expansion_gate_report(
    *, intake_expansion_policy_report: dict, scope_unlock_gate_report: dict, release_policy_report: dict
) -> dict:
    expansion = intake_expansion_policy_report.get("summary", {})
    unlock = scope_unlock_gate_report.get("summary", {})

    expansion_policy = str(expansion.get("intake_expansion_policy", "hold"))
    unlock_gate = str(unlock.get("scope_unlock_gate", "locked"))
    release_policy_status = str(release_policy_report.get("status", "missing"))

    gate = _gate(expansion_policy, unlock_gate, release_policy_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_expansion_gate": gate,
            "intake_expansion_policy": expansion_policy,
            "scope_unlock_gate": unlock_gate,
            "release_policy_status": release_policy_status,
        },
        "actions": [
            "Garder le gate d'expansion scope ferme tant que les preconditions ne sont pas satisfaites."
            if gate == "closed"
            else "Verifier le gate d'expansion scope avant chaque extension de perimetre."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope expansion gate report")
    p.add_argument("--intake-expansion-policy-report", required=True)
    p.add_argument("--scope-unlock-gate-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_expansion_gate_report(
        intake_expansion_policy_report=read_json(a.intake_expansion_policy_report),
        scope_unlock_gate_report=read_json(a.scope_unlock_gate_report),
        release_policy_report=read_json(a.release_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
