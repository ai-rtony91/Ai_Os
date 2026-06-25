from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.demo_account_readiness_gate_v1 import (
    DEMO_ACCOUNT_READY_FOR_REVIEW,
    DemoAccountReadinessInput,
    DemoAccountReadinessResult,
    demo_account_readiness_to_jsonable_dict,
    evaluate_demo_account_readiness,
)
from automation.forex_engine.sanitized_broker_snapshot_intake_v1 import (
    SANITIZED_BROKER_SNAPSHOT_INTAKE_READY,
    SanitizedBrokerSnapshotIntakeInput,
    SanitizedBrokerSnapshotIntakeResult,
    build_sample_blocked_snapshot_intake_input,
    build_sample_sanitized_snapshot_intake_input,
    intake_sanitized_broker_snapshot,
    sanitized_snapshot_intake_to_jsonable_dict,
)


DEMO_BROKER_SNAPSHOT_REVIEW_PACKET_VERSION = "demo_broker_snapshot_review_packet_v1"

DEMO_BROKER_SNAPSHOT_REVIEW_READY = "DEMO_BROKER_SNAPSHOT_REVIEW_READY"
DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE = "DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE"
DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS = (
    "DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS"
)
DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_UNSAFE_INPUT = (
    "DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_UNSAFE_INPUT"
)

ACCOUNT_STATUS_NOT_EVALUATED = "ACCOUNT_STATUS_NOT_EVALUATED"


@dataclass(frozen=True)
class DemoBrokerSnapshotReviewPacketInput:
    intake_input: SanitizedBrokerSnapshotIntakeInput | Mapping[str, Any] | str


@dataclass(frozen=True)
class DemoBrokerSnapshotReviewPacketResult:
    engine_version: str
    classification: str
    snapshot_review_allowed: bool
    account_review_allowed: bool
    guard_status: str
    intake_status: str
    account_status: str
    balance: Decimal | None
    margin_available: Decimal | None
    open_trades: int | None
    open_positions: int | None
    pending_orders: int | None
    market_hours_open: bool | None
    instrument_tradeable: bool | None
    spread: Decimal | None
    read_only_reconciled: bool | None
    sanitized: bool | None
    blockers: tuple[str, ...]
    operator_summary: str
    next_safe_action: str
    intake_result: SanitizedBrokerSnapshotIntakeResult | None
    account_result: DemoAccountReadinessResult | None
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_review_packet_input() -> DemoBrokerSnapshotReviewPacketInput:
    return DemoBrokerSnapshotReviewPacketInput(
        intake_input=build_sample_sanitized_snapshot_intake_input()
    )


def build_sample_blocked_review_packet_input() -> DemoBrokerSnapshotReviewPacketInput:
    return DemoBrokerSnapshotReviewPacketInput(
        intake_input=build_sample_blocked_snapshot_intake_input()
    )


def build_demo_broker_snapshot_review_packet(
    review_input: DemoBrokerSnapshotReviewPacketInput | Mapping[str, Any] | str | None = None,
) -> DemoBrokerSnapshotReviewPacketResult:
    try:
        active = _coerce_input(review_input or build_sample_review_packet_input())
    except (TypeError, KeyError):
        return _unsafe_input_result()

    intake = intake_sanitized_broker_snapshot(active.intake_input)
    snapshot = intake.normalized_snapshot
    if intake.classification != SANITIZED_BROKER_SNAPSHOT_INTAKE_READY or snapshot is None:
        return _result(
            classification=DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE,
            intake=intake,
            account=None,
            blockers=intake.blockers,
        )

    account = evaluate_demo_account_readiness(DemoAccountReadinessInput(broker_snapshot=snapshot))
    if account.classification != DEMO_ACCOUNT_READY_FOR_REVIEW:
        return _result(
            classification=DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS,
            intake=intake,
            account=account,
            blockers=account.blockers,
        )

    return _result(
        classification=DEMO_BROKER_SNAPSHOT_REVIEW_READY,
        intake=intake,
        account=account,
        blockers=(),
    )


def demo_broker_snapshot_review_packet_to_jsonable_dict(
    result: DemoBrokerSnapshotReviewPacketResult,
) -> dict[str, Any]:
    data = _json_value(result)
    if result.intake_result is not None:
        data["intake_result"] = sanitized_snapshot_intake_to_jsonable_dict(result.intake_result)
    if result.account_result is not None:
        data["account_result"] = demo_account_readiness_to_jsonable_dict(result.account_result)
    return data


def demo_broker_snapshot_review_packet_to_operator_text(
    result: DemoBrokerSnapshotReviewPacketResult | None = None,
) -> str:
    active = result or build_demo_broker_snapshot_review_packet()
    return f"{active.operator_summary} No trade was placed."


