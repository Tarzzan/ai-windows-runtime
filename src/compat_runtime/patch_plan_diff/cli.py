from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


TRACKED_FIELDS = ("priority", "title", "risk", "validation")


def _proposal_index(plan: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for proposal in plan.get("proposals", []):
        gap_id = proposal.get("gap_id")
        if isinstance(gap_id, str):
            index[gap_id] = proposal
    return index


def _change_entry(gap_id: str, before: dict, after: dict) -> dict | None:
    changed_fields = []
    for field in TRACKED_FIELDS:
        if before.get(field) != after.get(field):
            changed_fields.append(field)
    if not changed_fields:
        return None
    return {
        "gap_id": gap_id,
        "changed_fields": changed_fields,
        "before": {field: before.get(field) for field in TRACKED_FIELDS},
        "after": {field: after.get(field) for field in TRACKED_FIELDS},
    }


def _reviewer_focus(added: int, removed: int, changed: int) -> list[str]:
    focus = []
    if added > 0:
        focus.append("Review newly added proposals and confirm prioritization.")
    if changed > 0:
        focus.append("Review changed proposal fields and validate updated risk/priority.")
    if removed > 0:
        focus.append("Confirm removed proposals are intentionally deprecated.")
    if not focus:
        focus.append("No diff detected. Reuse previous reviewer approvals.")
    return focus


def build_patch_plan_diff(
    *,
    current_plan: dict,
    baseline_plan: dict | None = None,
    current_label: str = "current",
    baseline_label: str = "baseline",
) -> dict:
    baseline = baseline_plan or {"artifact_version": "1.0", "proposals": []}
    current_index = _proposal_index(current_plan)
    baseline_index = _proposal_index(baseline)

    current_ids = set(current_index.keys())
    baseline_ids = set(baseline_index.keys())

    added_ids = sorted(current_ids - baseline_ids)
    removed_ids = sorted(baseline_ids - current_ids)
    common_ids = sorted(current_ids & baseline_ids)

    added = [current_index[gap_id] for gap_id in added_ids]
    removed = [baseline_index[gap_id] for gap_id in removed_ids]
    changed = []
    for gap_id in common_ids:
        entry = _change_entry(gap_id, baseline_index[gap_id], current_index[gap_id])
        if entry:
            changed.append(entry)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "baseline_label": baseline_label,
            "current_label": current_label,
        },
        "summary": {
            "baseline_count": len(baseline_index),
            "current_count": len(current_index),
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": len(common_ids) - len(changed),
        },
        "added": added,
        "removed": removed,
        "changed": changed,
        "reviewer_focus": _reviewer_focus(len(added), len(removed), len(changed)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build patch plan diff artifact")
    parser.add_argument("--current", required=True, help="Current patch-plan JSON path")
    parser.add_argument("--baseline", required=False, help="Optional baseline patch-plan path")
    parser.add_argument(
        "--current-label",
        required=False,
        default="current",
        help="Current source label",
    )
    parser.add_argument(
        "--baseline-label",
        required=False,
        default="baseline",
        help="Baseline source label",
    )
    parser.add_argument("--output", required=True, help="Patch plan diff JSON output path")
    args = parser.parse_args()

    current = read_json(args.current)
    baseline = read_json(args.baseline) if args.baseline else None
    diff = build_patch_plan_diff(
        current_plan=current,
        baseline_plan=baseline,
        current_label=args.current_label,
        baseline_label=args.baseline_label,
    )
    write_json(args.output, diff)


if __name__ == "__main__":
    main()

