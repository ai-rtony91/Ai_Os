"""Top-level preview-only bridge from demo expectancy proof to live evidence gaps."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_expectancy_to_live_gap_mapper_v1 import (
    OandaDemoExpectancyToLiveGapMapperInput,
    build_sample_blocked_expectancy_gap_mapper_input,
    build_sample_missing_live_evidence_gap_mapper_input,
    build_sample_partial_live_evidence_gap_mapper_input,
    build_sample_ready_gap_mapper_input,
    build_sample_unsafe_gap_mapper_input,
    map_oanda_demo_expectancy_to_live_evidence_gaps,
    oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_live_evidence_bundle_gap_gate_v1 import (
    CLASSIFICATION_BLOCKED_EXPECTANCY as GATE_BLOCKED_EXPECTANCY,
    CLASSIFICATION_BLOCKED_UNSAFE as GATE_BLOCKED_UNSAFE,
    CLASSIFICATION_OWNER_REVIEW_READY as GATE_OWNER_REVIEW_READY,
    CLASSIFICATION_REQUIRE_MORE_EVIDENCE as GATE_REQUIRE_MORE_EVIDENCE,
    OandaDemoLiveEvidenceBundleGapGateInput,
    evaluate_oanda_demo_live_evidence_bundle_gap_gate,
    oanda_demo_live_evidence_bundle_gap_gate_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_live_evidence_requirement_matrix_v1 import (
    LIVE_GAP_WARNING,
    OWNER_WARNING,
    PERMISSION_DEFAULTS,
    build_oanda_demo_live_evidence_requirement_matrix,
    oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict,
)


OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_EPIC_VERSION = (
    "oanda_demo_expectancy_to_live_evidence_bundle_epic_v1"
)
VERSION = OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_EPIC_VERSION

CLASSIFICATION_READY_FOR_OWNER_REVIEW = (
    "OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_GAP_READY_FOR_OWNER_REVIEW"
)
CLASSIFICATION_REQUIRE_MORE_EVIDENCE = (
    "OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_GAP_REQUIRE_MORE_EVIDENCE"
)
CLASSIFICATION_BLOCKED = "OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_GAP_BLOCKED"

ONE_SENTENCE_ANSWER = (
    "AIOS can now map repeated demo expectancy proof into the live evidence bundle gap checklist, "
    "but live profitable execution remains blocked until every required live evidence item is complete "
    "and separately approved by Anthony."
)
PROFIT_CLAIM_STATUS = "REPEATED_EXPECTANCY_OWNER_PROOF_REVIEW_READY_BUT_NOT_LIVE_AUTHORITY"
LIVE_PROFIT_STATUS = (
    "LIVE_PROFITABLE_EXECUTION_BLOCKED_PENDING_COMPLETE_LIVE_EVIDENCE_BUNDLE_AND_OWNER_EXCEPTION"
)
EXACT_NEXT_OWNER_ACTION = (
    "Review the live evidence bundle gap map and complete or reject each missing live evidence item; "
    "do not treat the gap map as live trading approval."
)
EXACT_NEXT_CODEX_PACKET = "AIOS-FOREX-OANDA-DEMO-LIVE-EVIDENCE-BUNDLE-ASSEMBLER-V1"


@dataclass(frozen=True)
class OandaDemoExpectancyToLiveEvidenceBundleEpicConfig:
    packet_id: str = (
        "AIOS-FOREX-OANDA-DEMO-EXPECTANCY-TO-LIVE-EVIDENCE-BUNDLE-GAP-BRIDGE-V1"
    )


@dataclass(frozen=True)
class OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    mapper_input: OandaDemoExpectancyToLiveGapMapperInput
    config: OandaDemoExpectancyToLiveEvidenceBundleEpicConfig = field(
        default_factory=OandaDemoExpectancyToLiveEvidenceBundleEpicConfig
    )


@dataclass(frozen=True)
class OandaDemoExpectancyToLiveEvidenceBundleEpicResult:
    version: str
    packet_id: str
    classification: str
    one_sentence_answer: str
    expectancy_status: str
    requirement_matrix_status: str
    gap_mapper_status: str
    gap_gate_status: str
    requirement_count: int
    present_count: int
    missing_count: int
    blocked_count: int
    owner_action_required_count: int
    missing_items: tuple[str, ...]
    owner_action_required_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    live_evidence_bundle_preview: Mapping[str, Any]
    owner_gap_review_allowed: bool
    live_execution_allowed: bool
    live_micro_trade_exception_allowed: bool
    live_evidence_bundle_approved: bool
    profit_claim_status: str
    live_profit_status: str
    exact_next_owner_action: str
    exact_next_codex_packet: str
    owner_warning: str
    live_gap_warning: str
    protected_permission_flags: Mapping[str, bool]
    present_ratio: Decimal


def build_sample_missing_live_evidence_epic_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return OandaDemoExpectancyToLiveEvidenceBundleEpicInput(
        mapper_input=build_sample_missing_live_evidence_gap_mapper_input()
    )


def build_sample_partial_live_evidence_epic_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return OandaDemoExpectancyToLiveEvidenceBundleEpicInput(
        mapper_input=build_sample_partial_live_evidence_gap_mapper_input()
    )


def build_sample_ready_live_gap_review_epic_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return OandaDemoExpectancyToLiveEvidenceBundleEpicInput(
        mapper_input=build_sample_ready_gap_mapper_input()
    )


def build_sample_blocked_expectancy_epic_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return OandaDemoExpectancyToLiveEvidenceBundleEpicInput(
        mapper_input=build_sample_blocked_expectancy_gap_mapper_input()
    )


def build_sample_unsafe_live_evidence_epic_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return OandaDemoExpectancyToLiveEvidenceBundleEpicInput(
        mapper_input=build_sample_unsafe_gap_mapper_input()
    )


def build_sample_strong_expectancy_missing_live_evidence_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return build_sample_missing_live_evidence_epic_input()


def build_sample_strong_expectancy_partial_live_evidence_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return build_sample_partial_live_evidence_epic_input()


def build_sample_weak_expectancy_blocked_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return build_sample_blocked_expectancy_epic_input()


def build_sample_rejected_expectancy_blocked_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return build_sample_blocked_expectancy_epic_input()


def build_sample_unsafe_expectancy_blocked_input() -> OandaDemoExpectancyToLiveEvidenceBundleEpicInput:
    return build_sample_unsafe_live_evidence_epic_input()


def run_oanda_demo_expectancy_to_live_evidence_bundle_epic(
    epic_input: OandaDemoExpectancyToLiveEvidenceBundleEpicInput,
) -> OandaDemoExpectancyToLiveEvidenceBundleEpicResult:
    requirement_matrix_result = build_oanda_demo_live_evidence_requirement_matrix()
    mapper_result = map_oanda_demo_expectancy_to_live_evidence_gaps(epic_input.mapper_input)
    gate_result = evaluate_oanda_demo_live_evidence_bundle_gap_gate(
        OandaDemoLiveEvidenceBundleGapGateInput(gap_mapper_result=mapper_result)
    )
    if gate_result.classification == GATE_OWNER_REVIEW_READY:
        classification = CLASSIFICATION_READY_FOR_OWNER_REVIEW
    elif gate_result.classification == GATE_REQUIRE_MORE_EVIDENCE:
        classification = CLASSIFICATION_REQUIRE_MORE_EVIDENCE
    elif gate_result.classification in (GATE_BLOCKED_EXPECTANCY, GATE_BLOCKED_UNSAFE):
        classification = CLASSIFICATION_BLOCKED
    else:
        classification = CLASSIFICATION_BLOCKED
    preview = {
        "preview_only": True,
        "requirement_matrix_result": oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict(
            requirement_matrix_result
        ),
        "gap_mapper_result": oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
            mapper_result
        ),
        "gap_gate_result": oanda_demo_live_evidence_bundle_gap_gate_to_jsonable_dict(gate_result),
        "ready_gap_review_is_not_live_approval": True,
        "live_execution_allowed": False,
        "live_micro_trade_exception_allowed": False,
        "live_evidence_bundle_approved": False,
    }
    present_ratio = (
        Decimal(mapper_result.present_count) / Decimal(mapper_result.requirement_count)
        if mapper_result.requirement_count
        else Decimal("0")
    )
    return OandaDemoExpectancyToLiveEvidenceBundleEpicResult(
        version=VERSION,
        packet_id=epic_input.config.packet_id,
        classification=classification,
        one_sentence_answer=ONE_SENTENCE_ANSWER,
        expectancy_status=mapper_result.expectancy_status,
        requirement_matrix_status=requirement_matrix_result.classification,
        gap_mapper_status=mapper_result.classification,
        gap_gate_status=gate_result.classification,
        requirement_count=mapper_result.requirement_count,
        present_count=mapper_result.present_count,
        missing_count=mapper_result.missing_count,
        blocked_count=mapper_result.blocked_count,
        owner_action_required_count=mapper_result.owner_action_required_count,
        missing_items=mapper_result.missing_items,
        owner_action_required_items=mapper_result.owner_action_required_items,
        blocked_items=mapper_result.blocked_items,
        live_evidence_bundle_preview=preview,
        owner_gap_review_allowed=gate_result.owner_gap_review_allowed,
        live_execution_allowed=False,
        live_micro_trade_exception_allowed=False,
        live_evidence_bundle_approved=False,
        profit_claim_status=PROFIT_CLAIM_STATUS,
        live_profit_status=LIVE_PROFIT_STATUS,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        owner_warning=OWNER_WARNING,
        live_gap_warning=LIVE_GAP_WARNING,
        protected_permission_flags=dict(PERMISSION_DEFAULTS),
        present_ratio=present_ratio,
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def oanda_demo_expectancy_to_live_evidence_bundle_epic_to_jsonable_dict(
    result: OandaDemoExpectancyToLiveEvidenceBundleEpicResult,
) -> dict[str, Any]:
    return _jsonable(result)


def oanda_demo_expectancy_to_live_evidence_bundle_epic_to_operator_text(
    result: OandaDemoExpectancyToLiveEvidenceBundleEpicResult,
) -> str:
    return "\n".join(
        (
            f"Expectancy-to-live evidence bundle epic status: {result.classification}.",
            result.one_sentence_answer,
            f"Expectancy status: {result.expectancy_status}.",
            f"Requirement matrix status: {result.requirement_matrix_status}.",
            f"Gap mapper status: {result.gap_mapper_status}.",
            f"Gap gate status: {result.gap_gate_status}.",
            "Ready gap review is not live approval.",
            result.owner_warning,
            result.live_gap_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "Live profitable execution remains blocked.",
            f"Exact next owner action: {result.exact_next_owner_action}",
            f"Exact next Codex packet: {result.exact_next_codex_packet}",
        )
    )


def oanda_demo_expectancy_to_live_evidence_bundle_epic_to_markdown(
    result: OandaDemoExpectancyToLiveEvidenceBundleEpicResult,
) -> str:
    rows = [
        "# OANDA Demo Expectancy To Live Evidence Bundle Epic Report V1",
        "",
        f"- Packet ID: {result.packet_id}",
        f"- Classification: {result.classification}",
        f"- One sentence answer: {result.one_sentence_answer}",
        f"- Expectancy status: {result.expectancy_status}",
        f"- Requirement matrix status: {result.requirement_matrix_status}",
        f"- Gap mapper status: {result.gap_mapper_status}",
        f"- Gap gate status: {result.gap_gate_status}",
        f"- Requirement count: {result.requirement_count}",
        f"- Present: {result.present_count}",
        f"- Missing: {result.missing_count}",
        f"- Blocked: {result.blocked_count}",
        f"- Owner action required: {result.owner_action_required_count}",
        f"- Owner gap review allowed: {str(result.owner_gap_review_allowed).lower()}",
        "- Live execution allowed: false",
        "- Live micro-trade exception allowed: false",
        "- Live evidence bundle approved: false",
        "- Ready gap review is not live approval.",
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- Live profitable execution remains blocked.",
        f"- Profit claim status: {result.profit_claim_status}",
        f"- Live profit status: {result.live_profit_status}",
        f"- Exact next owner action: {result.exact_next_owner_action}",
        f"- Exact next Codex packet: {result.exact_next_codex_packet}",
        "",
        "## Evidence Gaps",
        f"- Missing items: {', '.join(result.missing_items) if result.missing_items else 'none'}",
        (
            "- Owner action required items: "
            f"{', '.join(result.owner_action_required_items) if result.owner_action_required_items else 'none'}"
        ),
        f"- Blocked items: {', '.join(result.blocked_items) if result.blocked_items else 'none'}",
        "",
        "## Permissions",
    ]
    for key in sorted(result.protected_permission_flags):
        rows.append(f"- `{key}`: {str(result.protected_permission_flags[key]).lower()}")
    return "\n".join(rows) + "\n"
