from compat_runtime.root_cause.cli import build_root_cause_summary


def _gaps(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "gaps": items}


def _plans(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": items}


def test_root_cause_summary_clusters_categories_and_actions():
    base_gaps = _gaps(
        [
            {
                "id": "gap-loader-1",
                "category": "loader",
                "severity": "high",
                "summary": "Loader/import blocker",
            },
            {
                "id": "gap-network-1",
                "category": "network",
                "severity": "medium",
                "summary": "Winhttp issue",
            },
        ]
    )
    runtime_gaps = _gaps(
        [
            {
                "id": "gap-loader-2",
                "category": "loader",
                "severity": "high",
                "summary": "Another loader blocker",
            }
        ]
    )
    base_plan = _plans([{"gap_id": "gap-loader-1", "priority": "P0"}])
    runtime_plan = _plans([{"gap_id": "gap-loader-2", "priority": "P0"}])

    report = build_root_cause_summary(
        [base_gaps, runtime_gaps],
        patch_plan_artifacts=[base_plan, runtime_plan],
        labels=["base", "runtime"],
    )

    assert report["summary"]["scenario_count"] == 2
    assert report["summary"]["total_gaps"] == 3
    assert report["summary"]["high_severity_gaps"] == 2
    assert report["summary"]["p0_linked_proposals"] == 2
    assert report["summary"]["top_root_causes"][0] == "loader"
    assert report["actions"]


def test_root_cause_summary_handles_empty_inputs():
    report = build_root_cause_summary([])
    assert report["summary"]["scenario_count"] == 0
    assert report["summary"]["total_gaps"] == 0
    assert report["root_cause_clusters"] == []
    assert report["actions"]

