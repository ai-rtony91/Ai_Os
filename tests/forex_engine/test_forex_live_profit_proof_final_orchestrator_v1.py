from __future__ import annotations

from automation.forex_engine import (
    forex_broker_verified_live_profit_proof_milestone_v1 as milestone,
)
from automation.forex_engine import (
    forex_live_profit_proof_final_orchestrator_v1 as orchestrator,
)


def _milestone_payload() -> dict:
    return {
        "governance_state": {
            "risk_policy_read": True,
            "commit_gate_read": True,
            "repo_memory_read": True,
            "protected_action_rules_active": True,
            "live_execution_requires_owner": True,
            "no_autonomous_live_execution": True,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "max_risk_per_trade_pct": 0.005,
            "max_daily_loss_pct": 0.02,
            "stop_loss_required": True,
            "take_profit_or_exit_plan_required": True,
            "one_order_only": True,
            "repeat_without_review_allowed": False,
            "account_protection_priority": True,
        },
        "market_state": {
            "market_open": True,
            "spread_within_limit": True,
            "high_impact_news_block": False,
            "low_liquidity_block": False,
            milestone.FIELD_MARKET_CLOSE_LIMIT: False,
            "weekend_block": False,
            "holiday_block": False,
            "runtime_calendar_ready": True,
            "active_supervision_window": True,
        },
        "broker_read_only_state": {
            milestone.FIELD_BROKER_LINK: True,
            "live_account_label_redacted": True,
            "account_id_absent": True,
            "credentials_absent": True,
            "raw_payload_absent": True,
            "open_positions_reconciled": True,
            "margin_risk_available": True,
            "realized_pl_available": True,
            "unrealized_pl_available": True,
            "daily_pl_available": True,
            "trading_history_available": True,
            "read_only_mode": True,
            "execution_permission": False,
        },
        "proof_state": {
            "demo_or_paper_repeatability_reviewed": True,
            "profit_bucket_logic_ready": True,
            "sos_contract_ready": True,
            "proof_ledger_ready": True,
            "post_trade_review_ready": True,
            "live_receipt_intake_ready": True,
            "exit_receipt_intake_ready": True,
            "pnl_reconciliation_ready": True,
        },
        "atm_milestone_state": {
            "countdown_active": True,
            "sos_contract_ready": True,
            "owner_message_ready": True,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
        },
        "owner_state": {
            "owner_present": True,
            "owner_understands_loss_possible": True,
            "owner_understands_no_profit_guarantee": True,
            "owner_approves_review_packet": True,
            "owner_live_micro_trade_final_approval": False,
        },
        "safety_policy": {
            "metadata_only": True,
            "no_broker_call": True,
            "no_trade_execution": True,
            "no_credential_read": True,
            "no_credential_storage": True,
            "no_account_id_storage": True,
            "no_money_movement": True,
            "no_banking": True,
            "no_withdrawal": True,
            "no_scheduler": True,
            "no_daemon": True,
            "no_webhook": True,
            "no_profit_promise": True,
        },
    }


def _owner_packet_payload() -> dict:
    return {
        "owner_decision_context": {
            "trade_scope": "single_owner_governed_live_micro_trade_review_only",
            "owner_live_micro_trade_final_approval": False,
        },
        "risk_acknowledgement": {
            "owner_understands_loss_possible": True,
            "owner_understands_no_profit_guarantee": True,
            "max_risk_per_trade_pct": 0.005,
            "max_daily_loss_pct": 0.02,
            "stop_loss_required": True,
            "take_profit_or_exit_plan_required": True,
            "one_order_only": True,
            "no_repeat_without_review": True,
            "account_protection_priority": True,
        },
        "evidence_capture_plan": {
            "broker_receipt_required": True,
            "entry_receipt_required": True,
            "exit_receipt_required": True,
            "realized_pnl_required": True,
            "cost_reconciliation_required": True,
            "post_trade_review_required": True,
            "sanitized_receipts_only": True,
            "repeat_attempt_blocked_until_review": True,
            "expected_evidence_after_action": [
                "sanitized_broker_receipt",
                "sanitized_exit_receipt",
                "realized_pnl_after_costs",
                "post_trade_review",
            ],
            "exact_stop_conditions": [
                "after_fill_or_rejection",
                "after_timeout",
                "after_error",
            ],
        },
        "safety_policy": {
            "metadata_only": True,
            "no_broker_call": True,
            "no_trade_execution": True,
            "no_credential_read": True,
            "no_credential_storage": True,
            "no_account_id_storage": True,
            "no_money_movement": True,
            "no_banking": True,
            "no_withdrawal": True,
            "no_scheduler": True,
            "no_daemon": True,
            "no_webhook": True,
            "no_profit_promise": True,
            "review_only": True,
        },
    }


def _receipt_contract_payload() -> dict:
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


def _payload() -> dict:
    return {
        "milestone_payload": _milestone_payload(),
        "owner_packet_payload": _owner_packet_payload(),
        "receipt_contract_payload": _receipt_contract_payload(),
    }


def _result(payload: dict | None = None) -> dict:
    return orchestrator.evaluate_forex_live_profit_proof_final_orchestrator_v1(payload)


def test_incomplete_inputs_block():
    assert _result({})["status"] == orchestrator.INCOMPLETE_INPUTS


def test_orchestrator_returns_final_ready_status():
    result = _result(_payload())
    assert result["status"] == orchestrator.FINAL_MILESTONE_READY_FOR_OWNER_ACTION
    assert result["ready"] is True
    assert result["live_micro_trade_owner_action_required"] is True


def test_orchestrator_maps_governance_blocker():
    payload = _payload()
    payload["milestone_payload"]["governance_state"]["risk_policy_read"] = False
    result = _result(payload)
    assert result["status"] == orchestrator.FINAL_MILESTONE_BLOCKED_BY_GOVERNANCE


def test_orchestrator_maps_receipt_contract_safety_blocker():
    payload = _payload()
    payload["receipt_contract_payload"]["raw_payload"] = {"private": "payload"}
    result = _result(payload)
    assert result["status"] == orchestrator.FINAL_MILESTONE_BLOCKED_BY_SAFETY


def test_all_hard_false_fields_remain_false():
    result = _result(_payload())
    for field in orchestrator.HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False
        assert result["hard_false_fields"][field] is False