def demo_broker_snapshot_review_packet_to_markdown(
    result: DemoBrokerSnapshotReviewPacketResult | None = None,
) -> str:
    active = result or build_demo_broker_snapshot_review_packet()
    return "\n".join(
        [
            "# Demo Broker Snapshot Review Packet V1",
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Guard status: {active.guard_status}",
            f"- Intake status: {active.intake_status}",
            f"- Account status: {active.account_status}",
            f"- Snapshot review allowed: {active.snapshot_review_allowed}",
            f"- Account review allowed: {active.account_review_allowed}",
            f"- Balance: {_display(active.balance)}",
            f"- Margin available: {_display(active.margin_available)}",
            f"- Open trades: {_display(active.open_trades)}",
            f"- Open positions: {_display(active.open_positions)}",
            f"- Pending orders: {_display(active.pending_orders)}",
            f"- Market hours open: {_display(active.market_hours_open)}",
            f"- Instrument tradeable: {_display(active.instrument_tradeable)}",
            f"- Spread: {_display(active.spread)}",
            f"- Read-only reconciled: {_display(active.read_only_reconciled)}",
            f"- Sanitized: {_display(active.sanitized)}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _coerce_input(
    value: DemoBrokerSnapshotReviewPacketInput | Mapping[str, Any] | str,
) -> DemoBrokerSnapshotReviewPacketInput:
    if isinstance(value, DemoBrokerSnapshotReviewPacketInput):
        return value
    if isinstance(value, str):
        return DemoBrokerSnapshotReviewPacketInput(intake_input=value)
    raw = dict(value)
    if "intake_input" in raw:
        return DemoBrokerSnapshotReviewPacketInput(intake_input=raw["intake_input"])
    return DemoBrokerSnapshotReviewPacketInput(intake_input=raw)


def _unsafe_input_result() -> DemoBrokerSnapshotReviewPacketResult:
    return DemoBrokerSnapshotReviewPacketResult(
        engine_version=DEMO_BROKER_SNAPSHOT_REVIEW_PACKET_VERSION,
        classification=DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_UNSAFE_INPUT,
        snapshot_review_allowed=False,
        account_review_allowed=False,
        guard_status="NOT_EVALUATED",
        intake_status="NOT_EVALUATED",
        account_status=ACCOUNT_STATUS_NOT_EVALUATED,
        balance=None,
        margin_available=None,
        open_trades=None,
        open_positions=None,
        pending_orders=None,
        market_hours_open=None,
        instrument_tradeable=None,
        spread=None,
        read_only_reconciled=None,
        sanitized=None,
        blockers=("review input was not a supported mapping or JSON string",),
        operator_summary="Broker snapshot review is blocked because the input shape is unsafe.",
        next_safe_action="Provide a sanitized snapshot mapping or JSON string.",
        intake_result=None,
        account_result=None,
        **_permission_defaults(),
    )


def _result(
    *,
    classification: str,
    intake: SanitizedBrokerSnapshotIntakeResult,
    account: DemoAccountReadinessResult | None,
    blockers: tuple[str, ...],
) -> DemoBrokerSnapshotReviewPacketResult:
    snapshot = intake.normalized_snapshot
    account_status = account.classification if account is not None else ACCOUNT_STATUS_NOT_EVALUATED
    return DemoBrokerSnapshotReviewPacketResult(
        engine_version=DEMO_BROKER_SNAPSHOT_REVIEW_PACKET_VERSION,
        classification=classification,
        snapshot_review_allowed=classification == DEMO_BROKER_SNAPSHOT_REVIEW_READY,
        account_review_allowed=account.account_review_allowed if account is not None else False,
        guard_status=intake.guard_status,
        intake_status=intake.classification,
        account_status=account_status,
        balance=snapshot.balance if snapshot is not None else None,
        margin_available=snapshot.margin_available if snapshot is not None else None,
        open_trades=snapshot.open_trades if snapshot is not None else None,
        open_positions=snapshot.open_positions if snapshot is not None else None,
        pending_orders=snapshot.pending_orders if snapshot is not None else None,
        market_hours_open=snapshot.market_hours_open if snapshot is not None else None,
        instrument_tradeable=snapshot.instrument_tradeable if snapshot is not None else None,
        spread=snapshot.spread if snapshot is not None else None,
        read_only_reconciled=snapshot.read_only_reconciled if snapshot is not None else None,
        sanitized=snapshot.sanitized if snapshot is not None else None,
        blockers=blockers,
        operator_summary=_operator_summary(classification, blockers),
        next_safe_action=_next_safe_action(classification),
        intake_result=intake,
        account_result=account,
        **_permission_defaults(),
    )


def _operator_summary(classification: str, blockers: tuple[str, ...]) -> str:
    if classification == DEMO_BROKER_SNAPSHOT_REVIEW_READY:
        return "Broker snapshot review is ready for Anthony to inspect locally."
    if classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE:
        return f"Broker snapshot review is blocked at intake: {'; '.join(blockers)}."
    if classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS:
        return f"Broker snapshot review is blocked by account readiness: {'; '.join(blockers)}."
    return "Broker snapshot review is blocked by unsafe input."


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_BROKER_SNAPSHOT_REVIEW_READY:
        return "Anthony may review the local broker snapshot packet; broker action remains locked."
    if classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE:
        return "Fix sanitized snapshot intake before account readiness review."
    if classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS:
        return "Fix account readiness blockers using sanitized read-only evidence."
    return "Provide only a sanitized mapping or JSON string for local review."


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


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


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
