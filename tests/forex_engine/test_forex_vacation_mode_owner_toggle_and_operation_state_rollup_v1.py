from pathlib import Path

from automation.forex_engine.forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY,
    VACATION_MODE_OWNER_TOGGLE_BALANCE_REVIEW,
    VACATION_MODE_OWNER_TOGGLE_KILL_SWITCH_STOP,
    VACATION_MODE_OWNER_TOGGLE_MAINTENANCE_READY,
    VACATION_MODE_OWNER_TOGGLE_OFF_READY,
    VACATION_MODE_OWNER_TOGGLE_PAUSED_READY,
    VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_PROOF,
    VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_RECEIPTS,
    evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1,
)
from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import HARD_FALSE_FIELDS


def _payload(
    command="ON",
    posture="ACTIVE_SUPERVISION",
    *,
    proof_ready=True,
    outstanding_receipts=False,
    balance_ready=True,
    context=None,
):
    attention_context = {
        "owner_attention_required": False,
        "severity": "INFO",
        "reason": "Informational state.",
        "next_safe_action": "Continue metadata review.",
        "no_sensitive_values": True,
    }
    if context:
        attention_context.update(context)
    return {
        "owner_command": {
            "command_id": f"CMD-{command}",
            "requested_toggle_state": command,
            "owner_control_required": True,
            "owner_identity_confirmed": True,
            "command_timestamp_present": True,
            "command_source": "OWNER_DASHBOARD",
            "toggle_is_request_only": True,
            "toggle_does_not_authorize_execution": True,
            "toggle_does_not_authorize_withdrawal": True,
            "kill_switch_is_separate": True,
            "no_banking_requested": True,
            "no_credentials_in_command": True,
        },
        "runtime_calendar_result": {
            "status": f"RUNTIME_{posture}",
            "ready": True,
            "current_runtime_posture": posture,
            "primary_job_lane": "supervise_runtime",
            "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
            "close_approaching": posture == "CLOSE_PROTECTION",
            "reopen_approaching": posture == "REOPEN_PREPARATION",
            "vacation_mode_toggle_semantics": {
                "toggle_does_not_authorize_withdrawal": True,
                "toggle_does_not_bypass_market_calendar": True,
                "toggle_does_not_bypass_kill_switch": True,
            },
            "kill_switch_semantics": {"kill_switch_is_not_vacation_mode_toggle": True},
            "runtime_product_fit_summary": {"banking_withdrawal_deferred": True},
        },
        "risk_state": {
            "kill_switch_active": command == "KILL_SWITCH_STOP",
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "max_drawdown_pct": 0.08,
            "current_drawdown_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "current_daily_loss_pct": 0.0,
            "no_new_trade_seeking_if_kill_switch": True,
            "no_new_trade_seeking_if_daily_loss_stop": True,
            "no_new_trade_seeking_if_drawdown_breach": True,
        },
        "proof_state": {
            "proof_required": True,
            "proof_ready": proof_ready,
            "fake_proof_blocked": True,
            "repeatability_review_ready": True,
            "owner_review_required_for_live": True,
        },
        "receipt_state": {
            "receipt_required_after_execution": True,
            "outstanding_receipts": outstanding_receipts,
            "post_trade_review_complete": not outstanding_receipts,
            "next_trade_blocked_until_receipts_reviewed": True,
        },
        "balance_state": {
            "balance_memory_ready": balance_ready,
            "compounding_observer_ready": balance_ready,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
            "money_moved": False,
        },
        "runtime_boundary": {
            "runtime_session_available": True,
            "broker_session_available": True,
            "credential_values_in_payload": False,
            "account_id_in_payload": False,
            "no_stored_credentials": True,
            "broker_call_allowed_by_this_module": False,
            "execute_allowed_by_this_module": False,
        },
        "permission_policy": {
            "may_scan_metadata_when_on": True,
            "may_prepare_candidates_when_on": True,
            "may_prepare_maintenance_when_closed": True,
            "may_prepare_owner_review_when_ready": True,
            "may_execute_live_by_this_module": False,
            "may_execute_demo_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "may_move_money": False,
            "may_withdraw": False,
            "may_bank_route": False,
            "owner_runtime_packet_required_for_execution": True,
        },
        "attention_policy": {
            "dashboard_summary_required": True,
            "owner_visible_reason_required": True,
            "raw_values_echoed": False,
            "sensitive_values_allowed": False,
            "alert_channel_metadata_only": True,
            "no_alert_runtime_created": True,
        },
        "owner_attention_context": attention_context,
    }


def _permission_snapshot(result):
    return result["runtime_permission_summary"]["permission_snapshot"]


