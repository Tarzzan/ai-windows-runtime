from compat_runtime.quality_gate.cli import build_quality_gate_report


def _execution(status: str) -> dict:
    return {"status": status}


def _kpi(level: str, failed_runs: int = 0) -> dict:
    return {"summary": {"risk_level": level, "failed_runs": failed_runs}}


def _trend(regressed: list[str]) -> dict:
    return {"summary": {"regressed_metrics": regressed}}


def _proposal_risk(high: int) -> dict:
    return {"summary": {"high_risk": high}}


def _crash(p0: int) -> dict:
    return {"summary": {"high_priority_signatures": p0}}


def _installer(errors: int) -> dict:
    return {"summary": {"error_events": errors}}


def _review(ready: bool) -> dict:
    return {"ready_for_approval": ready}


def _productization(ready: bool) -> dict:
    return {"ready": ready}


def _office(status: str) -> dict:
    return {"status": status}


def test_quality_gate_fail_when_required_checks_fail():
    report = build_quality_gate_report(
        execution_report=_execution("failed"),
        kpi_report=_kpi("high", failed_runs=1),
        trend_report=_trend(["base_gaps"]),
        proposal_risk_report=_proposal_risk(2),
        crash_signature_report=_crash(1),
        installer_phase_report=_installer(3),
        proposal_review_checklist=_review(False),
        productization_readiness=_productization(False),
        office_readiness_report=_office("blocked"),
    )

    assert report["gate"] == "fail"
    assert report["ready_for_release"] is False
    assert report["summary"]["required_failures"] >= 1
    assert report["summary"]["fail_items"] >= 1
    assert report["actions"]


def test_quality_gate_pass_when_all_green():
    report = build_quality_gate_report(
        execution_report=_execution("ok"),
        kpi_report=_kpi("low"),
        trend_report=_trend([]),
        proposal_risk_report=_proposal_risk(0),
        crash_signature_report=_crash(0),
        installer_phase_report=_installer(0),
        proposal_review_checklist=_review(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("ready"),
    )

    assert report["gate"] == "pass"
    assert report["ready_for_release"] is True
    assert report["summary"]["required_failures"] == 0
    assert report["summary"]["warn_items"] == 0


def test_quality_gate_warn_when_only_optional_checks_degrade():
    report = build_quality_gate_report(
        execution_report=_execution("ok"),
        kpi_report=_kpi("medium"),
        trend_report=_trend(["m1", "m2", "m3", "m4", "m5"]),
        proposal_risk_report=_proposal_risk(4),
        crash_signature_report=_crash(0),
        installer_phase_report=_installer(6),
        proposal_review_checklist=_review(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("limited"),
    )

    assert report["gate"] == "warn"
    assert report["ready_for_release"] is False
    assert report["summary"]["required_failures"] == 0
    assert report["summary"]["warn_items"] >= 1


def test_quality_gate_pass_when_kpi_high_without_failed_runs():
    report = build_quality_gate_report(
        execution_report=_execution("ok"),
        kpi_report=_kpi("high", failed_runs=0),
        trend_report=_trend([]),
        proposal_risk_report=_proposal_risk(0),
        crash_signature_report=_crash(0),
        installer_phase_report=_installer(0),
        proposal_review_checklist=_review(True),
        productization_readiness=_productization(True),
    )

    kpi_check = next(check for check in report["checks"] if check["id"] == "kpi_risk_level")
    assert kpi_check["status"] == "pass"
    assert report["summary"]["required_failures"] == 0


def test_quality_gate_pass_when_office_readiness_is_not_provided():
    report = build_quality_gate_report(
        execution_report=_execution("ok"),
        kpi_report=_kpi("low"),
        trend_report=_trend([]),
        proposal_risk_report=_proposal_risk(0),
        crash_signature_report=_crash(0),
        installer_phase_report=_installer(0),
        proposal_review_checklist=_review(True),
        productization_readiness=_productization(True),
    )

    office_check = next(check for check in report["checks"] if check["id"] == "office_readiness")
    assert office_check["status"] == "pass"
    assert office_check["detail"] == "status=not_provided"


def test_quality_gate_pass_when_office_readiness_is_limited_for_alpha():
    report = build_quality_gate_report(
        execution_report=_execution("ok"),
        kpi_report=_kpi("low"),
        trend_report=_trend([]),
        proposal_risk_report=_proposal_risk(0),
        crash_signature_report=_crash(0),
        installer_phase_report=_installer(0),
        proposal_review_checklist=_review(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("limited"),
    )

    office_check = next(check for check in report["checks"] if check["id"] == "office_readiness")
    assert office_check["status"] == "pass"
    assert report["gate"] == "pass"


def test_quality_gate_fails_when_office_readiness_is_blocked():
    report = build_quality_gate_report(
        execution_report=_execution("ok"),
        kpi_report=_kpi("low"),
        trend_report=_trend([]),
        proposal_risk_report=_proposal_risk(0),
        crash_signature_report=_crash(0),
        installer_phase_report=_installer(0),
        proposal_review_checklist=_review(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("blocked"),
    )

    office_check = next(check for check in report["checks"] if check["id"] == "office_readiness")
    assert office_check["status"] == "fail"
    assert report["gate"] == "fail"
