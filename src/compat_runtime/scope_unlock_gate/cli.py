from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _gate(resumption_policy: str, admission_gate: str, release_policy_status: str) -> str:
    if resumption_policy == "hold" or admission_gate == "closed" or release_policy_status != "pass":
        return "locked"
    if resumption_policy == "stage" or admission_gate == "guarded":
        return "guarded"
    return "unlocked"


def build_scope_unlock_gate_report(
    *, intake_resumption_policy_report: dict, scope_admission_gate_report: dict, release_policy_report: dict
) -> dict:
    resumption = intake_resumption_policy_report.get("summary", {})
    admission = scope_admission_gate_report.get("summary", {})

    resumption_policy = str(resumption.get("intake_resumption_policy", "hold"))
    admission_gate = str(admission.get("scope_admission_gate", "closed"))
    release_policy_status = str(release_policy_report.get("status", "missing"))

    gate = _gate(resumption_policy, admission_gate, release_policy_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_unlock_gate": gate,
            "intake_resumption_policy": resumption_policy,
            "scope_admission_gate": admission_gate,
            "release_policy_status": release_policy_status,
        },
        "actions": [
            "Garder le gate de deblocage scope verrouille tant que les preconditions ne sont pas satisfaites."
            if gate == "locked"
            else "Verifier le gate de deblocage scope avant chaque extension de perimetre."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope unlock gate report")
    p.add_argument("--intake-resumption-policy-report", required=True)
    p.add_argument("--scope-admission-gate-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_unlock_gate_report(
        intake_resumption_policy_report=read_json(a.intake_resumption_policy_report),
        scope_admission_gate_report=read_json(a.scope_admission_gate_report),
        release_policy_report=read_json(a.release_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
