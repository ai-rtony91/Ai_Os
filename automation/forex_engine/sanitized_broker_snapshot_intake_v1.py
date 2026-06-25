from __future__ import annotations

import json
from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.broker_read_only_snapshot_contract_v1 import (
    BROKER_SNAPSHOT_VALID,
    BrokerReadOnlySnapshot,
    BrokerSnapshotValidationResult,
    broker_snapshot_to_jsonable_dict,
    validate_broker_read_only_snapshot,
)
from automation.forex_engine.sanitized_broker_snapshot_redaction_guard_v1 import (
    SNAPSHOT_REDACTION_GUARD_CLEAR,
    SnapshotRedactionGuardInput,
    SnapshotRedactionGuardResult,
    build_sample_blocked_redaction_guard_input,
    build_sample_safe_redaction_guard_input,
    evaluate_snapshot_redaction_guard,
    redaction_guard_to_jsonable_dict,
)


SANITIZED_BROKER_SNAPSHOT_INTAKE_VERSION = "sanitized_broker_snapshot_intake_v1"

SANITIZED_BROKER_SNAPSHOT_INTAKE_READY = "SANITIZED_BROKER_SNAPSHOT_INTAKE_READY"
SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION_GUARD = (
    "SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION_GUARD"
)
SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS = (
    "SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS"
)
SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES = (
    "SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES"
)
SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT_VALIDATION = (
    "SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT_VALIDATION"
)

BROKER_SNAPSHOT_NOT_EVALUATED = "BROKER_SNAPSHOT_NOT_EVALUATED"

REQUIRED_SNAPSHOT_FIELDS = (
    "account_present",
    "account_reference",
    "balance_present",
    "balance",
    "margin_available_present",
    "margin_available",
    "open_trades_present",
    "open_trades",
    "open_positions_present",
    "open_positions",
    "pending_orders_present",
    "pending_orders",
    "last_transaction_id_present",
    "last_transaction_id",
    "market_hours_open",
    "instrument_tradeable",
    "spread_present",
    "spread",
    "timestamp_present",
    "read_only_reconciled",
    "no_unknown_open_exposure",
    "source",
    "sanitized",
)

DECIMAL_FIELDS = ("balance", "margin_available", "spread")
INTEGER_FIELDS = ("open_trades", "open_positions", "pending_orders")
BOOLEAN_FIELDS = (
    "account_present",
    "balance_present",
    "margin_available_present",
    "open_trades_present",
    "open_positions_present",
    "pending_orders_present",
    "last_transaction_id_present",
    "market_hours_open",
    "instrument_tradeable",
    "spread_present",
    "timestamp_present",
    "read_only_reconciled",
    "no_unknown_open_exposure",
    "sanitized",
)
STRING_FIELDS = ("account_reference", "last_transaction_id", "source")


@dataclass(frozen=True)
class SanitizedBrokerSnapshotIntakeConfig:
    run_contract_validation: bool = True


@dataclass(frozen=True)
class SanitizedBrokerSnapshotIntakeInput:
    snapshot: Any
    config: SanitizedBrokerSnapshotIntakeConfig = SanitizedBrokerSnapshotIntakeConfig()


@dataclass(frozen=True)
class SanitizedBrokerSnapshotIntakeResult:
    engine_version: str
    classification: str
    intake_review_allowed: bool
    guard_status: str
    broker_snapshot_status: str
    normalized_snapshot: BrokerReadOnlySnapshot | None
    blockers: tuple[str, ...]
    next_safe_action: str
    guard_result: SnapshotRedactionGuardResult
    broker_snapshot_result: BrokerSnapshotValidationResult | None
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_sanitized_snapshot_intake_input() -> SanitizedBrokerSnapshotIntakeInput:
    return SanitizedBrokerSnapshotIntakeInput(
        snapshot=build_sample_safe_redaction_guard_input().snapshot
    )


def build_sample_blocked_snapshot_intake_input() -> SanitizedBrokerSnapshotIntakeInput:
    return SanitizedBrokerSnapshotIntakeInput(
        snapshot=build_sample_blocked_redaction_guard_input().snapshot
    )


