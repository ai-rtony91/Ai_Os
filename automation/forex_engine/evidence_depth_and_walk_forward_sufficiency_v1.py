"""Read-only Forex evidence depth and walk-forward sufficiency evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1"
MODE = "READ_ONLY_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY"

SUFFICIENT_FOR_NEXT_PROFIT_LANE = "SUFFICIENT_FOR_NEXT_PROFIT_LANE"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
BLOCKED_BY_SAMPLE_SIZE = "BLOCKED_BY_SAMPLE_SIZE"
BLOCKED_BY_WALK_FORWARD = "BLOCKED_BY_WALK_FORWARD"
BLOCKED_BY_OOS_INSTABILITY = "BLOCKED_BY_OOS_INSTABILITY"
BLOCKED_BY_REGIME_COVERAGE = "BLOCKED_BY_REGIME_COVERAGE"
BLOCKED_BY_NEGATIVE_EXPECTANCY = "BLOCKED_BY_NEGATIVE_EXPECTANCY"
BLOCKED_BY_LOW_PROFIT_FACTOR = "BLOCKED_BY_LOW_PROFIT_FACTOR"
BLOCKED_BY_DRAWDOWN = "BLOCKED_BY_DRAWDOWN"
BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

CURRENT_LANE_ID = "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY"
NEXT_LANE_ID = "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT"
NEXT_PACKET_IF_SUFFICIENT = "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1"
THIS_PACKET = SCHEMA

OPPORTUNITY_CAPTURE_OBJECTIVE = (
    "maximize validated risk-adjusted opportunity capture while preserving capital and proving edge"
)

DEFAULT_THRESHOLDS: dict[str, float] = {
    "min_total_trades": 100,
    "min_oos_trades": 30,
    "min_walk_forward_windows": 3,
    "min_profitable_windows": 2,
    "min_regime_count": 3,
    "min_profit_factor": 1.20,
    "min_expectancy": 0.0,
    "max_drawdown_pct": 0.10,
    "min_data_quality_score": 0.80,
    "min_candidate_stability_score": 0.70,
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
    "strategy_evaluation",
    "walk_forward_validation",
    "profitability_evaluation",
    "paper_session_samples",
)

EVIDENCE_CONTEXT_KEYS = (
    "strategy_evaluation",
    "walk_forward_validation",
    "profitability_evaluation",
    "evidence_promotion_gate",
    "paper_session_summary",
    "candidate_quality_snapshot",
    "broker_demo_observability",
    "capital_withdrawal_owner_review_workflow",
)


def evaluate_evidence_depth_and_walk_forward_sufficiency_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate sanitized paper/simulated evidence and route the next owner-review lane."""

    source = payload if isinstance(payload, Mapping) else {}
    threshold_policy = _threshold_policy(_mapping(source.get("thresholds")))
    thresholds = threshold_policy["active_thresholds"]
    threshold_blockers = list(threshold_policy["threshold_blockers"])

    if _contains_sensitive_key(source):
        return _sensitive_payload(source, threshold_policy)

    contexts = _evidence_contexts(source)
    missing_information = _missing_information(source, contexts)
    missing_core_evidence = bool(missing_information)

    evidence_depth_summary, sample_sufficiency_summary = _sample_summaries(contexts, thresholds)
    walk_forward_summary = _walk_forward_summary(contexts, thresholds)
    out_of_sample_summary = _out_of_sample_summary(
        sample_sufficiency_summary,
        walk_forward_summary,
        thresholds,
    )
    regime_coverage_summary = _regime_coverage_summary(contexts, thresholds)
    profitability_summary = _profitability_summary(contexts, thresholds)
    drawdown_summary = _drawdown_summary(contexts, thresholds)
    data_quality_summary = _data_quality_summary(contexts, thresholds)
    leakage_summary = _leakage_summary(contexts)

    blocker_summary = _blocker_summary(
        sample_blockers=sample_sufficiency_summary["sample_blockers"],
        walk_forward_blockers=walk_forward_summary["walk_forward_blockers"],
        oos_blockers=out_of_sample_summary["oos_blockers"],
        regime_blockers=regime_coverage_summary["regime_blockers"],
        profitability_blockers=profitability_summary["profitability_blockers"],
        drawdown_blockers=drawdown_summary["drawdown_blockers"],
        data_quality_blockers=data_quality_summary["data_quality_blockers"],
        leakage_blockers=leakage_summary["leakage_blockers"],
        threshold_blockers=threshold_blockers,
    )

    evidence_status = _resolve_evidence_status(
        missing_core_evidence=missing_core_evidence,
        sample_sufficient=sample_sufficiency_summary["sample_sufficient"],
        oos_sample_sufficient=sample_sufficiency_summary["oos_sample_sufficient"],
        walk_forward_sufficient=walk_forward_summary["walk_forward_sufficient"],
        oos_stable=out_of_sample_summary["oos_stable"],
        regime_coverage_sufficient=regime_coverage_summary["regime_coverage_sufficient"],
        positive_expectancy=profitability_summary["positive_expectancy"],
        profit_factor_sufficient=profitability_summary["profit_factor_sufficient"],
        drawdown_within_limit=drawdown_summary["drawdown_within_limit"],
        data_quality_sufficient=data_quality_summary["data_quality_sufficient"],
    )

    sufficient_for_next_profit_lane = evidence_status == SUFFICIENT_FOR_NEXT_PROFIT_LANE
    critical_blockers = _critical_blockers(blocker_summary)
    sufficient_for_demo_candidate_review = (
        sufficient_for_next_profit_lane
        and evidence_depth_summary["total_trades"] >= thresholds["min_total_trades"]
        and sample_sufficiency_summary["oos_trades"] >= thresholds["min_oos_trades"]
        and walk_forward_summary["walk_forward_gate_cleared"] is True
        and profitability_summary["positive_expectancy"] is True
        and profitability_summary["profit_factor_sufficient"] is True
        and drawdown_summary["drawdown_within_limit"] is True
        and data_quality_summary["data_quality_sufficient"] is True
        and not critical_blockers
    )

    next_remaining_lane = _next_remaining_lane(_mapping(source.get("remaining_work_closure_index")))
    next_best_packet = NEXT_PACKET_IF_SUFFICIENT if sufficient_for_next_profit_lane else THIS_PACKET
    promotion_readiness = _promotion_readiness(
        evidence_status=evidence_status,
        sufficient_for_next_profit_lane=sufficient_for_next_profit_lane,
        sufficient_for_demo_candidate_review=sufficient_for_demo_candidate_review,
        blocker_summary=blocker_summary,
        missing_information=missing_information,
    )

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
        "evidence_status": evidence_status,
        "sufficient_for_next_profit_lane": sufficient_for_next_profit_lane,
        "sufficient_for_demo_candidate_review": sufficient_for_demo_candidate_review,
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "threshold_policy": threshold_policy,
        "evidence_depth_summary": evidence_depth_summary,
        "sample_sufficiency_summary": sample_sufficiency_summary,
        "walk_forward_summary": walk_forward_summary,
        "out_of_sample_summary": out_of_sample_summary,
        "regime_coverage_summary": regime_coverage_summary,
        "profitability_summary": profitability_summary,
        "drawdown_summary": drawdown_summary,
        "data_quality_summary": data_quality_summary,
        "leakage_and_missed_opportunity_summary": leakage_summary,
        "promotion_readiness": promotion_readiness,
        "blocker_summary": blocker_summary,
        "missing_information": missing_information,
        "owner_action_queue": _owner_action_queue(blocker_summary, next_best_packet),
        "next_best_packet": next_best_packet,
        "next_remaining_lane": next_remaining_lane,
        "safe_manual_next_action": _safe_manual_next_action(evidence_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "evidence_status": evidence_status,
            "next_best_packet": next_best_packet,
            "next_remaining_lane": next_remaining_lane,
            "read_only": True,
        },
        "safety": _safety(),
    }


