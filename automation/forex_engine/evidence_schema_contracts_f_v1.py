"""Packet F local evidence schema contracts for intent, approval, and attempt records.

This module is documentation-to-test aligned and contains only in-memory record
validation helpers with strict safety constraints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from automation.forex_engine import schema_contracts as schemas


INTENT_RECORD_VERSION = "AIOS_FOREX_INTENT_RECORD_V1"
APPROVAL_RECORD_VERSION = "AIOS_FOREX_APPROVAL_RECORD_V1"
BLOCKED_ATTEMPT_RECORD_VERSION = "AIOS_FOREX_BLOCKED_ATTEMPT_RECORD_V1"
REJECTED_ATTEMPT_RECORD_VERSION = "AIOS_FOREX_REJECTED_ATTEMPT_RECORD_V1"
ATTEMPT_RECORD_VERSION = "AIOS_FOREX_ATTEMPT_RECORD_V1"

ALLOWED_ENDPOINT_MODES = {"DEMO"}
ALLOWED_GOVERNANCE_STATUSES = {
    "DRAFT",
    "UNDER_REVIEW",
    "REVIEWED",
    "APPROVED",
    "CONDITIONAL_APPROVAL",
    "BLOCKED",
    "REJECTED",
}
ALLOWED_APPROVAL_STATUSES = {
    "PENDING",
    "APPROVED",
    "APPROVED_WITH_CONDITIONS",
    "DEFERRED",
    "REJECTED",
}
ALLOWED_ATTEMPT_OUTCOMES = {
    "DENIED",
    "BLOCKED",
    "DEFERRED",
    "REJECTED",
    "FORWARDED_FOR_APPROVAL",
}
ALLOWED_HALT_TYPES = {
    "CREDENTIAL_BOUNDARY",
    "ACCOUNT_BOUNDARY",
    "ENDPOINT_MODE_VIOLATION",
    "KILL_SWITCH_ACTIVE",
    "HARD_GATE_FAIL",
    "REPLAY_MISSING",
}

FORBIDDEN_BOOL_TRUE_FIELDS = (
    "broker_connection_active",
    "network_access",
    "credentials_accessed",
    "account_identifiers_accessed",
    "broker_sdk_allowed",
    "network_api_allowed",
    "execution_allowed",
    "live_trading_authorized",
    "order_execution_detected",
    "order_execution_enabled",
    "live_orders_allowed",
    "broker_paper_orders_allowed",
    "capital_allocation_detected",
    "execution_authority_granted",
    "account_id_present",
)


def build_evidence_schema_contract_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_EVIDENCE_RECORD_CONTRACTS_SUMMARY.v1",
        "intent_contract_version": INTENT_RECORD_VERSION,
        "approval_contract_version": APPROVAL_RECORD_VERSION,
        "attempt_contract_version": ATTEMPT_RECORD_VERSION,
        "blocked_attempt_contract_version": BLOCKED_ATTEMPT_RECORD_VERSION,
        "rejected_attempt_contract_version": REJECTED_ATTEMPT_RECORD_VERSION,
        "no_broker_connectivity": True,
        "no_credentials": True,
        "no_account_identifiers": True,
        "no_network_access": True,
        "no_order_execution": True,
        "no_live_trading": True,
        "required_common_fields": [
            "timestamp",
            "correlation_id",
            "strategy_id",
            "candidate_id",
            "risk_summary",
            "governance_status",
            "approval_status",
            "endpoint_mode",
            "kill_switch_state",
            "evidence_references",
            "replay_references",
        ],
    }


def validate_intent_record(record: dict[str, Any] | None) -> bool:
    payload = _ensure_mapping(record)
    _require_required_fields(
        payload,
        [
            "timestamp",
            "correlation_id",
            "strategy_id",
            "candidate_id",
            "risk_summary",
            "governance_status",
            "approval_status",
            "endpoint_mode",
            "kill_switch_state",
            "evidence_references",
            "replay_references",
        ],
    )
    _validate_timestamp(payload["timestamp"])
    _validate_non_empty_str(payload["correlation_id"])
    _validate_non_empty_str(payload["strategy_id"])
    _validate_non_empty_str(payload["candidate_id"])
    _validate_dict(payload["risk_summary"])
    _validate_membership(payload["governance_status"], ALLOWED_GOVERNANCE_STATUSES, "governance_status")
    _validate_membership(payload["approval_status"], ALLOWED_APPROVAL_STATUSES, "approval_status")
    _validate_endpoint_mode(payload["endpoint_mode"])
    _validate_bool(payload["kill_switch_state"], "kill_switch_state")
    _validate_string_list(payload["evidence_references"], "evidence_references")
    _validate_string_list(payload["replay_references"], "replay_references")
    _validate_record_safety(payload, allow_optional=True, require_execution_authority_false=True)
    schemas.assert_no_live_permissions(payload)
    payload["record_type"] = str(payload.get("record_type") or INTENT_RECORD_VERSION)
    payload["contract_version"] = INTENT_RECORD_VERSION
    return True


def validate_approval_record(record: dict[str, Any] | None) -> bool:
    payload = _ensure_mapping(record)
    _require_required_fields(
        payload,
        [
            "timestamp",
            "correlation_id",
            "strategy_id",
            "candidate_id",
            "governance_status",
            "risk_summary",
            "approval_status",
            "endpoint_mode",
            "kill_switch_state",
            "evidence_references",
            "replay_references",
            "approval_scope",
            "approval_window_expires_at",
            "manual_arming_required",
            "timeout_seconds",
        ],
    )
    _validate_timestamp(payload["timestamp"])
    _validate_timestamp(payload["approval_window_expires_at"])
    _validate_non_empty_str(payload["correlation_id"])
    _validate_non_empty_str(payload["strategy_id"])
    _validate_non_empty_str(payload["candidate_id"])
    _validate_dict(payload["risk_summary"])
    _validate_membership(payload["governance_status"], ALLOWED_GOVERNANCE_STATUSES, "governance_status")
    _validate_membership(payload["approval_status"], ALLOWED_APPROVAL_STATUSES, "approval_status")
    _validate_endpoint_mode(payload["endpoint_mode"])
    _validate_bool(payload["kill_switch_state"], "kill_switch_state")
    _validate_bool(payload["manual_arming_required"], "manual_arming_required")
    _validate_timeout_seconds(payload["timeout_seconds"])
    if str(payload["approval_status"]).upper() in {"APPROVED", "APPROVED_WITH_CONDITIONS", "DEFERRED"}:
        _validate_non_empty_str(payload["approval_window_expires_at"])
    _validate_string_list(payload["evidence_references"], "evidence_references")
    _validate_string_list(payload["replay_references"], "replay_references")
    _validate_non_empty_str(payload["approval_scope"])
    _validate_record_safety(payload, allow_optional=True, require_execution_authority_false=True)
    schemas.assert_no_live_permissions(payload)
    payload["record_type"] = str(payload.get("record_type") or APPROVAL_RECORD_VERSION)
    payload["contract_version"] = APPROVAL_RECORD_VERSION
    return True


def validate_attempt_record(record: dict[str, Any] | None) -> bool:
    payload = _ensure_mapping(record)
    _require_required_fields(
        payload,
        [
            "timestamp",
            "correlation_id",
            "strategy_id",
            "candidate_id",
            "governance_status",
            "risk_summary",
            "approval_status",
            "endpoint_mode",
            "kill_switch_state",
            "evidence_references",
            "replay_references",
        ],
    )
    _validate_timestamp(payload["timestamp"])
    _validate_non_empty_str(payload["correlation_id"])
    _validate_non_empty_str(payload["strategy_id"])
    _validate_non_empty_str(payload["candidate_id"])
    _validate_dict(payload["risk_summary"])
    _validate_membership(payload["governance_status"], ALLOWED_GOVERNANCE_STATUSES, "governance_status")
    _validate_membership(payload["approval_status"], ALLOWED_APPROVAL_STATUSES, "approval_status")
    _validate_endpoint_mode(payload["endpoint_mode"])
    _validate_bool(payload["kill_switch_state"], "kill_switch_state")
    _validate_string_list(payload["evidence_references"], "evidence_references")
    _validate_string_list(payload["replay_references"], "replay_references")
    _validate_record_safety(payload, allow_optional=True, require_execution_authority_false=True)
    schemas.assert_no_live_permissions(payload)
    payload["record_type"] = str(payload.get("record_type") or ATTEMPT_RECORD_VERSION)
    payload["contract_version"] = ATTEMPT_RECORD_VERSION
    return True


def validate_blocked_attempt_record(record: dict[str, Any] | None) -> bool:
    payload = _ensure_mapping(record)
    validate_attempt_record(payload)
    _require_required_fields(
        payload,
        [
            "blockers",
            "blocker_reason",
            "halt_type",
            "replay_summary_ref",
        ],
    )
    _validate_string_list(payload["blockers"], "blockers")
    _validate_non_empty_str(payload["blocker_reason"])
    _validate_membership(payload["halt_type"], ALLOWED_HALT_TYPES, "halt_type")
    _validate_non_empty_str(payload["replay_summary_ref"])
    payload["record_type"] = str(payload.get("record_type") or BLOCKED_ATTEMPT_RECORD_VERSION)
    payload["contract_version"] = BLOCKED_ATTEMPT_RECORD_VERSION
    return True


def validate_rejected_attempt_record(record: dict[str, Any] | None) -> bool:
    payload = _ensure_mapping(record)
    validate_attempt_record(payload)
    _require_required_fields(
        payload,
        [
            "rejection_reason",
            "rejection_code",
            "upstream_status_ref",
            "reapproval_path",
        ],
    )
    _validate_non_empty_str(payload["rejection_reason"])
    _validate_non_empty_str(payload["rejection_code"])
    _validate_non_empty_str(payload["upstream_status_ref"])
    _validate_string_list(payload["reapproval_path"], "reapproval_path")
    payload["record_type"] = str(payload.get("record_type") or REJECTED_ATTEMPT_RECORD_VERSION)
    payload["contract_version"] = REJECTED_ATTEMPT_RECORD_VERSION
    return True


def validate_execution_attempt_record(record: dict[str, Any] | None) -> bool:
    payload = _ensure_mapping(record)
    validate_attempt_record(payload)
    _require_required_fields(
        payload,
        [
            "attempt_outcome",
            "attempt_status",
            "next_safe_action",
            "final_disarm_required",
            "terminal_disposition",
        ],
    )
    _validate_membership(payload["attempt_outcome"], ALLOWED_ATTEMPT_OUTCOMES, "attempt_outcome")
    _validate_non_empty_str(payload["attempt_status"])
    _validate_non_empty_str(payload["next_safe_action"])
    _validate_bool(payload["final_disarm_required"], "final_disarm_required")
    if payload.get("attempt_status") != "NOT_EXECUTED":
        raise ValueError("attempt_status must remain NOT_EXECUTED in this phase")
    _validate_non_empty_str(payload["terminal_disposition"])
    _validate_record_safety(payload, allow_optional=True, require_execution_authority_false=True)
    payload["record_type"] = str(payload.get("record_type") or "AIOS_FOREX_EXECUTION_ATTEMPT_RECORD_V1")
    payload["contract_version"] = "AIOS_FOREX_EXECUTION_ATTEMPT_RECORD_V1"
    return True


def _validate_record_safety(
    payload: dict[str, Any],
    *,
    allow_optional: bool = True,
    require_execution_authority_false: bool = False,
) -> None:
    _ = allow_optional
    for field in FORBIDDEN_BOOL_TRUE_FIELDS:
        if field in payload:
            if payload[field] is True:
                if field == "execution_authority_granted":
                    raise ValueError("execution_authority_granted must be false")
                raise ValueError(f"forbidden unsafe field true: {field}")
        else:
            continue

    if require_execution_authority_false:
        if payload.get("execution_authority_granted", False) is not False:
            raise ValueError("execution_authority_granted must be false")

    for field in ("correlation_id", "strategy_id", "candidate_id", "record_id", "kill_switch_state"):
        _ = field

    if "account_id" in payload:
        raise ValueError("account_id must not be present")
    if "credentials" in payload:
        raise ValueError("credentials must not be present")
    if "credential" in "".join(sorted(payload.keys())).lower():
        # avoid accidental hidden credential fields
        for key in payload:
            if "credential" in key.lower():
                raise ValueError(f"credential field forbidden: {key}")


def _require_required_fields(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if field not in payload or payload[field] in (None, "")]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")


def _validate_non_empty_str(value: Any, field_name: str | None = None) -> None:
    name = field_name or "value"
    if not isinstance(value, str) or not str(value).strip():
        raise ValueError(f"{name} must be non-empty string")


def _validate_dict(value: Any, field_name: str = "risk_summary") -> None:
    if not isinstance(value, dict) or value == {}:
        raise ValueError(f"{field_name} must be a non-empty mapping")


def _validate_string_list(value: Any, field_name: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{field_name} must contain non-empty strings")


def _validate_membership(value: Any, allowed: set[str], field_name: str) -> None:
    if str(value) not in allowed:
        raise ValueError(f"{field_name} must be one of {sorted(allowed)}")


def _validate_endpoint_mode(value: Any) -> None:
    if str(value) not in ALLOWED_ENDPOINT_MODES:
        raise ValueError(f"endpoint_mode must be one of {sorted(ALLOWED_ENDPOINT_MODES)}")


def _validate_timeout_seconds(value: Any) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError("timeout_seconds must be positive int")


def _validate_bool(value: Any, field_name: str) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be bool")


def _validate_timestamp(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be non-empty string")
    try:
        # allow explicit UTC marker used in current codebase
        normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
        parsed = datetime.fromisoformat(normalized)
    except Exception as exc:
        raise ValueError("timestamp must be ISO-8601 UTC-like value") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")


def _ensure_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("record must be a dict")
    return dict(value)


def evaluate_intent_contract(state: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = _ensure_mapping(state)
    return {
        "record_contract_version": INTENT_RECORD_VERSION,
        "record_contract_summary": build_evidence_schema_contract_summary(),
        "record": payload,
        "allowed": True,
        "contract": {"record_type": INTENT_RECORD_VERSION, "forbidden_unsafe_true_fields": list(FORBIDDEN_BOOL_TRUE_FIELDS)},
    }


def evaluate_approval_contract(state: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = _ensure_mapping(state)
    return {
        "record_contract_version": APPROVAL_RECORD_VERSION,
        "record_contract_summary": build_evidence_schema_contract_summary(),
        "record": payload,
        "allowed": True,
        "contract": {"record_type": APPROVAL_RECORD_VERSION},
    }


def evaluate_attempt_contract(state: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = _ensure_mapping(state)
    return {
        "record_contract_version": ATTEMPT_RECORD_VERSION,
        "record_contract_summary": build_evidence_schema_contract_summary(),
        "record": payload,
        "allowed": True,
        "contract": {"record_type": ATTEMPT_RECORD_VERSION},
    }
