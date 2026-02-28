from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


SUITE_PLAYBOOK = {
    "loader": {
        "id": "pe-loader-regression",
        "name": "PE Loader Regression Suite",
        "command": "cargo test --manifest-path runtime-core/Cargo.toml pe::",
        "minutes": 12,
        "reason": "Validate import/export/relocation behavior.",
    },
    "com": {
        "id": "com-activation-suite",
        "name": "COM Activation Suite",
        "command": "pytest -q -k com",
        "minutes": 8,
        "reason": "Validate COM activation and class/object dispatch behavior.",
    },
    "installer": {
        "id": "installer-bootstrap-suite",
        "name": "Installer Bootstrap Suite",
        "command": "scripts/run-full-pipeline.sh out",
        "minutes": 15,
        "reason": "Validate installer bootstrap flow and instrumentation.",
    },
    "network": {
        "id": "winhttp-network-suite",
        "name": "WinHTTP Compatibility Suite",
        "command": "pytest -q -k network",
        "minutes": 8,
        "reason": "Validate runtime network negotiation compatibility.",
    },
    "sync": {
        "id": "sync-waits-suite",
        "name": "Sync/Waits Suite",
        "command": "cargo test --manifest-path runtime-core/Cargo.toml ntcore::tests::event",
        "minutes": 6,
        "reason": "Validate deterministic wait/event/mutex behavior.",
    },
    "file": {
        "id": "file-io-suite",
        "name": "File Adapter Suite",
        "command": "cargo test --manifest-path runtime-core/Cargo.toml ntcore::tests::file",
        "minutes": 6,
        "reason": "Validate file adapter semantics and handle lifecycle.",
    },
    "registry": {
        "id": "registry-adapter-suite",
        "name": "Registry Adapter Suite",
        "command": "cargo test --manifest-path runtime-core/Cargo.toml ntcore::tests::registry",
        "minutes": 6,
        "reason": "Validate registry key/value behavior and compatibility.",
    },
    "unimplemented": {
        "id": "api-stub-contract-suite",
        "name": "API Stub Contract Suite",
        "command": "cargo test --manifest-path runtime-core/Cargo.toml dispatcher::tests::",
        "minutes": 7,
        "reason": "Validate implemented/stubbed/missing API dispatch decisions.",
    },
    "runtime": {
        "id": "runtime-smoke-suite",
        "name": "Runtime Smoke Suite",
        "command": "bash scripts/runtime-core-smoke.sh",
        "minutes": 5,
        "reason": "Validate minimal runtime execution flow end-to-end.",
    },
}


def _priority_rank(priority: str) -> int:
    return {"P0": 3, "P1": 2, "P2": 1}.get(priority, 0)


def _suite_priority(current: str, candidate: str) -> str:
    return candidate if _priority_rank(candidate) > _priority_rank(current) else current


