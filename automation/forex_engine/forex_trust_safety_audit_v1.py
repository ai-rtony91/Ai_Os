"""Fail-closed trust and safety helpers for sanitized Forex payloads.

The helpers in this module inspect in-memory dictionaries only. They do not
read files, load environment values, call broker services, or execute orders.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from typing import Any

TRUST_SAFETY_AUDIT_READY = "TRUST_SAFETY_AUDIT_READY"
TRUST_SAFETY_AUDIT_BLOCKED = "TRUST_SAFETY_AUDIT_BLOCKED"

REDACTED_VALUE = "REDACTED_SENSITIVE_VALUE"

SAFE_KEY_EXCEPTIONS = frozenset(
    {
        "account_type",
        "account_currency",
        "broker_environment",
        "no_account_id_in_payload",
        "no_credentials_in_payload",
        "no_env_in_payload",
        "no_account_id_required",
        "no_credentials_required",
        "no_network_required",
        "no_order_execution",
        "owner_demo_order_approval_present",
        "owner_live_exception_present",
        "manual_owner_approval_required_for_demo_order",
        "live_exception_required_for_live_order",
        "sanitized_evidence_only",
        "sanitized_policy_only",
        "sanitized_intent_only",
    }
)

SENSITIVE_EXACT_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "password",
        "passphrase",
        "authorization",
        "credential",
        "credentials",
        "private_key",
        "account_id",
        "accountid",
        "account-number",
        "account_number",
        "accountnumber",
        ".env",
        "env_file",
    }
)

SENSITIVE_KEY_FRAGMENTS = (
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "bearer",
    "authorization",
    "credential",
    "password",
    "passphrase",
    "private_key",
    "account_id",
    "accountid",
    "account-number",
    "account_number",
    "accountnumber",
)

SENSITIVE_VALUE_FRAGMENTS = (
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "bearer ",
    "authorization:",
    "password=",
    "secret=",
    "credential",
    "private key",
    "account_id",
    "accountid",
    "account-number",
    "account_number",
    "accountnumber",
    "oanda account identifier",
    ".env",
    "environment file",
    "sk-",
)

OANDA_ACCOUNT_ID_PATTERN = re.compile(r"\b\d{3}-\d{3}-\d{5,}-\d{3}\b")
OPAQUE_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_\-]{40,}$")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _path(parent: str, key: Any) -> str:
    text = str(key)
    return text if not parent else f"{parent}.{text}"


def _is_sensitive_key(key: Any) -> bool:
    normalized = str(key).strip().lower()
    if normalized in SAFE_KEY_EXCEPTIONS:
        return False
    if normalized in SENSITIVE_EXACT_KEYS:
        return True
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def _looks_like_opaque_token(text: str) -> bool:
    if not OPAQUE_TOKEN_PATTERN.match(text):
        return False
    has_letter = any(char.isalpha() for char in text)
    has_digit = any(char.isdigit() for char in text)
    return has_letter and has_digit


def _is_sensitive_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    lowered = text.lower()
    if not text:
        return False
    if OANDA_ACCOUNT_ID_PATTERN.search(text):
        return True
    if _looks_like_opaque_token(text):
        return True
    return any(fragment in lowered for fragment in SENSITIVE_VALUE_FRAGMENTS)


def _collect_sensitive_locations(payload: Any, *, parent: str = "") -> tuple[list[str], list[str]]:
    rejected_keys: list[str] = []
    sensitive_locations: list[str] = []

    if isinstance(payload, Mapping):
        for key, value in payload.items():
            location = _path(parent, key)
            if _is_sensitive_key(key):
                rejected_keys.append(location)
                sensitive_locations.append(location)
            child_keys, child_locations = _collect_sensitive_locations(value, parent=location)
            rejected_keys.extend(child_keys)
            sensitive_locations.extend(child_locations)
    elif isinstance(payload, (list, tuple, set, frozenset)):
        for index, value in enumerate(payload):
            child_keys, child_locations = _collect_sensitive_locations(value, parent=f"{parent}[{index}]")
            rejected_keys.extend(child_keys)
            sensitive_locations.extend(child_locations)
    elif _is_sensitive_value(payload):
        sensitive_locations.append(parent or "$")

    return list(dict.fromkeys(rejected_keys)), list(dict.fromkeys(sensitive_locations))


def _redact(payload: Any) -> Any:
    if isinstance(payload, Mapping):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key)
            redacted[key_text] = REDACTED_VALUE if _is_sensitive_key(key) else _redact(value)
        return redacted
    if isinstance(payload, (list, tuple, set, frozenset)):
        return [_redact(item) for item in payload]
    if _is_sensitive_value(payload):
        return REDACTED_VALUE
    return _json_safe(payload)


def contains_sensitive_material(payload: Any) -> bool:
    """Return True when a sanitized payload appears to contain secrets or IDs."""
    rejected_keys, sensitive_locations = _collect_sensitive_locations(payload)
    return bool(rejected_keys or sensitive_locations)


def redact_sensitive_material(payload: Any) -> Any:
    """Return a JSON-safe copy with sensitive values replaced, never exposed."""
    return _redact(payload)


def audit_sanitized_payload(
    payload: Any,
    *,
    allowed_keys: Iterable[str] | None = None,
    required_keys: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Audit a sanitized payload and return a fail-closed JSON-safe result."""
    blockers: list[str] = []
    rejected_keys: list[str] = []
    sensitive_value_locations: list[str] = []
    unknown_keys: list[str] = []
    missing_required: list[str] = []

    if not isinstance(payload, Mapping):
        blockers.append("payload_not_mapping")
    else:
        payload_keys = {str(key) for key in payload.keys()}
        if allowed_keys is not None:
            allowed = {str(key) for key in allowed_keys}
            unknown_keys = sorted(payload_keys - allowed)
            if unknown_keys:
                blockers.append("unknown_keys_present")
        if required_keys is not None:
            required = {str(key) for key in required_keys}
            missing_required = sorted(required - payload_keys)
            if missing_required:
                blockers.append("missing_required_keys")

    key_hits, value_hits = _collect_sensitive_locations(payload)
    if key_hits:
        blockers.append("sensitive_keys_present")
        rejected_keys.extend(key_hits)
    if value_hits:
        blockers.append("sensitive_values_present")
        sensitive_value_locations.extend(value_hits)

    blockers = list(dict.fromkeys(blockers))
    ready = not blockers
    return {
        "status": TRUST_SAFETY_AUDIT_READY if ready else TRUST_SAFETY_AUDIT_BLOCKED,
        "ready": ready,
        "blockers": blockers,
        "redacted_payload": redact_sensitive_material(payload),
        "rejected_keys": list(dict.fromkeys(rejected_keys)),
        "unknown_keys": unknown_keys,
        "missing_required_keys": missing_required,
        "sensitive_value_locations": list(dict.fromkeys(sensitive_value_locations)),
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
    }


def build_safety_audit_result(
    payload: Any,
    *,
    allowed_keys: Iterable[str] | None = None,
    required_keys: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Compatibility wrapper for readiness modules."""
    return audit_sanitized_payload(payload, allowed_keys=allowed_keys, required_keys=required_keys)
