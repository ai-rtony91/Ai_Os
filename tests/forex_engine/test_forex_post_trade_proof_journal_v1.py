from __future__ import annotations

from automation.forex_engine import forex_post_trade_proof_journal_v1 as journal


def _receipt_proof() -> dict:
    return {
        "ready_for_post_trade_review": True,
        "receipt_sanitized": True,
        "demo_order_executed": True,
    }


def _post_trade_review() -> dict:
    return {
        "post_trade_review_required": True,
        "post_trade_review_completed": True,
        "daily_pnl_recorded": True,
        "realized_pnl_present": True,
        "realized_pnl_is_demo": True,
        "spread_slippage_recorded": True,
        "risk_review_recorded": True,
        "owner_review_required": True,
        "no_second_trade_without_review": True,
    }


def _result(payload: dict | None = None) -> dict:
    return journal.evaluate_forex_post_trade_proof_journal_v1(payload)


def test_empty_payload_blocks_review():
    result = _result({})
    assert result["status"] == journal.INCOMPLETE_INPUTS


def test_post_trade_review_missing_blocks():
    result = _result(
        {
            "receipt_proof": _receipt_proof(),
            "post_trade_review": {},
        }
    )
    assert result["status"] == journal.BLOCKED_BY_POST_TRADE_REVIEW
    assert result["proof_data_present"] is True


def test_ready_journal_with_complete_inputs():
    result = _result(
        {
            "receipt_proof": _receipt_proof(),
            "post_trade_review": _post_trade_review(),
        }
    )
    assert result["status"] == journal.POST_TRADE_PROOF_JOURNAL_READY
    assert result["ready"] is True
    assert result["journal_entry"]["demo_trade_reviewed"] is True
    assert result["journal_entry"]["no_live_trade_authorized"] is True


def test_sensitive_data_is_blocked_without_echo():
    payload = {
        "receipt_proof": _receipt_proof(),
        "post_trade_review": _post_trade_review(),
        "api_key": "sk-very-sensitive",
    }
    result = _result(payload)
    rendered = str(result).lower()
    assert result["status"] == journal.BLOCKED_BY_SENSITIVE_DATA
    assert "sk-very-sensitive" not in rendered


def test_banking_focus_is_blocked():
    payload = {
        "receipt_proof": _receipt_proof(),
        "post_trade_review": _post_trade_review(),
    }
    payload["wire"] = "disallowed"
    result = _result(payload)
    assert result["status"] == journal.BLOCKED_BY_BANKING_FOCUS


def test_hard_false_fields_remain_false():
    result = _result(
        {
            "receipt_proof": _receipt_proof(),
            "post_trade_review": _post_trade_review(),
        }
    )
    assert result["status"] == journal.POST_TRADE_PROOF_JOURNAL_READY
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
