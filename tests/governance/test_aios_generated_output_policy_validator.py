from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.validators.aios_generated_output_policy_validator import validate


def repo_root() -> Path:
    return REPO_ROOT


def test_generated_output_policy_validator_passes() -> None:
    result = validate(repo_root())
    assert result["status"] == "PASS", result


def test_generated_output_policy_validator_cli_json() -> None:
    result = subprocess.run(
        [
            "python",
            "automation/validators/aios_generated_output_policy_validator.py",
            "--sample-check",
            "--repo-root",
            ".",
            "--json",
        ],
        cwd=repo_root(),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"status": "PASS"' in result.stdout
