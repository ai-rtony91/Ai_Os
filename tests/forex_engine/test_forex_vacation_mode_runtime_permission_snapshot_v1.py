from automation.forex_engine.forex_vacation_mode_operation_state_machine_v1 import (
    VACATION_MODE_KILL_SWITCH_STOP,
    VACATION_MODE_OFF_IDLE,
    VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE,
    VACATION_MODE_ON_CLOSED_MAINTENANCE,
    VACATION_MODE_PAUSED,
    VACATION_MODE_WAITING_FOR_PROOF,
    VACATION_MODE_WAITING_FOR_RECEIPTS,
)
from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import HARD_FALSE_FIELDS
from automation.forex_engine.forex_vacation_mode_runtime_permission_snapshot_v1 import (
    VACATION_MODE_RUNTIME_PERMISSION_BLOCKED,
    VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY,
    VACATION_MODE_RUNTIME_PERMISSION_OFF,
    VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED,
    VACATION_MODE_RUNTIME_PERMISSION_PAUSED,
    VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY,
    evaluate_forex_vacation_mode_runtime_permission_snapshot_v1,
)


def _operation_state(state):
    toggle = "OFF" if state == VACATION_MODE_OFF_IDLE else "PAUSED" if state == VACATION_MODE_PAUSED else "ON"
    return {
        "status": state,
        "ready": True,
        "owner_decision_required": True,
        "vacation_mode_requested": toggle != "OFF",
        "vacation_mode_toggle_state": toggle,
        "vacation_mode_operation_state": state,
        "kill_switch_active": state == VACATION_MODE_KILL_SWITCH_STOP,
        "new_trade_seeking_allowed_by_this_module": state == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE,
        "maintenance_allowed_by_this_module": state == VACATION_MODE_ON_CLOSED_MAINTENANCE,
        "operation_state": {"vacation_mode_operation_state": state},
    }


def _payload(state):
    return {
        "operation_state_result": _operation_state(state),
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
    }


def test_off_returns_permission_off():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_OFF_IDLE)
    )

    assert result["status"] == VACATION_MODE_RUNTIME_PERMISSION_OFF
    assert result["permission_snapshot"]["may_scan_metadata"] is False


def test_paused_returns_permission_paused():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_PAUSED)
    )

    assert result["status"] == VACATION_MODE_RUNTIME_PERMISSION_PAUSED


def test_kill_switch_stop_blocks():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_KILL_SWITCH_STOP)
    )

    assert result["status"] == VACATION_MODE_RUNTIME_PERMISSION_BLOCKED
    assert result["permission_snapshot"]["may_scan_metadata"] is False


def test_maintenance_state_allows_maintenance_only():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_ON_CLOSED_MAINTENANCE)
    )

    assert result["status"] == VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY
    assert result["permission_snapshot"]["may_prepare_maintenance_work"] is True
    assert result["permission_snapshot"]["may_prepare_candidates"] is False


def test_active_supervision_ready_allows_metadata_but_not_execution():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE)
    )

    snapshot = result["permission_snapshot"]
    assert result["status"] == VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY
    assert snapshot["may_scan_metadata"] is True
    assert snapshot["may_prepare_candidates"] is True
    assert snapshot["may_execute_live_by_this_module"] is False
    assert snapshot["may_call_broker_by_this_module"] is False


def test_waiting_proof_routes_owner_review_required():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_WAITING_FOR_PROOF)
    )

    assert result["status"] == VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED


def test_waiting_receipts_routes_owner_review_required():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_WAITING_FOR_RECEIPTS)
    )

    assert result["status"] == VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED


def test_execution_broker_money_withdraw_and_bank_route_false_always():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE)
    )

    snapshot = result["permission_snapshot"]
    assert snapshot["may_execute_live_by_this_module"] is False
    assert snapshot["may_call_broker_by_this_module"] is False
    assert snapshot["may_move_money"] is False
    assert snapshot["may_withdraw"] is False
    assert snapshot["may_bank_route"] is False


def test_all_hard_false_fields_remain_false():
    result = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        _payload(VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE)
    )

    assert all(result[field] is False for field in HARD_FALSE_FIELDS)
