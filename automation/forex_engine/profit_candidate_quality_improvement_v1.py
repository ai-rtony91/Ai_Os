"""Read-only Forex profit candidate quality improvement evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1"
MODE = "READ_ONLY_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT"

QUALITY_IMPROVEMENT_READY = "QUALITY_IMPROVEMENT_READY"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
BLOCKED_BY_EXPECTANCY = "BLOCKED_BY_EXPECTANCY"
BLOCKED_BY_PROFIT_FACTOR = "BLOCKED_BY_PROFIT_FACTOR"
BLOCKED_BY_DRAWDOWN_EFFICIENCY = "BLOCKED_BY_DRAWDOWN_EFFICIENCY"
BLOCKED_BY_REGIME_WEAKNESS = "BLOCKED_BY_REGIME_WEAKNESS"
BLOCKED_BY_MISSED_OPPORTUNITY_LEAKAGE = "BLOCKED_BY_MISSED_OPPORTUNITY_LEAKAGE"
BLOCKED_BY_FALSE_POSITIVES = "BLOCKED_BY_FALSE_POSITIVES"
BLOCKED_BY_ENTRY_EXIT_QUALITY = "BLOCKED_BY_ENTRY_EXIT_QUALITY"
BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

CURRENT_LANE_ID = "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT"
NEXT_LANE_ID = "DEMO_CANDIDATE_REVIEW_READINESS"
NEXT_PACKET_IF_READY = "AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1"
THIS_PACKET = SCHEMA

OPPORTUNITY_CAPTURE_OBJECTIVE = (
    "maximize validated risk-adjusted opportunity capture while preserving capital and proving edge"
)

DEFAULT_THRESHOLDS: dict[str, float] = {
    "min_candidate_quality_score": 0.75,
    "min_expectancy_quality_score": 0.70,
    "min_profit_factor_quality_score": 0.70,
    "min_drawdown_efficiency_score": 0.70,
    "min_regime_quality_score": 0.65,
    "max_missed_opportunity_count": 0,
    "max_false_positive_count": 0,
    "max_late_entry_count": 0,
    "max_early_exit_count": 0,
    "min_risk_adjusted_quality_score": 0.70,
    "min_data_quality_score": 0.80,
}

SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "token",
    "secret",
    "credential",
    "credentials",
    "broker_token",
    "access_token",
)

CORE_EVIDENCE_KEYS = (
    "profitability_evaluation",
    "candidate_quality_snapshot",
    "opportunity_leakage",
    "entry_exit_review",
)

CONTEXT_KEYS = (
    "evidence_sufficiency",
    "profitability_evaluation",
    "candidate_quality_snapshot",
    "walk_forward_validation",
    "regime_results",
    "opportunity_leakage",
    "entry_exit_review",
    "false_positive_review",
    "risk_review",
)


def evaluate_profit_candidate_quality_improvement_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate sanitized candidate-quality evidence without execution authority."""

    source = payload if isinstance(payload, Mapping) else {}
    threshold_policy = _threshold_policy(_mapping(source.get("thresholds")))
    thresholds = threshold_policy["active_thresholds"]

    if _contains_sensitive_key(source):
        return _sensitive_payload(source, threshold_policy)

    contexts = _quality_contexts(source)
    missing_information = _missing_information(source, contexts)
    missing_core_evidence = bool(missing_information)

    expectancy_quality = _expectancy_quality(contexts, thresholds)
    profit_factor_quality = _profit_factor_quality(contexts, thresholds)
    drawdown_efficiency = _drawdown_efficiency(contexts, thresholds)
    regime_quality = _regime_quality(contexts, thresholds)
    missed_opportunity_quality = _missed_opportunity_quality(contexts, thresholds)
    false_positive_quality = _false_positive_quality(contexts, thresholds)
    entry_exit_quality = _entry_exit_quality(contexts, thresholds)
    risk_adjusted_quality = _risk_adjusted_quality(
        contexts,
        thresholds,
        expectancy_quality,
        profit_factor_quality,
        drawdown_efficiency,
    )
    data_quality = _data_quality(contexts, thresholds)

    sub_scores = {
        "expectancy_quality_score": expectancy_quality["score"],
        "profit_factor_quality_score": profit_factor_quality["score"],
        "drawdown_efficiency_score": drawdown_efficiency["score"],
        "regime_quality_score": regime_quality["score"],
        "risk_adjusted_quality_score": risk_adjusted_quality["score"],
        "data_quality_score": data_quality["score"],
    }
    explicit_candidate_quality_score = _score_from_keys(
        contexts,
        ("candidate_quality_score", "candidate_score"),
    )
    derived_candidate_quality_score = _average_score(sub_scores.values())
    candidate_quality_score = (
        explicit_candidate_quality_score
        if explicit_candidate_quality_score is not None
        else derived_candidate_quality_score
    )

    blocker_summary = _blocker_summary(
        candidate_blockers=_candidate_blockers(candidate_quality_score, thresholds),
        expectancy_blockers=expectancy_quality["blockers"],
        profit_factor_blockers=profit_factor_quality["blockers"],
        drawdown_blockers=drawdown_efficiency["blockers"],
        regime_blockers=regime_quality["blockers"],
        missed_opportunity_blockers=missed_opportunity_quality["blockers"],
        false_positive_blockers=false_positive_quality["blockers"],
        entry_exit_blockers=entry_exit_quality["blockers"],
        risk_adjusted_blockers=risk_adjusted_quality["blockers"],
        data_quality_blockers=data_quality["blockers"],
        threshold_blockers=threshold_policy["threshold_blockers"],
    )

    quality_status = _resolve_quality_status(
        missing_core_evidence=missing_core_evidence,
        expectancy_quality=expectancy_quality,
        profit_factor_quality=profit_factor_quality,
        drawdown_efficiency=drawdown_efficiency,
        regime_quality=regime_quality,
        missed_opportunity_quality=missed_opportunity_quality,
        false_positive_quality=false_positive_quality,
        entry_exit_quality=entry_exit_quality,
        risk_adjusted_quality=risk_adjusted_quality,
        data_quality=data_quality,
        candidate_quality_score=candidate_quality_score,
        thresholds=thresholds,
    )
    next_best_packet = NEXT_PACKET_IF_READY if quality_status == QUALITY_IMPROVEMENT_READY else THIS_PACKET
    improvement_actions = _improvement_actions(blocker_summary, next_best_packet)

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_decision_required": True,
        "quality_status": quality_status,
        "candidate_quality_score": candidate_quality_score,
        "improvement_priority": _improvement_priority(quality_status, blocker_summary),
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "input_summary": _input_summary(
            source,
            explicit_candidate_quality_score,
            derived_candidate_quality_score,
            sub_scores,
        ),
        "threshold_policy": threshold_policy,
        "expectancy_quality": expectancy_quality,
        "profit_factor_quality": profit_factor_quality,
        "drawdown_efficiency": drawdown_efficiency,
        "regime_quality": regime_quality,
        "missed_opportunity_quality": missed_opportunity_quality,
        "false_positive_quality": false_positive_quality,
        "entry_exit_quality": entry_exit_quality,
        "risk_adjusted_quality": risk_adjusted_quality,
        "data_quality": data_quality,
        "promotion_readiness": _promotion_readiness(quality_status, blocker_summary, missing_information),
        "improvement_actions": improvement_actions,
        "blocker_summary": blocker_summary,
        "missing_information": missing_information,
        "owner_action_queue": improvement_actions,
        "next_best_packet": next_best_packet,
        "next_remaining_lane": _next_remaining_lane(_mapping(source.get("remaining_work_closure_index"))),
        "safe_manual_next_action": _safe_manual_next_action(quality_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "quality_status": quality_status,
            "candidate_quality_score": candidate_quality_score,
            "next_best_packet": next_best_packet,
            "read_only": True,
        },
        "safety": _safety(),
    }


