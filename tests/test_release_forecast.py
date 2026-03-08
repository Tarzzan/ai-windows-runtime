from compat_runtime.release_forecast.cli import build_release_forecast_report


def _iteration(total: int, blocking: int, p0: int, hours: int, tasks: list[dict]) -> dict:
    return {
        "summary": {
            "total_tasks": total,
            "blocking_tasks": blocking,
            "p0_tasks": p0,
            "estimated_total_hours": hours,
        },
        "tasks": tasks,
    }


def _release(decision: str) -> dict:
    return {"decision": decision}


def _kpi(risk_level: str) -> dict:
    return {"summary": {"risk_level": risk_level}}


def _trend(improved: list[str], regressed: list[str]) -> dict:
    return {"summary": {"improved_metrics": improved, "regressed_metrics": regressed}}


def test_release_forecast_increases_iterations_on_high_risk_regression():
    report = build_release_forecast_report(
        iteration_plan_report=_iteration(
            total=8,
            blocking=6,
            p0=6,
            hours=64,
            tasks=[
                {"id": "t1", "priority": "P0", "blocking": True, "objective": "o1", "suggested_command": "cmd1"},
                {"id": "t2", "priority": "P0", "blocking": True, "objective": "o2", "suggested_command": "cmd2"},
            ],
        ),
        release_decision_report=_release("no-go"),
        kpi_report=_kpi("high"),
        trend_report=_trend(["a"], ["b", "c", "d"]),
        release_policy_report={"status": "fail", "failures": ["x"]},
    )

    assert report["summary"]["decision_context"] == "no-go"
    assert report["summary"]["estimated_iterations_to_go"] >= 2
    assert report["summary"]["release_policy_status"] == "fail"
    assert report["summary"]["release_policy_failures"] == 1
    assert report["summary"]["forecast_wave"] in {"near_term", "long_term"}
    assert report["top_tasks"]
    assert report["actions"]


def test_release_forecast_handles_low_risk_stable_case():
    report = build_release_forecast_report(
        iteration_plan_report=_iteration(total=2, blocking=0, p0=0, hours=8, tasks=[]),
        release_decision_report=_release("go"),
        kpi_report=_kpi("low"),
        trend_report=_trend(["a", "b"], []),
    )

    assert report["summary"]["estimated_iterations_to_go"] == 1
    assert report["summary"]["release_policy_status"] == "missing"
    assert report["summary"]["forecast_wave"] == "immediate"
