"""Governed review-only multi-pair opportunity scorer for paper/sim pipelines."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Sequence

from automation.forex_engine import schema_contracts as schemas


FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1 = "FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1"
SCORER_SCHEMA = "AIOS_FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1"

DEFAULT_MAX_PAIR_RISK_PERCENT = 2.0
DEFAULT_MAX_TOTAL_PORTFOLIO_RISK_PERCENT = 6.0
DEFAULT_MAX_PAIR_CAP_FLOOR = 0.0
DEFAULT_MAX_PORTFOLIO_CAP = 99.0

DEFAULT_MIN_SAMPLE_SIZE = 30
DEFAULT_MAX_EVIDENCE_AGE_DAYS = 45.0
DEFAULT_MIN_CONFIDENCE_SCORE = 40.0
DEFAULT_MIN_EVIDENCE_QUALITY = 45.0
DEFAULT_MAX_SPREAD_BPS = 4.5
DEFAULT_MAX_VOLATILITY = 2.4
DEFAULT_MAX_DRAWDOWN_PERCENT = 25.0
DEFAULT_MAX_LEVERAGE = 30.0

DEFAULT_CORRELATION_THRESHOLD = 0.70
DEFAULT_CORRELATION_PENALTY = 0.35
DEFAULT_DOMINANCE_THRESHOLD_LOW = 1.40
DEFAULT_DOMINANCE_THRESHOLD_HIGH = 1.75
DEFAULT_DOMINANCE_BONUS_LOW = 1.12
DEFAULT_DOMINANCE_BONUS_MID = 1.18
DEFAULT_DOMINANCE_BONUS_HIGH = 1.28
DEFAULT_EVIDENCE_REQUIRED_FOR_DOMINANCE = 75.0

SCORE_WEIGHTS = {
    "confidence": 0.22,
    "spread": 0.16,
    "volatility": 0.13,
    "liquidity": 0.14,
    "expectancy": 0.20,
    "drawdown": 0.12,
    "evidence": 0.13,
}


def score_multi_pair_opportunities(
    pair_metrics: Sequence[Mapping[str, Any]] | None,
    *,
    risk_policy: Mapping[str, Any] | None = None,
    execution_context: Mapping[str, Any] | None = None,
    pair_correlation_matrix: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Score and rank read-only pair opportunities with constrained allocation."""

    policy, policy_warnings = _normalize_policy(risk_policy)
    context = dict(execution_context or {})
    context_blockers = _global_blockers(context)

    normalized: list[dict[str, Any]] = []
    rejection_reasons = list(policy_warnings)

    if pair_metrics is None:
        pair_metrics = []
    elif not isinstance(pair_metrics, Sequence) or isinstance(pair_metrics, (str, bytes, bytearray)):
        rejection_reasons.append("input_must_be_sequence")
        pair_metrics = []

    for index, pair in enumerate(pair_metrics):
        if isinstance(pair, Mapping):
            normalized.append(_normalize_pair_payload(pair, index, policy))
        else:
            normalized.append(_malformed_pair_payload(index))

    if not pair_metrics:
        rejection_reasons.append("no_valid_pair_metrics")

    for item in normalized:
        reasons = list(item["rejection_reasons"])
        reasons.extend(rejection_reasons)
        reasons.extend(context_blockers)
        item["rejection_reasons"] = _unique(reasons)
        item["eligible"] = not bool(item["rejection_reasons"])

    eligible_pairs = [item for item in normalized if item["eligible"]]
    rejected_pairs = [item for item in normalized if not item["eligible"]]

    ranked_eligible = sorted(
        eligible_pairs,
        key=lambda item: (
            -(_safe_float(item["pair_score"]) or 0.0),
            -(_safe_float(item["confidence_score"]) or 0.0),
            _safe_str(item["pair"]),
        ),
    )

    allocations = _proposed_allocations(ranked_eligible, policy, pair_correlation_matrix)
    for rank, item in enumerate(ranked_eligible, start=1):
        item["rank"] = rank
        item["proposed_allocation_percent"] = allocations.get(item["pair"], 0.0)
    for item in rejected_pairs:
        item["rank"] = 0
        item["proposed_allocation_percent"] = 0.0

    ranked_pairs = ranked_eligible + rejected_pairs

    total_portfolio_risk_percent = _round_float(
        sum(item["proposed_allocation_percent"] for item in ranked_eligible),
        6,
    )

    if ranked_eligible and total_portfolio_risk_percent <= 0:
        safe_next_action = (
            "No allocation was produced due to score/cap constraints. "
            "Collect stronger evidence, reduce concentration risks, and rerun read-only scoring."
        )
    elif ranked_eligible:
        safe_next_action = (
            "Paper/simulation-only multi-pair allocation is ready for review. "
            "Do not route live orders, run scheduler/daemon/webhook execution, "
            "or increase live capital until owner approval and repeatability evidence are complete."
        )
    elif "input_must_be_sequence" in rejection_reasons or "no_valid_pair_metrics" in rejection_reasons:
        safe_next_action = "Collect and provide valid read-only pair metrics before rerunning scoring."
    else:
        safe_next_action = "Repair rejected pair blockers and rerun read-only scoring."

    rejection_reasons = _unique(rejection_reasons + [
        reason
        for item in normalized
        for reason in item["rejection_reasons"]
    ])

    ranking_scores = {
        "confidence_score": _weighted_average(ranked_eligible, "confidence_score"),
        "spread_score": _weighted_average(ranked_eligible, "spread_score"),
        "volatility_score": _weighted_average(ranked_eligible, "volatility_score"),
        "liquidity_score": _weighted_average(ranked_eligible, "liquidity_score"),
        "expectancy_score": _weighted_average(ranked_eligible, "expectancy_score"),
        "risk_adjusted_score": _weighted_average(ranked_eligible, "risk_adjusted_score"),
    }

    result: dict[str, Any] = {
        "schema": SCORER_SCHEMA,
        "mode": schemas.PAPER_ONLY,
        "engine_version": FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1,
        "ranked_pairs": ranked_pairs,
        "max_pair_risk_percent": policy["max_pair_risk_percent"],
        "total_portfolio_risk_percent": total_portfolio_risk_percent,
        "proposed_allocation_percent": total_portfolio_risk_percent,
        "rejection_reasons": rejection_reasons,
        "safe_next_action": safe_next_action,
        "review_only": True,
        "confidence_score": ranking_scores["confidence_score"],
        "spread_score": ranking_scores["spread_score"],
        "volatility_score": ranking_scores["volatility_score"],
        "liquidity_score": ranking_scores["liquidity_score"],
        "expectancy_score": ranking_scores["expectancy_score"],
        "risk_adjusted_score": ranking_scores["risk_adjusted_score"],
        "safety": _safety(),
        "execution_context": {
            "kill_switch_active": bool(context.get("kill_switch_active", False)),
            "daily_loss_stop_reached": bool(context.get("daily_loss_stop_reached", context.get("daily_loss_limit_reached", False))),
            "pair_repair_mode": bool(context.get("pair_repair_mode", False)),
            "scheduler_enabled": bool(context.get("scheduler_enabled", False)),
            "daemon_enabled": bool(context.get("daemon_enabled", False)),
            "webhook_enabled": bool(context.get("webhook_enabled", False)),
            "broker_integration_enabled": bool(context.get("broker_integration_enabled", False)),
            "live_execution_requested": bool(context.get("live_execution_requested", False)),
            "owner_approved_live_capital_increase": bool(context.get("owner_approved_live_capital_increase", False)),
        },
    }

    schemas.assert_no_live_permissions(result)
    return result


