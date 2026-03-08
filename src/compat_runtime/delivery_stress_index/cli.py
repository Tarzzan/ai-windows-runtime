from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def build_delivery_stress_index_report(
    *, scope_freeze_guard_report: dict, throughput_guard_band_report: dict, risk_watchlist_report: dict
) -> dict:
    freeze = scope_freeze_guard_report.get("summary", {})
    throughput = throughput_guard_band_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    freeze_mode = str(freeze.get("scope_freeze_guard", "freeze"))
    throughput_score = int(throughput.get("throughput_guard_score", 0))
    p0_entries = int(risks.get("p0_entries", 0))

    freeze_base = {"freeze": 78, "guarded": 52, "open": 24}.get(freeze_mode, 78)
    p0_pressure = min(30, p0_entries * 7)
    score = max(0, min(100, freeze_base + p0_pressure - (throughput_score // 4)))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "delivery_stress_score": score,
            "delivery_stress_band": band,
            "scope_freeze_guard": freeze_mode,
            "throughput_guard_score": throughput_score,
            "p0_entries": p0_entries,
        },
        "actions": [
            "Reduire la charge delivery tant que l'indice de stress reste eleve."
            if band == "high"
            else "Surveiller l'indice de stress delivery avant chaque arbitrage de scope."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build delivery stress index report")
    p.add_argument("--scope-freeze-guard-report", required=True)
    p.add_argument("--throughput-guard-band-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_delivery_stress_index_report(
        scope_freeze_guard_report=read_json(a.scope_freeze_guard_report),
        throughput_guard_band_report=read_json(a.throughput_guard_band_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
