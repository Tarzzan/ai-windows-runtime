from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _reserve(sync_state: str, scope_budget_mode: str, overloaded_owners: int) -> str:
    if sync_state == "blocked" or scope_budget_mode == "tight" or overloaded_owners >= 1:
        return "protected"
    if sync_state == "aligned" or scope_budget_mode == "balanced":
        return "managed"
    return "surplus"


def build_execution_reserve_report(
    *, delivery_intake_sync_report: dict, scope_budget_report: dict, owner_load_report: dict
) -> dict:
    sync = delivery_intake_sync_report.get("summary", {})
    scope = scope_budget_report.get("summary", {})
    owners = owner_load_report.get("summary", {})

    sync_state = str(sync.get("delivery_intake_sync", "blocked"))
    scope_mode = str(scope.get("scope_budget_mode", "tight"))
    overloaded_owners = int(owners.get("overloaded_owners", 0))

    reserve_mode = _reserve(sync_state, scope_mode, overloaded_owners)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "execution_reserve": reserve_mode,
            "delivery_intake_sync": sync_state,
            "scope_budget_mode": scope_mode,
            "overloaded_owners": overloaded_owners,
        },
        "actions": [
            "Protect execution reserve while sync is blocked or owner overload persists."
            if reserve_mode == "protected"
            else "Track execution reserve posture as scope and intake evolve."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build execution reserve report")
    p.add_argument("--delivery-intake-sync-report", required=True)
    p.add_argument("--scope-budget-report", required=True)
    p.add_argument("--owner-load-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_execution_reserve_report(
        delivery_intake_sync_report=read_json(a.delivery_intake_sync_report),
        scope_budget_report=read_json(a.scope_budget_report),
        owner_load_report=read_json(a.owner_load_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
