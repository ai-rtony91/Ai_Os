from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.demo_owner_approval_checklist_v1 import (
    DEMO_OWNER_APPROVAL_CHECKLIST_READY,
    DemoOwnerApprovalChecklistInput,
    DemoOwnerApprovalChecklistResult,
    build_sample_blocked_owner_approval_checklist_input,
    build_sample_ready_owner_approval_checklist_input,
    demo_owner_approval_checklist_to_jsonable_dict,
    evaluate_demo_owner_approval_checklist,
)
from automation.forex_engine.demo_owner_approval_phrase_gate_v1 import (
    DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW,
    OWNER_WARNING,
    REQUIRED_OWNER_APPROVAL_PHRASE,
    DemoOwnerApprovalPhraseGateInput,
    DemoOwnerApprovalPhraseGateResult,
    build_sample_missing_owner_approval_phrase_input,
    build_sample_valid_owner_approval_phrase_input,
    demo_owner_approval_phrase_gate_to_jsonable_dict,
    evaluate_demo_owner_approval_phrase_gate,
)
from automation.forex_engine.supervised_demo_trade_readiness_epic_v1 import (
    SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW,
    SupervisedDemoTradeReadinessEpicInput,
    SupervisedDemoTradeReadinessEpicResult,
    build_sample_supervised_demo_trade_readiness_blocked_input,
    build_sample_supervised_demo_trade_readiness_ready_input,
    run_supervised_demo_trade_readiness_epic,
    supervised_demo_trade_readiness_epic_to_jsonable_dict,
)


SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_VERSION = "supervised_demo_owner_approval_packet_v1"

SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW = (
    "SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW"
)
SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_READINESS = (
    "SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_READINESS"
)
SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PHRASE = (
    "SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PHRASE"
)
SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_CHECKLIST = (
    "SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_CHECKLIST"
)
SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PROTECTED_ACTION = (
    "SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PROTECTED_ACTION"
)

BLOCKED_ACTIONS = (
    "demo execution",
    "broker action",
    "real money",
    "compounding",
    "bank movement",
    "live trading",
    "credential access",
    "account id persistence",
)


@dataclass(frozen=True)
class SupervisedDemoOwnerApprovalPacketInput:
    readiness_input: SupervisedDemoTradeReadinessEpicInput | Mapping[str, Any]
    phrase_input: DemoOwnerApprovalPhraseGateInput | Mapping[str, Any]
    checklist_input: DemoOwnerApprovalChecklistInput | Mapping[str, Any]
    protected_action_requested: bool = False


@dataclass(frozen=True)
class SupervisedDemoOwnerApprovalPacketResult:
    engine_version: str
    classification: str
    owner_packet_review_allowed: bool
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
    blocked_actions: tuple[str, ...]
    blockers: tuple[str, ...]
    operator_summary: str
    next_safe_action: str
    readiness_result: SupervisedDemoTradeReadinessEpicResult
    phrase_result: DemoOwnerApprovalPhraseGateResult
    checklist_result: DemoOwnerApprovalChecklistResult
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_supervised_demo_owner_approval_packet_ready_input() -> SupervisedDemoOwnerApprovalPacketInput:
    return SupervisedDemoOwnerApprovalPacketInput(
        readiness_input=build_sample_supervised_demo_trade_readiness_ready_input(),
        phrase_input=build_sample_valid_owner_approval_phrase_input(),
        checklist_input=build_sample_ready_owner_approval_checklist_input(),
    )


def build_sample_supervised_demo_owner_approval_packet_blocked_input() -> SupervisedDemoOwnerApprovalPacketInput:
    return SupervisedDemoOwnerApprovalPacketInput(
        readiness_input=build_sample_supervised_demo_trade_readiness_blocked_input(),
        phrase_input=build_sample_missing_owner_approval_phrase_input(),
        checklist_input=build_sample_blocked_owner_approval_checklist_input(),
    )


