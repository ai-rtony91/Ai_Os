from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.orchestration.restart_safety.aios_restart_safety import classify_marker
from automation.validators.aios_restart_safety_validator import validate


def test_restart_safety_validator_passes() -> None:
    assert validate()["status"] == "PASS"


def test_completed_apply_phase_resumes_after_it() -> None:
    marker = {
        "cycle_id": "cycle-apply",
        "cycle_in_progress": True,
        "phases": [{"name": "hygiene"}, {"name": "clear-stale-approvals"}, {"name": "relay-runner"}],
        "completed_phases": ["hygiene", "clear-stale-approvals"],
    }
    decision = classify_marker(marker, marker_exists=True)

    assert decision.status == "RESUME_FROM_FIRST_INCOMPLETE_PHASE"
    assert decision.resume_from == "relay-runner"
    assert decision.completed_apply_phases == ["clear-stale-approvals"]
    assert decision.scheduler_allowed is False
    assert decision.live_sos_allowed is False


def test_validator_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "automation/validators/aios_restart_safety_validator.py",
            "--sample-check",
            "--json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert '"status": "PASS"' in result.stdout