def build_sample_missing_fields_snapshot_intake_input() -> SanitizedBrokerSnapshotIntakeInput:
    sample = dict(build_sample_sanitized_snapshot_intake_input().snapshot)
    sample.pop("balance")
    sample.pop("margin_available")
    return SanitizedBrokerSnapshotIntakeInput(snapshot=sample)


def intake_sanitized_broker_snapshot(
    intake_input: SanitizedBrokerSnapshotIntakeInput | Mapping[str, Any] | str | None = None,
) -> SanitizedBrokerSnapshotIntakeResult:
    active = _coerce_input(intake_input or build_sample_sanitized_snapshot_intake_input())
    guard = evaluate_snapshot_redaction_guard(SnapshotRedactionGuardInput(snapshot=active.snapshot))
    if guard.classification != SNAPSHOT_REDACTION_GUARD_CLEAR:
        return _result(
            classification=SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION_GUARD,
            guard=guard,
            broker_snapshot_status=BROKER_SNAPSHOT_NOT_EVALUATED,
            normalized_snapshot=None,
            broker_snapshot_result=None,
            blockers=guard.blockers,
        )

    parsed = _parse_snapshot(active.snapshot)
    if not isinstance(parsed, Mapping):
        return _result(
            classification=SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES,
            guard=guard,
            broker_snapshot_status=BROKER_SNAPSHOT_NOT_EVALUATED,
            normalized_snapshot=None,
            broker_snapshot_result=None,
            blockers=("snapshot input must be a JSON object or mapping",),
        )

    missing = [field for field in REQUIRED_SNAPSHOT_FIELDS if field not in parsed]
    if missing:
        return _result(
            classification=SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS,
            guard=guard,
            broker_snapshot_status=BROKER_SNAPSHOT_NOT_EVALUATED,
            normalized_snapshot=None,
            broker_snapshot_result=None,
            blockers=tuple(f"missing required field: {field}" for field in missing),
        )

    normalized, errors = _normalize_snapshot(parsed)
    if errors or normalized is None:
        return _result(
            classification=SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES,
            guard=guard,
            broker_snapshot_status=BROKER_SNAPSHOT_NOT_EVALUATED,
            normalized_snapshot=None,
            broker_snapshot_result=None,
            blockers=tuple(errors),
        )

    broker_result = validate_broker_read_only_snapshot(normalized)
    if active.config.run_contract_validation and broker_result.classification != BROKER_SNAPSHOT_VALID:
        return _result(
            classification=SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT_VALIDATION,
            guard=guard,
            broker_snapshot_status=broker_result.classification,
            normalized_snapshot=normalized,
            broker_snapshot_result=broker_result,
            blockers=broker_result.blockers or (broker_result.classification.lower(),),
        )

    return _result(
        classification=SANITIZED_BROKER_SNAPSHOT_INTAKE_READY,
        guard=guard,
        broker_snapshot_status=broker_result.classification,
        normalized_snapshot=normalized,
        broker_snapshot_result=broker_result,
        blockers=(),
    )


def sanitized_snapshot_intake_to_jsonable_dict(result: SanitizedBrokerSnapshotIntakeResult) -> dict[str, Any]:
    data = _json_value(result)
    if result.normalized_snapshot is not None:
        data["normalized_snapshot"] = broker_snapshot_to_jsonable_dict(result.normalized_snapshot)
    data["guard_result"] = redaction_guard_to_jsonable_dict(result.guard_result)
    return data


def sanitized_snapshot_intake_to_operator_text(
    result: SanitizedBrokerSnapshotIntakeResult | None = None,
) -> str:
    active = result or intake_sanitized_broker_snapshot()
    if active.intake_review_allowed:
        return (
            "Sanitized broker snapshot intake is review-ready. "
            "The snapshot was normalized into the read-only broker contract. No trade was placed."
        )
    blockers = "; ".join(active.blockers)
    return f"Sanitized broker snapshot intake is blocked: {blockers}. No trade was placed."


