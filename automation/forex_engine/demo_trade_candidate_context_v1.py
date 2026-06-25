from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping


DEMO_TRADE_CANDIDATE_CONTEXT_VERSION = "demo_trade_candidate_context_v1"

DEMO_TRADE_CANDIDATE_CONTEXT_READY = "DEMO_TRADE_CANDIDATE_CONTEXT_READY"
DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_STRATEGY = (
    "DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_STRATEGY"
)
DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_INSTRUMENT = (
    "DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_INSTRUMENT"
)
DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_DIRECTION = (
    "DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_DIRECTION"
)
DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_NOT_REVIEW_READY = (
    "DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_NOT_REVIEW_READY"
)
DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_EVIDENCE = (
    "DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_EVIDENCE"
)


@dataclass(frozen=True)
class DemoTradeCandidateContextConfig:
    require_review_ready_statuses: bool = True


@dataclass(frozen=True)
class DemoTradeCandidateContextInput:
    selected_strategy: str
    strategy_id: str
    candidate_id: str
    instrument: str
    direction: str
    supertrend_status: str
    candidate_review_ready: bool
    expectancy_status: str
    evidence_status: str
    promotion_status: str
    config: DemoTradeCandidateContextConfig = DemoTradeCandidateContextConfig()


@dataclass(frozen=True)
class DemoTradeCandidateContextResult:
    engine_version: str
    classification: str
    candidate_context_review_allowed: bool
    selected_strategy: str
    strategy_id: str
    candidate_id: str
    instrument: str
    direction: str
    supertrend_status: str
    expectancy_status: str
    evidence_status: str
    promotion_status: str
    blockers: tuple[str, ...]
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_ready_candidate_context_input() -> DemoTradeCandidateContextInput:
    return DemoTradeCandidateContextInput(
        selected_strategy="Supertrend",
        strategy_id="supertrend",
        candidate_id="supertrend-review-ready-sample",
        instrument="EUR_USD",
        direction="LONG",
        supertrend_status="SUPER_TREND_PROOF_REVIEW_READY",
        candidate_review_ready=True,
        expectancy_status="EXPECTANCY_REVIEW_READY",
        evidence_status="EVIDENCE_REVIEW_READY",
        promotion_status="STRATEGY_PROMOTION_REVIEW_READY",
    )


def build_sample_blocked_candidate_context_input() -> DemoTradeCandidateContextInput:
    sample = build_sample_ready_candidate_context_input()
    return _replace_input(sample, candidate_review_ready=False)


def evaluate_demo_trade_candidate_context(
    candidate_input: DemoTradeCandidateContextInput | Mapping[str, Any] | None = None,
) -> DemoTradeCandidateContextResult:
    active = _coerce_input(candidate_input or build_sample_ready_candidate_context_input())
    classification = _classify(active)
    blockers = tuple([] if classification == DEMO_TRADE_CANDIDATE_CONTEXT_READY else [_blocker(classification)])
    return DemoTradeCandidateContextResult(
        engine_version=DEMO_TRADE_CANDIDATE_CONTEXT_VERSION,
        classification=classification,
        candidate_context_review_allowed=classification == DEMO_TRADE_CANDIDATE_CONTEXT_READY,
        selected_strategy=active.selected_strategy,
        strategy_id=active.strategy_id,
        candidate_id=active.candidate_id,
        instrument=active.instrument,
        direction=active.direction,
        supertrend_status=active.supertrend_status,
        expectancy_status=active.expectancy_status,
        evidence_status=active.evidence_status,
        promotion_status=active.promotion_status,
        blockers=blockers,
        next_safe_action=_next_safe_action(classification),
        **_permission_defaults(),
    )


def demo_trade_candidate_context_to_jsonable_dict(result: DemoTradeCandidateContextResult) -> dict[str, Any]:
    return _json_value(result)


def demo_trade_candidate_context_to_operator_text(
    result: DemoTradeCandidateContextResult | None = None,
) -> str:
    active = result or evaluate_demo_trade_candidate_context()
    if active.candidate_context_review_allowed:
        return (
            f"Candidate context is review-ready for {active.selected_strategy} "
            f"{active.direction} {active.instrument}. No trade was placed."
        )
    return f"Candidate context is blocked: {'; '.join(active.blockers)}. No trade was placed."


def _classify(value: DemoTradeCandidateContextInput) -> str:
    if not value.selected_strategy.strip() or not value.strategy_id.strip():
        return DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_STRATEGY
    if not value.instrument.strip():
        return DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_INSTRUMENT
    if not value.direction.strip():
        return DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_DIRECTION
    if not value.candidate_review_ready or "REVIEW_READY" not in value.supertrend_status:
        return DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_NOT_REVIEW_READY
    if value.config.require_review_ready_statuses and not _evidence_statuses_ready(value):
        return DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_EVIDENCE
    return DEMO_TRADE_CANDIDATE_CONTEXT_READY


def _evidence_statuses_ready(value: DemoTradeCandidateContextInput) -> bool:
    return (
        "REVIEW_READY" in value.expectancy_status
        and "REVIEW_READY" in value.evidence_status
        and "REVIEW_READY" in value.promotion_status
    )


def _blocker(classification: str) -> str:
    if classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_STRATEGY:
        return "selected strategy or strategy id is missing"
    if classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_INSTRUMENT:
        return "instrument is missing"
    if classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_DIRECTION:
        return "direction is missing"
    if classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_EVIDENCE:
        return "candidate evidence, expectancy, or promotion status is not review-ready"
    return "candidate context is not review-ready"


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_TRADE_CANDIDATE_CONTEXT_READY:
        return "Continue to local readiness bridge review; keep execution locked."
    return "Fix candidate context blockers before building a supervised demo review package."


def _coerce_input(value: DemoTradeCandidateContextInput | Mapping[str, Any]) -> DemoTradeCandidateContextInput:
    if isinstance(value, DemoTradeCandidateContextInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoTradeCandidateContextConfig())
    if not isinstance(config, DemoTradeCandidateContextConfig):
        config = DemoTradeCandidateContextConfig(**dict(config))
    raw["config"] = config
    return DemoTradeCandidateContextInput(**raw)


def _replace_input(
    value: DemoTradeCandidateContextInput,
    **updates: Any,
) -> DemoTradeCandidateContextInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoTradeCandidateContextInput(**raw)


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
