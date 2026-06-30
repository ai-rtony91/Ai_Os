"""Read-only Big-Winner Watchtower 22H6D V1 for supplied Forex candidates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SCHEMA = "AIOS_FOREX_BIG_WINNER_WATCHTOWER_22H6D_V1"
MODE = "READ_ONLY_BIG_WINNER_WATCHTOWER"

DEFAULT_POLICY = {
    "max_risk_percent": 1.0,
    "min_reward_risk_ratio": 3.0,
    "min_expected_r_multiple": 2.5,
    "min_expectancy_score": 60.0,
    "min_upside_capture_score": 65.0,
    "min_volatility_expansion_score": 55.0,
    "min_evidence_quality_score": 60.0,
    "min_liquidity_score": 50.0,
    "min_spread_score": 50.0,
    "min_slippage_score": 50.0,
    "min_drawdown_risk_score": 40.0,
    "min_invalidation_quality_score": 60.0,
    "min_sample_size": 20,
}

SCORE_WEIGHTS = {
    "asymmetric_payoff": 0.14,
    "reward_to_risk": 0.10,
    "upside_capture": 0.11,
    "expectancy": 0.11,
    "volatility_expansion": 0.08,
    "trend_alignment": 0.06,
    "liquidity": 0.07,
    "spread": 0.06,
    "slippage": 0.05,
    "drawdown_risk": 0.07,
    "evidence_quality": 0.08,
    "invalidation_quality": 0.05,
    "sample_size": 0.02,
}

WATCH_SCHEDULE = {
    "status": "REVIEW_ONLY_22H_6D",
    "hours_per_day": 22,
    "days_per_week": 6,
    "alert_only": True,
    "execution_allowed": False,
    "scheduler_created": False,
    "daemon_created": False,
    "webhook_created": False,
}

UNSAFE_BLOCKERS = {
    "live_execution_requested",
    "broker_api_requested",
    "auto_entry_requested",
    "leverage_escalation_requested",
    "credential_or_secret_supplied",
    "martingale_detected",
    "revenge_trade_detected",
}

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token",
    "secret",
    "credential",
    "credentials",
    "password",
    "account_number",
    "routing_number",
    "debit_card_number",
    "card_number",
    "cvv",
)


def evaluate_big_winner_watchtower_22h6d_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Rank supplied candidates for owner-reviewed paper/simulation only."""

    source = payload if isinstance(payload, Mapping) else {}
    policy = _normalize_policy(source.get("risk_policy"))
    candidates_input = _candidate_sequence(source.get("candidates"))
    global_blockers = _global_boundary_blockers(source)

    ranked_opportunities = [
        _evaluate_candidate(candidate, index, policy, global_blockers)
        for index, candidate in enumerate(candidates_input)
    ]
    ranked_opportunities.sort(
        key=lambda item: (
            -float(item["opportunity_score"]),
            -float(item["evidence_quality_score"]),
            -float(item["reward_risk_ratio"]),
            str(item["pair"]),
        )
    )

    for rank, candidate in enumerate(ranked_opportunities, start=1):
        candidate["rank"] = rank

    qualified = [
        candidate
        for candidate in ranked_opportunities
        if candidate["big_winner_candidate"] is True
    ]
    top_opportunity = qualified[0] if qualified else None
    rejected_count = sum(
        1 for candidate in ranked_opportunities if candidate["rejection_reasons"]
    )
    risk_flags = _unique(
        _candidate_risk_flags(global_blockers)
        + [
            flag
            for candidate in ranked_opportunities
            for flag in candidate["risk_flags"]
        ]
    )
    rejection_reasons = _unique(
        list(global_blockers)
        + [
            reason
            for candidate in ranked_opportunities
            for reason in candidate["rejection_reasons"]
        ]
    )
    unsafe_detected = any(reason in UNSAFE_BLOCKERS for reason in rejection_reasons)
    alert_queue = [_alert_for_candidate(candidate) for candidate in qualified]
    score_source = top_opportunity or (ranked_opportunities[0] if ranked_opportunities else {})

    alert_level = _alert_level(
        unsafe_detected,
        bool(top_opportunity),
        len(ranked_opportunities),
        rejected_count,
    )
    safe_next_action = _safe_next_action(unsafe_detected, bool(top_opportunity))

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "paper_only": True,
        "live_trading_allowed": False,
        "broker_api_allowed": False,
        "auto_entry_allowed": False,
        "leverage_escalation_allowed": False,
        "watch_schedule": dict(WATCH_SCHEDULE),
        "ranked_opportunities": ranked_opportunities,
        "top_opportunity": top_opportunity,
        "big_winner_candidate_count": len(qualified),
        "rejected_candidate_count": rejected_count,
        "alert_level": alert_level,
        "alert_queue": alert_queue,
        "opportunity_score": _score_from_candidate(score_source, "opportunity_score"),
        "asymmetric_payoff_score": _score_from_candidate(
            score_source, "asymmetric_payoff_score"
        ),
        "reward_to_risk_score": _score_from_candidate(
            score_source, "reward_to_risk_score"
        ),
        "upside_capture_score": _score_from_candidate(
            score_source, "upside_capture_score"
        ),
        "expectancy_score": _score_from_candidate(score_source, "expectancy_score"),
        "volatility_expansion_score": _score_from_candidate(
            score_source, "volatility_expansion_score"
        ),
        "trend_alignment_score": _score_from_candidate(
            score_source, "trend_alignment_score"
        ),
        "liquidity_score": _score_from_candidate(score_source, "liquidity_score"),
        "spread_score": _score_from_candidate(score_source, "spread_score"),
        "slippage_score": _score_from_candidate(score_source, "slippage_score"),
        "drawdown_risk_score": _score_from_candidate(
            score_source, "drawdown_risk_score"
        ),
        "evidence_quality_score": _score_from_candidate(
            score_source, "evidence_quality_score"
        ),
        "invalidation_quality_score": _score_from_candidate(
            score_source, "invalidation_quality_score"
        ),
        "risk_flags": risk_flags,
        "rejection_reasons": rejection_reasons,
        "owner_decision_required": True,
        "safe_next_action": safe_next_action,
        "safety": _safety_boundary(),
    }


