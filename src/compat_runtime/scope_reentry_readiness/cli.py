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


def build_scope_reentry_readiness_report(
    *, scope_admission_gate_report: dict, transition_readiness_index_report: dict, risk_watchlist_report: dict
) -> dict:
    admission = scope_admission_gate_report.get("summary", {})
    readiness = transition_readiness_index_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    gate = str(admission.get("scope_admission_gate", "closed"))
    transition_score = int(readiness.get("transition_readiness_score", 0))
    p0_count = int(risks.get("p0_entries", 0))

    gate_base = {"closed": 20, "guarded": 52, "open": 78}.get(gate, 20)
    p0_penalty = min(30, p0_count * 7)

    score = max(0, min(100, gate_base + (transition_score // 3) - p0_penalty))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_reentry_readiness_score": score,
            "scope_reentry_readiness_band": band,
            "scope_admission_gate": gate,
            "transition_readiness_score": transition_score,
            "p0_entries": p0_count,
        },
        "actions": [
            "Maintenir la reentree scope bloquee tant que la readiness reste en mode bloque."
            if band == "blocked"
            else "Reevaluer la readiness de reentree scope a chaque cycle de triage."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope reentry readiness report")
    p.add_argument("--scope-admission-gate-report", required=True)
    p.add_argument("--transition-readiness-index-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_reentry_readiness_report(
        scope_admission_gate_report=read_json(a.scope_admission_gate_report),
        transition_readiness_index_report=read_json(a.transition_readiness_index_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
