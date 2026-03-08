from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_handoff_checklist_report(
    *,
    stakeholder_update_report: dict,
    ownership_assignment_report: dict,
    rollout_guardrails_report: dict,
    validation_command_pack: dict,
) -> dict:
    stakeholder_summary = stakeholder_update_report.get("summary", {})
    assignment_summary = ownership_assignment_report.get("summary", {})
    guardrails_summary = rollout_guardrails_report.get("summary", {})
    release_policy_status = str(stakeholder_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(stakeholder_summary.get("release_policy_failures", 0))

    checks = [
        {
            "id": "owners_assigned",
            "status": "pass" if int(assignment_summary.get("unassigned_items", 0)) == 0 else "warn",
            "detail": "All critical tasks and watchlist items have owners.",
        },
        {
            "id": "guardrails_defined",
            "status": "pass" if int(guardrails_summary.get("stop_conditions", 0)) > 0 else "fail",
            "detail": "Rollout stop conditions and safeguards are documented.",
        },
        {
            "id": "validation_commands_ready",
            "status": "pass" if len(validation_command_pack.get("commands", [])) > 0 else "warn",
            "detail": "Validation command pack is available for handoff execution.",
        },
        {
            "id": "stakeholder_alignment",
            "status": "pass"
            if str(stakeholder_summary.get("delivery_status", "at_risk")) in {"on_track", "watch"}
            else "warn",
            "detail": "Stakeholder-facing delivery status is available.",
        },
        {
            "id": "release_policy_alignment",
            "status": "pass" if release_policy_status in {"pass", "missing"} else "fail",
            "detail": "Release policy diagnostics are compatible with handoff.",
        },
    ]

    passed = sum(1 for row in checks if row["status"] == "pass")
    failed = sum(1 for row in checks if row["status"] == "fail")
    warned = len(checks) - passed - failed

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "checks_total": len(checks),
            "checks_pass": passed,
            "checks_warn": warned,
            "checks_fail": failed,
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "checks": checks,
        "actions": ["Resolve fail/warn checks before handoff sign-off."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build handoff checklist report")
    parser.add_argument("--stakeholder-update-report", required=True, help="Stakeholder update report")
    parser.add_argument(
        "--ownership-assignment-report", required=True, help="Ownership assignment report"
    )
    parser.add_argument("--rollout-guardrails-report", required=True, help="Rollout guardrails report")
    parser.add_argument("--validation-command-pack", required=True, help="Validation command pack")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_handoff_checklist_report(
        stakeholder_update_report=read_json(args.stakeholder_update_report),
        ownership_assignment_report=read_json(args.ownership_assignment_report),
        rollout_guardrails_report=read_json(args.rollout_guardrails_report),
        validation_command_pack=read_json(args.validation_command_pack),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
