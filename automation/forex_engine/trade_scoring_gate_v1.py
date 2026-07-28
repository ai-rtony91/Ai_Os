"""Trade Scoring Gate V1 for report-only Forex candidate eligibility."""

from __future__ import annotations

from datetime import UTC, datetime
from numbers import Real
from typing import Any, Mapping

VERSION = "TRADE_SCORING_GATE_V1"
DECISION_BLOCKED = "BLOCKED"
DECISION_PAPER_ELIGIBLE = "PAPER_ELIGIBLE"
DECISION_MICRO_LIVE_REVIEW_REQUIRED = "MICRO_LIVE_REVIEW_REQUIRED"

REQUIRED_FIELDS = (
    "symbol",
    "direction",
    "entry_type",
    "proposed_entry",
    "stop_loss",
    "take_profit",
    "risk_amount",
    "account_mode",
    "strategy_id",
    "session",
    "spread",
    "slippage_estimate",
    "volatility_state",
    "trend_alignment",
    "walk_forward_status",
    "recent_strategy_status",
    "kill_switch_active",
    "broker_ready",
    "evidence_depth",
)

LIVE_REVIEW_MODES = {"MICRO_LIVE_REVIEW", "LIVE_REVIEW", "OWNER_MICRO_LIVE_REVIEW"}
PAPER_MODES = {"PAPER", "PAPER_ONLY", "PAPER_SIMULATION", "DEMO", "DEMO_ONLY"}
PASS_WALK_FORWARD = {"PASS", "PASSED", "WALK_FORWARD_PASS"}
PAPER_WALK_FORWARD = PASS_WALK_FORWARD | {"MORE_PAPER_REQUIRED", "PAPER_EVIDENCE_REQUIRED"}
GOOD_RECENT_STATUS = {"PASS", "ACCEPTABLE", "GOOD", "STABLE"}
GOOD_TREND = {"ALIGNED", "STRONG", "WITH_TREND"}
GOOD_VOLATILITY = {"NORMAL", "STABLE", "ACCEPTABLE"}
GOOD_SESSION = {"LONDON", "NEW_YORK", "OVERLAP", "ACTIVE"}

MIN_RISK_REWARD = 1.5
MAX_SPREAD = 3.0
MAX_SLIPPAGE = 2.0
MAX_RISK_AMOUNT = 100.0
MIN_PAPER_EVIDENCE_DEPTH = 1
MIN_LIVE_REVIEW_EVIDENCE_DEPTH = 30


