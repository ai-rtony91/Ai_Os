from pathlib import Path

from automation.forex_engine.forex_vacation_mode_control_plane_orchestrator_v1 import (
    VACATION_MODE_BLOCKED_BY_RELEASE_SCORECARD,
    VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW,
    evaluate_forex_vacation_mode_control_plane_orchestrator_v1,
)
from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    HARD_FALSE_FIELDS,
)
from automation.forex_engine.forex_vacation_mode_release_candidate_scorecard_v1 import (
    SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW,
    SCORE_AREAS,
)


SOURCE_FILES = (
    "automation/forex_engine/forex_vacation_mode_entry_authority_gate_v1.py",
    "automation/forex_engine/forex_vacation_mode_position_supervisor_v1.py",
    "automation/forex_engine/forex_vacation_mode_exit_authority_gate_v1.py",
    "automation/forex_engine/forex_vacation_mode_owner_handoff_v1.py",
    "automation/forex_engine/forex_vacation_mode_control_plane_orchestrator_v1.py",
    "automation/forex_engine/forex_vacation_mode_release_candidate_scorecard_v1.py",
)


def _entry_payload():
    return {
        "product_policy_state": {
            "policy_docs_present": True,
            "financial_risk_disclosure_present": True,
            "no_profit_guarantee_acknowledged": True,
            "no_passive_income_claim_acknowledged": True,
            "metadata_only_readiness_separated_from_live_authority": True,
            "owner_review_required_before_release": True,
            "play_store_ready_claimed": False,
            "legal_compliance_ready_claimed": False,
            "sell_ready_claimed": False,
            "profit_ready_claimed": False,
        },
        "owner_authority_state": {
            "owner_authority_approved": True,
            "owner_identity_confirmed": True,
            "owner_approval_current": True,
            "one_action_stop_acknowledged": True,
            "repeat_attempt_blocked_until_review": True,
            "live_execution_authorized": False,
            "live_trade_authorized": False,
            "next_trade_authorized": False,
            "repeat_trade_authorized": False,
        },
        "setup_signal_state": {
            "setup_signal_valid": True,
            "entry_review_candidate_present": True,
            "strategy_metadata_present": True,
            "owner_visible_reason_present": True,
        },
        "risk_state": {
            "risk_per_trade_limit_defined": True,
            "daily_loss_limit_defined": True,
            "risk_within_limits": True,
            "stop_loss_ready": True,
            "exit_plan_ready": True,
            "max_loss_visible_to_owner": True,
            "daily_loss_stop_active": False,
            "kill_switch_active": False,
        },
        "market_state": {
            "market_open": True,
            "calendar_ready": True,
            "spread_within_limit": True,
            "supervision_window_ready": True,
        },
        "broker_read_only_state": {
            "metadata_only": True,
            "read_only": True,
            "execution_permission_false": True,
            "execution_permission": False,
            "order_permission": False,
            "close_permission": False,
        },
        "proof_state": {
            "proof_ledger_ready": True,
            "receipt_contract_ready": True,
            "post_action_evidence_plan_ready": True,
            "sanitized_evidence_required": True,
        },
        "safety_policy": {
            "metadata_only": True,
            "no_trade_execution": True,
            "no_broker_call": True,
            "no_oanda_call": True,
            "no_credential_access": True,
            "no_account_identifier_access": True,
            "no_money_movement": True,
            "no_notification_send": True,
            "no_background_runtime": True,
            "trade_execution_allowed": False,
            "broker_call_allowed": False,
            "oanda_call_allowed": False,
        },
    }


def _supervisor_payload():
    return {
        "position_state": {
            "position_metadata_present": True,
            "rule_failure_detected": False,
            "exit_review_required": False,
        },
        "risk_state": {
            "risk_within_limits": True,
            "daily_loss_stop_active": False,
            "max_loss_limit_hit": False,
        },
        "market_state": {"market_state_safe": True},
        "receipt_state": {"receipt_present": True},
        "owner_alert_state": {"owner_alert_required": False},
        "safety_policy": {
            "metadata_only": True,
            "no_trade_alteration": True,
            "no_trade_close": True,
            "no_broker_call": True,
            "no_oanda_call": True,
            "owner_visible_status": True,
            "kill_switch_active": False,
        },
    }


