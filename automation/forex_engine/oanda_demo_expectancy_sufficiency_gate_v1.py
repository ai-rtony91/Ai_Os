from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_expectancy_sample_intake_v1 import (
    EXACT_EXPECTANCY_WARNING_TEXT,
    PROTECTED_PERMISSION_DEFAULTS,
)
from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    EXACT_OWNER_WARNING_TEXT,
)
from automation.forex_engine.oanda_demo_repeated_expectancy_accumulator_v1 import (
    OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING,
    OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_STRONG,
    OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_BLOCKED,
    build_oanda_demo_repeated_expectancy_accumulator,
    build_sample_insufficient_accumulator_input,
    build_sample_losing_accumulator_input,
    build_sample_strong_accumulator_input,
    build_sample_unsafe_accumulator_input,
    oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict,
)


VERSION = "oanda_demo_expectancy_sufficiency_gate_v1"
OANDA_DEMO_EXPECTANCY_SUFFICIENCY_GATE_VERSION = VERSION

OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW = (
    "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW"
)
OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE = (
    "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE"
)
OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY = (
    "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY"
)
OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR = (
    "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR"
)
OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_UNSAFE = (
    "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_UNSAFE"
)
OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_INSUFFICIENT_SAMPLE = (
    "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_INSUFFICIENT_SAMPLE"
)


@dataclass(frozen=True)
class OandaDemoExpectancySufficiencyGateConfig:
    min_ready_sample_size: int = 10
    min_more_evidence_sample_size: int = 3
    min_ready_profit_factor: Decimal = Decimal("1.30")
    min_ready_average_r: Decimal = Decimal("0.10")
    min_ready_win_rate: Decimal = Decimal("0.40")


@dataclass(frozen=True)
class OandaDemoExpectancySufficiencyGateInput:
    accumulator_result: Mapping[str, Any]


@dataclass(frozen=True)
class OandaDemoExpectancySufficiencyGateResult:
    version: str
    classification: str
    owner_proof_review_allowed: bool
    requires_more_evidence: bool
    rejected: bool
    ready_blockers: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    metrics_summary: Mapping[str, Any]
    proof_preview_allowed: bool
    live_execution_allowed: bool
    next_safe_action: str
    owner_warning: str
    expectancy_warning: str
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


def build_sample_ready_sufficiency_input() -> OandaDemoExpectancySufficiencyGateInput:
    return _sufficiency_input(build_sample_strong_accumulator_input())


def build_sample_more_evidence_sufficiency_input() -> OandaDemoExpectancySufficiencyGateInput:
    return _sufficiency_input(build_sample_insufficient_accumulator_input())


def build_sample_rejected_sufficiency_input() -> OandaDemoExpectancySufficiencyGateInput:
    return _sufficiency_input(build_sample_losing_accumulator_input())


def build_sample_blocked_sufficiency_input() -> OandaDemoExpectancySufficiencyGateInput:
    return _sufficiency_input(build_sample_unsafe_accumulator_input())


def evaluate_oanda_demo_expectancy_sufficiency(
    gate_input: OandaDemoExpectancySufficiencyGateInput | Mapping[str, Any] | None = None,
    config: OandaDemoExpectancySufficiencyGateConfig | None = None,
) -> OandaDemoExpectancySufficiencyGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_sufficiency_input())
    active_config = config or OandaDemoExpectancySufficiencyGateConfig()
    accumulator = dict(active_input.accumulator_result)
    classification, blockers, gaps = _classification(accumulator, active_config)
    ready = classification == OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW
    more = classification == OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE
    rejected = classification in {
        OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY,
        OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR,
    }
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    return OandaDemoExpectancySufficiencyGateResult(
        version=VERSION,
        classification=classification,
        owner_proof_review_allowed=ready,
        requires_more_evidence=more,
        rejected=rejected,
        ready_blockers=tuple(blockers),
        evidence_gaps=tuple(gaps),
        metrics_summary=_metrics_summary(accumulator),
        proof_preview_allowed=ready,
        live_execution_allowed=False,
        next_safe_action=_next_safe_action(classification),
        owner_warning=EXACT_OWNER_WARNING_TEXT,
        expectancy_warning=EXACT_EXPECTANCY_WARNING_TEXT,
        permissions=permissions,
        **permissions,
    )


def oanda_demo_expectancy_sufficiency_to_jsonable_dict(
    result: OandaDemoExpectancySufficiencyGateResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "classification": result.classification,
        "owner_proof_review_allowed": result.owner_proof_review_allowed,
        "requires_more_evidence": result.requires_more_evidence,
        "rejected": result.rejected,
        "ready_blockers": list(result.ready_blockers),
        "evidence_gaps": list(result.evidence_gaps),
        "metrics_summary": _json_value(result.metrics_summary),
        "proof_preview_allowed": result.proof_preview_allowed,
        "live_execution_allowed": result.live_execution_allowed,
        "next_safe_action": result.next_safe_action,
        "owner_warning": result.owner_warning,
        "expectancy_warning": result.expectancy_warning,
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
        "mutates_existing_ledger_file": False,
        "preview_only": True,
    }


