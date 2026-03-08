from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _state(commitment_window: str, scope_rebalance: str, p0_entries: int) -> str:
    if commitment_window == "locked" or scope_rebalance == "reduce" or p0_entries >= 3:
        return "locked"
    if commitment_window == "managed" or scope_rebalance == "hold" or p0_entries >= 1:
        return "controlled"
    return "flexible"


def build_scope_lock_state_report(
    *, intake_commitment_window_report: dict, scope_rebalance_report: dict, risk_watchlist_report: dict
) -> dict:
    commitment = intake_commitment_window_report.get("summary", {})
    rebalance = scope_rebalance_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    commitment_window = str(commitment.get("intake_commitment_window", "locked"))
    scope_state = str(rebalance.get("scope_rebalance", "reduce"))
    p0_entries = int(risks.get("p0_entries", 0))

    lock_state = _state(commitment_window, scope_state, p0_entries)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_lock_state": lock_state,
            "intake_commitment_window": commitment_window,
            "scope_rebalance": scope_state,
            "p0_entries": p0_entries,
        },
        "actions": [
            "Maintain locked scope while P0 pressure and commitment lock remain active."
            if lock_state == "locked"
            else "Reassess scope lock state before expanding active scope."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope lock state report")
    p.add_argument("--intake-commitment-window-report", required=True)
    p.add_argument("--scope-rebalance-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_lock_state_report(
        intake_commitment_window_report=read_json(a.intake_commitment_window_report),
        scope_rebalance_report=read_json(a.scope_rebalance_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
