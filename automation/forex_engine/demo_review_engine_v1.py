"""Local-only AIOS Forex Demo Review Engine V1.

This module packages the current strongest strategy proof into an operator demo
review summary. It does not call brokers, read credentials, read .env files,
use network access, place orders, approve demo execution, approve real money,
approve compounding, approve withdrawals, approve deposits, or move money.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping

from automation.forex_engine.strategy_promotion_router_v1 import (
    STRATEGY_PROMOTION_REVIEW_READY,
    StrategyPromotionRouteResult,
    build_sample_all_blocked_promotion_input,
    build_sample_mixed_promotion_input,
    result_to_jsonable_dict as promotion_result_to_jsonable_dict,
    route_strategy_promotion,
)


DEMO_REVIEW_ENGINE_VERSION = "demo_review_engine_v1"

DEMO_REVIEW_READY = "DEMO_REVIEW_READY"
DEMO_REVIEW_MORE_PROOF_REQUIRED = "DEMO_REVIEW_MORE_PROOF_REQUIRED"
DEMO_REVIEW_BLOCKED = "DEMO_REVIEW_BLOCKED"
DEMO_REVIEW_UNKNOWN = "DEMO_REVIEW_UNKNOWN"

VALID_DEMO_REVIEW_STATUSES = {
    DEMO_REVIEW_READY,
    DEMO_REVIEW_MORE_PROOF_REQUIRED,
    DEMO_REVIEW_BLOCKED,
    DEMO_REVIEW_UNKNOWN,
}


@dataclass(frozen=True)
class DemoReviewResult:
    engine_version: str
    demo_review_status: str
    best_strategy: str
    best_strategy_name: str
    why: str
    supertrend_status: Mapping[str, Any]
    promotion_score: Decimal
    review_recommendation: str
    expectancy_status: str
    proof_status: str
    expectancy_improving: bool
    proof_improving: bool
    blockers: tuple[str, ...]
    what_must_improve_next: tuple[str, ...]
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    permissions: Mapping[str, bool]
    promotion_summary: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.demo_review_status not in VALID_DEMO_REVIEW_STATUSES:
            raise ValueError(f"invalid demo review status: {self.demo_review_status}")


def build_sample_mixed_demo_review_input() -> StrategyPromotionRouteResult:
    return route_strategy_promotion(build_sample_mixed_promotion_input())


def build_sample_all_blocked_demo_review_input() -> StrategyPromotionRouteResult:
    return route_strategy_promotion(build_sample_all_blocked_promotion_input())


def evaluate_demo_review(
    promotion_route: StrategyPromotionRouteResult | None = None,
) -> DemoReviewResult:
    active = promotion_route if promotion_route is not None else build_sample_mixed_demo_review_input()
    status = _demo_review_status(active)

    return DemoReviewResult(
        engine_version=DEMO_REVIEW_ENGINE_VERSION,
        demo_review_status=status,
        best_strategy=active.best_strategy,
        best_strategy_name=active.best_strategy_name,
        why=active.why,
        supertrend_status=active.supertrend_status,
        promotion_score=active.promotion_score,
        review_recommendation=active.review_recommendation,
        expectancy_status=active.expectancy_status,
        proof_status=active.proof_status,
        expectancy_improving=active.expectancy_improving,
        proof_improving=active.proof_improving,
        blockers=active.blockers,
        what_must_improve_next=active.what_must_improve_next,
        next_safe_action=_next_safe_action(status, active.best_strategy),
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        permissions=_permissions(),
        promotion_summary=_promotion_summary(active),
    )


def result_to_operator_text(result: DemoReviewResult | None = None) -> str:
    active = result if result is not None else evaluate_demo_review()
    lines = [
        "AIOS Forex Demo Review Engine V1",
        f"demo_review_status: {active.demo_review_status}",
        f"best_strategy: {active.best_strategy}",
        f"supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"promotion_score: {_json_value(active.promotion_score)}",
        f"review_recommendation: {active.review_recommendation}",
        f"expectancy_status: {active.expectancy_status}",
        f"proof_status: {active.proof_status}",
        f"expectancy_improving: {_bool_text(active.expectancy_improving)}",
        f"proof_improving: {_bool_text(active.proof_improving)}",
        f"demo_execution_allowed: {_bool_text(active.demo_execution_allowed)}",
        f"broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
        f"real_money_allowed: {_bool_text(active.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(active.compounding_allowed)}",
        f"bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
        "what_must_improve_next:",
    ]
    lines.extend(f"- {item}" for item in active.what_must_improve_next or ("none",))
    lines.append(f"next_safe_action: {active.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: DemoReviewResult | None = None) -> dict[str, Any]:
    active = result if result is not None else evaluate_demo_review()
    return {
        "engine_version": active.engine_version,
        "demo_review_status": active.demo_review_status,
        "best_strategy": active.best_strategy,
        "best_strategy_name": active.best_strategy_name,
        "why": active.why,
        "supertrend_status": _json_value(active.supertrend_status),
        "promotion_score": _json_value(active.promotion_score),
        "review_recommendation": active.review_recommendation,
        "expectancy_status": active.expectancy_status,
        "proof_status": active.proof_status,
        "expectancy_improving": active.expectancy_improving,
        "proof_improving": active.proof_improving,
        "blockers": list(active.blockers),
        "what_must_improve_next": list(active.what_must_improve_next),
        "next_safe_action": active.next_safe_action,
        "demo_execution_allowed": active.demo_execution_allowed,
        "broker_action_allowed": active.broker_action_allowed,
        "real_money_allowed": active.real_money_allowed,
        "compounding_allowed": active.compounding_allowed,
        "bank_movement_allowed": active.bank_movement_allowed,
        "permissions": dict(active.permissions),
        "promotion_summary": _json_value(active.promotion_summary),
        "safety": {
            "local_only": True,
            "broker_calls": False,
            "network_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "order_placement": False,
            "demo_execution_approval": False,
            "real_money_approval": False,
            "compounding_approval": False,
            "withdrawal_approval": False,
            "deposit_approval": False,
            "bank_movement_approval": False,
        },
    }


def demo_review_to_markdown(result: DemoReviewResult | None = None) -> str:
    active = result if result is not None else evaluate_demo_review()
    lines = [
        "# AIOS Forex Demo Review Engine V1",
        "",
        "## Status",
        f"- demo_review_status: {active.demo_review_status}",
        f"- best_strategy: {active.best_strategy}",
        f"- supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"- promotion_score: {_json_value(active.promotion_score)}",
        f"- review_recommendation: {active.review_recommendation}",
        f"- expectancy_status: {active.expectancy_status}",
        f"- proof_status: {active.proof_status}",
        "",
        "## Why",
        active.why,
        "",
        "## What Must Improve Next",
    ]
    lines.extend(f"- {item}" for item in active.what_must_improve_next or ("none",))
    lines.extend(
        [
            "",
            "## Safety Locks",
            f"- demo_execution_allowed: {_bool_text(active.demo_execution_allowed)}",
            f"- broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
            f"- real_money_allowed: {_bool_text(active.real_money_allowed)}",
            f"- compounding_allowed: {_bool_text(active.compounding_allowed)}",
            f"- bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
            "",
            "## Next Copy/Paste Action",
            active.next_safe_action,
            "",
        ]
    )
    return "\n".join(lines)


def _demo_review_status(active: StrategyPromotionRouteResult) -> str:
    if active.best_strategy == "NONE":
        return DEMO_REVIEW_UNKNOWN
    if active.promotion_status == STRATEGY_PROMOTION_REVIEW_READY:
        return DEMO_REVIEW_READY
    if active.failed_checks:
        return DEMO_REVIEW_BLOCKED
    return DEMO_REVIEW_MORE_PROOF_REQUIRED


def _next_safe_action(status: str, best_strategy: str) -> str:
    if status == DEMO_REVIEW_READY:
        return (
            f"Prepare a human demo-review decision note for {best_strategy}; do "
            "not run demo execution, broker action, real money, compounding, or bank movement."
        )
    if best_strategy != "NONE":
        return f"Collect missing proof for {best_strategy} before any demo review decision."
    return "Repair strategy proof evidence before creating a demo-review package."


def _permissions() -> dict[str, bool]:
    return {
        "demo_execution_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }


def _promotion_summary(active: StrategyPromotionRouteResult) -> dict[str, Any]:
    raw = promotion_result_to_jsonable_dict(active)
    return {
        "promotion_status": raw["promotion_status"],
        "best_strategy": raw["best_strategy"],
        "supertrend_status": raw["supertrend_status"],
        "promotion_score": raw["promotion_score"],
        "review_recommendation": raw["review_recommendation"],
        "expectancy_status": raw["expectancy_status"],
        "proof_status": raw["proof_status"],
        "what_must_improve_next": raw["what_must_improve_next"],
    }


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