def _sensitive_payload(source: Mapping[str, Any], threshold_policy: Mapping[str, Any]) -> dict[str, Any]:
    blocker_summary = _blocker_summary(
        sample_blockers=[],
        walk_forward_blockers=[],
        oos_blockers=[],
        regime_blockers=[],
        profitability_blockers=[],
        drawdown_blockers=[],
        data_quality_blockers=["sensitive_data_provided"],
        leakage_blockers=[],
        threshold_blockers=list(threshold_policy.get("threshold_blockers", [])),
    )
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
        "evidence_status": BLOCKED_BY_DATA_QUALITY,
        "sufficient_for_next_profit_lane": False,
        "sufficient_for_demo_candidate_review": False,
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "threshold_policy": dict(threshold_policy),
        "evidence_depth_summary": _empty_evidence_depth_summary(),
        "sample_sufficiency_summary": _empty_sample_sufficiency_summary(["sensitive_data_provided"]),
        "walk_forward_summary": _empty_walk_forward_summary(["sensitive_data_provided"]),
        "out_of_sample_summary": _empty_oos_summary(["sensitive_data_provided"]),
        "regime_coverage_summary": _empty_regime_summary(["sensitive_data_provided"]),
        "profitability_summary": _empty_profitability_summary(["sensitive_data_provided"]),
        "drawdown_summary": _empty_drawdown_summary(["sensitive_data_provided"]),
        "data_quality_summary": {
            "data_quality_score": None,
            "data_quality_sufficient": False,
            "spread_slippage_present": False,
            "missing_fields": [],
            "invalid_rows": 0,
            "duplicate_trades": 0,
            "malformed_timestamps": 0,
            "data_quality_blockers": ["sensitive_data_provided"],
        },
        "leakage_and_missed_opportunity_summary": _empty_leakage_summary(["sensitive_data_provided"]),
        "promotion_readiness": _promotion_readiness(
            evidence_status=BLOCKED_BY_DATA_QUALITY,
            sufficient_for_next_profit_lane=False,
            sufficient_for_demo_candidate_review=False,
            blocker_summary=blocker_summary,
            missing_information=["remove_sensitive_data"],
        ),
        "blocker_summary": blocker_summary,
        "missing_information": ["remove_sensitive_data"],
        "owner_action_queue": _owner_action_queue(blocker_summary, THIS_PACKET),
        "next_best_packet": THIS_PACKET,
        "next_remaining_lane": _next_remaining_lane(_mapping(source.get("remaining_work_closure_index"))),
        "safe_manual_next_action": "Remove sensitive data and rerun the read-only sufficiency evaluator.",
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "input_redacted": True,
            "evidence_status": BLOCKED_BY_DATA_QUALITY,
            "read_only": True,
        },
        "safety": _safety(),
    }


