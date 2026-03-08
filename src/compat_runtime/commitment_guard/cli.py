from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _guard(window_state: str, p0_entries: int, policy_status: str) -> str:
    if policy_status != "pass" or window_state == "restricted" or p0_entries >= 3:
        return "strict"
    if window_state == "controlled" or p0_entries >= 1:
        return "moderate"
    return "adaptive"


def build_commitment_guard_report(
    *, admission_window_report: dict, risk_watchlist_report: dict, release_policy_report: dict
) -> dict:
    window = admission_window_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    window_state = str(window.get("admission_window", "restricted"))
    p0_entries = int(risks.get("p0_entries", 0))
    policy_status = str(release_policy_report.get("status", "missing"))

    guard_mode = _guard(window_state, p0_entries, policy_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "commitment_guard": guard_mode,
            "admission_window": window_state,
            "p0_entries": p0_entries,
            "policy_status": policy_status,
        },
        "actions": [
            "Enforce strict commitment guard until policy and P0 risk posture improve."
            if guard_mode == "strict"
            else "Maintain commitment guard discipline with watchlist reviews."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build commitment guard report")
    p.add_argument("--admission-window-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--release-policy-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_commitment_guard_report(
        admission_window_report=read_json(a.admission_window_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
        release_policy_report=read_json(a.release_policy_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
