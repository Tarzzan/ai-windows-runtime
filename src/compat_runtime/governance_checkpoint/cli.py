from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _checkpoint_status(
    window_status: str,
    plan_mode: str,
    missing_reports: int,
    policy_config_valid: bool,
    policy_lockfile_sync: bool,
) -> str:
    if not policy_config_valid or not policy_lockfile_sync:
        return "block"
    if window_status == "stable" and plan_mode == "routine" and missing_reports == 0:
        return "pass"
    if missing_reports == 0 and window_status in {"stable", "watch"}:
        return "conditional"
    return "block"


def build_governance_checkpoint_report(
    *,
    stability_window_report: dict,
    hotfix_planner_report: dict,
    verification_snapshot_report: dict,
    evidence_catalog_report: dict,
) -> dict:
    window_summary = stability_window_report.get("summary", {})
    hotfix_summary = hotfix_planner_report.get("summary", {})
    snapshot_summary = verification_snapshot_report.get("summary", {})
    catalog_summary = evidence_catalog_report.get("summary", {})
    policy_config_valid = bool(catalog_summary.get("policy_config_valid", False))
    policy_lockfile_sync = bool(catalog_summary.get("policy_lockfile_sync", False))
    policy_compliance_level = str(catalog_summary.get("policy_compliance_level", "non_compliant"))

    status = _checkpoint_status(
        str(window_summary.get("window_status", "unstable")),
        str(hotfix_summary.get("plan_mode", "urgent")),
        int(snapshot_summary.get("missing_reports", 1)),
        policy_config_valid,
        policy_lockfile_sync,
    )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "window_status": str(window_summary.get("window_status", "unstable")),
            "hotfix_plan_mode": str(hotfix_summary.get("plan_mode", "urgent")),
            "missing_reports": int(snapshot_summary.get("missing_reports", 0)),
            "catalog_items": int(catalog_summary.get("catalog_items", 0)),
            "policy_config_valid": policy_config_valid,
            "policy_lockfile_sync": policy_lockfile_sync,
            "policy_compliance_level": policy_compliance_level,
        },
        "actions": ["Proceed only when governance checkpoint status is pass or conditional."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build governance checkpoint report")
    parser.add_argument("--stability-window-report", required=True, help="Stability window report")
    parser.add_argument("--hotfix-planner-report", required=True, help="Hotfix planner report")
    parser.add_argument("--verification-snapshot-report", required=True, help="Verification snapshot")
    parser.add_argument("--evidence-catalog-report", required=True, help="Evidence catalog report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_governance_checkpoint_report(
        stability_window_report=read_json(args.stability_window_report),
        hotfix_planner_report=read_json(args.hotfix_planner_report),
        verification_snapshot_report=read_json(args.verification_snapshot_report),
        evidence_catalog_report=read_json(args.evidence_catalog_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
