"""Metadata-only open-position supervision for AIOS Forex Vacation Mode."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    base_hard_false_fields,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_POSITION_SUPERVISOR_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_POSITION_SUPERVISOR"

POSITION_SUPERVISION_HOLD = "POSITION_SUPERVISION_HOLD"
POSITION_SUPERVISION_EXIT_REVIEW_REQUIRED = "POSITION_SUPERVISION_EXIT_REVIEW_REQUIRED"
POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED = "POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED"
POSITION_SUPERVISION_RECEIPT_REQUIRED = "POSITION_SUPERVISION_RECEIPT_REQUIRED"
POSITION_SUPERVISION_OWNER_ALERT_REQUIRED = "POSITION_SUPERVISION_OWNER_ALERT_REQUIRED"
POSITION_SUPERVISION_BLOCKED_BY_RISK = "POSITION_SUPERVISION_BLOCKED_BY_RISK"
POSITION_SUPERVISION_BLOCKED_BY_MARKET = "POSITION_SUPERVISION_BLOCKED_BY_MARKET"
POSITION_SUPERVISION_BLOCKED_BY_SAFETY = "POSITION_SUPERVISION_BLOCKED_BY_SAFETY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

REQUIRED_SECTIONS = (
    "position_state",
    "risk_state",
    "market_state",
    "receipt_state",
    "owner_alert_state",
    "safety_policy",
)


def evaluate_forex_vacation_mode_position_supervisor_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify open-position metadata and the next owner-visible action."""

    source = _mapping(payload)
    if not source:
        return _result(INCOMPLETE_INPUTS, False, ("payload_missing",), source)
    missing = _missing_sections(source, REQUIRED_SECTIONS)
    if missing:
        return _result(INCOMPLETE_INPUTS, False, missing, source)

    position = _mapping(source.get("position_state"))
    risk = _mapping(source.get("risk_state"))
    market = _mapping(source.get("market_state"))
    receipt = _mapping(source.get("receipt_state"))
    alert = _mapping(source.get("owner_alert_state"))
    safety = _mapping(source.get("safety_policy"))

    safety_blockers = _safety_blockers(safety)
    if safety_blockers:
        return _result(POSITION_SUPERVISION_BLOCKED_BY_SAFETY, False, safety_blockers, source)
    kill_switch_blockers = _kill_switch_blockers(safety)
    if kill_switch_blockers:
        return _result(POSITION_SUPERVISION_BLOCKED_BY_SAFETY, False, kill_switch_blockers, source)
    if safety.get("kill_switch_active") is True:
        return _result(
            POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED,
            True,
            ("kill_switch_active",),
            source,
        )
    risk_bool_blockers = _risk_required_bool_blockers(risk)
    if risk_bool_blockers:
        return _result(POSITION_SUPERVISION_BLOCKED_BY_RISK, False, risk_bool_blockers, source)
    risk_emergency_blockers = _risk_emergency_blockers(risk)
    if risk_emergency_blockers:
        return _result(
            POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED,
            True,
            risk_emergency_blockers,
            source,
        )

    risk_blockers = _risk_blockers(risk)
    if risk_blockers:
        return _result(POSITION_SUPERVISION_BLOCKED_BY_RISK, False, risk_blockers, source)

    market_blockers = _market_blockers(market)
    if market_blockers:
        return _result(POSITION_SUPERVISION_BLOCKED_BY_MARKET, False, market_blockers, source)

    if position.get("position_metadata_present") is not True:
        return _result(
            INCOMPLETE_INPUTS,
            False,
            ("position_metadata_present_required_true",),
            source,
        )
    if receipt.get("receipt_present") is not True:
        return _result(
            POSITION_SUPERVISION_RECEIPT_REQUIRED,
            True,
            ("receipt_present_required_true",),
            source,
        )
    if alert.get("owner_alert_required") is True:
        return _result(
            POSITION_SUPERVISION_OWNER_ALERT_REQUIRED,
            True,
            ("owner_alert_required",),
            source,
        )
    if position.get("rule_failure_detected") is True or position.get("exit_review_required") is True:
        return _result(
            POSITION_SUPERVISION_EXIT_REVIEW_REQUIRED,
            True,
            ("position_rule_requires_exit_review",),
            source,
        )
    return _result(POSITION_SUPERVISION_HOLD, True, (), source)


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
        "current_phase": "position_supervision",
        "owner_visible_reason": _reason(status),
        "owner_next_action": _next_action(status),
        "blockers": _unique(blockers),
        "source_sections_seen": sorted(str(key) for key in source.keys()),
        "supervision_recommendation": {
            "status": status,
            "may_hold": status == POSITION_SUPERVISION_HOLD,
            "requires_owner_review": status != POSITION_SUPERVISION_HOLD,
            "trade_alteration": "none",
        },
        **base_hard_false_fields(),
    }


