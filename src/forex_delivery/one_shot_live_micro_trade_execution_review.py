"""Final non-executing one-shot live micro-trade execution review.

This module evaluates sanitized evidence only. It does not read secrets, call a
broker, place orders, or close trades.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.forex_delivery.read_only_evidence_approval import (
    build_read_only_evidence_approval_model,
)


SCHEMA = "AIOS_FOREX_ONE_SHOT_LIVE_MICRO_TRADE_EXECUTION_REVIEW.v1"
REQUIRED_HUMAN_PHRASE = (
    "I AUTHORIZE ONE LIVE MICRO TRADE EXECUTION WITH MAXIMUM MICRO RISK"
)
ARMING_REQUIRED_HUMAN_PHRASE = (
    "I AUTHORIZE ONE LIVE MICRO TRADE DRY-RUN ARMING REVIEW"
)
NEXT_PACKET_CANDIDATE = "AIOS-FOREX-ONE-SHOT-LIVE-MICRO-TRADE-EXECUTION-V1"

READ_ONLY_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_DRY_RUN_V1.md"
)
PAPER_LOOP_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md"
)
ARMING_GATE_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_TRADE_ARMING_GATE_DRY_RUN_V1.md"
)
EXECUTION_REVIEW_EVIDENCE_PATH = Path(
    "Reports/forex_delivery/"
    "AIOS_FOREX_ONE_SHOT_LIVE_MICRO_TRADE_EXECUTION_REVIEW_DRY_RUN_V1.md"
)

DEFAULT_SELECTED_PAIR = "EUR_USD"
DEFAULT_PROPOSED_SIDE = "NONE"
DEFAULT_PROPOSED_UNITS = 1
DEFAULT_MAX_TRADE_RISK = 1.0
DEFAULT_DAILY_LOSS_CAP = 5.0


def build_one_shot_live_micro_trade_execution_review_result(
    *,
    repo_root: Path | None = None,
    read_only_evidence: Mapping[str, Any] | None = None,
    paper_loop_evidence: Mapping[str, Any] | None = None,
    arming_gate_evidence: Mapping[str, Any] | None = None,
    future_execution_phrase: str | None = None,
    generated_at_utc: str | None = None,
    evidence_path: str | None = None,
) -> dict[str, Any]:
    """Build the sanitized execution review result.

    The review is intentionally non-executing. Even when evidence is present,
    this result never permits live execution.
    """

    root = repo_root or Path(__file__).resolve().parents[2]
    read_only_model = (
        dict(read_only_evidence)
        if read_only_evidence is not None
        else load_evidence_model(root / READ_ONLY_EVIDENCE_PATH)
    )
    paper_model = (
        dict(paper_loop_evidence)
        if paper_loop_evidence is not None
        else load_evidence_model(root / PAPER_LOOP_EVIDENCE_PATH)
    )
    arming_model = (
        dict(arming_gate_evidence)
        if arming_gate_evidence is not None
        else load_evidence_model(root / ARMING_GATE_EVIDENCE_PATH)
    )

    read_only_status = evaluate_read_only_bridge_evidence(read_only_model)
    paper_status = evaluate_paper_loop_evidence(paper_model)
    arming_status = evaluate_arming_gate_evidence(arming_model)

    selected_pair = normalize_pair(
        first_present(
            paper_model,
            "selected_pair",
            "pair",
            default=first_present(read_only_model, "selected_pair", "pair", default=DEFAULT_SELECTED_PAIR),
        )
    )
    proposed_side = normalize_side(
        first_present(paper_model, "signal_side", "side", default=DEFAULT_PROPOSED_SIDE)
    )
    max_units = resolve_max_live_micro_units(arming_model)
    proposed_units = resolve_proposed_live_micro_units(max_units)
    max_trade_risk = coerce_float(
        first_present(
            paper_model,
            "max_trade_risk",
            "max_paper_trade_risk",
            default=DEFAULT_MAX_TRADE_RISK,
        ),
        DEFAULT_MAX_TRADE_RISK,
    )

    risk_status = evaluate_final_risk_requirements(
        read_only_status=read_only_status,
        paper_status=paper_status,
        proposed_units=proposed_units,
        max_units=max_units,
        max_trade_risk=max_trade_risk,
    )
    exit_status = evaluate_final_exit_requirements(paper_model)
    history_status = evaluate_trading_history_writeback(
        read_only_status=read_only_status,
        paper_status=paper_status,
    )
    human_status = evaluate_future_execution_phrase(future_execution_phrase)

    evidence_present = unique(
        read_only_status["evidence_present"]
        + paper_status["evidence_present"]
        + arming_status["evidence_present"]
        + risk_status["evidence_present"]
        + exit_status["evidence_present"]
        + history_status["evidence_present"]
        + human_status["evidence_present"]
    )
    evidence_missing = unique(
        read_only_status["evidence_missing"]
        + paper_status["evidence_missing"]
        + arming_status["evidence_missing"]
        + risk_status["evidence_missing"]
        + exit_status["evidence_missing"]
        + history_status["evidence_missing"]
        + human_status["evidence_missing"]
    )
    blocked_reasons = unique(
        read_only_status["blocked_reasons"]
        + paper_status["blocked_reasons"]
        + arming_status["blocked_reasons"]
        + risk_status["blocked_reasons"]
        + exit_status["blocked_reasons"]
        + history_status["blocked_reasons"]
        + human_status["blocked_reasons"]
        + ["execution_review_packet_is_not_an_execution_packet"]
    )

    execution_review_ready = False
    if not blocked_reasons and future_execution_phrase == REQUIRED_HUMAN_PHRASE:
        # Kept explicit for traceability; this packet still does not execute.
        execution_review_ready = True

    result = {
        "schema": SCHEMA,
        "EXECUTION_REVIEW_READY": execution_review_ready,
        "live_execution_allowed": False,
        "live_trade_placed": False,
        "selected_pair": selected_pair,
        "proposed_side": proposed_side,
        "proposed_units": proposed_units,
        "max_units": max_units,
        "max_trade_risk": max_trade_risk,
        "required_human_phrase": REQUIRED_HUMAN_PHRASE,
        "next_packet_candidate": NEXT_PACKET_CANDIDATE,
        "evidence_present": evidence_present,
        "evidence_missing": evidence_missing,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action(execution_review_ready),
        "read_only_bridge_status": read_only_status,
        "paper_loop_status": paper_status,
        "arming_gate_status": arming_status,
        "risk_gate_status": risk_status,
        "exit_plan_status": exit_status,
        "trading_history_writeback_status": history_status,
        "no_secret_status": "PASS_NO_SECRET_VALUES_RECORDED",
        "no_account_id_status": "PASS_NO_ACCOUNT_IDENTIFIER_VALUES_RECORDED",
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
        "generated_at_utc": generated_at_utc or utc_now_iso(),
        "evidence_path": evidence_path or str(EXECUTION_REVIEW_EVIDENCE_PATH),
    }
    assert_execution_review_sanitized(result)
    return result


def evaluate_read_only_bridge_evidence(model: Mapping[str, Any]) -> dict[str, Any]:
    approval = build_read_only_evidence_approval_model(model)
    if approval.get("READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW") is True:
        blockers = []
        if approval.get("trading_history_available") is not True:
            blockers.append("real_trading_history_unavailable_or_blocked")
        return {
            "status": "PRESENT_BLOCKED" if blockers else "PRESENT",
            "source_type": str(approval.get("source_type", "")).upper(),
            "source_label": approval.get("source_label"),
            "freshness_utc": approval.get("freshness_utc"),
            "live_trading_allowed_from_this_data": False,
            "broker_account_reachable": approval.get("broker_account_reachable") is True,
            "open_positions_reconciled": approval.get("open_positions_reconciled") is True,
            "open_position_count": approval.get("open_position_count", 0),
            "account_pl_available": approval.get("account_pl_available") is True,
            "daily_pl_available": approval.get("daily_pl_available") is True,
            "daily_pl_block_reason": approval.get("daily_pl_block_reason"),
            "realized_pl_available": approval.get("realized_pl_available") is True,
            "unrealized_pl_available": approval.get("unrealized_pl_available") is True,
            "margin_risk_available": approval.get("margin_risk_available") is True,
            "trading_history_available": approval.get("trading_history_available") is True,
            "trading_history_writeback_verified": approval.get(
                "trading_history_writeback_verified"
            )
            is True,
            "trading_history_evidence_path": approval.get("trading_history_evidence_path"),
            "trading_history_block_reason": str(approval.get("block_reason", "NONE")),
            "evidence_present": ["read_only_evidence_approved_for_future_live_review"]
            + list(approval.get("evidence_present") or []),
            "evidence_missing": list(approval.get("evidence_missing") or []),
            "blocked_reasons": unique(blockers),
            "read_only_evidence_approval": approval,
        }

    present: list[str] = []
    missing: list[str] = []
    blockers: list[str] = []

    if not model:
        return status_block(
            "MISSING",
            missing=["read_only_live_data_bridge_evidence_report"],
            blockers=["read_only_live_data_bridge_evidence_report_missing"],
        )

    present.append("read_only_live_data_bridge_evidence_report")
    source_type = lower_text(
        first_present_nested(
            model,
            "source_type",
            "market.source_type",
            "execution_readiness.source_type",
            default="UNKNOWN",
        )
    )
    source_label = str(
        first_present_nested(
            model,
            "source_label",
            "market.source_label",
            "execution_readiness.source_label",
            default="UNKNOWN",
        )
    )
    freshness = first_present_nested(
        model,
        "freshness_utc",
        "market.freshness_utc",
        "generated_at_utc",
        "execution_readiness.freshness_utc",
    )
    live_from_data = coerce_bool(
        first_present_nested(
            model,
            "live_trading_allowed_from_this_data",
            "market.live_trading_allowed_from_this_data",
            "execution_readiness.live_trading_allowed_from_this_data",
            default=False,
        )
    )
    broker_reachable = first_present_nested(
        model,
        "broker_state.account_reachable",
        "broker_state.reachable",
        "account_reachable",
        "broker_reachable",
    )
    positions_reconciled = first_present_nested(
        model,
        "broker_state.open_positions_reconciled",
        "positions.open_positions_reconciled",
        "open_positions_reconciled",
        "positions_reconciled",
    )
    daily_pl_available = first_present_nested(
        model,
        "broker_state.daily_pl_ledger_available",
        "risk_pl.daily_pl_ledger_available",
        "daily_pl_ledger_available",
        "daily_pl.available",
    )
    realized_pl = first_present_nested(
        model,
        "broker_state.realized_pl",
        "risk_pl.realized_pl",
        "realized_pl",
    )
    unrealized_pl = first_present_nested(
        model,
        "broker_state.unrealized_pl",
        "risk_pl.unrealized_pl",
        "unrealized_pl",
    )
    account_pl_available = is_available_value(realized_pl) or is_available_value(
        unrealized_pl
    )
    daily_pl_block_reason = (
        "NONE"
        if coerce_bool(daily_pl_available)
        else "daily P/L ledger not verified"
    )
    trading_history_available = first_present_nested(
        model,
        "trading_history.available",
        "trading_history.trading_history_available",
        "trading_history_available",
        "history_writeback_available",
    )
    trading_history_block_reason = first_present_nested(
        model,
        "trading_history.block_reason",
        "trading_history_block_reason",
        default="not_provided",
    )

    if source_type != "unknown":
        present.append("read_only_source_type_present")
    else:
        missing.append("read_only_source_type")
    if source_label != "UNKNOWN":
        present.append("read_only_source_label_present")
    else:
        missing.append("read_only_source_label")
    if freshness:
        present.append("read_only_freshness_present")
    else:
        missing.append("read_only_freshness")

    if source_type == "fixture" or "FIXTURE" in source_label.upper():
        blockers.append("read_only_bridge_fixture_source_not_live_permitted")
    if not live_from_data:
        blockers.append("read_only_data_not_approved_for_future_live_execution")

    if broker_reachable is None:
        missing.append("broker_account_reachability")
    elif coerce_bool(broker_reachable):
        present.append("broker_account_reachable")
    else:
        blockers.append("broker_account_not_reachable_in_read_only_evidence")

    if positions_reconciled is None:
        missing.append("open_positions_reconciliation")
    elif coerce_bool(positions_reconciled):
        present.append("open_positions_reconciled")
    else:
        blockers.append("open_positions_not_reconciled_in_read_only_evidence")

    if daily_pl_available is None:
        missing.append("daily_pl_availability")
    elif coerce_bool(daily_pl_available):
        present.append("daily_pl_available")
    else:
        blockers.append("daily_pl_not_available_in_read_only_evidence")
        if account_pl_available:
            present.append("account_pl_available")

    if trading_history_available is None:
        missing.append("trading_history_availability")
    elif coerce_bool(trading_history_available):
        present.append("real_trading_history_available")
    else:
        blockers.append("real_trading_history_unavailable_or_blocked")

    return {
        "status": "PRESENT_BLOCKED" if blockers else "PRESENT",
        "source_type": source_type.upper(),
        "source_label": source_label,
        "freshness_utc": freshness or "MISSING",
        "live_trading_allowed_from_this_data": live_from_data,
        "broker_account_reachable": bool(coerce_bool(broker_reachable)),
        "open_positions_reconciled": bool(coerce_bool(positions_reconciled)),
        "account_pl_available": account_pl_available,
        "daily_pl_available": bool(coerce_bool(daily_pl_available)),
        "daily_pl_block_reason": daily_pl_block_reason,
        "trading_history_available": bool(coerce_bool(trading_history_available)),
        "trading_history_writeback_verified": False,
        "trading_history_evidence_path": "MISSING",
        "trading_history_block_reason": str(trading_history_block_reason),
        "evidence_present": present,
        "evidence_missing": unique(missing),
        "blocked_reasons": unique(blockers),
    }


def evaluate_paper_loop_evidence(model: Mapping[str, Any]) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    blockers: list[str] = []

    if not model:
        return status_block(
            "MISSING",
            missing=["paper_signal_execution_loop_evidence_report"],
            blockers=["paper_signal_execution_loop_evidence_report_missing"],
        )

    present.append("paper_signal_execution_loop_evidence_report")
    side = normalize_side(first_present(model, "signal_side", "side", default="NONE"))
    risk_approved = coerce_bool(
        first_present(model, "risk_approval", "risk_approved", default=False)
    )
    entry_created = coerce_bool(
        first_present(model, "paper_entry_created", "entry_created", default=False)
    )
    exit_plan_status = upper_text(
        first_present(model, "exit_plan_status", "exit_plan_ready", default="MISSING")
    )
    close_reconciled = coerce_bool(
        first_present(
            model,
            "paper_close_reconcile",
            "paper_close_reconciled",
            "paper_reconcile_completed",
            default=False,
        )
    )
    realized_pl = first_present(
        model, "realized_paper_pl", "realized_pl", "paper_realized_pl"
    )
    history_written = coerce_bool(
        first_present(
            model,
            "trading_history_row_written",
            "history_row_written",
            default=False,
        )
    )
    live_allowed = coerce_bool(
        first_present(model, "live_execution_allowed", default=False)
    )

    if side in {"BUY", "SELL", "NONE"}:
        present.append("paper_signal_side_recorded")
    else:
        missing.append("paper_signal_side")
        blockers.append("paper_signal_side_invalid_or_missing")

    if risk_approved:
        present.append("paper_risk_gate_approved")
    else:
        blockers.append("paper_risk_gate_not_approved")

    if entry_created:
        present.append("paper_entry_created")
    else:
        blockers.append("paper_entry_not_created")

    if exit_plan_status in {"READY", "PRESENT", "TRUE"}:
        present.append("paper_exit_plan_present")
    else:
        blockers.append("paper_exit_plan_missing_or_not_ready")

    if close_reconciled:
        present.append("paper_close_reconcile_completed")
    else:
        blockers.append("paper_close_reconcile_not_completed")

    if realized_pl is not None:
        present.append("paper_pl_recorded")
    else:
        missing.append("realized_paper_pl")
        blockers.append("paper_pl_not_recorded")

    if history_written:
        present.append("paper_trading_history_row_written")
    else:
        blockers.append("paper_trading_history_row_not_written")

    if live_allowed:
        blockers.append("paper_loop_live_execution_allowed_must_remain_false")
    else:
        present.append("paper_loop_live_execution_allowed_false")

    return {
        "status": "PRESENT_BLOCKED" if blockers else "PRESENT",
        "signal_side": side,
        "risk_approved": risk_approved,
        "paper_entry_created": entry_created,
        "exit_plan_status": exit_plan_status,
        "paper_close_reconcile_completed": close_reconciled,
        "realized_paper_pl": realized_pl,
        "trading_history_row_written": history_written,
        "live_execution_allowed": False,
        "evidence_present": present,
        "evidence_missing": unique(missing),
        "blocked_reasons": unique(blockers),
    }


def evaluate_arming_gate_evidence(model: Mapping[str, Any]) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    blockers: list[str] = []

    if not model:
        return status_block(
            "MISSING",
            missing=["live_micro_trade_arming_gate_evidence_report"],
            blockers=["live_micro_trade_arming_gate_evidence_report_missing"],
        )

    present.append("live_micro_trade_arming_gate_evidence_report")
    live_armable = coerce_bool(first_present(model, "LIVE_ARMABLE", default=False))
    phrase = str(first_present(model, "required_human_phrase", default=""))
    live_allowed = coerce_bool(
        first_present(model, "live_execution_allowed", default=False)
    )
    broker_writes = coerce_bool(
        first_present(model, "broker_write_calls_allowed", default=False)
    )
    order_allowed = coerce_bool(
        first_present(model, "order_placement_allowed", default=False)
    )
    close_allowed = coerce_bool(first_present(model, "close_trade_allowed", default=False))

    present.append("live_armable_value_read")
    if not live_armable:
        blockers.append("live_micro_trade_arming_gate_not_armable")

    if phrase == ARMING_REQUIRED_HUMAN_PHRASE:
        present.append("arming_required_phrase_documented")
    else:
        missing.append("arming_required_human_phrase")
        blockers.append("arming_required_human_phrase_not_documented")

    if live_allowed:
        blockers.append("arming_gate_live_execution_allowed_must_remain_false")
    else:
        present.append("arming_gate_live_execution_allowed_false")
    if broker_writes:
        blockers.append("arming_gate_broker_write_calls_must_remain_false")
    else:
        present.append("arming_gate_broker_write_calls_false")
    if order_allowed:
        blockers.append("arming_gate_order_placement_must_remain_false")
    else:
        present.append("arming_gate_order_placement_false")
    if close_allowed:
        blockers.append("arming_gate_close_trade_must_remain_false")
    else:
        present.append("arming_gate_close_trade_false")

    return {
        "status": "PRESENT_BLOCKED" if blockers else "PRESENT",
        "LIVE_ARMABLE": live_armable,
        "required_human_phrase_documented": phrase == ARMING_REQUIRED_HUMAN_PHRASE,
        "live_execution_allowed": False,
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
        "evidence_present": present,
        "evidence_missing": unique(missing),
        "blocked_reasons": unique(blockers),
    }


def evaluate_final_risk_requirements(
    *,
    read_only_status: Mapping[str, Any],
    paper_status: Mapping[str, Any],
    proposed_units: int,
    max_units: int,
    max_trade_risk: float,
) -> dict[str, Any]:
    present: list[str] = []
    blockers: list[str] = []

    if proposed_units <= max_units <= DEFAULT_PROPOSED_UNITS:
        present.append("micro_sized_max_units")
    else:
        blockers.append("proposed_units_exceed_micro_trade_limit")

    if max_trade_risk > 0:
        present.append("max_trade_risk_present")
    else:
        blockers.append("max_trade_risk_missing")

    present.extend(
        [
            "daily_loss_cap_present",
            "one_position_rule_required",
            "no_duplicate_entry_rule_required",
            "no_revenge_loop_rule_required",
            "kill_switch_required",
        ]
    )

    if coerce_bool(read_only_status.get("open_positions_reconciled")):
        present.append("open_live_position_state_reconciled")
    else:
        blockers.append("open_live_position_state_not_reconciled")

    if coerce_bool(paper_status.get("risk_approved")):
        present.append("paper_risk_approval_observed")
    else:
        blockers.append("paper_risk_approval_missing")

    return {
        "status": "PRESENT_BLOCKED" if blockers else "PRESENT",
        "max_units": max_units,
        "max_trade_risk": max_trade_risk,
        "daily_loss_cap": DEFAULT_DAILY_LOSS_CAP,
        "one_position_rule": True,
        "no_duplicate_entry_rule": True,
        "no_revenge_loop_rule": True,
        "kill_switch_required": True,
        "risk_governor_approval": not blockers,
        "evidence_present": present,
        "evidence_missing": [],
        "blocked_reasons": unique(blockers),
    }


def evaluate_final_exit_requirements(model: Mapping[str, Any]) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    blockers: list[str] = []

    stop_loss = first_present(
        model,
        "stop_loss_policy",
        "stop_loss_required",
        default="MISSING",
    )
    take_profit = first_present(
        model,
        "take_profit_policy",
        "take_profit_or_waiver",
        default="MISSING",
    )
    max_time = first_present(model, "max_time_policy", default="MISSING")
    manual_fallback = first_present(
        model,
        "manual_close_fallback",
        "manual_broker_ui_fallback",
        default="MISSING",
    )

    if has_policy(stop_loss):
        present.append("stop_loss_required_before_or_with_entry")
    else:
        missing.append("stop_loss_policy")
        blockers.append("stop_loss_policy_missing")

    if has_policy(take_profit) or "WAIVED" in upper_text(take_profit):
        present.append("take_profit_policy_or_explicit_waiver_present")
    else:
        missing.append("take_profit_policy_or_explicit_waiver")
        blockers.append("take_profit_policy_or_explicit_waiver_missing")

    if has_policy(max_time):
        present.append("max_time_policy_present")
    else:
        missing.append("max_time_policy")
        blockers.append("max_time_policy_missing")

    if has_policy(manual_fallback):
        present.append("manual_broker_ui_fallback_required")
    else:
        missing.append("manual_broker_ui_fallback")
        blockers.append("manual_broker_ui_fallback_missing")

    blockers.append("auto_exit_readiness_not_implemented_for_live_execution")

    return {
        "status": "PRESENT_BLOCKED" if blockers else "PRESENT",
        "stop_loss_required_before_or_with_entry": has_policy(stop_loss),
        "take_profit_policy_or_waiver": str(take_profit),
        "max_time_policy": str(max_time),
        "manual_broker_ui_fallback_required": has_policy(manual_fallback),
        "auto_exit_readiness": False,
        "evidence_present": present,
        "evidence_missing": unique(missing),
        "blocked_reasons": unique(blockers),
    }


def evaluate_trading_history_writeback(
    *,
    read_only_status: Mapping[str, Any],
    paper_status: Mapping[str, Any],
) -> dict[str, Any]:
    present: list[str] = []
    blockers: list[str] = []

    if coerce_bool(paper_status.get("trading_history_row_written")):
        present.append("paper_trading_history_writeback_observed")
    else:
        blockers.append("paper_trading_history_writeback_missing")

    if coerce_bool(read_only_status.get("trading_history_writeback_verified")):
        present.append("real_trading_history_writeback_verified")
    else:
        blockers.append("real_trading_history_writeback_not_verified")

    return {
        "status": "PRESENT_BLOCKED" if blockers else "PRESENT",
        "paper_history_writeback": coerce_bool(
            paper_status.get("trading_history_row_written")
        ),
        "real_history_available": coerce_bool(
            read_only_status.get("trading_history_available")
        ),
        "real_history_writeback_verified": coerce_bool(
            read_only_status.get("trading_history_writeback_verified")
        ),
        "evidence_present": present,
        "evidence_missing": [],
        "blocked_reasons": unique(blockers),
    }


def evaluate_future_execution_phrase(phrase: str | None) -> dict[str, Any]:
    if phrase == REQUIRED_HUMAN_PHRASE:
        return {
            "status": "PRESENT",
            "evidence_present": ["future_execution_human_phrase_present"],
            "evidence_missing": [],
            "blocked_reasons": [],
        }
    return {
        "status": "MISSING",
        "evidence_present": ["required_future_execution_phrase_documented"],
        "evidence_missing": ["future_execution_human_phrase"],
        "blocked_reasons": ["future_execution_human_phrase_not_provided"],
    }


def resolve_max_live_micro_units(arming_model: Mapping[str, Any]) -> int:
    max_units = coerce_int(
        first_present_nested(
            arming_model,
            "max_units",
            "risk_gate_status.max_units",
            default=DEFAULT_PROPOSED_UNITS,
        ),
        DEFAULT_PROPOSED_UNITS,
    )
    if max_units < 0:
        return 0
    return min(max_units, DEFAULT_PROPOSED_UNITS)


def resolve_proposed_live_micro_units(max_units: int) -> int:
    if max_units < DEFAULT_PROPOSED_UNITS:
        return max_units
    return DEFAULT_PROPOSED_UNITS


def build_sanitized_report(result: Mapping[str, Any]) -> str:
    assert_execution_review_sanitized(result)
    summary = {
        "EXECUTION_REVIEW_READY": result.get("EXECUTION_REVIEW_READY"),
        "live_execution_allowed": result.get("live_execution_allowed"),
        "live_trade_placed": result.get("live_trade_placed"),
        "selected_pair": result.get("selected_pair"),
        "proposed_side": result.get("proposed_side"),
        "proposed_units": result.get("proposed_units"),
        "required_human_phrase": result.get("required_human_phrase"),
        "next_packet_candidate": result.get("next_packet_candidate"),
        "blocked_reasons": result.get("blocked_reasons", []),
        "next_safe_action": result.get("next_safe_action"),
        "broker_write_calls_allowed": result.get("broker_write_calls_allowed"),
        "order_placement_allowed": result.get("order_placement_allowed"),
        "close_trade_allowed": result.get("close_trade_allowed"),
        "generated_at_utc": result.get("generated_at_utc"),
        "evidence_path": result.get("evidence_path"),
    }
    evidence_present = "\n".join(
        f"- {item}" for item in result.get("evidence_present", [])
    ) or "- none"
    evidence_missing = "\n".join(
        f"- {item}" for item in result.get("evidence_missing", [])
    ) or "- none"
    blockers = "\n".join(f"- {item}" for item in result.get("blocked_reasons", [])) or "- none"

    return (
        "# AIOS Forex One-Shot Live Micro-Trade Execution Review Dry Run V1\n\n"
        "## Execution Review Status\n"
        f"- EXECUTION_REVIEW_READY: {result.get('EXECUTION_REVIEW_READY')}\n"
        f"- live_execution_allowed: {result.get('live_execution_allowed')}\n"
        f"- live_trade_placed: {result.get('live_trade_placed')}\n"
        f"- selected_pair: {result.get('selected_pair')}\n"
        f"- proposed_side: {result.get('proposed_side')}\n"
        f"- proposed_units: {result.get('proposed_units')}\n"
        f"- max_trade_risk: {result.get('max_trade_risk')}\n\n"
        "## Evidence Present\n"
        f"{evidence_present}\n\n"
        "## Evidence Missing\n"
        f"{evidence_missing}\n\n"
        "## Blockers\n"
        f"{blockers}\n\n"
        "## Required Human Phrase For A Future Execution Packet\n"
        f"{REQUIRED_HUMAN_PHRASE}\n\n"
        "## Next Packet Candidate\n"
        f"{NEXT_PACKET_CANDIDATE}\n\n"
        "## Next Safe Action\n"
        f"{result.get('next_safe_action')}\n\n"
        "## Explicit Safety Confirmations\n"
        "- No live trade was placed.\n"
        "- No broker write calls were made.\n"
        "- No secrets, account identifier values, broker order identifier values, "
        "or transaction identifier values were recorded.\n"
        "- Profitability is not guaranteed; any future packet must remain "
        "risk-governed and evidence-based.\n\n"
        "## Sanitized JSON Summary\n"
        "```json\n"
        f"{json.dumps(summary, indent=2, sort_keys=True)}\n"
        "```\n"
    )


def write_one_shot_live_micro_trade_execution_review_report(
    result: Mapping[str, Any], *, repo_root: Path | None = None
) -> Path:
    root = repo_root or Path(__file__).resolve().parents[2]
    report_path = root / EXECUTION_REVIEW_EVIDENCE_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    assert_execution_review_sanitized(result)
    report_path.write_text(build_sanitized_report(result), encoding="utf-8")
    return report_path


def cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    assert_execution_review_sanitized(result)
    return {
        "schema": result.get("schema"),
        "EXECUTION_REVIEW_READY": result.get("EXECUTION_REVIEW_READY"),
        "live_execution_allowed": result.get("live_execution_allowed"),
        "live_trade_placed": result.get("live_trade_placed"),
        "selected_pair": result.get("selected_pair"),
        "proposed_side": result.get("proposed_side"),
        "proposed_units": result.get("proposed_units"),
        "required_human_phrase": result.get("required_human_phrase"),
        "next_packet_candidate": result.get("next_packet_candidate"),
        "blocked_reasons": result.get("blocked_reasons", []),
        "next_safe_action": result.get("next_safe_action"),
        "evidence_path": result.get("evidence_path"),
    }


def load_evidence_model(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    json_blocks = []
    parts = text.split("```")
    for index, part in enumerate(parts):
        if index % 2 == 1:
            block = part.removeprefix("json").strip()
            json_blocks.append(block)
    for block in reversed(json_blocks):
        try:
            loaded = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            return loaded
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        return parse_markdown_key_values(text)
    return loaded if isinstance(loaded, dict) else {}


def parse_markdown_key_values(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        normalized_key = key.strip().replace(" ", "_")
        parsed[normalized_key] = parse_scalar(value.strip())
    return parsed


def assert_execution_review_sanitized(payload: Mapping[str, Any]) -> None:
    text = json.dumps(payload, sort_keys=True)
    forbidden_markers = (
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
        "Authorization",
        "Bearer ",
        "accountID",
        "account_id_value",
        "orderID",
        "order_id_value",
        "transactionID",
        "transaction_id_value",
        "rawBroker",
    )
    for marker in forbidden_markers:
        if marker in text:
            raise ValueError(f"Unsafe identifier or secret marker present: {marker}")
    forced_false_fields = (
        "live_execution_allowed",
        "live_trade_placed",
        "broker_write_calls_allowed",
        "order_placement_allowed",
        "close_trade_allowed",
    )
    for field in forced_false_fields:
        if payload.get(field) is not False:
            raise ValueError(f"{field} must remain false in execution review")


def next_safe_action(execution_review_ready: bool) -> str:
    if execution_review_ready:
        return (
            "Stop. Do not execute from this packet; require a separately approved "
            "one-shot execution packet before any live micro-trade can be considered."
        )
    return (
        "Do not execute. Resolve blocked evidence, refresh sanitized read-only "
        "bridge and paper evidence, review arming status, and require separate "
        "Human Owner approval before any future execution packet."
    )


def status_block(
    status: str, *, missing: list[str], blockers: list[str]
) -> dict[str, Any]:
    return {
        "status": status,
        "evidence_present": [],
        "evidence_missing": missing,
        "blocked_reasons": blockers,
    }


def first_present(
    model: Mapping[str, Any], *names: str, default: Any = None
) -> Any:
    for name in names:
        if name in model and model[name] is not None:
            return model[name]
    return default


def first_present_nested(
    model: Mapping[str, Any], *paths: str, default: Any = None
) -> Any:
    for path in paths:
        value = nested_value(model, path)
        if value is not None:
            return value
    return default


def nested_value(model: Mapping[str, Any], path: str) -> Any:
    current: Any = model
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"none", "null"}:
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ready", "present"}
    return bool(value)


def coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_pair(value: Any) -> str:
    text = str(value or DEFAULT_SELECTED_PAIR).upper().replace("/", "_").replace("-", "_")
    return text if text else DEFAULT_SELECTED_PAIR


def normalize_side(value: Any) -> str:
    side = upper_text(value)
    return side if side in {"BUY", "SELL", "NONE"} else DEFAULT_PROPOSED_SIDE


def lower_text(value: Any) -> str:
    return str(value or "").strip().lower()


def upper_text(value: Any) -> str:
    return str(value or "").strip().upper()


def has_policy(value: Any) -> bool:
    text = upper_text(value)
    return bool(text and text not in {"MISSING", "FALSE", "NONE", "NULL"})


def is_available_value(value: Any) -> bool:
    if value is None:
        return False
    return str(value).strip().upper() not in {"", "MISSING", "UNAVAILABLE", "NONE", "NULL"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output
