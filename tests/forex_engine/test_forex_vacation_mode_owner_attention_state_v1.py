from automation.forex_engine.forex_vacation_mode_owner_attention_state_v1 import (
    BLOCKED_BY_MISSING_OWNER_REASON,
    VACATION_MODE_OWNER_ATTENTION_NOT_REQUIRED,
    VACATION_MODE_OWNER_ATTENTION_REQUIRED,
    VACATION_MODE_OWNER_STOP_NOW_REQUIRED,
    evaluate_forex_vacation_mode_owner_attention_state_v1,
)


def _permission_snapshot(operation_state="VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE"):
    return {
        "status": "VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY",
        "ready": True,
        "owner_decision_required": True,
        "vacation_mode_requested": True,
        "vacation_mode_toggle_state": "ON",
        "vacation_mode_operation_state": operation_state,
        "kill_switch_active": operation_state == "VACATION_MODE_KILL_SWITCH_STOP",
        "new_trade_seeking_allowed_by_this_module": operation_state
        == "VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE",
        "maintenance_allowed_by_this_module": False,
        "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
        "safe_manual_next_action": "Continue metadata review.",
        "permission_snapshot": {
            "may_scan_metadata": operation_state == "VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE",
            "may_execute_live_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "may_move_money": False,
            "may_withdraw": False,
            "may_bank_route": False,
        },
    }


def _payload(operation_state="VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE", **context_overrides):
    context = {
        "owner_attention_required": False,
        "severity": "INFO",
        "reason": "Informational state.",
        "next_safe_action": "Continue metadata review.",
        "no_sensitive_values": True,
    }
    context.update(context_overrides)
    return {
        "permission_snapshot_result": _permission_snapshot(operation_state),
        "attention_policy": {
            "dashboard_summary_required": True,
            "owner_visible_reason_required": True,
            "raw_values_echoed": False,
            "sensitive_values_allowed": False,
            "alert_channel_metadata_only": True,
            "no_alert_runtime_created": True,
        },
        "owner_attention_context": context,
    }


def test_normal_active_supervision_returns_info_no_stop():
    result = evaluate_forex_vacation_mode_owner_attention_state_v1(_payload())

    assert result["status"] == VACATION_MODE_OWNER_ATTENTION_NOT_REQUIRED
    assert result["owner_attention_state"]["severity"] == "INFO"
    assert result["owner_attention_required"] is False


def test_waiting_proof_returns_review():
    result = evaluate_forex_vacation_mode_owner_attention_state_v1(
        _payload(
            "VACATION_MODE_WAITING_FOR_PROOF",
            owner_attention_required=True,
            severity="REVIEW",
            reason="Proof missing.",
        )
    )

    assert result["status"] == VACATION_MODE_OWNER_ATTENTION_REQUIRED
    assert result["owner_attention_state"]["severity"] == "REVIEW"


def test_waiting_receipts_returns_review():
    result = evaluate_forex_vacation_mode_owner_attention_state_v1(
        _payload(
            "VACATION_MODE_WAITING_FOR_RECEIPTS",
            owner_attention_required=True,
            severity="REVIEW",
            reason="Receipts missing.",
        )
    )

    assert result["status"] == VACATION_MODE_OWNER_ATTENTION_REQUIRED


def test_kill_switch_returns_stop_now():
    result = evaluate_forex_vacation_mode_owner_attention_state_v1(
        _payload(
            "VACATION_MODE_KILL_SWITCH_STOP",
            owner_attention_required=True,
            severity="STOP_NOW",
            reason="Kill switch active.",
            next_safe_action="Stop new trade seeking.",
        )
    )

    assert result["status"] == VACATION_MODE_OWNER_STOP_NOW_REQUIRED
    assert result["owner_attention_state"]["severity"] == "STOP_NOW"


def test_missing_reason_blocks_when_attention_required():
    payload = _payload(owner_attention_required=True, severity="REVIEW", reason="")

    result = evaluate_forex_vacation_mode_owner_attention_state_v1(payload)

    assert result["status"] == BLOCKED_BY_MISSING_OWNER_REASON


def test_raw_values_echoed_false_and_no_alert_runtime_created():
    result = evaluate_forex_vacation_mode_owner_attention_state_v1(_payload())

    assert result["owner_attention_state"]["raw_values_echoed"] is False
    assert result["owner_attention_state"]["no_alert_runtime_created"] is True
