from pathlib import Path

from automation.forex_engine.forex_governed_compounding_capital_scaling_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_BALANCE_OBSERVER,
    BLOCKED_BY_POLICY,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_RECEIPT_PROOF,
    BLOCKED_BY_RISK_STATE,
    BLOCKED_BY_SENSITIVE_DATA,
    GOVERNED_COMPOUNDING_HOLD_REQUIRED,
    GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED,
    GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED,
    GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED,
    GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT,
    INCOMPLETE_INPUTS,
    evaluate_forex_governed_compounding_capital_scaling_v1,
    HARD_FALSE_FIELDS,
    SCHEMA,
)


def _payload() -> dict:
    return {
        "balance_observer_result": {
            "status": "TARGET_NOT_REACHED",
            "ready": True,
            "realized_profit_from_baseline": 2500.0,
            "equity_drift": 12.5,
            "target_return_reached": False,
            "target_balance_reached": False,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
            "money_moved": False,
        },
        "compounding_scale_policy": {
            "compounding_enabled": True,
            "owner_review_required": True,
            "scale_up_allowed": True,
            "scale_down_on_drawdown": True,
            "stop_at_target": True,
            "current_risk_budget_pct": 0.0020,
            "max_scale_step_pct": 0.0010,
            "max_risk_per_trade_pct": 0.0100,
            "max_total_burst_risk_pct": 0.0250,
            "profit_lock_pct": 0.35,
            "reinvest_profit_pct": 0.25,
            "minimum_verified_profit_to_scale": 500.0,
            "consecutive_scale_ups_since_review": 1,
            "max_consecutive_scale_ups_before_review": 4,
            "withdrawal_allowed": False,
            "bank_routing_allowed": False,
            "money_movement_allowed": False,
        },
        "proof_state": {
            "receipts_sanitized": True,
            "realized_pnl_verified": True,
            "repeatability_score": 82,
            "proof_ready_for_scaling": True,
            "fake_pnl_blocked": True,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "current_drawdown_pct": 0.015,
            "max_drawdown_pct": 0.04,
            "current_daily_loss_pct": 0.004,
            "max_daily_loss_pct": 0.03,
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


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_governed_compounding_capital_scaling_v1(payload)


def _replace(payload: dict, **updates: dict) -> dict:
    working = _payload()
    for section, values in updates.items():
        if section == "balance_observer_result":
            working[section].update(values)
            continue
        if section == "compounding_scale_policy":
            working[section].update(values)
            continue
        if section == "proof_state":
            working[section].update(values)
            continue
        if section == "risk_state":
            working[section].update(values)
            continue
        if section == "claims":
            working[section].update(values)
            continue
        if section == "top":
            working.update(values)
    return working


def test_schema_and_mode_present() -> None:
    result = _run(_payload())
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["metadata_only"] is True


def test_clean_verified_profit_allows_scale_up() -> None:
    result = _run(_payload())
    assert result["status"] == GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED
    assert result["scale_decision"] == "SCALE_UP"
    assert result["scale_direction"] == "UP"
    assert result["proposed_next_risk_budget_pct"] == 0.003


def test_compounding_disabled_holds() -> None:
    payload = _replace(_payload(), compounding_scale_policy={"compounding_enabled": False})
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_HOLD_REQUIRED


def test_target_return_reached_routes_protect_profit() -> None:
    payload = _replace(_payload(), balance_observer_result={"target_return_reached": True})
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT


def test_target_balance_reached_routes_protect_profit() -> None:
    payload = _replace(
        _payload(),
        balance_observer_result={"target_balance_reached": True},
    )
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT


def test_drawdown_breach_routes_scale_down() -> None:
    payload = _replace(
        _payload(),
        risk_state={"drawdown_within_limit": False},
    )
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED
    assert result["next_best_packet"] == "AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1"


def test_daily_loss_stop_blocks() -> None:
    payload = _replace(_payload(), risk_state={"daily_loss_stop_active": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_kill_switch_blocks() -> None:
    payload = _replace(_payload(), risk_state={"kill_switch_active": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_missing_receipt_proof_blocks() -> None:
    payload = _replace(_payload(), proof_state={"receipts_sanitized": False})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_RECEIPT_PROOF


def test_unsanitized_receipts_block() -> None:
    payload = _replace(_payload(), proof_state={"fake_pnl_blocked": False})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_RECEIPT_PROOF


def test_low_repeatability_holds() -> None:
    payload = _replace(_payload(), proof_state={"repeatability_score": 50})
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_HOLD_REQUIRED


def test_scale_up_not_allowed_routes_owner_review() -> None:
    payload = _replace(_payload(), compounding_scale_policy={"scale_up_allowed": False})
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED


def test_max_consecutive_scale_ups_routes_owner_review() -> None:
    payload = _replace(
        _payload(),
        compounding_scale_policy={"consecutive_scale_ups_since_review": 3, "max_consecutive_scale_ups_before_review": 3},
    )
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED


def test_profit_claim_blocks() -> None:
    payload = _replace(_payload(), claims={"guaranteed_profit_claimed": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_PROFIT_CLAIM


def test_withdrawal_banking_focus_blocks() -> None:
    payload = _replace(_payload(), top={"active_withdrawal_plan": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_withdrawal_allowed_false_does_not_block() -> None:
    payload = _replace(_payload(), compounding_scale_policy={"withdrawal_allowed": False})
    result = _run(payload)
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS

    assert result["risk_policy_summary"]["withdrawal_allowed"] is False


def test_bank_routing_allowed_false_does_not_block() -> None:
    payload = _replace(_payload(), compounding_scale_policy={"bank_routing_allowed": False})
    result = _run(payload)
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS
    assert result["risk_policy_summary"]["bank_routing_allowed"] is False


def test_money_movement_allowed_false_does_not_block() -> None:
    payload = _replace(_payload(), compounding_scale_policy={"money_movement_allowed": False})
    result = _run(payload)
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS
    assert result["risk_policy_summary"]["money_movement_allowed"] is False


def test_large_numeric_balances_do_not_sensitive_block() -> None:
    payload = _replace(
        _payload(),
        balance_observer_result={"realized_profit_from_baseline": 12345678901234567890},
    )
    result = _run(payload)
    assert result["status"] != BLOCKED_BY_SENSITIVE_DATA


def test_secret_string_blocks_and_not_echoed() -> None:
    payload = _replace(_payload(), top={"api_key": "sk-DO-NOT-ECHO"})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-DO-NOT-ECHO" not in repr(result)


def test_proposed_risk_budget_is_capped() -> None:
    payload = _replace(
        _payload(),
        compounding_scale_policy={
            "current_risk_budget_pct": 0.0095,
            "max_scale_step_pct": 0.004,
            "max_risk_per_trade_pct": 0.01,
        },
    )
    result = _run(payload)
    assert result["status"] == GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED
    assert result["proposed_next_risk_budget_pct"] == 0.01


def test_profit_lock_and_reinvest_amounts_calculate() -> None:
    payload = _replace(
        _payload(),
        compounding_scale_policy={"profit_lock_pct": 0.4, "reinvest_profit_pct": 0.25},
        balance_observer_result={"realized_profit_from_baseline": 1000.0},
    )
    result = _run(payload)
    assert result["profit_lock_amount"] == 400.0
    assert result["reinvest_amount"] == 250.0
    assert result["protected_profit_amount"] == result["profit_lock_amount"]


def test_all_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    assert result["safety"]["read_only"] is True
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_missing_inputs_incomplete() -> None:
    result = _run({})
    assert result["status"] == INCOMPLETE_INPUTS


def test_policy_limit_checks_block() -> None:
    payload = _replace(
        _payload(),
        compounding_scale_policy={"max_scale_step_pct": 0.5},
    )
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_POLICY


def test_balance_money_moved_active_blocks() -> None:
    payload = _replace(_payload(), balance_observer_result={"money_moved": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_BALANCE_OBSERVER


def test_receipt_and_balance_blocking_repair_routing() -> None:
    payload = _replace(_payload(), proof_state={"proof_ready_for_scaling": False})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_RECEIPT_PROOF
    assert result["next_best_packet"] == "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"


def test_routing_for_hard_actions() -> None:
    assert (
        _run(_payload())["next_best_packet"]
        == "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
    )
    hold = _replace(_payload(), compounding_scale_policy={"compounding_enabled": False})
    assert (
        _run(hold)["next_best_packet"]
        == "AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1"
    )


def test_production_source_has_no_forbidden_runtime_markers() -> None:
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
    module_path = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "forex_governed_compounding_capital_scaling_v1.py"
    text = module_path.read_text(encoding="utf-8").lower()
    assert [marker for marker in forbidden if marker in text] == []
