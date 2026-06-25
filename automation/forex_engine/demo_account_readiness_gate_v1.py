from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.broker_read_only_snapshot_contract_v1 import (
    BROKER_SNAPSHOT_BLOCKED_INSTRUMENT_NOT_TRADEABLE,
    BROKER_SNAPSHOT_BLOCKED_MARKET_CLOSED,
    BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT,
    BROKER_SNAPSHOT_BLOCKED_MISSING_BALANCE,
    BROKER_SNAPSHOT_BLOCKED_MISSING_MARGIN,
    BROKER_SNAPSHOT_BLOCKED_SPREAD_MISSING,
    BROKER_SNAPSHOT_BLOCKED_STALE_OR_UNRECONCILED,
    BROKER_SNAPSHOT_BLOCKED_UNKNOWN_EXPOSURE,
    BROKER_SNAPSHOT_BLOCKED_UNSANITIZED,
    BROKER_SNAPSHOT_VALID,
    BrokerReadOnlySnapshot,
    BrokerSnapshotValidationResult,
    build_sample_missing_account_snapshot,
    build_sample_valid_broker_snapshot,
    validate_broker_read_only_snapshot,
)


DEMO_ACCOUNT_READINESS_VERSION = "demo_account_readiness_gate_v1"

DEMO_ACCOUNT_READY_FOR_REVIEW = "DEMO_ACCOUNT_READY_FOR_REVIEW"
DEMO_ACCOUNT_BLOCKED_BROKER_SNAPSHOT = "DEMO_ACCOUNT_BLOCKED_BROKER_SNAPSHOT"
DEMO_ACCOUNT_BLOCKED_MARKET = "DEMO_ACCOUNT_BLOCKED_MARKET"
DEMO_ACCOUNT_BLOCKED_SPREAD = "DEMO_ACCOUNT_BLOCKED_SPREAD"
DEMO_ACCOUNT_BLOCKED_MARGIN = "DEMO_ACCOUNT_BLOCKED_MARGIN"
DEMO_ACCOUNT_BLOCKED_UNKNOWN_EXPOSURE = "DEMO_ACCOUNT_BLOCKED_UNKNOWN_EXPOSURE"
DEMO_ACCOUNT_BLOCKED_UNSANITIZED = "DEMO_ACCOUNT_BLOCKED_UNSANITIZED"


@dataclass(frozen=True)
class DemoAccountReadinessConfig:
    max_spread: Decimal = Decimal("1.5")
    min_margin_available: Decimal = Decimal("100.00")


@dataclass(frozen=True)
class DemoAccountReadinessInput:
    broker_snapshot: BrokerReadOnlySnapshot
    config: DemoAccountReadinessConfig = DemoAccountReadinessConfig()


@dataclass(frozen=True)
class DemoAccountReadinessResult:
    engine_version: str
    classification: str
    account_review_allowed: bool
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    blockers: tuple[str, ...]
    next_safe_action: str
    broker_snapshot_status: str
    broker_snapshot_result: BrokerSnapshotValidationResult


def build_sample_ready_account_input() -> DemoAccountReadinessInput:
    return DemoAccountReadinessInput(broker_snapshot=build_sample_valid_broker_snapshot())


def build_sample_blocked_account_input() -> DemoAccountReadinessInput:
    return DemoAccountReadinessInput(broker_snapshot=build_sample_missing_account_snapshot())


def evaluate_demo_account_readiness(
    readiness_input: DemoAccountReadinessInput | Mapping[str, Any] | None = None,
) -> DemoAccountReadinessResult:
    active_input = _coerce_input(readiness_input or build_sample_ready_account_input())
    snapshot_result = validate_broker_read_only_snapshot(active_input.broker_snapshot)
    classification = _classify(snapshot_result, active_input.config)
    blockers = _blockers(classification, snapshot_result, active_input.config)
    return DemoAccountReadinessResult(
        engine_version=DEMO_ACCOUNT_READINESS_VERSION,
        classification=classification,
        account_review_allowed=classification == DEMO_ACCOUNT_READY_FOR_REVIEW,
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        blockers=tuple(blockers),
        next_safe_action=_next_safe_action(classification),
        broker_snapshot_status=snapshot_result.classification,
        broker_snapshot_result=snapshot_result,
    )


