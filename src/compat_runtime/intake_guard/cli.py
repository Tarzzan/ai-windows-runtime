from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _guard(mode: str, policy_status: str, corridor: str) -> str:
    if policy_status != "pass" or mode == "narrow" or corridor == "p0_only":
        return "strict"
    if mode == "controlled" or corridor == "p0_p1":
        return "moderate"
    return "open"


def build_intake_guard_report(
    *, delivery_bandwidth_report: dict, release_policy_report: dict, priority_corridor_report: dict
) -> dict:
    bw = delivery_bandwidth_report.get("summary", {})
    corridor = priority_corridor_report.get("summary", {})

    mode = str(bw.get("bandwidth_mode", "narrow"))
    policy_status = str(release_policy_report.get("status", "missing"))
    corridor_mode = str(corridor.get("priority_corridor", "p0_only"))

    guard = _guard(mode, policy_status, corridor_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_guard": guard,
            "bandwidth_mode": mode,
            "policy_status": policy_status,
            "priority_corridor": corridor_mode,
        },
        "actions": [
            "Keep strict intake guard and prioritize existing commitments."
            if guard == "strict"
            else "Maintain intake guard discipline with periodic policy checks."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake guard report")
    p.add_argument("--delivery-bandwidth-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--priority-corridor-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_guard_report(
        delivery_bandwidth_report=read_json(a.delivery_bandwidth_report),
        release_policy_report=read_json(a.release_policy_report),
        priority_corridor_report=read_json(a.priority_corridor_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
