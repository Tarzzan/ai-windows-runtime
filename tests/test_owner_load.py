from compat_runtime.owner_load.cli import build_owner_load_report


def test_owner_load_detects_overloaded_owner():
    report = build_owner_load_report(
        ownership_assignment_report={
            "tasks": [
                {"owner": "a"}, {"owner": "a"}, {"owner": "a"}, {"owner": "a"}, {"owner": "b"}
            ]
        }
    )
    assert report["summary"]["overloaded_owners"] >= 1


def test_owner_load_balanced_case():
    report = build_owner_load_report(
        ownership_assignment_report={"tasks": [{"owner": "a"}, {"owner": "b"}]}
    )
    assert report["summary"]["owners_total"] == 2
