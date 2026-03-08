from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 70:
        return "ready"
    if score >= 40:
        return "watch"
    return "blocked"


def build_scope_expansion_readiness_report(
    *, scope_unlock_gate_report: dict, scope_reentry_readiness_report: dict, risk_watchlist_report: dict
) -> dict:
    unlock = scope_unlock_gate_report.get("summary", {})
    reentry = scope_reentry_readiness_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    unlock_gate = str(unlock.get("scope_unlock_gate", "locked"))
    reentry_score = int(reentry.get("scope_reentry_readiness_score", 0))
    p0_count = int(risks.get("p0_entries", 0))

    unlock_base = {"locked": 18, "guarded": 50, "unlocked": 80}.get(unlock_gate, 18)
    p0_penalty = min(30, p0_count * 7)

    score = max(0, min(100, unlock_base + (reentry_score // 3) - p0_penalty))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_expansion_readiness_score": score,
            "scope_expansion_readiness_band": band,
            "scope_unlock_gate": unlock_gate,
            "scope_reentry_readiness_score": reentry_score,
            "p0_entries": p0_count,
        },
        "actions": [
            "Maintenir l'expansion scope bloquee tant que la readiness reste en mode bloque."
            if band == "blocked"
            else "Reevaluer la readiness d'expansion scope a chaque cycle de triage."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope expansion readiness report")
    p.add_argument("--scope-unlock-gate-report", required=True)
    p.add_argument("--scope-reentry-readiness-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_expansion_readiness_report(
        scope_unlock_gate_report=read_json(a.scope_unlock_gate_report),
        scope_reentry_readiness_report=read_json(a.scope_reentry_readiness_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
