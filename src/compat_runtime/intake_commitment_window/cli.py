from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _window(safety_band: str, release_window: str, commitment_guard: str) -> str:
    if safety_band == "narrow" or release_window == "closed" or commitment_guard == "strict":
        return "locked"
    if safety_band == "guarded" or release_window == "limited" or commitment_guard == "elevated":
        return "managed"
    return "open"


def build_intake_commitment_window_report(
    *, delivery_safety_margin_report: dict, intake_release_window_report: dict, execution_stability_guard_report: dict
) -> dict:
    safety = delivery_safety_margin_report.get("summary", {})
    release = intake_release_window_report.get("summary", {})
    stability = execution_stability_guard_report.get("summary", {})

    safety_band = str(safety.get("safety_margin_band", "narrow"))
    release_window = str(release.get("intake_release_window", "closed"))
    commitment_guard = str(stability.get("execution_stability_guard", "strict"))

    window = _window(safety_band, release_window, commitment_guard)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_commitment_window": window,
            "safety_margin_band": safety_band,
            "intake_release_window": release_window,
            "execution_stability_guard": commitment_guard,
        },
        "actions": [
            "Keep intake commitment window locked while stability guard remains strict."
            if window == "locked"
            else "Review commitment window posture at each planning checkpoint."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake commitment window report")
    p.add_argument("--delivery-safety-margin-report", required=True)
    p.add_argument("--intake-release-window-report", required=True)
    p.add_argument("--execution-stability-guard-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_commitment_window_report(
        delivery_safety_margin_report=read_json(a.delivery_safety_margin_report),
        intake_release_window_report=read_json(a.intake_release_window_report),
        execution_stability_guard_report=read_json(a.execution_stability_guard_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