def _evaluate_candidate(
    candidate_input: Any,
    index: int,
    policy: Mapping[str, Any],
    global_blockers: Sequence[str],
) -> dict[str, Any]:
    if not isinstance(candidate_input, Mapping):
        return _rejected_candidate(
            index,
            ["candidate_payload_not_mapping"],
            ["invalid_candidate_payload", "owner_decision_required"],
        )

    pair = _normalize_pair(candidate_input.get("pair"))
    direction = _normalize_text(candidate_input.get("direction")).upper()
    reward_risk_ratio = _safe_float(candidate_input.get("reward_risk_ratio"), 0.0)
    expected_r_multiple = _safe_float(candidate_input.get("expected_r_multiple"), 0.0)
    expectancy_score = _score(candidate_input.get("expectancy_score"), 0.0)
    upside_capture_score = _score(candidate_input.get("upside_capture_score"), 0.0)
    volatility_expansion_score = _score(
        candidate_input.get("volatility_expansion_score"), 0.0
    )
    trend_alignment_score = _score(candidate_input.get("trend_alignment_score"), 0.0)
    liquidity_score = _score(candidate_input.get("liquidity_score"), 0.0)
    spread_score = _resolve_spread_score(candidate_input)
    slippage_score = _resolve_slippage_score(candidate_input)
    drawdown_risk_score = _resolve_drawdown_risk_score(candidate_input)
    evidence_quality_score = _score(candidate_input.get("evidence_quality_score"), 0.0)
    invalidation_quality_score = _score(
        candidate_input.get("invalidation_quality_score"), 0.0
    )
    confidence_score = _score(candidate_input.get("confidence_score"), 0.0)
    sample_size = _safe_int(candidate_input.get("sample_size"), 0)
    sample_size_score = _sample_size_score(sample_size, policy)
    recent_win_rate = _score(candidate_input.get("recent_win_rate"), 0.0)
    max_drawdown_percent = _optional_float(candidate_input.get("max_drawdown_percent"))
    spread_pips = _optional_float(candidate_input.get("spread_pips"))
    slippage_pips = _optional_float(candidate_input.get("slippage_pips"))
    risk_percent = _safe_float(
        candidate_input.get("risk_percent"),
        float(policy["max_risk_percent"]),
    )
    stop_loss_defined = _truthy(candidate_input.get("stop_loss_defined"))
    take_profit_defined = _truthy(candidate_input.get("take_profit_defined"))
    invalidation_defined = _truthy(candidate_input.get("invalidation_defined"))

    asymmetric_payoff_score = _asymmetric_payoff_score(
        reward_risk_ratio,
        expected_r_multiple,
        policy,
    )
    reward_to_risk_score = _ratio_score(
        reward_risk_ratio,
        float(policy["min_reward_risk_ratio"]),
    )

    rejection_reasons = _candidate_rejection_reasons(
        candidate_input,
        pair,
        direction,
        reward_risk_ratio,
        expected_r_multiple,
        expectancy_score,
        upside_capture_score,
        volatility_expansion_score,
        liquidity_score,
        spread_score,
        slippage_score,
        drawdown_risk_score,
        evidence_quality_score,
        invalidation_quality_score,
        sample_size,
        risk_percent,
        stop_loss_defined,
        take_profit_defined,
        invalidation_defined,
        policy,
        global_blockers,
    )
    risk_flags = _candidate_risk_flags(rejection_reasons)
    big_winner_candidate = not rejection_reasons
    opportunity_score = (
        _opportunity_score(
            asymmetric_payoff_score,
            reward_to_risk_score,
            upside_capture_score,
            expectancy_score,
            volatility_expansion_score,
            trend_alignment_score,
            liquidity_score,
            spread_score,
            slippage_score,
            drawdown_risk_score,
            evidence_quality_score,
            invalidation_quality_score,
            sample_size_score,
        )
        if big_winner_candidate
        else 0.0
    )

    return {
        "rank": 0,
        "input_index": index,
        "pair": pair,
        "direction": direction,
        "setup_type": _normalize_text(candidate_input.get("setup_type")),
        "market_session": _normalize_text(candidate_input.get("market_session")),
        "catalyst": _normalize_text(candidate_input.get("catalyst")),
        "big_winner_candidate": big_winner_candidate,
        "opportunity_score": opportunity_score,
        "asymmetric_payoff_score": asymmetric_payoff_score,
        "reward_to_risk_score": reward_to_risk_score,
        "reward_risk_ratio": _round_float(reward_risk_ratio),
        "expected_r_multiple": _round_float(expected_r_multiple),
        "upside_capture_score": upside_capture_score,
        "expectancy_score": expectancy_score,
        "volatility_expansion_score": volatility_expansion_score,
        "trend_alignment_score": trend_alignment_score,
        "liquidity_score": liquidity_score,
        "spread_score": spread_score,
        "slippage_score": slippage_score,
        "drawdown_risk_score": drawdown_risk_score,
        "evidence_quality_score": evidence_quality_score,
        "invalidation_quality_score": invalidation_quality_score,
        "sample_size_score": sample_size_score,
        "confidence_score": confidence_score,
        "sample_size": sample_size,
        "recent_win_rate": recent_win_rate,
        "max_drawdown_percent": _round_optional(max_drawdown_percent),
        "spread_pips": _round_optional(spread_pips),
        "slippage_pips": _round_optional(slippage_pips),
        "risk_percent": _round_float(risk_percent),
        "stop_loss_defined": stop_loss_defined,
        "take_profit_defined": take_profit_defined,
        "invalidation_defined": invalidation_defined,
        "owner_approved_for_paper": _truthy(
            candidate_input.get("owner_approved_for_paper")
        ),
        "review_only": True,
        "paper_only": True,
        "execution_allowed": False,
        "owner_decision_required": True,
        "risk_flags": risk_flags,
        "rejection_reasons": rejection_reasons,
        "reason_summary": _reason_summary(pair, direction, opportunity_score),
        "safe_next_action": _candidate_safe_next_action(rejection_reasons),
    }