def demo_account_readiness_to_jsonable_dict(result: DemoAccountReadinessResult) -> dict[str, Any]:
    return _json_value(result)


def demo_account_readiness_to_operator_text(result: DemoAccountReadinessResult | None = None) -> str:
    active = result or evaluate_demo_account_readiness()
    if active.account_review_allowed:
        return "Demo account is ready for review. Execution remains locked and no trade was placed."
    return f"Demo account is blocked: {'; '.join(active.blockers)}. No trade was placed."


def _classify(
    snapshot_result: BrokerSnapshotValidationResult,
    config: DemoAccountReadinessConfig,
) -> str:
    if snapshot_result.classification == BROKER_SNAPSHOT_VALID:
        snapshot = snapshot_result.snapshot
        if snapshot.spread > config.max_spread:
            return DEMO_ACCOUNT_BLOCKED_SPREAD
        if snapshot.margin_available < config.min_margin_available:
            return DEMO_ACCOUNT_BLOCKED_MARGIN
        return DEMO_ACCOUNT_READY_FOR_REVIEW
    if snapshot_result.classification in (
        BROKER_SNAPSHOT_BLOCKED_MARKET_CLOSED,
        BROKER_SNAPSHOT_BLOCKED_INSTRUMENT_NOT_TRADEABLE,
    ):
        return DEMO_ACCOUNT_BLOCKED_MARKET
    if snapshot_result.classification == BROKER_SNAPSHOT_BLOCKED_SPREAD_MISSING:
        return DEMO_ACCOUNT_BLOCKED_SPREAD
    if snapshot_result.classification == BROKER_SNAPSHOT_BLOCKED_MISSING_MARGIN:
        return DEMO_ACCOUNT_BLOCKED_MARGIN
    if snapshot_result.classification == BROKER_SNAPSHOT_BLOCKED_UNKNOWN_EXPOSURE:
        return DEMO_ACCOUNT_BLOCKED_UNKNOWN_EXPOSURE
    if snapshot_result.classification == BROKER_SNAPSHOT_BLOCKED_UNSANITIZED:
        return DEMO_ACCOUNT_BLOCKED_UNSANITIZED
    if snapshot_result.classification in (
        BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT,
        BROKER_SNAPSHOT_BLOCKED_MISSING_BALANCE,
        BROKER_SNAPSHOT_BLOCKED_STALE_OR_UNRECONCILED,
    ):
        return DEMO_ACCOUNT_BLOCKED_BROKER_SNAPSHOT
    return DEMO_ACCOUNT_BLOCKED_BROKER_SNAPSHOT


def _blockers(
    classification: str,
    snapshot_result: BrokerSnapshotValidationResult,
    config: DemoAccountReadinessConfig,
) -> list[str]:
    if classification == DEMO_ACCOUNT_READY_FOR_REVIEW:
        return []
    if classification == DEMO_ACCOUNT_BLOCKED_SPREAD and snapshot_result.classification == BROKER_SNAPSHOT_VALID:
        return [f"spread {snapshot_result.snapshot.spread} is above max {config.max_spread}"]
    if classification == DEMO_ACCOUNT_BLOCKED_MARGIN and snapshot_result.classification == BROKER_SNAPSHOT_VALID:
        return [f"margin {snapshot_result.snapshot.margin_available} is below minimum {config.min_margin_available}"]
    return list(snapshot_result.blockers) or [classification.lower()]


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_ACCOUNT_READY_FOR_REVIEW:
        return "Continue to risk review; demo execution and broker action remain locked."
    return "Fix the account readiness blocker with sanitized read-only evidence before planning a demo order."


def _coerce_input(value: DemoAccountReadinessInput | Mapping[str, Any]) -> DemoAccountReadinessInput:
    if isinstance(value, DemoAccountReadinessInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoAccountReadinessConfig())
    if not isinstance(config, DemoAccountReadinessConfig):
        config = DemoAccountReadinessConfig(**{**config})
    return DemoAccountReadinessInput(broker_snapshot=raw["broker_snapshot"], config=config)


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


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
