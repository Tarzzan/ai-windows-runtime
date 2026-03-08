from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _policy(guard_band: str, commitment_window: str, intake_queue_policy: str) -> str:
    if guard_band == "tight" or commitment_window == "locked" or intake_queue_policy == "restrictive":
        return "minimal"
    if guard_band == "balanced" or commitment_window == "managed" or intake_queue_policy == "managed":
        return "moderate"
    return "expanded"


def build_intake_slot_policy_report(
    *, throughput_guard_band_report: dict, intake_commitment_window_report: dict, intake_queue_policy_report: dict
) -> dict:
    guard = throughput_guard_band_report.get("summary", {})
    commitment = intake_commitment_window_report.get("summary", {})
    queue = intake_queue_policy_report.get("summary", {})

    guard_band = str(guard.get("throughput_guard_band", "tight"))
    commitment_window = str(commitment.get("intake_commitment_window", "locked"))
    queue_policy = str(queue.get("intake_queue_policy", "restrictive"))

    policy = _policy(guard_band, commitment_window, queue_policy)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_slot_policy": policy,
            "throughput_guard_band": guard_band,
            "intake_commitment_window": commitment_window,
            "intake_queue_policy": queue_policy,
        },
        "actions": [
            "Appliquer une politique de slots intake minimale tant que les gardes restent contraints."
            if policy == "minimal"
            else "Revoir la politique de slots intake a chaque handoff de planification."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake slot policy report")
    p.add_argument("--throughput-guard-band-report", required=True)
    p.add_argument("--intake-commitment-window-report", required=True)
    p.add_argument("--intake-queue-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_slot_policy_report(
        throughput_guard_band_report=read_json(a.throughput_guard_band_report),
        intake_commitment_window_report=read_json(a.intake_commitment_window_report),
        intake_queue_policy_report=read_json(a.intake_queue_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
