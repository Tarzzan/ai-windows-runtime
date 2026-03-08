from compat_runtime.control_efficiency.cli import build_control_efficiency_report


def test_control_efficiency_low_with_heavy_command_load():
    report = build_control_efficiency_report(
        execution_confidence_report={"summary": {"confidence_score": 25}},
        execution_momentum_report={"summary": {"momentum_index": 20}},
        validation_command_pack={"summary": {"commands_total": 14, "blocking_commands": 5}},
    )
    assert report["summary"]["efficiency_band"] == "low"


def test_control_efficiency_high_when_clean():
    report = build_control_efficiency_report(
        execution_confidence_report={"summary": {"confidence_score": 95}},
        execution_momentum_report={"summary": {"momentum_index": 88}},
        validation_command_pack={"summary": {"commands_total": 3, "blocking_commands": 0}},
    )
    assert report["summary"]["efficiency_band"] == "high"
