from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.demo_operator_execution_ticket_v1 import (
    DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW,
    DemoOperatorTicketInput,
    build_demo_operator_execution_ticket,
    demo_operator_ticket_to_jsonable_dict,
)
from automation.forex_engine.demo_order_plan_builder_v1 import (
    DEMO_ORDER_PLAN_REVIEW_READY,
    DemoOrderPlanInput,
    build_demo_order_plan,
    demo_order_plan_to_jsonable_dict,
)
from automation.forex_engine.demo_position_sizer_v1 import (
    DEMO_POSITION_SIZE_READY,
    DemoPositionSizerInput,
    build_sample_blocked_position_size_input,
    build_sample_position_size_input,
    calculate_demo_position_size,
    demo_position_size_to_jsonable_dict,
)
from automation.forex_engine.demo_trade_candidate_context_v1 import (
    DEMO_TRADE_CANDIDATE_CONTEXT_READY,
    DemoTradeCandidateContextInput,
    DemoTradeCandidateContextResult,
    build_sample_blocked_candidate_context_input,
    build_sample_ready_candidate_context_input,
    demo_trade_candidate_context_to_jsonable_dict,
    evaluate_demo_trade_candidate_context,
)
from automation.forex_engine.demo_trade_feedback_router_v1 import (
    DemoTradeFeedbackInput,
    feedback_to_jsonable_dict,
    route_demo_trade_feedback,
)
from automation.forex_engine.demo_trade_risk_gate_v1 import (
    DEMO_RISK_REVIEW_READY,
    DemoTradeRiskInput,
    build_sample_blocked_risk_input,
    build_sample_valid_risk_input,
    demo_trade_risk_to_jsonable_dict,
    evaluate_demo_trade_risk,
)
from automation.forex_engine.post_trade_evidence_capture_v1 import (
    build_sample_post_trade_missing_input,
    capture_post_trade_evidence,
    post_trade_evidence_to_jsonable_dict,
)
from automation.forex_engine.supervised_demo_broker_snapshot_intake_epic_v1 import (
    SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_ACCOUNT,
    SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW,
    SupervisedDemoBrokerSnapshotIntakeEpicInput,
    SupervisedDemoBrokerSnapshotIntakeEpicResult,
    build_sample_supervised_demo_snapshot_intake_blocked_input,
    build_sample_supervised_demo_snapshot_intake_ready_input,
    run_supervised_demo_broker_snapshot_intake_epic,
    supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict,
)


DEMO_TRADE_READINESS_BRIDGE_VERSION = "demo_trade_readiness_bridge_v1"

DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW = (
    "DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW"
)
DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT = "DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT"
DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ACCOUNT = "DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ACCOUNT"
DEMO_TRADE_READINESS_BRIDGE_BLOCKED_CANDIDATE = "DEMO_TRADE_READINESS_BRIDGE_BLOCKED_CANDIDATE"
DEMO_TRADE_READINESS_BRIDGE_BLOCKED_RISK = "DEMO_TRADE_READINESS_BRIDGE_BLOCKED_RISK"
DEMO_TRADE_READINESS_BRIDGE_BLOCKED_POSITION_SIZE = (
    "DEMO_TRADE_READINESS_BRIDGE_BLOCKED_POSITION_SIZE"
)
DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ORDER_PLAN = (
    "DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ORDER_PLAN"
)
DEMO_TRADE_READINESS_BRIDGE_BLOCKED_OPERATOR_TICKET = (
    "DEMO_TRADE_READINESS_BRIDGE_BLOCKED_OPERATOR_TICKET"
)


@dataclass(frozen=True)
class DemoTradeReadinessBridgeConfig:
    order_plan_operator_review_required: bool = True
    ticket_owner_approval_required: bool = True


@dataclass(frozen=True)
class DemoTradeReadinessBridgeInput:
    snapshot_input: SupervisedDemoBrokerSnapshotIntakeEpicInput | Mapping[str, Any]
    candidate_input: DemoTradeCandidateContextInput | Mapping[str, Any]
    risk_input: DemoTradeRiskInput | Mapping[str, Any]
    position_input: DemoPositionSizerInput | Mapping[str, Any]
    config: DemoTradeReadinessBridgeConfig = DemoTradeReadinessBridgeConfig()


