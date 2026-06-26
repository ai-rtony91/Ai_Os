"""Reconcile owner-run result against planned ticket and capture checklist."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_RESULT_WARNING,
    decimal_value,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
    text_value,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_intake_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE,
    build_sample_breakeven_result_input as intake_breakeven_input,
    build_sample_loss_result_input as intake_loss_input,
    build_sample_missing_owner_result_input as intake_missing_input,
    build_sample_profit_result_input as intake_profit_input,
    build_sample_unsafe_result_input as intake_unsafe_input,
    intake_oanda_owner_run_live_microtrade_result,
)


VERSION = "oanda_owner_run_live_microtrade_reconciliation_gate_v1"

OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_REQUIRE_MORE_EVIDENCE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_REQUIRE_MORE_EVIDENCE"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_BLOCKED_UNSAFE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_BLOCKED_UNSAFE"
)

REQUIRED_RECONCILIATION_CHECKS = (
    "intake_accepted",
    "planned_instrument_matches_actual_instrument",
    "planned_direction_matches_actual_direction",
    "actual_units_within_max_units",
    "planned_one_shot_equals_confirmed_one_shot",
    "close_time_after_open_time",
    "evidence_references_sanitized",
    "post_trade_capture_complete",
    "no_raw_private_data",
)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeReconciliationGateInput:
    intake_input: Mapping[str, Any] | Any


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeReconciliationGateResult:
    version: str
    classification: str
    intake_status: str
    ready_checks: tuple[str, ...]
    missing_checks: tuple[str, ...]
    blocked_items: tuple[str, ...]
    planned_instrument: str
    actual_instrument: str
    planned_direction: str
    actual_direction: str
    actual_units: Decimal | None
    max_units: Decimal | None
    result_capture_only: bool
    owner_warning: str
    result_warning: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
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
    repeat_live_trade_allowed: bool


def build_sample_profit_result_input() -> OandaOwnerRunLiveMicrotradeReconciliationGateInput:
    return OandaOwnerRunLiveMicrotradeReconciliationGateInput(intake_input=intake_profit_input())


def build_sample_loss_result_input() -> OandaOwnerRunLiveMicrotradeReconciliationGateInput:
    return OandaOwnerRunLiveMicrotradeReconciliationGateInput(intake_input=intake_loss_input())


def build_sample_breakeven_result_input() -> OandaOwnerRunLiveMicrotradeReconciliationGateInput:
    return OandaOwnerRunLiveMicrotradeReconciliationGateInput(intake_input=intake_breakeven_input())


def build_sample_missing_owner_result_input() -> OandaOwnerRunLiveMicrotradeReconciliationGateInput:
    return OandaOwnerRunLiveMicrotradeReconciliationGateInput(intake_input=intake_missing_input())


def build_sample_unsafe_result_input() -> OandaOwnerRunLiveMicrotradeReconciliationGateInput:
    return OandaOwnerRunLiveMicrotradeReconciliationGateInput(intake_input=intake_unsafe_input())


def evaluate_oanda_owner_run_live_microtrade_reconciliation_gate(
    gate_input: OandaOwnerRunLiveMicrotradeReconciliationGateInput | Mapping[str, Any] | None = None,
) -> OandaOwnerRunLiveMicrotradeReconciliationGateResult:
    active_input = _coerce_input(gate_input or build_sample_profit_result_input())
    intake = intake_oanda_owner_run_live_microtrade_result(active_input.intake_input)
    sanitized = dict(intake.sanitized_result_fields)
    ready_checks = _ready_checks(intake, sanitized)
    missing_checks = tuple(
        check for check in REQUIRED_RECONCILIATION_CHECKS if check not in ready_checks
    )
    blocked_items = list(intake.blocked_items)
    if intake.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_BLOCKED_UNSAFE
    elif blocked_items:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_BLOCKED_UNSAFE
    elif missing_checks:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_REQUIRE_MORE_EVIDENCE
    else:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    return OandaOwnerRunLiveMicrotradeReconciliationGateResult(
        version=VERSION,
        classification=classification,
        intake_status=intake.classification,
        ready_checks=ready_checks,
        missing_checks=missing_checks,
        blocked_items=tuple(dict.fromkeys(blocked_items)),
        planned_instrument=text_value(sanitized.get("planned_instrument")),
        actual_instrument=text_value(sanitized.get("instrument")),
        planned_direction=text_value(sanitized.get("planned_direction")),
        actual_direction=text_value(sanitized.get("direction")),
        actual_units=decimal_value(sanitized.get("actual_units")),
        max_units=decimal_value(sanitized.get("max_units")),
        result_capture_only=True,
        owner_warning=EXACT_OWNER_WARNING,
        result_warning=EXACT_RESULT_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaOwnerRunLiveMicrotradeReconciliationGateResult) -> str:
    return "\n".join(
        (
            f"Result reconciliation status: {result.classification}.",
            f"Instrument: planned {result.planned_instrument or 'missing'}, actual {result.actual_instrument or 'missing'}.",
            f"Direction: planned {result.planned_direction or 'missing'}, actual {result.actual_direction or 'missing'}.",
            result.owner_warning,
            result.result_warning,
        )
    )


def to_markdown(result: OandaOwnerRunLiveMicrotradeReconciliationGateResult) -> str:
    rows = [
        "# AIOS Forex OANDA Owner-Run Live Microtrade Reconciliation Gate V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Intake status: `{result.intake_status}`",
        f"- Planned instrument: `{result.planned_instrument}`",
        f"- Actual instrument: `{result.actual_instrument}`",
        f"- Planned direction: `{result.planned_direction}`",
        f"- Actual direction: `{result.actual_direction}`",
        f"- Actual units: `{jsonable(result.actual_units)}`",
        f"- Max units: `{jsonable(result.max_units)}`",
        "",
        "## Ready Checks",
    ]
    rows.extend(f"- `{item}`" for item in result.ready_checks)
    rows.extend(("", "## Missing Checks"))
    rows.extend(f"- `{item}`" for item in result.missing_checks)
    rows.extend(("", "## Blocked Items"))
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaOwnerRunLiveMicrotradeReconciliationGateInput | Mapping[str, Any],
) -> OandaOwnerRunLiveMicrotradeReconciliationGateInput:
    if isinstance(value, OandaOwnerRunLiveMicrotradeReconciliationGateInput):
        return value
    raw = dict(value)
    return OandaOwnerRunLiveMicrotradeReconciliationGateInput(
        intake_input=raw.get("intake_input", raw)
    )


def _ready_checks(intake: Any, sanitized: Mapping[str, Any]) -> tuple[str, ...]:
    checks: list[str] = []
    if intake.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED:
        checks.append("intake_accepted")
    planned_instrument = text_value(sanitized.get("planned_instrument"))
    actual_instrument = text_value(sanitized.get("instrument"))
    if planned_instrument and planned_instrument == actual_instrument:
        checks.append("planned_instrument_matches_actual_instrument")
    planned_direction = text_value(sanitized.get("planned_direction"))
    actual_direction = text_value(sanitized.get("direction"))
    if planned_direction and planned_direction == actual_direction:
        checks.append("planned_direction_matches_actual_direction")
    actual_units = decimal_value(sanitized.get("actual_units"))
    max_units = decimal_value(sanitized.get("max_units"))
    if actual_units is not None and max_units is not None and actual_units <= max_units:
        checks.append("actual_units_within_max_units")
    if (
        sanitized.get("planned_one_shot_only") is True
        and sanitized.get("one_shot_only_confirmed") is True
    ):
        checks.append("planned_one_shot_equals_confirmed_one_shot")
    if _close_time_after_open_time(
        sanitized.get("open_time_utc"),
        sanitized.get("close_time_utc"),
    ):
        checks.append("close_time_after_open_time")
    if _evidence_references_sanitized(sanitized.get("evidence_references_sanitized")):
        checks.append("evidence_references_sanitized")
    if sanitized.get("post_trade_capture_complete") is True:
        checks.append("post_trade_capture_complete")
    if (
        sanitized.get("no_raw_broker_payload") is True
        and sanitized.get("no_account_id_in_payload") is True
        and sanitized.get("no_broker_order_id_in_payload") is True
        and sanitized.get("no_credentials_in_payload") is True
    ):
        checks.append("no_raw_private_data")
    return tuple(dict.fromkeys(checks))


def _close_time_after_open_time(open_time: Any, close_time: Any) -> bool:
    open_dt = _parse_utc_time(open_time)
    close_dt = _parse_utc_time(close_time)
    return bool(open_dt and close_dt and close_dt > open_dt)


def _parse_utc_time(value: Any) -> datetime | None:
    text = text_value(value)
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _evidence_references_sanitized(value: Any) -> bool:
    if not isinstance(value, (tuple, list)) or not value:
        return False
    return all("sanitized" in str(item).strip().lower() for item in value)

