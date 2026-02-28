from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


TEMPLATE_LIBRARY = {
    "tpl-loader-import": {
        "title": "Loader/import compatibility patch",
        "default_priority": "P0",
        "default_risk": "high",
        "strategy": "Implement missing import resolution or dependency search-path handling.",
        "validation_focus": "PE loader/import regression tests",
    },
    "tpl-com-activation": {
        "title": "COM activation shim",
        "default_priority": "P0",
        "default_risk": "high",
        "strategy": "Implement COM class registration/activation behavior or targeted shim.",
        "validation_focus": "COM activation and object lifecycle tests",
    },
    "tpl-installer-bootstrap": {
        "title": "Installer bootstrap instrumentation",
        "default_priority": "P0",
        "default_risk": "high",
        "strategy": "Instrument bootstrap stages and close installer handshake gaps.",
        "validation_focus": "Installer phase markers and full pipeline run",
    },
    "tpl-network-winhttp": {
        "title": "WinHTTP/network compatibility patch",
        "default_priority": "P1",
        "default_risk": "medium",
        "strategy": "Expand protocol negotiation and compatibility behavior for network calls.",
        "validation_focus": "Network negotiation and transport regression tests",
    },
    "tpl-sync-primitives": {
        "title": "Sync primitive behavior patch",
        "default_priority": "P1",
        "default_risk": "medium",
        "strategy": "Harden wait semantics and synchronization object state transitions.",
        "validation_focus": "Wait/event/mutex deterministic tests",
    },
    "tpl-file-adapter": {
        "title": "File adapter semantics patch",
        "default_priority": "P1",
        "default_risk": "medium",
        "strategy": "Improve file handle, cursor, and path behavior compatibility.",
        "validation_focus": "File adapter contract tests",
    },
    "tpl-registry-adapter": {
        "title": "Registry adapter semantics patch",
        "default_priority": "P1",
        "default_risk": "medium",
        "strategy": "Improve registry key/value operation compatibility.",
        "validation_focus": "Registry adapter contract tests",
    },
    "tpl-api-stub-contract": {
        "title": "API stub implementation patch",
        "default_priority": "P1",
        "default_risk": "medium",
        "strategy": "Upgrade stubbed APIs to behavior-compatible implementations.",
        "validation_focus": "Dispatcher API contract tests",
    },
    "tpl-runtime-investigate": {
        "title": "Generic runtime investigation patch",
        "default_priority": "P2",
        "default_risk": "medium",
        "strategy": "Investigate unsupported runtime path and design minimal safe patch.",
        "validation_focus": "Runtime smoke and focused reproduction",
    },
}


CATEGORY_TEMPLATE_MAP = {
    "loader": "tpl-loader-import",
    "com": "tpl-com-activation",
    "installer": "tpl-installer-bootstrap",
    "network": "tpl-network-winhttp",
    "sync": "tpl-sync-primitives",
    "file": "tpl-file-adapter",
    "registry": "tpl-registry-adapter",
    "unimplemented": "tpl-api-stub-contract",
}


def _proposal_index(patch_plan: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for proposal in patch_plan.get("proposals", []):
        gap_id = proposal.get("gap_id")
        if isinstance(gap_id, str):
            index[gap_id] = proposal
    return index


def _priority_distribution(gap_ids: list[str], proposal_by_gap: dict[str, dict]) -> dict[str, int]:
    dist = {"P0": 0, "P1": 0, "P2": 0, "other": 0}
    for gap_id in gap_ids:
        priority = str(proposal_by_gap.get(gap_id, {}).get("priority", "other"))
        if priority in dist:
            dist[priority] += 1
        else:
            dist["other"] += 1
    return dist


def _actions(*, unmapped_categories: list[str], used_templates: int) -> list[str]:
    actions = []
    if unmapped_categories:
        actions.append(
            "Define dedicated templates for unmapped categories: " + ", ".join(unmapped_categories)
        )
    if used_templates == 0:
        actions.append("No template usage detected. Verify gap and patch-plan generation inputs.")
    if not actions:
        actions.append("Template mapping is healthy. Continue maintaining template quality and tests.")
    return actions


def build_patch_template_catalog(
    *,
    gaps: dict,
    patch_plan: dict,
) -> dict:
    proposal_by_gap = _proposal_index(patch_plan)
    usage: dict[str, dict] = {}
    unmapped_categories: set[str] = set()

    for gap in gaps.get("gaps", []):
        gap_id = str(gap.get("id", "unknown"))
        category = str(gap.get("category", "runtime"))
        template_id = CATEGORY_TEMPLATE_MAP.get(category, "tpl-runtime-investigate")
        if category not in CATEGORY_TEMPLATE_MAP:
            unmapped_categories.add(category)

        if template_id not in usage:
            usage[template_id] = {
                "template_id": template_id,
                "gap_ids": [],
                "categories": set(),
            }
        usage_entry = usage[template_id]
        usage_entry["gap_ids"].append(gap_id)
        usage_entry["categories"].add(category)

    templates = []
    mapped_gaps = 0
    proposals_linked = 0
    for template_id, meta in TEMPLATE_LIBRARY.items():
        gap_ids = usage.get(template_id, {}).get("gap_ids", [])
        categories = sorted(list(usage.get(template_id, {}).get("categories", set())))
        priority_dist = _priority_distribution(gap_ids, proposal_by_gap)
        proposals_for_template = sum(priority_dist.values()) - priority_dist["other"]
        proposals_linked += proposals_for_template
        mapped_gaps += len(gap_ids)

        templates.append(
            {
                "id": template_id,
                "title": meta["title"],
                "default_priority": meta["default_priority"],
                "default_risk": meta["default_risk"],
                "strategy": meta["strategy"],
                "validation_focus": meta["validation_focus"],
                "usage": {
                    "gap_count": len(gap_ids),
                    "categories": categories,
                    "priority_distribution": priority_dist,
                    "example_gap_ids": gap_ids[:5],
                },
            }
        )

    used_templates = sum(1 for t in templates if t["usage"]["gap_count"] > 0)
    total_gaps = len(gaps.get("gaps", []))

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "templates_total": len(templates),
            "used_templates": used_templates,
            "mapped_gaps": mapped_gaps,
            "unmapped_gaps": max(total_gaps - mapped_gaps, 0),
            "proposals_linked": proposals_linked,
        },
        "unmapped_categories": sorted(unmapped_categories),
        "templates": templates,
        "actions": _actions(
            unmapped_categories=sorted(unmapped_categories),
            used_templates=used_templates,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build patch template catalog artifact")
    parser.add_argument("--gaps", required=True, help="Gaps JSON path")
    parser.add_argument("--patch-plan", required=True, help="Patch plan JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    gaps = read_json(args.gaps)
    patch_plan = read_json(args.patch_plan)
    artifact = build_patch_template_catalog(gaps=gaps, patch_plan=patch_plan)
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()

