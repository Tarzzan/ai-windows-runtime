from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import read_json, write_json


def _get_metric(report: dict, path: tuple[str, ...]) -> int:
    node = report
    for key in path:
        if not isinstance(node, dict):
            return 0
        node = node.get(key)
    return int(node) if isinstance(node, int) else 0


def _status_score(status: str) -> int:
    return 1 if status == "ok" else 0


def _metric_entry(name: str, current: int, baseline: int, better_when_lower: bool) -> dict:
    delta = current - baseline
    direction = "improved"
    if delta == 0:
        direction = "stable"
    elif better_when_lower and delta > 0:
        direction = "regressed"
    elif not better_when_lower and delta < 0:
        direction = "regressed"
    return {
        "name": name,
        "current": current,
        "baseline": baseline,
        "delta": delta,
        "better_when_lower": better_when_lower,
        "direction": direction,
    }


def _history_entry(path: str) -> dict:
    payload = read_json(path)
    return {
        "path": path,
        "generated_at": payload.get("generated_at"),
        "status": payload.get("status", "unknown"),
        "base_trace_events": _get_metric(payload, ("pipeline", "base", "trace_events")),
        "base_gaps": _get_metric(payload, ("pipeline", "base", "gaps")),
        "base_proposals": _get_metric(payload, ("pipeline", "base", "proposals")),
        "runtime_trace_events": _get_metric(payload, ("pipeline", "runtime", "trace_events")),
        "runtime_gaps": _get_metric(payload, ("pipeline", "runtime", "gaps")),
        "runtime_proposals": _get_metric(payload, ("pipeline", "runtime", "proposals")),
    }


def build_trend_report(
    *,
    current_report: dict,
    baseline_report: dict | None = None,
    history_paths: list[str] | None = None,
) -> dict:
    baseline = baseline_report or {"status": "failed", "pipeline": {}}

    metric_specs = [
        ("base_trace_events", ("pipeline", "base", "trace_events"), False),
        ("base_gaps", ("pipeline", "base", "gaps"), True),
        ("base_proposals", ("pipeline", "base", "proposals"), True),
        ("runtime_trace_events", ("pipeline", "runtime", "trace_events"), False),
        ("runtime_gaps", ("pipeline", "runtime", "gaps"), True),
        ("runtime_proposals", ("pipeline", "runtime", "proposals"), True),
    ]

    metrics = []
    for metric_name, path, better_when_lower in metric_specs:
        current = _get_metric(current_report, path)
        baseline_value = _get_metric(baseline, path)
        metrics.append(_metric_entry(metric_name, current, baseline_value, better_when_lower))

    improved = [m["name"] for m in metrics if m["direction"] == "improved"]
    regressed = [m["name"] for m in metrics if m["direction"] == "regressed"]
    stable = [m["name"] for m in metrics if m["direction"] == "stable"]

    current_status = current_report.get("status", "unknown")
    baseline_status = baseline.get("status", "unknown")
    status_delta = _status_score(current_status) - _status_score(baseline_status)

    history_entries = []
    for path in history_paths or []:
        if Path(path).exists():
            history_entries.append(_history_entry(path))

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "current_status": current_status,
            "baseline_status": baseline_status,
            "status_delta": status_delta,
            "improved_metrics": improved,
            "regressed_metrics": regressed,
            "stable_metrics": stable,
        },
        "metrics": metrics,
        "history": history_entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build trend report from execution-report artifacts"
    )
    parser.add_argument("--current", required=True, help="Current execution report path")
    parser.add_argument("--baseline", required=False, help="Baseline execution report path")
    parser.add_argument(
        "--history",
        required=False,
        nargs="*",
        help="Optional list of execution report paths for history section",
    )
    parser.add_argument("--output", required=True, help="Trend report JSON output")
    args = parser.parse_args()

    current = read_json(args.current)
    baseline = read_json(args.baseline) if args.baseline else None
    report = build_trend_report(
        current_report=current,
        baseline_report=baseline,
        history_paths=args.history or [],
    )
    write_json(args.output, report)


if __name__ == "__main__":
    main()
