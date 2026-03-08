from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _policy(reentry_band: str, transition_policy: str, delivery_temperature: str) -> str:
    if reentry_band == "blocked" or transition_policy == "hold" or delivery_temperature == "hot":
        return "hold"
    if reentry_band == "watch" or transition_policy == "stage" or delivery_temperature == "warm":
        return "stage"
    return "resume"


def build_intake_resumption_policy_report(
    *, scope_reentry_readiness_report: dict, intake_transition_policy_report: dict, delivery_temperature_report: dict
) -> dict:
    reentry = scope_reentry_readiness_report.get("summary", {})
    transition = intake_transition_policy_report.get("summary", {})
    temperature = delivery_temperature_report.get("summary", {})

    reentry_band = str(reentry.get("scope_reentry_readiness_band", "blocked"))
    transition_policy = str(transition.get("intake_transition_policy", "hold"))
    delivery_temperature = str(temperature.get("temperature", "hot"))

    policy = _policy(reentry_band, transition_policy, delivery_temperature)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_resumption_policy": policy,
            "scope_reentry_readiness_band": reentry_band,
            "intake_transition_policy": transition_policy,
            "delivery_temperature": delivery_temperature,
        },
        "actions": [
            "Maintenir la reprise intake en hold tant que la reentree est bloquee."
            if policy == "hold"
            else "Ajuster la politique de reprise intake en fonction des signaux de stabilisation."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake resumption policy report")
    p.add_argument("--scope-reentry-readiness-report", required=True)
    p.add_argument("--intake-transition-policy-report", required=True)
    p.add_argument("--delivery-temperature-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_resumption_policy_report(
        scope_reentry_readiness_report=read_json(a.scope_reentry_readiness_report),
        intake_transition_policy_report=read_json(a.intake_transition_policy_report),
        delivery_temperature_report=read_json(a.delivery_temperature_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
