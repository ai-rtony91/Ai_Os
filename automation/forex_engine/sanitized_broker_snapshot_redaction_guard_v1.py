from __future__ import annotations

import json
import re
from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence


SANITIZED_BROKER_SNAPSHOT_REDACTION_GUARD_VERSION = "sanitized_broker_snapshot_redaction_guard_v1"

SNAPSHOT_REDACTION_GUARD_CLEAR = "SNAPSHOT_REDACTION_GUARD_CLEAR"
SNAPSHOT_REDACTION_GUARD_BLOCKED_ACCOUNT_ID = "SNAPSHOT_REDACTION_GUARD_BLOCKED_ACCOUNT_ID"
SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET = "SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET"
SNAPSHOT_REDACTION_GUARD_BLOCKED_RAW_BROKER_PAYLOAD = (
    "SNAPSHOT_REDACTION_GUARD_BLOCKED_RAW_BROKER_PAYLOAD"
)
SNAPSHOT_REDACTION_GUARD_BLOCKED_LIVE_ENDPOINT = "SNAPSHOT_REDACTION_GUARD_BLOCKED_LIVE_ENDPOINT"
SNAPSHOT_REDACTION_GUARD_BLOCKED_UNSAFE_PERSISTENCE = (
    "SNAPSHOT_REDACTION_GUARD_BLOCKED_UNSAFE_PERSISTENCE"
)
SNAPSHOT_REDACTION_GUARD_BLOCKED_EMPTY_INPUT = "SNAPSHOT_REDACTION_GUARD_BLOCKED_EMPTY_INPUT"

DEMO_ACCOUNT_REFERENCE_PRESENT = "DEMO_ACCOUNT_REFERENCE_PRESENT"
SANITIZED_TRANSACTION_REFERENCE_PRESENT = "SANITIZED_TRANSACTION_REFERENCE_PRESENT"
SANITIZED_DEMO_TRADE_REFERENCE_PRESENT = "SANITIZED_DEMO_TRADE_REFERENCE_PRESENT"

ALLOWED_PLACEHOLDER_VALUES = (
    DEMO_ACCOUNT_REFERENCE_PRESENT,
    SANITIZED_TRANSACTION_REFERENCE_PRESENT,
    SANITIZED_DEMO_TRADE_REFERENCE_PRESENT,
)


@dataclass(frozen=True)
class SnapshotRedactionGuardConfig:
    allowed_placeholder_values: tuple[str, ...] = ALLOWED_PLACEHOLDER_VALUES
    max_preview_chars: int = 320


@dataclass(frozen=True)
class SnapshotRedactionGuardInput:
    snapshot: Any
    source: str = "manual_local_sanitized_snapshot"
    config: SnapshotRedactionGuardConfig = SnapshotRedactionGuardConfig()


@dataclass(frozen=True)
class SnapshotRedactionGuardResult:
    engine_version: str
    classification: str
    safe_to_process: bool
    blockers: tuple[str, ...]
    redacted_preview: str
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


@dataclass(frozen=True)
class _GuardIssue:
    category: str
    path: str
    reason: str


def build_sample_safe_redaction_guard_input() -> SnapshotRedactionGuardInput:
    return SnapshotRedactionGuardInput(
        snapshot={
            "account_present": True,
            "account_reference": DEMO_ACCOUNT_REFERENCE_PRESENT,
            "balance_present": True,
            "balance": "10000.00",
            "margin_available_present": True,
            "margin_available": "9500.00",
            "open_trades_present": True,
            "open_trades": 0,
            "open_positions_present": True,
            "open_positions": 0,
            "pending_orders_present": True,
            "pending_orders": 0,
            "last_transaction_id_present": True,
            "last_transaction_id": SANITIZED_TRANSACTION_REFERENCE_PRESENT,
            "market_hours_open": True,
            "instrument_tradeable": True,
            "spread_present": True,
            "spread": "0.8",
            "timestamp_present": True,
            "read_only_reconciled": True,
            "no_unknown_open_exposure": True,
            "source": "sanitized_manual_broker_review_snapshot",
            "sanitized": True,
        }
    )


def build_sample_blocked_account_id_input() -> SnapshotRedactionGuardInput:
    return SnapshotRedactionGuardInput(
        snapshot={
            "account_present": True,
            "account_reference": "101-001-1234567-001",
            "balance_present": True,
        }
    )


def build_sample_blocked_secret_input() -> SnapshotRedactionGuardInput:
    return SnapshotRedactionGuardInput(
        snapshot={
            "api_token": "DETERMINISTIC_SAMPLE_TOKEN_SHOULD_BLOCK",
            "account_reference": DEMO_ACCOUNT_REFERENCE_PRESENT,
        }
    )


