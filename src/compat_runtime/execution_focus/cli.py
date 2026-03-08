from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _top_p0(entries: list[dict], limit: int = 5) -> list[dict]:
    p0 = [e for e in entries if str(e.get("priority", "P2")) == "P0"]
    return p0[:limit]


def _actions(cadence: str, p0_count: int) -> list[str]:
    actions = []
    if cadence == "slow":
        actions.append("Focus on blocker burn-down before adding new implementation scope.")
    elif cadence == "moderate":
        actions.append("Balance blocker reduction and planned delivery increments.")
    else:
        actions.append("Accelerate planned increments while guarding regression checks.")
    if p0_count > 0:
        actions.append("Keep explicit P0 owner review in every execution cycle.")
    return actions


def build_execution_focus_report(
    *,
    cadence_recommendation_report: dict,
    risk_watchlist_report: dict,
    ownership_assignment_report: dict,
) -> dict:
    cadence = str(cadence_recommendation_report.get("summary", {}).get("cadence", "slow"))
    watch_entries = list(risk_watchlist_report.get("entries", []))
    owners = list(ownership_assignment_report.get("owners", []))

    p0_entries = _top_p0(watch_entries)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "cadence": cadence,
            "p0_focus_items": len(p0_entries),
            "owners_in_scope": len(owners),
        },
        "focus_items": [
            {
                "id": str(e.get("id", "risk")),
                "priority": str(e.get("priority", "P2")),
                "detail": str(e.get("detail", "")),
            }
            for e in p0_entries
        ],
        "actions": _actions(cadence, len(p0_entries)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build execution focus report")
    parser.add_argument("--cadence-recommendation-report", required=True)
    parser.add_argument("--risk-watchlist-report", required=True)
    parser.add_argument("--ownership-assignment-report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    artifact = build_execution_focus_report(
        cadence_recommendation_report=read_json(args.cadence_recommendation_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
        ownership_assignment_report=read_json(args.ownership_assignment_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
