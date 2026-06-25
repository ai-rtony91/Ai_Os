from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.demo_manual_execution_exception_checklist_v1 import (
    DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY,
    DemoManualExecutionExceptionChecklistInput,
    DemoManualExecutionExceptionChecklistResult,
    build_sample_blocked_manual_execution_exception_checklist_input,
    build_sample_ready_manual_execution_exception_checklist_input,
    demo_manual_execution_exception_checklist_to_jsonable_dict,
    evaluate_demo_manual_execution_exception_checklist,
)
from automation.forex_engine.demo_manual_execution_exception_scope_gate_v1 import (
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW,
    EXCEPTION_WARNING,
    OWNER_WARNING,
    REQUIRED_EXCEPTION_PHRASE,
    DemoManualExecutionExceptionScopeInput,
    DemoManualExecutionExceptionScopeResult,
    build_sample_missing_manual_execution_exception_scope_input,
    build_sample_valid_manual_execution_exception_scope_input,
    demo_manual_execution_exception_scope_to_jsonable_dict,
    evaluate_demo_manual_execution_exception_scope,
)
from automation.forex_engine.supervised_demo_owner_approval_epic_v1 import (
    SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW,
    SupervisedDemoOwnerApprovalEpicInput,
    SupervisedDemoOwnerApprovalEpicResult,
    build_sample_supervised_demo_owner_approval_blocked_input,
    build_sample_supervised_demo_owner_approval_ready_input,
    run_supervised_demo_owner_approval_epic,
    supervised_demo_owner_approval_epic_to_jsonable_dict,
)


SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_VERSION = (
    "supervised_demo_manual_execution_exception_packet_v1"
)

SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW = (
    "SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW"
)
SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_OWNER_APPROVAL = (
    "SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_OWNER_APPROVAL"
)
SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_SCOPE = (
    "SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_SCOPE"
)
SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_CHECKLIST = (
    "SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_CHECKLIST"
)
SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_PROTECTED_ACTION = (
    "SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_PROTECTED_ACTION"
)

ENTRY_TYPE = "operator_review_market_entry"
BLOCKED_ACTIONS = (
    "Codex demo execution",
    "Codex broker call",
    "broker action",
    "credential access",
    "account id persistence",
    "live trading",
    "real money",
    "compounding",
    "bank movement",
)


@dataclass(frozen=True)
class SupervisedDemoManualExecutionExceptionPacketInput:
    owner_approval_input: SupervisedDemoOwnerApprovalEpicInput | Mapping[str, Any]
    scope_input: DemoManualExecutionExceptionScopeInput | Mapping[str, Any]
    checklist_input: DemoManualExecutionExceptionChecklistInput | Mapping[str, Any]
    protected_action_requested: bool = False


@dataclass(frozen=True)
class SupervisedDemoManualExecutionExceptionPacketResult:
    engine_version: str
    classification: str
    exception_packet_review_allowed: bool
    owner_approval_status: str
    scope_status: str
    checklist_status: str
    selected_strategy: str
    candidate_id: str
    instrument: str
    direction: str
    entry_type: str
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    proposed_units: int
    max_loss: Decimal
    expected_reward: Decimal
    reward_to_risk: Decimal
    owner_warning: str
    exception_warning: str
    required_phrase: str
    blocked_actions: tuple[str, ...]
    blockers: tuple[str, ...]
    operator_summary: str
    next_safe_action: str
    post_trade_evidence_required: bool
    feedback_routing_required: bool
    owner_approval_result: SupervisedDemoOwnerApprovalEpicResult
    scope_result: DemoManualExecutionExceptionScopeResult
    checklist_result: DemoManualExecutionExceptionChecklistResult
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_supervised_demo_manual_execution_exception_packet_ready_input() -> SupervisedDemoManualExecutionExceptionPacketInput:
    return SupervisedDemoManualExecutionExceptionPacketInput(
        owner_approval_input=build_sample_supervised_demo_owner_approval_ready_input(),
        scope_input=build_sample_valid_manual_execution_exception_scope_input(),
        checklist_input=build_sample_ready_manual_execution_exception_checklist_input(),
    )


def build_sample_supervised_demo_manual_execution_exception_packet_blocked_input() -> SupervisedDemoManualExecutionExceptionPacketInput:
    return SupervisedDemoManualExecutionExceptionPacketInput(
        owner_approval_input=build_sample_supervised_demo_owner_approval_blocked_input(),
        scope_input=build_sample_missing_manual_execution_exception_scope_input(),
        checklist_input=build_sample_blocked_manual_execution_exception_checklist_input(),
    )