def _sensitive_payload(source: Mapping[str, Any], threshold_policy: Mapping[str, Any]) -> dict[str, Any]:
    blocker_summary = _blocker_summary(
        candidate_blockers=[],
        expectancy_blockers=["sensitive_data_provided"],
        profit_factor_blockers=["sensitive_data_provided"],
        drawdown_blockers=["sensitive_data_provided"],
        regime_blockers=["sensitive_data_provided"],
        missed_opportunity_blockers=["sensitive_data_provided"],
        false_positive_blockers=["sensitive_data_provided"],
        entry_exit_blockers=["sensitive_data_provided"],
        risk_adjusted_blockers=["sensitive_data_provided"],
        data_quality_blockers=["sensitive_data_provided"],
        threshold_blockers=list(threshold_policy.get("threshold_blockers", [])),
    )
    next_best_packet = THIS_PACKET
    improvement_actions = _improvement_actions(blocker_summary, next_best_packet)
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_decision_required": True,
        "quality_status": BLOCKED_BY_DATA_QUALITY,
        "candidate_quality_score": None,
        "improvement_priority": _improvement_priority(BLOCKED_BY_DATA_QUALITY, blocker_summary),
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "input_summary": {
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "input_redacted": True,
            "meaningful_evidence_present": False,
        },
        "threshold_policy": dict(threshold_policy),
        "expectancy_quality": _empty_quality_summary("expectancy_quality", ["sensitive_data_provided"]),
        "profit_factor_quality": _empty_quality_summary("profit_factor_quality", ["sensitive_data_provided"]),
        "drawdown_efficiency": _empty_quality_summary("drawdown_efficiency", ["sensitive_data_provided"]),
        "regime_quality": _empty_regime_quality(["sensitive_data_provided"]),
        "missed_opportunity_quality": _empty_missed_opportunity_quality(["sensitive_data_provided"]),
        "false_positive_quality": _empty_false_positive_quality(["sensitive_data_provided"]),
        "entry_exit_quality": _empty_entry_exit_quality(["sensitive_data_provided"]),
        "risk_adjusted_quality": _empty_quality_summary("risk_adjusted_quality", ["sensitive_data_provided"]),
        "data_quality": _empty_quality_summary("data_quality", ["sensitive_data_provided"]),
        "promotion_readiness": _promotion_readiness(
            BLOCKED_BY_DATA_QUALITY,
            blocker_summary,
            ["remove_sensitive_data"],
        ),
        "improvement_actions": improvement_actions,
        "blocker_summary": blocker_summary,
        "missing_information": ["remove_sensitive_data"],
        "owner_action_queue": improvement_actions,
        "next_best_packet": next_best_packet,
        "next_remaining_lane": _next_remaining_lane(_mapping(source.get("remaining_work_closure_index"))),
        "safe_manual_next_action": (
            "Remove sensitive data and rerun the read-only quality evaluator with sanitized "
            "candidate-quality evidence only."
        ),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "input_redacted": True,
            "quality_status": BLOCKED_BY_DATA_QUALITY,
            "read_only": True,
        },
        "safety": _safety(),
    }