@dataclass(frozen=True)
class DemoTradeReadinessBridgeResult:
    engine_version: str
    classification: str
    snapshot_intake_status: str
    snapshot_review_status: str
    account_status: str
    candidate_status: str
    risk_status: str
    position_size_status: str
    order_plan_status: str
    operator_ticket_status: str
    post_trade_capture_status: str
    feedback_router_status: str
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
    blockers: tuple[str, ...]
    operator_answer: str
    next_safe_action: str
    snapshot_result: SupervisedDemoBrokerSnapshotIntakeEpicResult
    candidate_result: DemoTradeCandidateContextResult
    risk_result: Any
    position_size_result: Any
    order_plan_result: Any
    operator_ticket_result: Any
    post_trade_capture_result: Any
    feedback_router_result: Any
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_demo_trade_readiness_bridge_ready_input() -> DemoTradeReadinessBridgeInput:
    return DemoTradeReadinessBridgeInput(
        snapshot_input=build_sample_supervised_demo_snapshot_intake_ready_input(),
        candidate_input=build_sample_ready_candidate_context_input(),
        risk_input=build_sample_valid_risk_input(),
        position_input=build_sample_position_size_input(),
    )


def build_sample_demo_trade_readiness_bridge_blocked_input() -> DemoTradeReadinessBridgeInput:
    return DemoTradeReadinessBridgeInput(
        snapshot_input=build_sample_supervised_demo_snapshot_intake_blocked_input(),
        candidate_input=build_sample_blocked_candidate_context_input(),
        risk_input=build_sample_blocked_risk_input(),
        position_input=build_sample_blocked_position_size_input(),
    )


