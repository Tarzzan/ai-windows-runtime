from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _policy(buffer_band: str, sync_state: str, guard_mode: str) -> str:
    if buffer_band == "low" or sync_state == "blocked" or guard_mode == "strict":
        return "restrictive"
    if buffer_band == "medium" or sync_state == "aligned" or guard_mode == "moderate":
        return "managed"
    return "permissive"


def build_intake_queue_policy_report(
    *, capacity_buffer_report: dict, delivery_intake_sync_report: dict, commitment_guard_report: dict
) -> dict:
    buffer = capacity_buffer_report.get("summary", {})
    sync = delivery_intake_sync_report.get("summary", {})
    guard = commitment_guard_report.get("summary", {})

    buffer_band = str(buffer.get("capacity_buffer_band", "low"))
    sync_state = str(sync.get("delivery_intake_sync", "blocked"))
    guard_mode = str(guard.get("commitment_guard", "strict"))

    policy_mode = _policy(buffer_band, sync_state, guard_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_queue_policy": policy_mode,
            "capacity_buffer_band": buffer_band,
            "delivery_intake_sync": sync_state,
            "commitment_guard": guard_mode,
        },
        "actions": [
            "Apply restrictive intake queue policy until sync and guard posture improve."
            if policy_mode == "restrictive"
            else "Review intake queue policy against current execution pressure."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake queue policy report")
    p.add_argument("--capacity-buffer-report", required=True)
    p.add_argument("--delivery-intake-sync-report", required=True)
    p.add_argument("--commitment-guard-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_queue_policy_report(
        capacity_buffer_report=read_json(a.capacity_buffer_report),
        delivery_intake_sync_report=read_json(a.delivery_intake_sync_report),
        commitment_guard_report=read_json(a.commitment_guard_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