def _gap_index(gaps: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for gap in gaps.get("gaps", []):
        gap_id = gap.get("id")
        if isinstance(gap_id, str):
            index[gap_id] = gap
    return index


def _root_cause_alignment(root_cause: dict | None, covered_categories: set[str]) -> list[dict]:
    if not root_cause:
        return []
    rows = []
    for cluster in root_cause.get("root_cause_clusters", []):
        category = str(cluster.get("category", "runtime"))
        rows.append(
            {
                "category": category,
                "count": int(cluster.get("count", 0)),
                "covered": category in covered_categories or "runtime" in covered_categories,
            }
        )
    return rows


def _actions(*, high_priority: int, weak_provenance: int, uncovered: list[str]) -> list[str]:
    actions = []
    if high_priority > 0:
        actions.append("Run high-priority suites first (P0-linked proposals).")
    if weak_provenance > 0:
        actions.append("Investigate weak provenance entries before broadening test scope.")
    if uncovered:
        actions.append("Add test mapping for uncovered categories: " + ", ".join(uncovered))
    if not actions:
        actions.append("Current test impact is stable. Keep smoke + targeted suites in CI.")
    return actions


def build_test_impact_report(
    *,
    patch_plan: dict,
    gaps: dict,
    root_cause: dict | None = None,
    proposal_provenance: dict | None = None,
) -> dict:
    gap_by_id = _gap_index(gaps)
    suites: dict[str, dict] = {}
    impacted_categories: set[str] = set()

    for proposal in patch_plan.get("proposals", []):
        gap_id = str(proposal.get("gap_id", ""))
        priority = str(proposal.get("priority", "P2"))
        gap = gap_by_id.get(gap_id, {})
        category = str(gap.get("category", "runtime"))
        impacted_categories.add(category)
        suite_meta = SUITE_PLAYBOOK.get(category, SUITE_PLAYBOOK["runtime"])
        suite_id = suite_meta["id"]

        if suite_id not in suites:
            suites[suite_id] = {
                "id": suite_id,
                "name": suite_meta["name"],
                "priority": priority,
                "estimated_minutes": suite_meta["minutes"],
                "trigger_categories": [category],
                "trigger_proposals": [gap_id] if gap_id else [],
                "suggested_command": suite_meta["command"],
                "reason": suite_meta["reason"],
            }
        else:
            entry = suites[suite_id]
            entry["priority"] = _suite_priority(str(entry["priority"]), priority)
            if category not in entry["trigger_categories"]:
                entry["trigger_categories"].append(category)
            if gap_id and gap_id not in entry["trigger_proposals"]:
                entry["trigger_proposals"].append(gap_id)

    # Always include global smoke checks.
    smoke_meta = SUITE_PLAYBOOK["runtime"]
    if smoke_meta["id"] not in suites:
        suites[smoke_meta["id"]] = {
            "id": smoke_meta["id"],
            "name": smoke_meta["name"],
            "priority": "P2",
            "estimated_minutes": smoke_meta["minutes"],
            "trigger_categories": ["runtime"],
            "trigger_proposals": [],
            "suggested_command": smoke_meta["command"],
            "reason": smoke_meta["reason"],
        }

    suite_list = sorted(
        suites.values(),
        key=lambda item: (-_priority_rank(str(item["priority"])), str(item["id"])),
    )

    weak_entries = 0
    if proposal_provenance:
        weak_entries = int(proposal_provenance.get("summary", {}).get("weak_provenance_entries", 0))

    categories_without_suite = sorted(
        category for category in impacted_categories if category not in SUITE_PLAYBOOK
    )
    high_priority_suites = sum(1 for suite in suite_list if suite["priority"] == "P0")
    covered_categories = {
        category for suite in suite_list for category in suite.get("trigger_categories", [])
    }

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_proposals": len(patch_plan.get("proposals", [])),
            "impacted_categories": len(impacted_categories),
            "suggested_suites": len(suite_list),
            "high_priority_suites": high_priority_suites,
            "weak_provenance_entries": weak_entries,
        },
        "suites": suite_list,
        "coverage": {
            "categories_without_suite": categories_without_suite,
            "root_cause_alignment": _root_cause_alignment(root_cause, covered_categories),
        },
        "actions": _actions(
            high_priority=high_priority_suites,
            weak_provenance=weak_entries,
            uncovered=categories_without_suite,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build test impact report from patch proposals")
    parser.add_argument("--patch-plan", required=True, help="Patch plan JSON path")
    parser.add_argument("--gaps", required=True, help="Gaps JSON path")
    parser.add_argument("--root-cause", required=False, help="Optional root-cause summary path")
    parser.add_argument(
        "--proposal-provenance", required=False, help="Optional proposal provenance JSON path"
    )
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    patch_plan = read_json(args.patch_plan)
    gaps = read_json(args.gaps)
    root_cause = read_json(args.root_cause) if args.root_cause else None
    provenance = read_json(args.proposal_provenance) if args.proposal_provenance else None

    report = build_test_impact_report(
        patch_plan=patch_plan,
        gaps=gaps,
        root_cause=root_cause,
        proposal_provenance=provenance,
    )
    write_json(args.output, report)


if __name__ == "__main__":
    main()

