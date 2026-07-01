from automation.forex_engine.forex_vacation_mode_operation_state_machine_v1 import (
    BLOCKED_BY_RISK_STATE,
    VACATION_MODE_BALANCE_MEMORY_REVIEW,
    VACATION_MODE_KILL_SWITCH_STOP,
    VACATION_MODE_OFF_IDLE,
    VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE,
    VACATION_MODE_ON_CLOSE_PROTECTION,
    VACATION_MODE_ON_CLOSED_MAINTENANCE,
    VACATION_MODE_ON_DEGRADED_MAINTENANCE,
    VACATION_MODE_ON_REOPEN_PREPARATION,
    VACATION_MODE_ON_WEEKEND_MAINTENANCE,
    VACATION_MODE_PAUSED,
    VACATION_MODE_WAITING_FOR_PROOF,
    VACATION_MODE_WAITING_FOR_RECEIPTS,
    evaluate_forex_vacation_mode_operation_state_machine_v1,
)
from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import (
    evaluate_forex_vacation_mode_owner_toggle_contract_v1,
)


def _owner_toggle(command="ON"):
    return evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        {
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
            }
        }
    )


def _calendar(posture="ACTIVE_SUPERVISION"):
    return {
        "status": f"RUNTIME_{posture}",
        "ready": True,
        "current_runtime_posture": posture,
        "primary_job_lane": "supervise_runtime",
        "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
        "vacation_mode_toggle_semantics": {"toggle_does_not_authorize_withdrawal": True},
        "kill_switch_semantics": {"kill_switch_is_not_vacation_mode_toggle": True},
    }


def _payload(command="ON", posture="ACTIVE_SUPERVISION", **section_overrides):
    payload = {
        "owner_toggle_result": _owner_toggle(command),
        "runtime_calendar_result": _calendar(posture),
        "risk_state": {
            "kill_switch_active": False,
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
            "proof_ready": True,
            "fake_proof_blocked": True,
            "repeatability_review_ready": True,
            "owner_review_required_for_live": True,
        },
        "receipt_state": {
            "receipt_required_after_execution": True,
            "outstanding_receipts": False,
            "post_trade_review_complete": True,
            "next_trade_blocked_until_receipts_reviewed": True,
        },
        "balance_state": {
            "balance_memory_ready": True,
            "compounding_observer_ready": True,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
            "money_moved": False,
        },
    }
    for section, updates in section_overrides.items():
        payload[section].update(updates)
    return payload


def test_off_routes_idle():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(_payload(command="OFF"))

    assert result["status"] == VACATION_MODE_OFF_IDLE


def test_pause_routes_paused():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(_payload(command="PAUSE"))

    assert result["status"] == VACATION_MODE_PAUSED


def test_kill_switch_stop_routes_kill_switch_stop():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(command="KILL_SWITCH_STOP")
    )

    assert result["status"] == VACATION_MODE_KILL_SWITCH_STOP


def test_kill_switch_active_true_routes_kill_switch_stop():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(risk_state={"kill_switch_active": True})
    )

    assert result["status"] == VACATION_MODE_KILL_SWITCH_STOP


def test_daily_loss_stop_blocks():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(risk_state={"daily_loss_stop_active": True})
    )

    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_drawdown_breach_blocks():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(risk_state={"drawdown_within_limit": False})
    )

    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_proof_missing_routes_waiting_proof():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(proof_state={"proof_ready": False})
    )

    assert result["status"] == VACATION_MODE_WAITING_FOR_PROOF


def test_outstanding_receipts_routes_waiting_receipts():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(receipt_state={"outstanding_receipts": True})
    )

    assert result["status"] == VACATION_MODE_WAITING_FOR_RECEIPTS


def test_balance_memory_missing_routes_balance_review():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(balance_state={"balance_memory_ready": False})
    )

    assert result["status"] == VACATION_MODE_BALANCE_MEMORY_REVIEW


def test_active_supervision_routes_active_supervision_eligible():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(_payload())

    assert result["status"] == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE
    assert result["new_trade_seeking_allowed_by_this_module"] is True


def test_close_protection_routes_close_protection():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(posture="CLOSE_PROTECTION")
    )

    assert result["status"] == VACATION_MODE_ON_CLOSE_PROTECTION


def test_closed_maintenance_routes_closed_maintenance():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(posture="CLOSED_MAINTENANCE")
    )

    assert result["status"] == VACATION_MODE_ON_CLOSED_MAINTENANCE


def test_reopen_preparation_routes_reopen_preparation():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(posture="REOPEN_PREPARATION")
    )

    assert result["status"] == VACATION_MODE_ON_REOPEN_PREPARATION


def test_weekend_heavy_maintenance_routes_weekend_maintenance():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(posture="WEEKEND_HEAVY_MAINTENANCE")
    )

    assert result["status"] == VACATION_MODE_ON_WEEKEND_MAINTENANCE


def test_degraded_routes_degraded_maintenance():
    result = evaluate_forex_vacation_mode_operation_state_machine_v1(
        _payload(posture="LOW_LIQUIDITY_MAINTENANCE")
    )

    assert result["status"] == VACATION_MODE_ON_DEGRADED_MAINTENANCE
