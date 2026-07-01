from __future__ import annotations

from automation.forex_engine import forex_proof_to_live_micro_gate_v1 as gate


def _payload() -> dict:
    return {
        "demo_receipt_review": {
            "demo_receipt_ready": True,
            "post_trade_review_ready": True,
            "demo_order_count": 1,
        },
        "repeatability_evidence": {
            "repeatability_score": 85,
            "expectancy_positive": True,
            "drawdown_within_limit": True,
            "profit_factor_meets_threshold": True,
        },
        "risk": {
            "max_risk_per_trade_pct": 0.005,
            "max_daily_loss_pct": 0.02,
            "kill_switch_ready": True,
            "daily_loss_stop_ready": True,
        },
        "owner": {
            "live_micro_owner_review_required": True,
            "live_execution_authorized": False,
            "live_trade_executed": False,
        },
    }


def _result(payload: dict | None = None) -> dict:
    return gate.evaluate_forex_proof_to_live_micro_gate_v1(payload)


def test_empty_payload_blocks_demo_receipt_required():
    result = _result({})
    assert result["status"] == gate.BLOCKED_BY_DEMO_RECEIPT_REQUIRED

def test_without_demo_evidence_blocks_review():
    result = _result(
        {
            "repeatability_evidence": _payload()["repeatability_evidence"],
            "risk": _payload()["risk"],
            "owner": _payload()["owner"],
        }
    )
    assert result["status"] == gate.BLOCKED_BY_DEMO_RECEIPT_REQUIRED


def test_ready_status_when_gate_inputs_pass():
    result = _result(_payload())
    assert result["status"] == gate.READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW
    assert result["ready"] is True
    assert result["ready_for_live_micro_review"] is True
    assert result["live_micro_review_packet"]["review_only"] is True


def test_sensitive_data_is_blocked():
    payload = _payload()
    payload["owner"]["private_key"] = "-----BEGIN PRIVATE KEY----- example"
    result = _result(payload)
    rendered = str(result).lower()
    assert result["status"] == gate.BLOCKED_BY_SENSITIVE_DATA
    assert "-----begin private key----- example" not in rendered


def test_banking_focus_is_blocked():
    payload = _payload()
    payload["risk"]["wire"] = True
    result = _result(payload)
    assert result["status"] == gate.BLOCKED_BY_BANKING_FOCUS


def test_hard_false_fields_remain_false():
    result = _result(_payload())
    assert result["status"] == gate.READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW
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
