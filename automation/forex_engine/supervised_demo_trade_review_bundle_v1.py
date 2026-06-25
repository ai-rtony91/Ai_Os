from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.demo_operator_execution_ticket_v1 import DO_NOT_EXECUTE_WARNING
from automation.forex_engine.demo_trade_readiness_bridge_v1 import (
    DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW,
    DemoTradeReadinessBridgeInput,
    DemoTradeReadinessBridgeResult,
    build_sample_demo_trade_readiness_bridge_blocked_input,
    build_sample_demo_trade_readiness_bridge_ready_input,
    demo_trade_readiness_bridge_to_jsonable_dict,
    run_demo_trade_readiness_bridge,
)


SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_VERSION = "supervised_demo_trade_review_bundle_v1"

SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY = "SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY"
SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_BLOCKED = "SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_BLOCKED"

BLOCKED_ACTIONS = (
    "demo execution",
    "broker action",
    "real money",
    "compounding",
    "bank movement",
    "live trading",
)


@dataclass(frozen=True)
class SupervisedDemoTradeReviewBundleInput:
    bridge_input: DemoTradeReadinessBridgeInput | Mapping[str, Any]


@dataclass(frozen=True)
class SupervisedDemoTradeReviewBundleResult:
    engine_version: str
    classification: str
    bundle_review_allowed: bool
    readiness_bridge_status: str
    operator_summary: str
    owner_warning: str
    blocked_actions: tuple[str, ...]
    review_sections: Mapping[str, Any]
    next_safe_action: str
    bridge_result: DemoTradeReadinessBridgeResult
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_supervised_demo_trade_review_bundle_ready_input() -> SupervisedDemoTradeReviewBundleInput:
    return SupervisedDemoTradeReviewBundleInput(
        bridge_input=build_sample_demo_trade_readiness_bridge_ready_input()
    )


def build_sample_supervised_demo_trade_review_bundle_blocked_input() -> SupervisedDemoTradeReviewBundleInput:
    return SupervisedDemoTradeReviewBundleInput(
        bridge_input=build_sample_demo_trade_readiness_bridge_blocked_input()
    )


def build_supervised_demo_trade_review_bundle(
    bundle_input: SupervisedDemoTradeReviewBundleInput | Mapping[str, Any] | None = None,
) -> SupervisedDemoTradeReviewBundleResult:
    active = _coerce_input(bundle_input or build_sample_supervised_demo_trade_review_bundle_ready_input())
    bridge = run_demo_trade_readiness_bridge(active.bridge_input)
    ready = bridge.classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW
    classification = (
        SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY
        if ready
        else SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_BLOCKED
    )
    return SupervisedDemoTradeReviewBundleResult(
        engine_version=SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_VERSION,
        classification=classification,
        bundle_review_allowed=ready,
        readiness_bridge_status=bridge.classification,
        operator_summary=_operator_summary(bridge),
        owner_warning=DO_NOT_EXECUTE_WARNING,
        blocked_actions=BLOCKED_ACTIONS,
        review_sections=_review_sections(bridge),
        next_safe_action=_next_safe_action(classification),
        bridge_result=bridge,
        **_permission_defaults(),
    )


def supervised_demo_trade_review_bundle_to_jsonable_dict(
    result: SupervisedDemoTradeReviewBundleResult,
) -> dict[str, Any]:
    data = _json_value(result)
    data["bridge_result"] = demo_trade_readiness_bridge_to_jsonable_dict(result.bridge_result)
    return data


def supervised_demo_trade_review_bundle_to_operator_text(
    result: SupervisedDemoTradeReviewBundleResult | None = None,
) -> str:
    active = result or build_supervised_demo_trade_review_bundle()
    return f"{active.operator_summary} {active.owner_warning} No trade was placed."


def supervised_demo_trade_review_bundle_to_markdown(
    result: SupervisedDemoTradeReviewBundleResult | None = None,
) -> str:
    active = result or build_supervised_demo_trade_review_bundle()
    lines = [
        "# Supervised Demo Trade Review Bundle V1",
        "",
        active.owner_warning,
        "",
        "No broker call was made. No trade was placed.",
        "",
        f"- Status: {active.classification}",
        f"- Readiness bridge status: {active.readiness_bridge_status}",
        f"- Bundle review allowed: {active.bundle_review_allowed}",
        "",
    ]
    for section_name, section in active.review_sections.items():
        lines.append(f"## {section_name}")
        for key, value in section.items():
            lines.append(f"- {key}: {_display(value)}")
        lines.append("")
    lines.append("## Blocked Actions")
    lines.extend(f"- {item}" for item in active.blocked_actions)
    return "\n".join(lines).rstrip()


def _coerce_input(
    value: SupervisedDemoTradeReviewBundleInput | Mapping[str, Any],
) -> SupervisedDemoTradeReviewBundleInput:
    if isinstance(value, SupervisedDemoTradeReviewBundleInput):
        return value
    raw = dict(value)
    return SupervisedDemoTradeReviewBundleInput(bridge_input=raw["bridge_input"])


def _operator_summary(bridge: DemoTradeReadinessBridgeResult) -> str:
    if bridge.classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW:
        return "Supervised demo trade review bundle is ready for Anthony's local review."
    return f"Supervised demo trade review bundle is blocked: {'; '.join(bridge.blockers)}."


def _review_sections(bridge: DemoTradeReadinessBridgeResult) -> Mapping[str, Any]:
    return {
        "Executive Summary": {
            "status": bridge.classification,
            "operator_answer": bridge.operator_answer,
            "next_safe_action": bridge.next_safe_action,
        },
        "Snapshot Review": {
            "snapshot_intake_status": bridge.snapshot_intake_status,
            "snapshot_review_status": bridge.snapshot_review_status,
            "account_status": bridge.account_status,
        },
        "Candidate Review": {
            "selected_strategy": bridge.selected_strategy,
            "candidate_id": bridge.candidate_id,
            "instrument": bridge.instrument,
            "direction": bridge.direction,
            "candidate_status": bridge.candidate_status,
        },
        "Risk Review": {"risk_status": bridge.risk_status, "max_loss": bridge.max_loss},
        "Position Sizing": {
            "position_size_status": bridge.position_size_status,
            "proposed_units": bridge.proposed_units,
        },
        "Order Plan": {
            "order_plan_status": bridge.order_plan_status,
            "entry_price": bridge.entry_price,
            "stop_loss": bridge.stop_loss,
            "take_profit": bridge.take_profit,
            "expected_reward": bridge.expected_reward,
            "reward_to_risk": bridge.reward_to_risk,
        },
        "Operator Ticket": {
            "operator_ticket_status": bridge.operator_ticket_status,
            "owner_warning": DO_NOT_EXECUTE_WARNING,
        },
        "Post-Trade Evidence": {
            "post_trade_capture_status": bridge.post_trade_capture_status,
            "plan": "Capture sanitized evidence only after a supervised demo trade exists.",
        },
        "Feedback Routing": {
            "feedback_router_status": bridge.feedback_router_status,
            "plan": "Route sanitized post-trade evidence after capture; no routing occurs before evidence exists.",
        },
    }


def _next_safe_action(classification: str) -> str:
    if classification == SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY:
        return "Anthony may review the local bundle manually; no execution approval is granted."
    return "Resolve readiness bridge blockers before owner review."


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
