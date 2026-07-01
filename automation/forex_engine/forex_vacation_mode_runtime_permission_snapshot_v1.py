"""Convert Vacation Mode operation state into metadata-only permission flags."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_operation_state_machine_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
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
)
from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import (
    build_common_result,
    banking_focus_blockers,
    sensitive_data_blockers,
    _bool,
    _mapping,
    _unique,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT"

VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY = "VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY"
VACATION_MODE_RUNTIME_PERMISSION_OFF = "VACATION_MODE_RUNTIME_PERMISSION_OFF"
VACATION_MODE_RUNTIME_PERMISSION_PAUSED = "VACATION_MODE_RUNTIME_PERMISSION_PAUSED"
VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY = "VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY"
VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED = (
    "VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED"
)
VACATION_MODE_RUNTIME_PERMISSION_BLOCKED = "VACATION_MODE_RUNTIME_PERMISSION_BLOCKED"
BLOCKED_BY_OPERATION_STATE = "BLOCKED_BY_OPERATION_STATE"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"

RUNTIME_BOUNDARY_FIELDS = (
    "runtime_session_available",
    "broker_session_available",
    "credential_values_in_payload",
    "account_id_in_payload",
    "no_stored_credentials",
    "broker_call_allowed_by_this_module",
    "execute_allowed_by_this_module",
)

PERMISSION_POLICY_FIELDS = (
    "may_scan_metadata_when_on",
    "may_prepare_candidates_when_on",
    "may_prepare_maintenance_when_closed",
    "may_prepare_owner_review_when_ready",
    "may_execute_live_by_this_module",
    "may_execute_demo_by_this_module",
    "may_call_broker_by_this_module",
    "may_move_money",
    "may_withdraw",
    "may_bank_route",
    "owner_runtime_packet_required_for_execution",
)

MAINTENANCE_STATES = frozenset(
    {
        VACATION_MODE_ON_CLOSED_MAINTENANCE,
        VACATION_MODE_ON_CLOSE_PROTECTION,
        VACATION_MODE_ON_REOPEN_PREPARATION,
        VACATION_MODE_ON_WEEKEND_MAINTENANCE,
        VACATION_MODE_ON_DEGRADED_MAINTENANCE,
    }
)

OWNER_REVIEW_STATES = frozenset(
    {
        VACATION_MODE_WAITING_FOR_PROOF,
        VACATION_MODE_WAITING_FOR_RECEIPTS,
        VACATION_MODE_BALANCE_MEMORY_REVIEW,
    }
)


def evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return explicit permission flags while keeping execution false."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _permission_result(source, BLOCKED_BY_SENSITIVE_DATA, False, sensitive_blockers)
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _permission_result(source, BLOCKED_BY_BANKING_FOCUS, False, banking_blockers)
    if not source:
        return _permission_result(source, INCOMPLETE_INPUTS, False, ("payload_missing",))

    operation_result = _mapping(source.get("operation_state_result"))
    runtime_boundary = _mapping(source.get("runtime_boundary"))
    permission_policy = _mapping(source.get("permission_policy"))
    if not operation_result:
        return _permission_result(source, INCOMPLETE_INPUTS, False, ("operation_state_result_missing",))
    if not runtime_boundary:
        return _permission_result(source, INCOMPLETE_INPUTS, False, ("runtime_boundary_missing",))
    if not permission_policy:
        return _permission_result(source, INCOMPLETE_INPUTS, False, ("permission_policy_missing",))

    missing = (
        *_missing_fields(runtime_boundary, RUNTIME_BOUNDARY_FIELDS, "runtime_boundary"),
        *_missing_fields(permission_policy, PERMISSION_POLICY_FIELDS, "permission_policy"),
    )
    if missing:
        return _permission_result(source, INCOMPLETE_INPUTS, False, missing)
    if not _mapping(operation_result.get("operation_state")):
        return _permission_result(source, BLOCKED_BY_OPERATION_STATE, False, ("operation_state_missing",))

    boundary_blockers = _runtime_boundary_blockers(runtime_boundary)
    policy_blockers = _permission_policy_blockers(permission_policy)
    if boundary_blockers or policy_blockers:
        return _permission_result(
            source,
            BLOCKED_BY_OPERATION_STATE,
            False,
            (*boundary_blockers, *policy_blockers),
        )

    operation_state = str(operation_result.get("vacation_mode_operation_state", ""))
    if operation_state == VACATION_MODE_OFF_IDLE:
        status = VACATION_MODE_RUNTIME_PERMISSION_OFF
    elif operation_state == VACATION_MODE_PAUSED:
        status = VACATION_MODE_RUNTIME_PERMISSION_PAUSED
    elif operation_state == VACATION_MODE_KILL_SWITCH_STOP:
        status = VACATION_MODE_RUNTIME_PERMISSION_BLOCKED
    elif operation_state in MAINTENANCE_STATES:
        status = VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY
    elif operation_state == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE:
        status = VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY
    elif operation_state in OWNER_REVIEW_STATES:
        status = VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED
    else:
        status = BLOCKED_BY_OPERATION_STATE

    ready = status != BLOCKED_BY_OPERATION_STATE
    blockers: tuple[str, ...] = () if ready else ("operation_state_unsupported",)
    return _permission_result(source, status, ready, blockers)


def _permission_result(
    source: Mapping[str, Any],
    status: str,
    ready: bool,
    blockers: Sequence[str],
) -> dict[str, Any]:
    operation_result = _mapping(source.get("operation_state_result"))
    operation_state = str(operation_result.get("vacation_mode_operation_state", "UNKNOWN"))
    toggle_state = str(operation_result.get("vacation_mode_toggle_state", "UNKNOWN"))
    permission_snapshot = _permission_snapshot(status, operation_state, _mapping(source.get("permission_policy")))
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=ready,
        vacation_mode_requested=_bool(operation_result.get("vacation_mode_requested")),
        vacation_mode_toggle_state=toggle_state,
        vacation_mode_operation_state=operation_state,
        kill_switch_active=_bool(operation_result.get("kill_switch_active")),
        new_trade_seeking_allowed_by_this_module=permission_snapshot["may_scan_metadata"]
        and operation_state == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE,
        maintenance_allowed_by_this_module=permission_snapshot["may_prepare_maintenance_work"],
        owner_attention_required=status
        in {
            VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED,
            VACATION_MODE_RUNTIME_PERMISSION_BLOCKED,
            BLOCKED_BY_OPERATION_STATE,
        },
        blockers=blockers,
        next_best_packet=_next_packet(status, operation_state),
        safe_manual_next_action=_safe_manual_next_action(status, operation_state),
        extra={"permission_snapshot": permission_snapshot},
    )


def _permission_snapshot(
    status: str,
    operation_state: str,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    active = status == VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY
    maintenance = status == VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY
    owner_review = status == VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED
    return {
        "may_scan_metadata": active and _bool(policy.get("may_scan_metadata_when_on")),
        "may_prepare_candidates": active and _bool(policy.get("may_prepare_candidates_when_on")),
        "may_prepare_demo_runtime_intent_metadata": active,
        "may_prepare_live_owner_review_metadata": active or owner_review,
        "may_prepare_maintenance_work": maintenance and _bool(policy.get("may_prepare_maintenance_when_closed")),
        "may_prepare_receipt_review": operation_state == VACATION_MODE_WAITING_FOR_RECEIPTS,
        "may_prepare_balance_learning_review": operation_state == VACATION_MODE_BALANCE_MEMORY_REVIEW,
        "may_execute_demo_by_this_module": False,
        "may_execute_live_by_this_module": False,
        "may_call_broker_by_this_module": False,
        "may_read_credentials_by_this_module": False,
        "may_move_money": False,
        "may_withdraw": False,
        "may_bank_route": False,
        "owner_runtime_packet_required_for_execution": True,
        "permission_reason": _permission_reason(status, operation_state),
        "blocked_actions": (
            "live_trade_execution_by_this_module",
            "demo_trade_execution_by_this_module",
            "broker_call_by_this_module",
            "credential_read_by_this_module",
            "money_movement_by_this_module",
            "withdrawal_by_this_module",
            "bank_route_by_this_module",
        ),
    }


def _runtime_boundary_blockers(runtime_boundary: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if runtime_boundary.get("credential_values_in_payload") is not False:
        blockers.append("credential_values_in_payload_not_false")
    if runtime_boundary.get("account_id_in_payload") is not False:
        blockers.append("account_id_in_payload_not_false")
    if not _bool(runtime_boundary.get("no_stored_credentials")):
        blockers.append("no_stored_credentials_false")
    if runtime_boundary.get("broker_call_allowed_by_this_module") is not False:
        blockers.append("broker_call_allowed_by_this_module_not_false")
    if runtime_boundary.get("execute_allowed_by_this_module") is not False:
        blockers.append("execute_allowed_by_this_module_not_false")
    return tuple(_unique(blockers))


def _permission_policy_blockers(permission_policy: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    true_required = (
        "may_scan_metadata_when_on",
        "may_prepare_candidates_when_on",
        "may_prepare_maintenance_when_closed",
        "may_prepare_owner_review_when_ready",
        "owner_runtime_packet_required_for_execution",
    )
    false_required = (
        "may_execute_live_by_this_module",
        "may_execute_demo_by_this_module",
        "may_call_broker_by_this_module",
        "may_move_money",
        "may_withdraw",
        "may_bank_route",
    )
    blockers.extend(f"{field}_false" for field in true_required if not _bool(permission_policy.get(field)))
    blockers.extend(f"{field}_not_false" for field in false_required if permission_policy.get(field) is not False)
    return tuple(_unique(blockers))


def _missing_fields(source: Mapping[str, Any], fields: Sequence[str], prefix: str) -> tuple[str, ...]:
    return tuple(f"missing_{prefix}_{field}" for field in fields if field not in source)


def _permission_reason(status: str, operation_state: str) -> str:
    if status == VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY:
        return "Active supervision metadata preparation is allowed; execution remains false."
    if status == VACATION_MODE_RUNTIME_PERMISSION_OFF:
        return "Vacation Mode is off; new trade seeking is stopped."
    if status == VACATION_MODE_RUNTIME_PERMISSION_PAUSED:
        return "Vacation Mode is paused; new trade seeking is held."
    if status == VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY:
        return "Current operation state allows maintenance or preparation work only."
    if status == VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED:
        return f"{operation_state} requires owner review metadata before new trade seeking."
    if status == VACATION_MODE_RUNTIME_PERMISSION_BLOCKED:
        return "Kill switch or hard stop state blocks new trade seeking."
    return "Operation state does not grant runtime permission metadata."


def _next_packet(status: str, operation_state: str) -> str:
    if status == VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY:
        return "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
    if status == VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY:
        if operation_state == VACATION_MODE_ON_CLOSE_PROTECTION:
            return "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1"
        if operation_state == VACATION_MODE_ON_REOPEN_PREPARATION:
            return "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"
        if operation_state == VACATION_MODE_ON_WEEKEND_MAINTENANCE:
            return "AIOS_FOREX_WEEKEND_HEAVY_MAINTENANCE_AND_AUDIT_V1"
        return "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
    if operation_state == VACATION_MODE_WAITING_FOR_PROOF:
        return "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1"
    if operation_state == VACATION_MODE_WAITING_FOR_RECEIPTS:
        return "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
    if operation_state == VACATION_MODE_BALANCE_MEMORY_REVIEW:
        return "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"
    return NEXT_BEST_PACKET


def _safe_manual_next_action(status: str, operation_state: str) -> str:
    if status == VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY:
        return "Prepare metadata-only active supervision; owner runtime packet is still required for execution."
    if status == VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY:
        return "Prepare safe maintenance work for the current calendar posture."
    if status == VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED:
        return f"Resolve {operation_state} before new trade seeking."
    if status == VACATION_MODE_RUNTIME_PERMISSION_BLOCKED:
        return "Keep new trade seeking stopped and route owner attention."
    if status == VACATION_MODE_RUNTIME_PERMISSION_OFF:
        return "Keep Vacation Mode idle until owner turns it on."
    if status == VACATION_MODE_RUNTIME_PERMISSION_PAUSED:
        return "Hold new trade seeking until owner resumes and gates recheck."
    return "Correct operation state metadata before permission review."


__all__ = [
    "VACATION_MODE_RUNTIME_PERMISSION_SNAPSHOT_READY",
    "VACATION_MODE_RUNTIME_PERMISSION_OFF",
    "VACATION_MODE_RUNTIME_PERMISSION_PAUSED",
    "VACATION_MODE_RUNTIME_PERMISSION_MAINTENANCE_ONLY",
    "VACATION_MODE_RUNTIME_PERMISSION_OWNER_REVIEW_REQUIRED",
    "VACATION_MODE_RUNTIME_PERMISSION_BLOCKED",
    "BLOCKED_BY_BANKING_FOCUS",
    "BLOCKED_BY_SENSITIVE_DATA",
    "evaluate_forex_vacation_mode_runtime_permission_snapshot_v1",
]
