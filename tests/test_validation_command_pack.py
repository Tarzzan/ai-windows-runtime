from compat_runtime.validation_command_pack.cli import build_validation_command_pack_report


def test_validation_command_pack_builds_ordered_deduped_commands():
    report = build_validation_command_pack_report(
        iteration_plan_report={
            "tasks": [
                {
                    "id": "t1",
                    "priority": "P0",
                    "blocking": True,
                    "objective": "Resolve com blocker",
                    "suggested_command": "pytest -q -k com",
                },
                {
                    "id": "t2",
                    "priority": "P1",
                    "blocking": False,
                    "objective": "Resolve network blocker",
                    "suggested_command": "pytest -q -k network",
                },
                {
                    "id": "t3",
                    "priority": "P0",
                    "blocking": True,
                    "objective": "Resolve com blocker 2",
                    "suggested_command": "pytest -q -k com",
                },
            ]
        },
        test_impact_report={"suites": []},
    )

    assert report["summary"]["commands_total"] == 2
    assert report["summary"]["blocking_commands"] == 1
    assert report["packs"]["quick"]


def test_validation_command_pack_handles_empty_tasks():
    report = build_validation_command_pack_report(
        iteration_plan_report={"tasks": []},
        test_impact_report={"suites": []},
    )
    assert report["summary"]["commands_total"] == 0
    assert report["packs"]["full"] == []
