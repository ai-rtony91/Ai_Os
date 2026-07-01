from __future__ import annotations

from pathlib import Path

from automation.forex_engine import (
    forex_broker_verified_live_profit_proof_milestone_v1 as milestone,
)


def _ready_payload() -> dict:
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


def _result(payload: dict | None = None) -> dict:
    return milestone.evaluate_forex_broker_verified_live_profit_proof_milestone_v1(
        payload
    )


def test_incomplete_inputs_block():
    assert _result({})["status"] == milestone.INCOMPLETE_INPUTS


def test_governance_missing_blocks():
    payload = _ready_payload()
    payload["governance_state"]["risk_policy_read"] = False
    assert _result(payload)["status"] == milestone.BLOCKED_BY_GOVERNANCE


def test_risk_violation_blocks():
    payload = _ready_payload()
    payload["risk_state"]["max_risk_per_trade_pct"] = 0.01
    assert _result(payload)["status"] == milestone.BLOCKED_BY_RISK


def test_market_closed_blocks():
    payload = _ready_payload()
    payload["market_state"]["market_open"] = False
    assert _result(payload)["status"] == milestone.BLOCKED_BY_MARKET_STATE


def test_broker_read_only_missing_blocks():
    payload = _ready_payload()
    payload["broker_read_only_state"]["read_only_mode"] = False
    assert _result(payload)["status"] == milestone.BLOCKED_BY_BROKER_READ_ONLY_STATE


def test_sensitive_broker_account_data_blocks():
    payload = _ready_payload()
    payload["broker_read_only_state"]["account_id"] = "redaction-missing"
    result = _result(payload)
    assert result["status"] == milestone.BLOCKED_BY_BROKER_READ_ONLY_STATE
    assert "redaction-missing" not in str(result)


def test_raw_payload_blocks():
    payload = _ready_payload()
    payload["broker_read_only_state"]["raw_payload"] = {"private": "payload"}
    assert _result(payload)["status"] == milestone.BLOCKED_BY_BROKER_READ_ONLY_STATE


def test_atm_milestone_missing_blocks():
    payload = _ready_payload()
    payload["atm_milestone_state"]["countdown_active"] = False
    assert _result(payload)["status"] == milestone.BLOCKED_BY_ATM_MILESTONE_STATE


def test_owner_not_present_blocks():
    payload = _ready_payload()
    payload["owner_state"]["owner_present"] = False
    assert _result(payload)["status"] == milestone.BLOCKED_BY_OWNER_STATE


def test_owner_final_approval_false_still_permits_review_only_ready_packet():
    result = _result(_ready_payload())
    assert result["status"] == milestone.READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION
    assert result["ready"] is True
    assert result["live_micro_trade_owner_action_required"] is True
    assert result["order_placed"] is False


def test_ready_state_requires_all_clean_gates():
    result = _result(_ready_payload())
    assert result["status"] == milestone.READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION
    assert result["post_live_evidence_required"] is True


def test_all_hard_false_fields_remain_false():
    result = _result(_ready_payload())
    for field in milestone.HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False
        assert result["hard_false_fields"][field] is False


def test_source_contains_no_forbidden_runtime_markers():
    source = Path(milestone.__file__).read_text(encoding="utf-8").lower()
    for marker in (
        "req" + "uests",
        "so" + "cket",
        "url" + "lib",
        "sub" + "process",
        "os." + "environ",
        "oanda" + "py",
        "broker" + "_sdk",
        "schedule" + ".every",
        "start" + "-process",
        "pl" + "aid",
        "str" + "ipe",
        "a" + "ch",
        "w" + "ire",
    ):
        assert marker not in source
