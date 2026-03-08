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


def build_scope_acceleration_readiness_report(
    *, scope_expansion_gate_report: dict, scope_expansion_readiness_report: dict, risk_watchlist_report: dict
) -> dict:
    expansion_gate = scope_expansion_gate_report.get("summary", {})
    expansion_readiness = scope_expansion_readiness_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    gate = str(expansion_gate.get("scope_expansion_gate", "closed"))
    readiness_score = int(expansion_readiness.get("scope_expansion_readiness_score", 0))
    p0_count = int(risks.get("p0_entries", 0))

    gate_base = {"closed": 20, "guarded": 52, "open": 80}.get(gate, 20)
    p0_penalty = min(30, p0_count * 7)

    score = max(0, min(100, gate_base + (readiness_score // 3) - p0_penalty))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_acceleration_readiness_score": score,
            "scope_acceleration_readiness_band": band,
            "scope_expansion_gate": gate,
            "scope_expansion_readiness_score": readiness_score,
            "p0_entries": p0_count,
        },
        "actions": [
            "Maintenir l'acceleration scope bloquee tant que la readiness reste en mode bloque."
            if band == "blocked"
            else "Reevaluer la readiness d'acceleration scope a chaque cycle de triage."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope acceleration readiness report")
    p.add_argument("--scope-expansion-gate-report", required=True)
    p.add_argument("--scope-expansion-readiness-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_acceleration_readiness_report(
        scope_expansion_gate_report=read_json(a.scope_expansion_gate_report),
        scope_expansion_readiness_report=read_json(a.scope_expansion_readiness_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
