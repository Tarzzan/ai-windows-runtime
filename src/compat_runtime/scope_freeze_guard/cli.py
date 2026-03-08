from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _guard(slot_policy: str, scope_lock_state: str, p0_entries: int) -> str:
    if slot_policy == "minimal" or scope_lock_state == "locked" or p0_entries >= 3:
        return "freeze"
    if slot_policy == "moderate" or scope_lock_state == "controlled" or p0_entries >= 1:
        return "guarded"
    return "open"


def build_scope_freeze_guard_report(
    *, intake_slot_policy_report: dict, scope_lock_state_report: dict, risk_watchlist_report: dict
) -> dict:
    slots = intake_slot_policy_report.get("summary", {})
    lock = scope_lock_state_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    slot_policy = str(slots.get("intake_slot_policy", "minimal"))
    lock_state = str(lock.get("scope_lock_state", "locked"))
    p0_entries = int(risks.get("p0_entries", 0))

    freeze_guard = _guard(slot_policy, lock_state, p0_entries)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_freeze_guard": freeze_guard,
            "intake_slot_policy": slot_policy,
            "scope_lock_state": lock_state,
            "p0_entries": p0_entries,
        },
        "actions": [
            "Maintenir un garde de gel du scope tant que la pression P0 reste elevee."
            if freeze_guard == "freeze"
            else "Revoir le garde de gel du scope avant chaque ajustement de perimetre."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope freeze guard report")
    p.add_argument("--intake-slot-policy-report", required=True)
    p.add_argument("--scope-lock-state-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_freeze_guard_report(
        intake_slot_policy_report=read_json(a.intake_slot_policy_report),
        scope_lock_state_report=read_json(a.scope_lock_state_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
