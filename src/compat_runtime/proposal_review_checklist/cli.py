from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


VALID_STATUSES = {"pass", "warn", "fail", "todo"}


def _new_item(
    *,
    item_id: str,
    title: str,
    required: bool,
    status: str,
    evidence: str,
    proposal_gap_id: str | None = None,
) -> dict:
    final_status = status if status in VALID_STATUSES else "todo"
    payload = {
        "id": item_id,
        "title": title,
        "required": required,
        "status": final_status,
        "evidence": evidence,
    }
    if proposal_gap_id:
        payload["proposal_gap_id"] = proposal_gap_id
    return payload


def _proposal_index_by_gap(payload: dict, key: str) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for item in payload.get(key, []):
        gap_id = item.get("gap_id")
        if isinstance(gap_id, str):
            index[gap_id] = item
    return index


def _actions(required_failures: int, warns: int, todos: int) -> list[str]:
    actions = []
    if required_failures > 0:
        actions.append("Resolve all required-fail checklist items before approval.")
    if warns > 0:
        actions.append("Review warning items and document accepted risk rationale.")
    if todos > 0:
        actions.append("Complete TODO checklist items before release cut.")
    if not actions:
        actions.append("Checklist is clean. Proceed with final reviewer sign-off.")
    return actions


def build_proposal_review_checklist(
    *,
    patch_plan: dict,
    proposal_provenance: dict | None = None,
    patch_plan_diff: dict | None = None,
    test_impact: dict | None = None,
    rollback_hints: dict | None = None,
) -> dict:
    proposals = patch_plan.get("proposals", [])
    provenance_index = _proposal_index_by_gap(proposal_provenance or {}, "proposals")
    rollback_index = _proposal_index_by_gap(rollback_hints or {}, "hints")

    changed_ids = set()
    if patch_plan_diff:
        for row in patch_plan_diff.get("changed", []):
            gap_id = row.get("gap_id")
            if isinstance(gap_id, str):
                changed_ids.add(gap_id)
        for row in patch_plan_diff.get("added", []):
            gap_id = row.get("gap_id")
            if isinstance(gap_id, str):
                changed_ids.add(gap_id)

    suggested_suites = int((test_impact or {}).get("summary", {}).get("suggested_suites", 0))
    total_hints = int((rollback_hints or {}).get("summary", {}).get("total_hints", 0))

    items = [
        _new_item(
            item_id="patch_plan_has_proposals",
            title="Patch plan contains proposals",
            required=True,
            status="pass" if len(proposals) > 0 else "fail",
            evidence="out/patch-plan.json",
        ),
        _new_item(
            item_id="test_impact_generated",
            title="Test impact suggestions generated",
            required=True,
            status="pass" if suggested_suites > 0 else "fail",
            evidence="out/test-impact-report.json",
        ),
        _new_item(
            item_id="rollback_hints_coverage",
            title="Rollback hints cover all proposals",
            required=True,
            status="pass" if total_hints >= len(proposals) else "fail",
            evidence="out/rollback-hints.json",
        ),
    ]

    for proposal in proposals:
        gap_id = str(proposal.get("gap_id", "unknown"))
        priority = str(proposal.get("priority", "P2"))
        risk = str(proposal.get("risk", "medium"))

        prov = provenance_index.get(gap_id)
        prov_found = bool(prov and prov.get("gap", {}).get("found"))
        prov_score = float((prov or {}).get("provenance", {}).get("provenance_score", 0.0))

        items.append(
            _new_item(
                item_id=f"{gap_id}:provenance_link",
                title=f"{gap_id} linked to gap evidence",
                required=True,
                status="pass" if prov_found else "fail",
                evidence="out/proposal-provenance.json",
                proposal_gap_id=gap_id,
            )
        )
        items.append(
            _new_item(
                item_id=f"{gap_id}:provenance_strength",
                title=f"{gap_id} provenance score acceptable",
                required=False,
                status="pass" if prov_score >= 0.6 else "warn",
                evidence="out/proposal-provenance.json",
                proposal_gap_id=gap_id,
            )
        )

        hint = rollback_index.get(gap_id)
        level = str((hint or {}).get("rollback_level", "unknown"))
        requires_full = priority == "P0" or risk == "high"
        rollback_ok = bool(hint) and (not requires_full or level == "full")

        items.append(
            _new_item(
                item_id=f"{gap_id}:rollback_plan",
                title=f"{gap_id} has rollback plan",
                required=True,
                status="pass" if rollback_ok else "fail",
                evidence="out/rollback-hints.json",
                proposal_gap_id=gap_id,
            )
        )

        if gap_id in changed_ids:
            items.append(
                _new_item(
                    item_id=f"{gap_id}:diff_review",
                    title=f"{gap_id} diff change reviewed",
                    required=False,
                    status="todo",
                    evidence="out/patch-plan-diff.json",
                    proposal_gap_id=gap_id,
                )
            )

    pass_count = sum(1 for item in items if item["status"] == "pass")
    warn_count = sum(1 for item in items if item["status"] == "warn")
    fail_count = sum(1 for item in items if item["status"] == "fail")
    todo_count = sum(1 for item in items if item["status"] == "todo")
    required_failures = sum(
        1 for item in items if item["required"] and item["status"] != "pass"
    )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ready_for_approval": required_failures == 0,
        "summary": {
            "proposal_count": len(proposals),
            "total_items": len(items),
            "pass_items": pass_count,
            "warn_items": warn_count,
            "fail_items": fail_count,
            "todo_items": todo_count,
            "required_failures": required_failures,
        },
        "items": items,
        "actions": _actions(required_failures, warn_count, todo_count),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build proposal reviewer checklist artifact")
    parser.add_argument("--patch-plan", required=True, help="Patch plan JSON path")
    parser.add_argument(
        "--proposal-provenance", required=False, help="Optional proposal provenance JSON path"
    )
    parser.add_argument("--patch-plan-diff", required=False, help="Optional patch plan diff path")
    parser.add_argument("--test-impact", required=False, help="Optional test impact report path")
    parser.add_argument("--rollback-hints", required=False, help="Optional rollback hints path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    patch_plan = read_json(args.patch_plan)
    provenance = read_json(args.proposal_provenance) if args.proposal_provenance else None
    diff = read_json(args.patch_plan_diff) if args.patch_plan_diff else None
    test_impact = read_json(args.test_impact) if args.test_impact else None
    rollback = read_json(args.rollback_hints) if args.rollback_hints else None

    artifact = build_proposal_review_checklist(
        patch_plan=patch_plan,
        proposal_provenance=provenance,
        patch_plan_diff=diff,
        test_impact=test_impact,
        rollback_hints=rollback,
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()

