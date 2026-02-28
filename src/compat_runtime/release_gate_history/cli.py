from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _trajectory(improved: int, regressed: int) -> str:
    if improved > regressed:
        return "improving"
    if regressed > improved:
        return "degrading"
    return "stable"


def build_release_gate_history_report(
    *,
    dashboard_timeseries: dict,
    trend_report: dict,
    quality_gate_report: dict,
    release_decision_report: dict,
    readiness_scorecard_report: dict,
) -> dict:
    points = dashboard_timeseries.get("points", [])
    improved = len(trend_report.get("summary", {}).get("improved_metrics", []))
    regressed = len(trend_report.get("summary", {}).get("regressed_metrics", []))

    snapshots = []
    for point in points:
        snapshots.append(
            {
                "index": point.get("index"),
                "generated_at": point.get("generated_at"),
                "execution_status": point.get("status"),
                "base_gaps": point.get("base_gaps"),
                "runtime_gaps": point.get("runtime_gaps"),
            }
        )

    snapshots.append(
        {
            "index": len(snapshots) + 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "execution_status": "gate",
            "quality_gate": quality_gate_report.get("gate"),
            "release_decision": release_decision_report.get("decision"),
            "readiness_score": readiness_scorecard_report.get("score"),
            "readiness_band": readiness_scorecard_report.get("band"),
        }
    )

    direction = _trajectory(improved, regressed)
    actions = []
    if direction == "degrading":
        actions.append("Gate trend is degrading. Freeze scope and prioritize blocker reduction.")
    elif direction == "improving":
        actions.append("Gate trend is improving. Keep cadence and monitor regression signals.")
    else:
        actions.append("Gate trend is stable. Continue collecting additional historical points.")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "snapshots": len(snapshots),
            "trend_improved_metrics": improved,
            "trend_regressed_metrics": regressed,
            "trajectory": direction,
            "latest_quality_gate": quality_gate_report.get("gate"),
            "latest_release_decision": release_decision_report.get("decision"),
            "latest_readiness_score": readiness_scorecard_report.get("score"),
        },
        "snapshots": snapshots,
        "actions": actions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release gate history report")
    parser.add_argument("--dashboard-timeseries", required=True, help="Dashboard timeseries path")
    parser.add_argument("--trend-report", required=True, help="Trend report path")
    parser.add_argument("--quality-gate-report", required=True, help="Quality gate report path")
    parser.add_argument("--release-decision-report", required=True, help="Release decision report path")
    parser.add_argument(
        "--readiness-scorecard-report", required=True, help="Readiness scorecard report path"
    )
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_release_gate_history_report(
        dashboard_timeseries=read_json(args.dashboard_timeseries),
        trend_report=read_json(args.trend_report),
        quality_gate_report=read_json(args.quality_gate_report),
        release_decision_report=read_json(args.release_decision_report),
        readiness_scorecard_report=read_json(args.readiness_scorecard_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
