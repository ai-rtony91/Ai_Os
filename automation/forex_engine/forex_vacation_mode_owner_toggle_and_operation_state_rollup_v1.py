"""Roll up Vacation Mode owner toggle, operation state, permission, and attention."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_operation_state_machine_v1 import (
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
from automation.forex_engine.forex_vacation_mode_owner_attention_state_v1 import (
    evaluate_forex_vacation_mode_owner_attention_state_v1,
)
from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    build_common_result,
    banking_focus_blockers,
    sensitive_data_blockers,
    _bool,
    _mapping,
    _unique,
    evaluate_forex_vacation_mode_owner_toggle_contract_v1,
)
from automation.forex_engine.forex_vacation_mode_runtime_permission_snapshot_v1 import (
    evaluate_forex_vacation_mode_runtime_permission_snapshot_v1,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_ROLLUP_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_ROLLUP"

VACATION_MODE_OWNER_TOGGLE_OPERATION_READY = "VACATION_MODE_OWNER_TOGGLE_OPERATION_READY"
VACATION_MODE_OWNER_TOGGLE_OFF_READY = "VACATION_MODE_OWNER_TOGGLE_OFF_READY"
VACATION_MODE_OWNER_TOGGLE_PAUSED_READY = "VACATION_MODE_OWNER_TOGGLE_PAUSED_READY"
VACATION_MODE_OWNER_TOGGLE_MAINTENANCE_READY = "VACATION_MODE_OWNER_TOGGLE_MAINTENANCE_READY"
VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY = (
    "VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY"
)
VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_PROOF = "VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_PROOF"
VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_RECEIPTS = (
    "VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_RECEIPTS"
)
VACATION_MODE_OWNER_TOGGLE_BALANCE_REVIEW = "VACATION_MODE_OWNER_TOGGLE_BALANCE_REVIEW"
VACATION_MODE_OWNER_TOGGLE_KILL_SWITCH_STOP = "VACATION_MODE_OWNER_TOGGLE_KILL_SWITCH_STOP"
BLOCKED_BY_OWNER_TOGGLE = "BLOCKED_BY_OWNER_TOGGLE"
BLOCKED_BY_OPERATION_STATE = "BLOCKED_BY_OPERATION_STATE"
BLOCKED_BY_PERMISSION_SNAPSHOT = "BLOCKED_BY_PERMISSION_SNAPSHOT"
BLOCKED_BY_OWNER_ATTENTION_STATE = "BLOCKED_BY_OWNER_ATTENTION_STATE"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"

REQUIRED_SECTIONS = (
    "owner_command",
    "runtime_calendar_result",
    "risk_state",
    "proof_state",
    "receipt_state",
    "balance_state",
    "runtime_boundary",
    "permission_policy",
    "attention_policy",
    "owner_attention_context",
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


def evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the Vacation Mode owner-toggle metadata chain."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _rollup_result(
            source,
            BLOCKED_BY_SENSITIVE_DATA,
            False,
            sensitive_blockers,
            next_best_packet=NEXT_BEST_PACKET,
        )
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _rollup_result(
            source,
            BLOCKED_BY_BANKING_FOCUS,
            False,
            banking_blockers,
            next_best_packet=NEXT_BEST_PACKET,
        )
    if not source:
        return _rollup_result(source, INCOMPLETE_INPUTS, False, ("payload_missing",))

    missing = tuple(f"{section}_missing" for section in REQUIRED_SECTIONS if section not in source)
    if missing:
        return _rollup_result(source, INCOMPLETE_INPUTS, False, missing)

    owner_toggle = evaluate_forex_vacation_mode_owner_toggle_contract_v1(
        {"owner_command": source.get("owner_command")}
    )
    if owner_toggle.get("ready") is not True:
        return _rollup_result(
            source,
            BLOCKED_BY_OWNER_TOGGLE,
            False,
            owner_toggle.get("blockers", ()),
            owner_toggle_contract_summary=owner_toggle,
            next_best_packet=NEXT_BEST_PACKET,
        )

    operation_state = evaluate_forex_vacation_mode_operation_state_machine_v1(
        {
            "owner_toggle_result": owner_toggle,
            "runtime_calendar_result": source.get("runtime_calendar_result"),
            "risk_state": source.get("risk_state"),
            "proof_state": source.get("proof_state"),
            "receipt_state": source.get("receipt_state"),
            "balance_state": source.get("balance_state"),
        }
    )
    if operation_state.get("status", "").startswith("BLOCKED_") or operation_state.get("ready") is not True:
        return _rollup_result(
            source,
            BLOCKED_BY_OPERATION_STATE,
            False,
            operation_state.get("blockers", ()),
            owner_toggle_contract_summary=owner_toggle,
            operation_state_summary=operation_state,
            next_best_packet=operation_state.get("next_best_packet", NEXT_BEST_PACKET),
        )

    permission_snapshot = evaluate_forex_vacation_mode_runtime_permission_snapshot_v1(
        {
            "operation_state_result": operation_state,
            "runtime_boundary": source.get("runtime_boundary"),
            "permission_policy": source.get("permission_policy"),
        }
    )
    if permission_snapshot.get("status", "").startswith("BLOCKED_") or permission_snapshot.get("ready") is not True:
        return _rollup_result(
            source,
            BLOCKED_BY_PERMISSION_SNAPSHOT,
            False,
            permission_snapshot.get("blockers", ()),
            owner_toggle_contract_summary=owner_toggle,
            operation_state_summary=operation_state,
            runtime_permission_summary=permission_snapshot,
            next_best_packet=permission_snapshot.get("next_best_packet", NEXT_BEST_PACKET),
        )

    attention_state = evaluate_forex_vacation_mode_owner_attention_state_v1(
        {
            "permission_snapshot_result": permission_snapshot,
            "attention_policy": source.get("attention_policy"),
            "owner_attention_context": _resolved_attention_context(
                _mapping(source.get("owner_attention_context")),
                operation_state,
                permission_snapshot,
            ),
        }
    )
    if attention_state.get("status", "").startswith("BLOCKED_") or attention_state.get("ready") is not True:
        return _rollup_result(
            source,
            BLOCKED_BY_OWNER_ATTENTION_STATE,
            False,
            attention_state.get("blockers", ()),
            owner_toggle_contract_summary=owner_toggle,
            operation_state_summary=operation_state,
            runtime_permission_summary=permission_snapshot,
            owner_attention_summary=attention_state,
            next_best_packet=attention_state.get("next_best_packet", NEXT_BEST_PACKET),
        )

    operation_name = str(operation_state.get("vacation_mode_operation_state", ""))
    campaign_status = _campaign_status(operation_name)
    return _rollup_result(
        source,
        campaign_status,
        True,
        (),
        owner_toggle_contract_summary=owner_toggle,
        operation_state_summary=operation_state,
        runtime_permission_summary=permission_snapshot,
        owner_attention_summary=attention_state,
        next_best_packet=_next_packet(operation_name),
    )


def _rollup_result(
    source: Mapping[str, Any],
    status: str,
    ready: bool,
    blockers: Sequence[str],
    *,
    owner_toggle_contract_summary: Mapping[str, Any] | None = None,
    operation_state_summary: Mapping[str, Any] | None = None,
    runtime_permission_summary: Mapping[str, Any] | None = None,
    owner_attention_summary: Mapping[str, Any] | None = None,
    next_best_packet: str = NEXT_BEST_PACKET,
) -> dict[str, Any]:
    owner_toggle = _mapping(owner_toggle_contract_summary)
    operation = _mapping(operation_state_summary)
    permission = _mapping(runtime_permission_summary)
    attention = _mapping(owner_attention_summary)
    operation_name = str(operation.get("vacation_mode_operation_state", "UNKNOWN"))
    attention_state = _mapping(attention.get("owner_attention_state"))
    extra = {
        "campaign_status": status,
        "campaign_ready": bool(ready),
        "owner_toggle_contract_summary": owner_toggle,
        "operation_state_summary": operation,
        "runtime_permission_summary": permission,
        "owner_attention_summary": attention,
        "destination_map": _destination_map(),
        "owner_action_queue": _owner_action_queue(attention_state, operation_name),
    }
    result = build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=ready,
        vacation_mode_requested=_bool(owner_toggle.get("vacation_mode_requested")),
        vacation_mode_toggle_state=str(owner_toggle.get("vacation_mode_toggle_state", "UNKNOWN")),
        vacation_mode_operation_state=operation_name,
        kill_switch_active=_bool(operation.get("kill_switch_active")) or operation_name == VACATION_MODE_KILL_SWITCH_STOP,
        new_trade_seeking_allowed_by_this_module=_bool(
            permission.get("new_trade_seeking_allowed_by_this_module")
        ),
        maintenance_allowed_by_this_module=_bool(permission.get("maintenance_allowed_by_this_module")),
        owner_attention_required=_bool(attention.get("owner_attention_required")),
        blockers=blockers,
        next_best_packet=next_best_packet,
        safe_manual_next_action=_safe_manual_next_action(operation_name, status),
        extra=extra,
    )
    result["campaign_status"] = status
    result["campaign_ready"] = bool(ready)
    return result


def _campaign_status(operation_state: str) -> str:
    if operation_state == VACATION_MODE_OFF_IDLE:
        return VACATION_MODE_OWNER_TOGGLE_OFF_READY
    if operation_state == VACATION_MODE_PAUSED:
        return VACATION_MODE_OWNER_TOGGLE_PAUSED_READY
    if operation_state == VACATION_MODE_KILL_SWITCH_STOP:
        return VACATION_MODE_OWNER_TOGGLE_KILL_SWITCH_STOP
    if operation_state == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE:
        return VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY
    if operation_state in MAINTENANCE_STATES:
        return VACATION_MODE_OWNER_TOGGLE_MAINTENANCE_READY
    if operation_state == VACATION_MODE_WAITING_FOR_PROOF:
        return VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_PROOF
    if operation_state == VACATION_MODE_WAITING_FOR_RECEIPTS:
        return VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_RECEIPTS
    if operation_state == VACATION_MODE_BALANCE_MEMORY_REVIEW:
        return VACATION_MODE_OWNER_TOGGLE_BALANCE_REVIEW
    return VACATION_MODE_OWNER_TOGGLE_OPERATION_READY


def _next_packet(operation_state: str) -> str:
    if operation_state == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE:
        return "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
    if operation_state in {VACATION_MODE_ON_CLOSED_MAINTENANCE, VACATION_MODE_ON_DEGRADED_MAINTENANCE}:
        return "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
    if operation_state == VACATION_MODE_ON_CLOSE_PROTECTION:
        return "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1"
    if operation_state == VACATION_MODE_ON_REOPEN_PREPARATION:
        return "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"
    if operation_state == VACATION_MODE_ON_WEEKEND_MAINTENANCE:
        return "AIOS_FOREX_WEEKEND_HEAVY_MAINTENANCE_AND_AUDIT_V1"
    if operation_state == VACATION_MODE_WAITING_FOR_PROOF:
        return "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1"
    if operation_state == VACATION_MODE_WAITING_FOR_RECEIPTS:
        return "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
    if operation_state == VACATION_MODE_BALANCE_MEMORY_REVIEW:
        return "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"
    return NEXT_BEST_PACKET


def _destination_map() -> dict[str, str]:
    return {
        "owner command": "owner toggle contract",
        "owner toggle contract": "operation state machine",
        "runtime calendar router": "operation state machine",
        "balance/equity observer": "operation state machine",
        "risk/proof/receipt state": "operation state machine",
        "operation state machine": "runtime permission snapshot",
        "runtime permission snapshot": "owner attention state",
        "owner attention state": "dashboard display metadata",
        "active supervision eligible": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
        "maintenance": "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1",
        "close protection": "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1",
        "reopen prep": "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1",
        "weekend maintenance": "AIOS_FOREX_WEEKEND_HEAVY_MAINTENANCE_AND_AUDIT_V1",
        "waiting proof": "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1",
        "waiting receipts": "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1",
        "balance review": "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1",
        "runtime execution candidate": (
            "AIOS_FOREX_OWNER_APPROVED_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1"
        ),
        "withdrawal review": "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
    }


def _owner_action_queue(attention_state: Mapping[str, Any], operation_state: str) -> list[dict[str, Any]]:
    if not attention_state:
        return []
    if not _bool(attention_state.get("owner_attention_required")):
        return []
    return [
        {
            "action_id": "vacation_mode_owner_attention_review",
            "operation_state": operation_state,
            "severity": str(attention_state.get("severity", "REVIEW")),
            "reason": str(attention_state.get("owner_visible_reason", "")),
            "next_safe_action": str(attention_state.get("next_safe_action", "")),
        }
    ]


def _resolved_attention_context(
    context: Mapping[str, Any],
    operation_state: Mapping[str, Any],
    permission_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    operation_name = str(operation_state.get("vacation_mode_operation_state", "UNKNOWN"))
    resolved = dict(context)
    mapping = _default_attention(operation_name, permission_snapshot)
    for key, value in mapping.items():
        resolved.setdefault(key, value)
    return resolved


def _default_attention(operation_state: str, permission_snapshot: Mapping[str, Any]) -> dict[str, Any]:
    if operation_state == VACATION_MODE_KILL_SWITCH_STOP:
        return {
            "owner_attention_required": True,
            "severity": "STOP_NOW",
            "reason": "Kill switch stop blocks new trade seeking.",
            "next_safe_action": "Keep operation stopped until owner review.",
            "no_sensitive_values": True,
        }
    if operation_state in {VACATION_MODE_WAITING_FOR_PROOF, VACATION_MODE_WAITING_FOR_RECEIPTS, VACATION_MODE_BALANCE_MEMORY_REVIEW}:
        return {
            "owner_attention_required": True,
            "severity": "REVIEW",
            "reason": str(permission_snapshot.get("safe_manual_next_action", "Owner review required.")),
            "next_safe_action": str(permission_snapshot.get("safe_manual_next_action", "Review current gate.")),
            "no_sensitive_values": True,
        }
    return {
        "owner_attention_required": False,
        "severity": "INFO",
        "reason": str(permission_snapshot.get("safe_manual_next_action", "Vacation Mode state is informational.")),
        "next_safe_action": str(permission_snapshot.get("safe_manual_next_action", "Continue metadata review.")),
        "no_sensitive_values": True,
    }


def _safe_manual_next_action(operation_state: str, status: str) -> str:
    if status.startswith("BLOCKED_"):
        return "Resolve blockers before continuing Vacation Mode owner-toggle operation state."
    if operation_state == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE:
        return "Route active supervision metadata; execution remains a future owner-approved runtime packet."
    if operation_state in MAINTENANCE_STATES:
        return "Route safe maintenance or preparation work for the current calendar posture."
    if operation_state == VACATION_MODE_WAITING_FOR_PROOF:
        return "Route proof review before new trade seeking."
    if operation_state == VACATION_MODE_WAITING_FOR_RECEIPTS:
        return "Route receipt and post-burst review before another burst."
    if operation_state == VACATION_MODE_BALANCE_MEMORY_REVIEW:
        return "Route balance/equity memory review before operation continues."
    if operation_state == VACATION_MODE_KILL_SWITCH_STOP:
        return "Keep new trade seeking stopped and surface owner attention."
    if operation_state == VACATION_MODE_OFF_IDLE:
        return "Keep Vacation Mode idle until owner turns it on."
    if operation_state == VACATION_MODE_PAUSED:
        return "Hold new trade seeking until owner resumes and gates recheck."
    return "Continue owner-governed Vacation Mode metadata review."


__all__ = [
    "VACATION_MODE_OWNER_TOGGLE_OPERATION_READY",
    "VACATION_MODE_OWNER_TOGGLE_OFF_READY",
    "VACATION_MODE_OWNER_TOGGLE_PAUSED_READY",
    "VACATION_MODE_OWNER_TOGGLE_MAINTENANCE_READY",
    "VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY",
    "VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_PROOF",
    "VACATION_MODE_OWNER_TOGGLE_WAITING_FOR_RECEIPTS",
    "VACATION_MODE_OWNER_TOGGLE_BALANCE_REVIEW",
    "VACATION_MODE_OWNER_TOGGLE_KILL_SWITCH_STOP",
    "BLOCKED_BY_BANKING_FOCUS",
    "BLOCKED_BY_SENSITIVE_DATA",
    "evaluate_forex_vacation_mode_owner_toggle_and_operation_state_rollup_v1",
]
