from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.supervised_demo_trade_review_bundle_v1 import (
    SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY,
    SupervisedDemoTradeReviewBundleInput,
    SupervisedDemoTradeReviewBundleResult,
    build_sample_supervised_demo_trade_review_bundle_blocked_input,
    build_sample_supervised_demo_trade_review_bundle_ready_input,
    build_supervised_demo_trade_review_bundle,
    supervised_demo_trade_review_bundle_to_jsonable_dict,
)


SUPERVISED_DEMO_TRADE_READINESS_EPIC_VERSION = "supervised_demo_trade_readiness_epic_v1"

SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW = (
    "SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW"
)
SUPERVISED_DEMO_TRADE_READINESS_BLOCKED = "SUPERVISED_DEMO_TRADE_READINESS_BLOCKED"


@dataclass(frozen=True)
class SupervisedDemoTradeReadinessEpicConfig:
    package_name: str = "Supervised Demo Trade Readiness V1"


@dataclass(frozen=True)
class SupervisedDemoTradeReadinessEpicInput:
    config: SupervisedDemoTradeReadinessEpicConfig
    review_bundle_input: SupervisedDemoTradeReviewBundleInput | Mapping[str, Any]


@dataclass(frozen=True)
class SupervisedDemoTradeReadinessEpicResult:
    engine_version: str
    classification: str
    readiness_bridge_status: str
    review_bundle_status: str
    snapshot_intake_status: str
    account_status: str
    candidate_status: str
    risk_status: str
    position_size_status: str
    order_plan_status: str
    operator_ticket_status: str
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
    review_bundle_result: SupervisedDemoTradeReviewBundleResult


def build_sample_supervised_demo_trade_readiness_ready_input() -> SupervisedDemoTradeReadinessEpicInput:
    return SupervisedDemoTradeReadinessEpicInput(
        config=SupervisedDemoTradeReadinessEpicConfig(),
        review_bundle_input=build_sample_supervised_demo_trade_review_bundle_ready_input(),
    )


def build_sample_supervised_demo_trade_readiness_blocked_input() -> SupervisedDemoTradeReadinessEpicInput:
    return SupervisedDemoTradeReadinessEpicInput(
        config=SupervisedDemoTradeReadinessEpicConfig(),
        review_bundle_input=build_sample_supervised_demo_trade_review_bundle_blocked_input(),
    )


def run_supervised_demo_trade_readiness_epic(
    epic_input: SupervisedDemoTradeReadinessEpicInput | Mapping[str, Any] | None = None,
) -> SupervisedDemoTradeReadinessEpicResult:
    active = _coerce_input(epic_input or build_sample_supervised_demo_trade_readiness_ready_input())
    bundle = build_supervised_demo_trade_review_bundle(active.review_bundle_input)
    bridge = bundle.bridge_result
    classification = (
        SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW
        if bundle.classification == SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY
        else SUPERVISED_DEMO_TRADE_READINESS_BLOCKED
    )
    return SupervisedDemoTradeReadinessEpicResult(
        engine_version=SUPERVISED_DEMO_TRADE_READINESS_EPIC_VERSION,
        classification=classification,
        readiness_bridge_status=bridge.classification,
        review_bundle_status=bundle.classification,
        snapshot_intake_status=bridge.snapshot_intake_status,
        account_status=bridge.account_status,
        candidate_status=bridge.candidate_status,
        risk_status=bridge.risk_status,
        position_size_status=bridge.position_size_status,
        order_plan_status=bridge.order_plan_status,
        operator_ticket_status=bridge.operator_ticket_status,
        selected_strategy=bridge.selected_strategy,
        candidate_id=bridge.candidate_id,
        instrument=bridge.instrument,
        direction=bridge.direction,
        proposed_units=bridge.proposed_units,
        entry_price=bridge.entry_price,
        stop_loss=bridge.stop_loss,
        take_profit=bridge.take_profit,
        max_loss=bridge.max_loss,
        expected_reward=bridge.expected_reward,
        reward_to_risk=bridge.reward_to_risk,
        operator_answer=_operator_answer(classification),
        next_safe_action=_next_safe_action(classification),
        review_bundle_result=bundle,
        **_permission_defaults(),
    )


def supervised_demo_trade_readiness_epic_to_jsonable_dict(
    result: SupervisedDemoTradeReadinessEpicResult,
) -> dict[str, Any]:
    data = _json_value(result)
    data["review_bundle_result"] = supervised_demo_trade_review_bundle_to_jsonable_dict(
        result.review_bundle_result
    )
    return data


def supervised_demo_trade_readiness_epic_to_operator_text(
    result: SupervisedDemoTradeReadinessEpicResult | None = None,
) -> str:
    active = result or run_supervised_demo_trade_readiness_epic()
    return (
        f"Supervised demo trade readiness status: {active.classification}. "
        f"{active.selected_strategy} {active.direction} {active.instrument}, "
        f"{active.proposed_units} units. {active.operator_answer} No trade was placed."
    )


def supervised_demo_trade_readiness_epic_to_markdown(
    result: SupervisedDemoTradeReadinessEpicResult | None = None,
) -> str:
    active = result or run_supervised_demo_trade_readiness_epic()
    return "\n".join(
        [
            "# Supervised Demo Trade Readiness Epic V1",
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Readiness bridge status: {active.readiness_bridge_status}",
            f"- Review bundle status: {active.review_bundle_status}",
            f"- Snapshot intake status: {active.snapshot_intake_status}",
            f"- Account status: {active.account_status}",
            f"- Candidate status: {active.candidate_status}",
            f"- Risk status: {active.risk_status}",
            f"- Position size status: {active.position_size_status}",
            f"- Order plan status: {active.order_plan_status}",
            f"- Operator ticket status: {active.operator_ticket_status}",
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
            f"- Real money allowed: {active.real_money_allowed}",
            f"- Compounding allowed: {active.compounding_allowed}",
            f"- Bank movement allowed: {active.bank_movement_allowed}",
            f"- Operator answer: {active.operator_answer}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _coerce_input(
    value: SupervisedDemoTradeReadinessEpicInput | Mapping[str, Any],
) -> SupervisedDemoTradeReadinessEpicInput:
    if isinstance(value, SupervisedDemoTradeReadinessEpicInput):
        return value
    raw = dict(value)
    config = raw.get("config", SupervisedDemoTradeReadinessEpicConfig())
    if not isinstance(config, SupervisedDemoTradeReadinessEpicConfig):
        config = SupervisedDemoTradeReadinessEpicConfig(**dict(config))
    return SupervisedDemoTradeReadinessEpicInput(
        config=config,
        review_bundle_input=raw["review_bundle_input"],
    )


def _operator_answer(classification: str) -> str:
    if classification == SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW:
        return "The full local readiness package is ready for owner review, but execution remains locked."
    return "The full local readiness package is blocked and must not be used for execution."


def _next_safe_action(classification: str) -> str:
    if classification == SUPERVISED_DEMO_TRADE_READINESS_READY_FOR_OWNER_REVIEW:
        return "Anthony may review the local readiness bundle; Codex must not execute or approve broker action."
    return "Resolve readiness blockers before owner review."


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
