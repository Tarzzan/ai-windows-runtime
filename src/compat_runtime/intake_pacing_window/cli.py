from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _window(stress_band: str, slot_policy: str, release_window: str) -> str:
    if stress_band == "high" or slot_policy == "minimal" or release_window == "closed":
        return "slow"
    if stress_band == "medium" or slot_policy == "moderate" or release_window == "limited":
        return "moderate"
    return "fast"


def build_intake_pacing_window_report(
    *, delivery_stress_index_report: dict, intake_slot_policy_report: dict, intake_release_window_report: dict
) -> dict:
    stress = delivery_stress_index_report.get("summary", {})
    slots = intake_slot_policy_report.get("summary", {})
    release = intake_release_window_report.get("summary", {})

    stress_band = str(stress.get("delivery_stress_band", "high"))
    slot_policy = str(slots.get("intake_slot_policy", "minimal"))
    release_window = str(release.get("intake_release_window", "closed"))

    pace = _window(stress_band, slot_policy, release_window)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_pacing_window": pace,
            "delivery_stress_band": stress_band,
            "intake_slot_policy": slot_policy,
            "intake_release_window": release_window,
        },
        "actions": [
            "Conserver une fenetre de pacing lente tant que le stress delivery reste eleve."
            if pace == "slow"
            else "Ajuster la fenetre de pacing intake a chaque cycle de gouvernance."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake pacing window report")
    p.add_argument("--delivery-stress-index-report", required=True)
    p.add_argument("--intake-slot-policy-report", required=True)
    p.add_argument("--intake-release-window-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_pacing_window_report(
        delivery_stress_index_report=read_json(a.delivery_stress_index_report),
        intake_slot_policy_report=read_json(a.intake_slot_policy_report),
        intake_release_window_report=read_json(a.intake_release_window_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
