"""Combine Vacation Mode toggle, calendar, risk, proof, receipt, and balance state."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_owner_toggle_contract_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    HARD_FALSE_FIELDS,
    build_common_result,
    banking_focus_blockers,
    sensitive_data_blockers,
    _bool,
    _mapping,
    _present,
    _unique,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_OPERATION_STATE_MACHINE_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_OPERATION_STATE_MACHINE"

VACATION_MODE_OFF_IDLE = "VACATION_MODE_OFF_IDLE"
VACATION_MODE_ON_EVALUATING_GATES = "VACATION_MODE_ON_EVALUATING_GATES"
VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE = "VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE"
VACATION_MODE_ON_CLOSED_MAINTENANCE = "VACATION_MODE_ON_CLOSED_MAINTENANCE"
VACATION_MODE_ON_CLOSE_PROTECTION = "VACATION_MODE_ON_CLOSE_PROTECTION"
VACATION_MODE_ON_REOPEN_PREPARATION = "VACATION_MODE_ON_REOPEN_PREPARATION"
VACATION_MODE_ON_WEEKEND_MAINTENANCE = "VACATION_MODE_ON_WEEKEND_MAINTENANCE"
VACATION_MODE_ON_DEGRADED_MAINTENANCE = "VACATION_MODE_ON_DEGRADED_MAINTENANCE"
VACATION_MODE_PAUSED = "VACATION_MODE_PAUSED"
VACATION_MODE_KILL_SWITCH_STOP = "VACATION_MODE_KILL_SWITCH_STOP"
VACATION_MODE_WAITING_FOR_PROOF = "VACATION_MODE_WAITING_FOR_PROOF"
VACATION_MODE_WAITING_FOR_RECEIPTS = "VACATION_MODE_WAITING_FOR_RECEIPTS"
VACATION_MODE_BALANCE_MEMORY_REVIEW = "VACATION_MODE_BALANCE_MEMORY_REVIEW"
BLOCKED_BY_OWNER_TOGGLE = "BLOCKED_BY_OWNER_TOGGLE"
BLOCKED_BY_RUNTIME_CALENDAR = "BLOCKED_BY_RUNTIME_CALENDAR"
BLOCKED_BY_RISK_STATE = "BLOCKED_BY_RISK_STATE"
BLOCKED_BY_PROOF_STATE = "BLOCKED_BY_PROOF_STATE"
BLOCKED_BY_RECEIPT_STATE = "BLOCKED_BY_RECEIPT_STATE"
BLOCKED_BY_BALANCE_MEMORY = "BLOCKED_BY_BALANCE_MEMORY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"

RISK_FIELDS = (
    "kill_switch_active",
    "daily_loss_stop_active",
    "drawdown_within_limit",
    "max_drawdown_pct",
    "current_drawdown_pct",
    "max_daily_loss_pct",
    "current_daily_loss_pct",
    "no_new_trade_seeking_if_kill_switch",
    "no_new_trade_seeking_if_daily_loss_stop",
    "no_new_trade_seeking_if_drawdown_breach",
)
PROOF_FIELDS = (
    "proof_required",
    "proof_ready",
    "fake_proof_blocked",
    "repeatability_review_ready",
    "owner_review_required_for_live",
)
RECEIPT_FIELDS = (
    "receipt_required_after_execution",
    "outstanding_receipts",
    "post_trade_review_complete",
    "next_trade_blocked_until_receipts_reviewed",
)
BALANCE_FIELDS = (
    "balance_memory_ready",
    "compounding_observer_ready",
    "withdrawal_deferred",
    "bank_routing_deferred",
    "money_moved",
)

POSTURE_TO_STATE = {
    "ACTIVE_SUPERVISION": VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE,
    "CLOSE_PROTECTION": VACATION_MODE_ON_CLOSE_PROTECTION,
    "CLOSED_MAINTENANCE": VACATION_MODE_ON_CLOSED_MAINTENANCE,
    "REOPEN_PREPARATION": VACATION_MODE_ON_REOPEN_PREPARATION,
    "WEEKEND_HEAVY_MAINTENANCE": VACATION_MODE_ON_WEEKEND_MAINTENANCE,
    "HOLIDAY_DEGRADED_MAINTENANCE": VACATION_MODE_ON_DEGRADED_MAINTENANCE,
    "LOW_LIQUIDITY_MAINTENANCE": VACATION_MODE_ON_DEGRADED_MAINTENANCE,
    "VACATION_MODE_YEAR_ROUND_REVIEW": VACATION_MODE_ON_EVALUATING_GATES,
}


def evaluate_forex_vacation_mode_operation_state_machine_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify Vacation Mode operation state without side effects."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _operation_result(source, BLOCKED_BY_SENSITIVE_DATA, False, sensitive_blockers)
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _operation_result(source, BLOCKED_BY_BANKING_FOCUS, False, banking_blockers)
    if not source:
        return _operation_result(source, INCOMPLETE_INPUTS, False, ("payload_missing",))

    owner_toggle = _mapping(source.get("owner_toggle_result"))
    calendar = _mapping(source.get("runtime_calendar_result"))
    risk = _mapping(source.get("risk_state"))
    proof = _mapping(source.get("proof_state"))
    receipt = _mapping(source.get("receipt_state"))
    balance = _mapping(source.get("balance_state"))

    missing = _missing_sections(owner_toggle, calendar, risk, proof, receipt, balance)
    if missing:
        return _operation_result(source, INCOMPLETE_INPUTS, False, missing)

    if owner_toggle.get("ready") is not True or not _mapping(owner_toggle.get("owner_toggle_contract")):
        return _operation_result(
            source,
            BLOCKED_BY_OWNER_TOGGLE,
            False,
            ("owner_toggle_result_not_ready",),
        )
    if calendar.get("ready") is not True or not _present(calendar.get("current_runtime_posture")):
        return _operation_result(
            source,
            BLOCKED_BY_RUNTIME_CALENDAR,
            False,
            ("runtime_calendar_result_not_ready",),
        )

    risk_meta_blockers = _required_fields(risk, RISK_FIELDS)
    proof_meta_blockers = _required_fields(proof, PROOF_FIELDS)
    receipt_meta_blockers = _required_fields(receipt, RECEIPT_FIELDS)
    balance_meta_blockers = _required_fields(balance, BALANCE_FIELDS)
    if risk_meta_blockers or proof_meta_blockers or receipt_meta_blockers or balance_meta_blockers:
        return _operation_result(
            source,
            INCOMPLETE_INPUTS,
            False,
            (*risk_meta_blockers, *proof_meta_blockers, *receipt_meta_blockers, *balance_meta_blockers),
        )

    toggle_state = str(owner_toggle.get("vacation_mode_toggle_state", "")).upper()
    if toggle_state == "OFF":
        return _operation_result(source, VACATION_MODE_OFF_IDLE, True, ())
    if toggle_state == "PAUSED":
        return _operation_result(source, VACATION_MODE_PAUSED, True, ())
    if toggle_state == "KILL_SWITCH_STOP":
        return _operation_result(source, VACATION_MODE_KILL_SWITCH_STOP, True, ())

    risk_blockers = _risk_blockers(risk)
    if _bool(risk.get("kill_switch_active")):
        return _operation_result(source, VACATION_MODE_KILL_SWITCH_STOP, True, ("kill_switch_active",))
    if risk_blockers:
        return _operation_result(source, BLOCKED_BY_RISK_STATE, False, risk_blockers)

    proof_blockers = _proof_blockers(proof)
    if proof_blockers:
        return _operation_result(source, VACATION_MODE_WAITING_FOR_PROOF, True, proof_blockers)

    receipt_blockers = _receipt_blockers(receipt)
    if receipt_blockers:
        return _operation_result(source, VACATION_MODE_WAITING_FOR_RECEIPTS, True, receipt_blockers)

    balance_blockers = _balance_blockers(balance)
    if balance_blockers:
        return _operation_result(source, VACATION_MODE_BALANCE_MEMORY_REVIEW, True, balance_blockers)

    posture = str(calendar.get("current_runtime_posture", "")).upper()
    status = POSTURE_TO_STATE.get(posture)
    if not status:
        return _operation_result(source, BLOCKED_BY_RUNTIME_CALENDAR, False, ("runtime_posture_unsupported",))
    return _operation_result(source, status, True, ())


def _operation_result(
    source: Mapping[str, Any],
    status: str,
    ready: bool,
    blockers: Sequence[str],
) -> dict[str, Any]:
    owner_toggle = _mapping(source.get("owner_toggle_result"))
    calendar = _mapping(source.get("runtime_calendar_result"))
    risk = _mapping(source.get("risk_state"))
    proof = _mapping(source.get("proof_state"))
    receipt = _mapping(source.get("receipt_state"))
    balance = _mapping(source.get("balance_state"))
    toggle_state = str(owner_toggle.get("vacation_mode_toggle_state", "UNKNOWN"))
    operation_state = _operation_state_summary(status, toggle_state, calendar, risk, proof, receipt, balance)
    extra = {"operation_state": operation_state}
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=ready,
        vacation_mode_requested=toggle_state not in {"OFF", "UNKNOWN"} or _bool(owner_toggle.get("vacation_mode_requested")),
        vacation_mode_toggle_state=toggle_state,
        vacation_mode_operation_state=operation_state["vacation_mode_operation_state"],
        kill_switch_active=_bool(risk.get("kill_switch_active")) or toggle_state == "KILL_SWITCH_STOP",
        new_trade_seeking_allowed_by_this_module=status == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE,
        maintenance_allowed_by_this_module=status in _maintenance_states() or toggle_state in {"OFF", "PAUSED"},
        owner_attention_required=status
        in {
            VACATION_MODE_KILL_SWITCH_STOP,
            VACATION_MODE_WAITING_FOR_PROOF,
            VACATION_MODE_WAITING_FOR_RECEIPTS,
            VACATION_MODE_BALANCE_MEMORY_REVIEW,
            BLOCKED_BY_RISK_STATE,
            BLOCKED_BY_RUNTIME_CALENDAR,
            BLOCKED_BY_OWNER_TOGGLE,
        },
        blockers=blockers,
        next_best_packet=_next_packet(status),
        safe_manual_next_action=_safe_manual_next_action(status),
        extra=extra,
    )


def _operation_state_summary(
    status: str,
    toggle_state: str,
    calendar: Mapping[str, Any],
    risk: Mapping[str, Any],
    proof: Mapping[str, Any],
    receipt: Mapping[str, Any],
    balance: Mapping[str, Any],
) -> dict[str, Any]:
    allowed = status == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE
    blocked = status.startswith("BLOCKED_") or status == VACATION_MODE_KILL_SWITCH_STOP
    return {
        "vacation_mode_operation_state": status,
        "owner_toggle_state": toggle_state,
        "calendar_posture": str(calendar.get("current_runtime_posture", "UNKNOWN")),
        "risk_gate_summary": {
            "kill_switch_active": _bool(risk.get("kill_switch_active")),
            "daily_loss_stop_active": _bool(risk.get("daily_loss_stop_active")),
            "drawdown_within_limit": _bool(risk.get("drawdown_within_limit")),
        },
        "proof_gate_summary": {
            "proof_required": _bool(proof.get("proof_required")),
            "proof_ready": _bool(proof.get("proof_ready")),
            "repeatability_review_ready": _bool(proof.get("repeatability_review_ready")),
        },
        "receipt_gate_summary": {
            "outstanding_receipts": _bool(receipt.get("outstanding_receipts")),
            "post_trade_review_complete": _bool(receipt.get("post_trade_review_complete")),
        },
        "balance_gate_summary": {
            "balance_memory_ready": _bool(balance.get("balance_memory_ready")),
            "compounding_observer_ready": _bool(balance.get("compounding_observer_ready")),
            "withdrawal_deferred": _bool(balance.get("withdrawal_deferred")),
            "bank_routing_deferred": _bool(balance.get("bank_routing_deferred")),
            "money_moved": False,
        },
        "allowed_now": allowed,
        "blocked_now": blocked,
        "owner_visible_reason": _owner_visible_reason(status),
        "next_required_action": _safe_manual_next_action(status),
    }


def _missing_sections(
    owner_toggle: Mapping[str, Any],
    calendar: Mapping[str, Any],
    risk: Mapping[str, Any],
    proof: Mapping[str, Any],
    receipt: Mapping[str, Any],
    balance: Mapping[str, Any],
) -> tuple[str, ...]:
    missing: list[str] = []
    if not owner_toggle:
        missing.append("owner_toggle_result_missing")
    if not calendar:
        missing.append("runtime_calendar_result_missing")
    if not risk:
        missing.append("risk_state_missing")
    if not proof:
        missing.append("proof_state_missing")
    if not receipt:
        missing.append("receipt_state_missing")
    if not balance:
        missing.append("balance_state_missing")
    return tuple(missing)


def _required_fields(source: Mapping[str, Any], fields: Sequence[str]) -> tuple[str, ...]:
    return tuple(f"missing_{field}" for field in fields if field not in source)


def _risk_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if _bool(risk.get("daily_loss_stop_active")):
        blockers.append("daily_loss_stop_active")
    if not _bool(risk.get("drawdown_within_limit")):
        blockers.append("drawdown_breach")
    for field in (
        "no_new_trade_seeking_if_kill_switch",
        "no_new_trade_seeking_if_daily_loss_stop",
        "no_new_trade_seeking_if_drawdown_breach",
    ):
        if not _bool(risk.get(field)):
            blockers.append(f"{field}_false")
    return tuple(_unique(blockers))


def _proof_blockers(proof: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if _bool(proof.get("proof_required")) and not _bool(proof.get("proof_ready")):
        blockers.append("proof_not_ready")
    if not _bool(proof.get("fake_proof_blocked")):
        blockers.append("fake_proof_boundary_missing")
    if not _bool(proof.get("owner_review_required_for_live")):
        blockers.append("owner_review_for_live_missing")
    return tuple(_unique(blockers))


def _receipt_blockers(receipt: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if _bool(receipt.get("outstanding_receipts")):
        blockers.append("outstanding_receipts")
    if not _bool(receipt.get("next_trade_blocked_until_receipts_reviewed")):
        blockers.append("next_trade_receipt_lock_missing")
    return tuple(_unique(blockers))


def _balance_blockers(balance: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _bool(balance.get("balance_memory_ready")):
        blockers.append("balance_memory_not_ready")
    if not _bool(balance.get("compounding_observer_ready")):
        blockers.append("compounding_observer_not_ready")
    if not _bool(balance.get("withdrawal_deferred")):
        blockers.append("withdrawal_not_deferred")
    if not _bool(balance.get("bank_routing_deferred")):
        blockers.append("bank_routing_not_deferred")
    if balance.get("money_moved") is not False:
        blockers.append("money_moved_not_false")
    return tuple(_unique(blockers))


def _maintenance_states() -> set[str]:
    return {
        VACATION_MODE_ON_CLOSED_MAINTENANCE,
        VACATION_MODE_ON_CLOSE_PROTECTION,
        VACATION_MODE_ON_REOPEN_PREPARATION,
        VACATION_MODE_ON_WEEKEND_MAINTENANCE,
        VACATION_MODE_ON_DEGRADED_MAINTENANCE,
        VACATION_MODE_ON_EVALUATING_GATES,
    }


def _owner_visible_reason(status: str) -> str:
    return {
        VACATION_MODE_OFF_IDLE: "Vacation Mode is OFF; new trade seeking is stopped.",
        VACATION_MODE_PAUSED: "Vacation Mode is paused; new trade seeking is held.",
        VACATION_MODE_KILL_SWITCH_STOP: "Kill switch stop is active and requires owner attention.",
        VACATION_MODE_WAITING_FOR_PROOF: "Proof is required before governed operation can continue.",
        VACATION_MODE_WAITING_FOR_RECEIPTS: "Outstanding receipts must be reviewed before another trade cycle.",
        VACATION_MODE_BALANCE_MEMORY_REVIEW: "Balance/equity memory must be ready before operation continues.",
        VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE: "All metadata gates allow active supervision preparation.",
        VACATION_MODE_ON_CLOSE_PROTECTION: "Market close protection posture is active.",
        VACATION_MODE_ON_CLOSED_MAINTENANCE: "Market is closed; maintenance work is the active posture.",
        VACATION_MODE_ON_REOPEN_PREPARATION: "Reopen preparation is the active posture.",
        VACATION_MODE_ON_WEEKEND_MAINTENANCE: "Weekend heavy maintenance is the active posture.",
        VACATION_MODE_ON_DEGRADED_MAINTENANCE: "Degraded market maintenance is the active posture.",
        VACATION_MODE_ON_EVALUATING_GATES: "Vacation Mode maturity review is evaluating gates.",
    }.get(status, "Vacation Mode operation state requires review.")


def _next_packet(status: str) -> str:
    if status == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE:
        return "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
    if status == VACATION_MODE_ON_CLOSE_PROTECTION:
        return "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1"
    if status == VACATION_MODE_ON_REOPEN_PREPARATION:
        return "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"
    if status == VACATION_MODE_ON_WEEKEND_MAINTENANCE:
        return "AIOS_FOREX_WEEKEND_HEAVY_MAINTENANCE_AND_AUDIT_V1"
    if status in {VACATION_MODE_ON_CLOSED_MAINTENANCE, VACATION_MODE_ON_DEGRADED_MAINTENANCE}:
        return "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
    if status == VACATION_MODE_WAITING_FOR_PROOF:
        return "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1"
    if status == VACATION_MODE_WAITING_FOR_RECEIPTS:
        return "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
    if status == VACATION_MODE_BALANCE_MEMORY_REVIEW:
        return "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"
    return NEXT_BEST_PACKET


def _safe_manual_next_action(status: str) -> str:
    if status == VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE:
        return "Prepare metadata-only active supervision review; execution remains separate."
    if status in _maintenance_states():
        return "Route safe non-broker maintenance or preparation work for owner visibility."
    if status == VACATION_MODE_WAITING_FOR_PROOF:
        return "Capture or review proof before seeking new trade candidates."
    if status == VACATION_MODE_WAITING_FOR_RECEIPTS:
        return "Review outstanding receipts and post-trade evidence before another cycle."
    if status == VACATION_MODE_BALANCE_MEMORY_REVIEW:
        return "Run balance/equity observer review before continuing operation state."
    if status == VACATION_MODE_KILL_SWITCH_STOP:
        return "Stop new trade seeking and route owner attention immediately."
    if status == VACATION_MODE_OFF_IDLE:
        return "Keep Vacation Mode idle until the owner turns it on."
    if status == VACATION_MODE_PAUSED:
        return "Hold new trade seeking until the owner resumes and gates are rechecked."
    return "Review blockers before continuing Vacation Mode operation state."


__all__ = [
    "HARD_FALSE_FIELDS",
    "VACATION_MODE_OFF_IDLE",
    "VACATION_MODE_ON_EVALUATING_GATES",
    "VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE",
    "VACATION_MODE_ON_CLOSED_MAINTENANCE",
    "VACATION_MODE_ON_CLOSE_PROTECTION",
    "VACATION_MODE_ON_REOPEN_PREPARATION",
    "VACATION_MODE_ON_WEEKEND_MAINTENANCE",
    "VACATION_MODE_ON_DEGRADED_MAINTENANCE",
    "VACATION_MODE_PAUSED",
    "VACATION_MODE_KILL_SWITCH_STOP",
    "VACATION_MODE_WAITING_FOR_PROOF",
    "VACATION_MODE_WAITING_FOR_RECEIPTS",
    "VACATION_MODE_BALANCE_MEMORY_REVIEW",
    "BLOCKED_BY_RISK_STATE",
    "BLOCKED_BY_BANKING_FOCUS",
    "BLOCKED_BY_SENSITIVE_DATA",
    "evaluate_forex_vacation_mode_operation_state_machine_v1",
]