def _candidate_rejection_reasons(
    candidate_input: Mapping[str, Any],
    pair: str,
    direction: str,
    reward_risk_ratio: float,
    expected_r_multiple: float,
    expectancy_score: float,
    upside_capture_score: float,
    volatility_expansion_score: float,
    liquidity_score: float,
    spread_score: float,
    slippage_score: float,
    drawdown_risk_score: float,
    evidence_quality_score: float,
    invalidation_quality_score: float,
    sample_size: int,
    risk_percent: float,
    stop_loss_defined: bool,
    take_profit_defined: bool,
    invalidation_defined: bool,
    policy: Mapping[str, Any],
    global_blockers: Sequence[str],
) -> list[str]:
    reasons = list(global_blockers)
    if not pair:
        reasons.append("missing_pair")
    if not direction:
        reasons.append("missing_direction")
    if not stop_loss_defined:
        reasons.append("missing_stop_loss")
    if not take_profit_defined:
        reasons.append("missing_take_profit")
    if not invalidation_defined:
        reasons.append("missing_invalidation")
    if sample_size < int(policy["min_sample_size"]):
        reasons.append("insufficient_sample_size")
    if (
        reward_risk_ratio < float(policy["min_reward_risk_ratio"])
        and expected_r_multiple < float(policy["min_expected_r_multiple"])
    ):
        reasons.append("reward_risk_too_low")
    if expectancy_score < float(policy["min_expectancy_score"]):
        reasons.append("expectancy_too_low")
    if upside_capture_score < float(policy["min_upside_capture_score"]):
        reasons.append("upside_capture_too_low")
    if volatility_expansion_score < float(policy["min_volatility_expansion_score"]):
        reasons.append("volatility_expansion_too_low")
    if evidence_quality_score < float(policy["min_evidence_quality_score"]):
        reasons.append("evidence_quality_too_low")
    if liquidity_score < float(policy["min_liquidity_score"]):
        reasons.append("liquidity_too_low")
    if spread_score < float(policy["min_spread_score"]):
        reasons.append("spread_too_wide")
    if slippage_score < float(policy["min_slippage_score"]):
        reasons.append("slippage_risk_too_high")
    if drawdown_risk_score < float(policy["min_drawdown_risk_score"]):
        reasons.append("drawdown_risk_too_high")
    if invalidation_quality_score < float(policy["min_invalidation_quality_score"]):
        reasons.append("invalidation_quality_too_low")
    if risk_percent > float(policy["max_risk_percent"]):
        reasons.append("risk_percent_above_cap")
    if _martingale_detected(candidate_input):
        reasons.append("martingale_detected")
    if _revenge_trade_detected(candidate_input):
        reasons.append("revenge_trade_detected")
    reasons.extend(_candidate_boundary_blockers(candidate_input))
    return _unique(reasons)


