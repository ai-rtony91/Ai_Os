from __future__ import annotations

import pytest

from automation.forex_engine import (
    forex_live_receipt_evidence_intake_contract_v1 as contract,
)


def _contract_payload() -> dict:
    return {
        "contract_only": True,
        "contract_acknowledged": True,
        "sanitized_evidence_only": True,
        "repeat_attempt_allowed": False,
        "account_id_absent": True,
        "order_id_absent_or_redacted": True,
        "transaction_id_absent_or_redacted": True,
        "credentials_absent": True,
        "raw_payload_absent": True,
        "screenshot_private_data_absent": True,
    }


def _evidence_payload() -> dict:
    return {
        "attempt_id_redacted": True,
        "broker_receipt_present": True,
        "entry_timestamp_utc": "2026-07-01T14:00:00Z",
        "instrument": "EUR_USD",
        "side": "buy",
        "units_or_size_redacted": True,
        "entry_price_present": True,
        "stop_loss_present": True,
        "take_profit_or_exit_plan_present": True,
        "exit_receipt_present": True,
        "exit_timestamp_utc": "2026-07-01T14:10:00Z",
        "exit_price_present": True,
        "realized_pnl_present": True,
        "realized_pnl_value": 1.23,
        "pnl_currency": "USD",
        "spread_cost_recorded": True,
        "fee_cost_recorded": True,
        "slippage_recorded": True,
        "net_pnl_after_costs": 1.01,
        "post_trade_review_complete": True,
        "rule_followed_classified": True,
        "mistake_classified": True,
        "repeat_attempt_allowed": False,
        "account_id_absent": True,
        "order_id_absent_or_redacted": True,
        "transaction_id_absent_or_redacted": True,
        "credentials_absent": True,
        "raw_payload_absent": True,
        "screenshot_private_data_absent": True,
    }


def _result(payload: dict | None = None) -> dict:
    return contract.evaluate_forex_live_receipt_evidence_intake_contract_v1(payload)


def test_incomplete_inputs_block():
    assert _result({})["status"] == contract.INCOMPLETE_INPUTS


def test_contract_ready_without_fabricating_evidence():
    result = _result(_contract_payload())
    assert result["status"] == contract.LIVE_RECEIPT_EVIDENCE_CONTRACT_READY
    assert result["ready"] is True


def test_complete_evidence_is_accepted():
    result = _result(_evidence_payload())
    assert result["status"] == contract.LIVE_RECEIPT_EVIDENCE_COMPLETE
    assert result["ready"] is True


def test_broker_receipt_required():
    payload = _evidence_payload()
    payload["broker_receipt_present"] = False
    assert _result(payload)["status"] == contract.BLOCKED_BY_MISSING_BROKER_RECEIPT


def test_exit_receipt_required():
    payload = _evidence_payload()
    payload["exit_receipt_present"] = False
    assert _result(payload)["status"] == contract.BLOCKED_BY_MISSING_EXIT_RECEIPT


def test_realized_pnl_required():
    payload = _evidence_payload()
    payload["realized_pnl_present"] = False
    assert _result(payload)["status"] == contract.BLOCKED_BY_MISSING_REALIZED_PNL


def test_cost_reconciliation_required():
    payload = _evidence_payload()
    payload["spread_cost_recorded"] = False
    assert _result(payload)["status"] == contract.BLOCKED_BY_MISSING_COST_RECONCILIATION


def test_post_trade_review_required():
    payload = _evidence_payload()
    payload["post_trade_review_complete"] = False
    assert _result(payload)["status"] == contract.BLOCKED_BY_MISSING_POST_TRADE_REVIEW


@pytest.mark.parametrize(
    ("field", "value", "expected_status", "forbidden_snippet"),
    (
        (
            "account_id",
            "unredacted-account",
            contract.BLOCKED_BY_SENSITIVE_DATA,
            "unredacted-account",
        ),
        ("api_key", "sk-sensitive", contract.BLOCKED_BY_SENSITIVE_DATA, "sk-sensitive"),
        ("token", "token-value", contract.BLOCKED_BY_SENSITIVE_DATA, "token-value"),
        (
            "secret",
            "secret-value-no-echo",
            contract.BLOCKED_BY_SENSITIVE_DATA,
            "secret-value-no-echo",
        ),
        (
            "credential",
            "credential-value-no-echo",
            contract.BLOCKED_BY_SENSITIVE_DATA,
            "credential-value-no-echo",
        ),
        (
            "raw_payload",
            {"private_marker": "payload-value-no-echo"},
            contract.BLOCKED_BY_RAW_PAYLOAD,
            "payload-value-no-echo",
        ),
    ),
)
def test_sensitive_and_raw_fields_are_rejected(
    field: str, value: object, expected_status: str, forbidden_snippet: str
):
    payload = _contract_payload()
    payload[field] = value
    result = _result(payload)
    assert result["status"] == expected_status
    assert forbidden_snippet not in str(result)


def test_all_hard_false_fields_remain_false():
    result = _result(_evidence_payload())
    for field in contract.HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False
        assert result["hard_false_fields"][field] is False
