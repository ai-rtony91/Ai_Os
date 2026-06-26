from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN,
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS,
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT,
    OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE,
    OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_MISSING_RECONCILIATION,
    OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_NOT_SANITIZED,
    OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE,
    PROTECTED_PERMISSION_DEFAULTS,
    RESULT_BUCKET_BREAKEVEN,
    RESULT_BUCKET_LOSS,
    RESULT_BUCKET_PROFIT,
    build_sample_breakeven_pl_evidence,
    build_sample_incomplete_pl_evidence,
    build_sample_loss_pl_evidence,
    build_sample_profit_pl_evidence,
    build_sample_unsafe_pl_evidence,
    intake_oanda_demo_read_only_pl_result,
)

VERSION = "oanda_demo_pl_result_quality_gate_v1"
OANDA_DEMO_PL_RESULT_QUALITY_GATE_VERSION = VERSION

OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY = (
    "OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY"
)
OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY = (
    "OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY"
)
OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE = (
    "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE"
)
OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE = (
    "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE"
)
OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL = (
    "OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL"
)


@dataclass(frozen=True)
class OandaDemoPlResultQualityGateConfig:
    min_abs_r_for_proof_ready: Decimal = Decimal("0.25")
    max_entry_slippage_abs: Decimal = Decimal("0.0005")
    require_reconciliation: bool = True
    require_sanitized: bool = True
    allow_loss_for_review: bool = True
    strict_low_signal_blocks_profit: bool = False


@dataclass(frozen=True)
class OandaDemoPlResultQualityGateInput:
    intake_result: Mapping[str, Any]
    min_abs_r_for_proof_ready: Decimal = Decimal("0.25")
    max_entry_slippage_abs: Decimal = Decimal("0.0005")
    require_reconciliation: bool = True
    require_sanitized: bool = True
    allow_loss_for_review: bool = True
    strict_low_signal_blocks_profit: bool = False


@dataclass(frozen=True)
class OandaDemoPlResultQualityGateResult:
    version: str
    classification: str
    quality_review_allowed: bool
    proof_routing_allowed: bool
    result_bucket: str
    realized_pl: Decimal | None
    realized_r_multiple: Decimal | None
    quality_notes: tuple[str, ...]
    blockers: tuple[str, ...]
    next_safe_action: str
    permissions: Mapping[str, bool]
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


def build_sample_profit_quality_input() -> OandaDemoPlResultQualityGateInput:
    return OandaDemoPlResultQualityGateInput(
        intake_result=_intake_json(build_sample_profit_pl_evidence())
    )


def build_sample_loss_quality_input() -> OandaDemoPlResultQualityGateInput:
    return OandaDemoPlResultQualityGateInput(
        intake_result=_intake_json(build_sample_loss_pl_evidence())
    )


def build_sample_breakeven_quality_input() -> OandaDemoPlResultQualityGateInput:
    return OandaDemoPlResultQualityGateInput(
        intake_result=_intake_json(build_sample_breakeven_pl_evidence())
    )


def build_sample_incomplete_quality_input() -> OandaDemoPlResultQualityGateInput:
    return OandaDemoPlResultQualityGateInput(
        intake_result=_intake_json(build_sample_incomplete_pl_evidence())
    )


def evaluate_oanda_demo_pl_result_quality(
    quality_input: OandaDemoPlResultQualityGateInput | Mapping[str, Any] | None = None,
    config: OandaDemoPlResultQualityGateConfig | None = None,
) -> OandaDemoPlResultQualityGateResult:
    active_input = _coerce_input(quality_input or build_sample_profit_quality_input())
    active_config = config or OandaDemoPlResultQualityGateConfig(
        min_abs_r_for_proof_ready=active_input.min_abs_r_for_proof_ready,
        max_entry_slippage_abs=active_input.max_entry_slippage_abs,
        require_reconciliation=active_input.require_reconciliation,
        require_sanitized=active_input.require_sanitized,
        allow_loss_for_review=active_input.allow_loss_for_review,
        strict_low_signal_blocks_profit=active_input.strict_low_signal_blocks_profit,
    )
    intake_result = dict(active_input.intake_result)
    classification, blockers, notes = _classification(intake_result, active_config)
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    return OandaDemoPlResultQualityGateResult(
        version=VERSION,
        classification=classification,
        quality_review_allowed=classification
        in {
            OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY,
            OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY,
        },
        proof_routing_allowed=classification == OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY,
        result_bucket=str(intake_result.get("result_bucket", "")),
        realized_pl=_optional_decimal(intake_result.get("realized_pl")),
        realized_r_multiple=_optional_decimal(intake_result.get("realized_r_multiple")),
        quality_notes=tuple(notes),
        blockers=tuple(blockers),
        next_safe_action=_next_safe_action(classification),
        permissions=permissions,
        **permissions,
    )