def _normalize_pair_payload(
    pair_payload: Mapping[str, Any],
    index: int,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    pair = _normalize_pair(pair_payload.get("pair"), default=f"PAIR_{index:03d}")

    rejection_reasons: list[str] = []

    confidence_score = _extract_score(
        pair_payload,
        ("confidence_score", "confidence", "signal_strength", "confidence_pct"),
    )
    spread_score = _resolve_spread_score(pair_payload, policy)
    volatility_score = _resolve_volatility_score(pair_payload, policy)
    liquidity_score = _extract_score(
        pair_payload,
        ("liquidity_score", "liquidity", "liquidity_quality_score"),
        default=60.0,
    )
    expectancy_score = _extract_score(
        pair_payload,
        ("expectancy_score", "expectancy", "expectancy_ratio", "edge_score"),
        default=45.0,
    )
    drawdown_score = _resolve_drawdown_score(pair_payload, policy)

    sample_size = _safe_int(pair_payload.get("sample_size"))
    evidence_age = _safe_float(pair_payload.get("evidence_age_days"))
    evidence_quality = _extract_score(
        pair_payload,
        ("evidence_quality_score", "evidence_score", "quality_score"),
        default=None,
    )

    spread_bps = _safe_float(pair_payload.get("spread_bps", pair_payload.get("spread")))
    if spread_bps is not None and spread_bps > policy["max_spread_bps"]:
        rejection_reasons.append("pair_spread_guard_violated")
    if not pair_payload.get("pair"):
        rejection_reasons.append("missing_pair")

    slippage_bps = _safe_float(pair_payload.get("estimated_slippage_bps", pair_payload.get("slippage_bps")))
    if slippage_bps is not None and slippage_bps > policy["max_spread_bps"]:
        rejection_reasons.append("pair_slippage_guard_violated")

    volatility_raw = _safe_float(pair_payload.get("volatility", pair_payload.get("atr")))
    if volatility_raw is not None and volatility_raw > policy["max_volatility"]:
        rejection_reasons.append("pair_volatility_guard_violated")

    drawdown_raw = _safe_float(
        pair_payload.get("max_drawdown_pct", pair_payload.get("drawdown_pct", pair_payload.get("drawdown")))
    )
    if drawdown_raw is not None and drawdown_raw > policy["max_drawdown_percent"]:
        rejection_reasons.append("pair_drawdown_guard_violated")

    if sample_size is not None and sample_size < policy["min_sample_size"]:
        rejection_reasons.append("insufficient_sample_size")
    if evidence_age is not None and evidence_age > policy["max_evidence_age_days"]:
        rejection_reasons.append("evidence_too_old")

    evidence_score = evidence_quality if evidence_quality is not None else _evidence_score_from_inputs(sample_size, evidence_age)
    if evidence_score < policy["min_evidence_quality"]:
        rejection_reasons.append("low_evidence_quality")

    if confidence_score < policy["min_confidence_score"]:
        rejection_reasons.append("low_confidence_score")

    leverage = _safe_float(pair_payload.get("leverage"))
    if leverage is not None and leverage > policy["max_leverage"]:
        rejection_reasons.append("uncontrolled_leverage")

    sizing_model = str(pair_payload.get("position_sizing_model", "")).lower()
    if _contains_forbidden_terms(sizing_model) or bool(pair_payload.get("is_martingale")):
        rejection_reasons.append("forbidden_sizing_model")
    if bool(pair_payload.get("is_revenge") or pair_payload.get("averaging_down")):
        rejection_reasons.append("forbidden_sizing_model")

    pair_score = _weighted_score(
        confidence_score,
        spread_score,
        volatility_score,
        liquidity_score,
        expectancy_score,
        drawdown_score,
        evidence_score,
    )
    if rejection_reasons:
        pair_score = 0.0

    risk_adjusted_score = _round_float(
        (
            (confidence_score * 0.15)
            + (expectancy_score * 0.46)
            + (drawdown_score * 0.24)
            + (spread_score * 0.10)
            + (volatility_score * 0.05)
        ),
        6,
    )

    return {
        "pair": pair,
        "confidence_score": confidence_score,
        "spread_score": spread_score,
        "volatility_score": volatility_score,
        "liquidity_score": liquidity_score,
        "expectancy_score": expectancy_score,
        "drawdown_score": drawdown_score,
        "evidence_score": evidence_score,
        "risk_adjusted_score": risk_adjusted_score,
        "pair_score": pair_score,
        "rejection_reasons": rejection_reasons,
        "eligible": False,
        "proposed_allocation_percent": 0.0,
        "rank": 0,
        "raw_values": dict(pair_payload),
    }


def _malformed_pair_payload(index: int) -> dict[str, Any]:
    return {
        "pair": f"PAIR_{index:03d}",
        "confidence_score": 0.0,
        "spread_score": 0.0,
        "volatility_score": 0.0,
        "liquidity_score": 0.0,
        "expectancy_score": 0.0,
        "drawdown_score": 0.0,
        "evidence_score": 0.0,
        "risk_adjusted_score": 0.0,
        "pair_score": 0.0,
        "rejection_reasons": ["non_mapping_pair_payload"],
        "eligible": False,
        "proposed_allocation_percent": 0.0,
        "rank": 0,
        "raw_values": {},
    }


def _proposed_allocations(
    ranked_pairs: list[dict[str, Any]],
    policy: Mapping[str, Any],
    pair_correlation_matrix: Mapping[str, Any] | None,
) -> dict[str, float]:
    if not ranked_pairs:
        return {}

    total_budget = _safe_float(policy["max_total_portfolio_risk_percent"]) or 0.0
    pair_cap = _safe_float(policy["max_pair_risk_percent"]) or 0.0
    if pair_cap <= 0 or total_budget <= 0:
        return {item["pair"]: 0.0 for item in ranked_pairs}

    weighted: list[tuple[str, float]] = []
    for index, item in enumerate(ranked_pairs):
        pair = str(item["pair"])
        weight = float(item["pair_score"])
        if weight <= 0:
            continue
        if index == 0:
            weight *= _dominance_boost(ranked_pairs, policy)
        weight *= _correlation_factor(pair, ranked_pairs, index, pair_correlation_matrix, policy)
        if weight > 0:
            weighted.append((pair, weight))

    if not weighted:
        return {item["pair"]: 0.0 for item in ranked_pairs}

    allocation: dict[str, float] = {pair: 0.0 for pair, _ in weighted}
    remaining: dict[str, float] = dict(weighted)
    remaining_budget = total_budget

    while remaining and remaining_budget > 0:
        total_weight = sum(remaining.values())
        if total_weight <= 0:
            break

        capped = False
        next_remaining: dict[str, float] = {}

        for pair, weight in remaining.items():
            proposed = remaining_budget * (weight / total_weight)
            if proposed >= pair_cap:
                allocation[pair] = _round_float(allocation[pair] + pair_cap, 6)
                remaining_budget = _round_float(remaining_budget - pair_cap, 6)
                capped = True
            else:
                next_remaining[pair] = weight

        if not capped:
            for pair, weight in remaining.items():
                allocation[pair] = _round_float(
                    allocation[pair] + remaining_budget * (weight / total_weight),
                    6,
                )
            break

        remaining = next_remaining

    return allocation


def _dominance_boost(ranked_pairs: list[dict[str, Any]], policy: Mapping[str, Any]) -> float:
    if len(ranked_pairs) < 2:
        return 1.0

    top = ranked_pairs[0]
    second = ranked_pairs[1]
    top_score = float(top["pair_score"])
    second_score = float(second["pair_score"])
    if second_score <= 0:
        return DEFAULT_DOMINANCE_BONUS_HIGH

    ratio = top_score / second_score
    top_evidence = float(top.get("evidence_score", 0.0))
    if ratio >= DEFAULT_DOMINANCE_THRESHOLD_HIGH and top_evidence >= DEFAULT_EVIDENCE_REQUIRED_FOR_DOMINANCE:
        return DEFAULT_DOMINANCE_BONUS_HIGH
    if ratio >= DEFAULT_DOMINANCE_THRESHOLD_LOW and top_evidence >= DEFAULT_EVIDENCE_REQUIRED_FOR_DOMINANCE:
        return DEFAULT_DOMINANCE_BONUS_MID
    if top_evidence >= DEFAULT_EVIDENCE_REQUIRED_FOR_DOMINANCE and ratio >= 1.0:
        return DEFAULT_DOMINANCE_BONUS_LOW
    return 1.0


def _correlation_factor(
    pair: str,
    ranked_pairs: list[dict[str, Any]],
    index: int,
    pair_correlation_matrix: Mapping[str, Any] | None,
    policy: Mapping[str, Any],
) -> float:
    if not pair_correlation_matrix:
        return 1.0

    source_row = _safe_mapping(pair_correlation_matrix.get(pair))
    if source_row is None:
        source_row = _safe_mapping(pair_correlation_matrix.get(_normalize_pair(pair, default=pair)))
    if source_row is None:
        return 1.0

    other_pairs = [item["pair"] for item_index, item in enumerate(ranked_pairs) if item_index != index]
    if not other_pairs:
        return 1.0

    correlations = [
        _safe_float(source_row.get(other_pair))
        for other_pair in other_pairs
        if _safe_float(source_row.get(other_pair)) is not None
    ]
    if not correlations:
        return 1.0

    threshold = _safe_float(policy["correlation_threshold"]) or 0.0
    if threshold < 0.0 or threshold >= 1.0:
        return 1.0

    penalty = _safe_float(policy["correlation_penalty"]) or 0.0
    if penalty <= 0:
        return 1.0

    max_corr = max(abs(value) for value in correlations)
    if max_corr <= threshold:
        return 1.0

    intensity = min(1.0, (max_corr - threshold) / (1.0 - threshold))
    return _round_float(max(0.4, 1.0 - (intensity * penalty)), 6)


def _global_blockers(execution_context: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if bool(execution_context.get("kill_switch_active", False)) or bool(execution_context.get("kill_switch_enabled", False)):
        blockers.append("kill_switch_active")
    if bool(execution_context.get("daily_loss_stop_reached", execution_context.get("daily_loss_limit_reached", False))):
        blockers.append("daily_loss_stop_reached")
    if bool(execution_context.get("scheduler_enabled", False)):
        blockers.append("scheduler_enabled_not_allowed")
    if bool(execution_context.get("daemon_enabled", False)):
        blockers.append("daemon_enabled_not_allowed")
    if bool(execution_context.get("webhook_enabled", False)):
        blockers.append("webhook_enabled_not_allowed")
    if bool(execution_context.get("broker_integration_enabled", False)):
        blockers.append("broker_integration_not_allowed")
    if bool(execution_context.get("live_execution_requested", False)):
        blockers.append("live_execution_requested_not_allowed")

    if bool(execution_context.get("request_auto_risk_scaling", False)) and not bool(
        execution_context.get("owner_approved_live_capital_increase", False)
    ):
        blockers.append("owner_approval_required_for_live_capital_increase")
    if bool(execution_context.get("pair_repair_mode", False)) and not bool(
        execution_context.get("pair_repair_evidence_present", False)
    ):
        blockers.append("pair_repair_evidence_missing")

    if not bool(execution_context.get("margin_guard_active", execution_context.get("margin_guard_ok", True))):
        blockers.append("margin_guard_blocked")

    return blockers


def _weighted_score(
    confidence_score: float,
    spread_score: float,
    volatility_score: float,
    liquidity_score: float,
    expectancy_score: float,
    drawdown_score: float,
    evidence_score: float,
) -> float:
    value = (
        confidence_score * SCORE_WEIGHTS["confidence"]
        + spread_score * SCORE_WEIGHTS["spread"]
        + volatility_score * SCORE_WEIGHTS["volatility"]
        + liquidity_score * SCORE_WEIGHTS["liquidity"]
        + expectancy_score * SCORE_WEIGHTS["expectancy"]
        + drawdown_score * SCORE_WEIGHTS["drawdown"]
        + evidence_score * SCORE_WEIGHTS["evidence"]
    )
    return _round_float(max(0.0, value), 6)


def _extract_score(
    payload: Mapping[str, Any],
    keys: Sequence[str],
    *,
    default: float | None = None,
    max_score: float = 100.0,
) -> float:
    for key in keys:
        raw = payload.get(key)
        value = _safe_float(raw)
        if value is None:
            continue
        if 0 <= value <= 1:
            value *= 100.0
        return _clamp(value, 0.0, max_score)
    if default is None:
        return 0.0
    return _clamp(float(default), 0.0, max_score)


def _resolve_spread_score(payload: Mapping[str, Any], policy: Mapping[str, Any]) -> float:
    score = _extract_score(payload, ("spread_score", "spread_quality_score"), default=None)
    if score > 0:
        return score

    spread = _safe_float(payload.get("spread_bps", payload.get("spread")))
    if spread is None:
        return _extract_score(payload, ("liquidity_score", "liquidity"), default=50.0)

    max_spread = _safe_float(policy["max_spread_bps"]) or 0.0
    if spread <= 0:
        return 100.0
    if max_spread <= 0:
        return 0.0
    return _clamp(100.0 - ((spread / max_spread) * 100.0), 0.0, 100.0)


def _resolve_volatility_score(payload: Mapping[str, Any], policy: Mapping[str, Any]) -> float:
    score = _extract_score(payload, ("volatility_score", "volatility_quality_score"), default=None)
    if score > 0:
        return score

    raw = _safe_float(payload.get("volatility", payload.get("atr")))
    if raw is None:
        return 50.0

    max_volatility = _safe_float(policy["max_volatility"]) or 0.0
    if raw <= 0:
        return 100.0
    if max_volatility <= 0:
        return 0.0
    return _clamp(100.0 - ((raw / max_volatility) * 100.0), 0.0, 100.0)


def _resolve_drawdown_score(payload: Mapping[str, Any], policy: Mapping[str, Any]) -> float:
    score = _extract_score(payload, ("drawdown_score", "drawdown_quality_score"), default=None)
    if score > 0:
        return score

    drawdown = _safe_float(payload.get("max_drawdown_pct", payload.get("drawdown_pct", payload.get("drawdown"))))
    if drawdown is None:
        return 60.0
    if drawdown <= 0:
        return 100.0

    max_drawdown = _safe_float(policy["max_drawdown_percent"]) or 0.0
    if max_drawdown <= 0:
        return 0.0
    return _clamp(100.0 - ((drawdown / max_drawdown) * 100.0), 0.0, 100.0)


def _evidence_score_from_inputs(sample_size: int | None, evidence_age: float | None) -> float:
    if sample_size is None:
        sample_score = 35.0
    else:
        sample_score = _clamp(float(sample_size), 0.0, 100.0)

    if evidence_age is None:
        age_score = 40.0
    elif evidence_age <= 1:
        age_score = 100.0
    elif evidence_age <= 7:
        age_score = 90.0
    elif evidence_age <= 30:
        age_score = 70.0
    elif evidence_age <= 90:
        age_score = 45.0
    else:
        age_score = 15.0

    return _round_float((sample_score * 0.5) + (age_score * 0.5), 6)


def _normalize_policy(risk_policy: Mapping[str, Any] | None) -> tuple[dict[str, Any], list[str]]:
    policy_input = dict(risk_policy or {})
    warnings: list[str] = []
    policy = {
        "max_pair_risk_percent": _normalize_percent(
            policy_input.get("max_pair_risk_percent"),
            "max_pair_risk_percent",
            DEFAULT_MAX_PAIR_RISK_PERCENT,
            DEFAULT_MAX_PAIR_CAP_FLOOR,
            DEFAULT_MAX_PORTFOLIO_CAP,
            warnings,
        ),
        "max_total_portfolio_risk_percent": min(
            _normalize_percent(
                policy_input.get("max_total_portfolio_risk_percent"),
                "max_total_portfolio_risk_percent",
                DEFAULT_MAX_TOTAL_PORTFOLIO_RISK_PERCENT,
                DEFAULT_MAX_PAIR_CAP_FLOOR,
                DEFAULT_MAX_PORTFOLIO_CAP,
                warnings,
            ),
            DEFAULT_MAX_PORTFOLIO_CAP,
        ),
        "min_sample_size": _normalize_int(
            policy_input.get("min_sample_size"),
            "min_sample_size",
            DEFAULT_MIN_SAMPLE_SIZE,
            1,
            1_000_000,
            warnings,
        ),
        "max_evidence_age_days": _normalize_percent(
            policy_input.get("max_evidence_age_days"),
            "max_evidence_age_days",
            DEFAULT_MAX_EVIDENCE_AGE_DAYS,
            0.0,
            3650.0,
            warnings,
        ),
        "min_confidence_score": _normalize_percent(
            policy_input.get("min_confidence_score"),
            "min_confidence_score",
            DEFAULT_MIN_CONFIDENCE_SCORE,
            0.0,
            100.0,
            warnings,
        ),
        "min_evidence_quality": _normalize_percent(
            policy_input.get("min_evidence_quality"),
            "min_evidence_quality",
            DEFAULT_MIN_EVIDENCE_QUALITY,
            0.0,
            100.0,
            warnings,
        ),
        "max_spread_bps": _normalize_percent(
            policy_input.get("max_spread_bps"),
            "max_spread_bps",
            DEFAULT_MAX_SPREAD_BPS,
            0.0,
            1000.0,
            warnings,
        ),
        "max_volatility": _normalize_percent(
            policy_input.get("max_volatility"),
            "max_volatility",
            DEFAULT_MAX_VOLATILITY,
            0.0,
            1000.0,
            warnings,
        ),
        "max_drawdown_percent": _normalize_percent(
            policy_input.get("max_drawdown_percent"),
            "max_drawdown_percent",
            DEFAULT_MAX_DRAWDOWN_PERCENT,
            0.0,
            1000.0,
            warnings,
        ),
        "max_leverage": _normalize_percent(
            policy_input.get("max_leverage"),
            "max_leverage",
            DEFAULT_MAX_LEVERAGE,
            1.0,
            1000.0,
            warnings,
        ),
        "correlation_threshold": _normalize_percent(
            policy_input.get("correlation_threshold"),
            "correlation_threshold",
            DEFAULT_CORRELATION_THRESHOLD,
            0.0,
            1.0,
            warnings,
        ),
        "correlation_penalty": _normalize_percent(
            policy_input.get("correlation_penalty"),
            "correlation_penalty",
            DEFAULT_CORRELATION_PENALTY,
            0.0,
            1.0,
            warnings,
        ),
    }

    if policy["max_pair_risk_percent"] > policy["max_total_portfolio_risk_percent"]:
        policy["max_pair_risk_percent"] = policy["max_total_portfolio_risk_percent"]
        warnings.append("max_pair_risk_percent_clamped_to_total_portfolio_cap")

    if policy["max_pair_risk_percent"] <= 0:
        warnings.append("policy_max_pair_risk_percent_non_positive")
    if policy["max_total_portfolio_risk_percent"] <= 0:
        warnings.append("policy_max_total_portfolio_risk_percent_non_positive")

    return policy, warnings


def _normalize_percent(
    raw: Any,
    field_name: str,
    default: float,
    minimum: float,
    maximum: float,
    warnings: list[str],
) -> float:
    value = _safe_float(raw)
    if value is None:
        if raw is not None:
            warnings.append(f"{field_name}_invalid_or_missing_using_default")
        return _round_float(float(default), 6)

    if value < minimum:
        warnings.append(f"{field_name}_below_minimum")
        return _round_float(minimum, 6)
    if value > maximum:
        warnings.append(f"{field_name}_above_maximum")
        return _round_float(maximum, 6)
    return _round_float(value, 6)


def _normalize_int(
    raw: Any,
    field_name: str,
    default: int,
    minimum: int,
    maximum: int,
    warnings: list[str],
) -> int:
    value = _safe_int(raw)
    if value is None:
        if raw is not None:
            warnings.append(f"{field_name}_invalid_or_missing_using_default")
        return int(default)
    if value < minimum:
        warnings.append(f"{field_name}_below_minimum")
        return int(minimum)
    if value > maximum:
        warnings.append(f"{field_name}_above_maximum")
        return int(maximum)
    return int(value)


def _weighted_average(items: list[dict[str, Any]], field_name: str) -> float:
    if not items:
        return 0.0

    total_weight = sum(float(item["proposed_allocation_percent"]) for item in items)
    if total_weight > 0:
        weighted = sum(float(item[field_name]) * float(item["proposed_allocation_percent"]) for item in items)
        return _round_float(weighted / total_weight, 6)

    fallback = sum(float(item[field_name]) for item in items) / max(1, len(items))
    return _round_float(fallback, 6)


def _contains_forbidden_terms(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in ("martingale", "revenge", "averaging", "grid"))


def _normalize_pair(value: Any, *, default: str) -> str:
    if value is None or value == "":
        return default
    normalized = str(value).strip().upper().replace("/", "").replace("_", "").replace("-", "")
    return normalized or default


def _safe_mapping(value: Any) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        return dict(value)
    return None


def _safe_float(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def _safe_int(value: Any) -> int | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return _round_float(min(maximum, max(minimum, value)), 6)


def _round_float(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def _safe_str(value: Any) -> str:
    return str(value)


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "local_only": True,
        "simulation_only": True,
        "read_only_inputs": True,
        "broker_integration": False,
        "live_trading": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "orders_allowed": False,
        "credentials_read": False,
        "network_market_data": False,
    }


__all__ = [
    "FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1",
    "SCORE_WEIGHTS",
    "score_multi_pair_opportunities",
]
