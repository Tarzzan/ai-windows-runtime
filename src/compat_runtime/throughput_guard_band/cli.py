from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 70:
        return "wide"
    if score >= 40:
        return "balanced"
    return "tight"


def build_throughput_guard_band_report(
    *, scope_lock_state_report: dict, delivery_safety_margin_report: dict, execution_reserve_report: dict
) -> dict:
    lock_state = scope_lock_state_report.get("summary", {})
    safety = delivery_safety_margin_report.get("summary", {})
    reserve = execution_reserve_report.get("summary", {})

    lock_mode = str(lock_state.get("scope_lock_state", "locked"))
    safety_score = int(safety.get("safety_margin_score", 0))
    reserve_mode = str(reserve.get("execution_reserve", "protected"))

    lock_base = {"locked": 22, "controlled": 50, "flexible": 78}.get(lock_mode, 22)
    reserve_bonus = {"protected": -8, "managed": 4, "surplus": 12}.get(reserve_mode, -8)
    score = max(0, min(100, lock_base + reserve_bonus + (safety_score // 3)))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "throughput_guard_score": score,
            "throughput_guard_band": band,
            "scope_lock_state": lock_mode,
            "safety_margin_score": safety_score,
            "execution_reserve": reserve_mode,
        },
        "actions": [
            "Maintenir une bande de garde de debit stricte tant que le verrou de scope reste actif."
            if band == "tight"
            else "Re-evaluer la bande de garde de debit a chaque gate d'iteration."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build throughput guard band report")
    p.add_argument("--scope-lock-state-report", required=True)
    p.add_argument("--delivery-safety-margin-report", required=True)
    p.add_argument("--execution-reserve-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_throughput_guard_band_report(
        scope_lock_state_report=read_json(a.scope_lock_state_report),
        delivery_safety_margin_report=read_json(a.delivery_safety_margin_report),
        execution_reserve_report=read_json(a.execution_reserve_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
