from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json
from compat_runtime.common.policy import load_alpha_gating_policy


def _warning_budget() -> int:
    policy = load_alpha_gating_policy().get("release_decision", {})
    return int(policy.get("warning_budget", 2))


def _check(
    item_id: str,
    title: str,
    *,
    required: bool,
    status: str,
    evidence: str,
    detail: str,
) -> dict:
    return {
        "id": item_id,
        "title": title,
        "required": required,
        "status": status,
        "evidence": evidence,
        "detail": detail,
    }


def _decision(*, blockers: int, warnings: int, warning_budget: int) -> str:
    if blockers > 0:
        return "no-go"
    if warnings > warning_budget:
        return "hold"
    return "go"


def _actions(decision: str) -> list[str]:
    if decision == "no-go":
        return [
            "Block release and resolve blocking checks before packaging.",
            "Re-run scripts/run-full-pipeline.sh out and scripts/build-release-decision-report.sh out.",
        ]
    if decision == "hold":
        return [
            "Collect explicit reviewer sign-off for warning checks before promotion.",
            "Document mitigation owner and target date in release notes.",
        ]
    return ["Decision is GO. Proceed with release packaging and pilot rollout."]


def _warn_count_from_checklist(alpha_release_checklist: dict) -> int:
    summary = alpha_release_checklist.get("summary", {})
    val = summary.get("warn_items", 0)
    return int(val) if isinstance(val, int) else 0


def _warn_count_from_gate(quality_gate_report: dict) -> int:
    summary = quality_gate_report.get("summary", {})
    val = summary.get("warn_items", 0)
    return int(val) if isinstance(val, int) else 0


def build_release_decision_report(
    *,
    quality_gate_report: dict,
    alpha_release_checklist: dict,
    compatibility_matrix: dict,
    productization_readiness: dict,
    office_readiness_report: dict | None = None,
) -> dict:
    warning_budget = _warning_budget()
    checks = []

    gate = str(quality_gate_report.get("gate", "fail"))
    gate_status = "pass" if gate == "pass" else ("warn" if gate == "warn" else "fail")
    checks.append(
        _check(
            "quality_gate",
            "Quality gate status",
            required=True,
            status=gate_status,
            evidence="out/quality-gate-report.json",
            detail=f"gate={gate}",
        )
    )

    checklist_ready = bool(alpha_release_checklist.get("release_ready", False))
    checks.append(
        _check(
            "alpha_checklist",
            "Alpha release checklist readiness",
            required=True,
            status="pass" if checklist_ready else "fail",
            evidence="out/alpha-release-checklist.json",
            detail=f"release_ready={checklist_ready}",
        )
    )

    matrix_ready = bool(compatibility_matrix.get("release_ready", False))
    checks.append(
        _check(
            "compatibility_matrix",
            "Compatibility matrix readiness",
            required=True,
            status="pass" if matrix_ready else "fail",
            evidence="out/compatibility-matrix.json",
            detail=f"release_ready={matrix_ready}",
        )
    )

    product_ready = bool(productization_readiness.get("ready", False))
    checks.append(
        _check(
            "productization_readiness",
            "Productization readiness",
            required=True,
            status="pass" if product_ready else "fail",
            evidence="out/productization-readiness.json",
            detail=f"ready={product_ready}",
        )
    )

    office_status = str((office_readiness_report or {}).get("status", "not_provided"))
    office_required = office_status == "blocked"
    if office_status == "ready":
        office_gate_status = "pass"
    elif office_status == "limited":
        office_gate_status = "warn"
    elif office_status == "blocked":
        office_gate_status = "fail"
    else:
        office_gate_status = "pass"

    checks.append(
        _check(
            "office_readiness",
            "Office runtime readiness",
            required=office_required,
            status=office_gate_status,
            evidence="out/office-readiness-report.json",
            detail=f"status={office_status}",
        )
    )

    warnings = _warn_count_from_gate(quality_gate_report) + _warn_count_from_checklist(
        alpha_release_checklist
    )
    if office_gate_status == "warn":
        warnings += 1
    checks.append(
        _check(
            "warning_budget",
            "Warning budget observed",
            required=False,
            status="warn" if warnings > warning_budget else "pass",
            evidence="out/quality-gate-report.json + out/alpha-release-checklist.json",
            detail=f"budget_warnings={warnings}",
        )
    )

    blockers = sum(1 for item in checks if item["required"] and item["status"] == "fail")
    decision = _decision(blockers=blockers, warnings=warnings, warning_budget=warning_budget)
    release_ready = decision == "go"
    pass_count = sum(1 for item in checks if item["status"] == "pass")
    warn_count = sum(1 for item in checks if item["status"] == "warn")
    fail_count = sum(1 for item in checks if item["status"] == "fail")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "release_ready": release_ready,
        "summary": {
            "total_checks": len(checks),
            "pass_checks": pass_count,
            "warn_checks": warn_count,
            "fail_checks": fail_count,
            "blocking_failures": blockers,
            "total_warnings": warn_count,
            "budget_warnings": warnings,
        },
        "checks": checks,
        "actions": _actions(decision),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release decision report")
    parser.add_argument("--quality-gate-report", required=True, help="Quality gate report path")
    parser.add_argument("--alpha-release-checklist", required=True, help="Alpha checklist path")
    parser.add_argument("--compatibility-matrix", required=True, help="Compatibility matrix path")
    parser.add_argument(
        "--productization-readiness", required=True, help="Productization readiness path"
    )
    parser.add_argument(
        "--office-readiness-report",
        required=False,
        help="Office readiness report path (optional)",
    )
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_release_decision_report(
        quality_gate_report=read_json(args.quality_gate_report),
        alpha_release_checklist=read_json(args.alpha_release_checklist),
        compatibility_matrix=read_json(args.compatibility_matrix),
        productization_readiness=read_json(args.productization_readiness),
        office_readiness_report=(
            read_json(args.office_readiness_report) if args.office_readiness_report else None
        ),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