def _risk_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if risk.get("risk_within_limits") is not True:
        blockers.append("risk_within_limits_required_true")
    return tuple(blockers)


def _risk_required_bool_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        f"{field}_required_bool"
        for field in ("daily_loss_stop_active", "max_loss_limit_hit")
        if field not in risk or not isinstance(risk.get(field), bool)
    )


def _risk_emergency_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if risk.get("daily_loss_stop_active") is True:
        blockers.append("daily_loss_stop_active")
    if risk.get("max_loss_limit_hit") is True:
        blockers.append("max_loss_limit_hit")
    return tuple(blockers)


def _market_blockers(market: Mapping[str, Any]) -> tuple[str, ...]:
    if market.get("market_state_safe") is not True:
        return ("market_state_safe_required_true",)
    return ()


def _safety_blockers(safety: Mapping[str, Any]) -> tuple[str, ...]:
    required = (
        "metadata_only",
        "no_trade_alteration",
        "no_trade_close",
        "no_broker_call",
        "no_oanda_call",
        "owner_visible_status",
    )
    return tuple(f"{field}_required_true" for field in required if safety.get(field) is not True)


def _kill_switch_blockers(safety: Mapping[str, Any]) -> tuple[str, ...]:
    kill_switch_active = safety.get("kill_switch_active")
    if "kill_switch_active" not in safety or not isinstance(kill_switch_active, bool):
        return ("kill_switch_active_required_bool",)
    return ()


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
        POSITION_SUPERVISION_HOLD: "Position metadata is stable; hold review may continue.",
        POSITION_SUPERVISION_EXIT_REVIEW_REQUIRED: "A rule failure requires owner exit review.",
        POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED: "Kill switch metadata requires emergency stop review.",
        POSITION_SUPERVISION_RECEIPT_REQUIRED: "Receipt evidence is required before supervision continues.",
        POSITION_SUPERVISION_OWNER_ALERT_REQUIRED: "Owner alert review is required.",
        POSITION_SUPERVISION_BLOCKED_BY_RISK: "Risk metadata blocks supervision.",
        POSITION_SUPERVISION_BLOCKED_BY_MARKET: "Market metadata blocks supervision.",
        POSITION_SUPERVISION_BLOCKED_BY_SAFETY: "Safety metadata blocks supervision.",
    }.get(status, "Inputs are incomplete.")


def _next_action(status: str) -> str:
    if status == POSITION_SUPERVISION_HOLD:
        return "Continue metadata-only supervision; do not alter or close a trade."
    return "Route owner-visible review for the listed supervision blockers."


__all__ = [
    "POSITION_SUPERVISION_HOLD",
    "POSITION_SUPERVISION_EXIT_REVIEW_REQUIRED",
    "POSITION_SUPERVISION_EMERGENCY_STOP_REQUIRED",
    "POSITION_SUPERVISION_RECEIPT_REQUIRED",
    "POSITION_SUPERVISION_OWNER_ALERT_REQUIRED",
    "POSITION_SUPERVISION_BLOCKED_BY_RISK",
    "POSITION_SUPERVISION_BLOCKED_BY_MARKET",
    "POSITION_SUPERVISION_BLOCKED_BY_SAFETY",
    "INCOMPLETE_INPUTS",
    "evaluate_forex_vacation_mode_position_supervisor_v1",
]