def _threshold_policy(overrides: Mapping[str, Any]) -> dict[str, Any]:
    active = dict(DEFAULT_THRESHOLDS)
    rejected: list[dict[str, str]] = []
    for key, raw_value in overrides.items():
        if key not in DEFAULT_THRESHOLDS:
            continue
        value = _threshold_value(key, raw_value)
        if value is None or not _threshold_override_allowed(key, value):
            rejected.append({"threshold": key, "reason": "threshold_override_rejected"})
            continue
        active[key] = value
    return {
        "default_thresholds": dict(DEFAULT_THRESHOLDS),
        "active_thresholds": active,
        "rejected_overrides": rejected,
        "threshold_blockers": ["threshold_override_rejected"] if rejected else [],
        "guardrails": {
            "min_candidate_quality_score_floor": 0.60,
            "min_expectancy_quality_score_floor": 0.60,
            "min_profit_factor_quality_score_floor": 0.60,
            "min_drawdown_efficiency_score_floor": 0.60,
            "max_missed_opportunity_count_ceiling": 3,
            "max_false_positive_count_ceiling": 3,
            "min_data_quality_score_floor": 0.70,
        },
    }


def _threshold_value(key: str, value: Any) -> float | None:
    number = _number(value)
    if number is None:
        return None
    if key.startswith("min_") and key.endswith("_score"):
        return _normalize_score(number)
    return number


def _threshold_override_allowed(key: str, value: float) -> bool:
    if key == "min_candidate_quality_score":
        return 0.60 <= value <= 1.0
    if key == "min_expectancy_quality_score":
        return 0.60 <= value <= 1.0
    if key == "min_profit_factor_quality_score":
        return 0.60 <= value <= 1.0
    if key == "min_drawdown_efficiency_score":
        return 0.60 <= value <= 1.0
    if key == "max_missed_opportunity_count":
        return 0 <= value <= 3
    if key == "max_false_positive_count":
        return 0 <= value <= 3
    if key == "min_data_quality_score":
        return 0.70 <= value <= 1.0
    if key.startswith("min_") and key.endswith("_score"):
        return DEFAULT_THRESHOLDS[key] <= value <= 1.0
    if key.startswith("max_") and key.endswith("_count"):
        return 0 <= value <= DEFAULT_THRESHOLDS[key]
    return True


def _expectancy_quality(contexts: Sequence[Mapping[str, Any]], thresholds: Mapping[str, float]) -> dict[str, Any]:
    score = _score_from_keys(contexts, ("expectancy_quality_score", "expectancy_score"))
    expectancy = _first_number(contexts, ("expectancy", "expectancy_r"))
    if score is None and expectancy is not None:
        score = _score_from_expectancy(expectancy)
    return _score_quality(
        "expectancy_quality",
        score,
        thresholds["min_expectancy_quality_score"],
        "expectancy_quality_score_missing",
        "expectancy_quality_score_below_threshold",
        {"expectancy": expectancy},
    )


def _profit_factor_quality(contexts: Sequence[Mapping[str, Any]], thresholds: Mapping[str, float]) -> dict[str, Any]:
    score = _score_from_keys(contexts, ("profit_factor_quality_score", "profit_factor_score"))
    profit_factor = _first_number(contexts, ("profit_factor",))
    if score is None and profit_factor is not None:
        score = min(max(profit_factor / 2.0, 0.0), 1.0)
    return _score_quality(
        "profit_factor_quality",
        score,
        thresholds["min_profit_factor_quality_score"],
        "profit_factor_quality_score_missing",
        "profit_factor_quality_score_below_threshold",
        {"profit_factor": profit_factor},
    )


def _drawdown_efficiency(contexts: Sequence[Mapping[str, Any]], thresholds: Mapping[str, float]) -> dict[str, Any]:
    score = _score_from_keys(
        contexts,
        ("drawdown_efficiency_score", "drawdown_score", "drawdown_quality_score"),
    )
    max_drawdown_pct = _drawdown_pct(contexts)
    if score is None and max_drawdown_pct is not None:
        score = min(max(1.0 - max_drawdown_pct, 0.0), 1.0)
    return _score_quality(
        "drawdown_efficiency",
        score,
        thresholds["min_drawdown_efficiency_score"],
        "drawdown_efficiency_score_missing",
        "drawdown_efficiency_score_below_threshold",
        {"max_drawdown_pct": max_drawdown_pct},
    )