def oanda_demo_pl_result_quality_to_jsonable_dict(
    result: OandaDemoPlResultQualityGateResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "classification": result.classification,
        "quality_review_allowed": result.quality_review_allowed,
        "proof_routing_allowed": result.proof_routing_allowed,
        "result_bucket": result.result_bucket,
        "realized_pl": _json_value(result.realized_pl),
        "realized_r_multiple": _json_value(result.realized_r_multiple),
        "quality_notes": list(result.quality_notes),
        "blockers": list(result.blockers),
        "next_safe_action": result.next_safe_action,
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
    }


def oanda_demo_pl_result_quality_to_operator_text(
    result: OandaDemoPlResultQualityGateResult,
) -> str:
    return "\n".join(
        (
            f"P/L quality status: {result.classification}.",
            f"Result bucket: {result.result_bucket}.",
            f"Proof routing allowed: {str(result.proof_routing_allowed).lower()}.",
            "No trade placed by this packet.",
            "No broker call made by this packet.",
        )
    )


def oanda_demo_pl_result_quality_to_markdown(
    result: OandaDemoPlResultQualityGateResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo P/L Result Quality Gate V1",
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Quality review allowed: `{result.quality_review_allowed}`",
        f"- Proof routing allowed: `{result.proof_routing_allowed}`",
        f"- Realized R multiple: `{_json_value(result.realized_r_multiple)}`",
        "",
        "## Notes",
    ]
    lines.extend(f"- {note}" for note in result.quality_notes)
    lines.extend(
        [
            "",
            "## Safety",
            "- No trade placed by this packet.",
            "- No broker call made by this packet.",
            "- All protected permission flags remain false.",
        ]
    )
    return "\n".join(lines) + "\n"


def _intake_json(evidence: Any) -> dict[str, Any]:
    from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
        oanda_demo_read_only_pl_result_intake_to_jsonable_dict,
    )

    return oanda_demo_read_only_pl_result_intake_to_jsonable_dict(
        intake_oanda_demo_read_only_pl_result(evidence)
    )


def _coerce_input(
    quality_input: OandaDemoPlResultQualityGateInput | Mapping[str, Any],
) -> OandaDemoPlResultQualityGateInput:
    if isinstance(quality_input, OandaDemoPlResultQualityGateInput):
        return quality_input
    raw = dict(quality_input)
    return OandaDemoPlResultQualityGateInput(
        intake_result=raw.get("intake_result", {}),
        min_abs_r_for_proof_ready=Decimal(str(raw.get("min_abs_r_for_proof_ready", "0.25"))),
        max_entry_slippage_abs=Decimal(str(raw.get("max_entry_slippage_abs", "0.0005"))),
        require_reconciliation=bool(raw.get("require_reconciliation", True)),
        require_sanitized=bool(raw.get("require_sanitized", True)),
        allow_loss_for_review=bool(raw.get("allow_loss_for_review", True)),
        strict_low_signal_blocks_profit=bool(
            raw.get("strict_low_signal_blocks_profit", False)
        ),
    )


def _classification(
    intake_result: Mapping[str, Any],
    config: OandaDemoPlResultQualityGateConfig,
) -> tuple[str, list[str], list[str]]:
    intake_classification = str(intake_result.get("classification", ""))
    result_bucket = str(intake_result.get("result_bucket", ""))
    realized_r = _optional_decimal(intake_result.get("realized_r_multiple"))
    notes = ["local preview only", "one result does not prove repeated expectancy"]
    blockers: list[str] = []
    if intake_classification in {
        OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE,
        OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_NOT_SANITIZED,
    }:
        return OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE, ["intake_result_unsafe"], notes
    if intake_classification in {
        OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE,
        OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_MISSING_RECONCILIATION,
    }:
        return (
            OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE,
            ["intake_result_incomplete_or_unreconciled"],
            notes,
        )
    if result_bucket == RESULT_BUCKET_PROFIT:
        if realized_r is None:
            return OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE, ["r_multiple_missing"], notes
        if abs(realized_r) >= config.min_abs_r_for_proof_ready:
            notes.append("profit sample clears minimum R threshold")
            return OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY, blockers, notes
        notes.append("profit sample is below minimum R threshold")
        if config.strict_low_signal_blocks_profit:
            return OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL, ["profit_r_below_threshold"], notes
        return OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY, blockers, notes
    if result_bucket in {RESULT_BUCKET_LOSS, RESULT_BUCKET_BREAKEVEN}:
        notes.append("accepted non-profit sample is review-ready evidence only")
        if result_bucket == RESULT_BUCKET_LOSS and not config.allow_loss_for_review:
            return (
                OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL,
                ["loss_review_disabled"],
                notes,
            )
        return OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY, blockers, notes
    return OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE, ["unsupported_result_bucket"], notes


def _next_safe_action(classification: str) -> str:
    if classification == OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY:
        return "Route the first result into proof ledger preview for owner review."
    if classification == OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY:
        return "Route the result into review evidence, not a profit claim."
    if classification == OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL:
        return "Collect clearer P/L evidence or lower-signal review before proof routing."
    return "Repair the P/L intake result before quality review continues."


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_json_value(child) for child in value]
    if isinstance(value, list):
        return [_json_value(child) for child in value]
    return value