def build_supervised_demo_manual_execution_exception_packet(
    packet_input: SupervisedDemoManualExecutionExceptionPacketInput | Mapping[str, Any] | None = None,
) -> SupervisedDemoManualExecutionExceptionPacketResult:
    active = _coerce_input(
        packet_input or build_sample_supervised_demo_manual_execution_exception_packet_ready_input()
    )
    owner = run_supervised_demo_owner_approval_epic(active.owner_approval_input)
    scope = evaluate_demo_manual_execution_exception_scope(active.scope_input)
    checklist = evaluate_demo_manual_execution_exception_checklist(active.checklist_input)
    classification = _classify(active, owner, scope, checklist)
    return SupervisedDemoManualExecutionExceptionPacketResult(
        engine_version=SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_VERSION,
        classification=classification,
        exception_packet_review_allowed=classification
        == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW,
        owner_approval_status=owner.classification,
        scope_status=scope.classification,
        checklist_status=checklist.classification,
        selected_strategy=owner.selected_strategy,
        candidate_id=owner.candidate_id,
        instrument=owner.instrument,
        direction=owner.direction,
        entry_type=ENTRY_TYPE,
        entry_price=owner.entry_price,
        stop_loss=owner.stop_loss,
        take_profit=owner.take_profit,
        proposed_units=owner.proposed_units,
        max_loss=owner.max_loss,
        expected_reward=owner.expected_reward,
        reward_to_risk=owner.reward_to_risk,
        owner_warning=OWNER_WARNING,
        exception_warning=EXCEPTION_WARNING,
        required_phrase=REQUIRED_EXCEPTION_PHRASE,
        blocked_actions=BLOCKED_ACTIONS,
        blockers=_blockers(classification, owner, scope, checklist),
        operator_summary=_operator_summary(classification),
        next_safe_action=_next_safe_action(classification),
        post_trade_evidence_required=True,
        feedback_routing_required=True,
        owner_approval_result=owner,
        scope_result=scope,
        checklist_result=checklist,
        **_permission_defaults(),
    )


def supervised_demo_manual_execution_exception_packet_to_jsonable_dict(
    result: SupervisedDemoManualExecutionExceptionPacketResult,
) -> dict[str, Any]:
    data = _json_value(result)
    data["owner_approval_result"] = supervised_demo_owner_approval_epic_to_jsonable_dict(
        result.owner_approval_result
    )
    data["scope_result"] = demo_manual_execution_exception_scope_to_jsonable_dict(
        result.scope_result
    )
    data["checklist_result"] = demo_manual_execution_exception_checklist_to_jsonable_dict(
        result.checklist_result
    )
    return data


def supervised_demo_manual_execution_exception_packet_to_operator_text(
    result: SupervisedDemoManualExecutionExceptionPacketResult | None = None,
) -> str:
    active = result or build_supervised_demo_manual_execution_exception_packet()
    return (
        f"Supervised demo manual execution exception packet status: {active.classification}. "
        f"{active.operator_summary} Codex cannot execute, call a broker, or place orders. "
        "No trade was placed."
    )


def supervised_demo_manual_execution_exception_packet_to_markdown(
    result: SupervisedDemoManualExecutionExceptionPacketResult | None = None,
) -> str:
    active = result or build_supervised_demo_manual_execution_exception_packet()
    lines = [
        "# Supervised Demo Manual Execution Exception Packet V1",
        "",
        active.owner_warning,
        active.exception_warning,
        "",
        "No broker call was made. No trade was placed.",
        "",
        f"- Status: {active.classification}",
        f"- Exception packet review allowed: {active.exception_packet_review_allowed}",
        f"- Owner approval status: {active.owner_approval_status}",
        f"- Scope status: {active.scope_status}",
        f"- Checklist status: {active.checklist_status}",
        f"- Selected strategy: {active.selected_strategy}",
        f"- Candidate id: {active.candidate_id}",
        f"- Instrument: {active.instrument}",
        f"- Direction: {active.direction}",
        f"- Entry type: {active.entry_type}",
        f"- Entry price: {active.entry_price}",
        f"- Stop loss: {active.stop_loss}",
        f"- Take profit: {active.take_profit}",
        f"- Proposed units: {active.proposed_units}",
        f"- Max loss: {active.max_loss}",
        f"- Expected reward: {active.expected_reward}",
        f"- Reward-to-risk: {active.reward_to_risk}",
        f"- Required phrase: {active.required_phrase}",
        f"- Post-trade evidence required: {active.post_trade_evidence_required}",
        f"- Feedback routing required: {active.feedback_routing_required}",
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
    value: SupervisedDemoManualExecutionExceptionPacketInput,
    owner: SupervisedDemoOwnerApprovalEpicResult,
    scope: DemoManualExecutionExceptionScopeResult,
    checklist: DemoManualExecutionExceptionChecklistResult,
) -> str:
    if value.protected_action_requested:
        return SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_PROTECTED_ACTION
    if owner.classification != SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW:
        return SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_OWNER_APPROVAL
    if scope.classification != DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW:
        return SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_SCOPE
    if checklist.classification != DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY:
        return SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_CHECKLIST
    return SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW


def _blockers(
    classification: str,
    owner: SupervisedDemoOwnerApprovalEpicResult,
    scope: DemoManualExecutionExceptionScopeResult,
    checklist: DemoManualExecutionExceptionChecklistResult,
) -> tuple[str, ...]:
    if classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW:
        return ()
    if classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_OWNER_APPROVAL:
        return (owner.classification.lower(),)
    if classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_SCOPE:
        return scope.blockers
    if classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_CHECKLIST:
        return checklist.missing_items
    return ("protected action request detected",)


def _operator_summary(classification: str) -> str:
    if classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW:
        return "The local manual execution exception packet is ready for Anthony's manual review only."
    return "The local manual execution exception packet is blocked and must not be used for execution."


def _next_safe_action(classification: str) -> str:
    if classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW:
        return "Anthony may manually review the exception packet outside Codex; Codex must not execute or call a broker."
    return "Resolve manual exception packet blockers before owner review can continue."


def _coerce_input(
    value: SupervisedDemoManualExecutionExceptionPacketInput | Mapping[str, Any],
) -> SupervisedDemoManualExecutionExceptionPacketInput:
    if isinstance(value, SupervisedDemoManualExecutionExceptionPacketInput):
        return value
    raw = dict(value)
    return SupervisedDemoManualExecutionExceptionPacketInput(
        owner_approval_input=raw["owner_approval_input"],
        scope_input=raw["scope_input"],
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
