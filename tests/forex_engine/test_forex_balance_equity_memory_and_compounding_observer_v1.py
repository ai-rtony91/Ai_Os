from pathlib import Path

from automation.forex_engine.forex_balance_equity_memory_and_compounding_observer_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_RECEIPT_PROOF,
    BLOCKED_BY_SENSITIVE_DATA,
    GOVERNED_COMPOUNDING_ELIGIBLE,
    HARD_FALSE_FIELDS,
    PROFIT_STACKING_OBSERVATION_READY,
    SCALE_DOWN_ON_DRAWDOWN,
    TARGET_REACHED_PROTECT_PROFIT,
    evaluate_forex_balance_equity_memory_and_compounding_observer_v1,
)


def _payload(**overrides):
    payload = {
        "balance_memory": {
            "starting_balance": 10000.0,
            "current_balance": 10300.0,
            "current_equity": 10325.0,
            "realized_net_pnl": 300.0,
            "unrealized_pnl": 25.0,
            "trade_open_balance": 10250.0,
            "trade_close_balance": 10300.0,
            "day_start_balance": 10100.0,
            "day_current_balance": 10300.0,
            "week_start_balance": 10050.0,
            "week_current_balance": 10300.0,
            "month_start_balance": 10000.0,
            "month_current_balance": 10300.0,
            "vacation_mode_start_balance": 9900.0,
            "vacation_mode_current_balance": 10300.0,
            "snapshot_scope": "RUNTIME",
            "snapshot_event_id": "BALANCE-EVENT-001",
            "account_id_absent": True,
            "credentials_absent": True,
            "broker_values_absent": True,
        },
        "receipt_proof": {
            "receipts_required": True,
            "receipts_sanitized": True,
            "realized_pnl_verified": True,
            "fake_pnl_blocked": True,
            "balance_snapshot_source": "SANITIZED_RUNTIME_SNAPSHOT",
            "proof_ready_for_learning": True,
        },
        "compounding_policy": {
            "compounding_enabled": False,
            "compound_mode": "HOLD",
            "target_return_pct": 0.10,
            "target_balance": 12000.0,
            "profit_lock_pct": 0.5,
            "reinvest_profit_pct": 0.5,
            "max_scale_step_pct": 0.10,
            "stop_compounding_at_target": True,
            "scale_down_on_drawdown": True,
            "owner_review_required": True,
            "withdrawal_allowed": False,
            "bank_routing_allowed": False,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "max_drawdown_pct": 0.08,
            "current_drawdown_pct": 0.02,
            "max_daily_loss_pct": 0.03,
            "current_daily_loss_pct": 0.01,
        },
        "claims": {
            "guaranteed_profit_claimed": False,
            "fixed_return_promised": False,
            "daily_profit_guaranteed": False,
            "weekly_profit_guaranteed": False,
            "monthly_profit_guaranteed": False,
            "yearly_profit_guaranteed": False,
        },
    }
    for section, values in overrides.items():
        payload[section].update(values)
    return payload


def test_positive_realized_profit_stacks_correctly():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(_payload())

    assert result["status"] == PROFIT_STACKING_OBSERVATION_READY
    assert result["realized_profit_from_baseline"] == 300.0
    assert result["recommended_profit_lock_amount"] == 150.0
    assert result["recommended_reinvest_amount"] == 150.0


def test_trade_day_week_month_vacation_deltas_calculate_correctly():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(_payload())

    assert result["trade_delta"] == 50.0
    assert result["day_delta"] == 200.0
    assert result["week_delta"] == 250.0
    assert result["month_delta"] == 300.0
    assert result["vacation_mode_delta"] == 400.0
    assert result["equity_drift"] == 25.0


def test_compounding_disabled_returns_profit_stacking_observation():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(_payload())

    assert result["status"] == PROFIT_STACKING_OBSERVATION_READY
    assert result["next_best_packet"] == "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"


def test_compounding_enabled_with_verified_profit_returns_eligible():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(compounding_policy={"compounding_enabled": True, "compound_mode": "COMPOUND_TO_PERCENT_TARGET"})
    )

    assert result["status"] == GOVERNED_COMPOUNDING_ELIGIBLE
    assert result["next_best_packet"] == "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"


def test_target_return_reached_routes_profit_protection_future_packet():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(compounding_policy={"target_return_pct": 0.02})
    )

    assert result["status"] == TARGET_REACHED_PROTECT_PROFIT
    assert result["target_return_reached"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1"


def test_target_balance_reached_routes_profit_protection_future_packet():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(compounding_policy={"target_balance": 10200.0})
    )

    assert result["status"] == TARGET_REACHED_PROTECT_PROFIT
    assert result["target_balance_reached"] is True


def test_drawdown_breach_routes_scale_down():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(
            compounding_policy={"compounding_enabled": True},
            risk_state={"drawdown_within_limit": False, "current_drawdown_pct": 0.12},
        )
    )

    assert result["status"] == SCALE_DOWN_ON_DRAWDOWN
    assert result["next_best_packet"] == "AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1"


def test_missing_receipt_proof_blocks():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(receipt_proof={"receipts_sanitized": False})
    )

    assert result["status"] == BLOCKED_BY_RECEIPT_PROOF


def test_profit_guarantee_blocks():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(claims={"daily_profit_guaranteed": True})
    )

    assert result["status"] == BLOCKED_BY_PROFIT_CLAIM


def test_sensitive_data_blocks_and_does_not_echo_raw_value():
    payload = _payload()
    payload["receipt_proof"]["api_key"] = "sk-private-value"

    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(payload)

    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-private-value" not in str(result)


def test_string_long_digit_secret_looking_value_blocks():
    payload = _payload()
    payload["balance_memory"]["note"] = "9999999999"

    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(payload)

    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA


def test_large_numeric_balance_fields_do_not_false_positive_as_secrets():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(balance_memory={"current_balance": 100000000.0, "current_equity": 100000010.0})
    )

    assert result["status"] == TARGET_REACHED_PROTECT_PROFIT
    assert not result["blockers"]


def test_banking_or_withdrawal_focus_blocks():
    payload = _payload()
    payload["compounding_policy"]["withdrawal_plan"] = "active"

    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(payload)

    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_withdrawal_allowed_false_does_not_block():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(compounding_policy={"withdrawal_allowed": False})
    )

    assert result["status"] == PROFIT_STACKING_OBSERVATION_READY


def test_bank_routing_allowed_false_does_not_block():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
        _payload(compounding_policy={"bank_routing_allowed": False})
    )

    assert result["status"] == PROFIT_STACKING_OBSERVATION_READY


def test_withdrawal_allowed_by_this_module_remains_false():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(_payload())

    assert result["withdrawal_allowed_by_this_module"] is False
    assert result["safety"]["withdrawal_allowed_by_this_module"] is False


def test_bank_routing_built_remains_false():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(_payload())

    assert result["bank_routing_built"] is False
    assert result["safety"]["bank_routing_built"] is False


def test_all_hard_false_fields_remain_false():
    result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(_payload())

    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_production_source_has_no_forbidden_runtime_markers():
    source = Path(
        "automation/forex_engine/forex_balance_equity_memory_and_compounding_observer_v1.py"
    ).read_text(encoding="utf-8").lower()
    forbidden = [
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ]

    assert {marker: marker in source for marker in forbidden} == {
        marker: False for marker in forbidden
    }
