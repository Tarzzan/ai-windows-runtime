from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _policy(readiness_band: str, pacing_window: str, slot_policy: str) -> str:
    if readiness_band == "blocked" or pacing_window == "slow" or slot_policy == "minimal":
        return "hold"
    if readiness_band == "watch" or pacing_window == "moderate" or slot_policy == "moderate":
        return "stage"
    return "advance"


def build_intake_transition_policy_report(
    *, transition_readiness_index_report: dict, intake_pacing_window_report: dict, intake_slot_policy_report: dict
) -> dict:
    readiness = transition_readiness_index_report.get("summary", {})
    pacing = intake_pacing_window_report.get("summary", {})
    slots = intake_slot_policy_report.get("summary", {})

    readiness_band = str(readiness.get("transition_readiness_band", "blocked"))
    pacing_window = str(pacing.get("intake_pacing_window", "slow"))
    slot_policy = str(slots.get("intake_slot_policy", "minimal"))

    policy = _policy(readiness_band, pacing_window, slot_policy)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_transition_policy": policy,
            "transition_readiness_band": readiness_band,
            "intake_pacing_window": pacing_window,
            "intake_slot_policy": slot_policy,
        },
        "actions": [
            "Maintenir la politique de transition intake en hold tant que la readiness est bloquee."
            if policy == "hold"
            else "Ajuster la politique de transition intake a chaque revue de cycle."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake transition policy report")
    p.add_argument("--transition-readiness-index-report", required=True)
    p.add_argument("--intake-pacing-window-report", required=True)
    p.add_argument("--intake-slot-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_transition_policy_report(
        transition_readiness_index_report=read_json(a.transition_readiness_index_report),
        intake_pacing_window_report=read_json(a.intake_pacing_window_report),
        intake_slot_policy_report=read_json(a.intake_slot_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
