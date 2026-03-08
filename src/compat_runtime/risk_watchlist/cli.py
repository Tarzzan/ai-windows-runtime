from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _entry(entry_id: str, kind: str, priority: str, detail: str, evidence: str) -> dict:
    return {
        "id": entry_id,
        "kind": kind,
        "priority": priority,
        "detail": detail,
        "evidence": evidence,
    }


def build_risk_watchlist_report(
    *,
    proposal_risk_report: dict,
    hook_backlog_report: dict,
    runtime_signal_report: dict,
    release_policy_report: dict | None = None,
) -> dict:
    entries = []

    for proposal in proposal_risk_report.get("proposals", []):
        gap_id = str(proposal.get("gap_id", "unknown"))
        risk_level = str(proposal.get("risk_level", "low"))
        if risk_level == "high":
            entries.append(
                _entry(
                    f"risk-{gap_id}",
                    "proposal_risk",
                    "P0",
                    f"High-risk proposal {gap_id} (score={proposal.get('risk_score', 'n/a')})",
                    "out/proposal-risk-report.json",
                )
            )
        elif risk_level == "medium":
            entries.append(
                _entry(
                    f"risk-{gap_id}",
                    "proposal_risk",
                    "P1",
                    f"Medium-risk proposal {gap_id} (score={proposal.get('risk_score', 'n/a')})",
                    "out/proposal-risk-report.json",
                )
            )

    for item in hook_backlog_report.get("items", []):
        if not item.get("missing_hook"):
            continue
        domain = str(item.get("domain", "runtime"))
        urgency = str(item.get("urgency", "P1"))
        detail = (
            f"Missing {domain} hook, errors={item.get('errors', 0)}, "
            f"related_high_risk={item.get('related_high_risk', 0)}"
        )
        entries.append(
            _entry(
                f"hook-{domain}",
                "hook_backlog",
                urgency,
                detail,
                "out/hook-backlog-report.json",
            )
        )

    for issue in runtime_signal_report.get("issues", []):
        severity = str(issue.get("severity", "medium"))
        if severity != "high":
            continue
        issue_id = str(issue.get("id", "issue"))
        domain = str(issue.get("domain", "runtime"))
        entries.append(
            _entry(
                f"signal-{issue_id}",
                "runtime_signal",
                "P1",
                f"High-severity runtime issue in {domain}: {issue.get('message', '')}",
                "out/runtime-signal-report.json",
            )
        )

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    entries.sort(key=lambda row: (priority_order.get(row["priority"], 3), row["id"]))

    p0 = sum(1 for row in entries if row["priority"] == "P0")
    p1 = sum(1 for row in entries if row["priority"] == "P1")
    p2 = sum(1 for row in entries if row["priority"] == "P2")
    policy = release_policy_report or {}
    release_policy_status = str(policy.get("status", "missing"))
    release_policy_failures = len(policy.get("failures", []))

    actions = []
    if p0 > 0:
        actions.append("Escalate P0 watchlist entries in next triage meeting.")
    if p1 > 0:
        actions.append("Track P1 watchlist entries with explicit owners and due dates.")
    if not actions:
        actions.append("No significant watchlist entry detected.")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "entries_total": len(entries),
            "p0_entries": p0,
            "p1_entries": p1,
            "p2_entries": p2,
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "entries": entries,
        "actions": actions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build consolidated risk watchlist report")
    parser.add_argument("--proposal-risk-report", required=True, help="Proposal risk report path")
    parser.add_argument("--hook-backlog-report", required=True, help="Hook backlog report path")
    parser.add_argument("--runtime-signal-report", required=True, help="Runtime signal report path")
    parser.add_argument("--release-policy-report", required=False, help="Optional release policy report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_risk_watchlist_report(
        proposal_risk_report=read_json(args.proposal_risk_report),
        hook_backlog_report=read_json(args.hook_backlog_report),
        runtime_signal_report=read_json(args.runtime_signal_report),
        release_policy_report=read_json(args.release_policy_report) if args.release_policy_report else None,
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
