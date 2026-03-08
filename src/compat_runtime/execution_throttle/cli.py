from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _throttle(cadence: str, overloaded: int, friction_band: str) -> str:
    if friction_band == "high" or overloaded > 0 or cadence == "slow":
        return "tight"
    if cadence == "moderate":
        return "balanced"
    return "open"


def _actions(mode: str) -> list[str]:
    if mode == "tight":
        return ["Apply tight throttle: only blocker-critical tasks enter active queue."]
    if mode == "balanced":
        return ["Apply balanced throttle with controlled intake per owner."]
    return ["Use open throttle while monitoring risk drift each cycle."]


def build_execution_throttle_report(
    *, cadence_recommendation_report: dict, governance_friction_report: dict, owner_load_report: dict
) -> dict:
    cadence = str(cadence_recommendation_report.get("summary", {}).get("cadence", "slow"))
    friction_band = str(governance_friction_report.get("summary", {}).get("friction_band", "high"))
    overloaded = int(owner_load_report.get("summary", {}).get("overloaded_owners", 0))

    mode = _throttle(cadence, overloaded, friction_band)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "throttle_mode": mode,
            "cadence": cadence,
            "friction_band": friction_band,
            "overloaded_owners": overloaded,
        },
        "actions": _actions(mode),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build execution throttle report")
    p.add_argument("--cadence-recommendation-report", required=True)
    p.add_argument("--governance-friction-report", required=True)
    p.add_argument("--owner-load-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_execution_throttle_report(
        cadence_recommendation_report=read_json(a.cadence_recommendation_report),
        governance_friction_report=read_json(a.governance_friction_report),
        owner_load_report=read_json(a.owner_load_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