def test_on_active_supervision_routes_active_supervision_status_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(_payload())

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY
    assert result["next_best_packet"] == "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"


def test_off_routes_off_ready():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(command="OFF")
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_OFF_READY


def test_pause_routes_paused_ready():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(command="PAUSE")
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_PAUSED_READY


def test_kill_switch_routes_stop_now():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(
            command="KILL_SWITCH_STOP",
            context={
                "owner_attention_required": True,
                "severity": "STOP_NOW",
                "reason": "Kill switch active.",
                "next_safe_action": "Stop new trade seeking.",
            },
        )
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_KILL_SWITCH_STOP
    assert result["owner_attention_summary"]["owner_attention_state"]["severity"] == "STOP_NOW"


def test_market_closed_routes_maintenance_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(posture="CLOSED_MAINTENANCE")
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_MAINTENANCE_READY
    assert result["next_best_packet"] == "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"


def test_close_approaching_routes_close_protection_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(posture="CLOSE_PROTECTION")
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_MAINTENANCE_READY
    assert result["next_best_packet"] == "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1"


def test_reopen_approaching_routes_next_session_prep_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(posture="REOPEN_PREPARATION")
    )

    assert result["next_best_packet"] == "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"


def test_weekend_routes_weekend_maintenance_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(posture="WEEKEND_HEAVY_MAINTENANCE")
    )

    assert result["next_best_packet"] == "AIOS_FOREX_WEEKEND_HEAVY_MAINTENANCE_AND_AUDIT_V1"


def test_proof_missing_routes_proof_pipeline_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(
            proof_ready=False,
            context={
                "owner_attention_required": True,
                "severity": "REVIEW",
                "reason": "Proof missing.",
                "next_safe_action": "Review proof.",
            },
        )
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_PROOF
    assert result["next_best_packet"] == "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1"


def test_receipt_missing_routes_receipt_review_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(
            outstanding_receipts=True,
            context={
                "owner_attention_required": True,
                "severity": "REVIEW",
                "reason": "Receipts missing.",
                "next_safe_action": "Review receipts.",
            },
        )
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_RECEIPTS
    assert result["next_best_packet"] == "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"


def test_balance_review_routes_balance_observer_packet():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
        _payload(
            balance_ready=False,
            context={
                "owner_attention_required": True,
                "severity": "REVIEW",
                "reason": "Balance memory review required.",
                "next_safe_action": "Review balance memory.",
            },
        )
    )

    assert result["campaign_status"] == VACATION_MODE_OWNER_TOGGLE_BALANCE_REVIEW
    assert result["next_best_packet"] == "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"


def test_active_operation_does_not_execute_or_call_broker():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(_payload())

    snapshot = _permission_snapshot(result)
    assert snapshot["may_execute_live_by_this_module"] is False
    assert snapshot["may_call_broker_by_this_module"] is False


def test_vacation_mode_on_does_not_authorize_withdrawal():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(_payload())

    snapshot = _permission_snapshot(result)
    assert snapshot["may_withdraw"] is False
    assert snapshot["may_bank_route"] is False


def test_banking_or_withdrawal_focus_blocks():
    payload = _payload()
    payload["owner_command"]["withdrawal_plan"] = "active"

    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(payload)

    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_close_and_reopen_approaching_do_not_false_positive_banking_block():
    close_payload = _payload(posture="CLOSE_PROTECTION")
    reopen_payload = _payload(posture="REOPEN_PREPARATION")

    close_result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(close_payload)
    reopen_result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(reopen_payload)

    assert close_result["status"] != BLOCKED_BY_BANKING_FOCUS
    assert reopen_result["status"] != BLOCKED_BY_BANKING_FOCUS


def test_all_hard_false_fields_remain_false():
    result = evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(_payload())

    assert all(result[field] is False for field in HARD_FALSE_FIELDS)


def test_production_source_has_no_forbidden_runtime_markers():
    files = [
        Path("automation/forex_engine/forex_vacation_mode_owner_toggle_contract_v1.py"),
        Path("automation/forex_engine/forex_vacation_mode_operation_state_machine_v1.py"),
        Path("automation/forex_engine/forex_vacation_mode_runtime_permission_snapshot_v1.py"),
        Path("automation/forex_engine/forex_vacation_mode_owner_attention_state_v1.py"),
        Path("automation/forex_engine/forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1.py"),
    ]
    forbidden = [
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ]
    hits = {
        str(path): [marker for marker in forbidden if marker in path.read_text(encoding="utf-8").lower()]
        for path in files
    }

    assert not any(hits.values())
