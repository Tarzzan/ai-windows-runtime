from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


PRIORITY_SCORE = {"P0": 35, "P1": 20, "P2": 10}
DECLARED_RISK_SCORE = {"high": 35, "medium": 20, "low": 10}
SUITE_PRIORITY_SCORE = {"P0": 8, "P1": 5, "P2": 2}
ROLLBACK_SCORE = {"full": 10, "partial": 5, "minimal": 0}


def _changed_ids(patch_plan_diff: dict | None) -> set[str]:
    if not patch_plan_diff:
        return set()
    ids = set()
    for row in patch_plan_diff.get("added", []):
        gap_id = row.get("gap_id")
        if isinstance(gap_id, str):
            ids.add(gap_id)
    for row in patch_plan_diff.get("changed", []):
        gap_id = row.get("gap_id")
        if isinstance(gap_id, str):
            ids.add(gap_id)
    return ids


def _provenance_scores(proposal_provenance: dict | None) -> dict[str, float]:
    scores: dict[str, float] = {}
    if not proposal_provenance:
        return scores
    for row in proposal_provenance.get("proposals", []):
        gap_id = row.get("gap_id")
        if not isinstance(gap_id, str):
            continue
        score = row.get("provenance", {}).get("provenance_score", 0.0)
        try:
            scores[gap_id] = float(score)
        except (TypeError, ValueError):
            scores[gap_id] = 0.0
    return scores


def _rollback_levels(rollback_hints: dict | None) -> dict[str, str]:
    levels: dict[str, str] = {}
    if not rollback_hints:
        return levels
    for row in rollback_hints.get("hints", []):
        gap_id = row.get("gap_id")
        if isinstance(gap_id, str):
            levels[gap_id] = str(row.get("rollback_level", "minimal"))
    return levels


def _suite_priority_map(test_impact: dict | None) -> dict[str, str]:
    by_gap: dict[str, str] = {}
    if not test_impact:
        return by_gap
    for suite in test_impact.get("suites", []):
        suite_priority = str(suite.get("priority", "P2"))
        for gap_id in suite.get("trigger_proposals", []):
            if not isinstance(gap_id, str):
                continue
            current = by_gap.get(gap_id, "P2")
            if PRIORITY_SCORE.get(suite_priority, 0) > PRIORITY_SCORE.get(current, 0):
                by_gap[gap_id] = suite_priority
    return by_gap


def _risk_level(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _actions(high: int, medium: int, weak_provenance: int) -> list[str]:
    actions = []
    if high > 0:
        actions.append("Run explicit senior review for all high-risk proposals.")
    if medium > 0:
        actions.append("Schedule focused validation for medium-risk proposals.")
    if weak_provenance > 0:
        actions.append("Collect stronger evidence for low-provenance proposals before merge.")
    if not actions:
        actions.append("Risk posture is controlled. Continue standard approval workflow.")
    return actions


def build_proposal_risk_report(
    *,
    patch_plan: dict,
    proposal_provenance: dict | None = None,
    patch_plan_diff: dict | None = None,
    test_impact: dict | None = None,
    rollback_hints: dict | None = None,
) -> dict:
    changed = _changed_ids(patch_plan_diff)
    provenance = _provenance_scores(proposal_provenance)
    rollback = _rollback_levels(rollback_hints)
    suite_priority = _suite_priority_map(test_impact)

    entries = []
    high = medium = low = 0
    weak_provenance = 0

    for proposal in patch_plan.get("proposals", []):
        gap_id = str(proposal.get("gap_id", "unknown"))
        priority = str(proposal.get("priority", "P2"))
        declared_risk = str(proposal.get("risk", "medium"))

        score = 0
        drivers = []

        pscore = PRIORITY_SCORE.get(priority, 10)
        score += pscore
        drivers.append(f"priority:{priority}(+{pscore})")

        drscore = DECLARED_RISK_SCORE.get(declared_risk, 15)
        score += drscore
        drivers.append(f"declared_risk:{declared_risk}(+{drscore})")

        pscore_val = provenance.get(gap_id, 0.0)
        if pscore_val < 0.6:
            score += 15
            weak_provenance += 1
            drivers.append("provenance<0.6(+15)")
        elif pscore_val < 0.8:
            score += 8
            drivers.append("provenance<0.8(+8)")
        else:
            drivers.append("provenance>=0.8(+0)")

        if gap_id in changed:
            score += 10
            drivers.append("changed_or_added(+10)")
        else:
            drivers.append("unchanged(+0)")

        rollback_level = rollback.get(gap_id, "minimal")
        rbscore = ROLLBACK_SCORE.get(rollback_level, 0)
        score += rbscore
        drivers.append(f"rollback:{rollback_level}(+{rbscore})")

        suite_p = suite_priority.get(gap_id, "P2")
        sscore = SUITE_PRIORITY_SCORE.get(suite_p, 2)
        score += sscore
        drivers.append(f"test_suite_priority:{suite_p}(+{sscore})")

        score = min(score, 100)
        level = _risk_level(score)

        if level == "high":
            high += 1
        elif level == "medium":
            medium += 1
        else:
            low += 1

        entries.append(
            {
                "gap_id": gap_id,
                "priority": priority,
                "declared_risk": declared_risk,
                "risk_score": score,
                "risk_level": level,
                "provenance_score": round(pscore_val, 3),
                "rollback_level": rollback_level,
                "changed_or_added": gap_id in changed,
                "drivers": drivers,
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_proposals": len(entries),
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low,
            "weak_provenance": weak_provenance,
        },
        "proposals": entries,
        "actions": _actions(high, medium, weak_provenance),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build proposal risk scoring artifact")
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
    rollback_hints = read_json(args.rollback_hints) if args.rollback_hints else None

    artifact = build_proposal_risk_report(
        patch_plan=patch_plan,
        proposal_provenance=provenance,
        patch_plan_diff=diff,
        test_impact=test_impact,
        rollback_hints=rollback_hints,
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()

