from __future__ import annotations

from automation.forex_engine import (
    forex_live_micro_trade_owner_final_decision_packet_v1 as packet,
)


def _payload() -> dict:
    return {
        "milestone_result": {
            "status": "READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION",
        },
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


def _result(payload: dict | None = None) -> dict:
    return packet.evaluate_forex_live_micro_trade_owner_final_decision_packet_v1(
        payload
    )


def test_incomplete_inputs_block():
    assert _result({})["status"] == packet.INCOMPLETE_INPUTS


def test_milestone_not_ready_blocks_owner_packet():
    payload = _payload()
    payload["milestone_result"]["status"] = "BLOCKED_BY_RISK"
    assert _result(payload)["status"] == packet.OWNER_PACKET_BLOCKED_BY_MILESTONE


def test_risk_ack_missing_blocks_owner_packet():
    payload = _payload()
    payload["risk_acknowledgement"]["owner_understands_loss_possible"] = False
    assert _result(payload)["status"] == packet.OWNER_PACKET_BLOCKED_BY_RISK_ACK


def test_evidence_plan_missing_blocks_owner_packet():
    payload = _payload()
    payload["evidence_capture_plan"]["exit_receipt_required"] = False
    assert _result(payload)["status"] == packet.OWNER_PACKET_BLOCKED_BY_EVIDENCE_PLAN


def test_safety_policy_missing_blocks_owner_packet():
    payload = _payload()
    payload["safety_policy"]["no_trade_execution"] = False
    assert _result(payload)["status"] == packet.OWNER_PACKET_BLOCKED_BY_SAFETY


def test_owner_packet_ready_review_only_says_codex_did_not_trade():
    result = _result(_payload())
    assert result["status"] == packet.OWNER_PACKET_READY_REVIEW_ONLY
    assert packet.NO_TRADE_STATEMENT in result["no_trade_statement"]
    assert result["order_placed"] is False


def test_all_hard_false_fields_remain_false():
    result = _result(_payload())
    for field in packet.HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False
        assert result["hard_false_fields"][field] is False
