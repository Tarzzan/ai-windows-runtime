from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


HOOK_DOMAINS = ["com", "winrt", "registry", "network", "installer"]

DOMAIN_HOOKS = {
    "com": "combase.CoCreateInstance hook with CLSID diagnostics",
    "winrt": "combase.RoActivateInstance hook with activation metadata",
    "registry": "RegOpenKeyEx/RegQueryValueEx coverage with missing-key markers",
    "network": "WinHttpSendRequest/WinHttpReceiveResponse handshake tracing",
    "installer": "CreateProcess/Wait bootstrap phase markers and timeout probes",
}

DOMAIN_KEYWORDS = {
    "com": ("com", "cocreateinstance", "ole"),
    "winrt": ("winrt", "roactivateinstance", "rogetactivationfactory"),
    "registry": ("registry", "reg", "key", "value"),
    "network": ("network", "winhttp", "http", "tls", "proxy"),
    "installer": ("installer", "bootstrap", "c2r", "setup"),
}


def _risk_by_gap_id(proposal_risk_report: dict) -> dict[str, dict]:
    rows = {}
    for proposal in proposal_risk_report.get("proposals", []):
        gap_id = proposal.get("gap_id")
        if isinstance(gap_id, str):
            rows[gap_id] = proposal
    return rows


def _domain_from_title(title: str) -> str | None:
    text = title.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return domain
    return None


def _domain_proposals(patch_plan: dict) -> dict[str, list[str]]:
    by_domain = {domain: [] for domain in HOOK_DOMAINS}
    for proposal in patch_plan.get("proposals", []):
        gap_id = proposal.get("gap_id")
        title = str(proposal.get("title", ""))
        if not isinstance(gap_id, str):
            continue
        domain = _domain_from_title(title)
        if domain is None:
            continue
        by_domain[domain].append(gap_id)
    return by_domain


def _urgency(errors: int, high_risk_related: int, events: int) -> str:
    if errors > 0 or high_risk_related > 0:
        return "P0"
    if events > 0:
        return "P1"
    return "P2"


def _impact_score(
    *,
    events: int,
    errors: int,
    high_risk_related: int,
    medium_risk_related: int,
) -> int:
    score = 0
    score += events * 4
    score += errors * 15
    score += high_risk_related * 20
    score += medium_risk_related * 8
    return min(score, 100)


def _actions(items: list[dict]) -> list[str]:
    missing = [item for item in items if item["missing_hook"]]
    if not missing:
        return ["No missing runtime hooks detected for tracked domains."]

    p0 = [item for item in missing if item["urgency"] == "P0"]
    actions = []
    if p0:
        top = ", ".join(item["domain"] for item in p0[:3])
        actions.append(f"Implement P0 runtime hooks first: {top}.")
    actions.append("Attach hook-backlog-report.json to runtime instrumentation planning.")
    return actions


def build_hook_backlog_report(
    *,
    runtime_signal_report: dict,
    patch_plan: dict,
    proposal_risk_report: dict,
) -> dict:
    coverage_rows = {row.get("domain"): row for row in runtime_signal_report.get("coverage", [])}
    proposal_by_domain = _domain_proposals(patch_plan)
    risk_by_gap = _risk_by_gap_id(proposal_risk_report)

    items = []
    total_related_high_risk = 0
    total_related = 0
    for domain in HOOK_DOMAINS:
        coverage = coverage_rows.get(domain, {}) if isinstance(coverage_rows.get(domain), dict) else {}
        events = int(coverage.get("events", 0))
        errors = int(coverage.get("errors", 0))
        hook_present = bool(coverage.get("hook_present", False))
        gap_ids = proposal_by_domain.get(domain, [])

        high_risk_related = 0
        medium_risk_related = 0
        for gap_id in gap_ids:
            risk_row = risk_by_gap.get(gap_id, {})
            risk_level = str(risk_row.get("risk_level", "unknown"))
            if risk_level == "high":
                high_risk_related += 1
            elif risk_level == "medium":
                medium_risk_related += 1

        total_related_high_risk += high_risk_related
        total_related += len(gap_ids)

        urgency = _urgency(errors, high_risk_related, events)
        impact = _impact_score(
            events=events,
            errors=errors,
            high_risk_related=high_risk_related,
            medium_risk_related=medium_risk_related,
        )

        rationale_parts = [
            f"events={events}",
            f"errors={errors}",
            f"related_proposals={len(gap_ids)}",
            f"related_high_risk={high_risk_related}",
        ]
        items.append(
            {
                "domain": domain,
                "missing_hook": not hook_present,
                "urgency": urgency,
                "impact_score": impact,
                "events": events,
                "errors": errors,
                "related_proposals": len(gap_ids),
                "related_high_risk": high_risk_related,
                "recommended_hook": DOMAIN_HOOKS[domain],
                "rationale": ", ".join(rationale_parts),
            }
        )

    items.sort(
        key=lambda row: (
            0 if row["missing_hook"] else 1,
            0 if row["urgency"] == "P0" else (1 if row["urgency"] == "P1" else 2),
            -row["impact_score"],
            row["domain"],
        )
    )

    missing_items = [item for item in items if item["missing_hook"]]
    p0_items = [item for item in missing_items if item["urgency"] == "P0"]
    missing_with_errors = [item for item in missing_items if item["errors"] > 0]

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "domains_considered": len(HOOK_DOMAINS),
            "missing_hooks": len(missing_items),
            "missing_hooks_with_errors": len(missing_with_errors),
            "p0_items": len(p0_items),
            "related_proposals": total_related,
            "related_high_risk_proposals": total_related_high_risk,
        },
        "items": items,
        "actions": _actions(items),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build runtime hook backlog prioritization report")
    parser.add_argument("--runtime-signal-report", required=True, help="Runtime signal report path")
    parser.add_argument("--patch-plan", required=True, help="Patch plan path")
    parser.add_argument("--proposal-risk-report", required=True, help="Proposal risk report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_hook_backlog_report(
        runtime_signal_report=read_json(args.runtime_signal_report),
        patch_plan=read_json(args.patch_plan),
        proposal_risk_report=read_json(args.proposal_risk_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
