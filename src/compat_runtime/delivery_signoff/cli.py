from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _signoff_status(
    *,
    launch_status: str,
    packet_ready: bool,
    runbook_readiness: str,
    dependency_blockers: int,
    release_policy_status: str,
) -> str:
    if (
        launch_status == "ready"
        and packet_ready
        and runbook_readiness == "operational"
        and dependency_blockers == 0
        and release_policy_status == "pass"
    ):
        return "approved"
    if (
        launch_status in {"ready", "limited"}
        and dependency_blockers == 0
        and release_policy_status in {"pass", "missing"}
    ):
        return "conditional"
    return "blocked"


def build_delivery_signoff_report(
    *,
    release_packet_report: dict,
    ops_runbook_report: dict,
    dependency_watch_report: dict,
    readiness_delta_report: dict,
    launch_readiness_report: dict,
) -> dict:
    packet_summary = release_packet_report.get("summary", {})
    runbook_summary = ops_runbook_report.get("summary", {})
    dependency_summary = dependency_watch_report.get("summary", {})
    delta_summary = readiness_delta_report.get("summary", {})

    launch_status = str(launch_readiness_report.get("status", "blocked"))
    packet_ready = bool(packet_summary.get("packet_ready", False))
    runbook_readiness = str(runbook_summary.get("runbook_readiness", "needs_attention"))
    dependency_blockers = int(dependency_summary.get("dependencies_blocking", 0))
    release_policy_status = str(packet_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(packet_summary.get("release_policy_failures", 0))

    status = _signoff_status(
        launch_status=launch_status,
        packet_ready=packet_ready,
        runbook_readiness=runbook_readiness,
        dependency_blockers=dependency_blockers,
        release_policy_status=release_policy_status,
    )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "launch_status": launch_status,
            "packet_ready": packet_ready,
            "runbook_readiness": runbook_readiness,
            "dependency_blockers": dependency_blockers,
            "readiness_score_delta": int(delta_summary.get("readiness_score_delta", 0)),
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "actions": ["Grant final signoff only when status is approved."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build delivery signoff report")
    parser.add_argument("--release-packet-report", required=True, help="Release packet report")
    parser.add_argument("--ops-runbook-report", required=True, help="Ops runbook report")
    parser.add_argument("--dependency-watch-report", required=True, help="Dependency watch report")
    parser.add_argument("--readiness-delta-report", required=True, help="Readiness delta report")
    parser.add_argument("--launch-readiness-report", required=True, help="Launch readiness report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_delivery_signoff_report(
        release_packet_report=read_json(args.release_packet_report),
        ops_runbook_report=read_json(args.ops_runbook_report),
        dependency_watch_report=read_json(args.dependency_watch_report),
        readiness_delta_report=read_json(args.readiness_delta_report),
        launch_readiness_report=read_json(args.launch_readiness_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
