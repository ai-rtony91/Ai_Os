from automation.orchestration.self_development.aios_self_build_validator_repair_engine import (
    build_validator_repair_result,
)


def test_pass_validators_stop_cleanly() -> None:
    result = build_validator_repair_result(
        {"validator_results": [{"validator_id": "identity", "status": "PASS"}]}
    )

    assert result["status"] == "PASS"
    assert result["repair_needed"] is False
    assert result["wake_required"] is False


def test_fail_validators_propose_repair_when_attempts_remain() -> None:
    result = build_validator_repair_result(
        {
            "validator_results": [{"validator_id": "chain", "status": "FAIL"}],
            "current_attempt": 0,
            "max_repair_attempts": 2,
        }
    )

    assert result["status"] == "REPAIR_ATTEMPT_AVAILABLE"
    assert result["repair_needed"] is True
    assert result["next_repair_action"]


def test_fail_after_max_attempts_stops_review_required() -> None:
    result = build_validator_repair_result(
        {
            "validator_results": [{"validator_id": "chain", "status": "FAIL"}],
            "current_attempt": 2,
            "max_repair_attempts": 2,
        }
    )

    assert result["status"] == "REPAIR_EXHAUSTED"
    assert result["repair_needed"] is False
    assert result["wake_required"] is False
    assert "MAX_REPAIR_ATTEMPTS_EXHAUSTED" in result["stop_conditions"]


def test_sos_hard_stops() -> None:
    result = build_validator_repair_result({"sos_status": "SOS_ACTIVE"})

    assert result["status"] == "HARD_STOP"
    assert result["wake_required"] is True
    assert "SOS_ACTIVE" in result["stop_conditions"]


def test_protected_boundary_hard_stops() -> None:
    result = build_validator_repair_result({"protected_boundary_hits": ["secrets"]})

    assert result["status"] == "HARD_STOP"
    assert result["wake_required"] is True
    assert "PROTECTED_BOUNDARY_HIT" in result["stop_conditions"]


def test_does_not_exceed_max_attempts() -> None:
    result = build_validator_repair_result(
        {
            "validator_results": [{"validator_id": "chain", "status": "FAIL"}],
            "current_attempt": 3,
            "max_repair_attempts": 2,
        }
    )

    assert result["current_attempt"] == 3
    assert result["max_repair_attempts"] == 2
    assert result["status"] == "REPAIR_EXHAUSTED"