def run_demo_trade_readiness_bridge(
    bridge_input: DemoTradeReadinessBridgeInput | Mapping[str, Any] | None = None,
) -> DemoTradeReadinessBridgeResult:
    active = _coerce_input(bridge_input or build_sample_demo_trade_readiness_bridge_ready_input())
    snapshot = run_supervised_demo_broker_snapshot_intake_epic(active.snapshot_input)
    candidate = evaluate_demo_trade_candidate_context(active.candidate_input)
    risk = evaluate_demo_trade_risk(active.risk_input)
    size = calculate_demo_position_size(active.position_input)

    order_plan = build_demo_order_plan(
        DemoOrderPlanInput(
            strategy_id=candidate.strategy_id,
            strategy_name=candidate.selected_strategy,
            supertrend_status=candidate.supertrend_status,
            instrument=candidate.instrument,
            direction=candidate.direction,
            entry_type="operator_review_market_entry",
            entry_price=size.sizing_input.entry_price,
            stop_loss_price=size.sizing_input.stop_loss_price,
            take_profit_price=size.sizing_input.take_profit_price,
            proposed_units=size.proposed_units,
            risk_amount=size.max_loss,
            estimated_reward=size.expected_reward,
            reward_to_risk=size.reward_to_risk,
            spread=_snapshot_spread(snapshot),
            max_spread=Decimal("1.5"),
            account_ready=snapshot.classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW,
            risk_ready=risk.classification == DEMO_RISK_REVIEW_READY,
            position_size_ready=size.sizing_status == DEMO_POSITION_SIZE_READY,
            operator_review_required=active.config.order_plan_operator_review_required,
        )
    )
    ticket = build_demo_operator_execution_ticket(
        DemoOperatorTicketInput(
            selected_strategy=candidate.selected_strategy,
            supertrend_status=candidate.supertrend_status,
            instrument=candidate.instrument,
            direction=candidate.direction,
            units=size.proposed_units,
            stop_loss=size.sizing_input.stop_loss_price,
            take_profit=size.sizing_input.take_profit_price,
            max_loss=size.max_loss,
            expected_reward=size.expected_reward,
            reason_for_trade="Local readiness bridge assembled a deterministic supervised demo review package.",
            reason_not_to_trade="Anthony has not explicitly approved execution and broker action remains locked.",
            checklist=(
                "Review sanitized broker snapshot intake.",
                "Review candidate, risk, and sizing gates.",
                "Review local order plan and operator ticket.",
                "Confirm Anthony explicitly approves before any demo action.",
            ),
            blocked_actions=("demo execution", "broker action", "real money", "compounding", "bank movement"),
            owner_approval_required=active.config.ticket_owner_approval_required,
            order_plan_present=order_plan.classification == DEMO_ORDER_PLAN_REVIEW_READY,
            risk_ready=risk.classification == DEMO_RISK_REVIEW_READY,
            broker_state_ready=snapshot.classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW,
        )
    )
    post_trade = capture_post_trade_evidence(build_sample_post_trade_missing_input())
    feedback = route_demo_trade_feedback(
        DemoTradeFeedbackInput(
            post_trade_evidence_present=False,
            post_trade_status=post_trade.classification,
            strategy_id=candidate.strategy_id,
            result="PENDING",
            realized_pl=None,
            broker_reconciled=False,
            sanitized=True,
            notes="Feedback remains pending until supervised demo post-trade evidence exists.",
        )
    )
    classification = _classify(snapshot, candidate, risk, size, order_plan, ticket)
    return DemoTradeReadinessBridgeResult(
        engine_version=DEMO_TRADE_READINESS_BRIDGE_VERSION,
        classification=classification,
        snapshot_intake_status=snapshot.intake_status,
        snapshot_review_status=snapshot.review_packet_result.classification,
        account_status=snapshot.account_status,
        candidate_status=candidate.classification,
        risk_status=risk.classification,
        position_size_status=size.sizing_status,
        order_plan_status=order_plan.classification,
        operator_ticket_status=ticket.classification,
        post_trade_capture_status=post_trade.classification,
        feedback_router_status=feedback.classification,
        selected_strategy=candidate.selected_strategy,
        candidate_id=candidate.candidate_id,
        instrument=candidate.instrument,
        direction=candidate.direction,
        proposed_units=size.proposed_units,
        entry_price=size.sizing_input.entry_price,
        stop_loss=size.sizing_input.stop_loss_price,
        take_profit=size.sizing_input.take_profit_price,
        max_loss=size.max_loss,
        expected_reward=size.expected_reward,
        reward_to_risk=size.reward_to_risk,
        blockers=_blockers(classification, snapshot, candidate, risk, size, order_plan, ticket),
        operator_answer=_operator_answer(classification),
        next_safe_action=_next_safe_action(classification),
        snapshot_result=snapshot,
        candidate_result=candidate,
        risk_result=risk,
        position_size_result=size,
        order_plan_result=order_plan,
        operator_ticket_result=ticket,
        post_trade_capture_result=post_trade,
        feedback_router_result=feedback,
        **_permission_defaults(),
    )


def demo_trade_readiness_bridge_to_jsonable_dict(result: DemoTradeReadinessBridgeResult) -> dict[str, Any]:
    data = _json_value(result)
    data["snapshot_result"] = supervised_demo_broker_snapshot_intake_epic_to_jsonable_dict(
        result.snapshot_result
    )
    data["candidate_result"] = demo_trade_candidate_context_to_jsonable_dict(result.candidate_result)
    data["risk_result"] = demo_trade_risk_to_jsonable_dict(result.risk_result)
    data["position_size_result"] = demo_position_size_to_jsonable_dict(result.position_size_result)
    data["order_plan_result"] = demo_order_plan_to_jsonable_dict(result.order_plan_result)
    data["operator_ticket_result"] = demo_operator_ticket_to_jsonable_dict(result.operator_ticket_result)
    data["post_trade_capture_result"] = post_trade_evidence_to_jsonable_dict(result.post_trade_capture_result)
    data["feedback_router_result"] = feedback_to_jsonable_dict(result.feedback_router_result)
    return data


def demo_trade_readiness_bridge_to_operator_text(
    result: DemoTradeReadinessBridgeResult | None = None,
) -> str:
    active = result or run_demo_trade_readiness_bridge()
    return (
        f"Demo trade readiness bridge status: {active.classification}. "
        f"{active.selected_strategy} {active.direction} {active.instrument}, "
        f"{active.proposed_units} units. {active.operator_answer} No trade was placed."
    )