def _threshold_policy(overrides: Mapping[str, Any]) -> dict[str, Any]:
    active = dict(DEFAULT_THRESHOLDS)
    rejected: list[dict[str, Any]] = []
    for key, raw_value in overrides.items():
        if key not in DEFAULT_THRESHOLDS:
            continue
        value = _number(raw_value)
        if value is None or not _threshold_override_allowed(key, value):
            rejected.append({"threshold": key, "reason": "threshold_override_rejected"})
            continue
        active[key] = value
    threshold_blockers = ["threshold_override_rejected"] if rejected else []
    return {
        "default_thresholds": dict(DEFAULT_THRESHOLDS),
        "active_thresholds": active,
        "rejected_overrides": rejected,
        "threshold_blockers": threshold_blockers,
        "guardrails": {
            "min_total_trades_floor": 30,
            "min_oos_trades_floor": 10,
            "min_walk_forward_windows_floor": 2,
            "min_profit_factor_floor": 1.0,
            "max_drawdown_pct_ceiling": 0.25,
        },
    }


def _threshold_override_allowed(key: str, value: float) -> bool:
    if key == "min_total_trades":
        return value >= 30
    if key == "min_oos_trades":
        return value >= 10
    if key == "min_walk_forward_windows":
        return value >= 2
    if key == "min_profit_factor":
        return value >= 1.0
    if key == "max_drawdown_pct":
        return value <= 0.25
    if key == "min_expectancy":
        return value >= 0.0
    if key in {"min_profitable_windows", "min_regime_count"}:
        return value >= 1
    if key in {"min_data_quality_score", "min_candidate_stability_score"}:
        return 0.0 <= value <= 1.0
    return True


