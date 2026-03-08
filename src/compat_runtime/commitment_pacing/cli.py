from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _mode(admission_state: str, p0_items: int, bandwidth_mode: str) -> str:
    if admission_state == "gated" or bandwidth_mode == "narrow" or p0_items >= 3:
        return "stabilize"
    if admission_state == "selective" or bandwidth_mode == "controlled" or p0_items >= 1:
        return "paced"
    return "expand"


def build_commitment_pacing_report(
    *, admission_control_report: dict, backlog_refresh_report: dict, delivery_bandwidth_report: dict
) -> dict:
    admission = admission_control_report.get("summary", {})
    backlog_items = backlog_refresh_report.get("items", [])
    bandwidth = delivery_bandwidth_report.get("summary", {})

    admission_state = str(admission.get("admission_state", "gated"))
    bandwidth_mode = str(bandwidth.get("bandwidth_mode", "narrow"))
    p0_items = sum(1 for item in backlog_items if str(item.get("priority", "")).upper() == "P0")

    mode = _mode(admission_state, p0_items, bandwidth_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "commitment_mode": mode,
            "admission_state": admission_state,
            "p0_backlog_items": p0_items,
            "bandwidth_mode": bandwidth_mode,
        },
        "actions": [
            "Stabilize commitments and avoid net-new scope until P0 backlog shrinks."
            if mode == "stabilize"
            else "Run commitment pacing review before admitting additional scope."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build commitment pacing report")
    p.add_argument("--admission-control-report", required=True)
    p.add_argument("--backlog-refresh-report", required=True)
    p.add_argument("--delivery-bandwidth-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_commitment_pacing_report(
        admission_control_report=read_json(a.admission_control_report),
        backlog_refresh_report=read_json(a.backlog_refresh_report),
        delivery_bandwidth_report=read_json(a.delivery_bandwidth_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
