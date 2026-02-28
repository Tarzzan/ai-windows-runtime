from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _gap_index(gaps: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for gap in gaps.get("gaps", []):
        gap_id = gap.get("id")
        if isinstance(gap_id, str):
            index[gap_id] = gap
    return index


def _trace_evidence(trace: dict | None, category: str, severity: str) -> tuple[int, list[str]]:
    if not trace:
        return 0, []

    messages: list[str] = []
    count = 0
    for event in trace.get("events", []):
        event_category = str(event.get("category", "runtime"))
        event_severity = str(event.get("severity", "low"))
        if event_category != category:
            continue
        if severity != "unknown" and event_severity != severity:
            continue
        count += 1
        message = str(event.get("message", "")).strip()
        if message and message not in messages:
            messages.append(message)
        if len(messages) >= 3:
            break
    return count, messages


def _provenance_score(*, has_gap: bool, gap_confidence: float, trace_event_count: int) -> float:
    if not has_gap:
        return 0.0
    bonus = min(trace_event_count, 5) * 0.05
    return round(min(1.0, gap_confidence + bonus), 3)


def _actions(*, unmatched: int, weak: int) -> list[str]:
    hints = []
    if unmatched > 0:
        hints.append("Resolve unmatched proposal->gap links before implementation review.")
    if weak > 0:
        hints.append("Collect more trace evidence for low-confidence provenance entries.")
    if not hints:
        hints.append("Provenance coverage is consistent. Continue reviewer validation workflow.")
    return hints


def build_proposal_provenance(
    *,
    patch_plan: dict,
    gaps: dict,
    trace: dict | None = None,
) -> dict:
    gap_by_id = _gap_index(gaps)
    entries = []
    matched = 0
    weak = 0

    for proposal in patch_plan.get("proposals", []):
        gap_id = str(proposal.get("gap_id", "unknown"))
        gap = gap_by_id.get(gap_id)
        has_gap = gap is not None
        category = str(gap.get("category", "unknown")) if has_gap else "unknown"
        severity = str(gap.get("severity", "unknown")) if has_gap else "unknown"
        confidence = float(gap.get("confidence", 0.0)) if has_gap else 0.0
        gap_summary = str(gap.get("summary", "")) if has_gap else ""

        trace_count, evidence = _trace_evidence(trace, category, severity)
        score = _provenance_score(
            has_gap=has_gap, gap_confidence=confidence, trace_event_count=trace_count
        )
        if has_gap:
            matched += 1
        if score < 0.6:
            weak += 1

        entries.append(
            {
                "gap_id": gap_id,
                "priority": str(proposal.get("priority", "P2")),
                "title": str(proposal.get("title", "")),
                "risk": str(proposal.get("risk", "unknown")),
                "gap": {
                    "found": has_gap,
                    "category": category,
                    "severity": severity,
                    "confidence": confidence,
                    "summary": gap_summary,
                },
                "provenance": {
                    "lineage": "trace->gaps->patch-plan",
                    "source_artifacts": ["trace.json", "gaps.json", "patch-plan.json"],
                    "trace_event_count": trace_count,
                    "evidence_messages": evidence,
                    "provenance_score": score,
                },
            }
        )

    unmatched = len(entries) - matched
    events_considered = len(trace.get("events", [])) if trace else 0

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_proposals": len(entries),
            "matched_gaps": matched,
            "unmatched_gaps": unmatched,
            "events_considered": events_considered,
            "weak_provenance_entries": weak,
        },
        "proposals": entries,
        "actions": _actions(unmatched=unmatched, weak=weak),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build proposal provenance artifact")
    parser.add_argument("--patch-plan", required=True, help="Patch plan JSON path")
    parser.add_argument("--gaps", required=True, help="Gaps JSON path")
    parser.add_argument("--trace", required=False, help="Optional trace JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    patch_plan = read_json(args.patch_plan)
    gaps = read_json(args.gaps)
    trace = read_json(args.trace) if args.trace else None
    artifact = build_proposal_provenance(patch_plan=patch_plan, gaps=gaps, trace=trace)
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()

