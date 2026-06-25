from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.broker_read_only_snapshot_contract_v1 import BROKER_SNAPSHOT_VALID
from automation.forex_engine.demo_account_readiness_gate_v1 import DEMO_ACCOUNT_READY_FOR_REVIEW
from automation.forex_engine.demo_broker_snapshot_review_packet_v1 import (
    DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS,
    DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE,
    DEMO_BROKER_SNAPSHOT_REVIEW_READY,
    DemoBrokerSnapshotReviewPacketInput,
    DemoBrokerSnapshotReviewPacketResult,
    build_demo_broker_snapshot_review_packet,
    build_sample_blocked_review_packet_input,
    build_sample_review_packet_input,
    demo_broker_snapshot_review_packet_to_jsonable_dict,
)
from automation.forex_engine.sanitized_broker_snapshot_intake_v1 import (
    SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT_VALIDATION,
    SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES,
    SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS,
)
from automation.forex_engine.sanitized_broker_snapshot_redaction_guard_v1 import (
    SNAPSHOT_REDACTION_GUARD_CLEAR,
)


SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_EPIC_VERSION = (
    "supervised_demo_broker_snapshot_intake_epic_v1"
)

SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW = (
    "SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW"
)
SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION = (
    "SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION"
)
SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT = (
    "SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT"
)
SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_ACCOUNT = (
    "SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_ACCOUNT"
)


@dataclass(frozen=True)
class SupervisedDemoBrokerSnapshotIntakeEpicConfig:
    selected_strategy_context: str = "Supertrend"
    instrument_context: str = "EUR_USD"


@dataclass(frozen=True)
class SupervisedDemoBrokerSnapshotIntakeEpicInput:
    config: SupervisedDemoBrokerSnapshotIntakeEpicConfig
    review_packet_input: DemoBrokerSnapshotReviewPacketInput | Mapping[str, Any] | str


@dataclass(frozen=True)
class SupervisedDemoBrokerSnapshotIntakeEpicResult:
    engine_version: str
    classification: str
    selected_strategy_context: str
    instrument_context: str
    guard_status: str
    intake_status: str
    broker_snapshot_status: str
    account_status: str
    snapshot_review_allowed: bool
    account_review_allowed: bool
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    operator_answer: str
    next_safe_action: str
    review_packet_result: DemoBrokerSnapshotReviewPacketResult


def build_sample_supervised_demo_snapshot_intake_ready_input() -> SupervisedDemoBrokerSnapshotIntakeEpicInput:
    return SupervisedDemoBrokerSnapshotIntakeEpicInput(
        config=SupervisedDemoBrokerSnapshotIntakeEpicConfig(),
        review_packet_input=build_sample_review_packet_input(),
    )


def build_sample_supervised_demo_snapshot_intake_blocked_input() -> SupervisedDemoBrokerSnapshotIntakeEpicInput:
    return SupervisedDemoBrokerSnapshotIntakeEpicInput(
        config=SupervisedDemoBrokerSnapshotIntakeEpicConfig(),
        review_packet_input=build_sample_blocked_review_packet_input(),
    )


def run_supervised_demo_broker_snapshot_intake_epic(
    epic_input: SupervisedDemoBrokerSnapshotIntakeEpicInput | Mapping[str, Any] | None = None,
) -> SupervisedDemoBrokerSnapshotIntakeEpicResult:
    active = _coerce_input(epic_input or build_sample_supervised_demo_snapshot_intake_ready_input())
    review = build_demo_broker_snapshot_review_packet(active.review_packet_input)
    classification = _classify(review)
    return SupervisedDemoBrokerSnapshotIntakeEpicResult(
        engine_version=SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_EPIC_VERSION,
        classification=classification,
        selected_strategy_context=active.config.selected_strategy_context,
        instrument_context=active.config.instrument_context,
        guard_status=review.guard_status,
        intake_status=review.intake_status,
        broker_snapshot_status=_broker_snapshot_status(review),
        account_status=review.account_status,
        snapshot_review_allowed=review.snapshot_review_allowed,
        account_review_allowed=review.account_review_allowed,
        operator_answer=_operator_answer(classification),
        next_safe_action=_next_safe_action(classification),
        review_packet_result=review,
        **_permission_defaults(),
    )


def supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
    result: SupervisedDemoBrokerSnapshotIntakeEpicResult,
) -> dict[str, Any]:
    data = _json_value(result)
    data["review_packet_result"] = demo_broker_snapshot_review_packet_to_jsonable_dict(
        result.review_packet_result
    )
    return data


def supervised_demo_broker_snapshot_intake_epic_to_operator_text(
    result: SupervisedDemoBrokerSnapshotIntakeEpicResult | None = None,
) -> str:
    active = result or run_supervised_demo_broker_snapshot_intake_epic()
    return (
        f"Supervised demo broker snapshot intake status: {active.classification}. "
        f"{active.operator_answer} No trade was placed."
    )


def supervised_demo_broker_snapshot_intake_epic_to_markdown(
    result: SupervisedDemoBrokerSnapshotIntakeEpicResult | None = None,
) -> str:
    active = result or run_supervised_demo_broker_snapshot_intake_epic()
    return "\n".join(
        [
            "# Supervised Demo Broker Snapshot Intake Epic V1",
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Selected strategy context: {active.selected_strategy_context}",
            f"- Instrument context: {active.instrument_context}",
            f"- Guard status: {active.guard_status}",
            f"- Intake status: {active.intake_status}",
            f"- Broker snapshot status: {active.broker_snapshot_status}",
            f"- Account status: {active.account_status}",
            f"- Snapshot review allowed: {active.snapshot_review_allowed}",
            f"- Account review allowed: {active.account_review_allowed}",
            f"- Demo execution allowed: {active.demo_execution_allowed}",
            f"- Broker action allowed: {active.broker_action_allowed}",
            f"- Real money allowed: {active.real_money_allowed}",
            f"- Compounding allowed: {active.compounding_allowed}",
            f"- Bank movement allowed: {active.bank_movement_allowed}",
            f"- Operator answer: {active.operator_answer}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _coerce_input(
    value: SupervisedDemoBrokerSnapshotIntakeEpicInput | Mapping[str, Any],
) -> SupervisedDemoBrokerSnapshotIntakeEpicInput:
    if isinstance(value, SupervisedDemoBrokerSnapshotIntakeEpicInput):
        return value
    raw = dict(value)
    config = raw.get("config", SupervisedDemoBrokerSnapshotIntakeEpicConfig())
    if not isinstance(config, SupervisedDemoBrokerSnapshotIntakeEpicConfig):
        config = SupervisedDemoBrokerSnapshotIntakeEpicConfig(**dict(config))
    return SupervisedDemoBrokerSnapshotIntakeEpicInput(
        config=config,
        review_packet_input=raw["review_packet_input"],
    )


def _classify(review: DemoBrokerSnapshotReviewPacketResult) -> str:
    if review.guard_status != SNAPSHOT_REDACTION_GUARD_CLEAR:
        return SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION
    if review.classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE:
        if review.intake_status in (
            SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT_VALIDATION,
            SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_MISSING_REQUIRED_FIELDS,
            SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_INVALID_TYPES,
        ):
            return SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT
        return SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION
    if review.classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS:
        return SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_ACCOUNT
    if (
        review.classification == DEMO_BROKER_SNAPSHOT_REVIEW_READY
        and review.account_status == DEMO_ACCOUNT_READY_FOR_REVIEW
        and _broker_snapshot_status(review) == BROKER_SNAPSHOT_VALID
    ):
        return SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW
    return SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_ACCOUNT


def _broker_snapshot_status(review: DemoBrokerSnapshotReviewPacketResult) -> str:
    if review.intake_result is None:
        return "BROKER_SNAPSHOT_NOT_EVALUATED"
    return review.intake_result.broker_snapshot_status


def _operator_answer(classification: str) -> str:
    if classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW:
        return (
            "The sanitized snapshot is ready for local review, but demo execution and broker action remain locked."
        )
    if classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION:
        return "The snapshot is blocked because unsafe redaction risk was detected."
    if classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT:
        return "The snapshot is blocked because it did not satisfy the read-only broker contract."
    return "The snapshot is blocked by account readiness review."


def _next_safe_action(classification: str) -> str:
    if classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW:
        return "Anthony may review the local snapshot packet; no execution approval is granted."
    if classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION:
        return "Remove unsafe identifiers, secrets, endpoint references, or raw payloads and retry locally."
    if classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT:
        return "Fix sanitized snapshot fields before asking for account readiness review."
    return "Resolve account readiness blockers before any supervised demo trade review package."


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
