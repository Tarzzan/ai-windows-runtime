from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import read_json, write_json


def _metric(report: dict, path: tuple[str, ...]) -> int:
    node = report
    for key in path:
        if not isinstance(node, dict):
            return 0
        node = node.get(key)
    return int(node) if isinstance(node, int) else 0


def _status(report: dict) -> str:
    status = report.get("status", "unknown")
    return status if isinstance(status, str) else "unknown"


def build_dashboard_timeseries(reports: list[dict], paths: list[str]) -> dict:
    points = []
    for idx, (report, path) in enumerate(zip(reports, paths), start=1):
        points.append(
            {
                "index": idx,
                "path": path,
                "generated_at": report.get("generated_at"),
                "status": _status(report),
                "base_trace_events": _metric(report, ("pipeline", "base", "trace_events")),
                "base_gaps": _metric(report, ("pipeline", "base", "gaps")),
                "base_proposals": _metric(report, ("pipeline", "base", "proposals")),
                "runtime_trace_events": _metric(report, ("pipeline", "runtime", "trace_events")),
                "runtime_gaps": _metric(report, ("pipeline", "runtime", "gaps")),
                "runtime_proposals": _metric(report, ("pipeline", "runtime", "proposals")),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "points": points,
    }


def _risk_level(*, failed_runs: int, regressed_metrics: int) -> str:
    score = failed_runs + regressed_metrics
    if score >= 3:
        return "high"
    if score >= 1:
        return "medium"
    return "low"


def build_kpi_report(reports: list[dict], trend_report: dict | None = None) -> dict:
    if not reports:
        return {
            "artifact_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_runs": 0,
                "ok_runs": 0,
                "failed_runs": 0,
                "ok_rate": 0.0,
                "latest_status": "unknown",
                "risk_level": "high",
            },
            "metrics": {},
            "actions": [
                "No execution reports found. Run scripts/run-full-pipeline.sh to produce artifacts."
            ],
        }

    statuses = [_status(report) for report in reports]
    total_runs = len(reports)
    ok_runs = sum(1 for status in statuses if status == "ok")
    failed_runs = total_runs - ok_runs
    ok_rate = round(ok_runs / total_runs, 3)

    base_gaps = [_metric(r, ("pipeline", "base", "gaps")) for r in reports]
    runtime_gaps = [_metric(r, ("pipeline", "runtime", "gaps")) for r in reports]
    base_proposals = [_metric(r, ("pipeline", "base", "proposals")) for r in reports]
    runtime_proposals = [_metric(r, ("pipeline", "runtime", "proposals")) for r in reports]

    regressed_metrics = len((trend_report or {}).get("summary", {}).get("regressed_metrics", []))
    improved_metrics = len((trend_report or {}).get("summary", {}).get("improved_metrics", []))
    risk_level = _risk_level(failed_runs=failed_runs, regressed_metrics=regressed_metrics)

    latest = reports[-1]
    metrics = {
        "latest_base_gaps": _metric(latest, ("pipeline", "base", "gaps")),
        "latest_runtime_gaps": _metric(latest, ("pipeline", "runtime", "gaps")),
        "avg_base_gaps": round(sum(base_gaps) / total_runs, 3),
        "avg_runtime_gaps": round(sum(runtime_gaps) / total_runs, 3),
        "avg_base_proposals": round(sum(base_proposals) / total_runs, 3),
        "avg_runtime_proposals": round(sum(runtime_proposals) / total_runs, 3),
        "regressed_metrics_count": regressed_metrics,
        "improved_metrics_count": improved_metrics,
    }

    actions: list[str] = []
    if failed_runs > 0:
        actions.append("Investigate failed runs and restore green pipeline status.")
    if regressed_metrics > 0:
        actions.append("Review regressed trend metrics and prioritize rollback/fix tasks.")
    if metrics["latest_runtime_gaps"] > 0:
        actions.append("Prioritize runtime compatibility gaps from latest run.")
    if not actions:
        actions.append("Pipeline is stable. Continue reducing remaining gap/proposal counts.")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_runs": total_runs,
            "ok_runs": ok_runs,
            "failed_runs": failed_runs,
            "ok_rate": ok_rate,
            "latest_status": statuses[-1],
            "risk_level": risk_level,
        },
        "metrics": metrics,
        "actions": actions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build KPI report and optional dashboard timeseries from execution reports"
    )
    parser.add_argument(
        "--reports",
        required=True,
        nargs="+",
        help="Execution report paths (ordered oldest -> newest)",
    )
    parser.add_argument(
        "--trend",
        required=False,
        help="Optional trend report path to enrich KPI with regression/improvement counts",
    )
    parser.add_argument("--output", required=True, help="KPI report output path")
    parser.add_argument(
        "--dashboard-output",
        required=False,
        help="Optional dashboard timeseries output path",
    )
    args = parser.parse_args()

    report_paths = [path for path in args.reports if Path(path).exists()]
    reports = [read_json(path) for path in report_paths]
    trend = read_json(args.trend) if args.trend and Path(args.trend).exists() else None

    kpi_report = build_kpi_report(reports, trend_report=trend)
    write_json(args.output, kpi_report)

    if args.dashboard_output:
        dashboard = build_dashboard_timeseries(reports, report_paths)
        write_json(args.dashboard_output, dashboard)


if __name__ == "__main__":
    main()
