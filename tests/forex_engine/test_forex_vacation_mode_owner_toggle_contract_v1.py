from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_OWNER_COMMAND,
    BLOCKED_BY_SENSITIVE_DATA,
    VACATION_MODE_KILL_SWITCH_REQUEST_VALID,
    VACATION_MODE_KILL_SWITCH_RESET_REVIEW_REQUIRED,
    VACATION_MODE_OWNER_PAUSE_REQUEST_VALID,
    VACATION_MODE_OWNER_RESUME_REQUEST_VALID,
    VACATION_MODE_OWNER_TOGGLE_OFF_REQUEST_VALID,
    VACATION_MODE_OWNER_TOGGLE_ON_REQUEST_VALID,
    evaluate_forex_vacation_mode_owner_toggle_contract_v1,
)


def _payload(command="ON", **overrides):
    owner_command = {
        "command_id": "CMD-001",
        "requested_toggle_state": command,
        "owner_control_required": True,
        "owner_identity_confirmed": True,
        "command_timestamp_present": True,
        "command_source": "OWNER_DASHBOARD",
        "toggle_is_request_only": True,
        "toggle_does_not_authorize_execution": True,
        "toggle_does_not_authorize_withdrawal": True,
        "kill_switch_is_separate": True,
        "no_banking_requested": True,
        "no_credentials_in_command": True,
    }
    owner_command.update(overrides)
    return {"owner_command": owner_command}


def test_on_request_valid():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(_payload("ON"))

    assert result["status"] == VACATION_MODE_OWNER_TOGGLE_ON_REQUEST_VALID
    assert result["vacation_mode_requested"] is True
    assert result["vacation_mode_toggle_state"] == "ON"
    assert result["owner_toggle_contract"]["toggle_semantics"]["toggle_does_not_execute"] is True


def test_off_request_valid():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(_payload("OFF"))

    assert result["status"] == VACATION_MODE_OWNER_TOGGLE_OFF_REQUEST_VALID
    assert result["vacation_mode_requested"] is False
    assert result["vacation_mode_toggle_state"] == "OFF"


def test_pause_request_valid():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(_payload("PAUSE"))

    assert result["status"] == VACATION_MODE_OWNER_PAUSE_REQUEST_VALID
    assert result["vacation_mode_toggle_state"] == "PAUSED"


def test_resume_request_valid():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(_payload("RESUME"))

    assert result["status"] == VACATION_MODE_OWNER_RESUME_REQUEST_VALID
    assert result["vacation_mode_toggle_state"] == "RESUME_REVIEW"


def test_kill_switch_stop_request_valid():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(_payload("KILL_SWITCH_STOP"))

    assert result["status"] == VACATION_MODE_KILL_SWITCH_REQUEST_VALID
    assert result["kill_switch_active"] is True


def test_kill_switch_reset_review_requires_review():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(_payload("KILL_SWITCH_RESET_REVIEW"))

    assert result["status"] == VACATION_MODE_KILL_SWITCH_RESET_REVIEW_REQUIRED
    assert result["owner_attention_required"] is True


def test_toggle_is_request_only_false_blocks():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        _payload("ON", toggle_is_request_only=False)
    )

    assert result["status"] == BLOCKED_BY_OWNER_COMMAND
    assert "toggle_is_request_only" in result["blockers"]


def test_toggle_does_not_authorize_execution_false_blocks():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        _payload("ON", toggle_does_not_authorize_execution=False)
    )

    assert result["status"] == BLOCKED_BY_OWNER_COMMAND


def test_toggle_does_not_authorize_withdrawal_false_blocks():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        _payload("ON", toggle_does_not_authorize_withdrawal=False)
    )

    assert result["status"] == BLOCKED_BY_OWNER_COMMAND


def test_kill_switch_is_separate_false_blocks():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        _payload("ON", kill_switch_is_separate=False)
    )

    assert result["status"] == BLOCKED_BY_OWNER_COMMAND


def test_sensitive_data_blocks_and_does_not_echo_raw_value():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        _payload("ON", api_key="sk-private-value")
    )

    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-private-value" not in str(result)


def test_banking_focus_blocks():
    result = evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        _payload("ON", withdrawal_plan="active")
    )

    assert result["status"] == BLOCKED_BY_BANKING_FOCUS