def build_supervised_demo_owner_approval_packet(
    packet_input: SupervisedDemoOwnerApprovalPacketInput | Mapping[str, Any] | None = None,
) -> SupervisedDemoOwnerApprovalPacketResult:
    active = _coerce_input(packet_input or build_sample_supervised_demo_owner_approval_packet_ready_input())
    readiness = run_supervised_demo_trade_readiness_epic(active.readiness_input)
    phrase = evaluate_demo_owner_approval_phrase_gate(active.phrase_input)
    checklist = evaluate_demo_owner_approval_checklist(active.checklist_input)
    classification = _classify(active, readiness, phrase, checklist)
    return SupervisedDemoOwnerApprovalPacketResult(
        engine_version=SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_VERSION,
        classification=classification,
        owner_packet_review_allowed=classification
        == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW,
        readiness_status=readiness.classification,
        phrase_status=phrase.classification,
        checklist_status=checklist.classification,
        selected_strategy=readiness.selected_strategy,
        candidate_id=readiness.candidate_id,
        instrument=readiness.instrument,
        direction=readiness.direction,
        proposed_units=readiness.proposed_units,
        entry_price=readiness.entry_price,
        stop_loss=readiness.stop_loss,
        take_profit=readiness.take_profit,
        max_loss=readiness.max_loss,
        expected_reward=readiness.expected_reward,
        reward_to_risk=readiness.reward_to_risk,
        owner_warning=OWNER_WARNING,
        required_phrase=REQUIRED_OWNER_APPROVAL_PHRASE,
        blocked_actions=BLOCKED_ACTIONS,
        blockers=_blockers(classification, readiness, phrase, checklist),
        operator_summary=_operator_summary(classification),
        next_safe_action=_next_safe_action(classification),
        readiness_result=readiness,
        phrase_result=phrase,
        checklist_result=checklist,
        **_permission_defaults(),
    )


def supervised_demo_owner_approval_packet_to_jsonable_dict(
    result: SupervisedDemoOwnerApprovalPacketResult,
) -> dict[str, Any]:
    data = _json_value(result)
    data["readiness_result"] = supervised_demo_trade_readiness_epic_to_jsonable_dict(
        result.readiness_result
    )
    data["phrase_result"] = demo_owner_approval_phrase_gate_to_jsonable_dict(result.phrase_result)
    data["checklist_result"] = demo_owner_approval_checklist_to_jsonable_dict(result.checklist_result)
    return data


def supervised_demo_owner_approval_packet_to_operator_text(
    result: SupervisedDemoOwnerApprovalPacketResult | None = None,
) -> str:
    active = result or build_supervised_demo_owner_approval_packet()
    return (
        f"Supervised demo owner approval packet status: {active.classification}. "
        f"{active.operator_summary} Broker action and demo execution remain false. No trade was placed."
    )


def supervised_demo_owner_approval_packet_to_markdown(
    result: SupervisedDemoOwnerApprovalPacketResult | None = None,
) -> str:
    active = result or build_supervised_demo_owner_approval_packet()
    lines = [
        "# Supervised Demo Owner Approval Packet V1",
        "",
        active.owner_warning,
        "",
        "No broker call was made. No trade was placed.",
        "",
        f"- Status: {active.classification}",
        f"- Owner packet review allowed: {active.owner_packet_review_allowed}",
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
        "",
        "## Blocked Actions",
    ]
    lines.extend(f"- {item}" for item in active.blocked_actions)
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in active.blockers)
    lines.extend(["", f"Next safe action: {active.next_safe_action}"])
    return "\n".join(lines)


def _classify(
    value: SupervisedDemoOwnerApprovalPacketInput,
    readiness: SupervisedDemoTradeReadinessEpicResult,
    phrase: DemoOwnerApprovalPhraseGateResult,
    checklist: DemoOwnerApprovalChecklistResult,
) -> str:
    if value.protected_action_requested:
        return SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PROTECTED_ACTION
    if readiness.classification != SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW:
        return SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_READINESS
    if phrase.classification != DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW:
        return SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PHRASE
    if checklist.classification != DEMO_OWNER_APPROVAL_CHECKLIST_READY:
        return SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_CHECKLIST
    return SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW


def _blockers(
    classification: str,
    readiness: SupervisedDemoTradeReadinessEpicResult,
    phrase: DemoOwnerApprovalPhraseGateResult,
    checklist: DemoOwnerApprovalChecklistResult,
) -> tuple[str, ...]:
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW:
        return ()
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_READINESS:
        return (readiness.classification.lower(),)
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PHRASE:
        return phrase.blockers
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_CHECKLIST:
        return checklist.missing_items
    return ("protected action request detected",)


def _operator_summary(classification: str) -> str:
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW:
        return "The local owner approval packet is ready for Anthony's manual review only."
    return "The local owner approval packet is blocked and must not be used for execution."


def _next_safe_action(classification: str) -> str:
    if classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW:
        return "Anthony may review the packet manually; Codex must not execute or call a broker."
    return "Resolve owner approval packet blockers before any further supervised demo review."


def _coerce_input(
    value: SupervisedDemoOwnerApprovalPacketInput | Mapping[str, Any],
) -> SupervisedDemoOwnerApprovalPacketInput:
    if isinstance(value, SupervisedDemoOwnerApprovalPacketInput):
        return value
    raw = dict(value)
    return SupervisedDemoOwnerApprovalPacketInput(
        readiness_input=raw["readiness_input"],
        phrase_input=raw["phrase_input"],
        checklist_input=raw["checklist_input"],
        protected_action_requested=bool(raw.get("protected_action_requested", False)),
    )


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
