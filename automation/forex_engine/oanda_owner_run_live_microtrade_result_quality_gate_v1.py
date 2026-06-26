"""Review-quality gate for owner-run live microtrade result capture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_RESULT_WARNING,
    protected_flags_false,
    jsonable,
    markdown_safety_lines,
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


VERSION = "oanda_owner_run_live_microtrade_result_quality_gate_v1"

OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_REQUIRE_MORE_EVIDENCE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_REQUIRE_MORE_EVIDENCE"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE"
)

REQUIRED_QUALITY_CHECKS = (
    "intake_accepted",
    "trade_closed",
    "realized_pl_present",
    "realized_r_present",
    "spread_observed_present",
    "slippage_observed_present",
    "planned_max_loss_present",
    "one_shot_confirmed",
    "no_repeat_confirmed",
    "evidence_references_sanitized",
    "post_trade_capture_evidence_present",
    "no_protected_flags_true",
)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultQualityGateInput:
    intake_input: Mapping[str, Any] | Any


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultQualityGateResult:
    version: str
    classification: str
    intake_status: str
    ready_checks: tuple[str, ...]
    missing_checks: tuple[str, ...]
    blocked_items: tuple[str, ...]
    owner_review_allowed: bool
    sanitized_result_fields: Mapping[str, Any]
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


def build_sample_profit_result_input() -> OandaOwnerRunLiveMicrotradeResultQualityGateInput:
    return OandaOwnerRunLiveMicrotradeResultQualityGateInput(intake_input=intake_profit_input())


def build_sample_loss_result_input() -> OandaOwnerRunLiveMicrotradeResultQualityGateInput:
    return OandaOwnerRunLiveMicrotradeResultQualityGateInput(intake_input=intake_loss_input())


def build_sample_breakeven_result_input() -> OandaOwnerRunLiveMicrotradeResultQualityGateInput:
    return OandaOwnerRunLiveMicrotradeResultQualityGateInput(intake_input=intake_breakeven_input())


def build_sample_missing_owner_result_input() -> OandaOwnerRunLiveMicrotradeResultQualityGateInput:
    return OandaOwnerRunLiveMicrotradeResultQualityGateInput(intake_input=intake_missing_input())


def build_sample_unsafe_result_input() -> OandaOwnerRunLiveMicrotradeResultQualityGateInput:
    return OandaOwnerRunLiveMicrotradeResultQualityGateInput(intake_input=intake_unsafe_input())


def evaluate_oanda_owner_run_live_microtrade_result_quality_gate(
    gate_input: OandaOwnerRunLiveMicrotradeResultQualityGateInput | Mapping[str, Any] | None = None,
) -> OandaOwnerRunLiveMicrotradeResultQualityGateResult:
    active_input = _coerce_input(gate_input or build_sample_profit_result_input())
    intake = intake_oanda_owner_run_live_microtrade_result(active_input.intake_input)
    sanitized = dict(intake.sanitized_result_fields)
    blocked_items = list(intake.blocked_items)
    ready_checks = _ready_checks(intake, sanitized)
    missing_checks = tuple(
        check for check in REQUIRED_QUALITY_CHECKS if check not in ready_checks
    )
    if intake.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE
    elif blocked_items:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE
    elif missing_checks:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_REQUIRE_MORE_EVIDENCE
    else:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    return OandaOwnerRunLiveMicrotradeResultQualityGateResult(
        version=VERSION,
        classification=classification,
        intake_status=intake.classification,
        ready_checks=ready_checks,
        missing_checks=missing_checks,
        blocked_items=tuple(dict.fromkeys(blocked_items)),
        owner_review_allowed=classification
        == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW,
        sanitized_result_fields=jsonable(sanitized),
        result_capture_only=True,
        owner_warning=EXACT_OWNER_WARNING,
        result_warning=EXACT_RESULT_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaOwnerRunLiveMicrotradeResultQualityGateResult) -> str:
    return "\n".join(
        (
            f"Result quality status: {result.classification}.",
            f"Intake status: {result.intake_status}.",
            "Review-quality does not approve repeat trading.",
            result.owner_warning,
            result.result_warning,
        )
    )


def to_markdown(result: OandaOwnerRunLiveMicrotradeResultQualityGateResult) -> str:
    rows = [
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Quality Gate V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Intake status: `{result.intake_status}`",
        f"- Owner review allowed: `{str(result.owner_review_allowed).lower()}`",
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
    value: OandaOwnerRunLiveMicrotradeResultQualityGateInput | Mapping[str, Any],
) -> OandaOwnerRunLiveMicrotradeResultQualityGateInput:
    if isinstance(value, OandaOwnerRunLiveMicrotradeResultQualityGateInput):
        return value
    raw = dict(value)
    return OandaOwnerRunLiveMicrotradeResultQualityGateInput(
        intake_input=raw.get("intake_input", raw)
    )


def _ready_checks(intake: Any, sanitized: Mapping[str, Any]) -> tuple[str, ...]:
    checks: list[str] = []
    if intake.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED:
        checks.append("intake_accepted")
    if sanitized.get("trade_closed") is True:
        checks.append("trade_closed")
    if sanitized.get("realized_pl") is not None:
        checks.append("realized_pl_present")
    if sanitized.get("realized_r") is not None:
        checks.append("realized_r_present")
    if sanitized.get("spread_observed") is not None:
        checks.append("spread_observed_present")
    if sanitized.get("slippage_observed") is not None:
        checks.append("slippage_observed_present")
    if sanitized.get("planned_max_loss") is not None:
        checks.append("planned_max_loss_present")
    if sanitized.get("one_shot_only_confirmed") is True:
        checks.append("one_shot_confirmed")
    if sanitized.get("no_repeat_execution_confirmed") is True:
        checks.append("no_repeat_confirmed")
    if _evidence_references_sanitized(sanitized.get("evidence_references_sanitized")):
        checks.append("evidence_references_sanitized")
    if sanitized.get("post_trade_capture_evidence_present") is True:
        checks.append("post_trade_capture_evidence_present")
    if all(value is False for value in intake.protected_flags.values()):
        checks.append("no_protected_flags_true")
    return tuple(dict.fromkeys(checks))


def _evidence_references_sanitized(value: Any) -> bool:
    if not isinstance(value, (tuple, list)) or not value:
        return False
    for item in value:
        text = str(item).strip().lower()
        if not text or "sanitized" not in text:
            return False
    return True

