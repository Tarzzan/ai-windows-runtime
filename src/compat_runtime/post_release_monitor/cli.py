from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_post_release_monitor_report(
    *, delivery_signoff_report: dict, runtime_signal_report: dict, crash_signature_report: dict
) -> dict:
    signoff_status = str(delivery_signoff_report.get("status", "blocked"))
    runtime_summary = runtime_signal_report.get("summary", {})
    crash_summary = crash_signature_report.get("summary", {})

    high_crash = int(crash_summary.get("high_priority_signatures", 0))
    missing_hooks = int(runtime_summary.get("missing_hooks", 0))

    monitor_status = "stable"
    if high_crash > 0 or signoff_status == "blocked":
        monitor_status = "critical"
    elif missing_hooks > 0 or signoff_status == "conditional":
        monitor_status = "watch"

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "monitor_status": monitor_status,
            "delivery_signoff_status": signoff_status,
            "missing_hooks": missing_hooks,
            "high_priority_crash_signatures": high_crash,
            "runtime_events": int(runtime_summary.get("total_events", 0)),
        },
        "actions": ["Track post-release telemetry until monitor_status is stable."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build post-release monitor report")
    parser.add_argument("--delivery-signoff-report", required=True, help="Delivery signoff report path")
    parser.add_argument("--runtime-signal-report", required=True, help="Runtime signal report path")
    parser.add_argument("--crash-signature-report", required=True, help="Crash signature report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_post_release_monitor_report(
        delivery_signoff_report=read_json(args.delivery_signoff_report),
        runtime_signal_report=read_json(args.runtime_signal_report),
        crash_signature_report=read_json(args.crash_signature_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
