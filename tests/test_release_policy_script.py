from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-release-policy.sh"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_green_release_artifacts(tmp_path: Path, launch_status: str = "ready") -> None:
    _write_json(tmp_path / "quality-gate-report.json", {"gate": "pass"})
    _write_json(tmp_path / "release-decision-report.json", {"decision": "go"})
    _write_json(tmp_path / "launch-readiness-report.json", {"status": launch_status})
    _write_json(
        tmp_path / "policy-health-report.json",
        {"config_valid": True, "lockfile_sync": True},
    )


def test_release_policy_script_passes_for_green_outputs(tmp_path):
    if shutil.which("jq") is None:
        return

    _write_green_release_artifacts(tmp_path, launch_status="ready")

    result = subprocess.run(
        [str(SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "release policy check: ok" in result.stdout


def test_release_policy_script_fails_for_non_ready_launch(tmp_path):
    if shutil.which("jq") is None:
        return

    _write_green_release_artifacts(tmp_path, launch_status="limited")

    result = subprocess.run(
        [str(SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "expected launch readiness 'ready'" in result.stderr


def test_release_policy_script_fails_when_policy_health_is_not_synced(tmp_path):
    if shutil.which("jq") is None:
        return

    _write_green_release_artifacts(tmp_path, launch_status="ready")
    _write_json(
        tmp_path / "policy-health-report.json",
        {"config_valid": True, "lockfile_sync": False},
    )

    result = subprocess.run(
        [str(SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "expected policy lockfile_sync=true" in result.stderr


def test_release_policy_script_fails_when_jq_is_missing(tmp_path):
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    (fake_bin / "dirname").symlink_to("/usr/bin/dirname")

    result = subprocess.run(
        ["/bin/bash", str(SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": str(fake_bin)},
    )

    assert result.returncode == 2
    assert "missing dependency 'jq'" in result.stderr
