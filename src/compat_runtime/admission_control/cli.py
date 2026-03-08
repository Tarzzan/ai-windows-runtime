from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _state(capacity_mode: str, policy_status: str, corridor: str) -> str:
    if policy_status != "pass" or capacity_mode == "constrained" or corridor == "p0_only":
        return "gated"
    if capacity_mode == "balanced" or corridor == "p0_p1":
        return "selective"
    return "open"


def build_admission_control_report(
    *, intake_capacity_report: dict, release_policy_report: dict, priority_corridor_report: dict
) -> dict:
    capacity = intake_capacity_report.get("summary", {})
    corridor = priority_corridor_report.get("summary", {})

    capacity_mode = str(capacity.get("intake_capacity_mode", "constrained"))
    policy_status = str(release_policy_report.get("status", "missing"))
    corridor_mode = str(corridor.get("priority_corridor", "p0_only"))

    admission_state = _state(capacity_mode, policy_status, corridor_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "admission_state": admission_state,
            "intake_capacity_mode": capacity_mode,
            "policy_status": policy_status,
            "priority_corridor": corridor_mode,
        },
        "actions": [
            "Gate new admissions and protect existing delivery commitments."
            if admission_state == "gated"
            else "Apply admission controls aligned with capacity and policy posture."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build admission control report")
    p.add_argument("--intake-capacity-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--priority-corridor-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_admission_control_report(
        intake_capacity_report=read_json(a.intake_capacity_report),
        release_policy_report=read_json(a.release_policy_report),
        priority_corridor_report=read_json(a.priority_corridor_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