def build_sample_blocked_raw_broker_payload_input() -> SnapshotRedactionGuardInput:
    return SnapshotRedactionGuardInput(
        snapshot={
            "raw_broker_response": {
                "private_payload": "deterministic raw response sample should block",
            }
        }
    )


def build_sample_blocked_live_endpoint_input() -> SnapshotRedactionGuardInput:
    return SnapshotRedactionGuardInput(
        snapshot={
            "read_endpoint": "https://api-fxtrade.example.invalid/v3/accounts",
            "account_reference": DEMO_ACCOUNT_REFERENCE_PRESENT,
        }
    )


def build_sample_blocked_unsafe_persistence_input() -> SnapshotRedactionGuardInput:
    return SnapshotRedactionGuardInput(
        snapshot={
            "store_account_identifier_for_later": True,
            "account_reference": DEMO_ACCOUNT_REFERENCE_PRESENT,
        }
    )


def build_sample_blocked_redaction_guard_input() -> SnapshotRedactionGuardInput:
    return build_sample_blocked_account_id_input()


def evaluate_snapshot_redaction_guard(
    guard_input: SnapshotRedactionGuardInput | Mapping[str, Any] | str | None = None,
) -> SnapshotRedactionGuardResult:
    active = _coerce_input(guard_input or build_sample_safe_redaction_guard_input())
    if _empty_input(active.snapshot):
        return SnapshotRedactionGuardResult(
            engine_version=SANITIZED_BROKER_SNAPSHOT_REDACTION_GUARD_VERSION,
            classification=SNAPSHOT_REDACTION_GUARD_BLOCKED_EMPTY_INPUT,
            safe_to_process=False,
            blockers=("snapshot input is empty",),
            redacted_preview="Empty snapshot input. Nothing was processed.",
            next_safe_action=_next_safe_action(SNAPSHOT_REDACTION_GUARD_BLOCKED_EMPTY_INPUT),
            **_permission_defaults(),
        )

    issues = _detect_issues(active.snapshot, active.config)
    classification = _classification(issues)
    safe_to_process = classification == SNAPSHOT_REDACTION_GUARD_CLEAR
    return SnapshotRedactionGuardResult(
        engine_version=SANITIZED_BROKER_SNAPSHOT_REDACTION_GUARD_VERSION,
        classification=classification,
        safe_to_process=safe_to_process,
        blockers=tuple(_blockers(issues)),
        redacted_preview=_redacted_preview(active.snapshot, active.config, issues),
        next_safe_action=_next_safe_action(classification),
        **_permission_defaults(),
    )


def redaction_guard_to_jsonable_dict(result: SnapshotRedactionGuardResult) -> dict[str, Any]:
    return _json_value(result)


def redaction_guard_to_operator_text(result: SnapshotRedactionGuardResult | None = None) -> str:
    active = result or evaluate_snapshot_redaction_guard()
    if active.safe_to_process:
        return (
            "Sanitized broker snapshot redaction guard is clear. "
            "The snapshot can move to local intake review. No trade was placed."
        )
    blockers = "; ".join(active.blockers)
    return f"Sanitized broker snapshot is blocked: {blockers}. No trade was placed."


def _coerce_input(value: SnapshotRedactionGuardInput | Mapping[str, Any] | str) -> SnapshotRedactionGuardInput:
    if isinstance(value, SnapshotRedactionGuardInput):
        return value
    if isinstance(value, str):
        return SnapshotRedactionGuardInput(snapshot=value)
    raw = dict(value)
    if "snapshot" in raw:
        config = raw.get("config", SnapshotRedactionGuardConfig())
        if not isinstance(config, SnapshotRedactionGuardConfig):
            config = SnapshotRedactionGuardConfig(**dict(config))
        return SnapshotRedactionGuardInput(
            snapshot=raw["snapshot"],
            source=str(raw.get("source", "manual_local_sanitized_snapshot")),
            config=config,
        )
    return SnapshotRedactionGuardInput(snapshot=raw)


def _detect_issues(value: Any, config: SnapshotRedactionGuardConfig) -> list[_GuardIssue]:
    issues: list[_GuardIssue] = []

    def walk(candidate: Any, path: tuple[str, ...]) -> None:
        if isinstance(candidate, Mapping):
            for key, child in candidate.items():
                child_path = path + (str(key),)
                issues.extend(_issues_for_key_value(str(key), child, child_path, config))
                walk(child, child_path)
        elif isinstance(candidate, list):
            for index, child in enumerate(candidate):
                walk(child, path + (str(index),))
        else:
            issues.extend(_issues_for_scalar(candidate, path, config))

    walk(value, ())
    return _unique_issues(issues)


