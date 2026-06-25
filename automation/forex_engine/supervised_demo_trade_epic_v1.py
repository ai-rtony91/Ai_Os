from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.demo_account_readiness_gate_v1 import (
    DEMO_ACCOUNT_READY_FOR_REVIEW,
    DemoAccountReadinessInput,
    build_sample_blocked_account_input,
    build_sample_ready_account_input,
    demo_account_readiness_to_jsonable_dict,
    evaluate_demo_account_readiness,
)
from automation.forex_engine.demo_operator_execution_ticket_v1 import (
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
    build_sample_position_size_input,
    calculate_demo_position_size,
    demo_position_size_to_jsonable_dict,
)
from automation.forex_engine.demo_trade_risk_gate_v1 import (
    DEMO_RISK_REVIEW_READY,
    DemoTradeRiskInput,
    build_sample_blocked_risk_input,
    build_sample_valid_risk_input,
    demo_trade_risk_to_jsonable_dict,
    evaluate_demo_trade_risk,
)


SUPERVISED_DEMO_TRADE_EPIC_VERSION = "supervised_demo_trade_epic_v1"

SUPERVISED_DEMO_TRADE_REVIEW_READY = "SUPERVISED_DEMO_TRADE_REVIEW_READY"
SUPERVISED_DEMO_TRADE_BLOCKED_ACCOUNT = "SUPERVISED_DEMO_TRADE_BLOCKED_ACCOUNT"
SUPERVISED_DEMO_TRADE_BLOCKED_RISK = "SUPERVISED_DEMO_TRADE_BLOCKED_RISK"
SUPERVISED_DEMO_TRADE_BLOCKED_POSITION_SIZE = "SUPERVISED_DEMO_TRADE_BLOCKED_POSITION_SIZE"
SUPERVISED_DEMO_TRADE_BLOCKED_ORDER_PLAN = "SUPERVISED_DEMO_TRADE_BLOCKED_ORDER_PLAN"
SUPERVISED_DEMO_TRADE_BLOCKED_OPERATOR_APPROVAL = "SUPERVISED_DEMO_TRADE_BLOCKED_OPERATOR_APPROVAL"
SUPERVISED_DEMO_TRADE_BLOCKED_BROKER_ACTION_LOCKED = "SUPERVISED_DEMO_TRADE_BLOCKED_BROKER_ACTION_LOCKED"
SUPERVISED_DEMO_TRADE_BLOCKED_REAL_MONEY_LOCKED = "SUPERVISED_DEMO_TRADE_BLOCKED_REAL_MONEY_LOCKED"
SUPERVISED_DEMO_TRADE_BLOCKED_COMPOUNDING_LOCKED = "SUPERVISED_DEMO_TRADE_BLOCKED_COMPOUNDING_LOCKED"

POST_TRADE_CAPTURE_PENDING = "POST_TRADE_EVIDENCE_PENDING_AFTER_SUPERVISED_DEMO_TRADE"
FEEDBACK_ROUTER_PENDING = "FEEDBACK_PENDING_POST_TRADE_EVIDENCE"


@dataclass(frozen=True)
class SupervisedDemoTradeEpicConfig:
    selected_strategy: str = "Supertrend"
    strategy_id: str = "supertrend"
    supertrend_status: str = "SUPER_TREND_PROOF_REVIEW_READY"
    instrument: str = "EUR_USD"
    direction: str = "LONG"
    operator_review_required: bool = True


@dataclass(frozen=True)
class SupervisedDemoTradeEpicInput:
    config: SupervisedDemoTradeEpicConfig
    account_input: DemoAccountReadinessInput
    risk_input: DemoTradeRiskInput
    position_input: DemoPositionSizerInput


@dataclass(frozen=True)
class SupervisedDemoTradeEpicResult:
    engine_version: str
    classification: str
    selected_strategy: str
    supertrend_status: str
    instrument: str
    direction: str
    proposed_units: int
    stop_loss: Decimal
    take_profit: Decimal
    max_loss: Decimal
    expected_reward: Decimal
    reward_to_risk: Decimal
    account_status: str
    risk_status: str
    position_size_status: str
    order_plan_status: str
    operator_ticket_status: str
    post_trade_capture_status: str
    feedback_router_status: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    next_safe_action: str
    operator_answer: str
    account_result: Any
    risk_result: Any
    position_size_result: Any
    order_plan_result: Any
    operator_ticket_result: Any


def build_sample_supervised_demo_ready_input() -> SupervisedDemoTradeEpicInput:
    return SupervisedDemoTradeEpicInput(
        config=SupervisedDemoTradeEpicConfig(),
        account_input=build_sample_ready_account_input(),
        risk_input=build_sample_valid_risk_input(),
        position_input=build_sample_position_size_input(),
    )


