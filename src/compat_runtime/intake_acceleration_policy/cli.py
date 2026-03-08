from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _policy(accel_band: str, expansion_policy: str, bandwidth_mode: str) -> str:
    if accel_band == "blocked" or expansion_policy == "hold" or bandwidth_mode == "constrained":
        return "hold"
    if accel_band == "watch" or expansion_policy == "stage" or bandwidth_mode == "balanced":
        return "stage"
    return "accelerate"


def build_intake_acceleration_policy_report(
    *, scope_acceleration_readiness_report: dict, intake_expansion_policy_report: dict, delivery_bandwidth_report: dict
) -> dict:
    accel = scope_acceleration_readiness_report.get("summary", {})
    expansion = intake_expansion_policy_report.get("summary", {})
    bandwidth = delivery_bandwidth_report.get("summary", {})

    accel_band = str(accel.get("scope_acceleration_readiness_band", "blocked"))
    expansion_policy = str(expansion.get("intake_expansion_policy", "hold"))
    bandwidth_mode = str(bandwidth.get("bandwidth_mode", "constrained"))

    policy = _policy(accel_band, expansion_policy, bandwidth_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_acceleration_policy": policy,
            "scope_acceleration_readiness_band": accel_band,
            "intake_expansion_policy": expansion_policy,
            "bandwidth_mode": bandwidth_mode,
        },
        "actions": [
            "Maintenir l'acceleration intake en hold tant que la readiness d'acceleration reste bloquee."
            if policy == "hold"
            else "Ajuster la politique d'acceleration intake selon readiness et bande passante delivery."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake acceleration policy report")
    p.add_argument("--scope-acceleration-readiness-report", required=True)
    p.add_argument("--intake-expansion-policy-report", required=True)
    p.add_argument("--delivery-bandwidth-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_acceleration_policy_report(
        scope_acceleration_readiness_report=read_json(a.scope_acceleration_readiness_report),
        intake_expansion_policy_report=read_json(a.intake_expansion_policy_report),
        delivery_bandwidth_report=read_json(a.delivery_bandwidth_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
