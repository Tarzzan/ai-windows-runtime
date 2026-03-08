from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json
from compat_runtime.common.policy import load_alpha_gating_policy


def _grade(has_fail: bool, has_warn: bool) -> str:
    if has_fail:
        return "fail"
    if has_warn:
        return "warn"
    return "pass"


def _item(item_id: str, title: str, required: bool, status: str, evidence: str, detail: str) -> dict:
    return {
        "id": item_id,
        "title": title,
        "required": required,
        "status": status,
        "evidence": evidence,
        "detail": detail,
    }


def _actions(grade: str) -> list[str]:
    if grade == "fail":
        return [
            "Block release and resolve all required failing checks.",
            "Re-run scripts/run-full-pipeline.sh out after corrective changes.",
        ]
    if grade == "warn":
        return [
            "Proceed only with explicit reviewer sign-off for warning checks.",
            "Track warning items in the next compatibility iteration.",
        ]
    return ["Quality gate is green. Proceed with release packaging and pilot validation."]


def build_quality_gate_report(
    *,
    execution_report: dict,
    kpi_report: dict,
    trend_report: dict,
    proposal_risk_report: dict,
    crash_signature_report: dict,
    installer_phase_report: dict,
    proposal_review_checklist: dict,
    productization_readiness: dict,
    office_readiness_report: dict | None = None,
) -> dict:
    policy = load_alpha_gating_policy().get("quality_gate", {})
    kpi_high_without_failed_runs_pass = bool(
        policy.get("kpi_high_without_failed_runs_pass", True)
    )
    trend_warn_threshold = int(policy.get("trend_regression_warn_threshold", 4))
    proposal_high_risk_warn_threshold = int(policy.get("proposal_high_risk_warn_threshold", 3))
    installer_error_warn_threshold = int(policy.get("installer_error_warn_threshold", 5))
    office_limited_as_pass = bool(policy.get("office_limited_as_pass", True))

    items = []

    execution_ok = execution_report.get("status") == "ok"
    items.append(
        _item(
            "execution_pipeline",
            "Execution pipeline status",
            True,
            "pass" if execution_ok else "fail",
            "out/execution-report.json",
            f"status={execution_report.get('status', 'unknown')}",
        )
    )

    kpi_summary = kpi_report.get("summary", {})
    kpi_risk = str(kpi_summary.get("risk_level", "unknown"))
    kpi_failed_runs = int(kpi_summary.get("failed_runs", 0))
    if kpi_risk in {"low", "medium"}:
        kpi_status = "pass"
    elif kpi_risk == "high" and kpi_failed_runs == 0 and kpi_high_without_failed_runs_pass:
        kpi_status = "pass"
    else:
        kpi_status = "fail"
    items.append(
        _item(
            "kpi_risk_level",
            "KPI risk level acceptable",
            True,
            kpi_status,
            "out/kpi-report.json",
            f"risk_level={kpi_risk},failed_runs={kpi_failed_runs}",
        )
    )

    regressed = len(trend_report.get("summary", {}).get("regressed_metrics", []))
    trend_status = "warn" if regressed > trend_warn_threshold else "pass"
    items.append(
        _item(
            "trend_regressions",
            "Trend regressions reviewed",
            False,
            trend_status,
            "out/trend-report.json",
            f"regressed_metrics={regressed}",
        )
    )

    high_risk = int(proposal_risk_report.get("summary", {}).get("high_risk", 0))
    proposal_risk_status = "warn" if high_risk > proposal_high_risk_warn_threshold else "pass"
    items.append(
        _item(
            "proposal_risk_high",
            "High-risk proposals controlled",
            False,
            proposal_risk_status,
            "out/proposal-risk-report.json",
            f"high_risk={high_risk}",
        )
    )

    crash_p0 = int(crash_signature_report.get("summary", {}).get("high_priority_signatures", 0))
    crash_status = "fail" if crash_p0 > 0 else "pass"
    items.append(
        _item(
            "crash_signatures",
            "No high-priority crash signatures",
            True,
            crash_status,
            "out/crash-signature-report.json",
            f"high_priority_signatures={crash_p0}",
        )
    )

    installer_errors = int(installer_phase_report.get("summary", {}).get("error_events", 0))
    installer_status = "warn" if installer_errors > installer_error_warn_threshold else "pass"
    items.append(
        _item(
            "installer_phases",
            "Installer phase errors under control",
            False,
            installer_status,
            "out/installer-phase-report.json",
            f"error_events={installer_errors}",
        )
    )

    review_ready = bool(proposal_review_checklist.get("ready_for_approval", False))
    review_status = "pass" if review_ready else "fail"
    items.append(
        _item(
            "proposal_review_gate",
            "Proposal review checklist approved",
            True,
            review_status,
            "out/proposal-review-checklist.json",
            f"ready_for_approval={review_ready}",
        )
    )

    productization_ready = bool(productization_readiness.get("ready", False))
    product_status = "pass" if productization_ready else "fail"
    items.append(
        _item(
            "productization_gate",
            "Productization readiness passed",
            True,
            product_status,
            "out/productization-readiness.json",
            f"ready={productization_ready}",
        )
    )

    office_status = str((office_readiness_report or {}).get("status", "not_provided"))
    if office_status == "ready":
        office_gate_status = "pass"
    elif office_status == "limited":
        office_gate_status = "pass" if office_limited_as_pass else "warn"
    elif office_status == "blocked":
        office_gate_status = "fail"
    else:
        office_gate_status = "pass"

    items.append(
        _item(
            "office_readiness",
            "Office runtime readiness",
            False,
            office_gate_status,
            "out/office-readiness-report.json",
            f"status={office_status}",
        )
    )

    required_failures = sum(
        1 for item in items if item["required"] and item["status"] == "fail"
    )
    warn_count = sum(1 for item in items if item["status"] == "warn")
    fail_count = sum(1 for item in items if item["status"] == "fail")
    pass_count = sum(1 for item in items if item["status"] == "pass")
    gate = _grade(has_fail=fail_count > 0, has_warn=warn_count > 0)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gate": gate,
        "ready_for_release": required_failures == 0 and gate == "pass",
        "summary": {
            "total_items": len(items),
            "pass_items": pass_count,
            "warn_items": warn_count,
            "fail_items": fail_count,
            "required_failures": required_failures,
        },
        "checks": items,
        "actions": _actions(gate),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build quality gate report")
    parser.add_argument("--execution-report", required=True, help="Execution report path")
    parser.add_argument("--kpi-report", required=True, help="KPI report path")
    parser.add_argument("--trend-report", required=True, help="Trend report path")
    parser.add_argument("--proposal-risk-report", required=True, help="Proposal risk report path")
    parser.add_argument("--crash-signature-report", required=True, help="Crash signature report path")
    parser.add_argument("--installer-phase-report", required=True, help="Installer phase report path")
    parser.add_argument(
        "--proposal-review-checklist", required=True, help="Proposal review checklist path"
    )
    parser.add_argument(
        "--productization-readiness", required=True, help="Productization readiness report path"
    )
    parser.add_argument(
        "--office-readiness-report",
        required=False,
        help="Office readiness report path (optional)",
    )
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    report = build_quality_gate_report(
        execution_report=read_json(args.execution_report),
        kpi_report=read_json(args.kpi_report),
        trend_report=read_json(args.trend_report),
        proposal_risk_report=read_json(args.proposal_risk_report),
        crash_signature_report=read_json(args.crash_signature_report),
        installer_phase_report=read_json(args.installer_phase_report),
        proposal_review_checklist=read_json(args.proposal_review_checklist),
        productization_readiness=read_json(args.productization_readiness),
        office_readiness_report=(
            read_json(args.office_readiness_report) if args.office_readiness_report else None
        ),
    )
    write_json(args.output, report)


if __name__ == "__main__":
    main()
