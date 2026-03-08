from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 70:
        return "ready"
    if score >= 40:
        return "watch"
    return "blocked"


def build_transition_readiness_index_report(
    *, scope_transition_gate_report: dict, delivery_stress_index_report: dict, policy_health_report: dict
) -> dict:
    transition = scope_transition_gate_report.get("summary", {})
    stress = delivery_stress_index_report.get("summary", {})

    gate = str(transition.get("scope_transition_gate", "blocked"))
    stress_score = int(stress.get("delivery_stress_score", 100))
    compliance = str(policy_health_report.get("policy_compliance_level", "unknown"))

    gate_base = {"blocked": 18, "conditional": 46, "open": 78}.get(gate, 18)
    stress_penalty = min(28, stress_score // 4)
    compliance_bonus = {"non_compliant": -10, "partially_compliant": 0, "compliant": 10}.get(
        compliance, 0
    )

    score = max(0, min(100, gate_base - stress_penalty + compliance_bonus + 20))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "transition_readiness_score": score,
            "transition_readiness_band": band,
            "scope_transition_gate": gate,
            "delivery_stress_score": stress_score,
            "policy_compliance_level": compliance,
        },
        "actions": [
            "Bloquer les transitions tant que la readiness reste en mode bloque." if band == "blocked" else "Suivre la readiness de transition avant chaque decision de passage."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build transition readiness index report")
    p.add_argument("--scope-transition-gate-report", required=True)
    p.add_argument("--delivery-stress-index-report", required=True)
    p.add_argument("--policy-health-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_transition_readiness_index_report(
        scope_transition_gate_report=read_json(a.scope_transition_gate_report),
        delivery_stress_index_report=read_json(a.delivery_stress_index_report),
        policy_health_report=read_json(a.policy_health_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