def oanda_demo_expectancy_sufficiency_to_operator_text(
    result: OandaDemoExpectancySufficiencyGateResult,
) -> str:
    return "\n".join(
        (
            f"Repeated expectancy sufficiency status: {result.classification}.",
            f"Owner proof review allowed: {str(result.owner_proof_review_allowed).lower()}.",
            "Repeated expectancy proof is not live execution authority.",
            "No trade placed by this packet.",
            "No broker call made by this packet.",
        )
    )


def oanda_demo_expectancy_sufficiency_to_markdown(
    result: OandaDemoExpectancySufficiencyGateResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Expectancy Sufficiency Gate V1",
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Owner proof review allowed: `{result.owner_proof_review_allowed}`",
        f"- Requires more evidence: `{result.requires_more_evidence}`",
        f"- Rejected: `{result.rejected}`",
        "",
        "## Safety",
        "- Repeated expectancy proof is not live execution authority.",
        "- No trade placed by this packet.",
        "- No broker call made by this packet.",
        "- All protected permission flags remain false.",
    ]
    return "\n".join(lines) + "\n"


def _sufficiency_input(accumulator_input: Any) -> OandaDemoExpectancySufficiencyGateInput:
    result = build_oanda_demo_repeated_expectancy_accumulator(accumulator_input)
    return OandaDemoExpectancySufficiencyGateInput(
        accumulator_result=oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict(result)
    )


def _coerce_input(
    gate_input: OandaDemoExpectancySufficiencyGateInput | Mapping[str, Any],
) -> OandaDemoExpectancySufficiencyGateInput:
    if isinstance(gate_input, OandaDemoExpectancySufficiencyGateInput):
        return gate_input
    raw = dict(gate_input)
    return OandaDemoExpectancySufficiencyGateInput(
        accumulator_result=raw.get("accumulator_result", {})
    )


def _classification(
    accumulator: Mapping[str, Any],
    config: OandaDemoExpectancySufficiencyGateConfig,
) -> tuple[str, list[str], list[str]]:
    status = str(accumulator.get("classification", ""))
    if status == OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_BLOCKED:
        return OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_UNSAFE, ["accumulator_blocked"], []
    result_count = int(accumulator.get("result_count", 0))
    expectancy = _decimal(accumulator.get("expectancy_per_trade", "0"))
    average_r = _decimal(accumulator.get("average_r", "0"))
    win_rate = _decimal(accumulator.get("win_rate", "0"))
    profit_factor = _optional_decimal(accumulator.get("profit_factor"))
    gaps = _evidence_gaps(accumulator, config)
    if result_count <= 0:
        return (
            OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_INSUFFICIENT_SAMPLE,
            ["sample_empty"],
            gaps,
        )
    if expectancy < Decimal("0") or status == OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING:
        return (
            OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY,
            ["negative_expectancy"],
            gaps,
        )
    if (
        result_count >= config.min_ready_sample_size
        and profit_factor is not None
        and profit_factor < config.min_ready_profit_factor
    ):
        return (
            OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR,
            ["profit_factor_below_ready_threshold"],
            gaps,
        )
    if (
        result_count >= config.min_ready_sample_size
        and expectancy > Decimal("0")
        and (profit_factor is None or profit_factor >= config.min_ready_profit_factor)
        and average_r >= config.min_ready_average_r
        and win_rate >= config.min_ready_win_rate
    ):
        return OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW, [], gaps
    if expectancy >= Decimal("0"):
        return OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE, gaps, gaps
    return OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_INSUFFICIENT_SAMPLE, ["unsupported_state"], gaps


def _evidence_gaps(
    accumulator: Mapping[str, Any],
    config: OandaDemoExpectancySufficiencyGateConfig,
) -> list[str]:
    gaps: list[str] = []
    if int(accumulator.get("result_count", 0)) < config.min_ready_sample_size:
        gaps.append("sample_size_below_ready_threshold")
    profit_factor = _optional_decimal(accumulator.get("profit_factor"))
    if profit_factor is not None and profit_factor < config.min_ready_profit_factor:
        gaps.append("profit_factor_below_ready_threshold")
    if _decimal(accumulator.get("average_r", "0")) < config.min_ready_average_r:
        gaps.append("average_r_below_ready_threshold")
    if _decimal(accumulator.get("win_rate", "0")) < config.min_ready_win_rate:
        gaps.append("win_rate_below_ready_threshold")
    return gaps


def _metrics_summary(accumulator: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "classification",
        "result_count",
        "profit_count",
        "loss_count",
        "breakeven_count",
        "win_rate",
        "total_realized_pl",
        "profit_factor",
        "expectancy_per_trade",
        "average_r",
        "best_r",
        "worst_r",
    )
    return {field: accumulator.get(field) for field in fields}


def _next_safe_action(classification: str) -> str:
    if classification == OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW:
        return "Prepare a preview-only proof packet for Anthony's owner review."
    if classification == OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE:
        return "Accumulate more sanitized demo P/L evidence before owner proof review."
    if classification in {
        OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY,
        OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR,
    }:
        return "Reject the sample for profit proof and route to demo review."
    return "Repair unsafe or incomplete expectancy evidence before sufficiency review."


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


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
