from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _policy(expansion_band: str, resumption_policy: str, bandwidth_mode: str) -> str:
    if expansion_band == "blocked" or resumption_policy == "hold" or bandwidth_mode == "constrained":
        return "hold"
    if expansion_band == "watch" or resumption_policy == "stage" or bandwidth_mode == "balanced":
        return "stage"
    return "expand"


def build_intake_expansion_policy_report(
    *, scope_expansion_readiness_report: dict, intake_resumption_policy_report: dict, delivery_bandwidth_report: dict
) -> dict:
    expansion = scope_expansion_readiness_report.get("summary", {})
    resumption = intake_resumption_policy_report.get("summary", {})
    bandwidth = delivery_bandwidth_report.get("summary", {})

    expansion_band = str(expansion.get("scope_expansion_readiness_band", "blocked"))
    resumption_policy = str(resumption.get("intake_resumption_policy", "hold"))
    bandwidth_mode = str(bandwidth.get("bandwidth_mode", "constrained"))

    policy = _policy(expansion_band, resumption_policy, bandwidth_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_expansion_policy": policy,
            "scope_expansion_readiness_band": expansion_band,
            "intake_resumption_policy": resumption_policy,
            "bandwidth_mode": bandwidth_mode,
        },
        "actions": [
            "Maintenir l'expansion intake en hold tant que la readiness d'expansion reste bloquee."
            if policy == "hold"
            else "Ajuster la politique d'expansion intake selon readiness et bande passante delivery."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake expansion policy report")
    p.add_argument("--scope-expansion-readiness-report", required=True)
    p.add_argument("--intake-resumption-policy-report", required=True)
    p.add_argument("--delivery-bandwidth-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_expansion_policy_report(
        scope_expansion_readiness_report=read_json(a.scope_expansion_readiness_report),
        intake_resumption_policy_report=read_json(a.intake_resumption_policy_report),
        delivery_bandwidth_report=read_json(a.delivery_bandwidth_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
