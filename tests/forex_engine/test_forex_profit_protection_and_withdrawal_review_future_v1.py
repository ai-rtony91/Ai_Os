from pathlib import Path

from automation.forex_engine.forex_profit_protection_and_withdrawal_review_future_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_COMPOUNDING_RESULT,
    BLOCKED_BY_MISSING_RECEIPTS,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_PROFIT_POLICY,
    BLOCKED_BY_SENSITIVE_DATA,
    BLOCKED_BY_UNREALIZED_PROFIT,
    OWNER_REVIEW_REQUIRED,
    PROFIT_LOCK_READY,
    REINVESTMENT_BUCKET_READY,
    WITHDRAWAL_REVIEW_FUTURE_READY,
    HARD_FALSE_FIELDS,
    evaluate_forex_profit_protection_and_withdrawal_review_future_v1,
)


def _payload() -> dict:
    return {
        "compounding_result": {
            "status": "GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED",
            "ready": True,
            "scale_decision": "SCALE_UP",
            "protected_profit_amount": 800.0,
            "reinvest_amount": 400.0,
            "profit_lock_amount": 800.0,
            "money_moved": False,
            "withdrawal_allowed_by_this_module": False,
            "bank_routing_allowed_by_this_module": False,
            "live_profit_guaranteed": False,
            "fixed_return_promised_by_aios": False,
        },
        "profit_protection_policy": {
            "realized_profit_only": True,
            "receipts_required": True,
            "receipts_sanitized": True,
            "owner_review_required": True,
            "protect_profit_at_target": True,
            "profit_lock_pct": 0.4,
            "reinvest_profit_pct": 0.2,
            "minimum_profit_to_protect": 500.0,
            "withdrawal_review_future_allowed": True,
            "withdrawal_execution_allowed": False,
            "bank_routing_allowed": False,
            "money_movement_allowed": False,
            "transfer_allowed": False,
            "ach_allowed": False,
            "wire_allowed": False,
            "card_allowed": False,
            "deposit_allowed": False,
        },
        "profit_state": {
            "realized_net_profit": 2000.0,
            "unrealized_profit": 0.0,
            "target_reached": False,
            "target_type": "RETURN_TARGET",
            "receipts_ready": True,
            "pnl_reconciled": True,
            "fake_pnl_blocked": True,
            "balance_snapshot_ready": True,
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
    return evaluate_forex_profit_protection_and_withdrawal_review_future_v1(payload)


def _replace(**updates: dict) -> dict:
    payload = _payload()
    for section, values in updates.items():
        if section in payload:
            payload[section].update(values)
        else:
            payload.update(values)
    return payload


def test_realized_profit_locks() -> None:
    result = _run(_payload())
    assert result["status"] == PROFIT_LOCK_READY
    assert result["next_best_packet"] == "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"


def test_target_reached_routes_future_withdrawal_review() -> None:
    payload = _replace(profit_state={"target_reached": True})
    result = _run(payload)
    assert result["status"] == WITHDRAWAL_REVIEW_FUTURE_READY
    assert result["withdrawal_review_future_enabled"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_PROFIT_WITHDRAWAL_OWNER_REVIEW_FUTURE_V1"


def test_reinvestment_bucket_routes_active_supervision() -> None:
    payload = _replace(
        profit_protection_policy={"minimum_profit_to_protect": 5000.0},
        compounding_result={"reinvest_amount": 250.0},
        profit_state={"target_reached": False},
    )
    result = _run(payload)
    assert result["status"] == REINVESTMENT_BUCKET_READY
    assert result["next_best_packet"] == "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"


def test_unrealized_only_profit_blocks() -> None:
    payload = _replace(profit_state={"realized_net_profit": 0.0, "unrealized_profit": 250.0})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_UNREALIZED_PROFIT


def test_missing_receipts_blocks() -> None:
    payload = _replace(profit_state={"receipts_ready": False})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_MISSING_RECEIPTS


def test_unsanitized_receipts_block() -> None:
    payload = _replace(profit_protection_policy={"receipts_sanitized": False})
    result = _run(payload)
    assert result["status"] in {BLOCKED_BY_PROFIT_POLICY, BLOCKED_BY_MISSING_RECEIPTS}


def test_unreconciled_pnl_blocks() -> None:
    payload = _replace(profit_state={"pnl_reconciled": False})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_MISSING_RECEIPTS


def test_fake_pnl_boundary_missing_blocks() -> None:
    payload = _replace(profit_state={"fake_pnl_blocked": False})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_MISSING_RECEIPTS


def test_compounding_result_not_ready_blocks() -> None:
    payload = _replace(compounding_result={"ready": False})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_COMPOUNDING_RESULT


def test_compounding_result_money_moved_true_blocks() -> None:
    payload = _replace(compounding_result={"money_moved": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_COMPOUNDING_RESULT


def test_active_withdrawal_request_blocks() -> None:
    payload = _replace(profit_protection_policy={"withdrawal_execution_allowed": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_active_bank_routing_blocks() -> None:
    payload = _replace(profit_protection_policy={"bank_routing_allowed": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_active_money_movement_blocks() -> None:
    payload = _replace(profit_protection_policy={"money_movement_allowed": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_active_transfer_ach_wire_card_deposit_blocks() -> None:
    for field in ("transfer_allowed", "ach_allowed", "wire_allowed", "card_allowed", "deposit_allowed"):
        payload = _replace(profit_protection_policy={field: True})
        result = _run(payload)
        assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_false_banking_flags_do_not_block() -> None:
    payload = _replace(
        profit_protection_policy={
            "withdrawal_execution_allowed": False,
            "bank_routing_allowed": False,
            "money_movement_allowed": False,
            "transfer_allowed": False,
            "ach_allowed": False,
            "wire_allowed": False,
            "card_allowed": False,
            "deposit_allowed": False,
        }
    )
    result = _run(payload)
    assert result["status"] == PROFIT_LOCK_READY
    assert result["withdrawal_execution_allowed"] is False
    assert result["bank_routing_allowed"] is False
    assert result["money_moved"] is False


def test_profit_guarantee_blocks() -> None:
    payload = _replace(claims={"guaranteed_profit_claimed": True})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_PROFIT_CLAIM


def test_secret_string_blocks_and_not_echoed() -> None:
    payload = _replace(top={"api_key": "sk-DO-NOT-ECHO"})
    result = _run(payload)
    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-DO-NOT-ECHO" not in repr(result)


def test_large_numeric_profit_values_do_not_sensitive_block() -> None:
    payload = _replace(profit_state={"realized_net_profit": 12345678901234567890})
    result = _run(payload)
    assert result["status"] == PROFIT_LOCK_READY


def test_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_withdrawal_review_future_enabled_true_only_for_future_review_not_execution() -> None:
    future_review = _run(_replace(profit_state={"target_reached": True}))
    lock_ready = _run(_payload())
    assert future_review["withdrawal_review_future_enabled"] is True
    assert lock_ready["withdrawal_review_future_enabled"] is False


def test_owner_review_required_for_low_profit() -> None:
    payload = _replace(
        profit_protection_policy={"minimum_profit_to_protect": 5000.0},
        compounding_result={"reinvest_amount": 0.0},
        profit_state={"target_type": "OWNER_REVIEW_TARGET"},
    )
    result = _run(payload)
    assert result["status"] == OWNER_REVIEW_REQUIRED


def test_profit_protection_ready_for_clean_positive_profit() -> None:
    payload = _replace(
        profit_protection_policy={"minimum_profit_to_protect": 5000.0},
        compounding_result={"reinvest_amount": 0.0},
    )
    result = _run(payload)
    assert result["status"] == "PROFIT_PROTECTION_READY"


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
    module_path = (
        Path(__file__).resolve().parents[2]
        / "automation"
        / "forex_engine"
        / "forex_profit_protection_and_withdrawal_review_future_v1.py"
    )
    text = module_path.read_text(encoding="utf-8").lower()
    assert [marker for marker in forbidden if marker in text] == []
