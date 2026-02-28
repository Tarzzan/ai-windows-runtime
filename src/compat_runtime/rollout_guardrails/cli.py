from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _phase(recommendation: str) -> str:
    if recommendation == "ready":
        return "pilot_open"
    if recommendation == "limited_pilot":
        return "pilot_limited"
    return "hold"


def build_rollout_guardrails_report(
    *,
    pilot_readiness_report: dict,
    rollback_hints_report: dict,
    proposal_risk_report: dict,
    crash_signature_report: dict,
) -> dict:
    recommendation = str(pilot_readiness_report.get("recommendation", "not_ready"))
    high_risk = int(proposal_risk_report.get("summary", {}).get("high_risk", 0))
    crash_p0 = int(crash_signature_report.get("summary", {}).get("high_priority_signatures", 0))
    rollback_full = sum(
        1
        for hint in rollback_hints_report.get("hints", [])
        if str(hint.get("rollback_level", "minimal")) == "full"
    )

    stop_conditions = [
        "New P0 crash signature detected in pilot telemetry stream.",
        "Any required release check regresses from pass to fail.",
    ]
    if high_risk > 0:
        stop_conditions.append("High-risk proposal count increases during rollout.")

    safeguards = [
        {
            "id": "telemetry_watch",
            "description": "Monitor crash signatures and installer errors on each rollout wave.",
            "required": True,
        },
        {
            "id": "rollback_drill",
            "description": "Execute rollback command pack rehearsal before expanding rollout scope.",
            "required": True,
        },
        {
            "id": "owner_on_call",
            "description": "Keep compatibility + runtime owners on-call during rollout windows.",
            "required": True,
        },
    ]

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "rollout_phase": _phase(recommendation),
            "pilot_recommendation": recommendation,
            "high_risk_proposals": high_risk,
            "high_priority_crash_signatures": crash_p0,
            "full_rollback_paths": rollback_full,
            "stop_conditions": len(stop_conditions),
        },
        "stop_conditions": stop_conditions,
        "safeguards": safeguards,
        "actions": [
            "Review stop conditions before each rollout increment.",
            "Do not expand rollout scope until safeguards are verified.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build rollout guardrails report")
    parser.add_argument("--pilot-readiness-report", required=True, help="Pilot readiness report path")
    parser.add_argument("--rollback-hints-report", required=True, help="Rollback hints report path")
    parser.add_argument("--proposal-risk-report", required=True, help="Proposal risk report path")
    parser.add_argument("--crash-signature-report", required=True, help="Crash signature report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_rollout_guardrails_report(
        pilot_readiness_report=read_json(args.pilot_readiness_report),
        rollback_hints_report=read_json(args.rollback_hints_report),
        proposal_risk_report=read_json(args.proposal_risk_report),
        crash_signature_report=read_json(args.crash_signature_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
