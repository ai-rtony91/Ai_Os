from automation.forex_engine.forex_vacation_mode_exit_authority_gate_v1 import (
    EXIT_AUTHORITY_HOLD_ALLOWED,
    EXIT_REQUIRED_BY_KILL_SWITCH,
    EXIT_REQUIRED_BY_MARKET_CLOSE,
    EXIT_REQUIRED_BY_RULE_FAILURE,
    EXIT_REQUIRED_BY_STOP_LOSS,
    EXIT_REQUIRED_BY_TAKE_PROFIT,
    INCOMPLETE_INPUTS,
    evaluate_forex_vacation_mode_exit_authority_gate_v1,
)


def _exit_payload(**overrides):
    payload = {
        "position_state": {"rule_failure_detected": False},
        "exit_signal_state": {
            "take_profit_triggered": False,
            "rule_failure_exit_required": False,
            "owner_exit_review_requested": False,
            "post_exit_receipt_capture_plan_ready": True,
            "owner_visible_reason_present": True,
        },
        "risk_state": {
            "stop_loss_triggered": False,
            "daily_loss_stop_active": False,
            "max_loss_limit_hit": False,
        },
        "market_state": {"market_close_exit_required": False},
        "owner_authority_state": {
            "owner_exit_review_allowed": True,
            "owner_visible_reason_required": True,
            "repeat_attempt_blocked_until_review": True,
        },
        "safety_policy": {
            "metadata_only": True,
            "no_order_close": True,
            "no_broker_call": True,
            "no_oanda_call": True,
            "no_trade_execution": True,
            "kill_switch_active": False,
        },
    }
    for section, values in overrides.items():
        payload[section].update(values)
    return payload


def _missing_receipt_plan_payload(**overrides):
    payload = _exit_payload(**overrides)
    del payload["exit_signal_state"]["post_exit_receipt_capture_plan_ready"]
    del payload["exit_signal_state"]["owner_visible_reason_present"]
    return payload


def _assert_receipt_plan_blockers(result):
    assert "post_exit_receipt_capture_plan_ready_required_true" in result["blockers"]
    assert "owner_visible_reason_present_required_true" in result["blockers"]


def test_incomplete_input_blocks():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1()

    assert result["status"] == INCOMPLETE_INPUTS


def test_holds_when_no_exit_trigger_exists():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(_exit_payload())

    assert result["status"] == EXIT_AUTHORITY_HOLD_ALLOWED


def test_missing_stop_loss_trigger_blocks():
    payload = _exit_payload()
    del payload["risk_state"]["stop_loss_triggered"]

    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(payload)

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "stop_loss_triggered_required_bool" in result["blockers"]


def test_non_bool_stop_loss_trigger_blocks():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"stop_loss_triggered": "true"})
    )

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "stop_loss_triggered_required_bool" in result["blockers"]


def test_truthy_non_bool_values_do_not_hold_for_stop_loss():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"stop_loss_triggered": 1})
    )

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "stop_loss_triggered_required_bool" in result["blockers"]


def test_stop_loss_false_can_hold_when_clear():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"stop_loss_triggered": False})
    )

    assert result["status"] == EXIT_AUTHORITY_HOLD_ALLOWED


def test_missing_daily_loss_stop_active_blocks():
    payload = _exit_payload()
    del payload["risk_state"]["daily_loss_stop_active"]

    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(payload)

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "daily_loss_stop_active_required_bool" in result["blockers"]


def test_non_bool_daily_loss_stop_active_blocks():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"daily_loss_stop_active": "true"})
    )

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "daily_loss_stop_active_required_bool" in result["blockers"]


def test_missing_max_loss_limit_hit_blocks():
    payload = _exit_payload()
    del payload["risk_state"]["max_loss_limit_hit"]

    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(payload)

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "max_loss_limit_hit_required_bool" in result["blockers"]


def test_non_bool_max_loss_limit_hit_blocks():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"max_loss_limit_hit": "true"})
    )

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "max_loss_limit_hit_required_bool" in result["blockers"]


def test_daily_loss_stop_active_requires_exit():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"daily_loss_stop_active": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_STOP_LOSS


def test_max_loss_limit_hit_requires_exit():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"max_loss_limit_hit": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_STOP_LOSS


def test_missing_kill_switch_blocks():
    payload = _exit_payload()
    del payload["safety_policy"]["kill_switch_active"]

    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(payload)

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "kill_switch_active_required_bool" in result["blockers"]
    assert result["status"] != EXIT_AUTHORITY_HOLD_ALLOWED


def test_non_bool_kill_switch_blocks():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(safety_policy={"kill_switch_active": "unknown"})
    )

    assert result["status"] == "EXIT_BLOCKED_BY_SAFETY"
    assert "kill_switch_active_required_bool" in result["blockers"]
    assert result["status"] != EXIT_AUTHORITY_HOLD_ALLOWED


def test_requires_exit_for_stop_loss():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(risk_state={"stop_loss_triggered": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_STOP_LOSS


def test_requires_exit_for_take_profit():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(exit_signal_state={"take_profit_triggered": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_TAKE_PROFIT


def test_requires_exit_for_market_close():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(market_state={"market_close_exit_required": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_MARKET_CLOSE


def test_requires_exit_for_kill_switch():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(safety_policy={"kill_switch_active": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_KILL_SWITCH


def test_false_kill_switch_can_still_hold_when_clear():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _exit_payload(safety_policy={"kill_switch_active": False})
    )

    assert result["status"] == EXIT_AUTHORITY_HOLD_ALLOWED


def test_stop_loss_keeps_status_when_receipt_plan_missing():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _missing_receipt_plan_payload(risk_state={"stop_loss_triggered": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_STOP_LOSS
    _assert_receipt_plan_blockers(result)


def test_take_profit_keeps_status_when_receipt_plan_missing():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _missing_receipt_plan_payload(exit_signal_state={"take_profit_triggered": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_TAKE_PROFIT
    _assert_receipt_plan_blockers(result)


def test_market_close_keeps_status_when_receipt_plan_missing():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _missing_receipt_plan_payload(market_state={"market_close_exit_required": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_MARKET_CLOSE
    _assert_receipt_plan_blockers(result)


def test_kill_switch_keeps_status_when_receipt_plan_missing():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _missing_receipt_plan_payload(safety_policy={"kill_switch_active": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_KILL_SWITCH
    _assert_receipt_plan_blockers(result)


def test_rule_failure_keeps_status_when_receipt_plan_missing():
    result = evaluate_forex_vacation_mode_exit_authority_gate_v1(
        _missing_receipt_plan_payload(exit_signal_state={"rule_failure_exit_required": True})
    )

    assert result["status"] == EXIT_REQUIRED_BY_RULE_FAILURE
    _assert_receipt_plan_blockers(result)