def _rejected_candidate(
    index: int,
    rejection_reasons: Sequence[str],
    risk_flags: Sequence[str],
) -> dict[str, Any]:
    return {
        "rank": 0,
        "input_index": index,
        "pair": "",
        "direction": "",
        "setup_type": "",
        "market_session": "",
        "catalyst": "",
        "big_winner_candidate": False,
        "opportunity_score": 0.0,
        "asymmetric_payoff_score": 0.0,
        "reward_to_risk_score": 0.0,
        "reward_risk_ratio": 0.0,
        "expected_r_multiple": 0.0,
        "upside_capture_score": 0.0,
        "expectancy_score": 0.0,
        "volatility_expansion_score": 0.0,
        "trend_alignment_score": 0.0,
        "liquidity_score": 0.0,
        "spread_score": 0.0,
        "slippage_score": 0.0,
        "drawdown_risk_score": 0.0,
        "evidence_quality_score": 0.0,
        "invalidation_quality_score": 0.0,
        "sample_size_score": 0.0,
        "confidence_score": 0.0,
        "sample_size": 0,
        "recent_win_rate": 0.0,
        "max_drawdown_percent": None,
        "spread_pips": None,
        "slippage_pips": None,
        "risk_percent": 0.0,
        "stop_loss_defined": False,
        "take_profit_defined": False,
        "invalidation_defined": False,
        "owner_approved_for_paper": False,
        "review_only": True,
        "paper_only": True,
        "execution_allowed": False,
        "owner_decision_required": True,
        "risk_flags": list(risk_flags),
        "rejection_reasons": list(rejection_reasons),
        "reason_summary": "Candidate payload rejected before scoring.",
        "safe_next_action": "Repair candidate payload and rerun read-only scan.",
    }