def _exit_payload():
    return {
        "position_state": {"rule_failure_detected": False},
        "exit_signal_state": {
            "take_profit_triggered": False,
            "rule_failure_exit_required": False,
            "owner_exit_review_requested": False,
            "post_exit_receipt_capture_plan_ready": True,
            "owner_visible_reason_present": True,
        },
        "risk_state": {
            "stop_loss_triggered": False,
            "daily_loss_stop_active": False,
            "max_loss_limit_hit": False,
        },
        "market_state": {"market_close_exit_required": False},
        "owner_authority_state": {
            "owner_exit_review_allowed": True,
            "owner_visible_reason_required": True,
            "repeat_attempt_blocked_until_review": True,
        },
        "safety_policy": {
            "metadata_only": True,
            "no_order_close": True,
            "no_broker_call": True,
            "no_oanda_call": True,
            "no_trade_execution": True,
            "kill_switch_active": False,
        },
    }


def _scorecard_payload():
    return {area: {"ready": True, "status": "READY"} for area in SCORE_AREAS}


def _orchestrator_payload():
    return {
        "entry_payload": _entry_payload(),
        "supervisor_payload": _supervisor_payload(),
        "exit_payload": _exit_payload(),
        "scorecard_payload": _scorecard_payload(),
        "owner_alert_state": {"alerting_safe": True, "owner_visible": True},
        "handoff_safety_policy": {
            "metadata_only": True,
            "no_live_execution": True,
            "no_profit_guarantee": True,
            "legal_compliance_not_complete": True,
            "not_play_store_ready": True,
            "not_sell_ready": True,
        },
    }


def test_orchestrator_returns_ready_for_owner_review_when_metadata_complete():
    result = evaluate_forex_vacation_mode_control_plane_orchestrator_v1(
        _orchestrator_payload()
    )

    assert result["status"] == VACATION_MODE_CONTROL_PLANE_READY_FOR_OWNER_REVIEW


def test_orchestrator_blocks_when_final_release_candidate_readiness_is_false():
    payload = _orchestrator_payload()
    payload["scorecard_payload"]["final_release_candidate_readiness"] = {
        "ready": False,
        "status": "BLOCKED",
    }

    result = evaluate_forex_vacation_mode_control_plane_orchestrator_v1(payload)
    scorecard = result["module_results"]["scorecard_result"]

    assert result["status"] == VACATION_MODE_BLOCKED_BY_RELEASE_SCORECARD
    assert result["ready"] is False
    assert scorecard["status"] != SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW
    assert scorecard["final_release_candidate_ready"] is False
    assert "final_release_candidate_readiness" in scorecard["blockers"]


def test_orchestrator_does_not_claim_play_store_ready():
    result = evaluate_forex_vacation_mode_control_plane_orchestrator_v1(
        _orchestrator_payload()
    )

    assert result["play_store_ready_claimed"] is False


def test_orchestrator_does_not_claim_sell_ready():
    result = evaluate_forex_vacation_mode_control_plane_orchestrator_v1(
        _orchestrator_payload()
    )

    assert result["sell_ready_claimed"] is False


def test_all_hard_false_fields_remain_false():
    result = evaluate_forex_vacation_mode_control_plane_orchestrator_v1(
        _orchestrator_payload()
    )

    for field in HARD_FALSE_FIELDS:
        assert result[field] is False


def test_new_source_files_contain_no_blocked_runtime_terms():
    terms = (
        "re" + "quests",
        "so" + "cket",
        "ur" + "llib",
        "sub" + "process",
        "os." + "environ",
        "oan" + "dapy",
        "broker" + "_sdk",
        "schedule" + ".every",
        "start" + "-process",
        "pl" + "aid",
        "str" + "ipe",
        "a" + "ch",
        "wi" + "re",
    )
    root = Path(__file__).resolve().parents[2]

    for file_name in SOURCE_FILES:
        text = (root / file_name).read_text(encoding="utf-8").lower()
        for term in terms:
            assert term not in text
