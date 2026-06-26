from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_expectancy_sample_intake_v1 import (
    EXACT_EXPECTANCY_WARNING_TEXT,
    PROTECTED_PERMISSION_DEFAULTS,
    build_sample_insufficient_expectancy_inputs,
    build_sample_losing_expectancy_inputs,
    build_sample_strong_expectancy_inputs,
    build_sample_unsafe_expectancy_inputs,
    build_sample_weak_mixed_expectancy_inputs,
    intake_oanda_demo_expectancy_sample,
    oanda_demo_expectancy_sample_intake_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_expectancy_sufficiency_gate_v1 import (
    OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_UNSAFE,
    OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW,
    OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR,
    OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY,
    OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE,
    evaluate_oanda_demo_expectancy_sufficiency,
    oanda_demo_expectancy_sufficiency_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    EXACT_OWNER_WARNING_TEXT,
)
from automation.forex_engine.oanda_demo_repeated_expectancy_accumulator_v1 import (
    build_oanda_demo_repeated_expectancy_accumulator,
    oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict,
)


VERSION = "oanda_demo_repeated_expectancy_sample_epic_v1"
OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_VERSION = VERSION

PACKET_ID = "AIOS-FOREX-OANDA-DEMO-REPEATED-EXPECTANCY-SAMPLE-ACCUMULATOR-V1"

EXACT_ONE_SENTENCE_ANSWER = (
    "AIOS can now accumulate sanitized OANDA demo P/L results into a repeated "
    "expectancy sample for owner proof review, but live profitable execution "
    "remains blocked until demo proof and live evidence are complete."
)
EXACT_NEXT_OWNER_ACTION = (
    "Review the repeated demo expectancy sample metrics and decide whether the "
    "sample is accurate enough for owner proof review; do not treat it as live "
    "execution authority."
)
EXACT_NEXT_CODEX_PACKET = (
    "AIOS-FOREX-OANDA-DEMO-EXPECTANCY-TO-LIVE-EVIDENCE-BUNDLE-GAP-BRIDGE-V1"
)
LIVE_PROFIT_STATUS = "LIVE_PROFITABLE_EXECUTION_STILL_BLOCKED_PENDING_LIVE_EVIDENCE_BUNDLE"

OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW"
)
OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REQUIRE_MORE_EVIDENCE = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REQUIRE_MORE_EVIDENCE"
)
OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REJECTED = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REJECTED"
)
OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_BLOCKED = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_BLOCKED"
)

BASE_ROUTING_TARGETS = (
    "Profit Proof Ledger",
    "Strategy Proof Engine",
    "Expectancy Strength Router",
    "Real Evidence Depth Engine",
    "Demo Review Engine",
    "Strategy Promotion Router",
)


@dataclass(frozen=True)
class OandaDemoRepeatedExpectancySampleEpicConfig:
    packet_id: str = PACKET_ID


@dataclass(frozen=True)
class OandaDemoRepeatedExpectancySampleEpicInput:
    sample_input: Mapping[str, Any]


@dataclass(frozen=True)
class OandaDemoRepeatedExpectancySampleEpicResult:
    version: str
    packet_id: str
    classification: str
    one_sentence_answer: str
    sample_intake_status: str
    accumulator_status: str
    sufficiency_status: str
    strategy_id: str
    candidate_id: str
    instrument: str
    result_count: int
    profit_count: int
    loss_count: int
    breakeven_count: int
    win_rate: Decimal
    total_realized_pl: Decimal
    profit_factor: Decimal | None
    expectancy_per_trade: Decimal
    average_r: Decimal
    best_r: Decimal | None
    worst_r: Decimal | None
    owner_proof_review_allowed: bool
    requires_more_evidence: bool
    rejected: bool
    proof_packet_preview: Mapping[str, Any]
    routing_targets: tuple[str, ...]
    profit_claim_status: str
    live_profit_status: str
    exact_next_owner_action: str
    exact_next_codex_packet: str
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


def build_sample_strong_repeated_expectancy_epic_input() -> OandaDemoRepeatedExpectancySampleEpicInput:
    return OandaDemoRepeatedExpectancySampleEpicInput(
        sample_input=_input_json(build_sample_strong_expectancy_inputs())
    )


def build_sample_weak_repeated_expectancy_epic_input() -> OandaDemoRepeatedExpectancySampleEpicInput:
    return OandaDemoRepeatedExpectancySampleEpicInput(
        sample_input=_input_json(build_sample_weak_mixed_expectancy_inputs())
    )


def build_sample_insufficient_repeated_expectancy_epic_input() -> OandaDemoRepeatedExpectancySampleEpicInput:
    return OandaDemoRepeatedExpectancySampleEpicInput(
        sample_input=_input_json(build_sample_insufficient_expectancy_inputs())
    )


def build_sample_losing_repeated_expectancy_epic_input() -> OandaDemoRepeatedExpectancySampleEpicInput:
    return OandaDemoRepeatedExpectancySampleEpicInput(
        sample_input=_input_json(build_sample_losing_expectancy_inputs())
    )