def build_sample_supervised_demo_blocked_input() -> SupervisedDemoTradeEpicInput:
    return SupervisedDemoTradeEpicInput(
        config=SupervisedDemoTradeEpicConfig(),
        account_input=build_sample_blocked_account_input(),
        risk_input=build_sample_blocked_risk_input(),
        position_input=build_sample_position_size_input(),
    )


def run_supervised_demo_trade_epic(
    epic_input: SupervisedDemoTradeEpicInput | Mapping[str, Any] | None = None,
) -> SupervisedDemoTradeEpicResult:
    active = _coerce_input(epic_input or build_sample_supervised_demo_ready_input())
    account = evaluate_demo_account_readiness(active.account_input)
    risk = evaluate_demo_trade_risk(active.risk_input)
    size = calculate_demo_position_size(active.position_input)
    plan_input = DemoOrderPlanInput(
        strategy_id=active.config.strategy_id,
        strategy_name=active.config.selected_strategy,
        supertrend_status=active.config.supertrend_status,
        instrument=active.config.instrument,
        direction=active.config.direction,
        entry_type="operator_review_market_entry",
        entry_price=active.position_input.entry_price,
        stop_loss_price=active.position_input.stop_loss_price,
        take_profit_price=active.position_input.take_profit_price,
        proposed_units=size.proposed_units,
        risk_amount=size.max_loss,
        estimated_reward=size.expected_reward,
        reward_to_risk=size.reward_to_risk,
        spread=account.broker_snapshot_result.snapshot.spread,
        max_spread=account.broker_snapshot_result.snapshot.spread
        if account.classification != DEMO_ACCOUNT_READY_FOR_REVIEW
        else active.account_input.config.max_spread,
        account_ready=account.classification == DEMO_ACCOUNT_READY_FOR_REVIEW,
        risk_ready=risk.classification == DEMO_RISK_REVIEW_READY,
        position_size_ready=size.sizing_status == DEMO_POSITION_SIZE_READY,
        operator_review_required=active.config.operator_review_required,
    )
    order_plan = build_demo_order_plan(plan_input)
    ticket_input = DemoOperatorTicketInput(
        selected_strategy=active.config.selected_strategy,
        supertrend_status=active.config.supertrend_status,
        instrument=active.config.instrument,
        direction=active.config.direction,
        units=size.proposed_units,
        stop_loss=active.position_input.stop_loss_price,
        take_profit=active.position_input.take_profit_price,
        max_loss=size.max_loss,
        expected_reward=size.expected_reward,
        reason_for_trade="Supertrend is the strongest deterministic proof-review sample.",
        reason_not_to_trade="Owner approval is required and broker action remains locked.",
        checklist=(
            "Review sanitized broker snapshot.",
            "Review account, risk, and position-size gates.",
            "Confirm no unknown exposure.",
            "Confirm Anthony explicitly approves before any demo action.",
        ),
        blocked_actions=("broker action", "real money", "compounding", "bank movement", "live trading"),
        owner_approval_required=True,
        order_plan_present=order_plan.classification == DEMO_ORDER_PLAN_REVIEW_READY,
        risk_ready=risk.classification == DEMO_RISK_REVIEW_READY,
        broker_state_ready=account.classification == DEMO_ACCOUNT_READY_FOR_REVIEW,
    )
    ticket = build_demo_operator_execution_ticket(ticket_input)
    classification = _classify(account, risk, size, order_plan, ticket)
    return SupervisedDemoTradeEpicResult(
        engine_version=SUPERVISED_DEMO_TRADE_EPIC_VERSION,
        classification=classification,
        selected_strategy=active.config.selected_strategy,
        supertrend_status=active.config.supertrend_status,
        instrument=active.config.instrument,
        direction=active.config.direction,
        proposed_units=size.proposed_units,
        stop_loss=active.position_input.stop_loss_price,
        take_profit=active.position_input.take_profit_price,
        max_loss=size.max_loss,
        expected_reward=size.expected_reward,
        reward_to_risk=size.reward_to_risk,
        account_status=account.classification,
        risk_status=risk.classification,
        position_size_status=size.sizing_status,
        order_plan_status=order_plan.classification,
        operator_ticket_status=ticket.classification,
        post_trade_capture_status=POST_TRADE_CAPTURE_PENDING,
        feedback_router_status=FEEDBACK_ROUTER_PENDING,
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        next_safe_action=_next_safe_action(classification),
        operator_answer=_operator_answer(classification),
        account_result=account,
        risk_result=risk,
        position_size_result=size,
        order_plan_result=order_plan,
        operator_ticket_result=ticket,
    )


def supervised_demo_epic_to_jsonable_dict(result: SupervisedDemoTradeEpicResult) -> dict[str, Any]:
    return _json_value(result)


