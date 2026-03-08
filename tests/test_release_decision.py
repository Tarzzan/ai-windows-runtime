from compat_runtime.release_decision.cli import build_release_decision_report


def _quality(gate: str, warn_items: int) -> dict:
    return {"gate": gate, "summary": {"warn_items": warn_items}}


def _checklist(release_ready: bool, warn_items: int) -> dict:
    return {"release_ready": release_ready, "summary": {"warn_items": warn_items}}


def _matrix(release_ready: bool) -> dict:
    return {"release_ready": release_ready}


def _productization(ready: bool) -> dict:
    return {"ready": ready}


def _office(status: str) -> dict:
    return {"status": status}


def test_release_decision_no_go_on_blocking_failure():
    report = build_release_decision_report(
        quality_gate_report=_quality("fail", 2),
        alpha_release_checklist=_checklist(False, 1),
        compatibility_matrix=_matrix(False),
        productization_readiness=_productization(True),
    )

    assert report["decision"] == "no-go"
    assert report["release_ready"] is False
    assert report["summary"]["blocking_failures"] >= 1
    assert report["actions"]


def test_release_decision_hold_on_warnings_only():
    report = build_release_decision_report(
        quality_gate_report=_quality("warn", 2),
        alpha_release_checklist=_checklist(True, 1),
        compatibility_matrix=_matrix(True),
        productization_readiness=_productization(True),
    )

    assert report["decision"] == "hold"
    assert report["release_ready"] is False
    assert report["summary"]["blocking_failures"] == 0
    assert report["summary"]["total_warnings"] == 2
    assert report["summary"]["budget_warnings"] == 3
    budget_check = next(check for check in report["checks"] if check["id"] == "warning_budget")
    assert budget_check["status"] == "warn"
    assert budget_check["detail"] == "budget_warnings=3"


def test_release_decision_go_when_green():
    report = build_release_decision_report(
        quality_gate_report=_quality("pass", 0),
        alpha_release_checklist=_checklist(True, 0),
        compatibility_matrix=_matrix(True),
        productization_readiness=_productization(True),
    )

    assert report["decision"] == "go"
    assert report["release_ready"] is True
    assert report["summary"]["blocking_failures"] == 0
    assert report["summary"]["warn_checks"] == 0


def test_release_decision_no_go_when_office_is_blocked():
    report = build_release_decision_report(
        quality_gate_report=_quality("pass", 0),
        alpha_release_checklist=_checklist(True, 0),
        compatibility_matrix=_matrix(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("blocked"),
    )

    office_check = next(check for check in report["checks"] if check["id"] == "office_readiness")
    assert office_check["required"] is True
    assert office_check["status"] == "fail"
    assert report["decision"] == "no-go"


def test_release_decision_go_when_only_office_is_limited():
    report = build_release_decision_report(
        quality_gate_report=_quality("pass", 0),
        alpha_release_checklist=_checklist(True, 0),
        compatibility_matrix=_matrix(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("limited"),
    )

    office_check = next(check for check in report["checks"] if check["id"] == "office_readiness")
    assert office_check["required"] is False
    assert office_check["status"] == "warn"
    assert report["decision"] == "go"


def test_release_decision_go_when_warning_budget_not_exceeded():
    report = build_release_decision_report(
        quality_gate_report=_quality("warn", 1),
        alpha_release_checklist=_checklist(True, 0),
        compatibility_matrix=_matrix(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("limited"),
    )

    assert report["summary"]["blocking_failures"] == 0
    assert report["summary"]["total_warnings"] == 2
    assert report["summary"]["budget_warnings"] == 2
    budget_check = next(check for check in report["checks"] if check["id"] == "warning_budget")
    assert budget_check["status"] == "pass"
    assert budget_check["detail"] == "budget_warnings=2"
    assert report["decision"] == "go"


def test_release_decision_summary_warning_count_matches_warn_checks():
    report = build_release_decision_report(
        quality_gate_report=_quality("warn", 1),
        alpha_release_checklist=_checklist(True, 0),
        compatibility_matrix=_matrix(True),
        productization_readiness=_productization(True),
        office_readiness_report=_office("limited"),
    )

    assert report["summary"]["total_warnings"] == report["summary"]["warn_checks"]
