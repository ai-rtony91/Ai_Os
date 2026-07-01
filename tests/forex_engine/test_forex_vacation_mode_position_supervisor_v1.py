from automation.forex_engine.forex_vacation_mode_position_supervisor_v1 import (
    INCOMPLETE_INPUTS,
    POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED,
    POSITION_SUPERVISION_EXIT_REVIEW_REQUIRED,
    POSITION_SUPERVISION_HOLD,
    POSITION_SUPERVISION_RECEIPT_REQUIRED,
    evaluate_forex_vacation_mode_position_supervisor_v1,
)


def _position_payload(**overrides):
    payload = {
        "position_state": {
            "position_metadata_present": True,
            "rule_failure_detected": False,
            "exit_review_required": False,
        },
        "risk_state": {
            "risk_within_limits": True,
            "daily_loss_stop_active": False,
            "max_loss_limit_hit": False,
        },
        "market_state": {"market_state_safe": True},
        "receipt_state": {"receipt_present": True},
        "owner_alert_state": {"owner_alert_required": False},
        "safety_policy": {
            "metadata_only": True,
            "no_trade_alteration": True,
            "no_trade_close": True,
            "no_broker_call": True,
            "no_oanda_call": True,
            "owner_visible_status": True,
            "kill_switch_active": False,
        },
    }
    for section, values in overrides.items():
        payload[section].update(values)
    return payload


def test_incomplete_input_blocks():
    result = evaluate_forex_vacation_mode_position_supervisor_v1()

    assert result["status"] == INCOMPLETE_INPUTS


def test_hold_when_all_clear():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(_position_payload())

    assert result["status"] == POSITION_SUPERVISION_HOLD


def test_missing_kill_switch_blocks():
    payload = _position_payload()
    del payload["safety_policy"]["kill_switch_active"]

    result = evaluate_forex_vacation_mode_position_supervisor_v1(payload)

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_SAFETY"
    assert "kill_switch_active_required_bool" in result["blockers"]
    assert result["status"] != POSITION_SUPERVISION_HOLD


def test_non_bool_kill_switch_blocks():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(safety_policy={"kill_switch_active": "unknown"})
    )

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_SAFETY"
    assert "kill_switch_active_required_bool" in result["blockers"]
    assert result["status"] != POSITION_SUPERVISION_HOLD


def test_missing_position_metadata_present_does_not_hold():
    payload = _position_payload()
    del payload["position_state"]["position_metadata_present"]

    result = evaluate_forex_vacation_mode_position_supervisor_v1(payload)

    assert result["status"] == INCOMPLETE_INPUTS
    assert result["status"] != POSITION_SUPERVISION_HOLD
    assert "position_metadata_present_required_true" in result["blockers"]


def test_false_position_metadata_present_does_not_hold():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(position_state={"position_metadata_present": False})
    )

    assert result["status"] == INCOMPLETE_INPUTS
    assert result["status"] != POSITION_SUPERVISION_HOLD
    assert "position_metadata_present_required_true" in result["blockers"]


def test_exit_review_for_rule_failure():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(position_state={"rule_failure_detected": True})
    )

    assert result["status"] == POSITION_SUPERVISION_EXIT_REVIEW_REQUIRED


def test_emergency_stop_for_kill_switch():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(safety_policy={"kill_switch_active": True})
    )

    assert result["status"] == POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED


def test_false_kill_switch_can_still_hold_when_clear():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(safety_policy={"kill_switch_active": False})
    )

    assert result["status"] == POSITION_SUPERVISION_HOLD


def test_missing_daily_loss_stop_active_blocks():
    payload = _position_payload()
    del payload["risk_state"]["daily_loss_stop_active"]

    result = evaluate_forex_vacation_mode_position_supervisor_v1(payload)

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_RISK"
    assert "daily_loss_stop_active_required_bool" in result["blockers"]


def test_non_bool_daily_loss_stop_active_blocks():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"daily_loss_stop_active": 1})
    )

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_RISK"
    assert "daily_loss_stop_active_required_bool" in result["blockers"]


def test_truthy_non_bool_daily_loss_stop_active_does_not_hold():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"daily_loss_stop_active": "true"})
    )

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_RISK"
    assert "daily_loss_stop_active_required_bool" in result["blockers"]


def test_daily_loss_stop_active_routes_to_emergency_stop():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"daily_loss_stop_active": True})
    )

    assert result["status"] == POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED
    assert "daily_loss_stop_active" in result["blockers"]


def test_daily_loss_stop_active_false_can_still_hold_when_clear():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"daily_loss_stop_active": False})
    )

    assert result["status"] == POSITION_SUPERVISION_HOLD


def test_missing_max_loss_limit_hit_blocks():
    payload = _position_payload()
    del payload["risk_state"]["max_loss_limit_hit"]

    result = evaluate_forex_vacation_mode_position_supervisor_v1(payload)

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_RISK"
    assert "max_loss_limit_hit_required_bool" in result["blockers"]


def test_non_bool_max_loss_limit_hit_blocks():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"max_loss_limit_hit": 1})
    )

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_RISK"
    assert "max_loss_limit_hit_required_bool" in result["blockers"]


def test_truthy_non_bool_max_loss_limit_hit_does_not_hold():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"max_loss_limit_hit": "true"})
    )

    assert result["status"] == "POSITION_SUPERVISION_BLOCKED_BY_RISK"
    assert "max_loss_limit_hit_required_bool" in result["blockers"]


def test_max_loss_limit_hit_routes_to_emergency_stop():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"max_loss_limit_hit": True})
    )

    assert result["status"] == POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED
    assert "max_loss_limit_hit" in result["blockers"]


def test_max_loss_limit_hit_false_can_still_hold_when_clear():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(risk_state={"max_loss_limit_hit": False})
    )

    assert result["status"] == POSITION_SUPERVISION_HOLD


def test_receipt_required_when_missing():
    result = evaluate_forex_vacation_mode_position_supervisor_v1(
        _position_payload(receipt_state={"receipt_present": False})
    )

    assert result["status"] == POSITION_SUPERVISION_RECEIPT_REQUIRED