def supervised_demo_epic_to_operator_text(result: SupervisedDemoTradeEpicResult | None = None) -> str:
    active = result or run_supervised_demo_trade_epic()
    return (
        f"Supervised demo trade package status: {active.classification}. "
        f"{active.selected_strategy} {active.direction} {active.instrument}, {active.proposed_units} units. "
        f"{active.operator_answer} No trade was placed."
    )


def supervised_demo_epic_to_markdown(result: SupervisedDemoTradeEpicResult | None = None) -> str:
    active = result or run_supervised_demo_trade_epic()
    return "\n".join(
        [
            "# Supervised Demo Trade Epic V1",
            "",
            "No trade was placed. This package is for owner review only.",
            "",
            f"- Status: {active.classification}",
            f"- Selected strategy: {active.selected_strategy}",
            f"- Supertrend status: {active.supertrend_status}",
            f"- Proposed instrument: {active.instrument}",
            f"- Proposed direction: {active.direction}",
            f"- Proposed units: {active.proposed_units}",
            f"- Stop loss: {active.stop_loss}",
            f"- Take profit: {active.take_profit}",
            f"- Max loss: {active.max_loss}",
            f"- Expected reward: {active.expected_reward}",
            f"- Reward-to-risk: {active.reward_to_risk}",
            f"- Account status: {active.account_status}",
            f"- Risk status: {active.risk_status}",
            f"- Order plan status: {active.order_plan_status}",
            f"- Operator ticket status: {active.operator_ticket_status}",
            f"- Post-trade capture status: {active.post_trade_capture_status}",
            f"- Feedback router status: {active.feedback_router_status}",
            f"- Demo execution allowed: {active.demo_execution_allowed}",
            f"- Broker action allowed: {active.broker_action_allowed}",
            f"- Real money allowed: {active.real_money_allowed}",
            f"- Compounding allowed: {active.compounding_allowed}",
            f"- Bank movement allowed: {active.bank_movement_allowed}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _classify(account: Any, risk: Any, size: Any, order_plan: Any, ticket: Any) -> str:
    if account.classification != DEMO_ACCOUNT_READY_FOR_REVIEW:
        return SUPERVISED_DEMO_TRADE_BLOCKED_ACCOUNT
    if risk.classification != DEMO_RISK_REVIEW_READY:
        return SUPERVISED_DEMO_TRADE_BLOCKED_RISK
    if size.sizing_status != DEMO_POSITION_SIZE_READY:
        return SUPERVISED_DEMO_TRADE_BLOCKED_POSITION_SIZE
    if order_plan.classification != DEMO_ORDER_PLAN_REVIEW_READY:
        return SUPERVISED_DEMO_TRADE_BLOCKED_ORDER_PLAN
    if "READY" not in ticket.classification:
        return SUPERVISED_DEMO_TRADE_BLOCKED_OPERATOR_APPROVAL
    return SUPERVISED_DEMO_TRADE_REVIEW_READY


def _next_safe_action(classification: str) -> str:
    if classification == SUPERVISED_DEMO_TRADE_REVIEW_READY:
        return "Anthony may review the ticket manually; Codex must not execute or approve broker action."
    return "Resolve the blocked gate before asking Anthony to consider supervised demo execution."


def _operator_answer(classification: str) -> str:
    if classification == SUPERVISED_DEMO_TRADE_REVIEW_READY:
        return "The review package is ready, but execution remains locked until Anthony explicitly approves."
    return "The review package is blocked and must not be used for execution."


def _coerce_input(value: SupervisedDemoTradeEpicInput | Mapping[str, Any]) -> SupervisedDemoTradeEpicInput:
    if isinstance(value, SupervisedDemoTradeEpicInput):
        return value
    raw = dict(value)
    config = raw.get("config", SupervisedDemoTradeEpicConfig())
    if not isinstance(config, SupervisedDemoTradeEpicConfig):
        config = SupervisedDemoTradeEpicConfig(**dict(config))
    return SupervisedDemoTradeEpicInput(
        config=config,
        account_input=raw["account_input"],
        risk_input=raw["risk_input"],
        position_input=raw["position_input"],
    )


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


def _nested_summary(result: SupervisedDemoTradeEpicResult) -> dict[str, Any]:
    return {
        "account": demo_account_readiness_to_jsonable_dict(result.account_result),
        "risk": demo_trade_risk_to_jsonable_dict(result.risk_result),
        "position_size": demo_position_size_to_jsonable_dict(result.position_size_result),
        "order_plan": demo_order_plan_to_jsonable_dict(result.order_plan_result),
        "operator_ticket": demo_operator_ticket_to_jsonable_dict(result.operator_ticket_result),
    }