def _sample_summaries(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    total_trades = _first_number(
        contexts,
        ("total_trades", "sample_count", "trade_count", "observed_trade_count", "sample_size"),
    )
    if total_trades is None:
        total_trades = _trade_count_from_sequences(contexts)
    oos_trades = _first_number(
        contexts,
        ("oos_trade_count", "out_of_sample_trade_count", "oos_trades", "out_of_sample_trades"),
    )
    in_sample_trades = _first_number(
        contexts,
        ("in_sample_trade_count", "in_sample_trades", "ins_trade_count"),
    )
    if oos_trades is None:
        oos_trades = _trade_count_from_named_sequences(
            contexts,
            ("oos_trades", "out_of_sample_trades", "oos_results", "out_of_sample_results"),
        )
    if in_sample_trades is None and total_trades is not None and oos_trades is not None:
        in_sample_trades = max(total_trades - oos_trades, 0)

    win_count = _first_number(contexts, ("win_count", "winning_trades", "wins"))
    loss_count = _first_number(contexts, ("loss_count", "losing_trades", "losses"))
    breakeven_count = _first_number(contexts, ("breakeven_count", "flat_trades"))
    win_rate = None
    if win_count is not None and loss_count is not None:
        denominator = win_count + loss_count + (breakeven_count or 0)
        if denominator > 0:
            win_rate = win_count / denominator

    total_trades_value = int(total_trades or 0)
    oos_trades_value = int(oos_trades or 0)
    sample_sufficient = total_trades_value >= thresholds["min_total_trades"]
    oos_sample_sufficient = oos_trades_value >= thresholds["min_oos_trades"]

    sample_blockers: list[str] = []
    if total_trades is None:
        sample_blockers.append("total_trades_missing")
    elif not sample_sufficient:
        sample_blockers.append("total_trades_below_minimum")
    if oos_trades is None:
        sample_blockers.append("oos_trade_count_missing")
    elif not oos_sample_sufficient:
        sample_blockers.append("oos_trades_below_minimum")

    evidence_depth_summary = {
        "total_trades": total_trades_value,
        "oos_trades": oos_trades_value,
        "in_sample_trades": int(in_sample_trades or 0),
        "win_count": int(win_count or 0),
        "loss_count": int(loss_count or 0),
        "breakeven_count": int(breakeven_count or 0),
        "win_rate": win_rate,
        "sample_count": total_trades_value,
        "session_count": _session_count(contexts),
    }
    sample_sufficiency_summary = {
        "total_trades": total_trades_value,
        "required_total_trades": thresholds["min_total_trades"],
        "oos_trades": oos_trades_value,
        "required_oos_trades": thresholds["min_oos_trades"],
        "sample_sufficient": sample_sufficient,
        "oos_sample_sufficient": oos_sample_sufficient,
        "sample_blockers": sample_blockers,
    }
    return evidence_depth_summary, sample_sufficiency_summary


def _walk_forward_summary(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    windows = _first_sequence(contexts, ("walk_forward_windows", "windows", "window_results"))
    total_windows = _first_number(
        contexts,
        ("walk_forward_window_count", "observed_walkforward_windows", "total_windows"),
    )
    if total_windows is None and windows:
        total_windows = len(windows)
    profitable_windows = _first_number(contexts, ("profitable_windows", "passed_windows", "passing_windows"))
    if profitable_windows is None and windows:
        profitable_windows = sum(1 for window in windows if _window_passed(window))
    failed_windows = _first_number(contexts, ("failed_windows", "failing_windows"))
    if failed_windows is None and total_windows is not None and profitable_windows is not None:
        failed_windows = max(total_windows - profitable_windows, 0)

    explicit_gate = _first_bool(contexts, ("walk_forward_gate_cleared", "walk_forward_passed", "gate_cleared"))
    total_windows_value = int(total_windows or 0)
    profitable_windows_value = int(profitable_windows or 0)
    inferred_gate = (
        total_windows_value >= thresholds["min_walk_forward_windows"]
        and profitable_windows_value >= thresholds["min_profitable_windows"]
    )
    walk_forward_gate_cleared = explicit_gate if explicit_gate is not None else inferred_gate
    stability_score = _first_number(contexts, ("stability_score", "candidate_stability_score"))
    oos_pass_rate = _normalize_rate(_first_number(contexts, ("oos_pass_rate", "out_of_sample_pass_rate")))

    walk_forward_sufficient = (
        total_windows_value >= thresholds["min_walk_forward_windows"]
        and profitable_windows_value >= thresholds["min_profitable_windows"]
        and walk_forward_gate_cleared is True
    )
    blockers: list[str] = []
    if total_windows is None:
        blockers.append("walk_forward_windows_missing")
    elif total_windows_value < thresholds["min_walk_forward_windows"]:
        blockers.append("walk_forward_windows_below_minimum")
    if profitable_windows is None:
        blockers.append("profitable_windows_missing")
    elif profitable_windows_value < thresholds["min_profitable_windows"]:
        blockers.append("profitable_windows_below_minimum")
    if walk_forward_gate_cleared is not True:
        blockers.append("walk_forward_gate_not_cleared")

    return {
        "total_windows": total_windows_value,
        "required_windows": thresholds["min_walk_forward_windows"],
        "profitable_windows": profitable_windows_value,
        "required_profitable_windows": thresholds["min_profitable_windows"],
        "failed_windows": int(failed_windows or 0),
        "walk_forward_gate_cleared": walk_forward_gate_cleared is True,
        "walk_forward_sufficient": walk_forward_sufficient,
        "stability_score": stability_score,
        "oos_pass_rate": oos_pass_rate,
        "walk_forward_blockers": blockers,
    }


def _out_of_sample_summary(
    sample_summary: Mapping[str, Any],
    walk_forward: Mapping[str, Any],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    stability_score = walk_forward.get("stability_score")
    oos_pass_rate = walk_forward.get("oos_pass_rate")
    blockers: list[str] = []
    if not sample_summary["oos_sample_sufficient"]:
        blockers.append("oos_sample_below_minimum")
    if stability_score is not None and stability_score < thresholds["min_candidate_stability_score"]:
        blockers.append("oos_stability_score_below_minimum")
    if oos_pass_rate is not None and oos_pass_rate < 0.50:
        blockers.append("oos_pass_rate_below_minimum")
    oos_stable = (
        sample_summary["oos_sample_sufficient"] is True
        and "oos_stability_score_below_minimum" not in blockers
        and "oos_pass_rate_below_minimum" not in blockers
    )
    return {
        "oos_trades": sample_summary["oos_trades"],
        "required_oos_trades": thresholds["min_oos_trades"],
        "stability_score": stability_score,
        "required_stability_score": thresholds["min_candidate_stability_score"],
        "oos_pass_rate": oos_pass_rate,
        "oos_stable": oos_stable,
        "oos_blockers": blockers,
    }


def _regime_coverage_summary(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    covered = _covered_regimes(contexts)
    regime_count = len(covered)
    sufficient = regime_count >= thresholds["min_regime_count"]
    blockers = [] if sufficient else ["regime_count_below_minimum"]
    return {
        "regime_count": regime_count,
        "required_regime_count": thresholds["min_regime_count"],
        "covered_regimes": covered,
        "regime_coverage_sufficient": sufficient,
        "regime_blockers": blockers,
    }


def _profitability_summary(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    expectancy = _first_number(contexts, ("expectancy", "average_pnl", "expectancy_per_trade"))
    profit_factor = _first_number(contexts, ("profit_factor",))
    gross_profit = _first_number(contexts, ("gross_profit",))
    gross_loss = _first_number(contexts, ("gross_loss",))
    if profit_factor is None and gross_profit is not None and gross_loss not in (None, 0):
        profit_factor = abs(gross_profit) / abs(gross_loss)

    positive_expectancy = expectancy is not None and expectancy >= thresholds["min_expectancy"]
    profit_factor_sufficient = profit_factor is not None and profit_factor >= thresholds["min_profit_factor"]
    blockers: list[str] = []
    if expectancy is None:
        blockers.append("expectancy_missing")
    elif not positive_expectancy:
        blockers.append("expectancy_below_minimum")
    if profit_factor is None:
        blockers.append("profit_factor_missing")
    elif not profit_factor_sufficient:
        blockers.append("profit_factor_below_minimum")

    return {
        "expectancy": expectancy,
        "required_expectancy": thresholds["min_expectancy"],
        "profit_factor": profit_factor,
        "required_profit_factor": thresholds["min_profit_factor"],
        "positive_expectancy": positive_expectancy,
        "profit_factor_sufficient": profit_factor_sufficient,
        "total_pnl": _first_number(contexts, ("total_pnl", "net_pnl")),
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "candidate_status": _first_text(contexts, ("candidate_status",)),
        "promotion_status": _first_text(contexts, ("promotion_status",)),
        "profitability_blockers": blockers,
    }


def _drawdown_summary(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    max_drawdown_pct = _first_drawdown_pct(contexts)
    if max_drawdown_pct is None:
        max_drawdown_pct = _drawdown_from_equity_curve(contexts)
    daily_loss_stop_triggered = _first_bool(contexts, ("daily_loss_stop_triggered",))
    risk_blocks = _strings(_first_value(contexts, ("risk_blocks",)))
    drawdown_within_limit = (
        max_drawdown_pct is not None
        and max_drawdown_pct <= thresholds["max_drawdown_pct"]
        and daily_loss_stop_triggered is not True
        and not risk_blocks
    )
    blockers: list[str] = []
    if max_drawdown_pct is None:
        blockers.append("max_drawdown_pct_missing")
    elif max_drawdown_pct > thresholds["max_drawdown_pct"]:
        blockers.append("max_drawdown_pct_above_limit")
    if daily_loss_stop_triggered is True:
        blockers.append("daily_loss_stop_triggered")
    blockers.extend(risk_blocks)

    return {
        "max_drawdown_pct": max_drawdown_pct,
        "max_allowed_drawdown_pct": thresholds["max_drawdown_pct"],
        "drawdown_within_limit": drawdown_within_limit,
        "daily_loss_stop_triggered": daily_loss_stop_triggered is True,
        "risk_blocks": risk_blocks,
        "drawdown_blockers": _unique(blockers),
    }


def _data_quality_summary(
    contexts: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float],
) -> dict[str, Any]:
    score = _first_number(contexts, ("data_quality_score", "quality_score"))
    missing_fields = _strings(_first_value(contexts, ("missing_fields",)))
    invalid_rows = int(_first_number(contexts, ("invalid_rows",)) or 0)
    duplicate_trades = int(_first_number(contexts, ("duplicate_trades",)) or 0)
    malformed_timestamps = int(_first_number(contexts, ("malformed_timestamps",)) or 0)
    spread_available = _first_bool(contexts, ("spread_available",))
    slippage_available = _first_bool(contexts, ("slippage_available",))
    spread_slippage_present = spread_available is True and slippage_available is True

    blockers: list[str] = []
    if score is None:
        blockers.append("data_quality_score_missing")
    elif score < thresholds["min_data_quality_score"]:
        blockers.append("data_quality_score_below_minimum")
    if missing_fields:
        blockers.append("missing_fields_present")
    if invalid_rows > 0:
        blockers.append("invalid_rows_present")
    if duplicate_trades > 0:
        blockers.append("duplicate_trades_present")
    if malformed_timestamps > 0:
        blockers.append("malformed_timestamps_present")
    if not spread_slippage_present:
        blockers.append("spread_or_slippage_missing")

    return {
        "data_quality_score": score,
        "required_data_quality_score": thresholds["min_data_quality_score"],
        "data_quality_sufficient": not blockers,
        "spread_slippage_present": spread_slippage_present,
        "missing_fields": missing_fields,
        "invalid_rows": invalid_rows,
        "duplicate_trades": duplicate_trades,
        "malformed_timestamps": malformed_timestamps,
        "data_quality_blockers": blockers,
    }


def _leakage_summary(contexts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    fields = (
        "missed_valid_setups_count",
        "false_positive_count",
        "rejected_winner_count",
        "late_entry_count",
        "early_exit_count",
    )
    counts = {field: int(_first_number(contexts, (field,)) or 0) for field in fields}
    notes = _strings(_first_value(contexts, ("opportunity_leakage_notes",)))
    leakage_known = any(_first_value(contexts, (field,)) is not None for field in fields) or bool(notes)
    missed_opportunity_count = (
        counts["missed_valid_setups_count"]
        + counts["rejected_winner_count"]
        + counts["late_entry_count"]
        + counts["early_exit_count"]
    )
    blockers: list[str] = []
    if not leakage_known:
        blockers.append("missed_opportunity_leakage_unknown")
    elif missed_opportunity_count > 0:
        blockers.append("missed_opportunity_leakage_present")
    if counts["false_positive_count"] > 0:
        blockers.append("false_positive_review_needed")

    next_focus = "candidate_quality_improvement"
    if blockers:
        next_focus = "review_missed_opportunity_leakage"

    return {
        "leakage_known": leakage_known,
        "missed_opportunity_count": missed_opportunity_count,
        "false_positive_count": counts["false_positive_count"],
        "rejected_winner_count": counts["rejected_winner_count"],
        "late_entry_count": counts["late_entry_count"],
        "early_exit_count": counts["early_exit_count"],
        "opportunity_leakage_notes": notes,
        "leakage_blockers": blockers,
        "candidate_quality_next_focus": next_focus,
    }


def _resolve_evidence_status(
    *,
    missing_core_evidence: bool,
    sample_sufficient: bool,
    oos_sample_sufficient: bool,
    walk_forward_sufficient: bool,
    oos_stable: bool,
    regime_coverage_sufficient: bool,
    positive_expectancy: bool,
    profit_factor_sufficient: bool,
    drawdown_within_limit: bool,
    data_quality_sufficient: bool,
) -> str:
    if missing_core_evidence:
        return INCOMPLETE_INPUTS
    if not sample_sufficient or not oos_sample_sufficient:
        return BLOCKED_BY_SAMPLE_SIZE
    if not walk_forward_sufficient:
        return BLOCKED_BY_WALK_FORWARD
    if not oos_stable:
        return BLOCKED_BY_OOS_INSTABILITY
    if not regime_coverage_sufficient:
        return BLOCKED_BY_REGIME_COVERAGE
    if not positive_expectancy:
        return BLOCKED_BY_NEGATIVE_EXPECTANCY
    if not profit_factor_sufficient:
        return BLOCKED_BY_LOW_PROFIT_FACTOR
    if not drawdown_within_limit:
        return BLOCKED_BY_DRAWDOWN
    if not data_quality_sufficient:
        return BLOCKED_BY_DATA_QUALITY
    return SUFFICIENT_FOR_NEXT_PROFIT_LANE


def _promotion_readiness(
    *,
    evidence_status: str,
    sufficient_for_next_profit_lane: bool,
    sufficient_for_demo_candidate_review: bool,
    blocker_summary: Mapping[str, Any],
    missing_information: Sequence[str],
) -> dict[str, Any]:
    required = list(missing_information)
    required.extend(blocker_summary.get("all_blockers", []))
    if not required and sufficient_for_next_profit_lane:
        required = ["owner_review_of_sufficiency_packet"]
    return {
        "current_status": evidence_status,
        "next_review_lane": NEXT_LANE_ID,
        "can_promote_to_candidate_quality_improvement": sufficient_for_next_profit_lane,
        "can_promote_to_demo_candidate_review": sufficient_for_demo_candidate_review,
        "demo_execution_authorized": False,
        "live_execution_authorized": False,
        "promotion_blockers": list(blocker_summary.get("all_blockers", [])),
        "required_evidence_to_clear": _unique(required),
    }


def _blocker_summary(
    *,
    sample_blockers: Sequence[str],
    walk_forward_blockers: Sequence[str],
    oos_blockers: Sequence[str],
    regime_blockers: Sequence[str],
    profitability_blockers: Sequence[str],
    drawdown_blockers: Sequence[str],
    data_quality_blockers: Sequence[str],
    leakage_blockers: Sequence[str],
    threshold_blockers: Sequence[str],
) -> dict[str, list[str]]:
    all_blockers = _unique(
        [
            *sample_blockers,
            *walk_forward_blockers,
            *oos_blockers,
            *regime_blockers,
            *profitability_blockers,
            *drawdown_blockers,
            *data_quality_blockers,
            *leakage_blockers,
            *threshold_blockers,
        ]
    )
    return {
        "sample_blockers": list(sample_blockers),
        "walk_forward_blockers": list(walk_forward_blockers),
        "oos_blockers": list(oos_blockers),
        "regime_blockers": list(regime_blockers),
        "profitability_blockers": list(profitability_blockers),
        "drawdown_blockers": list(drawdown_blockers),
        "data_quality_blockers": list(data_quality_blockers),
        "leakage_blockers": list(leakage_blockers),
        "threshold_blockers": list(threshold_blockers),
        "all_blockers": all_blockers,
    }


def _critical_blockers(blocker_summary: Mapping[str, Sequence[str]]) -> list[str]:
    critical_keys = (
        "sample_blockers",
        "walk_forward_blockers",
        "oos_blockers",
        "regime_blockers",
        "profitability_blockers",
        "drawdown_blockers",
        "data_quality_blockers",
        "threshold_blockers",
    )
    blockers: list[str] = []
    for key in critical_keys:
        blockers.extend(blocker_summary.get(key, []))
    return _unique(blockers)


def _owner_action_queue(blocker_summary: Mapping[str, Sequence[str]], next_best_packet: str) -> list[dict[str, Any]]:
    actions = [
        ("REVIEW_SAMPLE_DEPTH", "Review sample depth", "high", blocker_summary.get("sample_blockers", [])),
        (
            "REVIEW_WALK_FORWARD_WINDOWS",
            "Review walk-forward windows",
            "high",
            blocker_summary.get("walk_forward_blockers", []),
        ),
        ("REVIEW_OOS_STABILITY", "Review out-of-sample stability", "high", blocker_summary.get("oos_blockers", [])),
        ("REVIEW_REGIME_COVERAGE", "Review regime coverage", "high", blocker_summary.get("regime_blockers", [])),
        (
            "REVIEW_EXPECTANCY_AND_PROFIT_FACTOR",
            "Review expectancy and profit factor",
            "high",
            blocker_summary.get("profitability_blockers", []),
        ),
        (
            "REVIEW_DRAWDOWN_AND_RISK_LIMITS",
            "Review drawdown and risk limits",
            "high",
            blocker_summary.get("drawdown_blockers", []),
        ),
        ("REVIEW_DATA_QUALITY", "Review data quality", "high", blocker_summary.get("data_quality_blockers", [])),
        (
            "REVIEW_MISSED_OPPORTUNITY_LEAKAGE",
            "Review missed-opportunity leakage",
            "medium",
            blocker_summary.get("leakage_blockers", []),
        ),
        ("REVIEW_NEXT_PROFIT_PACKET", f"Review next packet: {next_best_packet}", "medium", ["owner_review_required"]),
    ]
    return [_action(action_id, title, priority, blocked_by) for action_id, title, priority, blocked_by in actions]


def _action(action_id: str, title: str, priority: str, blocked_by: Sequence[str]) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "title": title,
        "priority": priority,
        "owner_decision_required": True,
        "execution_allowed": False,
        "safe_action": "Review sanitized evidence manually; no execution is allowed.",
        "blocked_by": list(blocked_by) or ["owner_review_required"],
    }


def _safe_manual_next_action(evidence_status: str) -> str:
    if evidence_status == SUFFICIENT_FOR_NEXT_PROFIT_LANE:
        return (
            "Owner may review the evidence sufficiency packet and queue profit candidate quality "
            "improvement. AIOS does not execute trades, access brokers, transfer funds, or use credentials."
        )
    if evidence_status == INCOMPLETE_INPUTS:
        return (
            "Provide sanitized strategy evaluation, walk-forward validation, profitability evaluation, "
            "and paper-session evidence, then rerun this evaluator."
        )
    return (
        "Collect the missing evidence, rerun the read-only sufficiency evaluator, and keep all trading, "
        "broker, bank, and money actions outside AIOS until owner approval."
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
        "title": "Candidate quality improvement packet",
        "status": "NEEDS_MORE_EVIDENCE",
        "priority": "high",
        "safe_packet_name": NEXT_PACKET_IF_SUFFICIENT,
    }


def _missing_information(source: Mapping[str, Any], contexts: Sequence[Mapping[str, Any]]) -> list[str]:
    if not source:
        return list(CORE_EVIDENCE_KEYS)
    missing: list[str] = []
    if not isinstance(source.get("strategy_evaluation"), Mapping) and _first_value(
        contexts,
        ("total_trades", "sample_count", "trade_count"),
    ) is None:
        missing.append("strategy_evaluation")
    if not isinstance(source.get("walk_forward_validation"), Mapping) and _first_value(
        contexts,
        ("walk_forward_windows", "windows", "window_results", "passed_windows"),
    ) is None:
        missing.append("walk_forward_validation")
    if not isinstance(source.get("profitability_evaluation"), Mapping) and _first_value(
        contexts,
        ("expectancy", "profit_factor", "gross_profit"),
    ) is None:
        missing.append("profitability_evaluation")
    has_paper_samples = bool(_sequence(source.get("paper_session_samples"))) or isinstance(
        source.get("paper_session_summary"),
        Mapping,
    )
    if not has_paper_samples and _first_value(contexts, ("trades", "paper_sessions")) is None:
        missing.append("paper_session_samples")
    return _unique(missing)


def _evidence_contexts(source: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    contexts: list[Mapping[str, Any]] = [source]
    for key in EVIDENCE_CONTEXT_KEYS:
        value = source.get(key)
        if isinstance(value, Mapping):
            contexts.append(value)
    for key in ("paper_session_samples", "paper_sessions", "trades"):
        value = source.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
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
                regime_name = _text(item.get("regime") or item.get("name") or item.get("regime_id"))
                if regime_name:
                    regimes.append(regime_name)
            else:
                text = _text(item)
                if text:
                    regimes.append(text)
    regime_results = _first_value(contexts, ("regime_results",))
    if isinstance(regime_results, Mapping):
        regimes.extend(str(key) for key in regime_results.keys() if str(key).strip())
    elif isinstance(regime_results, Sequence) and not isinstance(regime_results, (str, bytes, bytearray)):
        for item in regime_results:
            if isinstance(item, Mapping):
                regime_name = _text(item.get("regime") or item.get("name") or item.get("regime_id"))
                if regime_name:
                    regimes.append(regime_name)
    for regime_key in ("trend", "range", "volatile", "low_volatility", "high_spread", "news_blocked"):
        if _first_bool(contexts, (regime_key,)) is True:
            regimes.append(regime_key)
    return _unique(regimes)


def _first_drawdown_pct(contexts: Sequence[Mapping[str, Any]]) -> float | None:
    value = _first_number(contexts, ("max_drawdown_pct", "drawdown_pct"))
    if value is not None:
        return _normalize_rate(value)
    raw_drawdown = _first_number(contexts, ("max_drawdown",))
    if raw_drawdown is not None and 0 <= raw_drawdown <= 1:
        return raw_drawdown
    return None


def _drawdown_from_equity_curve(contexts: Sequence[Mapping[str, Any]]) -> float | None:
    curve = _first_sequence(contexts, ("equity_curve",))
    values = [_number(item) for item in curve]
    numeric_values = [item for item in values if item is not None]
    if len(numeric_values) < 2:
        return None
    peak = numeric_values[0]
    max_drawdown = 0.0
    for value in numeric_values:
        peak = max(peak, value)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - value) / peak)
    return max_drawdown


def _trade_count_from_sequences(contexts: Sequence[Mapping[str, Any]]) -> float | None:
    count = _trade_count_from_named_sequences(contexts, ("trades",))
    if count is not None:
        return count
    sessions = _first_sequence(contexts, ("paper_sessions", "paper_session_samples"))
    if not sessions:
        return None
    total = 0
    found = False
    for session in sessions:
        if isinstance(session, Mapping):
            session_count = _first_number([session], ("total_trades", "sample_count", "trade_count"))
            if session_count is None:
                session_count = _trade_count_from_named_sequences([session], ("trades",))
            if session_count is not None:
                total += int(session_count)
                found = True
    return float(total) if found else float(len(sessions))


def _trade_count_from_named_sequences(
    contexts: Sequence[Mapping[str, Any]],
    keys: Sequence[str],
) -> float | None:
    for key in keys:
        items = _first_sequence(contexts, (key,))
        if items:
            return float(len(items))
    return None


def _session_count(contexts: Sequence[Mapping[str, Any]]) -> int:
    session_count = _first_number(contexts, ("session_count",))
    if session_count is not None:
        return int(session_count)
    sessions = _first_sequence(contexts, ("paper_sessions", "paper_session_samples"))
    return len(sessions)


def _window_passed(window: Any) -> bool:
    if not isinstance(window, Mapping):
        return False
    status = _text(window.get("status") or window.get("result")).lower()
    if status in {"pass", "passed", "profitable", "win"}:
        return True
    if _bool(window.get("passed")) is True or _bool(window.get("profitable")) is True:
        return True
    pnl = _number(window.get("pnl") or window.get("total_pnl"))
    return pnl is not None and pnl > 0


def _first_value(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> Any:
    for context in contexts:
        for key in keys:
            if key in context and context.get(key) not in (None, ""):
                return context.get(key)
    return None


def _first_number(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _number(_first_value(contexts, keys))


def _first_text(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> str:
    return _text(_first_value(contexts, keys))


def _first_bool(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> bool | None:
    value = _first_value(contexts, keys)
    if value is None:
        return None
    return _bool(value)


def _first_sequence(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> list[Any]:
    value = _first_value(contexts, keys)
    return _sequence(value)


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
        return number / 100 if percent else number
    return None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "pass", "passed"}
    return bool(value)


def _normalize_rate(value: float | None) -> float | None:
    if value is None:
        return None
    return value / 100 if abs(value) > 1 else value


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value).strip()))


def _empty_evidence_depth_summary() -> dict[str, Any]:
    return {
        "total_trades": 0,
        "oos_trades": 0,
        "in_sample_trades": 0,
        "win_count": 0,
        "loss_count": 0,
        "breakeven_count": 0,
        "win_rate": None,
        "sample_count": 0,
        "session_count": 0,
    }


def _empty_sample_sufficiency_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "total_trades": 0,
        "required_total_trades": DEFAULT_THRESHOLDS["min_total_trades"],
        "oos_trades": 0,
        "required_oos_trades": DEFAULT_THRESHOLDS["min_oos_trades"],
        "sample_sufficient": False,
        "oos_sample_sufficient": False,
        "sample_blockers": list(blockers),
    }


def _empty_walk_forward_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "total_windows": 0,
        "required_windows": DEFAULT_THRESHOLDS["min_walk_forward_windows"],
        "profitable_windows": 0,
        "required_profitable_windows": DEFAULT_THRESHOLDS["min_profitable_windows"],
        "failed_windows": 0,
        "walk_forward_gate_cleared": False,
        "walk_forward_sufficient": False,
        "stability_score": None,
        "oos_pass_rate": None,
        "walk_forward_blockers": list(blockers),
    }


def _empty_oos_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "oos_trades": 0,
        "required_oos_trades": DEFAULT_THRESHOLDS["min_oos_trades"],
        "stability_score": None,
        "required_stability_score": DEFAULT_THRESHOLDS["min_candidate_stability_score"],
        "oos_pass_rate": None,
        "oos_stable": False,
        "oos_blockers": list(blockers),
    }


def _empty_regime_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "regime_count": 0,
        "required_regime_count": DEFAULT_THRESHOLDS["min_regime_count"],
        "covered_regimes": [],
        "regime_coverage_sufficient": False,
        "regime_blockers": list(blockers),
    }


def _empty_profitability_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "expectancy": None,
        "required_expectancy": DEFAULT_THRESHOLDS["min_expectancy"],
        "profit_factor": None,
        "required_profit_factor": DEFAULT_THRESHOLDS["min_profit_factor"],
        "positive_expectancy": False,
        "profit_factor_sufficient": False,
        "total_pnl": None,
        "gross_profit": None,
        "gross_loss": None,
        "candidate_status": "",
        "promotion_status": "",
        "profitability_blockers": list(blockers),
    }


def _empty_drawdown_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "max_drawdown_pct": None,
        "max_allowed_drawdown_pct": DEFAULT_THRESHOLDS["max_drawdown_pct"],
        "drawdown_within_limit": False,
        "daily_loss_stop_triggered": False,
        "risk_blocks": [],
        "drawdown_blockers": list(blockers),
    }


def _empty_leakage_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "leakage_known": False,
        "missed_opportunity_count": 0,
        "false_positive_count": 0,
        "rejected_winner_count": 0,
        "late_entry_count": 0,
        "early_exit_count": 0,
        "opportunity_leakage_notes": [],
        "leakage_blockers": list(blockers),
        "candidate_quality_next_focus": "review_missed_opportunity_leakage",
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
    "evaluate_evidence_depth_and_walk_forward_sufficiency_v1",
]
