from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _guard(window: str, p0_entries: int, monitor_status: str) -> str:
    if window == "closed" or p0_entries >= 3 or monitor_status == "critical":
        return "strict"
    if window == "limited" or p0_entries >= 1 or monitor_status == "watch":
        return "elevated"
    return "normal"


def build_execution_stability_guard_report(
    *, intake_release_window_report: dict, risk_watchlist_report: dict, post_release_monitor_report: dict
) -> dict:
    release = intake_release_window_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})
    monitor = post_release_monitor_report.get("summary", {})

    release_window = str(release.get("intake_release_window", "closed"))
    p0_entries = int(risks.get("p0_entries", 0))
    monitor_status = str(monitor.get("monitor_status", "watch"))

    guard = _guard(release_window, p0_entries, monitor_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "execution_stability_guard": guard,
            "intake_release_window": release_window,
            "p0_entries": p0_entries,
            "monitor_status": monitor_status,
        },
        "actions": [
            "Apply strict execution stability guard while risk pressure remains elevated."
            if guard == "strict"
            else "Track stability guard level during each release governance review."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build execution stability guard report")
    p.add_argument("--intake-release-window-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--post-release-monitor-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_execution_stability_guard_report(
        intake_release_window_report=read_json(a.intake_release_window_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
        post_release_monitor_report=read_json(a.post_release_monitor_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