def _normalize_policy(raw_policy: Any) -> dict[str, Any]:
    source = raw_policy if isinstance(raw_policy, Mapping) else {}
    policy: dict[str, Any] = {}
    for key, default in DEFAULT_POLICY.items():
        if key == "min_sample_size":
            policy[key] = _positive_int(source.get(key), int(default))
        else:
            policy[key] = _positive_float(source.get(key), float(default))
    return policy


def _candidate_sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _global_boundary_blockers(payload: Mapping[str, Any]) -> list[str]:
    return _boundary_blockers(payload, skip_candidate_list=True)


def _candidate_boundary_blockers(payload: Mapping[str, Any]) -> list[str]:
    return _boundary_blockers(payload, skip_candidate_list=False)


def _boundary_blockers(
    payload: Mapping[str, Any],
    *,
    skip_candidate_list: bool,
) -> list[str]:
    blockers = []
    if _truthy_any(payload, ("request_live_execution", "live_execution_requested")):
        blockers.append("live_execution_requested")
    if _truthy_any(payload, ("request_broker_api", "broker_api_requested")):
        blockers.append("broker_api_requested")
    if _truthy_any(payload, ("request_auto_entry", "auto_entry_requested")):
        blockers.append("auto_entry_requested")
    if _truthy_any(
        payload,
        ("request_leverage_escalation", "leverage_escalation_requested"),
    ):
        blockers.append("leverage_escalation_requested")
    if _contains_sensitive_key(payload, skip_candidate_list=skip_candidate_list):
        blockers.append("credential_or_secret_supplied")
    return blockers


def _candidate_risk_flags(rejection_reasons: Sequence[str]) -> list[str]:
    flags = ["owner_decision_required", "read_only_review_only"]
    flags.extend(reason for reason in rejection_reasons if reason in UNSAFE_BLOCKERS)
    return _unique(flags)


def _contains_sensitive_key(value: Any, *, skip_candidate_list: bool) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if any(part in key_text for part in SENSITIVE_KEY_PARTS):
                return True
            if skip_candidate_list and key_text == "candidates":
                continue
            if _contains_sensitive_key(item, skip_candidate_list=skip_candidate_list):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(
            _contains_sensitive_key(item, skip_candidate_list=skip_candidate_list)
            for item in value
        )
    return False


def _martingale_detected(candidate_input: Mapping[str, Any]) -> bool:
    if _truthy_any(candidate_input, ("is_martingale", "martingale")):
        return True
    text = " ".join(
        _normalize_text(candidate_input.get(field))
        for field in ("setup_type", "catalyst", "strategy", "sizing_model")
    ).lower()
    return any(token in text for token in ("martingale", "grid", "averaging down"))


def _revenge_trade_detected(candidate_input: Mapping[str, Any]) -> bool:
    if _truthy_any(candidate_input, ("is_revenge", "revenge_trade", "is_revenge_trade")):
        return True
    text = " ".join(
        _normalize_text(candidate_input.get(field))
        for field in ("setup_type", "catalyst", "strategy", "trade_reason", "sizing_model")
    ).lower()
    return "revenge" in text


