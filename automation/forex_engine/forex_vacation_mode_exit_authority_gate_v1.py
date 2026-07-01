"""Metadata-only exit authority gate for AIOS Forex Vacation Mode."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    base_hard_false_fields,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_EXIT_AUTHORITY_GATE_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_EXIT_AUTHORITY_GATE"

EXIT_AUTHORITY_HOLD_ALLOWED = "EXIT_AUTHORITY_HOLD_ALLOWED"
EXIT_AUTHORITY_READY_FOR_OWNER_REVIEW = "EXIT_AUTHORITY_READY_FOR_OWNER_REVIEW"
EXIT_REQUIRED_BY_STOP_LOSS = "EXIT_REQUIRED_BY_STOP_LOSS"
EXIT_REQUIRED_BY_TAKE_PROFIT = "EXIT_REQUIRED_BY_TAKE_PROFIT"
EXIT_REQUIRED_BY_MARKET_CLOSE = "EXIT_REQUIRED_BY_MARKET_CLOSE"
EXIT_REQUIRED_BY_KILL_SWITCH = "EXIT_REQUIRED_BY_KILL_SWITCH"
EXIT_REQUIRED_BY_RULE_FAILURE = "EXIT_REQUIRED_BY_RULE_FAILURE"
EXIT_BLOCKED_BY_OWNER_AUTHORITY = "EXIT_BLOCKED_BY_OWNER_AUTHORITY"
EXIT_BLOCKED_BY_SAFETY = "EXIT_BLOCKED_BY_SAFETY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

REQUIRED_SECTIONS = (
    "position_state",
    "exit_signal_state",
    "risk_state",
    "market_state",
    "owner_authority_state",
    "safety_policy",
)


def evaluate_forex_vacation_mode_exit_authority_gate_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate whether an owner-visible exit recommendation is required."""

    source = _mapping(payload)
    if not source:
        return _result(INCOMPLETE_INPUTS, False, ("payload_missing",), source)
    missing = _missing_sections(source, REQUIRED_SECTIONS)
    if missing:
        return _result(INCOMPLETE_INPUTS, False, missing, source)

    position = _mapping(source.get("position_state"))
    exit_signal = _mapping(source.get("exit_signal_state"))
    risk = _mapping(source.get("risk_state"))
    market = _mapping(source.get("market_state"))
    owner = _mapping(source.get("owner_authority_state"))
    safety = _mapping(source.get("safety_policy"))

    safety_blockers = _safety_blockers(safety)
    if safety_blockers:
        return _result(EXIT_BLOCKED_BY_SAFETY, False, safety_blockers, source)
    kill_switch_blockers = _kill_switch_blockers(safety)
    if kill_switch_blockers:
        return _result(EXIT_BLOCKED_BY_SAFETY, False, kill_switch_blockers, source)
    trigger_blockers = _exit_trigger_blockers(position, exit_signal, risk, market)
    if trigger_blockers:
        return _result(EXIT_BLOCKED_BY_SAFETY, False, trigger_blockers, source)
    receipt_blockers = _receipt_plan_blockers(exit_signal)
    if safety.get("kill_switch_active") is True:
        return _result(
            EXIT_REQUIRED_BY_KILL_SWITCH,
            True,
            ("kill_switch_active", *receipt_blockers),
            source,
        )

    owner_blockers = _owner_blockers(owner)
    if owner_blockers:
        return _result(EXIT_BLOCKED_BY_OWNER_AUTHORITY, False, owner_blockers, source)

    trigger_status, trigger_blockers = _exit_trigger(position, exit_signal, risk, market)
    if trigger_status:
        return _result(trigger_status, True, (*trigger_blockers, *receipt_blockers), source)
    if _owner_exit_requested(exit_signal) is True:
        return _result(
            EXIT_AUTHORITY_READY_FOR_OWNER_REVIEW,
            True,
            ("owner_exit_requested", *receipt_blockers),
            source,
        )
    return _result(EXIT_AUTHORITY_HOLD_ALLOWED, True, (), source)


def _result(
    status: str,
    ready: bool,
    blockers: Sequence[str],
    source: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "metadata_only": True,
        "read_only": True,
        "exit_recommendation_only": True,
        "owner_visible_reason": _reason(status),
        "owner_next_action": _next_action(status),
        "post_exit_receipt_capture_required": status != EXIT_AUTHORITY_HOLD_ALLOWED,
        "repeat_attempt_blocked_until_review": True,
        "blockers": _unique(blockers),
        "source_sections_seen": sorted(str(key) for key in source.keys()),
        **base_hard_false_fields(),
    }


def _owner_blockers(owner: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        f"{field}_required_true"
        for field in (
            "owner_exit_review_allowed",
            "owner_visible_reason_required",
            "repeat_attempt_blocked_until_review",
        )
        if owner.get(field) is not True
    )


def _safety_blockers(safety: Mapping[str, Any]) -> tuple[str, ...]:
    required = (
        "metadata_only",
        "no_order_close",
        "no_broker_call",
        "no_oanda_call",
        "no_trade_execution",
    )
    return tuple(f"{field}_required_true" for field in required if safety.get(field) is not True)


def _receipt_plan_blockers(exit_signal: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        f"{field}_required_true"
        for field in ("post_exit_receipt_capture_plan_ready", "owner_visible_reason_present")
        if exit_signal.get(field) is not True
    )


