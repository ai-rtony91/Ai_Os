from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


DEMO_TRADE_FEEDBACK_ROUTER_VERSION = "demo_trade_feedback_router_v1"

FEEDBACK_ROUTED_PROFIT_IMPROVES_EVIDENCE = "FEEDBACK_ROUTED_PROFIT_IMPROVES_EVIDENCE"
FEEDBACK_ROUTED_LOSS_REQUIRES_REVIEW = "FEEDBACK_ROUTED_LOSS_REQUIRES_REVIEW"
FEEDBACK_ROUTED_MORE_EVIDENCE_REQUIRED = "FEEDBACK_ROUTED_MORE_EVIDENCE_REQUIRED"
FEEDBACK_BLOCKED_MISSING_POST_TRADE_EVIDENCE = "FEEDBACK_BLOCKED_MISSING_POST_TRADE_EVIDENCE"
FEEDBACK_BLOCKED_UNRECONCILED = "FEEDBACK_BLOCKED_UNRECONCILED"

FEEDBACK_TARGETS = (
    "Profit Proof Ledger",
    "Strategy Proof Engine",
    "Expectancy Strength Router",
    "Demo Review Engine",
    "Strategy Promotion Router",
    "Real Evidence Depth Engine",
)


@dataclass(frozen=True)
class DemoTradeFeedbackInput:
    post_trade_evidence_present: bool
    post_trade_status: str
    strategy_id: str
    result: str
    realized_pl: Decimal | None
    broker_reconciled: bool
    sanitized: bool
    notes: str


@dataclass(frozen=True)
class DemoTradeFeedbackResult:
    engine_version: str
    classification: str
    strategy_id: str
    targets: tuple[str, ...]
    routed: bool
    blockers: tuple[str, ...]
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool


def build_sample_feedback_profit_input() -> DemoTradeFeedbackInput:
    return DemoTradeFeedbackInput(
        post_trade_evidence_present=True,
        post_trade_status="POST_TRADE_EVIDENCE_CAPTURED_PROFIT",
        strategy_id="supertrend",
        result="PROFIT",
        realized_pl=Decimal("185.40"),
        broker_reconciled=True,
        sanitized=True,
        notes="Sanitized profit sample for local proof feedback.",
    )


def build_sample_feedback_loss_input() -> DemoTradeFeedbackInput:
    sample = build_sample_feedback_profit_input()
    return _replace_input(
        sample,
        post_trade_status="POST_TRADE_EVIDENCE_CAPTURED_LOSS",
        result="LOSS",
        realized_pl=Decimal("-75.20"),
        notes="Sanitized loss sample for review feedback.",
    )


def route_demo_trade_feedback(
    feedback_input: DemoTradeFeedbackInput | Mapping[str, Any] | None = None,
) -> DemoTradeFeedbackResult:
    active = _coerce_input(feedback_input or build_sample_feedback_profit_input())
    classification = _classify(active)
    routed = classification in (
        FEEDBACK_ROUTED_PROFIT_IMPROVES_EVIDENCE,
        FEEDBACK_ROUTED_LOSS_REQUIRES_REVIEW,
        FEEDBACK_ROUTED_MORE_EVIDENCE_REQUIRED,
    )
    return DemoTradeFeedbackResult(
        engine_version=DEMO_TRADE_FEEDBACK_ROUTER_VERSION,
        classification=classification,
        strategy_id=active.strategy_id,
        targets=FEEDBACK_TARGETS,
        routed=routed,
        blockers=tuple([] if routed else [classification.lower()]),
        next_safe_action=_next_safe_action(classification),
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
    )


def feedback_to_jsonable_dict(result: DemoTradeFeedbackResult) -> dict[str, Any]:
    return _json_value(result)


def feedback_to_operator_text(result: DemoTradeFeedbackResult | None = None) -> str:
    active = result or route_demo_trade_feedback()
    if active.routed:
        return f"Feedback routed to proof systems for {active.strategy_id}. No trade was placed by this router."
    return f"Feedback routing is blocked: {'; '.join(active.blockers)}."


def _classify(value: DemoTradeFeedbackInput) -> str:
    if not value.post_trade_evidence_present:
        return FEEDBACK_BLOCKED_MISSING_POST_TRADE_EVIDENCE
    if not value.broker_reconciled or not value.sanitized:
        return FEEDBACK_BLOCKED_UNRECONCILED
    if value.realized_pl is None:
        return FEEDBACK_ROUTED_MORE_EVIDENCE_REQUIRED
    if value.realized_pl > 0 or value.result.upper() == "PROFIT":
        return FEEDBACK_ROUTED_PROFIT_IMPROVES_EVIDENCE
    if value.realized_pl < 0 or value.result.upper() == "LOSS":
        return FEEDBACK_ROUTED_LOSS_REQUIRES_REVIEW
    return FEEDBACK_ROUTED_MORE_EVIDENCE_REQUIRED


def _next_safe_action(classification: str) -> str:
    if classification == FEEDBACK_ROUTED_PROFIT_IMPROVES_EVIDENCE:
        return "Update proof evidence review with the sanitized profit result."
    if classification == FEEDBACK_ROUTED_LOSS_REQUIRES_REVIEW:
        return "Review the loss before any further supervised demo consideration."
    if classification == FEEDBACK_ROUTED_MORE_EVIDENCE_REQUIRED:
        return "Collect more reconciled evidence before changing promotion confidence."
    return "Capture reconciled sanitized post-trade evidence before routing feedback."


def _replace_input(value: DemoTradeFeedbackInput, **updates: Any) -> DemoTradeFeedbackInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoTradeFeedbackInput(**raw)


def _coerce_input(value: DemoTradeFeedbackInput | Mapping[str, Any]) -> DemoTradeFeedbackInput:
    if isinstance(value, DemoTradeFeedbackInput):
        return value
    raw = dict(value)
    if raw.get("realized_pl") is not None:
        raw["realized_pl"] = _to_decimal(raw["realized_pl"])
    return DemoTradeFeedbackInput(**raw)


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


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
