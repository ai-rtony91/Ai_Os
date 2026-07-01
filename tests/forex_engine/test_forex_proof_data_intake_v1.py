from __future__ import annotations

from automation.forex_engine import forex_proof_data_intake_v1 as intake


def _proof_source() -> dict:
    return {
        "source_type": "OWNER_APPROVED_DEMO_READINESS",
        "upstream_packet_id": "AIOS-FROM-READINESS-001",
        "receipt_present": False,
        "demo_order_executed": True,
        "live_trade_executed": False,
        "money_moved": False,
        "receipt_sanitized": False,
        "raw_broker_payload_present": False,
        "account_id_redacted": True,
        "order_id_redacted": True,
        "credential_values_redacted": True,
        "profit_claimed": False,
    }


def _result(payload: dict | None = None) -> dict:
    return intake.evaluate_forex_proof_data_intake_v1(payload)


def test_empty_payload_is_incomplete():
    result = _result({})
    assert result["status"] == intake.INCOMPLETE_INPUTS
    assert "proof_source_missing" in result["blockers"]


def test_readiness_without_receipt_waits_for_demo_receipt():
    result = _result({"proof_source": _proof_source()})
    assert result["status"] == intake.PROOF_DATA_WAITING_FOR_DEMO_RECEIPT
    assert result["proof_data_present"] is False


def test_fake_profit_claim_without_receipt_is_blocked():
    payload = _proof_source()
    payload["source_type"] = "OANDA_DEMO_RECEIPT"
    payload["profit_claimed"] = True
    result = _result({"proof_source": payload})
    assert result["status"] == intake.BLOCKED_BY_FAKE_PROOF_CLAIM
    assert result["proof_data_sanitized"] is False


def test_unsanitized_receipt_is_blocked():
    payload = _proof_source()
    payload["receipt_present"] = True
    payload["receipt_sanitized"] = False
    result = _result({"proof_source": payload})
    assert result["status"] == intake.BLOCKED_BY_UNSANITIZED_PROOF_DATA


def test_ready_receipt_status_from_valid_readiness_input():
    payload = _proof_source()
    payload["receipt_present"] = True
    payload["receipt_sanitized"] = True
    result = _result({"proof_source": payload})
    assert result["status"] == intake.PROOF_DATA_READY_FOR_ROUTING
    assert result["ready"] is True
    assert result["proof_source_summary"]["source_type"] == "OWNER_APPROVED_DEMO_READINESS"


def test_sensitive_data_is_blocked_without_echo():
    payload = _proof_source()
    payload["receipt_present"] = True
    payload["receipt_sanitized"] = True
    payload["api_key"] = "sk-abc-def-12345678"
    result = _result({"proof_source": payload})
    rendered = str(result).lower()
    assert result["status"] == intake.BLOCKED_BY_SENSITIVE_DATA
    assert "sk-abc-def-12345678" not in rendered
    assert "api key" not in rendered


def test_banking_key_is_blocked():
    payload = _proof_source()
    payload["receipt_present"] = True
    payload["receipt_sanitized"] = True
    payload["banking"] = True
    result = _result({"proof_source": payload})
    assert result["status"] == intake.BLOCKED_BY_BANKING_FOCUS


def test_hard_false_fields_remain_false_when_ready():
    payload = _proof_source()
    payload["receipt_present"] = True
    payload["receipt_sanitized"] = True
    result = _result({"proof_source": payload})
    assert result["status"] == intake.PROOF_DATA_READY_FOR_ROUTING
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
