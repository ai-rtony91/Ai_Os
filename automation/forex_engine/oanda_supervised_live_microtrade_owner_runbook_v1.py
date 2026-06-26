"""Placeholder-only owner runbook for one supervised live microtrade review."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    EXACT_LIVE_WARNING,
    EXACT_NEXT_CODEX_PACKET,
    EXACT_OWNER_WARNING,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
)


VERSION = "oanda_supervised_live_microtrade_owner_runbook_v1"

OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_READY_FOR_OWNER_REVIEW = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_READY_FOR_OWNER_REVIEW"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_REQUIRE_REPAIR = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_REQUIRE_REPAIR"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_BLOCKED_UNSAFE = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_BLOCKED_UNSAFE"
)

OWNER_CHECKLIST = (
    "Anthony performs any real broker action manually outside Codex.",
    "Codex does not execute.",
    "AIOS does not execute autonomously.",
    "Runtime values are not persisted.",
    "Account identifiers are not stored.",
    "One tiny trade only.",
    "No compounding.",
    "No bank movement.",
    "No unattended loop.",
    "No vacation mode approval.",
    "No profit guarantee.",
)
RUNTIME_PLACEHOLDERS = (
    "OWNER_RUNTIME_PROVIDER_LABEL",
    "OWNER_RUNTIME_ACCOUNT_BOUNDARY_CONFIRMATION",
    "OWNER_RUNTIME_INSTRUMENT_CONFIRMATION",
    "OWNER_RUNTIME_UNITS_CONFIRMATION",
    "OWNER_RUNTIME_STOP_DISTANCE_CONFIRMATION",
    "OWNER_RUNTIME_TAKE_PROFIT_DISTANCE_CONFIRMATION",
    "OWNER_RUNTIME_FINAL_CONFIRMATION_PHRASE",
)
FORBIDDEN_VALUES = (
    "real endpoint URL",
    "credential value",
    "account identifier",
    "raw broker payload",
    "broker order identifier",
    "saved runtime value",
)
ABORT_CHECKLIST = (
    "abort_before_execution",
    "abort_on_timeout",
    "abort_on_unexpected_spread",
    "abort_on_market_closed",
    "abort_on_duplicate_order_risk",
    "abort_if_account_boundary_unclear",
    "abort_if_credential_boundary_unclear",
)
POST_TRADE_CAPTURE_CHECKLIST = (
    "filled_trade_evidence_checklist",
    "realized_pl_capture_checklist",
    "spread_slippage_capture_checklist",
    "reconciliation_checklist",
    "screenshot_evidence_checklist",
    "journal_checklist",
    "route_live_result_back_to_evidence_ledger",
)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeOwnerRunbookInput:
    owner_checklist: tuple[str, ...] = OWNER_CHECKLIST
    runtime_placeholder_list: tuple[str, ...] = RUNTIME_PLACEHOLDERS
    forbidden_value_list: tuple[str, ...] = FORBIDDEN_VALUES
    final_confirmation_phrase_placeholder: str = "OWNER_RUNTIME_FINAL_CONFIRMATION_PHRASE"
    abort_checklist: tuple[str, ...] = ABORT_CHECKLIST
    post_trade_capture_checklist: tuple[str, ...] = POST_TRADE_CAPTURE_CHECKLIST
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeOwnerRunbookResult:
    version: str
    classification: str
    owner_checklist: tuple[str, ...]
    runtime_placeholder_list: tuple[str, ...]
    forbidden_value_list: tuple[str, ...]
    final_confirmation_phrase_placeholder: str
    abort_checklist: tuple[str, ...]
    post_trade_capture_checklist: tuple[str, ...]
    next_packet_after_owner_run: str
    missing_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    owner_runbook_preview: Mapping[str, Any]
    owner_warning: str
    live_warning: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    live_micro_trade_exception_allowed: bool
    owner_live_execution_approval_present: bool
    codex_live_execution_authorized: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool


def build_sample_ready_input() -> OandaSupervisedLiveMicrotradeOwnerRunbookInput:
    return OandaSupervisedLiveMicrotradeOwnerRunbookInput()


def build_sample_missing_input() -> OandaSupervisedLiveMicrotradeOwnerRunbookInput:
    return OandaSupervisedLiveMicrotradeOwnerRunbookInput(
        owner_checklist=OWNER_CHECKLIST[:-2]
    )


def build_sample_unsafe_input() -> OandaSupervisedLiveMicrotradeOwnerRunbookInput:
    return OandaSupervisedLiveMicrotradeOwnerRunbookInput(
        unsafe_flags={"runtime_value_persistence_attempt": True}
    )


def build_oanda_supervised_live_microtrade_owner_runbook(
    runbook_input: OandaSupervisedLiveMicrotradeOwnerRunbookInput | Mapping[str, Any] | None = None,
) -> OandaSupervisedLiveMicrotradeOwnerRunbookResult:
    active_input = _coerce_input(runbook_input or build_sample_ready_input())
    missing_items = _missing_items(active_input)
    blocked_items = tuple(
        dict.fromkeys(name for name, value in active_input.unsafe_flags.items() if bool(value))
    )
    if blocked_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_BLOCKED_UNSAFE
    elif missing_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_REQUIRE_REPAIR
    else:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    preview = {
        "preview_only": True,
        "placeholder_only": True,
        "owner_checklist": active_input.owner_checklist,
        "runtime_placeholder_list": active_input.runtime_placeholder_list,
        "forbidden_value_list": active_input.forbidden_value_list,
        "final_confirmation_phrase_placeholder": active_input.final_confirmation_phrase_placeholder,
        "abort_checklist": active_input.abort_checklist,
        "post_trade_capture_checklist": active_input.post_trade_capture_checklist,
        "next_packet_after_owner_run": EXACT_NEXT_CODEX_PACKET,
    }
    return OandaSupervisedLiveMicrotradeOwnerRunbookResult(
        version=VERSION,
        classification=classification,
        owner_checklist=active_input.owner_checklist,
        runtime_placeholder_list=active_input.runtime_placeholder_list,
        forbidden_value_list=active_input.forbidden_value_list,
        final_confirmation_phrase_placeholder=active_input.final_confirmation_phrase_placeholder,
        abort_checklist=active_input.abort_checklist,
        post_trade_capture_checklist=active_input.post_trade_capture_checklist,
        next_packet_after_owner_run=EXACT_NEXT_CODEX_PACKET,
        missing_items=missing_items,
        blocked_items=blocked_items,
        owner_runbook_preview=jsonable(preview),
        owner_warning=EXACT_OWNER_WARNING,
        live_warning=EXACT_LIVE_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaSupervisedLiveMicrotradeOwnerRunbookResult) -> str:
    return "\n".join(
        (
            f"Owner runbook status: {result.classification}.",
            "Anthony performs any real broker action manually outside Codex.",
            "Codex does not execute.",
            "AIOS does not execute autonomously.",
            "Runtime values are not persisted.",
            "Account identifiers are not stored.",
            result.owner_warning,
            result.live_warning,
        )
    )


def to_markdown(result: OandaSupervisedLiveMicrotradeOwnerRunbookResult) -> str:
    rows = [
        "# AIOS Forex OANDA Supervised Live Microtrade Owner Runbook V1",
        "",
        f"- Classification: `{result.classification}`",
        "",
        "## Owner Checklist",
    ]
    rows.extend(f"- {item}" for item in result.owner_checklist)
    rows.extend(("", "## Runtime Placeholders"))
    rows.extend(f"- `{item}`" for item in result.runtime_placeholder_list)
    rows.extend(("", "## Forbidden Values"))
    rows.extend(f"- {item}" for item in result.forbidden_value_list)
    rows.extend(("", "## Abort Checklist"))
    rows.extend(f"- `{item}`" for item in result.abort_checklist)
    rows.extend(("", "## Post-Trade Capture Checklist"))
    rows.extend(f"- `{item}`" for item in result.post_trade_capture_checklist)
    rows.extend(("", f"Next packet after owner run: `{result.next_packet_after_owner_run}`"))
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaSupervisedLiveMicrotradeOwnerRunbookInput | Mapping[str, Any],
) -> OandaSupervisedLiveMicrotradeOwnerRunbookInput:
    if isinstance(value, OandaSupervisedLiveMicrotradeOwnerRunbookInput):
        return value
    raw = dict(value)
    return OandaSupervisedLiveMicrotradeOwnerRunbookInput(
        owner_checklist=tuple(raw.get("owner_checklist", ())),
        runtime_placeholder_list=tuple(raw.get("runtime_placeholder_list", ())),
        forbidden_value_list=tuple(raw.get("forbidden_value_list", ())),
        final_confirmation_phrase_placeholder=str(
            raw.get("final_confirmation_phrase_placeholder", "")
        ),
        abort_checklist=tuple(raw.get("abort_checklist", ())),
        post_trade_capture_checklist=tuple(raw.get("post_trade_capture_checklist", ())),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _missing_items(active_input: OandaSupervisedLiveMicrotradeOwnerRunbookInput) -> tuple[str, ...]:
    missing: list[str] = []
    for item in OWNER_CHECKLIST:
        if item not in active_input.owner_checklist:
            missing.append(item)
    for item in RUNTIME_PLACEHOLDERS:
        if item not in active_input.runtime_placeholder_list:
            missing.append(item)
    for item in FORBIDDEN_VALUES:
        if item not in active_input.forbidden_value_list:
            missing.append(item)
    for item in ABORT_CHECKLIST:
        if item not in active_input.abort_checklist:
            missing.append(item)
    for item in POST_TRADE_CAPTURE_CHECKLIST:
        if item not in active_input.post_trade_capture_checklist:
            missing.append(item)
    if active_input.final_confirmation_phrase_placeholder != "OWNER_RUNTIME_FINAL_CONFIRMATION_PHRASE":
        missing.append("final_confirmation_phrase_placeholder")
    return tuple(missing)