def _resolve_spread_score(candidate_input: Mapping[str, Any]) -> float:
    explicit = _optional_float(candidate_input.get("spread_score"))
    if explicit is not None:
        return _score(explicit, 0.0)
    spread_pips = _optional_float(candidate_input.get("spread_pips"))
    if spread_pips is None:
        return 0.0
    if spread_pips <= 0:
        return 100.0
    return _clamp(100.0 - (spread_pips * 20.0), 0.0, 100.0)


def _resolve_slippage_score(candidate_input: Mapping[str, Any]) -> float:
    explicit = _optional_float(candidate_input.get("slippage_score"))
    if explicit is not None:
        return _score(explicit, 0.0)
    slippage_pips = _optional_float(candidate_input.get("slippage_pips"))
    if slippage_pips is None:
        return 0.0
    if slippage_pips <= 0:
        return 100.0
    return _clamp(100.0 - (slippage_pips * 25.0), 0.0, 100.0)


def _resolve_drawdown_risk_score(candidate_input: Mapping[str, Any]) -> float:
    explicit = _optional_float(candidate_input.get("drawdown_risk_score"))
    if explicit is not None:
        return _score(explicit, 0.0)
    max_drawdown_percent = _optional_float(candidate_input.get("max_drawdown_percent"))
    if max_drawdown_percent is None:
        return 0.0
    if max_drawdown_percent <= 0:
        return 100.0
    return _clamp(100.0 - (max_drawdown_percent * 4.0), 0.0, 100.0)


def _asymmetric_payoff_score(
    reward_risk_ratio: float,
    expected_r_multiple: float,
    policy: Mapping[str, Any],
) -> float:
    expected_score = _ratio_score(
        expected_r_multiple,
        float(policy["min_expected_r_multiple"]),
    )
    reward_score = _ratio_score(
        reward_risk_ratio,
        float(policy["min_reward_risk_ratio"]),
    )
    return _round_float(max(expected_score, reward_score))


def _ratio_score(value: float, minimum: float) -> float:
    if value <= 0 or minimum <= 0:
        return 0.0
    return _clamp((value / minimum) * 100.0, 0.0, 100.0)


def _sample_size_score(sample_size: int, policy: Mapping[str, Any]) -> float:
    target = int(policy["min_sample_size"])
    if sample_size <= 0 or target <= 0:
        return 0.0
    return _clamp((sample_size / target) * 100.0, 0.0, 100.0)


def _opportunity_score(
    asymmetric_payoff_score: float,
    reward_to_risk_score: float,
    upside_capture_score: float,
    expectancy_score: float,
    volatility_expansion_score: float,
    trend_alignment_score: float,
    liquidity_score: float,
    spread_score: float,
    slippage_score: float,
    drawdown_risk_score: float,
    evidence_quality_score: float,
    invalidation_quality_score: float,
    sample_size_score: float,
) -> float:
    value = (
        asymmetric_payoff_score * SCORE_WEIGHTS["asymmetric_payoff"]
        + reward_to_risk_score * SCORE_WEIGHTS["reward_to_risk"]
        + upside_capture_score * SCORE_WEIGHTS["upside_capture"]
        + expectancy_score * SCORE_WEIGHTS["expectancy"]
        + volatility_expansion_score * SCORE_WEIGHTS["volatility_expansion"]
        + trend_alignment_score * SCORE_WEIGHTS["trend_alignment"]
        + liquidity_score * SCORE_WEIGHTS["liquidity"]
        + spread_score * SCORE_WEIGHTS["spread"]
        + slippage_score * SCORE_WEIGHTS["slippage"]
        + drawdown_risk_score * SCORE_WEIGHTS["drawdown_risk"]
        + evidence_quality_score * SCORE_WEIGHTS["evidence_quality"]
        + invalidation_quality_score * SCORE_WEIGHTS["invalidation_quality"]
        + sample_size_score * SCORE_WEIGHTS["sample_size"]
    )
    return _round_float(value)


def _alert_for_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "pair": candidate["pair"],
        "direction": candidate["direction"],
        "alert_type": "ASYMMETRIC_BIG_WINNER_CANDIDATE",
        "review_only": True,
        "paper_only": True,
        "owner_decision_required": True,
        "execution_allowed": False,
        "reason_summary": candidate["reason_summary"],
        "safe_next_action": (
            "Review top asymmetric big-winner candidate in paper/simulation only; "
            "no live execution without owner gate."
        ),
    }