def build_sample_unsafe_repeated_expectancy_epic_input() -> OandaDemoRepeatedExpectancySampleEpicInput:
    return OandaDemoRepeatedExpectancySampleEpicInput(
        sample_input=_input_json(build_sample_unsafe_expectancy_inputs())
    )


def run_oanda_demo_repeated_expectancy_sample_epic(
    epic_input: OandaDemoRepeatedExpectancySampleEpicInput | Mapping[str, Any] | None = None,
    config: OandaDemoRepeatedExpectancySampleEpicConfig | None = None,
) -> OandaDemoRepeatedExpectancySampleEpicResult:
    active_config = config or OandaDemoRepeatedExpectancySampleEpicConfig()
    active_input = _coerce_input(epic_input or build_sample_strong_repeated_expectancy_epic_input())
    intake_result = intake_oanda_demo_expectancy_sample(active_input.sample_input)
    intake_json = oanda_demo_expectancy_sample_intake_to_jsonable_dict(intake_result)
    accumulator_result = build_oanda_demo_repeated_expectancy_accumulator(
        {"sample_intake_result": intake_json}
    )
    accumulator_json = oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict(
        accumulator_result
    )
    sufficiency_result = evaluate_oanda_demo_expectancy_sufficiency(
        {"accumulator_result": accumulator_json}
    )
    sufficiency_json = oanda_demo_expectancy_sufficiency_to_jsonable_dict(
        sufficiency_result
    )
    classification = _epic_classification(sufficiency_json)
    routing_targets = _routing_targets(accumulator_json, classification)
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    return OandaDemoRepeatedExpectancySampleEpicResult(
        version=VERSION,
        packet_id=active_config.packet_id,
        classification=classification,
        one_sentence_answer=EXACT_ONE_SENTENCE_ANSWER,
        sample_intake_status=str(intake_json.get("classification", "")),
        accumulator_status=str(accumulator_json.get("classification", "")),
        sufficiency_status=str(sufficiency_json.get("classification", "")),
        strategy_id=str(accumulator_json.get("strategy_id", "")),
        candidate_id=str(accumulator_json.get("candidate_id", "")),
        instrument=str(accumulator_json.get("instrument", "")),
        result_count=int(accumulator_json.get("result_count", 0)),
        profit_count=int(accumulator_json.get("profit_count", 0)),
        loss_count=int(accumulator_json.get("loss_count", 0)),
        breakeven_count=int(accumulator_json.get("breakeven_count", 0)),
        win_rate=_decimal(accumulator_json.get("win_rate", "0")),
        total_realized_pl=_decimal(accumulator_json.get("total_realized_pl", "0")),
        profit_factor=_optional_decimal(accumulator_json.get("profit_factor")),
        expectancy_per_trade=_decimal(accumulator_json.get("expectancy_per_trade", "0")),
        average_r=_decimal(accumulator_json.get("average_r", "0")),
        best_r=_optional_decimal(accumulator_json.get("best_r")),
        worst_r=_optional_decimal(accumulator_json.get("worst_r")),
        owner_proof_review_allowed=bool(sufficiency_json.get("owner_proof_review_allowed", False)),
        requires_more_evidence=bool(sufficiency_json.get("requires_more_evidence", False)),
        rejected=bool(sufficiency_json.get("rejected", False)),
        proof_packet_preview=_proof_packet_preview(
            accumulator_json, sufficiency_json, routing_targets
        ),
        routing_targets=routing_targets,
        profit_claim_status=_profit_claim_status(classification),
        live_profit_status=LIVE_PROFIT_STATUS,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        owner_warning=EXACT_OWNER_WARNING_TEXT,
        expectancy_warning=EXACT_EXPECTANCY_WARNING_TEXT,
        permissions=permissions,
        **permissions,
    )


def oanda_demo_repeated_expectancy_sample_epic_to_jsonable_dict(
    result: OandaDemoRepeatedExpectancySampleEpicResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "packet_id": result.packet_id,
        "classification": result.classification,
        "one_sentence_answer": result.one_sentence_answer,
        "sample_intake_status": result.sample_intake_status,
        "accumulator_status": result.accumulator_status,
        "sufficiency_status": result.sufficiency_status,
        "strategy_id": result.strategy_id,
        "candidate_id": result.candidate_id,
        "instrument": result.instrument,
        "result_count": result.result_count,
        "profit_count": result.profit_count,
        "loss_count": result.loss_count,
        "breakeven_count": result.breakeven_count,
        "win_rate": _json_value(result.win_rate),
        "total_realized_pl": _json_value(result.total_realized_pl),
        "profit_factor": _json_value(result.profit_factor),
        "expectancy_per_trade": _json_value(result.expectancy_per_trade),
        "average_r": _json_value(result.average_r),
        "best_r": _json_value(result.best_r),
        "worst_r": _json_value(result.worst_r),
        "owner_proof_review_allowed": result.owner_proof_review_allowed,
        "requires_more_evidence": result.requires_more_evidence,
        "rejected": result.rejected,
        "proof_packet_preview": _json_value(result.proof_packet_preview),
        "routing_targets": list(result.routing_targets),
        "profit_claim_status": result.profit_claim_status,
        "live_profit_status": result.live_profit_status,
        "exact_next_owner_action": result.exact_next_owner_action,
        "exact_next_codex_packet": result.exact_next_codex_packet,
        "owner_warning": result.owner_warning,
        "expectancy_warning": result.expectancy_warning,
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
        "mutates_existing_ledger_file": False,
        "preview_only": True,
    }