def _issues_for_key_value(
    key: str,
    value: Any,
    path: tuple[str, ...],
    config: SnapshotRedactionGuardConfig,
) -> list[_GuardIssue]:
    issues: list[_GuardIssue] = []
    normalized_key = _normalized_key(key)
    path_text = _path_text(path)
    scalar_text = _scalar_text(value)

    if _account_key(normalized_key) and not _allowed_placeholder(scalar_text, config):
        if normalized_key in {"accountreference", "accountid", "accountidentifier", "accountnumber"}:
            issues.append(_issue("account_id", path_text, "account identifier placeholder is not sanitized"))
        elif _looks_like_account_identifier(scalar_text):
            issues.append(_issue("account_id", path_text, "account identifier looking value is present"))

    if _secret_key(normalized_key):
        issues.append(_issue("secret", path_text, "secret or authorization shaped field is present"))

    if _raw_payload_key(normalized_key):
        issues.append(_issue("raw_payload", path_text, "raw broker payload shaped field is present"))

    if _unsafe_persistence_hint(normalized_key, scalar_text):
        issues.append(_issue("unsafe_persistence", path_text, "unsafe account or credential persistence hint is present"))

    return issues


def _issues_for_scalar(value: Any, path: tuple[str, ...], config: SnapshotRedactionGuardConfig) -> list[_GuardIssue]:
    if not isinstance(value, str):
        return []
    if _allowed_placeholder(value, config):
        return []

    lowered = value.strip().lower()
    path_text = _path_text(path)
    issues: list[_GuardIssue] = []

    if _account_phrase_with_identifier(lowered):
        issues.append(_issue("account_id", path_text, "account identifier looking text is present"))
    if _secret_fragment(lowered):
        issues.append(_issue("secret", path_text, "secret or authorization fragment is present"))
    if _raw_payload_fragment(lowered):
        issues.append(_issue("raw_payload", path_text, "raw broker payload label is present"))
    if _live_endpoint_fragment(lowered):
        issues.append(_issue("live_endpoint", path_text, "live endpoint reference is present"))
    if _unsafe_persistence_hint("", lowered):
        issues.append(_issue("unsafe_persistence", path_text, "unsafe persistence wording is present"))
    return issues


def _classification(issues: Sequence[_GuardIssue]) -> str:
    categories = {issue.category for issue in issues}
    if not categories:
        return SNAPSHOT_REDACTION_GUARD_CLEAR
    if "account_id" in categories:
        return SNAPSHOT_REDACTION_GUARD_BLOCKED_ACCOUNT_ID
    if "secret" in categories:
        return SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET
    if "raw_payload" in categories:
        return SNAPSHOT_REDACTION_GUARD_BLOCKED_RAW_BROKER_PAYLOAD
    if "live_endpoint" in categories:
        return SNAPSHOT_REDACTION_GUARD_BLOCKED_LIVE_ENDPOINT
    return SNAPSHOT_REDACTION_GUARD_BLOCKED_UNSAFE_PERSISTENCE


def _blockers(issues: Sequence[_GuardIssue]) -> list[str]:
    return _unique([f"{issue.reason} at {issue.path}" for issue in issues])


def _redacted_preview(
    value: Any,
    config: SnapshotRedactionGuardConfig,
    issues: Sequence[_GuardIssue],
) -> str:
    if issues:
        categories = ", ".join(_unique(issue.category for issue in issues))
        return f"Unsafe snapshot withheld. Blocked categories: {categories}. No private values are shown."
    text = _safe_json_preview(value)
    if len(text) > config.max_preview_chars:
        return text[: config.max_preview_chars] + "...[truncated]"
    return text


def _next_safe_action(classification: str) -> str:
    if classification == SNAPSHOT_REDACTION_GUARD_CLEAR:
        return "Continue to sanitized broker snapshot intake; keep broker action locked."
    if classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_EMPTY_INPUT:
        return "Provide a sanitized read-only broker snapshot with placeholders only."
    if classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_ACCOUNT_ID:
        return "Remove account identifiers and use DEMO_ACCOUNT_REFERENCE_PRESENT only."
    if classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_SECRET:
        return "Remove tokens, passwords, authorization headers, and credential-shaped fields."
    if classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_RAW_BROKER_PAYLOAD:
        return "Replace raw broker payloads with the approved sanitized snapshot fields only."
    if classification == SNAPSHOT_REDACTION_GUARD_BLOCKED_LIVE_ENDPOINT:
        return "Remove live endpoint references before local intake review."
    return "Remove persistence hints for account identifiers or credentials before review."