def _alert_level(
    unsafe_detected: bool,
    top_qualifies: bool,
    candidate_count: int,
    rejected_count: int,
) -> str:
    if unsafe_detected:
        return "BLOCKED_UNSAFE_REQUEST"
    if top_qualifies:
        return "BIG_WINNER_REVIEW"
    if candidate_count == 0 or rejected_count == candidate_count:
        return "NO_VALID_CANDIDATES"
    return "WATCHLIST_ONLY"


def _safe_next_action(unsafe_detected: bool, top_qualifies: bool) -> str:
    if unsafe_detected:
        return (
            "Unsafe request blocked. Remove live/broker/auto-entry/leverage/"
            "credential/revenge/martingale fields and rerun read-only scan."
        )
    if top_qualifies:
        return (
            "Review top asymmetric big-winner candidate in paper/simulation only; "
            "no live execution without owner gate."
        )
    return "No qualified asymmetric big-winner candidate. Continue read-only 22h/6d scan."


def _candidate_safe_next_action(rejection_reasons: Sequence[str]) -> str:
    if any(reason in UNSAFE_BLOCKERS for reason in rejection_reasons):
        return (
            "Unsafe request blocked. Remove live/broker/auto-entry/leverage/"
            "credential/revenge/martingale fields and rerun read-only scan."
        )
    if rejection_reasons:
        return "Repair rejected candidate blockers and rerun read-only scan."
    return (
        "Review top asymmetric big-winner candidate in paper/simulation only; "
        "no live execution without owner gate."
    )


def _reason_summary(pair: str, direction: str, opportunity_score: float) -> str:
    if not pair:
        return "Candidate lacks required pair identity."
    if opportunity_score <= 0:
        return f"{pair} {direction} did not clear all capped-downside review gates."
    return (
        f"{pair} {direction} qualifies with opportunity_score "
        f"{_round_float(opportunity_score)} and capped downside controls."
    )


def _safety_boundary() -> dict[str, bool]:
    return {
        "read_only": True,
        "paper_only": True,
        "live_trading_allowed": False,
        "broker_api_allowed": False,
        "auto_entry_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "leverage_escalation_allowed": False,
        "martingale_allowed": False,
        "revenge_trading_allowed": False,
        "all_in_allocation_allowed": False,
        "credential_use_allowed": False,
        "owner_gate_required": True,
    }


def _truthy_any(payload: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return any(_truthy(payload.get(key)) for key in keys)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return False


def _score(value: Any, default: float) -> float:
    return _clamp(_safe_float(value, default), 0.0, 100.0)


def _safe_float(value: Any, default: float) -> float:
    number = _optional_float(value)
    if number is None:
        return float(default)
    return number


def _positive_float(value: Any, default: float) -> float:
    number = _optional_float(value)
    if number is None or number <= 0:
        return float(default)
    return _round_float(number)


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def _safe_int(value: Any, default: int) -> int:
    if isinstance(value, bool) or value in (None, ""):
        return int(default)
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return int(default)


def _positive_int(value: Any, default: int) -> int:
    number = _safe_int(value, default)
    if number <= 0:
        return int(default)
    return number


def _normalize_pair(value: Any) -> str:
    text = _normalize_text(value).upper()
    return text.replace("/", "").replace("_", "").replace("-", "")


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _score_from_candidate(candidate: Mapping[str, Any], field_name: str) -> float:
    return _round_float(_safe_float(candidate.get(field_name), 0.0))


def _round_optional(value: float | None) -> float | None:
    if value is None:
        return None
    return _round_float(value)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return _round_float(min(maximum, max(minimum, value)))


def _round_float(value: float, digits: int = 6) -> float:
    return round(float(value), digits)


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


__all__ = [
    "MODE",
    "SCHEMA",
    "evaluate_big_winner_watchtower_22h6d_v1",
]