def sanitized_snapshot_intake_to_markdown(
    result: SanitizedBrokerSnapshotIntakeResult | None = None,
) -> str:
    active = result or intake_sanitized_broker_snapshot()
    return "\n".join(
        [
            "# Sanitized Broker Snapshot Intake V1",
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Guard status: {active.guard_status}",
            f"- Broker snapshot status: {active.broker_snapshot_status}",
            f"- Intake review allowed: {active.intake_review_allowed}",
            f"- Demo execution allowed: {active.demo_execution_allowed}",
            f"- Broker action allowed: {active.broker_action_allowed}",
            f"- Real money allowed: {active.real_money_allowed}",
            f"- Compounding allowed: {active.compounding_allowed}",
            f"- Bank movement allowed: {active.bank_movement_allowed}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _coerce_input(
    value: SanitizedBrokerSnapshotIntakeInput | Mapping[str, Any] | str,
) -> SanitizedBrokerSnapshotIntakeInput:
    if isinstance(value, SanitizedBrokerSnapshotIntakeInput):
        return value
    if isinstance(value, str):
        return SanitizedBrokerSnapshotIntakeInput(snapshot=value)
    raw = dict(value)
    if "snapshot" in raw:
        config = raw.get("config", SanitizedBrokerSnapshotIntakeConfig())
        if not isinstance(config, SanitizedBrokerSnapshotIntakeConfig):
            config = SanitizedBrokerSnapshotIntakeConfig(**dict(config))
        return SanitizedBrokerSnapshotIntakeInput(snapshot=raw["snapshot"], config=config)
    return SanitizedBrokerSnapshotIntakeInput(snapshot=raw)


def _parse_snapshot(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return dict(parsed) if isinstance(parsed, Mapping) else None
    return None


def _normalize_snapshot(raw: Mapping[str, Any]) -> tuple[BrokerReadOnlySnapshot | None, list[str]]:
    values: dict[str, Any] = {}
    errors: list[str] = []

    for field in BOOLEAN_FIELDS:
        value = raw[field]
        if not isinstance(value, bool):
            errors.append(f"invalid boolean field: {field}")
        else:
            values[field] = value

    for field in DECIMAL_FIELDS:
        try:
            values[field] = _to_decimal(raw[field])
        except ValueError:
            errors.append(f"invalid decimal field: {field}")

    for field in INTEGER_FIELDS:
        try:
            values[field] = _to_int(raw[field])
        except ValueError:
            errors.append(f"invalid integer field: {field}")

    for field in STRING_FIELDS:
        value = raw[field]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"invalid string field: {field}")
        else:
            values[field] = value.strip()

    if errors:
        return None, errors
    return BrokerReadOnlySnapshot(**values), []


def _result(
    *,
    classification: str,
    guard: SnapshotRedactionGuardResult,
    broker_snapshot_status: str,
    normalized_snapshot: BrokerReadOnlySnapshot | None,
    broker_snapshot_result: BrokerSnapshotValidationResult | None,
    blockers: tuple[str, ...],
) -> SanitizedBrokerSnapshotIntakeResult:
    return SanitizedBrokerSnapshotIntakeResult(
        engine_version=SANITIZED_BROKER_SNAPSHOT_INTAKE_VERSION,
        classification=classification,
        intake_review_allowed=classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_READY,
        guard_status=guard.classification,
        broker_snapshot_status=broker_snapshot_status,
        normalized_snapshot=normalized_snapshot,
        blockers=blockers,
        next_safe_action=_next_safe_action(classification),
        guard_result=guard,
        broker_snapshot_result=broker_snapshot_result,
        **_permission_defaults(),
    )


def _next_safe_action(classification: str) -> str:
    if classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_READY:
        return "Continue to broker snapshot review packet; do not call a broker or place a trade."
    if classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION_GUARD:
        return "Remove unsafe identifiers or secret-shaped input before intake."
    if classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS:
        return "Provide every required sanitized broker snapshot field."
    if classification == SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES:
        return "Fix field types before local broker snapshot contract validation."
    return "Fix broker snapshot contract blockers before account readiness review."


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


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not a decimal")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


def _to_int(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("boolean is not an integer")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    raise ValueError(f"invalid integer value: {value!r}")


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
