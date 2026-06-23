"""AIOS Forex compounding capital bucket supervisor.

This module models governed capital-bucket compounding cycles from sanitized
in-memory dictionaries. It does not read files, read environment variables,
call brokers, place orders, persist data, or grant execution authority.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


PACKET_ID = "AIOS-FOREX-COMPOUNDING-CAPITAL-BUCKET-SUPERVISOR-V1"
SUPERVISOR_VERSION = "v1"

BUCKET_BLOCKED_MISSING_STATE = "BUCKET_BLOCKED_MISSING_STATE"
BUCKET_BLOCKED_RISK = "BUCKET_BLOCKED_RISK"
BUCKET_BLOCKED_EVIDENCE = "BUCKET_BLOCKED_EVIDENCE"
BUCKET_BLOCKED_POLICY = "BUCKET_BLOCKED_POLICY"
BUCKET_ACTIVE_ACCUMULATING = "BUCKET_ACTIVE_ACCUMULATING"
BUCKET_TARGET_REACHED_COLLECT_PROFIT = "BUCKET_TARGET_REACHED_COLLECT_PROFIT"
BUCKET_READY_FOR_REDISTRIBUTION_REVIEW = "BUCKET_READY_FOR_REDISTRIBUTION_REVIEW"
BUCKET_REJECTED = "BUCKET_REJECTED"

DEFAULT_TARGET_MIN_RETURN_PERCENT = 100.0
DEFAULT_TARGET_MAX_RETURN_PERCENT = 120.0
FUTURE_TARGET_RETURN_PERCENT = 150.0

BUCKET_REQUIRED_FIELDS = (
    "starting_balance",
    "current_balance",
    "realized_profit",
    "unrealized_profit",
    "active_deployed_capital",
    "reserve_capital",
    "cycle_start_balance",
    "cycle_current_equity",
    "cycle_realized_profit",
    "cycle_unrealized_profit",
    "cycle_trade_count",
    "current_return_percent",
    "total_goal_amount",
    "current_goal_progress_percent",
)

POLICY_REQUIRED_FIELDS = (
    "compounding_enabled",
    "collect_when_target_reached",
    "redistribute_after_collection",
    "max_pairs_per_cycle",
    "min_pair_quality_score",
    "equal_weight_allowed",
    "risk_weighted_allowed",
    "scale_invariant_logic_required",
    "allow_future_150_percent_target",
    "force_trades_to_hit_quota",
)

RISK_REQUIRED_TRUE_FIELDS = (
    "risk_gate_passed",
    "kill_switch_ready",
    "daily_stop_ready",
    "max_loss_gate_ready",
    "margin_safe",
    "no_averaging_down",
    "one_cycle_at_a_time",
)

RISK_REQUIRED_NUMERIC_FIELDS = (
    "max_total_bucket_risk_percent",
    "max_pair_risk_percent",
)

EVIDENCE_REQUIRED_TRUE_FIELDS = (
    "evidence_capture_ready",
    "trade_outcome_tracking_ready",
    "profit_collection_tracking_ready",
    "redistribution_tracking_ready",
    "sanitized_money_state_ready",
    "no_profit_guarantee_acknowledged",
)

PAIR_FIELDS = (
    "instrument",
    "direction_bias",
    "quality_score",
    "spread_ok",
    "margin_required",
    "max_position_size_units",
    "expected_reward_risk",
    "eligible_for_allocation",
    "blocked_reason",
)

EXECUTION_AUTHORITY_KEYS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)


def evaluate_compounding_capital_bucket_supervisor_v1(
    bucket_state: dict | None = None,
    pair_candidates: list[dict] | None = None,
    cycle_policy: dict | None = None,
    risk_state: dict | None = None,
    evidence_state: dict | None = None,
) -> dict:
    """Evaluate a governed capital-bucket compounding cycle."""

    bucket = _mapping(bucket_state)
    pairs = _pairs(pair_candidates)
    policy = _mapping(cycle_policy)
    risk = _mapping(risk_state)
    evidence = _mapping(evidence_state)

    if not bucket:
        return _result(
            status=BUCKET_BLOCKED_MISSING_STATE,
            blockers=["missing_bucket_state"],
            warnings=_base_warnings(),
            bucket=bucket,
            pairs=pairs,
            policy=policy,
            risk=risk,
            evidence=evidence,
            selected_pairs=[],
            excluded_pairs=[],
        )

    unsafe_blockers = _unsafe_authority_blockers(bucket, policy, risk, evidence)
    bucket_blockers = _bucket_blockers(bucket)
    policy_blockers = _policy_blockers(policy, bucket)
    risk_blockers = _risk_blockers(risk)
    evidence_blockers = _evidence_blockers(evidence)

    selected_pairs, excluded_pairs = _select_pairs(bucket, pairs, policy, risk)

    blockers = _unique(unsafe_blockers + bucket_blockers + policy_blockers + risk_blockers + evidence_blockers)
    warnings = _warnings(bucket, policy, selected_pairs, pairs)

    if unsafe_blockers:
        status = BUCKET_REJECTED
    elif bucket_blockers:
        status = BUCKET_BLOCKED_MISSING_STATE
    elif policy_blockers:
        status = BUCKET_BLOCKED_POLICY
    elif risk_blockers:
        status = BUCKET_BLOCKED_RISK
    elif evidence_blockers:
        status = BUCKET_BLOCKED_EVIDENCE
    else:
        status = _ready_status(bucket, policy)

    return _result(
        status=status,
        blockers=blockers,
        warnings=warnings,
        bucket=bucket,
        pairs=pairs,
        policy=policy,
        risk=risk,
        evidence=evidence,
        selected_pairs=selected_pairs,
        excluded_pairs=excluded_pairs,
    )


def _ready_status(bucket: Mapping[str, Any], policy: Mapping[str, Any]) -> str:
    current_return = _number(bucket.get("current_return_percent"), default=0.0)
    target_min = _target_min(bucket)
    target_max = _target_max(bucket, policy)

    if _bool(bucket.get("profit_collected_for_cycle")) and _bool(policy.get("redistribute_after_collection")):
        return BUCKET_READY_FOR_REDISTRIBUTION_REVIEW
    if current_return >= target_min:
        return BUCKET_TARGET_REACHED_COLLECT_PROFIT
    if current_return < target_min:
        return BUCKET_ACTIVE_ACCUMULATING
    if current_return > target_max:
        return BUCKET_TARGET_REACHED_COLLECT_PROFIT
    return BUCKET_ACTIVE_ACCUMULATING


def _bucket_blockers(bucket: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in BUCKET_REQUIRED_FIELDS:
        if not _present(bucket.get(field)):
            blockers.append(f"missing_{field}")
        elif _number(bucket.get(field)) is None:
            blockers.append(f"{field}_not_numeric")

    if _number(bucket.get("starting_balance"), default=0.0) <= 0:
        blockers.append("starting_balance_not_positive")
    if _number(bucket.get("cycle_start_balance"), default=0.0) <= 0:
        blockers.append("cycle_start_balance_not_positive")
    if _number(bucket.get("total_goal_amount"), default=0.0) <= 0:
        blockers.append("total_goal_amount_not_positive")
    return _unique(blockers)


def _policy_blockers(policy: Mapping[str, Any], bucket: Mapping[str, Any]) -> list[str]:
    if not policy:
        return ["missing_cycle_policy"]

    blockers: list[str] = []
    for field in POLICY_REQUIRED_FIELDS:
        if field not in policy:
            blockers.append(f"missing_{field}")

    if not _bool(policy.get("compounding_enabled")):
        blockers.append("compounding_not_enabled")
    if not _bool(policy.get("collect_when_target_reached")):
        blockers.append("collect_when_target_reached_not_enabled")
    if not _bool(policy.get("redistribute_after_collection")):
        blockers.append("redistribute_after_collection_not_enabled")
    if not _bool(policy.get("scale_invariant_logic_required")):
        blockers.append("scale_invariant_logic_not_required")
    if _bool(policy.get("force_trades_to_hit_quota")):
        blockers.append("force_trades_to_hit_quota_must_be_false")
    if not (_bool(policy.get("equal_weight_allowed")) or _bool(policy.get("risk_weighted_allowed"))):
        blockers.append("no_allocation_weighting_method_allowed")

    max_pairs = _integer(policy.get("max_pairs_per_cycle"))
    if max_pairs is None or max_pairs <= 0:
        blockers.append("max_pairs_per_cycle_not_positive")

    min_quality = _number(policy.get("min_pair_quality_score"))
    if min_quality is None or min_quality < 0:
        blockers.append("min_pair_quality_score_invalid")

    future_target = _future_target(policy, bucket)
    if future_target == FUTURE_TARGET_RETURN_PERCENT and not _bool(policy.get("allow_future_150_percent_target")):
        blockers.append("future_150_percent_target_not_allowed")

    return _unique(blockers)


def _risk_blockers(risk: Mapping[str, Any]) -> list[str]:
    if not risk:
        return ["missing_risk_state"]

    blockers: list[str] = []
    for field in RISK_REQUIRED_TRUE_FIELDS:
        if not _bool(risk.get(field)):
            blockers.append(f"{field}_not_ready")
    for field in RISK_REQUIRED_NUMERIC_FIELDS:
        value = _number(risk.get(field))
        if value is None or value <= 0:
            blockers.append(f"{field}_not_positive")
    return _unique(blockers)


def _evidence_blockers(evidence: Mapping[str, Any]) -> list[str]:
    if not evidence:
        return ["missing_evidence_state"]

    return [f"{field}_not_ready" for field in EVIDENCE_REQUIRED_TRUE_FIELDS if not _bool(evidence.get(field))]


def _select_pairs(
    bucket: Mapping[str, Any],
    pairs: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
    risk: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    reserve = _number(bucket.get("reserve_capital"), default=0.0)
    max_pairs = _integer(policy.get("max_pairs_per_cycle"), default=0) or 0
    min_quality = _number(policy.get("min_pair_quality_score"), default=0.0)
    max_pair_risk_percent = _number(risk.get("max_pair_risk_percent"), default=0.0)

    for pair in pairs:
        normalized = _pair_summary(pair)
        reason = _pair_exclusion_reason(pair, reserve, min_quality)
        if reason:
            normalized["excluded_reason"] = reason
            excluded.append(normalized)
            continue
        if len(selected) >= max_pairs:
            normalized["excluded_reason"] = "max_pairs_per_cycle_reached"
            excluded.append(normalized)
            continue
        allocation = _pair_allocation(bucket, pair, max_pair_risk_percent)
        selected.append(normalized | allocation)

    return selected, excluded


def _pair_exclusion_reason(pair: Mapping[str, Any], reserve: float, min_quality: float | None) -> str:
    if not _bool(pair.get("eligible_for_allocation")):
        return _text(pair.get("blocked_reason"), "pair_not_eligible")
    quality = _number(pair.get("quality_score"))
    if quality is None or quality < (min_quality or 0.0):
        return "quality_below_minimum"
    if not _bool(pair.get("spread_ok")):
        return "spread_blocked"
    margin_required = _number(pair.get("margin_required"))
    if margin_required is None or margin_required > reserve:
        return "margin_unaffordable"
    return ""


def _pair_allocation(
    bucket: Mapping[str, Any],
    pair: Mapping[str, Any],
    max_pair_risk_percent: float | None,
) -> dict[str, Any]:
    current_balance = _number(bucket.get("current_balance"), default=0.0)
    risk_percent = max_pair_risk_percent or 0.0
    risk_budget = current_balance * (risk_percent / 100.0)
    return {
        "allocation_basis": "percentage_risk_budget",
        "risk_budget_amount": _round(risk_budget),
        "max_position_size_units": _number(pair.get("max_position_size_units")),
    }


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    bucket: Mapping[str, Any],
    pairs: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
    risk: Mapping[str, Any],
    evidence: Mapping[str, Any],
    selected_pairs: list[dict[str, Any]],
    excluded_pairs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "supervisor_version": SUPERVISOR_VERSION,
        "status": status,
        "blockers": _unique(blockers),
        "warnings": _unique(warnings),
        "bucket_summary": _bucket_summary(bucket),
        "cycle_summary": _cycle_summary(bucket, policy),
        "allocation_plan": _allocation_plan(selected_pairs, excluded_pairs, policy),
        "collection_plan": _collection_plan(status, bucket, policy),
        "redistribution_plan": _redistribution_plan(status, selected_pairs, excluded_pairs, policy),
        "progress_gauges": _progress_gauges(bucket, policy, status),
        "risk_summary": _risk_summary(risk),
        "evidence_summary": _evidence_summary(evidence),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _bucket_summary(bucket: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "starting_balance": _number(bucket.get("starting_balance")),
        "current_balance": _number(bucket.get("current_balance")),
        "realized_profit": _number(bucket.get("realized_profit")),
        "unrealized_profit": _number(bucket.get("unrealized_profit")),
        "active_deployed_capital": _number(bucket.get("active_deployed_capital")),
        "reserve_capital": _number(bucket.get("reserve_capital")),
        "scale_invariant": True,
        "profit_guaranteed": False,
    }


def _cycle_summary(bucket: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cycle_start_balance": _number(bucket.get("cycle_start_balance")),
        "cycle_current_equity": _number(bucket.get("cycle_current_equity")),
        "cycle_realized_profit": _number(bucket.get("cycle_realized_profit")),
        "cycle_unrealized_profit": _number(bucket.get("cycle_unrealized_profit")),
        "cycle_trade_count": _integer(bucket.get("cycle_trade_count")),
        "current_return_percent": _number(bucket.get("current_return_percent")),
        "target_return_min_percent": _target_min(bucket),
        "target_return_max_percent": _target_max(bucket, policy),
        "target_is_campaign_quota_not_promise": True,
        "force_trades_to_hit_quota": _bool(policy.get("force_trades_to_hit_quota")),
    }


def _allocation_plan(
    selected_pairs: list[dict[str, Any]],
    excluded_pairs: list[dict[str, Any]],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "allocation_allowed": bool(selected_pairs),
        "allocation_method": "risk_weighted" if _bool(policy.get("risk_weighted_allowed")) else "equal_weight",
        "selected_pair_count": len(selected_pairs),
        "selected_pairs": selected_pairs,
        "excluded_pairs": excluded_pairs,
        "max_pairs_per_cycle": _integer(policy.get("max_pairs_per_cycle")),
        "forced_quota_chasing_blocked": True,
    }


def _collection_plan(status: str, bucket: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    ready_to_collect = status in {BUCKET_TARGET_REACHED_COLLECT_PROFIT, BUCKET_READY_FOR_REDISTRIBUTION_REVIEW}
    return {
        "collect_profit_ready": ready_to_collect,
        "collect_when_target_reached": _bool(policy.get("collect_when_target_reached")),
        "realized_profit": _number(bucket.get("cycle_realized_profit")),
        "unrealized_profit": _number(bucket.get("cycle_unrealized_profit")),
        "new_bucket_after_collection": _new_bucket_after_collection(bucket),
        "profit_guaranteed": False,
    }


def _redistribution_plan(
    status: str,
    selected_pairs: list[dict[str, Any]],
    excluded_pairs: list[dict[str, Any]],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "ready_for_redistribution_review": status == BUCKET_READY_FOR_REDISTRIBUTION_REVIEW,
        "redistribute_after_collection": _bool(policy.get("redistribute_after_collection")),
        "candidate_pairs_for_next_cycle": selected_pairs,
        "excluded_pairs": excluded_pairs,
        "max_pairs_per_cycle": _integer(policy.get("max_pairs_per_cycle")),
        "same_percentage_logic_for_all_bucket_sizes": True,
    }


def _progress_gauges(bucket: Mapping[str, Any], policy: Mapping[str, Any], status: str) -> dict[str, Any]:
    current_return = _number(bucket.get("current_return_percent"), default=0.0)
    target_min = _target_min(bucket)
    target_max = _target_max(bucket, policy)
    current_balance = _number(bucket.get("current_balance"), default=0.0)
    total_goal = _number(bucket.get("total_goal_amount"), default=100000.0)
    goal_progress = _number(bucket.get("current_goal_progress_percent"))
    if goal_progress is None and total_goal > 0:
        goal_progress = (current_balance / total_goal) * 100.0

    return {
        "return_cycle_gauge": {
            "gauge_id": "forex_return_100_120_progress",
            "current_return_percent": current_return,
            "target_min_return_percent": target_min,
            "target_max_return_percent": target_max,
            "progress_percent_to_min_target": _progress(current_return, target_min),
            "progress_percent_to_max_target": _progress(current_return, target_max),
            "state": _gauge_state(status, current_return, target_min, target_max),
            "visual_intent": "execution_grade_animated_3d_profit_gauge",
        },
        "total_goal_gauge": {
            "gauge_id": "account_goal_100k_progress",
            "current_balance": current_balance,
            "total_goal_amount": total_goal,
            "current_goal_progress_percent": _round(goal_progress or 0.0),
            "state": "blocked" if status.startswith("BUCKET_BLOCKED") else "tracking",
            "visual_intent": "execution_grade_animated_3d_capital_gauge",
        },
    }


def _risk_summary(risk: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "risk_gate_passed": _bool(risk.get("risk_gate_passed")),
        "kill_switch_ready": _bool(risk.get("kill_switch_ready")),
        "daily_stop_ready": _bool(risk.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(risk.get("max_loss_gate_ready")),
        "max_total_bucket_risk_percent": _number(risk.get("max_total_bucket_risk_percent")),
        "max_pair_risk_percent": _number(risk.get("max_pair_risk_percent")),
        "margin_safe": _bool(risk.get("margin_safe")),
        "no_averaging_down": _bool(risk.get("no_averaging_down")),
        "one_cycle_at_a_time": _bool(risk.get("one_cycle_at_a_time")),
    }


def _evidence_summary(evidence: Mapping[str, Any]) -> dict[str, bool]:
    return {field: _bool(evidence.get(field)) for field in EVIDENCE_REQUIRED_TRUE_FIELDS}


def _pair_summary(pair: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": _text(pair.get("instrument"), "MISSING"),
        "direction_bias": _text(pair.get("direction_bias"), "MISSING"),
        "quality_score": _number(pair.get("quality_score")),
        "spread_ok": _bool(pair.get("spread_ok")),
        "margin_required": _number(pair.get("margin_required")),
        "max_position_size_units": _number(pair.get("max_position_size_units")),
        "expected_reward_risk": _number(pair.get("expected_reward_risk")),
        "eligible_for_allocation": _bool(pair.get("eligible_for_allocation")),
        "blocked_reason": _text(pair.get("blocked_reason")),
    }


def _warnings(
    bucket: Mapping[str, Any],
    policy: Mapping[str, Any],
    selected_pairs: list[dict[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
) -> list[str]:
    warnings = _base_warnings()
    current_return = _number(bucket.get("current_return_percent"), default=0.0)
    target_max = _target_max(bucket, policy)
    if current_return > target_max:
        warnings.append("over_target_return_collect_before_redeploy")
    if not selected_pairs and pairs:
        warnings.append("no_pairs_selected_after_filters")
    if _number(bucket.get("current_return_percent"), default=0.0) < 0:
        warnings.append("negative_cycle_return_do_not_compound_blindly")
    if _future_target(policy, bucket) == FUTURE_TARGET_RETURN_PERCENT:
        warnings.append("future_150_percent_target_requires_explicit_evidence")
    return _unique(warnings)


def _base_warnings() -> list[str]:
    return [
        "target_is_campaign_quota_not_profit_promise",
        "profit_not_guaranteed",
        "execution_authority_false",
        "do_not_force_trades_to_hit_quota",
    ]


def _next_safe_action(status: str) -> str:
    return {
        BUCKET_BLOCKED_MISSING_STATE: "provide_sanitized_bucket_state_policy_risk_evidence_and_pairs",
        BUCKET_BLOCKED_RISK: "repair_risk_gates_before_allocation_review",
        BUCKET_BLOCKED_EVIDENCE: "enable_sanitized_evidence_capture_before_cycle_review",
        BUCKET_BLOCKED_POLICY: "repair_cycle_policy_before_compounding_review",
        BUCKET_ACTIVE_ACCUMULATING: "continue_observing_valid_setups_without_forcing_trades",
        BUCKET_TARGET_REACHED_COLLECT_PROFIT: "collect_profit_and_prepare_redistribution_review",
        BUCKET_READY_FOR_REDISTRIBUTION_REVIEW: "review_next_cycle_pair_redistribution_without_execution_authority",
        BUCKET_REJECTED: "remove_unsafe_execution_authority_request_before_review",
    }.get(status, "stop_and_review_bucket_supervisor_state")


def _execution_authority() -> dict[str, bool]:
    return {key: False for key in EXECUTION_AUTHORITY_KEYS}


def _unsafe_authority_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for payload in payloads:
        for key in EXECUTION_AUTHORITY_KEYS:
            if _bool(payload.get(key)):
                blockers.append(f"unsafe_{key}_true")
    return _unique(blockers)


def _new_bucket_after_collection(bucket: Mapping[str, Any]) -> float | None:
    current_balance = _number(bucket.get("current_balance"))
    unrealized = _number(bucket.get("cycle_unrealized_profit"), default=0.0)
    if current_balance is None:
        return None
    return _round(current_balance + unrealized)


def _target_min(bucket: Mapping[str, Any]) -> float:
    value = _number(bucket.get("target_return_min_percent"))
    return value if value is not None and value > 0 else DEFAULT_TARGET_MIN_RETURN_PERCENT


def _target_max(bucket: Mapping[str, Any], policy: Mapping[str, Any]) -> float:
    future = _future_target(policy, bucket)
    if future is not None and _bool(policy.get("allow_future_150_percent_target")):
        return future
    value = _number(bucket.get("target_return_max_percent"))
    return value if value is not None and value > 0 else DEFAULT_TARGET_MAX_RETURN_PERCENT


def _future_target(policy: Mapping[str, Any], bucket: Mapping[str, Any]) -> float | None:
    for value in (policy.get("future_target_return_percent"), bucket.get("future_target_return_percent")):
        target = _number(value)
        if target is not None:
            return target
    return None


def _progress(current: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return _round((current / target) * 100.0)


def _gauge_state(status: str, current: float, target_min: float, target_max: float) -> str:
    if status.startswith("BUCKET_BLOCKED") or status == BUCKET_REJECTED:
        return "blocked"
    if current > target_max:
        return "over_target_collect"
    if current >= target_min:
        return "target_reached"
    return "accumulating"


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _pairs(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ready", "passed", "pass"}
    return bool(value)


def _number(value: Any, default: float | None = None) -> float | None:
    if isinstance(value, str):
        value = value.strip().removesuffix("%")
    try:
        if value in (None, ""):
            return default
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number != number or number in (float("inf"), float("-inf")):
        return default
    return number


def _integer(value: Any, default: int | None = None) -> int | None:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value).strip()


def _present(value: Any) -> bool:
    if value in (None, "", [], {}):
        return False
    if isinstance(value, str) and value.strip().upper() in {"UNAVAILABLE", "UNKNOWN", "MISSING"}:
        return False
    return True


def _round(value: float) -> float:
    return round(value, 6)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