def _required_bool(source: Mapping[str, Any], fields: Sequence[str]) -> tuple[str, ...]:
    return tuple(
        f"{field}_required_bool"
        for field in fields
        if field not in source or not isinstance(source.get(field), bool)
    )


def _kill_switch_blockers(safety: Mapping[str, Any]) -> tuple[str, ...]:
    kill_switch_active = safety.get("kill_switch_active")
    if "kill_switch_active" not in safety or not isinstance(kill_switch_active, bool):
        return ("kill_switch_active_required_bool",)
    return ()


def _owner_exit_requested(exit_signal: Mapping[str, Any]) -> bool:
    if "owner_exit_requested" in exit_signal:
        return bool(exit_signal["owner_exit_requested"])
    return bool(exit_signal.get("owner_exit_review_requested", False))


def _exit_trigger(
    position: Mapping[str, Any],
    exit_signal: Mapping[str, Any],
    risk: Mapping[str, Any],
    market: Mapping[str, Any],
) -> tuple[str, tuple[str, ...]]:
    if risk.get("stop_loss_triggered") is True:
        return EXIT_REQUIRED_BY_STOP_LOSS, ("stop_loss_triggered",)
    if risk.get("daily_loss_stop_active") is True:
        return EXIT_REQUIRED_BY_STOP_LOSS, ("daily_loss_stop_active",)
    if risk.get("max_loss_limit_hit") is True:
        return EXIT_REQUIRED_BY_STOP_LOSS, ("max_loss_limit_hit",)
    if exit_signal.get("take_profit_triggered") is True:
        return EXIT_REQUIRED_BY_TAKE_PROFIT, ("take_profit_triggered",)
    if market.get("market_close_exit_required") is True:
        return EXIT_REQUIRED_BY_MARKET_CLOSE, ("market_close_exit_required",)
    if position.get("rule_failure_detected") is True:
        return EXIT_REQUIRED_BY_RULE_FAILURE, ("rule_failure_detected",)
    if exit_signal.get("rule_failure_exit_required") is True:
        return EXIT_REQUIRED_BY_RULE_FAILURE, ("rule_failure_exit_required",)
    return "", ()


def _exit_trigger_blockers(
    position: Mapping[str, Any],
    exit_signal: Mapping[str, Any],
    risk: Mapping[str, Any],
    market: Mapping[str, Any],
) -> tuple[str, ...]:
    blockers = _required_bool(
        risk,
        (
            "stop_loss_triggered",
            "daily_loss_stop_active",
            "max_loss_limit_hit",
        ),
    )
    blockers += _required_bool(
        exit_signal,
        (
            "take_profit_triggered",
            "rule_failure_exit_required",
            "owner_exit_requested" if "owner_exit_requested" in exit_signal else "owner_exit_review_requested",
        ),
    )
    if (
        "owner_exit_requested" not in exit_signal
        and "owner_exit_review_requested" not in exit_signal
    ):
        blockers += ("owner_exit_requested_required_bool",)
    blockers += _required_bool(market, ("market_close_exit_required",))
    blockers += _required_bool(position, ("rule_failure_detected",))
    return blockers


def _missing_sections(source: Mapping[str, Any], sections: Sequence[str]) -> tuple[str, ...]:
    return tuple(f"{section}_missing" for section in sections if not _mapping(source.get(section)))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _reason(status: str) -> str:
    return {
        EXIT_AUTHORITY_HOLD_ALLOWED: "No exit trigger exists; metadata hold is allowed.",
        EXIT_AUTHORITY_READY_FOR_OWNER_REVIEW: "Owner exit review was requested.",
        EXIT_REQUIRED_BY_STOP_LOSS: "Stop-loss metadata requires exit review.",
        EXIT_REQUIRED_BY_TAKE_PROFIT: "Take-profit metadata requires exit review.",
        EXIT_REQUIRED_BY_MARKET_CLOSE: "Market close metadata requires exit review.",
        EXIT_REQUIRED_BY_KILL_SWITCH: "Kill switch metadata requires exit review.",
        EXIT_REQUIRED_BY_RULE_FAILURE: "Rule failure metadata requires exit review.",
        EXIT_BLOCKED_BY_OWNER_AUTHORITY: "Owner exit authority metadata is incomplete.",
        EXIT_BLOCKED_BY_SAFETY: "Safety metadata blocks exit review.",
    }.get(status, "Inputs are incomplete.")


def _next_action(status: str) -> str:
    if status == EXIT_AUTHORITY_HOLD_ALLOWED:
        return "Keep metadata-only hold; do not close an order."
    return "Route owner-visible exit review and capture post-exit evidence plan."


__all__ = [
    "EXIT_AUTHORITY_HOLD_ALLOWED",
    "EXIT_AUTHORITY_READY_FOR_OWNER_REVIEW",
    "EXIT_REQUIRED_BY_STOP_LOSS",
    "EXIT_REQUIRED_BY_TAKE_PROFIT",
    "EXIT_REQUIRED_BY_MARKET_CLOSE",
    "EXIT_REQUIRED_BY_KILL_SWITCH",
    "EXIT_REQUIRED_BY_RULE_FAILURE",
    "EXIT_BLOCKED_BY_OWNER_AUTHORITY",
    "EXIT_BLOCKED_BY_SAFETY",
    "INCOMPLETE_INPUTS",
    "evaluate_forex_vacation_mode_exit_authority_gate_v1",
]
