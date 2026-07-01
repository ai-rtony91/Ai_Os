"""Govern portfolio risk and exposure for a multi-pair burst basket."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_multi_pair_opportunity_batch_v1 import (
    MULTI_PAIR_OPPORTUNITY_BATCH_READY,
)
from automation.forex_engine.forex_multi_pair_universe_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    _bool,
    _governed_requested,
    _int,
    _mapping,
    _number,
    banking_focus_blockers,
    build_common_result,
    sensitive_data_blockers,
)

SCHEMA = "AIOS_FOREX_BASKET_RISK_EXPOSURE_GOVERNOR_V1"
MODE = "READ_ONLY_METADATA_ONLY_BASKET_RISK_EXPOSURE_GOVERNOR"

BASKET_RISK_EXPOSURE_READY = "BASKET_RISK_EXPOSURE_READY"
BLOCKED_BY_EMPTY_BASKET = "BLOCKED_BY_EMPTY_BASKET"
BLOCKED_BY_PER_TRADE_RISK = "BLOCKED_BY_PER_TRADE_RISK"
BLOCKED_BY_TOTAL_BASKET_RISK = "BLOCKED_BY_TOTAL_BASKET_RISK"
BLOCKED_BY_CURRENCY_EXPOSURE = "BLOCKED_BY_CURRENCY_EXPOSURE"
BLOCKED_BY_CORRELATION = "BLOCKED_BY_CORRELATION"
BLOCKED_BY_MAX_OPEN_TRADES = "BLOCKED_BY_MAX_OPEN_TRADES"
BLOCKED_BY_DAILY_LOSS_STOP = "BLOCKED_BY_DAILY_LOSS_STOP"
BLOCKED_BY_KILL_SWITCH = "BLOCKED_BY_KILL_SWITCH"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_GOVERNED_MULTI_PAIR_BURST_VACATION_MODE_V1"

REQUIRED_POLICY_FIELDS = (
    "max_risk_per_trade_pct",
    "max_total_burst_risk_pct",
    "max_daily_loss_pct",
    "max_concurrent_open_trades",
    "max_candidates_per_burst",
    "max_same_currency_exposure_count",
    "correlation_gate_required",
    "correlation_within_limit",
    "currency_exposure_within_limit",
    "kill_switch_active",
    "daily_loss_stop_active",
    "one_burst_at_a_time",
    "next_burst_blocked_until_review",
)


def evaluate_forex_basket_risk_exposure_governor_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply per-trade and portfolio gates to a selected basket."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _risk_result(source, BLOCKED_BY_SENSITIVE_DATA, sensitive_blockers)
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _risk_result(source, BLOCKED_BY_BANKING_FOCUS, banking_blockers)

    batch_result = _mapping(source.get("opportunity_batch_result"))
    if batch_result.get("status") != MULTI_PAIR_OPPORTUNITY_BATCH_READY or batch_result.get("ready") is not True:
        return _risk_result(source, INCOMPLETE_INPUTS, ("opportunity_batch_result_not_ready",))

    selected = batch_result.get("selected_candidates")
    if not isinstance(selected, Sequence) or isinstance(selected, (str, bytes, bytearray)) or not selected:
        return _risk_result(source, BLOCKED_BY_EMPTY_BASKET, ("selected_candidates_empty",))

    policy = _mapping(source.get("risk_policy"))
    if not policy:
        return _risk_result(source, INCOMPLETE_INPUTS, ("risk_policy_missing",))
    missing = tuple(field for field in REQUIRED_POLICY_FIELDS if field not in policy)
    if missing:
        return _risk_result(source, INCOMPLETE_INPUTS, tuple(f"missing_{field}" for field in missing))

    max_risk_per_trade = _number(policy.get("max_risk_per_trade_pct"))
    max_total_burst = _number(policy.get("max_total_burst_risk_pct"))
    max_daily_loss = _number(policy.get("max_daily_loss_pct"))
    max_open = _int(policy.get("max_concurrent_open_trades"))
    max_candidates = _int(policy.get("max_candidates_per_burst"))
    max_currency = _int(policy.get("max_same_currency_exposure_count"))

    if max_risk_per_trade <= 0 or max_risk_per_trade > 0.01:
        return _risk_result(source, BLOCKED_BY_PER_TRADE_RISK, ("max_risk_per_trade_pct_above_limit",))
    if max_total_burst <= 0 or max_total_burst > 0.03:
        return _risk_result(source, BLOCKED_BY_TOTAL_BASKET_RISK, ("max_total_burst_risk_pct_above_limit",))
    if max_daily_loss <= 0 or max_daily_loss > 0.03:
        return _risk_result(source, BLOCKED_BY_DAILY_LOSS_STOP, ("max_daily_loss_pct_above_limit",))
    if _bool(policy.get("kill_switch_active")):
        return _risk_result(source, BLOCKED_BY_KILL_SWITCH, ("kill_switch_active_true",))
    if _bool(policy.get("daily_loss_stop_active")):
        return _risk_result(source, BLOCKED_BY_DAILY_LOSS_STOP, ("daily_loss_stop_active_true",))
    if len(selected) > max_candidates or len(selected) > max_open:
        return _risk_result(source, BLOCKED_BY_MAX_OPEN_TRADES, ("selected_count_exceeds_burst_or_open_trade_limit",))
    if not _bool(policy.get("correlation_gate_required")) or not _bool(policy.get("correlation_within_limit")):
        return _risk_result(source, BLOCKED_BY_CORRELATION, ("correlation_gate_not_clear",))
    if not _bool(policy.get("currency_exposure_within_limit")):
        return _risk_result(source, BLOCKED_BY_CURRENCY_EXPOSURE, ("currency_exposure_gate_not_clear",))
    if not _bool(policy.get("one_burst_at_a_time")) or not _bool(policy.get("next_burst_blocked_until_review")):
        return _risk_result(source, INCOMPLETE_INPUTS, ("burst_review_lock_metadata_not_ready",))

    approved_basket = [dict(item) for item in selected if isinstance(item, Mapping)]
    risk_values = [_number(item.get("risk_pct")) for item in approved_basket]
    if any(value <= 0 for value in risk_values):
        return _risk_result(source, BLOCKED_BY_PER_TRADE_RISK, ("candidate_risk_pct_missing",))
    if any(value > max_risk_per_trade for value in risk_values):
        return _risk_result(source, BLOCKED_BY_PER_TRADE_RISK, ("candidate_risk_pct_above_per_trade_limit",))

    total_risk = round(sum(risk_values), 6)
    if total_risk > max_total_burst:
        return _risk_result(source, BLOCKED_BY_TOTAL_BASKET_RISK, ("total_burst_risk_above_limit",))

    currency_summary = _currency_exposure_summary(approved_basket)
    if max_currency < 1 or any(count > max_currency for count in currency_summary["currency_counts"].values()):
        return _risk_result(source, BLOCKED_BY_CURRENCY_EXPOSURE, ("same_currency_exposure_above_limit",))

    extra = _risk_extra(
        approved_basket=approved_basket,
        total_burst_risk_pct=total_risk,
        selected_pair_count=len(approved_basket),
        currency_exposure_summary=currency_summary,
        correlation_summary={
            "correlation_gate_required": True,
            "correlation_within_limit": True,
        },
        ready_for_burst_permission=True,
    )
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=BASKET_RISK_EXPOSURE_READY,
        ready=True,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=True,
        blockers=(),
        next_best_packet="AIOS_FOREX_GOVERNED_BURST_PERMISSION_ENGINE_V1",
        safe_manual_next_action="Route approved basket into the governed burst permission engine.",
        extra=extra,
    )


def _currency_exposure_summary(basket: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for item in basket:
        pair = str(item.get("pair", ""))
        for part in pair.replace("/", "_").split("_"):
            if part:
                counts[part] = counts.get(part, 0) + 1
    return {"currency_counts": counts, "currency_exposure_gate": "METADATA_POLICY_PASSED"}


def _risk_result(source: Mapping[str, Any], status: str, blockers: Sequence[str]) -> dict[str, Any]:
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
        extra=_risk_extra(),
    )


def _risk_extra(
    *,
    approved_basket: Sequence[Mapping[str, Any]] = (),
    rejected_basket_summary: Mapping[str, Any] | None = None,
    total_burst_risk_pct: float = 0.0,
    selected_pair_count: int = 0,
    currency_exposure_summary: Mapping[str, Any] | None = None,
    correlation_summary: Mapping[str, Any] | None = None,
    ready_for_burst_permission: bool = False,
) -> dict[str, Any]:
    return {
        "approved_basket": [dict(item) for item in approved_basket],
        "rejected_basket_summary": dict(rejected_basket_summary or {}),
        "total_burst_risk_pct": total_burst_risk_pct,
        "selected_pair_count": selected_pair_count,
        "currency_exposure_summary": dict(currency_exposure_summary or {}),
        "correlation_summary": dict(correlation_summary or {}),
        "ready_for_burst_permission": ready_for_burst_permission,
    }


def _safe_manual_next_action(status: str) -> str:
    if status == BLOCKED_BY_EMPTY_BASKET:
        return "Provide selected candidates before basket risk review."
    if status == BLOCKED_BY_PER_TRADE_RISK:
        return "Lower per-trade risk or repair missing risk_pct metadata."
    if status == BLOCKED_BY_TOTAL_BASKET_RISK:
        return "Reduce total burst risk before permission review."
    if status == BLOCKED_BY_CURRENCY_EXPOSURE:
        return "Reduce same-currency exposure or repair exposure metadata."
    if status == BLOCKED_BY_CORRELATION:
        return "Resolve correlation gate evidence before basket approval."
    if status == BLOCKED_BY_MAX_OPEN_TRADES:
        return "Reduce candidate count to max burst and open-trade limits."
    if status == BLOCKED_BY_KILL_SWITCH:
        return "Clear kill switch before any burst permission review."
    if status == BLOCKED_BY_DAILY_LOSS_STOP:
        return "Clear daily loss stop and daily risk limits first."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, or money-movement focus fields."
    return "Provide complete basket risk policy metadata."
