from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _launch_status(decision: str, gate: str, failed_checks: int, missing_reports: int) -> str:
    if decision == "go" and gate == "pass" and failed_checks == 0 and missing_reports == 0:
        return "ready"
    if decision in {"go", "hold"} and gate in {"pass", "warn"}:
        return "limited"
    return "blocked"


def build_launch_readiness_report(
    *,
    handoff_checklist_report: dict,
    validation_coverage_report: dict,
    quality_gate_report: dict,
    release_decision_report: dict,
    pilot_readiness_report: dict,
) -> dict:
    handoff_summary = handoff_checklist_report.get("summary", {})
    coverage_summary = validation_coverage_report.get("summary", {})

    failed_checks = int(handoff_summary.get("checks_fail", 0))
    missing_reports = int(coverage_summary.get("missing_reports", 0))
    release_decision = str(release_decision_report.get("decision", "no-go"))
    quality_gate = str(quality_gate_report.get("gate", "fail"))

    status = _launch_status(release_decision, quality_gate, failed_checks, missing_reports)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "release_decision": release_decision,
            "quality_gate": quality_gate,
            "pilot_recommendation": str(pilot_readiness_report.get("recommendation", "not_ready")),
            "handoff_failed_checks": failed_checks,
            "validation_missing_reports": missing_reports,
        },
        "actions": [
            "Authorize launch only when status is ready and guardrails stay active.",
            "Re-run full pipeline after any critical remediation change.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build launch readiness report")
    parser.add_argument("--handoff-checklist-report", required=True, help="Handoff checklist report")
    parser.add_argument(
        "--validation-coverage-report", required=True, help="Validation coverage report"
    )
    parser.add_argument("--quality-gate-report", required=True, help="Quality gate report")
    parser.add_argument("--release-decision-report", required=True, help="Release decision report")
    parser.add_argument("--pilot-readiness-report", required=True, help="Pilot readiness report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_launch_readiness_report(
        handoff_checklist_report=read_json(args.handoff_checklist_report),
        validation_coverage_report=read_json(args.validation_coverage_report),
        quality_gate_report=read_json(args.quality_gate_report),
        release_decision_report=read_json(args.release_decision_report),
        pilot_readiness_report=read_json(args.pilot_readiness_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
