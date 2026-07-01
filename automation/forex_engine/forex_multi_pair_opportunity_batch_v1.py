"""Score and filter governed multi-pair Forex burst candidates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_multi_pair_universe_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    MULTI_PAIR_UNIVERSE_READY,
    _bool,
    _governed_requested,
    _int,
    _mapping,
    _number,
    _pair_text,
    _unique,
    banking_focus_blockers,
    build_common_result,
    sensitive_data_blockers,
)

SCHEMA = "AIOS_FOREX_MULTI_PAIR_OPPORTUNITY_BATCH_V1"
MODE = "READ_ONLY_METADATA_ONLY_MULTI_PAIR_OPPORTUNITY_BATCH"

MULTI_PAIR_OPPORTUNITY_BATCH_READY = "MULTI_PAIR_OPPORTUNITY_BATCH_READY"
BLOCKED_BY_PAIR_UNIVERSE = "BLOCKED_BY_PAIR_UNIVERSE"
BLOCKED_BY_EMPTY_CANDIDATES = "BLOCKED_BY_EMPTY_CANDIDATES"
BLOCKED_BY_CANDIDATE_QUALITY = "BLOCKED_BY_CANDIDATE_QUALITY"
BLOCKED_BY_SPREAD_SLIPPAGE = "BLOCKED_BY_SPREAD_SLIPPAGE"
BLOCKED_BY_NEWS_BLACKOUT = "BLOCKED_BY_NEWS_BLACKOUT"
BLOCKED_BY_DUPLICATE_PAIR = "BLOCKED_BY_DUPLICATE_PAIR"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_GOVERNED_MULTI_PAIR_BURST_VACATION_MODE_V1"

REQUIRED_BATCH_FIELDS = (
    "candidates",
    "min_candidate_score",
    "max_candidates_per_burst",
    "require_stop_loss",
    "require_take_profit",
    "require_session_allowed",
    "require_news_blackout_clear",
    "require_spread_within_limit",
    "require_slippage_within_limit",
    "duplicate_pair_block",
)

REQUIRED_CANDIDATE_FIELDS = (
    "pair",
    "side",
    "order_type",
    "units",
    "setup_id",
    "evidence_id",
    "candidate_score",
    "expected_r_multiple",
    "minimum_reward_risk_ratio",
    "stop_loss_present",
    "take_profit_present",
    "session_allowed",
    "news_blackout_clear",
    "spread_within_limit",
    "slippage_within_limit",
)


def evaluate_forex_multi_pair_opportunity_batch_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a ranked candidate batch without execution side effects."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _batch_result(source, BLOCKED_BY_SENSITIVE_DATA, sensitive_blockers)
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _batch_result(source, BLOCKED_BY_BANKING_FOCUS, banking_blockers)

    universe = _mapping(source.get("pair_universe_result"))
    if universe.get("status") != MULTI_PAIR_UNIVERSE_READY or universe.get("ready") is not True:
        return _batch_result(source, BLOCKED_BY_PAIR_UNIVERSE, ("pair_universe_not_ready",))

    batch = _mapping(source.get("opportunity_batch"))
    if not batch:
        return _batch_result(source, INCOMPLETE_INPUTS, ("opportunity_batch_missing",))
    missing = tuple(field for field in REQUIRED_BATCH_FIELDS if field not in batch)
    if missing:
        return _batch_result(source, INCOMPLETE_INPUTS, tuple(f"missing_{field}" for field in missing))

    candidates = batch.get("candidates")
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes, bytearray)) or not candidates:
        return _batch_result(source, BLOCKED_BY_EMPTY_CANDIDATES, ("candidate_batch_empty",))

    policy_gates = {
        "require_stop_loss": _bool(batch.get("require_stop_loss")),
        "require_take_profit": _bool(batch.get("require_take_profit")),
        "require_session_allowed": _bool(batch.get("require_session_allowed")),
        "require_news_blackout_clear": _bool(batch.get("require_news_blackout_clear")),
        "require_spread_within_limit": _bool(batch.get("require_spread_within_limit")),
        "require_slippage_within_limit": _bool(batch.get("require_slippage_within_limit")),
    }
    false_policy = tuple(key for key, value in policy_gates.items() if not value)
    if false_policy:
        return _batch_result(source, INCOMPLETE_INPUTS, false_policy)

    min_score = _number(batch.get("min_candidate_score"))
    max_candidates = _int(batch.get("max_candidates_per_burst"))
    if max_candidates < 1:
        return _batch_result(source, INCOMPLETE_INPUTS, ("max_candidates_per_burst_below_one",))

    allowed_pairs = set(str(pair) for pair in universe.get("allowed_pairs_sanitized", []))
    duplicate_pair_block = _bool(batch.get("duplicate_pair_block"))
    normalized_candidates = [_candidate_summary(item) for item in candidates if isinstance(item, Mapping)]
    pairs = [item["pair"] for item in normalized_candidates]
    duplicate_pairs = sorted({pair for pair in pairs if pairs.count(pair) > 1})
    if duplicate_pairs and duplicate_pair_block:
        return _batch_result(
            source,
            BLOCKED_BY_DUPLICATE_PAIR,
            tuple(f"duplicate_pair_{pair}" for pair in duplicate_pairs),
            candidate_count=len(normalized_candidates),
        )

    rejected: list[dict[str, Any]] = []
    selected_pool: list[dict[str, Any]] = []
    blocking_status = ""
    blocking_reasons: list[str] = []

    for candidate in normalized_candidates:
        reasons = _candidate_rejection_reasons(candidate, allowed_pairs, min_score)
        if reasons:
            rejected.append({"pair": candidate.get("pair", ""), "setup_id": candidate.get("setup_id", ""), "reasons": reasons})
            if any("spread_within_limit_false" in reason or "slippage_within_limit_false" in reason for reason in reasons):
                blocking_status = BLOCKED_BY_SPREAD_SLIPPAGE
                blocking_reasons.extend(reasons)
            elif any("news_blackout_clear_false" in reason for reason in reasons):
                blocking_status = BLOCKED_BY_NEWS_BLACKOUT
                blocking_reasons.extend(reasons)
            elif any("pair_not_allowed" in reason for reason in reasons):
                blocking_status = BLOCKED_BY_PAIR_UNIVERSE
                blocking_reasons.extend(reasons)
            else:
                blocking_reasons.extend(reasons)
            continue
        selected_pool.append(candidate)

    if blocking_status:
        return _batch_result(
            source,
            blocking_status,
            tuple(blocking_reasons),
            candidate_count=len(normalized_candidates),
            rejected_candidates_summary=rejected,
        )
    if not selected_pool:
        return _batch_result(
            source,
            BLOCKED_BY_CANDIDATE_QUALITY,
            tuple(blocking_reasons or ["no_candidate_met_quality_gates"]),
            candidate_count=len(normalized_candidates),
            rejected_candidates_summary=rejected,
        )

    if duplicate_pairs and not duplicate_pair_block:
        selected_by_pair: dict[str, dict[str, Any]] = {}
        for candidate in selected_pool:
            existing = selected_by_pair.get(candidate["pair"])
            if existing is None or candidate["candidate_score"] > existing["candidate_score"]:
                selected_by_pair[candidate["pair"]] = candidate
        selected_pool = list(selected_by_pair.values())

    selected = sorted(
        selected_pool,
        key=lambda item: (item["candidate_score"], item["expected_r_multiple"]),
        reverse=True,
    )[:max_candidates]
    extra = _batch_extra(
        selected_candidates=selected,
        rejected_candidates_summary=rejected,
        candidate_count=len(normalized_candidates),
        selected_count=len(selected),
        ready_for_basket_risk_governor=True,
    )
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=MULTI_PAIR_OPPORTUNITY_BATCH_READY,
        ready=True,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=True,
        blockers=(),
        next_best_packet="AIOS_FOREX_BASKET_RISK_EXPOSURE_GOVERNOR_V1",
        safe_manual_next_action="Route selected candidates into the basket risk exposure governor.",
        extra=extra,
    )


def _candidate_rejection_reasons(candidate: Mapping[str, Any], allowed_pairs: set[str], min_score: float) -> list[str]:
    reasons: list[str] = []
    missing = [field for field in REQUIRED_CANDIDATE_FIELDS if field not in candidate]
    reasons.extend(f"missing_{field}" for field in missing)
    if candidate.get("pair") not in allowed_pairs:
        reasons.append("pair_not_allowed")
    if candidate.get("candidate_score", 0.0) < min_score:
        reasons.append("candidate_score_below_minimum")
    if candidate.get("expected_r_multiple", 0.0) < candidate.get("minimum_reward_risk_ratio", 0.0):
        reasons.append("expected_r_below_minimum_reward_risk")
    for field in (
        "stop_loss_present",
        "take_profit_present",
        "session_allowed",
        "news_blackout_clear",
        "spread_within_limit",
        "slippage_within_limit",
    ):
        if candidate.get(field) is not True:
            reasons.append(f"{field}_false")
    if candidate.get("units", 0.0) <= 0:
        reasons.append("units_not_positive")
    return _unique(reasons)


def _candidate_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "pair": _pair_text(data.get("pair")),
        "side": str(data.get("side", "")).upper(),
        "order_type": str(data.get("order_type", "")).upper(),
        "units": _number(data.get("units")),
        "setup_id": str(data.get("setup_id", "")),
        "evidence_id": str(data.get("evidence_id", "")),
        "candidate_score": _number(data.get("candidate_score")),
        "expected_r_multiple": _number(data.get("expected_r_multiple")),
        "minimum_reward_risk_ratio": _number(data.get("minimum_reward_risk_ratio")),
        "risk_pct": _number(data.get("risk_pct")),
        "stop_loss_present": _bool(data.get("stop_loss_present")),
        "take_profit_present": _bool(data.get("take_profit_present")),
        "session_allowed": _bool(data.get("session_allowed")),
        "news_blackout_clear": _bool(data.get("news_blackout_clear")),
        "spread_within_limit": _bool(data.get("spread_within_limit")),
        "slippage_within_limit": _bool(data.get("slippage_within_limit")),
    }


def _batch_result(
    source: Mapping[str, Any],
    status: str,
    blockers: Sequence[str],
    *,
    candidate_count: int = 0,
    rejected_candidates_summary: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=False,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=False,
        blockers=blockers,
        next_best_packet=NEXT_BEST_PACKET,
        safe_manual_next_action=_safe_manual_next_action(status),
        extra=_batch_extra(
            candidate_count=candidate_count,
            rejected_candidates_summary=rejected_candidates_summary,
        ),
    )


def _batch_extra(
    *,
    selected_candidates: Sequence[Mapping[str, Any]] = (),
    rejected_candidates_summary: Sequence[Mapping[str, Any]] = (),
    candidate_count: int = 0,
    selected_count: int = 0,
    ready_for_basket_risk_governor: bool = False,
) -> dict[str, Any]:
    return {
        "selected_candidates": [dict(item) for item in selected_candidates],
        "rejected_candidates_summary": [dict(item) for item in rejected_candidates_summary],
        "candidate_count": candidate_count,
        "selected_count": selected_count,
        "ready_for_basket_risk_governor": ready_for_basket_risk_governor,
    }


def _safe_manual_next_action(status: str) -> str:
    if status == BLOCKED_BY_PAIR_UNIVERSE:
        return "Repair the pair universe result before scoring opportunities."
    if status == BLOCKED_BY_EMPTY_CANDIDATES:
        return "Provide at least one sanitized candidate trade."
    if status == BLOCKED_BY_SPREAD_SLIPPAGE:
        return "Remove candidates that fail spread or slippage gates."
    if status == BLOCKED_BY_NEWS_BLACKOUT:
        return "Remove candidates inside news blackout windows."
    if status == BLOCKED_BY_DUPLICATE_PAIR:
        return "Keep only one candidate per pair or explicitly allow highest-ranked de-duplication."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, or money-movement focus fields."
    return "Repair candidate quality metadata and rerun."
