from compat_runtime.quality_gate.cli import build_quality_gate_report


def _execution(status: str) -> dict:
    return {"status": status}


def _kpi(level: str) -> dict:
    return {"summary": {"risk_level": level}}


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


def test_quality_gate_fail_when_required_checks_fail():
    report = build_quality_gate_report(
        execution_report=_execution("failed"),
        kpi_report=_kpi("high"),
        trend_report=_trend(["base_gaps"]),
        proposal_risk_report=_proposal_risk(2),
        crash_signature_report=_crash(1),
        installer_phase_report=_installer(3),
        proposal_review_checklist=_review(False),
        productization_readiness=_productization(False),
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
    )

    assert report["gate"] == "pass"
    assert report["ready_for_release"] is True
    assert report["summary"]["required_failures"] == 0
    assert report["summary"]["warn_items"] == 0


def test_quality_gate_warn_when_only_optional_checks_degrade():
    report = build_quality_gate_report(
        execution_report=_execution("ok"),
        kpi_report=_kpi("medium"),
        trend_report=_trend(["runtime_gaps"]),
        proposal_risk_report=_proposal_risk(1),
        crash_signature_report=_crash(0),
        installer_phase_report=_installer(2),
        proposal_review_checklist=_review(True),
        productization_readiness=_productization(True),
    )

    assert report["gate"] == "warn"
    assert report["ready_for_release"] is False
    assert report["summary"]["required_failures"] == 0
    assert report["summary"]["warn_items"] >= 1
