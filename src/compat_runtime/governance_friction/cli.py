from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _actions(band: str) -> list[str]:
    if band == "high":
        return ["Reduce governance friction by shrinking concurrent blocking streams."]
    if band == "medium":
        return ["Stabilize governance cadence with tighter owner feedback loops."]
    return ["Governance friction is low; maintain current control rhythm."]


def build_governance_friction_report(
    *,
    control_efficiency_report: dict,
    intervention_plan_report: dict,
    validation_coverage_report: dict,
) -> dict:
    eff = control_efficiency_report.get("summary", {})
    intervention = intervention_plan_report.get("summary", {})
    coverage = validation_coverage_report.get("summary", {})

    efficiency_score = int(eff.get("efficiency_score", 0))
    intervention_mode = str(intervention.get("intervention_mode", "urgent"))
    missing_reports = int(coverage.get("missing_reports", 0))

    mode_penalty = {"routine": 0, "targeted": 12, "urgent": 24}.get(intervention_mode, 18)
    validation_penalty = min(20, missing_reports * 5)

    friction_score = max(0, min(100, (100 - efficiency_score) + mode_penalty + validation_penalty))
    friction_band = _band(friction_score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "friction_score": friction_score,
            "friction_band": friction_band,
            "efficiency_score": efficiency_score,
            "intervention_mode": intervention_mode,
            "missing_validation_reports": missing_reports,
        },
        "actions": _actions(friction_band),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build governance friction report")
    parser.add_argument("--control-efficiency-report", required=True)
    parser.add_argument("--intervention-plan-report", required=True)
    parser.add_argument("--validation-coverage-report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    artifact = build_governance_friction_report(
        control_efficiency_report=read_json(args.control_efficiency_report),
        intervention_plan_report=read_json(args.intervention_plan_report),
        validation_coverage_report=read_json(args.validation_coverage_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
