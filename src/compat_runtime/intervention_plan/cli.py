from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _mode(efficiency_band: str, p0_risks: int, dependency_blockers: int) -> str:
    if efficiency_band == "low" or p0_risks >= 3 or dependency_blockers > 0:
        return "urgent"
    if efficiency_band == "medium" or p0_risks > 0:
        return "targeted"
    return "routine"


def _actions(mode: str) -> list[str]:
    if mode == "urgent":
        return ["Execute urgent intervention sprint on blockers and P0 risk items."]
    if mode == "targeted":
        return ["Run targeted intervention plan with owner-level checkpoints."]
    return ["Continue routine intervention hygiene and monitor drift."]


def build_intervention_plan_report(
    *,
    control_efficiency_report: dict,
    risk_watchlist_report: dict,
    dependency_watch_report: dict,
) -> dict:
    efficiency_summary = control_efficiency_report.get("summary", {})
    risk_summary = risk_watchlist_report.get("summary", {})
    dependency_summary = dependency_watch_report.get("summary", {})

    efficiency_band = str(efficiency_summary.get("efficiency_band", "low"))
    efficiency_score = int(efficiency_summary.get("efficiency_score", 0))
    p0_risks = int(risk_summary.get("p0_entries", 0))
    dependency_blockers = int(dependency_summary.get("dependencies_blocking", 0))

    mode = _mode(efficiency_band, p0_risks, dependency_blockers)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intervention_mode": mode,
            "efficiency_band": efficiency_band,
            "efficiency_score": efficiency_score,
            "p0_risks": p0_risks,
            "dependency_blockers": dependency_blockers,
        },
        "actions": _actions(mode),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build intervention plan report")
    parser.add_argument("--control-efficiency-report", required=True, help="Control efficiency report path")
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report path")
    parser.add_argument("--dependency-watch-report", required=True, help="Dependency watch report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_intervention_plan_report(
        control_efficiency_report=read_json(args.control_efficiency_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
        dependency_watch_report=read_json(args.dependency_watch_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
