from __future__ import annotations

from pathlib import Path

from automation.forex_engine import forex_proof_pipeline_pause_and_continue_v1 as pipeline


def _base_proof_source() -> dict:
    return {
        "proof_source": {
            "source_type": "OWNER_APPROVED_DEMO_READINESS",
            "upstream_packet_id": "READINESS-READY-001",
            "receipt_present": True,
            "demo_order_executed": True,
            "live_trade_executed": False,
            "money_moved": False,
            "receipt_sanitized": True,
            "raw_broker_payload_present": False,
            "account_id_redacted": True,
            "order_id_redacted": True,
            "credential_values_redacted": True,
            "profit_claimed": False,
        },
        "receipt": {
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
        },
        "post_trade_review": {
            "post_trade_review_required": True,
            "post_trade_review_completed": True,
            "daily_pnl_recorded": True,
            "realized_pnl_present": True,
            "realized_pnl_is_demo": True,
            "spread_slippage_recorded": True,
            "risk_review_recorded": True,
            "owner_review_required": True,
            "no_second_trade_without_review": True,
        },
        "evidence": {
            "sample_count": 20,
            "min_sample_count": 20,
            "expectancy_positive": True,
            "profit_factor": 1.8,
            "min_profit_factor": 1.3,
            "max_drawdown_pct": 0.02,
            "max_allowed_drawdown_pct": 0.03,
            "walk_forward_gate_cleared": True,
            "out_of_sample_passed": True,
            "daily_review_count": 1,
            "weekly_review_count": 1,
            "monthly_review_count": 1,
            "yearly_review_ready": True,
            "guaranteed_profit_claimed": False,
            "fixed_return_promised": False,
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
    return pipeline.evaluate_forex_proof_pipeline_pause_and_continue_v1(payload)


def test_waiting_for_receipt_returns_waiting_status():
    payload = _base_proof_source()
    payload["proof_source"]["demo_order_executed"] = True
    payload["proof_source"]["receipt_present"] = False
    payload["proof_source"]["receipt_sanitized"] = False
    result = _result(payload)
    assert result["campaign_status"] == pipeline.PROOF_DATA_WAITING_FOR_DEMO_RECEIPT
    assert result["proof_data_destination_map"]["no proof"] == pipeline.PROOF_DATA_WAITING_FOR_DEMO_RECEIPT
    assert result["campaign_ready"] is False


def test_ready_for_owner_live_micro_exception_review_routes_chain():
    result = _result(_base_proof_source())
    assert result["campaign_status"] == pipeline.READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW
    assert result["campaign_ready"] is True
    destination_map = result["proof_data_destination_map"]
    assert destination_map["demo receipt -> receipt router"] == "ROUTED"
    assert destination_map["receipt router -> post-trade journal"] == "ROUTED"
    assert destination_map["post-trade journal -> repeatability evidence"] == "READY"
    assert destination_map["repeatability evidence -> live micro gate"] == "READY"
    assert destination_map["live micro gate -> owner live micro exception review packet"] == "READY"


def test_pipeline_preserves_hard_false_fields_when_ready():
    result = _result(_base_proof_source())
    assert result["campaign_status"] == pipeline.READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW
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


def test_sensitive_data_is_blocked_and_not_echoed():
    payload = _base_proof_source()
    payload["proof_source"]["api_key"] = "sk-very-sensitive"
    result = _result(payload)
    rendered = str(result).lower()
    assert result["campaign_status"] == pipeline.BLOCKED_BY_SENSITIVE_DATA
    assert "sk-very-sensitive" not in rendered


def test_banking_focus_is_blocked():
    payload = _base_proof_source()
    payload["receipt"]["bank"] = "acct"
    result = _result(payload)
    assert result["campaign_status"] == pipeline.BLOCKED_BY_BANKING_FOCUS


def test_scan_pipeline_payloads_for_forbidden_runtime_markers():
    files = [
        "automation/forex_engine/forex_proof_data_intake_v1.py",
        "automation/forex_engine/forex_demo_receipt_proof_router_v1.py",
        "automation/forex_engine/forex_post_trade_proof_journal_v1.py",
        "automation/forex_engine/forex_profit_repeatability_evidence_v1.py",
        "automation/forex_engine/forex_proof_to_live_micro_gate_v1.py",
        "automation/forex_engine/forex_proof_pipeline_pause_and_continue_v1.py",
    ]
    forbidden = ["requests", "socket", "urllib", "subprocess", "os.environ", "broker_sdk", "schedule.every", "start-process"]
    for file_path in files:
        text = Path(file_path).read_text(encoding="utf-8").lower()
        assert not any(marker in text for marker in forbidden)
