from __future__ import annotations

from pathlib import Path

from automation.validators.aios_worker_dispatcher_validator import sample_check


def test_worker_dispatcher_validator_sample_check_passes() -> None:
    result = sample_check(Path(__file__).resolve().parents[2])
    assert result["status"] == "PASS", result