def oanda_demo_repeated_expectancy_sample_epic_to_operator_text(
    result: OandaDemoRepeatedExpectancySampleEpicResult,
) -> str:
    return "\n".join(
        (
            result.one_sentence_answer,
            f"repeated_expectancy_sample_status: {result.classification}",
            f"profit_claim_status: {result.profit_claim_status}",
            f"live_profit_status: {result.live_profit_status}",
            "Repeated expectancy proof is not live execution authority.",
            f"exact_next_owner_action: {result.exact_next_owner_action}",
            f"exact_next_codex_packet: {result.exact_next_codex_packet}",
            "no_trade_placed_by_this_packet: true",
            "no_broker_call_made_by_this_packet: true",
        )
    )


def oanda_demo_repeated_expectancy_sample_epic_to_markdown(
    result: OandaDemoRepeatedExpectancySampleEpicResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Repeated Expectancy Sample Epic V1",
        "",
        "## One Sentence Answer",
        result.one_sentence_answer,
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Result count: `{result.result_count}`",
        f"- Win rate: `{_json_value(result.win_rate)}`",
        f"- Profit factor: `{_json_value(result.profit_factor)}`",
        f"- Expectancy per trade: `{_json_value(result.expectancy_per_trade)}`",
        f"- Average R: `{_json_value(result.average_r)}`",
        f"- Profit claim status: `{result.profit_claim_status}`",
        f"- Live profit status: `{result.live_profit_status}`",
        "",
        "## Authority Boundary",
        "Repeated expectancy proof is not live execution authority.",
        "",
        "## Next Actions",
        f"- Owner: {result.exact_next_owner_action}",
        f"- Codex packet: `{result.exact_next_codex_packet}`",
        "",
        "## Safety",
        "- No trade placed by this packet.",
        "- No broker call made by this packet.",
        "- All protected permission flags remain false.",
    ]
    return "\n".join(lines) + "\n"


def _input_json(sample_input: Any) -> dict[str, Any]:
    return {"result_intake_objects": list(sample_input.result_intake_objects)}


def _coerce_input(
    epic_input: OandaDemoRepeatedExpectancySampleEpicInput | Mapping[str, Any],
) -> OandaDemoRepeatedExpectancySampleEpicInput:
    if isinstance(epic_input, OandaDemoRepeatedExpectancySampleEpicInput):
        return epic_input
    raw = dict(epic_input)
    return OandaDemoRepeatedExpectancySampleEpicInput(
        sample_input=raw.get("sample_input", {})
    )


def _epic_classification(sufficiency: Mapping[str, Any]) -> str:
    status = str(sufficiency.get("classification", ""))
    if status == OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW:
        return OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW
    if status == OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE:
        return OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REQUIRE_MORE_EVIDENCE
    if status in {
        OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY,
        OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR,
    }:
        return OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REJECTED
    if status == OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_UNSAFE:
        return OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_BLOCKED
    return OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_BLOCKED


def _profit_claim_status(classification: str) -> str:
    if classification == OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW:
        return "REPEATED_EXPECTANCY_READY_FOR_OWNER_PROOF_REVIEW"
    if classification == OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REQUIRE_MORE_EVIDENCE:
        return "REPEATED_EXPECTANCY_REQUIRE_MORE_EVIDENCE"
    if classification == OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REJECTED:
        return "REPEATED_EXPECTANCY_REJECTED"
    return "REPEATED_EXPECTANCY_BLOCKED"


def _routing_targets(
    accumulator: Mapping[str, Any], classification: str
) -> tuple[str, ...]:
    targets = list(BASE_ROUTING_TARGETS)
    if classification == OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REJECTED or int(accumulator.get("loss_count", 0)) > 0:
        targets.append("Loss To Next Profit Candidate Gate")
    return tuple(targets)


def _proof_packet_preview(
    accumulator: Mapping[str, Any],
    sufficiency: Mapping[str, Any],
    routing_targets: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "preview_only": True,
        "mutates_existing_ledger_file": False,
        "proof_type": "repeated_demo_expectancy_sample",
        "strategy_id": accumulator.get("strategy_id", ""),
        "candidate_id": accumulator.get("candidate_id", ""),
        "instrument": accumulator.get("instrument", ""),
        "metrics_summary": sufficiency.get("metrics_summary", {}),
        "owner_proof_review_allowed": sufficiency.get("owner_proof_review_allowed", False),
        "repeated_demo_proof_only": True,
        "live_execution_authority": False,
        "routing_targets": list(routing_targets),
    }


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