def demo_trade_readiness_bridge_to_markdown(
    result: DemoTradeReadinessBridgeResult | None = None,
) -> str:
    active = result or run_demo_trade_readiness_bridge()
    return "\n".join(
        [
            "# Demo Trade Readiness Bridge V1",
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Snapshot intake status: {active.snapshot_intake_status}",
            f"- Snapshot review status: {active.snapshot_review_status}",
            f"- Account status: {active.account_status}",
            f"- Candidate status: {active.candidate_status}",
            f"- Risk status: {active.risk_status}",
            f"- Position size status: {active.position_size_status}",
            f"- Order plan status: {active.order_plan_status}",
            f"- Operator ticket status: {active.operator_ticket_status}",
            f"- Post-trade capture status: {active.post_trade_capture_status}",
            f"- Feedback router status: {active.feedback_router_status}",
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
            f"- Demo execution allowed: {active.demo_execution_allowed}",
            f"- Broker action allowed: {active.broker_action_allowed}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _coerce_input(value: DemoTradeReadinessBridgeInput | Mapping[str, Any]) -> DemoTradeReadinessBridgeInput:
    if isinstance(value, DemoTradeReadinessBridgeInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoTradeReadinessBridgeConfig())
    if not isinstance(config, DemoTradeReadinessBridgeConfig):
        config = DemoTradeReadinessBridgeConfig(**dict(config))
    return DemoTradeReadinessBridgeInput(
        snapshot_input=raw["snapshot_input"],
        candidate_input=raw["candidate_input"],
        risk_input=raw["risk_input"],
        position_input=raw["position_input"],
        config=config,
    )


def _classify(snapshot: Any, candidate: Any, risk: Any, size: Any, order_plan: Any, ticket: Any) -> str:
    if snapshot.classification != SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_READY_FOR_REVIEW:
        if snapshot.classification == SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_ACCOUNT:
            return DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ACCOUNT
        return DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT
    if candidate.classification != DEMO_TRADE_CANDIDATE_CONTEXT_READY:
        return DEMO_TRADE_READINESS_BRIDGE_BLOCKED_CANDIDATE
    if risk.classification != DEMO_RISK_REVIEW_READY:
        return DEMO_TRADE_READINESS_BRIDGE_BLOCKED_RISK
    if size.sizing_status != DEMO_POSITION_SIZE_READY:
        return DEMO_TRADE_READINESS_BRIDGE_BLOCKED_POSITION_SIZE
    if order_plan.classification != DEMO_ORDER_PLAN_REVIEW_READY:
        return DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ORDER_PLAN
    if ticket.classification != DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW:
        return DEMO_TRADE_READINESS_BRIDGE_BLOCKED_OPERATOR_TICKET
    return DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW


def _blockers(
    classification: str,
    snapshot: Any,
    candidate: Any,
    risk: Any,
    size: Any,
    order_plan: Any,
    ticket: Any,
) -> tuple[str, ...]:
    if classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW:
        return ()
    if classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT:
        return tuple(snapshot.review_packet_result.blockers) or (snapshot.classification.lower(),)
    if classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ACCOUNT:
        return tuple(snapshot.review_packet_result.blockers) or (snapshot.account_status.lower(),)
    if classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_CANDIDATE:
        return candidate.blockers
    if classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_RISK:
        return risk.blockers
    if classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_POSITION_SIZE:
        return size.blockers
    if classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ORDER_PLAN:
        return order_plan.blockers
    return ticket.blocked_actions or (ticket.classification.lower(),)


def _operator_answer(classification: str) -> str:
    if classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW:
        return "The local review package is ready, but execution remains locked until Anthony explicitly approves."
    return "The local review package is blocked and must not be used for execution."


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW:
        return "Anthony may review the bundle manually; Codex must not execute or approve broker action."
    return "Resolve the bridge blocker before preparing an owner review bundle."


def _snapshot_spread(snapshot: SupervisedDemoBrokerSnapshotIntakeEpicResult) -> Decimal:
    review = snapshot.review_packet_result
    if review.spread is not None:
        return review.spread
    return Decimal("0")


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
