from __future__ import annotations

from automation.forex_engine import forex_demo_receipt_proof_router_v1 as router


def _receipt() -> dict:
    return {
        "receipt_present": True,
        "broker_name": "OANDA",
        "mode": "OANDA_DEMO",
        "demo_order_executed": True,
        "live_trade_executed": False,
        "money_moved": False,
        "order_count": 1,
        "instrument": "EUR_USD",
        "side": "buy",
        "units": 1000,
        "order_id_redacted": True,
        "account_id_redacted": True,
        "credential_values_redacted": True,
        "stop_loss_present": True,
        "take_profit_present": True,
        "execution_timestamp_present": True,
        "receipt_sanitized": True,
    }


def _result(payload: dict | None = None) -> dict:
    return router.evaluate_forex_demo_receipt_proof_router_v1(payload)


def test_empty_payload_is_incomplete():
    result = _result({})
    assert result["status"] == router.INCOMPLETE_INPUTS


def test_valid_receipt_routes_to_post_trade_review():
    result = _result({"receipt": _receipt()})
    assert result["status"] == router.DEMO_RECEIPT_PROOF_ROUTED
    assert result["ready"] is True
    assert result["routed_proof_packet"]["ready_for_post_trade_review"] is True
    assert result["routed_proof_packet"]["receipt_sanitized"] is True


def test_unsanitized_receipt_blocks_routing():
    bad = _receipt()
    bad["receipt_sanitized"] = False
    result = _result({"receipt": bad})
    assert result["status"] == router.BLOCKED_BY_RECEIPT_UNSANITIZED


def test_order_count_more_than_one_blocks():
    bad = _receipt()
    bad["order_count"] = 2
    result = _result({"receipt": bad})
    assert result["status"] == router.BLOCKED_BY_ORDER_COUNT


def test_sensitive_data_is_blocked_without_echo():
    bad = _receipt()
    bad["password"] = "topsecret-password-123"
    result = _result({"receipt": bad})
    rendered = str(result).lower()
    assert result["status"] == router.BLOCKED_BY_SENSITIVE_DATA
    assert "topsecret-password-123" not in rendered


def test_banking_focus_is_blocked():
    bad = _receipt()
    bad["withdrawal"] = "attempt"
    result = _result({"receipt": bad})
    assert result["status"] == router.BLOCKED_BY_BANKING_FOCUS


def test_hard_false_fields_remain_false():
    result = _result({"receipt": _receipt()})
    assert result["status"] == router.DEMO_RECEIPT_PROOF_ROUTED
    for field in (
        "live_trade_executed",
        "live_execution_authorized",
        "demo_trade_executed_by_this_module",
        "broker_api_called",
        "credential_read",
        "credential_stored",
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
        "money_moved",
        "bank_access_used",
        "scheduler_created",
        "daemon_created",
        "webhook_created",
        "dashboard_runtime_created",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
    ):
        assert result[field] is False
        assert result["safety"][field] is False
