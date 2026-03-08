from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _policy_compliance_level(*, policy_config_valid: bool, policy_lockfile_sync: bool) -> str:
    if policy_config_valid and policy_lockfile_sync:
        return "compliant"
    if policy_config_valid or policy_lockfile_sync:
        return "degraded"
    return "non_compliant"


def build_release_packet_report(
    *,
    launch_readiness_report: dict,
    release_bundle_manifest: dict,
    stakeholder_update_report: dict,
    policy_health_report: dict | None = None,
) -> dict:
    launch_status = str(launch_readiness_report.get("status", "blocked"))
    launch_summary = launch_readiness_report.get("summary", {})
    files = release_bundle_manifest.get("files", [])
    missing = release_bundle_manifest.get("missing", [])
    stakeholder_summary = stakeholder_update_report.get("summary", {})
    policy_health_summary = policy_health_report or {}
    policy_config_valid = bool(policy_health_summary.get("config_valid", False))
    policy_lockfile_sync = bool(policy_health_summary.get("lockfile_sync", False))

    packet_ready = launch_status in {"ready", "limited"} and len(missing) == 0

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "packet_ready": packet_ready,
            "launch_status": launch_status,
            "release_decision": str(launch_summary.get("release_decision", "no-go")),
            "bundle_files": len(files),
            "bundle_missing": len(missing),
            "stakeholder_delivery_status": str(stakeholder_summary.get("delivery_status", "at_risk")),
            "policy_config_valid": policy_config_valid,
            "policy_lockfile_sync": policy_lockfile_sync,
            "policy_compliance_level": _policy_compliance_level(
                policy_config_valid=policy_config_valid,
                policy_lockfile_sync=policy_lockfile_sync,
            ),
        },
        "missing": missing,
        "actions": [
            "Finalize release packet only when bundle_missing is zero.",
            "Keep stakeholder update attached to packet handoff.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release packet report")
    parser.add_argument("--launch-readiness-report", required=True, help="Launch readiness report path")
    parser.add_argument("--release-bundle-manifest", required=True, help="Release bundle manifest path")
    parser.add_argument("--stakeholder-update-report", required=True, help="Stakeholder update report path")
    parser.add_argument("--policy-health-report", required=False, help="Optional policy health report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    policy_health_report: dict | None = None
    if args.policy_health_report:
        policy_health_report = read_json(args.policy_health_report)

    artifact = build_release_packet_report(
        launch_readiness_report=read_json(args.launch_readiness_report),
        release_bundle_manifest=read_json(args.release_bundle_manifest),
        stakeholder_update_report=read_json(args.stakeholder_update_report),
        policy_health_report=policy_health_report,
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
