"""Prepare owner-visible Vacation Mode attention metadata."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    build_common_result,
    banking_focus_blockers,
    sensitive_data_blockers,
    _bool,
    _mapping,
    _present,
    _unique,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_OWNER_ATTENTION_STATE_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_OWNER_ATTENTION_STATE"

VACATION_MODE_OWNER_ATTENTION_READY = "VACATION_MODE_OWNER_ATTENTION_READY"
VACATION_MODE_OWNER_ATTENTION_NOT_REQUIRED = "VACATION_MODE_OWNER_ATTENTION_NOT_REQUIRED"
VACATION_MODE_OWNER_ATTENTION_REQUIRED = "VACATION_MODE_OWNER_ATTENTION_REQUIRED"
VACATION_MODE_OWNER_STOP_NOW_REQUIRED = "VACATION_MODE_OWNER_STOP_NOW_REQUIRED"
BLOCKED_BY_PERMISSION_SNAPSHOT = "BLOCKED_BY_PERMISSION_SNAPSHOT"
BLOCKED_BY_MISSING_OWNER_REASON = "BLOCKED_BY_MISSING_OWNER_REASON"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"
VALID_SEVERITIES = frozenset({"INFO", "REVIEW", "BLOCKED", "STOP_NOW"})

ATTENTION_POLICY_FIELDS = (
    "dashboard_summary_required",
    "owner_visible_reason_required",
    "raw_values_echoed",
    "sensitive_values_allowed",
    "alert_channel_metadata_only",
    "no_alert_runtime_created",
)

OWNER_CONTEXT_FIELDS = (
    "owner_attention_required",
    "severity",
    "next_safe_action",
    "no_sensitive_values",
)


def evaluate_forex_vacation_mode_owner_attention_state_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create owner-facing attention state without creating alert runtime."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _attention_result(source, BLOCKED_BY_SENSITIVE_DATA, False, sensitive_blockers)
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _attention_result(source, BLOCKED_BY_BANKING_FOCUS, False, banking_blockers)
    if not source:
        return _attention_result(source, INCOMPLETE_INPUTS, False, ("payload_missing",))

    permission = _mapping(source.get("permission_snapshot_result"))
    attention_policy = _mapping(source.get("attention_policy"))
    context = _mapping(source.get("owner_attention_context"))
    if not permission:
        return _attention_result(source, INCOMPLETE_INPUTS, False, ("permission_snapshot_result_missing",))
    if not attention_policy:
        return _attention_result(source, INCOMPLETE_INPUTS, False, ("attention_policy_missing",))
    if not context:
        return _attention_result(source, INCOMPLETE_INPUTS, False, ("owner_attention_context_missing",))
    if not _mapping(permission.get("permission_snapshot")):
        return _attention_result(source, BLOCKED_BY_PERMISSION_SNAPSHOT, False, ("permission_snapshot_missing",))

    missing = (
        *_missing_fields(attention_policy, ATTENTION_POLICY_FIELDS, "attention_policy"),
        *_missing_fields(context, OWNER_CONTEXT_FIELDS, "owner_attention_context"),
    )
    if missing:
        return _attention_result(source, INCOMPLETE_INPUTS, False, missing)

    policy_blockers = _attention_policy_blockers(attention_policy)
    if policy_blockers:
        return _attention_result(source, INCOMPLETE_INPUTS, False, policy_blockers)

    severity = str(context.get("severity", "")).upper()
    if severity not in VALID_SEVERITIES:
        return _attention_result(source, INCOMPLETE_INPUTS, False, ("severity_invalid",))
    required = _bool(context.get("owner_attention_required"))
    if required and not _present(context.get("reason")):
        return _attention_result(source, BLOCKED_BY_MISSING_OWNER_REASON, False, ("owner_reason_missing",))
    if required and severity == "STOP_NOW":
        status = VACATION_MODE_OWNER_STOP_NOW_REQUIRED
    elif required:
        status = VACATION_MODE_OWNER_ATTENTION_REQUIRED
    elif severity == "INFO":
        status = VACATION_MODE_OWNER_ATTENTION_NOT_REQUIRED
    else:
        status = VACATION_MODE_OWNER_ATTENTION_READY
    return _attention_result(source, status, True, ())


def _attention_result(
    source: Mapping[str, Any],
    status: str,
    ready: bool,
    blockers: Sequence[str],
) -> dict[str, Any]:
    permission = _mapping(source.get("permission_snapshot_result"))
    context = _mapping(source.get("owner_attention_context"))
    severity = str(context.get("severity", "INFO")).upper()
    required = _bool(context.get("owner_attention_required"))
    attention_state = {
        "owner_attention_required": required,
        "severity": severity,
        "owner_visible_reason": str(context.get("reason", "")),
        "next_safe_action": str(context.get("next_safe_action", "")),
        "dashboard_summary": _dashboard_summary(permission, context, status),
        "raw_values_echoed": False,
        "no_alert_runtime_created": True,
    }
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=ready,
        vacation_mode_requested=_bool(permission.get("vacation_mode_requested")),
        vacation_mode_toggle_state=str(permission.get("vacation_mode_toggle_state", "UNKNOWN")),
        vacation_mode_operation_state=str(permission.get("vacation_mode_operation_state", "UNKNOWN")),
        kill_switch_active=_bool(permission.get("kill_switch_active")),
        new_trade_seeking_allowed_by_this_module=_bool(
            permission.get("new_trade_seeking_allowed_by_this_module")
        ),
        maintenance_allowed_by_this_module=_bool(permission.get("maintenance_allowed_by_this_module")),
        owner_attention_required=required or status in {BLOCKED_BY_PERMISSION_SNAPSHOT, BLOCKED_BY_MISSING_OWNER_REASON},
        blockers=blockers,
        next_best_packet=permission.get("next_best_packet", NEXT_BEST_PACKET),
        safe_manual_next_action=attention_state["next_safe_action"]
        or "Review owner attention state before display.",
        extra={"owner_attention_state": attention_state},
    )


def _attention_policy_blockers(policy: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "dashboard_summary_required",
        "owner_visible_reason_required",
        "alert_channel_metadata_only",
        "no_alert_runtime_created",
    ):
        if not _bool(policy.get(field)):
            blockers.append(f"{field}_false")
    for field in ("raw_values_echoed", "sensitive_values_allowed"):
        if policy.get(field) is not False:
            blockers.append(f"{field}_not_false")
    return tuple(_unique(blockers))


def _dashboard_summary(
    permission: Mapping[str, Any],
    context: Mapping[str, Any],
    status: str,
) -> dict[str, Any]:
    return {
        "vacation_mode_toggle_state": str(permission.get("vacation_mode_toggle_state", "UNKNOWN")),
        "vacation_mode_operation_state": str(permission.get("vacation_mode_operation_state", "UNKNOWN")),
        "permission_status": str(permission.get("status", "UNKNOWN")),
        "attention_status": status,
        "severity": str(context.get("severity", "INFO")).upper(),
        "reason": str(context.get("reason", "")),
        "next_safe_action": str(context.get("next_safe_action", "")),
        "metadata_only": True,
    }


def _missing_fields(source: Mapping[str, Any], fields: Sequence[str], prefix: str) -> tuple[str, ...]:
    return tuple(f"missing_{prefix}_{field}" for field in fields if field not in source)


__all__ = [
    "VACATION_MODE_OWNER_ATTENTION_READY",
    "VACATION_MODE_OWNER_ATTENTION_NOT_REQUIRED",
    "VACATION_MODE_OWNER_ATTENTION_REQUIRED",
    "VACATION_MODE_OWNER_STOP_NOW_REQUIRED",
    "BLOCKED_BY_MISSING_OWNER_REASON",
    "BLOCKED_BY_BANKING_FOCUS",
    "BLOCKED_BY_SENSITIVE_DATA",
    "evaluate_forex_vacation_mode_owner_attention_state_v1",
]