def evaluate_trade_scoring_gate_v1(candidate: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(candidate or {})
    blockers: list[str] = []
    warnings: list[str] = []
    required_next_evidence: list[str] = []

    missing = [field for field in REQUIRED_FIELDS if field not in source]
    if missing:
        blockers.extend(f"{field}_missing" for field in missing)

    kill_switch_active = source.get("kill_switch_active")
    if not isinstance(kill_switch_active, bool):
        blockers.append("kill_switch_active_missing_or_non_bool")
    elif kill_switch_active:
        blockers.append("kill_switch_active_true")

    direction = _text(source.get("direction")).upper()
    entry = _number(source.get("proposed_entry"))
    stop = _number(source.get("stop_loss"))
    target = _number(source.get("take_profit"))
    risk_amount = _number(source.get("risk_amount"))
    spread = _number(source.get("spread"))
    slippage = _number(source.get("slippage_estimate"))
    evidence_depth = _number(source.get("evidence_depth"))
    risk_reward = _risk_reward(direction, entry, stop, target)

    if not missing:
        if risk_reward is None:
            blockers.append("invalid_stop_take_profit_geometry")
        elif risk_reward < MIN_RISK_REWARD:
            blockers.append("risk_reward_below_minimum")

        if spread is None or spread > MAX_SPREAD:
            blockers.append("spread_unacceptable")
        if slippage is None or slippage > MAX_SLIPPAGE:
            blockers.append("slippage_unacceptable")
        if risk_amount is None or risk_amount <= 0 or risk_amount > MAX_RISK_AMOUNT:
            blockers.append("risk_budget_failed")

        walk_forward = _text(source.get("walk_forward_status")).upper()
        if walk_forward in {"FAIL", "FAILED", "WALK_FORWARD_FAILED"}:
            blockers.append("walk_forward_failed")
        elif walk_forward not in PAPER_WALK_FORWARD:
            blockers.append("walk_forward_status_unacceptable")

        account_mode = _text(source.get("account_mode")).upper()
        broker_ready = source.get("broker_ready")
        if account_mode in LIVE_REVIEW_MODES and broker_ready is not True:
            blockers.append("broker_readiness_required_but_false")

        if evidence_depth is None or evidence_depth < MIN_PAPER_EVIDENCE_DEPTH:
            blockers.append("evidence_depth_insufficient")
        elif account_mode in LIVE_REVIEW_MODES and evidence_depth < MIN_LIVE_REVIEW_EVIDENCE_DEPTH:
            blockers.append("evidence_depth_insufficient_for_escalation")
            required_next_evidence.append("continue_paper_evidence_until_live_review_depth_is_met")

    score_breakdown = _score_breakdown(source, risk_reward, blockers)
    score_total = sum(score_breakdown.values())
    decision = _decision(source, blockers)
    if decision == DECISION_PAPER_ELIGIBLE and _text(source.get("walk_forward_status")).upper() not in PASS_WALK_FORWARD:
        required_next_evidence.append("more_paper_evidence_required_before_live_review")
    if decision == DECISION_BLOCKED and not required_next_evidence:
        required_next_evidence.append("repair_blockers_and_rescore_candidate")

    return {
        "decision": decision,
        "score_total": score_total,
        "score_breakdown": score_breakdown,
        "blockers": blockers,
        "warnings": warnings,
        "required_next_evidence": required_next_evidence,
        "execution_allowed": False,
        "broker_action_allowed": False,
        "human_review_required": decision != DECISION_PAPER_ELIGIBLE,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "version": VERSION,
    }


def _decision(source: Mapping[str, Any], blockers: list[str]) -> str:
    if blockers:
        return DECISION_BLOCKED
    account_mode = _text(source.get("account_mode")).upper()
    if (
        account_mode in LIVE_REVIEW_MODES
        and _text(source.get("walk_forward_status")).upper() in PASS_WALK_FORWARD
        and _text(source.get("recent_strategy_status")).upper() in GOOD_RECENT_STATUS
        and source.get("broker_ready") is True
        and (_number(source.get("evidence_depth")) or 0) >= MIN_LIVE_REVIEW_EVIDENCE_DEPTH
    ):
        return DECISION_MICRO_LIVE_REVIEW_REQUIRED
    return DECISION_PAPER_ELIGIBLE


def _score_breakdown(source: Mapping[str, Any], risk_reward: float | None, blockers: list[str]) -> dict[str, int]:
    return {
        "setup_quality": 0 if any(blocker.endswith("_missing") for blocker in blockers) else 10,
        "trend_alignment": 10 if _text(source.get("trend_alignment")).upper() in GOOD_TREND else 5,
        "risk_reward": 10 if risk_reward is not None and risk_reward >= 2 else 7 if risk_reward is not None and risk_reward >= MIN_RISK_REWARD else 0,
        "spread_slippage": 10 if (_number(source.get("spread")) or 999) <= MAX_SPREAD and (_number(source.get("slippage_estimate")) or 999) <= MAX_SLIPPAGE else 0,
        "session_quality": 10 if _text(source.get("session")).upper() in GOOD_SESSION else 5,
        "volatility_quality": 10 if _text(source.get("volatility_state")).upper() in GOOD_VOLATILITY else 5,
        "walk_forward_quality": 10 if _text(source.get("walk_forward_status")).upper() in PASS_WALK_FORWARD else 5 if _text(source.get("walk_forward_status")).upper() in PAPER_WALK_FORWARD else 0,
        "recent_performance_quality": 10 if _text(source.get("recent_strategy_status")).upper() in GOOD_RECENT_STATUS else 5,
        "risk_budget_quality": 10 if (_number(source.get("risk_amount")) or 999) <= MAX_RISK_AMOUNT else 0,
        "safety_gate_quality": 10 if source.get("kill_switch_active") is False else 0,
    }


def _risk_reward(direction: str, entry: float | None, stop: float | None, target: float | None) -> float | None:
    if entry is None or stop is None or target is None:
        return None
    if direction in {"BUY", "LONG"}:
        risk = entry - stop
        reward = target - entry
    elif direction in {"SELL", "SHORT"}:
        risk = stop - entry
        reward = entry - target
    else:
        return None
    if risk <= 0 or reward <= 0:
        return None
    return reward / risk


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    return float(value)


def _text(value: Any) -> str:
    return str(value or "").strip()
