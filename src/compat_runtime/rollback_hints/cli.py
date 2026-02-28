from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _rank_priority(priority: str) -> int:
    return {"P0": 3, "P1": 2, "P2": 1}.get(priority, 0)


def _rollback_level(priority: str, risk: str) -> str:
    if priority == "P0" or risk == "high":
        return "full"
    if priority == "P1" or risk == "medium":
        return "partial"
    return "minimal"


def _trigger_signals(priority: str, category: str, risk: str) -> list[str]:
    signals = [
        "Critical regression detected in targeted suite.",
        "Runtime smoke checks fail after patch deployment.",
    ]
    if priority == "P0":
        signals.append("Production-like scenario blocker reappears.")
    if risk == "high":
        signals.append("Data integrity or process stability risk detected.")
    if category == "installer":
        signals.append("Installer bootstrap no longer reaches expected phase markers.")
    return signals


def _validation_commands(category: str) -> list[str]:
    cmds = ["bash scripts/runtime-core-smoke.sh", "scripts/run-full-pipeline.sh out"]
    category_cmd = {
        "loader": "cargo test --manifest-path runtime-core/Cargo.toml pe::",
        "network": "pytest -q -k network",
        "com": "pytest -q -k com",
        "sync": "cargo test --manifest-path runtime-core/Cargo.toml ntcore::tests::event",
        "file": "cargo test --manifest-path runtime-core/Cargo.toml ntcore::tests::file",
        "registry": "cargo test --manifest-path runtime-core/Cargo.toml ntcore::tests::registry",
        "unimplemented": "cargo test --manifest-path runtime-core/Cargo.toml dispatcher::tests::",
        "installer": "scripts/run-full-pipeline.sh out",
    }.get(category)
    if category_cmd and category_cmd not in cmds:
        cmds.append(category_cmd)
    return cmds


def _proposal_hint(proposal: dict, category: str) -> dict:
    gap_id = str(proposal.get("gap_id", "unknown"))
    priority = str(proposal.get("priority", "P2"))
    risk = str(proposal.get("risk", "medium"))
    level = _rollback_level(priority, risk)

    return {
        "gap_id": gap_id,
        "priority": priority,
        "risk": risk,
        "category": category,
        "rollback_level": level,
        "trigger_signals": _trigger_signals(priority, category, risk),
        "prechecks": [
            "Capture current artifact set and release-bundle-manifest checksum.",
            "Ensure rollback target version/build hash is available.",
        ],
        "rollback_steps": [
            "Disable new patch path behind feature flag or compatibility toggle.",
            "Restore previous known-good implementation branch or binary.",
            "Re-run schema validation and targeted test suites.",
        ],
        "validation_commands": _validation_commands(category),
    }


def _gap_category(gaps: dict) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for gap in gaps.get("gaps", []):
        gap_id = gap.get("id")
        if isinstance(gap_id, str):
            mapping[gap_id] = str(gap.get("category", "runtime"))
    return mapping


def _actions(full: int, partial: int, minimal: int) -> list[str]:
    actions = []
    if full > 0:
        actions.append("Prepare immediate rollback playbook for all full-level hints.")
    if partial > 0:
        actions.append("Schedule staged rollback rehearsals for partial-level hints.")
    if minimal > 0:
        actions.append("Track minimal-level rollback checks in regular regression cadence.")
    if not actions:
        actions.append("No rollback hints generated. Review patch-plan inputs.")
    return actions


def build_rollback_hints(
    *,
    patch_plan: dict,
    gaps: dict,
    test_impact: dict | None = None,
) -> dict:
    categories = _gap_category(gaps)
    hints = []
    full = partial = minimal = 0

    for proposal in patch_plan.get("proposals", []):
        gap_id = str(proposal.get("gap_id", "unknown"))
        category = categories.get(gap_id, "runtime")
        hint = _proposal_hint(proposal, category)
        hints.append(hint)
        level = hint["rollback_level"]
        if level == "full":
            full += 1
        elif level == "partial":
            partial += 1
        else:
            minimal += 1

    highest_priority = "none"
    for proposal in patch_plan.get("proposals", []):
        p = str(proposal.get("priority", "P2"))
        if _rank_priority(p) > _rank_priority(highest_priority):
            highest_priority = p

    suggested_suites = 0
    if test_impact:
        suggested_suites = int(test_impact.get("summary", {}).get("suggested_suites", 0))

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_hints": len(hints),
            "full_rollbacks": full,
            "partial_rollbacks": partial,
            "minimal_rollbacks": minimal,
            "highest_priority": highest_priority,
            "suggested_suites": suggested_suites,
        },
        "hints": hints,
        "actions": _actions(full, partial, minimal),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build rollback hints from patch plan")
    parser.add_argument("--patch-plan", required=True, help="Patch plan JSON path")
    parser.add_argument("--gaps", required=True, help="Gaps JSON path")
    parser.add_argument("--test-impact", required=False, help="Optional test impact JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    patch_plan = read_json(args.patch_plan)
    gaps = read_json(args.gaps)
    test_impact = read_json(args.test_impact) if args.test_impact else None

    artifact = build_rollback_hints(
        patch_plan=patch_plan,
        gaps=gaps,
        test_impact=test_impact,
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()

