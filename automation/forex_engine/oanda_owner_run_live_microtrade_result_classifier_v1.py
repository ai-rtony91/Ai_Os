"""Outcome classifier for one captured owner-run live microtrade result."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_RESULT_WARNING,
    decimal_value,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_quality_gate_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW,
    build_sample_breakeven_result_input as quality_breakeven_input,
    build_sample_loss_result_input as quality_loss_input,
    build_sample_missing_owner_result_input as quality_missing_input,
    build_sample_profit_result_input as quality_profit_input,
    build_sample_unsafe_result_input as quality_unsafe_input,
    evaluate_oanda_owner_run_live_microtrade_result_quality_gate,
)


VERSION = "oanda_owner_run_live_microtrade_result_classifier_v1"

OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_REQUIRE_MORE_EVIDENCE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_REQUIRE_MORE_EVIDENCE"
)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultClassifierInput:
    quality_gate_input: Mapping[str, Any] | Any


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultClassifierResult:
    version: str
    classification: str
    quality_gate_status: str
    intake_status: str
    realized_pl: Decimal | None
    realized_r: Decimal | None
    planned_max_loss: Decimal | None
    max_loss_respected: bool
    risk_limit_respected: bool
    risk_breach: bool
    result_bucket: str
    profit_loss_label: str
    owner_review_summary: str
    blocked_items: tuple[str, ...]
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


def build_sample_profit_result_input() -> OandaOwnerRunLiveMicrotradeResultClassifierInput:
    return OandaOwnerRunLiveMicrotradeResultClassifierInput(
        quality_gate_input=quality_profit_input()
    )


def build_sample_loss_result_input() -> OandaOwnerRunLiveMicrotradeResultClassifierInput:
    return OandaOwnerRunLiveMicrotradeResultClassifierInput(
        quality_gate_input=quality_loss_input()
    )


def build_sample_breakeven_result_input() -> OandaOwnerRunLiveMicrotradeResultClassifierInput:
    return OandaOwnerRunLiveMicrotradeResultClassifierInput(
        quality_gate_input=quality_breakeven_input()
    )


def build_sample_missing_owner_result_input() -> OandaOwnerRunLiveMicrotradeResultClassifierInput:
    return OandaOwnerRunLiveMicrotradeResultClassifierInput(
        quality_gate_input=quality_missing_input()
    )


def build_sample_unsafe_result_input() -> OandaOwnerRunLiveMicrotradeResultClassifierInput:
    return OandaOwnerRunLiveMicrotradeResultClassifierInput(
        quality_gate_input=quality_unsafe_input()
    )


def classify_oanda_owner_run_live_microtrade_result(
    classifier_input: OandaOwnerRunLiveMicrotradeResultClassifierInput | Mapping[str, Any] | None = None,
) -> OandaOwnerRunLiveMicrotradeResultClassifierResult:
    active_input = _coerce_input(classifier_input or build_sample_profit_result_input())
    quality = evaluate_oanda_owner_run_live_microtrade_result_quality_gate(
        active_input.quality_gate_input
    )
    sanitized = dict(quality.sanitized_result_fields)
    realized_pl = decimal_value(sanitized.get("realized_pl"))
    realized_r = decimal_value(sanitized.get("realized_r"))
    planned_max_loss = decimal_value(sanitized.get("planned_max_loss"))
    max_loss_respected = _max_loss_respected(realized_pl, planned_max_loss)
    risk_breach = (
        quality.classification
        == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW
        and realized_pl is not None
        and planned_max_loss is not None
        and not max_loss_respected
    )
    blocked_items = list(quality.blocked_items)
    if risk_breach:
        blocked_items.append("loss_exceeds_planned_max_loss")
    if quality.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE
    elif risk_breach:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE
    elif quality.classification != OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_REQUIRE_MORE_EVIDENCE
    elif realized_pl is None or realized_r is None:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_REQUIRE_MORE_EVIDENCE
    elif realized_pl > Decimal("0"):
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT
    elif realized_pl < Decimal("0"):
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS
    else:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN
    result_bucket = _result_bucket(classification)
    protected_flags = protected_flags_false()
    return OandaOwnerRunLiveMicrotradeResultClassifierResult(
        version=VERSION,
        classification=classification,
        quality_gate_status=quality.classification,
        intake_status=quality.intake_status,
        realized_pl=realized_pl,
        realized_r=realized_r,
        planned_max_loss=planned_max_loss,
        max_loss_respected=max_loss_respected,
        risk_limit_respected=max_loss_respected,
        risk_breach=risk_breach,
        result_bucket=result_bucket,
        profit_loss_label=_profit_loss_label(classification),
        owner_review_summary=_owner_review_summary(classification),
        blocked_items=tuple(dict.fromkeys(blocked_items)),
        result_capture_only=True,
        owner_warning=EXACT_OWNER_WARNING,
        result_warning=EXACT_RESULT_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaOwnerRunLiveMicrotradeResultClassifierResult) -> str:
    return "\n".join(
        (
            f"Result classifier status: {result.classification}.",
            f"Intake status: {result.intake_status}.",
            f"Result bucket: {result.result_bucket}.",
            result.owner_review_summary,
            "Profit, if present, does not approve repeat trading.",
            result.owner_warning,
            result.result_warning,
        )
    )


def to_markdown(result: OandaOwnerRunLiveMicrotradeResultClassifierResult) -> str:
    rows = [
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Classifier V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Intake status: `{result.intake_status}`",
        f"- Result bucket: `{result.result_bucket}`",
        f"- Realized P/L: `{jsonable(result.realized_pl)}`",
        f"- Realized R: `{jsonable(result.realized_r)}`",
        f"- Planned max loss: `{jsonable(result.planned_max_loss)}`",
        f"- Max loss respected: `{str(result.max_loss_respected).lower()}`",
        f"- Risk breach: `{str(result.risk_breach).lower()}`",
        f"- Owner review summary: {result.owner_review_summary}",
        "",
        "## Blocked Items",
    ]
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaOwnerRunLiveMicrotradeResultClassifierInput | Mapping[str, Any],
) -> OandaOwnerRunLiveMicrotradeResultClassifierInput:
    if isinstance(value, OandaOwnerRunLiveMicrotradeResultClassifierInput):
        return value
    raw = dict(value)
    return OandaOwnerRunLiveMicrotradeResultClassifierInput(
        quality_gate_input=raw.get("quality_gate_input", raw)
    )


def _max_loss_respected(
    realized_pl: Decimal | None,
    planned_max_loss: Decimal | None,
) -> bool:
    if realized_pl is None or planned_max_loss is None:
        return False
    if planned_max_loss <= Decimal("0"):
        return False
    if realized_pl >= Decimal("0"):
        return True
    return abs(realized_pl) <= planned_max_loss


def _result_bucket(classification: str) -> str:
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT:
        return "profit"
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS:
        return "loss"
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN:
        return "breakeven"
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE:
        return "unsafe"
    return "requires_more_evidence"


def _profit_loss_label(classification: str) -> str:
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT:
        return "profit"
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS:
        return "loss"
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN:
        return "breakeven"
    return "not_classified"


def _owner_review_summary(classification: str) -> str:
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT:
        return "Profit result routes to live proof candidate review; repeat trading remains blocked."
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS:
        return "Loss result routes to loss review and next profit candidate gate."
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN:
        return "Breakeven result routes to more evidence before any next proof step."
    if classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE:
        return "Unsafe result blocks routing until repaired by owner review."
    return "Incomplete result requires more evidence before classification."