def _permission_defaults() -> dict[str, bool]:
    return {
        "demo_execution_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
        "live_trading_allowed": False,
        "credential_access_allowed": False,
        "account_id_persistence_allowed": False,
    }


def _empty_input(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Mapping):
        return not value
    if isinstance(value, list):
        return not value
    return False


def _issue(category: str, path: str, reason: str) -> _GuardIssue:
    return _GuardIssue(category=category, path=path, reason=reason)


def _unique_issues(issues: Sequence[_GuardIssue]) -> list[_GuardIssue]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[_GuardIssue] = []
    for issue in issues:
        key = (issue.category, issue.path, issue.reason)
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    return unique


def _account_key(normalized_key: str) -> bool:
    return normalized_key in {
        "accountreference",
        "accountid",
        "accountidentifier",
        "accountnumber",
        "liveaccountid",
    }


def _secret_key(normalized_key: str) -> bool:
    markers = (
        "apikey",
        "apitoken",
        "accesstoken",
        "refreshtoken",
        "bearertoken",
        "authtoken",
        "authorization",
        "authheader",
        "credential",
        "password",
        "passphrase",
        "privatekey",
        "secret",
    )
    return any(marker in normalized_key for marker in markers)


def _raw_payload_key(normalized_key: str) -> bool:
    markers = (
        "rawbrokerresponse",
        "rawbrokerpayload",
        "rawresponse",
        "rawpayload",
        "rawrequest",
        "responsebody",
        "requestbody",
        "privatepayload",
    )
    return any(marker in normalized_key for marker in markers)


def _allowed_placeholder(value: Any, config: SnapshotRedactionGuardConfig) -> bool:
    return isinstance(value, str) and value in config.allowed_placeholder_values


def _looks_like_account_identifier(value: str) -> bool:
    text = str(value).strip()
    if not text:
        return False
    if re.search(r"\b\d{3}-\d{3}-\d{5,}-\d{2,}\b", text):
        return True
    digits = re.sub(r"\D", "", text)
    return len(digits) >= 8 and bool(re.search(r"\d", text))


def _account_phrase_with_identifier(lowered: str) -> bool:
    return bool(
        re.search(
            r"account[^a-z0-9]{0,8}(id|identifier|number)[^a-z0-9]{0,8}[:= ][^,\s]{4,}",
            lowered,
        )
    )


def _secret_fragment(lowered: str) -> bool:
    fragments = (
        "authorization:",
        "bearer ",
        "basic ",
        "api_key=",
        "api token",
        "token=",
        "secret=",
        "password=",
        "access_token",
        "refresh_token",
        "sk-",
        ".env",
    )
    return any(fragment in lowered for fragment in fragments)


def _raw_payload_fragment(lowered: str) -> bool:
    fragments = (
        "raw broker response",
        "raw broker payload",
        "raw_response",
        "raw_payload",
        "response_body",
        "request_body",
    )
    return any(fragment in lowered for fragment in fragments)


def _live_endpoint_fragment(lowered: str) -> bool:
    fragments = (
        "https://",
        "http://",
        "api-fxtrade",
        "live endpoint",
        "live_endpoint",
        "live-api",
        "live broker endpoint",
    )
    return any(fragment in lowered for fragment in fragments)


def _unsafe_persistence_hint(normalized_key: str, lowered_value: str) -> bool:
    haystack = f"{normalized_key} {lowered_value}".lower()
    persistence_words = ("persist", "store", "save", "write", "cache", "retain")
    sensitive_words = (
        "accountid",
        "account id",
        "accountidentifier",
        "account identifier",
        "accountnumber",
        "account number",
        "credential",
        "token",
        "secret",
        "password",
    )
    return any(word in haystack for word in persistence_words) and any(
        word in haystack for word in sensitive_words
    )


def _scalar_text(value: Any) -> str:
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return ""


def _normalized_key(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum())


def _path_text(path: Sequence[str]) -> str:
    if not path:
        return "root"
    return ".".join(str(part) for part in path)


def _safe_json_preview(value: Any) -> str:
    try:
        return json.dumps(_json_value(value), sort_keys=True)
    except TypeError:
        return str(value)


def _unique(values: Sequence[str] | Any) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            unique.append(text)
    return unique


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if is_dataclass(value):
        return {field.name: _json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value
