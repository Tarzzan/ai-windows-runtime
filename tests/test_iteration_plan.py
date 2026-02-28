from compat_runtime.iteration_plan.cli import build_iteration_plan_report


def _release(decision: str, checks: list[dict]) -> dict:
    return {"decision": decision, "checks": checks}


def _hook_backlog(items: list[dict]) -> dict:
    return {"items": items}


def _risk(proposals: list[dict]) -> dict:
    return {"proposals": proposals}


def _impact(suites: list[dict]) -> dict:
    return {"suites": suites}


def test_iteration_plan_adds_blocking_and_hook_tasks():
    release = _release(
        "no-go",
        [
            {"id": "quality_gate", "title": "Quality gate status", "required": True, "status": "fail"},
            {"id": "warning_budget", "title": "Warning budget", "required": False, "status": "warn"},
        ],
    )
    backlog = _hook_backlog(
        [
            {
                "domain": "com",
                "missing_hook": True,
                "urgency": "P0",
                "errors": 2,
                "related_high_risk": 1,
                "recommended_hook": "com hook",
            },
            {"domain": "network", "missing_hook": True, "urgency": "P1", "errors": 0, "related_high_risk": 0},
        ]
    )
    risk = _risk(
        [
            {"gap_id": "g1", "risk_level": "high", "risk_score": 92},
            {"gap_id": "g2", "risk_level": "medium", "risk_score": 61},
        ]
    )
    impact = _impact(
        [
            {"trigger_proposals": ["g1"], "suggested_command": "pytest -q -k com", "trigger_categories": ["com"]},
            {"trigger_proposals": ["g2"], "suggested_command": "pytest -q -k network", "trigger_categories": ["network"]},
        ]
    )

    report = build_iteration_plan_report(
        release_decision_report=release,
        hook_backlog_report=backlog,
        proposal_risk_report=risk,
        test_impact_report=impact,
    )

    assert report["decision_context"] == "no-go"
    assert report["summary"]["blocking_tasks"] >= 2
    assert report["summary"]["p0_tasks"] >= 2
    assert report["tasks"]
    assert report["actions"]


def test_iteration_plan_handles_green_inputs():
    report = build_iteration_plan_report(
        release_decision_report=_release("go", []),
        hook_backlog_report=_hook_backlog([]),
        proposal_risk_report=_risk([]),
        test_impact_report=_impact([]),
    )

    assert report["summary"]["total_tasks"] == 0
    assert report["summary"]["blocking_tasks"] == 0
    assert report["summary"]["estimated_total_hours"] == 0
