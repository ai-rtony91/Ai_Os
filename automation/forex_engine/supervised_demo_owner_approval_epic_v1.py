from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.supervised_demo_owner_approval_packet_v1 import (
    SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW,
    SupervisedDemoOwnerApprovalPacketInput,
    SupervisedDemoOwnerApprovalPacketResult,
    build_sample_supervised_demo_owner_approval_packet_blocked_input,
    build_sample_supervised_demo_owner_approval_packet_ready_input,
    build_supervised_demo_owner_approval_packet,
    supervised_demo_owner_approval_packet_to_jsonable_dict,
)


SUPERVISED_DEMO_OWNER_APPROVAL_EPIC_VERSION = "supervised_demo_owner_approval_epic_v1"

SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW = (
    "SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW"
)
SUPERVISED_DEMO_OWNER_APPROVAL_BLOCKED = "SUPERVISED_DEMO_OWNER_APPROVAL_BLOCKED"


@dataclass(frozen=True)
class SupervisedDemoOwnerApprovalEpicConfig:
    package_name: str = "Supervised Demo Owner Approval Gate V1"


@dataclass(frozen=True)
class SupervisedDemoOwnerApprovalEpicInput:
    config: SupervisedDemoOwnerApprovalEpicConfig
    owner_packet_input: SupervisedDemoOwnerApprovalPacketInput | Mapping[str, Any]


@dataclass(frozen=True)
class SupervisedDemoOwnerApprovalEpicResult:
    engine_version: str
    classification: str
    owner_packet_status: str
    readiness_status: str
    phrase_status: str
    checklist_status: str
    selected_strategy: str
    candidate_id: str
    instrument: str
    direction: str
    proposed_units: int
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    max_loss: Decimal
    expected_reward: Decimal
    reward_to_risk: Decimal
    owner_warning: str
    required_phrase: str
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
    owner_packet_result: SupervisedDemoOwnerApprovalPacketResult


def build_sample_supervised_demo_owner_approval_ready_input() -> SupervisedDemoOwnerApprovalEpicInput:
    return SupervisedDemoOwnerApprovalEpicInput(
        config=SupervisedDemoOwnerApprovalEpicConfig(),
        owner_packet_input=build_sample_supervised_demo_owner_approval_packet_ready_input(),
    )


def build_sample_supervised_demo_owner_approval_blocked_input() -> SupervisedDemoOwnerApprovalEpicInput:
    return SupervisedDemoOwnerApprovalEpicInput(
        config=SupervisedDemoOwnerApprovalEpicConfig(),
        owner_packet_input=build_sample_supervised_demo_owner_approval_packet_blocked_input(),
    )


def run_supervised_demo_owner_approval_epic(
    epic_input: SupervisedDemoOwnerApprovalEpicInput | Mapping[str, Any] | None = None,
) -> SupervisedDemoOwnerApprovalEpicResult:
    active = _coerce_input(epic_input or build_sample_supervised_demo_owner_approval_ready_input())
    packet = build_supervised_demo_owner_approval_packet(active.owner_packet_input)
    classification = (
        SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW
        if packet.classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW
        else SUPERVISED_DEMO_OWNER_APPROVAL_BLOCKED
    )
    return SupervisedDemoOwnerApprovalEpicResult(
        engine_version=SUPERVISED_DEMO_OWNER_APPROVAL_EPIC_VERSION,
        classification=classification,
        owner_packet_status=packet.classification,
        readiness_status=packet.readiness_status,
        phrase_status=packet.phrase_status,
        checklist_status=packet.checklist_status,
        selected_strategy=packet.selected_strategy,
        candidate_id=packet.candidate_id,
        instrument=packet.instrument,
        direction=packet.direction,
        proposed_units=packet.proposed_units,
        entry_price=packet.entry_price,
        stop_loss=packet.stop_loss,
        take_profit=packet.take_profit,
        max_loss=packet.max_loss,
        expected_reward=packet.expected_reward,
        reward_to_risk=packet.reward_to_risk,
        owner_warning=packet.owner_warning,
        required_phrase=packet.required_phrase,
        operator_answer=_operator_answer(classification),
        next_safe_action=_next_safe_action(classification),
        owner_packet_result=packet,
        **_permission_defaults(),
    )


def supervised_demo_owner_approval_epic_to_jsonable_dict(
    result: SupervisedDemoOwnerApprovalEpicResult,
) -> dict[str, Any]:
    data = _json_value(result)
    data["owner_packet_result"] = supervised_demo_owner_approval_packet_to_jsonable_dict(
        result.owner_packet_result
    )
    return data


def supervised_demo_owner_approval_epic_to_operator_text(
    result: SupervisedDemoOwnerApprovalEpicResult | None = None,
) -> str:
    active = result or run_supervised_demo_owner_approval_epic()
    return (
        f"Supervised demo owner approval status: {active.classification}. "
        f"{active.selected_strategy} {active.direction} {active.instrument}, "
        f"{active.proposed_units} units. {active.operator_answer} No trade was placed."
    )


def supervised_demo_owner_approval_epic_to_markdown(
    result: SupervisedDemoOwnerApprovalEpicResult | None = None,
) -> str:
    active = result or run_supervised_demo_owner_approval_epic()
    return "\n".join(
        [
            "# Supervised Demo Owner Approval Epic V1",
            "",
            active.owner_warning,
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Owner packet status: {active.owner_packet_status}",
            f"- Readiness status: {active.readiness_status}",
            f"- Phrase status: {active.phrase_status}",
            f"- Checklist status: {active.checklist_status}",
            f"- Selected strategy: {active.selected_strategy}",
            f"- Candidate id: {active.candidate_id}",
            f"- Instrument: {active.instrument}",
            f"- Direction: {active.direction}",
            f"- Proposed units: {active.proposed_units}",
            f"- Entry price: {active.entry_price}",
            f"- Stop loss: {active.stop_loss}",
            f"- Take profit: {active.take_profit}",
            f"- Max loss: {active.max_loss}",
            f"- Expected reward: {active.expected_reward}",
            f"- Reward-to-risk: {active.reward_to_risk}",
            f"- Required phrase: {active.required_phrase}",
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
    value: SupervisedDemoOwnerApprovalEpicInput | Mapping[str, Any],
) -> SupervisedDemoOwnerApprovalEpicInput:
    if isinstance(value, SupervisedDemoOwnerApprovalEpicInput):
        return value
    raw = dict(value)
    config = raw.get("config", SupervisedDemoOwnerApprovalEpicConfig())
    if not isinstance(config, SupervisedDemoOwnerApprovalEpicConfig):
        config = SupervisedDemoOwnerApprovalEpicConfig(**dict(config))
    return SupervisedDemoOwnerApprovalEpicInput(
        config=config,
        owner_packet_input=raw["owner_packet_input"],
    )


def _operator_answer(classification: str) -> str:
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW:
        return "The final local owner approval packet is ready for manual review only; execution remains locked."
    return "The final local owner approval packet is blocked and must not be used for execution."


def _next_safe_action(classification: str) -> str:
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW:
        return "Anthony may review the owner packet manually; Codex must not execute or approve broker action."
    return "Resolve owner approval blockers before any supervised demo review can continue."


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