def _regime_quality(contexts: Sequence[Mapping[str, Any]], thresholds: Mapping[str, float]) -> dict[str, Any]:
    score = _score_from_keys(contexts, ("regime_quality_score", "regime_score", "regime_coverage_score"))
    covered_regimes = _covered_regimes(contexts)
    weak_regimes = _weak_regimes(contexts)
    if score is None and covered_regimes:
        score = min(len(covered_regimes) / 3.0, 1.0)
    summary = _score_quality(
        "regime_quality",
        score,
        thresholds["min_regime_quality_score"],
        "regime_quality_score_missing",
        "regime_quality_score_below_threshold",
        {"covered_regimes": covered_regimes, "weak_regimes": weak_regimes},
    )
    if weak_regimes and "regime_specific_weakness_present" not in summary["blockers"]:
        summary["blockers"].append("regime_specific_weakness_present")
        summary["sufficient"] = False
    return summary


def _missed_opportunity_quality(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    missed_count = int(_first_number(contexts, ("missed_opportunity_count", "missed_valid_setups_count")) or 0)
    rejected_winner_count = int(_first_number(contexts, ("rejected_winner_count", "rejected_winners")) or 0)
    leakage_count = missed_count + rejected_winner_count
    max_allowed = int(thresholds["max_missed_opportunity_count"])
    blockers: list[str] = []
    if missed_count > max_allowed:
        blockers.append("missed_opportunity_count_above_threshold")
    if rejected_winner_count > max_allowed:
        blockers.append("rejected_winner_count_above_threshold")
    return {
        "missed_opportunity_count": missed_count,
        "rejected_winner_count": rejected_winner_count,
        "leakage_count": leakage_count,
        "max_allowed_missed_opportunity_count": max_allowed,
        "sufficient": not blockers,
        "blockers": blockers,
        "notes": _strings(_first_value(contexts, ("opportunity_leakage_notes", "leakage_notes"))),
    }


def _false_positive_quality(contexts: Sequence[Mapping[str, Any]], thresholds: Mapping[str, float]) -> dict[str, Any]:
    count = int(_first_number(contexts, ("false_positive_count", "false_positives")) or 0)
    max_allowed = int(thresholds["max_false_positive_count"])
    blockers = ["false_positive_count_above_threshold"] if count > max_allowed else []
    return {
        "false_positive_count": count,
        "max_allowed_false_positive_count": max_allowed,
        "sufficient": not blockers,
        "blockers": blockers,
    }


def _entry_exit_quality(contexts: Sequence[Mapping[str, Any]], thresholds: Mapping[str, float]) -> dict[str, Any]:
    score = _score_from_keys(contexts, ("entry_exit_quality_score", "entry_exit_score", "timing_quality_score"))
    late_entry_count = int(_first_number(contexts, ("late_entry_count", "late_entries")) or 0)
    early_exit_count = int(_first_number(contexts, ("early_exit_count", "early_exits")) or 0)
    max_late = int(thresholds["max_late_entry_count"])
    max_early = int(thresholds["max_early_exit_count"])
    blockers: list[str] = []
    if late_entry_count > max_late:
        blockers.append("late_entry_count_above_threshold")
    if early_exit_count > max_early:
        blockers.append("early_exit_count_above_threshold")
    return {
        "score": score,
        "late_entry_count": late_entry_count,
        "early_exit_count": early_exit_count,
        "max_allowed_late_entry_count": max_late,
        "max_allowed_early_exit_count": max_early,
        "sufficient": not blockers,
        "blockers": blockers,
    }


def _risk_adjusted_quality(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
    expectancy_quality: Mapping[str, Any],
    profit_factor_quality: Mapping[str, Any],
    drawdown_efficiency: Mapping[str, Any],
) -> dict[str, Any]:
    score = _score_from_keys(
        contexts,
        ("risk_adjusted_quality_score", "risk_adjusted_score", "risk_adjusted_opportunity_capture_score"),
    )
    if score is None:
        score = _average_score(
            (
                expectancy_quality.get("score"),
                profit_factor_quality.get("score"),
                drawdown_efficiency.get("score"),
            )
        )
    return _score_quality(
        "risk_adjusted_quality",
        score,
        thresholds["min_risk_adjusted_quality_score"],
        "risk_adjusted_quality_score_missing",
        "risk_adjusted_quality_score_below_threshold",
        {},
    )


def _data_quality(contexts: Sequence[Mapping[str, Any]], thresholds: Mapping[str, float]) -> dict[str, Any]:
    score = _score_from_keys(contexts, ("data_quality_score", "evidence_data_quality_score"))
    missing_fields = _strings(_first_value(contexts, ("missing_fields", "missing_data_fields")))
    invalid_rows = int(_first_number(contexts, ("invalid_rows", "invalid_row_count")) or 0)
    duplicate_trades = int(_first_number(contexts, ("duplicate_trades", "duplicate_trade_count")) or 0)
    malformed_timestamps = int(_first_number(contexts, ("malformed_timestamps", "bad_timestamp_count")) or 0)
    summary = _score_quality(
        "data_quality",
        score,
        thresholds["min_data_quality_score"],
        "data_quality_score_missing",
        "data_quality_score_below_threshold",
        {
            "missing_fields": missing_fields,
            "invalid_rows": invalid_rows,
            "duplicate_trades": duplicate_trades,
            "malformed_timestamps": malformed_timestamps,
        },
    )
    if missing_fields:
        summary["blockers"].append("data_quality_missing_fields")
        summary["sufficient"] = False
    if invalid_rows > 0:
        summary["blockers"].append("data_quality_invalid_rows")
        summary["sufficient"] = False
    if duplicate_trades > 0:
        summary["blockers"].append("data_quality_duplicate_trades")
        summary["sufficient"] = False
    if malformed_timestamps > 0:
        summary["blockers"].append("data_quality_malformed_timestamps")
        summary["sufficient"] = False
    summary["blockers"] = _unique(summary["blockers"])
    return summary


def _score_quality(
    quality_name: str,
    score: float | None,
    threshold: float,
    missing_blocker: str,
    low_blocker: str,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    if score is None:
        blockers.append(missing_blocker)
    elif score < threshold:
        blockers.append(low_blocker)
    return {
        "quality_name": quality_name,
        "score": score,
        "required_score": threshold,
        "sufficient": score is not None and score >= threshold,
        "blockers": blockers,
        **dict(extra),
    }


def _candidate_blockers(candidate_quality_score: float | None, thresholds: Mapping[str, float]) -> list[str]:
    if candidate_quality_score is None:
        return ["candidate_quality_score_missing"]
    if candidate_quality_score < thresholds["min_candidate_quality_score"]:
        return ["candidate_quality_score_below_threshold"]
    return []


def _resolve_quality_status(
    *,
    missing_core_evidence: bool,
    expectancy_quality: Mapping[str, Any],
    profit_factor_quality: Mapping[str, Any],
    drawdown_efficiency: Mapping[str, Any],
    regime_quality: Mapping[str, Any],
    missed_opportunity_quality: Mapping[str, Any],
    false_positive_quality: Mapping[str, Any],
    entry_exit_quality: Mapping[str, Any],
    risk_adjusted_quality: Mapping[str, Any],
    data_quality: Mapping[str, Any],
    candidate_quality_score: float | None,
    thresholds: Mapping[str, float],
) -> str:
    if missing_core_evidence:
        return INCOMPLETE_INPUTS
    if expectancy_quality.get("score") is None:
        return NEEDS_MORE_EVIDENCE
    if expectancy_quality.get("sufficient") is not True:
        return BLOCKED_BY_EXPECTANCY
    if profit_factor_quality.get("score") is None:
        return NEEDS_MORE_EVIDENCE
    if profit_factor_quality.get("sufficient") is not True:
        return BLOCKED_BY_PROFIT_FACTOR
    if drawdown_efficiency.get("score") is None:
        return NEEDS_MORE_EVIDENCE
    if drawdown_efficiency.get("sufficient") is not True:
        return BLOCKED_BY_DRAWDOWN_EFFICIENCY
    if regime_quality.get("score") is None:
        return NEEDS_MORE_EVIDENCE
    if regime_quality.get("sufficient") is not True:
        return BLOCKED_BY_REGIME_WEAKNESS
    if missed_opportunity_quality.get("sufficient") is not True:
        return BLOCKED_BY_MISSED_OPPORTUNITY_LEAKAGE
    if false_positive_quality.get("sufficient") is not True:
        return BLOCKED_BY_FALSE_POSITIVES
    if entry_exit_quality.get("sufficient") is not True:
        return BLOCKED_BY_ENTRY_EXIT_QUALITY
    if data_quality.get("score") is None:
        return NEEDS_MORE_EVIDENCE
    if data_quality.get("sufficient") is not True:
        return BLOCKED_BY_DATA_QUALITY
    if risk_adjusted_quality.get("score") is None:
        return NEEDS_MORE_EVIDENCE
    if risk_adjusted_quality.get("sufficient") is not True:
        return NEEDS_MORE_EVIDENCE
    if candidate_quality_score is None:
        return NEEDS_MORE_EVIDENCE
    if candidate_quality_score < thresholds["min_candidate_quality_score"]:
        return NEEDS_MORE_EVIDENCE
    return QUALITY_IMPROVEMENT_READY


def _blocker_summary(
    *,
    candidate_blockers: Sequence[str],
    expectancy_blockers: Sequence[str],
    profit_factor_blockers: Sequence[str],
    drawdown_blockers: Sequence[str],
    regime_blockers: Sequence[str],
    missed_opportunity_blockers: Sequence[str],
    false_positive_blockers: Sequence[str],
    entry_exit_blockers: Sequence[str],
    risk_adjusted_blockers: Sequence[str],
    data_quality_blockers: Sequence[str],
    threshold_blockers: Sequence[str],
) -> dict[str, list[str]]:
    all_blockers = _unique(
        [
            *candidate_blockers,
            *expectancy_blockers,
            *profit_factor_blockers,
            *drawdown_blockers,
            *regime_blockers,
            *missed_opportunity_blockers,
            *false_positive_blockers,
            *entry_exit_blockers,
            *risk_adjusted_blockers,
            *data_quality_blockers,
            *threshold_blockers,
        ]
    )
    return {
        "candidate_blockers": list(candidate_blockers),
        "expectancy_blockers": list(expectancy_blockers),
        "profit_factor_blockers": list(profit_factor_blockers),
        "drawdown_blockers": list(drawdown_blockers),
        "regime_blockers": list(regime_blockers),
        "missed_opportunity_blockers": list(missed_opportunity_blockers),
        "false_positive_blockers": list(false_positive_blockers),
        "entry_exit_blockers": list(entry_exit_blockers),
        "risk_adjusted_blockers": list(risk_adjusted_blockers),
        "data_quality_blockers": list(data_quality_blockers),
        "threshold_blockers": list(threshold_blockers),
        "all_blockers": all_blockers,
    }


def _improvement_actions(blocker_summary: Mapping[str, Sequence[str]], next_best_packet: str) -> list[dict[str, Any]]:
    actions = [
        (
            "IMPROVE_EXPECTANCY_QUALITY",
            "Improve expectancy quality",
            "high",
            blocker_summary.get("expectancy_blockers", []),
            "Review sanitized expectancy evidence and isolate loss patterns before any owner decision.",
        ),
        (
            "IMPROVE_PROFIT_FACTOR_QUALITY",
            "Improve profit factor quality",
            "high",
            blocker_summary.get("profit_factor_blockers", []),
            "Review sanitized profit-factor evidence and costs before any owner decision.",
        ),
        (
            "IMPROVE_DRAWDOWN_EFFICIENCY",
            "Improve drawdown efficiency",
            "high",
            blocker_summary.get("drawdown_blockers", []),
            "Review sanitized drawdown and risk efficiency evidence before any owner decision.",
        ),
        (
            "IMPROVE_REGIME_WEAKNESS",
            "Improve regime weakness",
            "high",
            blocker_summary.get("regime_blockers", []),
            "Review sanitized regime evidence and isolate weak regimes before any owner decision.",
        ),
        (
            "REVIEW_MISSED_OPPORTUNITY_LEAKAGE",
            "Review missed-opportunity leakage",
            "high",
            blocker_summary.get("missed_opportunity_blockers", []),
            "Review sanitized missed setups and rejected winners before any owner decision.",
        ),
        (
            "REVIEW_FALSE_POSITIVES",
            "Review false positives",
            "high",
            blocker_summary.get("false_positive_blockers", []),
            "Review sanitized false-positive evidence before any owner decision.",
        ),
        (
            "REVIEW_ENTRY_EXIT_TIMING",
            "Review entry and exit timing",
            "high",
            blocker_summary.get("entry_exit_blockers", []),
            "Review sanitized late-entry and early-exit evidence before any owner decision.",
        ),
        (
            "REVIEW_RISK_ADJUSTED_QUALITY",
            "Review risk-adjusted quality",
            "high",
            blocker_summary.get("risk_adjusted_blockers", []),
            "Review sanitized risk-adjusted opportunity capture evidence before any owner decision.",
        ),
        (
            "REVIEW_NEXT_PACKET",
            f"Review next packet: {next_best_packet}",
            "medium",
            ["owner_review_required"],
            "Review the next packet manually; no execution is authorized.",
        ),
    ]
    return [_action(action_id, title, priority, blocked_by, safe_action) for action_id, title, priority, blocked_by, safe_action in actions]


def _action(
    action_id: str,
    title: str,
    priority: str,
    blocked_by: Sequence[str],
    safe_action: str,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "title": title,
        "priority": priority,
        "owner_decision_required": True,
        "execution_allowed": False,
        "safe_action": safe_action,
        "blocked_by": list(blocked_by) or ["owner_review_required"],
    }


def _improvement_priority(quality_status: str, blocker_summary: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    if quality_status == QUALITY_IMPROVEMENT_READY:
        return {
            "priority": "medium",
            "next_action_id": "REVIEW_NEXT_PACKET",
            "blocked_by": ["owner_review_required"],
        }
    if quality_status == INCOMPLETE_INPUTS:
        return {
            "priority": "high",
            "next_action_id": "COLLECT_SANITIZED_CANDIDATE_QUALITY_EVIDENCE",
            "blocked_by": ["incomplete_inputs"],
        }
    return {
        "priority": "high",
        "next_action_id": _status_action_id(quality_status),
        "blocked_by": list(blocker_summary.get("all_blockers", [])) or ["owner_review_required"],
    }


def _status_action_id(quality_status: str) -> str:
    return {
        BLOCKED_BY_EXPECTANCY: "IMPROVE_EXPECTANCY_QUALITY",
        BLOCKED_BY_PROFIT_FACTOR: "IMPROVE_PROFIT_FACTOR_QUALITY",
        BLOCKED_BY_DRAWDOWN_EFFICIENCY: "IMPROVE_DRAWDOWN_EFFICIENCY",
        BLOCKED_BY_REGIME_WEAKNESS: "IMPROVE_REGIME_WEAKNESS",
        BLOCKED_BY_MISSED_OPPORTUNITY_LEAKAGE: "REVIEW_MISSED_OPPORTUNITY_LEAKAGE",
        BLOCKED_BY_FALSE_POSITIVES: "REVIEW_FALSE_POSITIVES",
        BLOCKED_BY_ENTRY_EXIT_QUALITY: "REVIEW_ENTRY_EXIT_TIMING",
        BLOCKED_BY_DATA_QUALITY: "REVIEW_DATA_QUALITY",
    }.get(quality_status, "REVIEW_RISK_ADJUSTED_QUALITY")


def _promotion_readiness(
    quality_status: str,
    blocker_summary: Mapping[str, Sequence[str]],
    missing_information: Sequence[str],
) -> dict[str, Any]:
    ready = quality_status == QUALITY_IMPROVEMENT_READY
    return {
        "quality_status": quality_status,
        "can_queue_demo_candidate_review_readiness": ready,
        "demo_execution_authorized": False,
        "live_execution_authorized": False,
        "broker_execution_authorized": False,
        "required_owner_review": True,
        "promotion_blockers": list(blocker_summary.get("all_blockers", [])),
        "missing_information": list(missing_information),
    }


def _safe_manual_next_action(quality_status: str) -> str:
    if quality_status == QUALITY_IMPROVEMENT_READY:
        return (
            "Owner may review the candidate-quality improvement packet and queue demo-candidate "
            "review readiness. AIOS does not trade, access brokers, transfer funds, or use credentials."
        )
    if quality_status == INCOMPLETE_INPUTS:
        return (
            "Provide sanitized profitability evaluation, candidate-quality snapshot, opportunity-leakage "
            "review, and entry-exit review, then rerun this evaluator."
        )
    return (
        "Collect sanitized candidate-quality evidence, rerun the read-only quality evaluator, and keep "
        "all trading, broker, bank, and money actions outside AIOS until owner approval."
    )


def _next_remaining_lane(remaining: Mapping[str, Any]) -> dict[str, Any]:
    lanes = _sequence(remaining.get("remaining_lanes"))
    normalized = [dict(item) for item in lanes if isinstance(item, Mapping)]
    for index, lane in enumerate(normalized):
        if _text(lane.get("lane_id")) == CURRENT_LANE_ID:
            if index + 1 < len(normalized):
                return normalized[index + 1]
            break
    for lane in normalized:
        if _text(lane.get("lane_id")) == NEXT_LANE_ID:
            return lane
    return {
        "lane_id": NEXT_LANE_ID,
        "title": "Demo-candidate review readiness",
        "status": "OWNER_REVIEW_REQUIRED",
        "priority": "high",
        "safe_packet_name": NEXT_PACKET_IF_READY,
    }


def _input_summary(
    source: Mapping[str, Any],
    explicit_candidate_quality_score: float | None,
    derived_candidate_quality_score: float | None,
    sub_scores: Mapping[str, float | None],
) -> dict[str, Any]:
    return {
        "input_fields_seen": sorted(str(key) for key in source.keys()),
        "meaningful_evidence_present": _has_meaningful_evidence(source, _quality_contexts(source)),
        "explicit_candidate_quality_score": explicit_candidate_quality_score,
        "derived_candidate_quality_score": derived_candidate_quality_score,
        "sub_scores": dict(sub_scores),
        "threshold_overrides_seen": sorted(str(key) for key in _mapping(source.get("thresholds")).keys()),
        "as_of_date": _text(source.get("as_of_date")),
        "owner_name": _text(source.get("owner_name"), "Anthony"),
    }


def _missing_information(source: Mapping[str, Any], contexts: Sequence[Mapping[str, Any]]) -> list[str]:
    if _has_meaningful_evidence(source, contexts):
        return []
    return list(CORE_EVIDENCE_KEYS)


def _has_meaningful_evidence(source: Mapping[str, Any], contexts: Sequence[Mapping[str, Any]]) -> bool:
    if any(isinstance(source.get(key), Mapping) and source.get(key) for key in CORE_EVIDENCE_KEYS):
        return True
    score_keys = (
        "candidate_quality_score",
        "expectancy_quality_score",
        "profit_factor_quality_score",
        "drawdown_efficiency_score",
        "regime_quality_score",
        "risk_adjusted_quality_score",
        "data_quality_score",
        "missed_opportunity_count",
        "false_positive_count",
        "late_entry_count",
        "early_exit_count",
    )
    return any(_first_value(contexts, (key,)) is not None for key in score_keys)


def _quality_contexts(source: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    contexts: list[Mapping[str, Any]] = [source]
    for key in CONTEXT_KEYS:
        value = source.get(key)
        if isinstance(value, Mapping):
            contexts.append(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            contexts.extend(item for item in value if isinstance(item, Mapping))
    return contexts


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            key = str(raw_key).strip().lower()
            if any(part in key for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(nested):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _covered_regimes(contexts: Sequence[Mapping[str, Any]]) -> list[str]:
    regimes: list[str] = []
    for key in ("covered_regimes", "regimes"):
        for item in _sequence(_first_value(contexts, (key,))):
            if isinstance(item, Mapping):
                text = _text(item.get("regime") or item.get("name") or item.get("regime_id"))
            else:
                text = _text(item)
            if text:
                regimes.append(text)
    regime_results = _first_value(contexts, ("regime_results",))
    if isinstance(regime_results, Mapping):
        regimes.extend(str(key) for key in regime_results.keys() if str(key).strip())
    return _unique(regimes)


def _weak_regimes(contexts: Sequence[Mapping[str, Any]]) -> list[str]:
    weak = _strings(_first_value(contexts, ("weak_regimes", "underperforming_regimes")))
    regime_results = _first_value(contexts, ("regime_results",))
    if isinstance(regime_results, Mapping):
        for regime_name, result in regime_results.items():
            if isinstance(result, Mapping):
                score = _score_from_keys([result], ("quality_score", "regime_quality_score", "score"))
                if score is not None and score < DEFAULT_THRESHOLDS["min_regime_quality_score"]:
                    weak.append(str(regime_name))
    return _unique(weak)


def _drawdown_pct(contexts: Sequence[Mapping[str, Any]]) -> float | None:
    value = _first_number(contexts, ("max_drawdown_pct", "drawdown_pct"))
    if value is not None:
        return _normalize_rate(value)
    raw_drawdown = _first_number(contexts, ("max_drawdown",))
    if raw_drawdown is not None and 0 <= raw_drawdown <= 1:
        return raw_drawdown
    return None


def _score_from_expectancy(expectancy: float) -> float:
    if expectancy < 0:
        return 0.0
    return min(0.70 + min(expectancy, 0.30), 1.0)


def _score_from_keys(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    number = _first_number(contexts, keys)
    if number is None:
        return None
    return _normalize_score(number)


def _average_score(values: Sequence[Any]) -> float | None:
    scores = [value for value in (_score_like(item) for item in values) if value is not None]
    if not scores:
        return None
    return round(sum(scores) / len(scores), 6)


def _score_like(value: Any) -> float | None:
    number = _number(value)
    if number is None:
        return None
    return _normalize_score(number)


def _normalize_score(value: float) -> float:
    if value > 1:
        value = value / 100.0
    return min(max(value, 0.0), 1.0)


def _normalize_rate(value: float | None) -> float | None:
    if value is None:
        return None
    return value / 100.0 if abs(value) > 1 else value


def _first_value(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> Any:
    for context in contexts:
        for key in keys:
            if key in context and context.get(key) not in (None, ""):
                return context.get(key)
    return None


def _first_number(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _number(_first_value(contexts, keys))


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [value]
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _sequence(value) if str(item).strip()]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        percent = text.endswith("%")
        if percent:
            text = text[:-1].strip()
        try:
            number = float(text)
        except ValueError:
            return None
        return number / 100.0 if percent else number
    return None


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value).strip()))


def _empty_quality_summary(quality_name: str, blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "quality_name": quality_name,
        "score": None,
        "required_score": None,
        "sufficient": False,
        "blockers": list(blockers),
    }


def _empty_regime_quality(blockers: Sequence[str]) -> dict[str, Any]:
    summary = _empty_quality_summary("regime_quality", blockers)
    summary.update({"covered_regimes": [], "weak_regimes": []})
    return summary


def _empty_missed_opportunity_quality(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "missed_opportunity_count": 0,
        "rejected_winner_count": 0,
        "leakage_count": 0,
        "max_allowed_missed_opportunity_count": DEFAULT_THRESHOLDS["max_missed_opportunity_count"],
        "sufficient": False,
        "blockers": list(blockers),
        "notes": [],
    }


def _empty_false_positive_quality(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "false_positive_count": 0,
        "max_allowed_false_positive_count": DEFAULT_THRESHOLDS["max_false_positive_count"],
        "sufficient": False,
        "blockers": list(blockers),
    }


def _empty_entry_exit_quality(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "score": None,
        "late_entry_count": 0,
        "early_exit_count": 0,
        "max_allowed_late_entry_count": DEFAULT_THRESHOLDS["max_late_entry_count"],
        "max_allowed_early_exit_count": DEFAULT_THRESHOLDS["max_early_exit_count"],
        "sufficient": False,
        "blockers": list(blockers),
    }


def _safety() -> dict[str, bool]:
    return {
        "read_only": True,
        "manual_execution_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "dashboard_runtime_allowed": False,
        "owner_gate_required": True,
        "fixed_return_target_promised": False,
        "profit_claim_authorized": False,
    }


__all__ = [
    "MODE",
    "SCHEMA",
    "evaluate_profit_candidate_quality_improvement_v1",
]
