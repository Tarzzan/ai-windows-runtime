from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _category_hint(category: str) -> str:
    hints = {
        "loader": "Prioritize loader/import resolution and dependency search path rules.",
        "com": "Expand COM activation path and class registration behavior.",
        "installer": "Instrument installer stages and bootstrap handshakes.",
        "network": "Improve winhttp and TLS/proxy compatibility behavior.",
        "sync": "Harden wait semantics for mutex/event synchronization.",
        "file": "Expand file adapter semantics for handles and path edge-cases.",
        "registry": "Increase registry key/value behavior fidelity.",
        "unimplemented": "Implement missing APIs with behavior-focused tests.",
    }
    return hints.get(category, "Investigate runtime limitation and define a minimal shim.")


def _priority_of_gap(gap_id: str, proposals: list[dict]) -> str:
    for proposal in proposals:
        if proposal.get("gap_id") == gap_id:
            return str(proposal.get("priority", "P2"))
    return "P2"


def _build_scenario_summary(label: str, gaps: dict, patch_plan: dict | None) -> dict:
    items = gaps.get("gaps", [])
    proposals = (patch_plan or {}).get("proposals", [])
    category_counts: dict[str, int] = {}
    high_severity = 0
    p0_links = 0
    top_gaps = []

    for gap in items:
        category = str(gap.get("category", "runtime"))
        severity = str(gap.get("severity", "low"))
        gap_id = str(gap.get("id", "unknown"))
        priority = _priority_of_gap(gap_id, proposals)

        category_counts[category] = category_counts.get(category, 0) + 1
        if severity == "high":
            high_severity += 1
        if priority == "P0":
            p0_links += 1

        top_gaps.append(
            {
                "id": gap_id,
                "category": category,
                "severity": severity,
                "priority": priority,
                "summary": str(gap.get("summary", "")),
            }
        )

    top_categories = [
        {"category": category, "count": count, "hint": _category_hint(category)}
        for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    return {
        "label": label,
        "gap_count": len(items),
        "high_severity_gaps": high_severity,
        "p0_linked_proposals": p0_links,
        "top_categories": top_categories[:5],
        "top_gaps": top_gaps[:5],
    }


def _aggregate_categories(scenarios: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for scenario in scenarios:
        for entry in scenario.get("top_categories", []):
            category = str(entry.get("category", "runtime"))
            counts[category] = counts.get(category, 0) + int(entry.get("count", 0))
    return [
        {"category": category, "count": count, "hint": _category_hint(category)}
        for category, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _action_hints(global_categories: list[dict], has_p0: bool) -> list[str]:
    actions = []
    if has_p0:
        actions.append("Address P0-linked gaps first before lower-priority categories.")
    for entry in global_categories[:3]:
        actions.append(entry["hint"])
    if not actions:
        actions.append("No critical gap detected. Continue collecting broader compatibility corpus.")
    return actions


def build_root_cause_summary(
    gap_artifacts: list[dict],
    *,
    patch_plan_artifacts: list[dict] | None = None,
    labels: list[str] | None = None,
) -> dict:
    patch_plans = patch_plan_artifacts or []
    scenario_summaries = []

    for index, gaps in enumerate(gap_artifacts):
        label = labels[index] if labels and index < len(labels) else f"scenario-{index + 1}"
        plan = patch_plans[index] if index < len(patch_plans) else None
        scenario_summaries.append(_build_scenario_summary(label, gaps, plan))

    total_gaps = sum(int(s["gap_count"]) for s in scenario_summaries)
    high_severity_gaps = sum(int(s["high_severity_gaps"]) for s in scenario_summaries)
    p0_linked_proposals = sum(int(s["p0_linked_proposals"]) for s in scenario_summaries)
    global_categories = _aggregate_categories(scenario_summaries)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scenario_count": len(scenario_summaries),
            "total_gaps": total_gaps,
            "high_severity_gaps": high_severity_gaps,
            "p0_linked_proposals": p0_linked_proposals,
            "top_root_causes": [entry["category"] for entry in global_categories[:5]],
        },
        "root_cause_clusters": global_categories,
        "scenarios": scenario_summaries,
        "actions": _action_hints(global_categories, has_p0=p0_linked_proposals > 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build root cause summary from gap artifacts")
    parser.add_argument("--gaps", required=True, nargs="+", help="Gap artifact paths")
    parser.add_argument(
        "--patch-plans",
        required=False,
        nargs="*",
        help="Optional patch plan paths aligned with --gaps order",
    )
    parser.add_argument(
        "--labels",
        required=False,
        nargs="*",
        help="Optional scenario labels aligned with --gaps order",
    )
    parser.add_argument("--output", required=True, help="Root cause summary output path")
    args = parser.parse_args()

    gaps = [read_json(path) for path in args.gaps]
    patch_plans = [read_json(path) for path in (args.patch_plans or [])]
    summary = build_root_cause_summary(
        gaps,
        patch_plan_artifacts=patch_plans,
        labels=args.labels,
    )
    write_json(args.output, summary)


if __name__ == "__main__":
    main()

