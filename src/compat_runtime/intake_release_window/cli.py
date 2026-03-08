from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _window(flow_mode: str, queue_policy: str, admission_window: str) -> str:
    if flow_mode == "tight" or queue_policy == "restrictive" or admission_window == "restricted":
        return "closed"
    if flow_mode == "managed" or queue_policy == "managed" or admission_window == "controlled":
        return "limited"
    return "open"


def build_intake_release_window_report(
    *, flow_control_budget_report: dict, intake_queue_policy_report: dict, admission_window_report: dict
) -> dict:
    flow = flow_control_budget_report.get("summary", {})
    queue = intake_queue_policy_report.get("summary", {})
    admission = admission_window_report.get("summary", {})

    flow_mode = str(flow.get("flow_control_mode", "tight"))
    queue_policy = str(queue.get("intake_queue_policy", "restrictive"))
    admission_state = str(admission.get("admission_window", "restricted"))

    release_window = _window(flow_mode, queue_policy, admission_state)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_release_window": release_window,
            "flow_control_mode": flow_mode,
            "intake_queue_policy": queue_policy,
            "admission_window": admission_state,
        },
        "actions": [
            "Keep intake release window closed until flow and queue posture improve."
            if release_window == "closed"
            else "Re-check intake release window before each new admission batch."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake release window report")
    p.add_argument("--flow-control-budget-report", required=True)
    p.add_argument("--intake-queue-policy-report", required=True)
    p.add_argument("--admission-window-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_release_window_report(
        flow_control_budget_report=read_json(a.flow_control_budget_report),
        intake_queue_policy_report=read_json(a.intake_queue_policy_report),
        admission_window_report=read_json(a.admission_window_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
