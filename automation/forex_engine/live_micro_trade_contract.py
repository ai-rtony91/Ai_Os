"""Contract-only validation for future single live micro-trade packets.

This module defines fail-closed data contracts. It does not place trades,
connect to brokers, inspect credentials, call network APIs, write files,
launch subprocesses, or schedule runtime work.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from typing import Any


CONTRACT_SCHEMA_VERSION = "single-live-micro-trade-contract-v1"
CONTRACT_MODE = "CONTRACT_ONLY"
EXPECTED_HUMAN_OWNER = "Anthony"
ACTIVE_APPROVAL_TYPE = "single_live_micro_trade_exception"

FORBIDDEN_FIELD_KEYS = {
    "credentials",
    "token",
    "tokens",
    "api_key",
    "password",
    "secret",
    "account_id",
    "account_identifier",
    "broker_order_id",
    "raw_live_payload",
    "live_payload",
    "private_account_data",
}

NON_AUTHORITATIVE_APPROVAL_KEYS = {
    "validator_approval",
    "validator_approved",
    "validator_pass",
    "validator_passed",
    "dashboard_approval",
    "dashboard_approved",
    "router_approval",
    "router_approved",
}

GENERIC_APPROVAL_KEYS = {
    "approved",
    "approved_by_human",
    "approval_granted",
    "approval_status",
}

ALLOWED_SIDES = {"buy", "sell"}
ALLOWED_ORDER_TYPES = {"market", "limit", "stop"}
ALLOWED_AUDIT_EVENT_TYPES = {
    "request",
    "review",
    "approval",
    "rejection",
    "expiry",
    "arming",
    "kill_switch_state",
    "daily_loss_gate",
    "credential_handle_release_denial",
    "order_terminal_result",
    "final_disarm",
}
TERMINAL_DISARM_STATES = {
    "fill",
    "rejection",
    "error",
    "timeout",
    "expiry",
    "manual_kill",
    "validation_mismatch",
}


class ContractValidationError(ValueError):
    """Raised when a live micro-trade contract fails closed."""

    def __init__(self, code: str, reasons: list[str]) -> None:
        self.code = code
        self.reasons = reasons
        super().__init__(f"{code}: {'; '.join(reasons)}")


@dataclass(frozen=True)
class SingleLiveMicroTradeRequest:
    packet_id: str
    approval_window: dict[str, str]
    broker_path: str
    instrument: str
    side: str
    max_loss: float
    daily_loss_cap: float
    stop_loss: float
    order_type: str
    evidence_bundle_id: str
    kill_switch_required: bool
    approval_nonce_hash: str
    arming_step: str
    stop_point: str
    units: int | None = None
    notional_limit: float | None = None
    live_mode: bool = False
    one_order_only: bool = True
    retry_allowed: bool = False
    autonomous_reentry_allowed: bool = False


@dataclass(frozen=True)
class SingleLiveMicroTradeApproval:
    packet_id: str
    human_owner: str
    approval_type: str
    approval_window: dict[str, str]
    broker_path: str
    instrument: str
    side: str
    max_loss: float
    daily_loss_cap: float
    stop_loss: float
    order_type: str
    evidence_bundle_id: str
    approval_nonce_hash: str
    arming_step: str
    stop_point: str
    units: int | None = None
    notional_limit: float | None = None
    non_transferable: bool = True
    expires_after_use: bool = True
    validator_authority: bool = False
    dashboard_authority: bool = False
    router_authority: bool = False


@dataclass(frozen=True)
class SingleLiveMicroTradeAuditEvent:
    event_type: str
    packet_id: str
    sanitized: bool
    redacted_identifiers_only: bool
    contains_private_data: bool = False


@dataclass(frozen=True)
class SingleLiveMicroTradeEvidenceBundle:
    evidence_bundle_id: str
    packet_id: str
    broker_sandbox_or_demo_proof: bool
    risk_gate_passed: bool
    kill_switch_active: bool
    daily_loss_cap_active: bool
    approval_hash_verified: bool
    sanitized: bool


@dataclass(frozen=True)
class SingleLiveMicroTradeArmingState:
    packet_id: str
    approval_nonce_hash: str
    evidence_bundle_id: str
    kill_switch_active: bool
    daily_loss_cap_active: bool
    evidence_bundle_present: bool
    approval_hash_verified: bool
    approval_window_active: bool
    one_order_remaining: bool
    armed: bool = True
    orders_remaining: int = 1
    live_mode: bool = False
    retry_allowed: bool = False
    autonomous_reentry_allowed: bool = False


@dataclass(frozen=True)
class SingleLiveMicroTradeDisarmState:
    packet_id: str
    terminal_state: str
    disarmed: bool
    final: bool
    live_mode: bool = False
    retry_allowed: bool = False
    autonomous_reentry_allowed: bool = False


def validate_micro_trade_request(payload: Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    _ensure_no_forbidden_fields(data)
    _require_fields(
        data,
        [
            "packet_id",
            "approval_window",
            "broker_path",
            "instrument",
            "side",
            "max_loss",
            "daily_loss_cap",
            "stop_loss",
            "order_type",
            "evidence_bundle_id",
            "kill_switch_required",
            "approval_nonce_hash",
            "arming_step",
            "stop_point",
        ],
    )
    _validate_common_trade_shape(data)
    _require_boolean(data, "kill_switch_required", True)
    _ensure_live_mode_false(data)
    _ensure_single_order_invariants(data)

    normalized = _normalized_contract(data)
    normalized.update(
        {
            "contract": "SingleLiveMicroTradeRequest",
            "request_contract_valid": True,
            "human_owner_approval_required": True,
        }
    )
    return normalized


def validate_micro_trade_approval(payload: Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    _ensure_no_forbidden_fields(data)
    _reject_non_authoritative_approval(data)
    _require_fields(
        data,
        [
            "packet_id",
            "human_owner",
            "approval_type",
            "approval_window",
            "broker_path",
            "instrument",
            "side",
            "max_loss",
            "daily_loss_cap",
            "stop_loss",
            "order_type",
            "evidence_bundle_id",
            "approval_nonce_hash",
            "arming_step",
            "stop_point",
            "non_transferable",
            "expires_after_use",
        ],
    )
    if data["human_owner"] != EXPECTED_HUMAN_OWNER:
        _fail("human_owner_required", ["approval must name Anthony as Human Owner"])
    if data["approval_type"] != ACTIVE_APPROVAL_TYPE:
        _fail(
            "specific_approval_type_required",
            ["generic approval status cannot satisfy the exception"],
        )
    _require_boolean(data, "non_transferable", True)
    _require_boolean(data, "expires_after_use", True)
    _require_boolean(data, "validator_authority", False, default=False)
    _require_boolean(data, "dashboard_authority", False, default=False)
    _require_boolean(data, "router_authority", False, default=False)
    _validate_common_trade_shape(data)

    normalized = _normalized_contract(data)
    normalized.update(
        {
            "contract": "SingleLiveMicroTradeApproval",
            "approval_contract_valid": True,
            "human_owner": EXPECTED_HUMAN_OWNER,
            "generic_approval_booleans_sufficient": False,
            "validator_approval_sufficient": False,
            "dashboard_approval_sufficient": False,
            "router_approval_sufficient": False,
        }
    )
    return normalized


def validate_evidence_bundle(payload: Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    _ensure_no_forbidden_fields(data)
    required = [
        "evidence_bundle_id",
        "packet_id",
        "broker_sandbox_or_demo_proof",
        "risk_gate_passed",
        "kill_switch_active",
        "daily_loss_cap_active",
        "approval_hash_verified",
        "sanitized",
    ]
    _require_fields(data, required)
    for key in required[2:]:
        _require_boolean(data, key, True)

    normalized = _normalized_contract(data)
    normalized.update(
        {
            "contract": "SingleLiveMicroTradeEvidenceBundle",
            "evidence_bundle_contract_valid": True,
        }
    )
    return normalized


def validate_audit_event(payload: Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    _ensure_no_forbidden_fields(data)
    _require_fields(data, ["event_type", "packet_id", "sanitized", "redacted_identifiers_only"])
    if data["event_type"] not in ALLOWED_AUDIT_EVENT_TYPES:
        _fail("unsupported_audit_event_type", [f"unsupported audit event: {data['event_type']}"])
    _require_boolean(data, "sanitized", True)
    _require_boolean(data, "redacted_identifiers_only", True)
    _require_boolean(data, "contains_private_data", False, default=False)

    normalized = _normalized_contract(data)
    normalized.update(
        {
            "contract": "SingleLiveMicroTradeAuditEvent",
            "audit_event_contract_valid": True,
        }
    )
    return normalized


def validate_arming_state(payload: Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    _ensure_no_forbidden_fields(data)
    _require_fields(
        data,
        [
            "packet_id",
            "approval_nonce_hash",
            "evidence_bundle_id",
            "kill_switch_active",
            "daily_loss_cap_active",
            "evidence_bundle_present",
            "approval_hash_verified",
            "approval_window_active",
            "one_order_remaining",
            "armed",
        ],
    )
    for key in [
        "kill_switch_active",
        "daily_loss_cap_active",
        "evidence_bundle_present",
        "approval_hash_verified",
        "approval_window_active",
        "one_order_remaining",
        "armed",
    ]:
        _require_boolean(data, key, True)
    if data.get("orders_remaining", 1) != 1:
        _fail("one_order_limit_required", ["arming must have exactly one order remaining"])
    _ensure_live_mode_false(data)
    _ensure_single_order_invariants(data)

    normalized = _normalized_contract(data)
    normalized.update(
        {
            "contract": "SingleLiveMicroTradeArmingState",
            "arming_contract_valid": True,
            "execution_allowed": False,
        }
    )
    return normalized


def validate_disarm_state(payload: Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    _ensure_no_forbidden_fields(data)
    _require_fields(data, ["packet_id", "terminal_state", "disarmed", "final"])
    if data["terminal_state"] not in TERMINAL_DISARM_STATES:
        _fail("terminal_disarm_state_required", [f"nonterminal state: {data['terminal_state']}"])
    _require_boolean(data, "disarmed", True)
    _require_boolean(data, "final", True)
    _ensure_live_mode_false(data)
    _ensure_single_order_invariants(data)

    normalized = _normalized_contract(data)
    normalized.update(
        {
            "contract": "SingleLiveMicroTradeDisarmState",
            "disarm_contract_valid": True,
            "terminal": True,
            "execution_allowed": False,
        }
    )
    return normalized


def assert_contract_module_has_no_execution_capabilities() -> dict[str, Any]:
    return contract_boundary_summary()


def contract_boundary_summary() -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA_VERSION,
        "mode": CONTRACT_MODE,
        "broker_sdk_allowed": False,
        "network_allowed": False,
        "credential_access_allowed": False,
        "environment_secret_read_allowed": False,
        "file_write_allowed": False,
        "subprocess_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "live_trading_enabled": False,
        "orders_allowed": False,
        "retry_allowed": False,
        "autonomous_reentry_allowed": False,
        "validator_can_approve": False,
        "dashboard_can_approve": False,
        "router_can_approve": False,
    }


def _as_mapping(payload: Any) -> dict[str, Any]:
    if is_dataclass(payload):
        return asdict(payload)
    if isinstance(payload, dict):
        return dict(payload)
    _fail("invalid_payload_type", ["payload must be a dataclass instance or dictionary"])


def _normalized_contract(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    normalized.update(
        {
            "schema": CONTRACT_SCHEMA_VERSION,
            "mode": CONTRACT_MODE,
            "live_mode": False,
            "one_order_only": True,
            "retry_allowed": False,
            "autonomous_reentry_allowed": False,
            "broker_sdk_allowed": False,
            "network_allowed": False,
            "credential_access_allowed": False,
            "file_write_allowed": False,
            "subprocess_allowed": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "live_trading_enabled": False,
        }
    )
    return normalized


def _require_fields(data: dict[str, Any], required: list[str]) -> None:
    missing = [key for key in required if key not in data or data[key] in (None, "")]
    if missing:
        _fail("missing_required_fields", [f"missing required field: {key}" for key in missing])


def _validate_common_trade_shape(data: dict[str, Any]) -> None:
    _validate_units_or_notional(data)
    _validate_approval_window(data["approval_window"])
    if str(data["side"]).lower() not in ALLOWED_SIDES:
        _fail("unsupported_side", [f"unsupported side: {data['side']}"])
    if str(data["order_type"]).lower() not in ALLOWED_ORDER_TYPES:
        _fail("unsupported_order_type", [f"unsupported order type: {data['order_type']}"])
    for key in ["max_loss", "daily_loss_cap", "stop_loss"]:
        _require_positive_number(data, key)
    if float(data["max_loss"]) > float(data["daily_loss_cap"]):
        _fail("max_loss_exceeds_daily_cap", ["max_loss must not exceed daily_loss_cap"])


def _validate_units_or_notional(data: dict[str, Any]) -> None:
    has_units = "units" in data and data["units"] not in (None, "")
    has_notional = "notional_limit" in data and data["notional_limit"] not in (None, "")
    if not has_units and not has_notional:
        _fail("missing_trade_size", ["request must include exactly one of units or notional_limit"])
    if has_units and has_notional:
        _fail("ambiguous_trade_size", ["request cannot include both units and notional_limit"])
    if has_units:
        value = data["units"]
        if not isinstance(value, int) or value <= 0:
            _fail("invalid_units", ["units must be a positive integer"])
    if has_notional:
        _require_positive_number(data, "notional_limit")


def _validate_approval_window(value: Any) -> None:
    if not isinstance(value, dict):
        _fail("invalid_approval_window", ["approval_window must be a dictionary"])
    _require_fields(value, ["starts_at_utc", "expires_at_utc"])
    starts_at = _parse_utc_datetime(value["starts_at_utc"], "starts_at_utc")
    expires_at = _parse_utc_datetime(value["expires_at_utc"], "expires_at_utc")
    if starts_at >= expires_at:
        _fail("invalid_approval_window", ["approval window start must be before expiry"])
    now = datetime.now(timezone.utc)
    if not starts_at <= now <= expires_at:
        _fail("inactive_approval_window", ["approval window must be active"])


def _parse_utc_datetime(value: Any, key: str) -> datetime:
    if not isinstance(value, str):
        _fail("invalid_datetime", [f"{key} must be an ISO-8601 UTC string"])
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ContractValidationError("invalid_datetime", [f"{key} is not ISO-8601"]) from exc
    if parsed.tzinfo is None:
        _fail("invalid_datetime", [f"{key} must include timezone"])
    return parsed.astimezone(timezone.utc)


def _require_positive_number(data: dict[str, Any], key: str) -> None:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        _fail("invalid_positive_number", [f"{key} must be a positive number"])


def _require_boolean(
    data: dict[str, Any],
    key: str,
    expected: bool,
    *,
    default: bool | None = None,
) -> None:
    value = data.get(key, default)
    if value is not expected:
        _fail("invalid_boolean_gate", [f"{key} must be {expected}"])


def _ensure_live_mode_false(data: dict[str, Any]) -> None:
    if data.get("live_mode", False) is not False:
        _fail("live_mode_must_default_false", ["live_mode must remain false in contracts"])


def _ensure_single_order_invariants(data: dict[str, Any]) -> None:
    if data.get("one_order_only", True) is not True:
        _fail("one_order_limit_required", ["contract must be one-order-only"])
    if data.get("retry_allowed", False) is not False:
        _fail("retry_forbidden", ["retry is not allowed"])
    if data.get("autonomous_reentry_allowed", False) is not False:
        _fail("autonomous_reentry_forbidden", ["autonomous re-entry is not allowed"])


def _reject_non_authoritative_approval(data: dict[str, Any]) -> None:
    active_sources = [
        key
        for key in NON_AUTHORITATIVE_APPROVAL_KEYS
        if key in data and bool(data.get(key)) is True
    ]
    if active_sources:
        _fail(
            "non_authoritative_approval_source",
            [f"{key} cannot approve a live micro-trade exception" for key in active_sources],
        )
    generic_only = [
        key
        for key in GENERIC_APPROVAL_KEYS
        if key in data and data.get(key) not in (None, "", False)
    ]
    if generic_only and "approval_type" not in data:
        _fail(
            "specific_human_owner_approval_required",
            [f"{key} is not sufficient approval authority" for key in generic_only],
        )


def _ensure_no_forbidden_fields(data: Any) -> None:
    found = sorted(_find_forbidden_keys(data))
    if found:
        _fail("forbidden_field", [f"forbidden field present: {key}" for key in found])


def _find_forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested_value in value.items():
            key_text = str(key).lower()
            if key_text in FORBIDDEN_FIELD_KEYS:
                found.add(key_text)
            found.update(_find_forbidden_keys(nested_value))
    elif isinstance(value, list):
        for item in value:
            found.update(_find_forbidden_keys(item))
    elif isinstance(value, tuple):
        for item in value:
            found.update(_find_forbidden_keys(item))
    return found


def _fail(code: str, reasons: list[str]) -> None:
    raise ContractValidationError(code, reasons)
