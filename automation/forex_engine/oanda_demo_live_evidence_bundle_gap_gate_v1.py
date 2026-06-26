"""Gate preview-only live evidence bundle gaps for owner review readiness."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_expectancy_to_live_gap_mapper_v1 import (
    CLASSIFICATION_BLOCKED_EXPECTANCY as MAPPER_BLOCKED_EXPECTANCY,
    CLASSIFICATION_BLOCKED_UNSAFE as MAPPER_BLOCKED_UNSAFE,
    CLASSIFICATION_MISSING as MAPPER_MISSING,
    CLASSIFICATION_PARTIAL as MAPPER_PARTIAL,
    CLASSIFICATION_READY as MAPPER_READY,
    OandaDemoExpectancyToLiveGapMapperResult,
    build_sample_blocked_expectancy_gap_mapper_input,
    build_sample_missing_live_evidence_gap_mapper_input,
    build_sample_partial_live_evidence_gap_mapper_input,
    build_sample_ready_gap_mapper_input,
    build_sample_unsafe_gap_mapper_input,
    map_oanda_demo_expectancy_to_live_evidence_gaps,
    oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_live_evidence_requirement_matrix_v1 import (
    LIVE_GAP_WARNING,
    OWNER_WARNING,
    PERMISSION_DEFAULTS,
)


OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_VERSION = (
    "oanda_demo_live_evidence_bundle_gap_gate_v1"
)
VERSION = OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_VERSION

CLASSIFICATION_OWNER_REVIEW_READY = (
    "OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_OWNER_REVIEW_READY"
)
CLASSIFICATION_REQUIRE_MORE_EVIDENCE = (
    "OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_REQUIRE_MORE_EVIDENCE"
)
CLASSIFICATION_BLOCKED_EXPECTANCY = "OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_BLOCKED_EXPECTANCY"
CLASSIFICATION_BLOCKED_UNSAFE = "OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_BLOCKED_UNSAFE"
CLASSIFICATION_LIVE_APPROVAL_STILL_FALSE = (
    "OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_LIVE_APPROVAL_STILL_FALSE"
)


@dataclass(frozen=True)
class OandaDemoLiveEvidenceBundleGapGateConfig:
    next_safe_action: str = (
        "Finish the missing live evidence items before asking Anthony to review the gap bundle."
    )


@dataclass(frozen=True)
class OandaDemoLiveEvidenceBundleGapGateInput:
    gap_mapper_result: OandaDemoExpectancyToLiveGapMapperResult | Mapping[str, Any]
    config: OandaDemoLiveEvidenceBundleGapGateConfig = field(
        default_factory=OandaDemoLiveEvidenceBundleGapGateConfig
    )


@dataclass(frozen=True)
class OandaDemoLiveEvidenceBundleGapGateResult:
    version: str
    classification: str
    secondary_classifications: tuple[str, ...]
    owner_gap_review_allowed: bool
    requires_more_evidence: bool
    blocked: bool
    live_approval_still_false: bool
    gap_summary: str
    missing_items: tuple[str, ...]
    owner_action_required_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    evidence_bundle_preview: Mapping[str, Any]
    next_safe_action: str
    owner_warning: str
    live_gap_warning: str
    protected_permission_flags: Mapping[str, bool]


def _mapper_value(
    mapper_result: OandaDemoExpectancyToLiveGapMapperResult | Mapping[str, Any],
    key: str,
    default: Any = None,
) -> Any:
    if isinstance(mapper_result, Mapping):
        return mapper_result.get(key, default)
    return getattr(mapper_result, key, default)


def _mapper_json(
    mapper_result: OandaDemoExpectancyToLiveGapMapperResult | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(mapper_result, Mapping):
        return dict(mapper_result)
    return oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(mapper_result)


def build_sample_missing_live_evidence_gap_gate_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    mapper_result = map_oanda_demo_expectancy_to_live_evidence_gaps(
        build_sample_missing_live_evidence_gap_mapper_input()
    )
    return OandaDemoLiveEvidenceBundleGapGateInput(gap_mapper_result=mapper_result)


def build_sample_partial_live_evidence_gap_gate_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    mapper_result = map_oanda_demo_expectancy_to_live_evidence_gaps(
        build_sample_partial_live_evidence_gap_mapper_input()
    )
    return OandaDemoLiveEvidenceBundleGapGateInput(gap_mapper_result=mapper_result)


def build_sample_ready_live_evidence_gap_gate_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    mapper_result = map_oanda_demo_expectancy_to_live_evidence_gaps(
        build_sample_ready_gap_mapper_input()
    )
    return OandaDemoLiveEvidenceBundleGapGateInput(gap_mapper_result=mapper_result)


def build_sample_blocked_live_evidence_gap_gate_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    mapper_result = map_oanda_demo_expectancy_to_live_evidence_gaps(
        build_sample_blocked_expectancy_gap_mapper_input()
    )
    return OandaDemoLiveEvidenceBundleGapGateInput(gap_mapper_result=mapper_result)


def build_sample_unsafe_live_evidence_gap_gate_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    mapper_result = map_oanda_demo_expectancy_to_live_evidence_gaps(
        build_sample_unsafe_gap_mapper_input()
    )
    return OandaDemoLiveEvidenceBundleGapGateInput(gap_mapper_result=mapper_result)


def build_sample_strong_expectancy_missing_live_evidence_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    return build_sample_missing_live_evidence_gap_gate_input()


def build_sample_strong_expectancy_partial_live_evidence_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    return build_sample_partial_live_evidence_gap_gate_input()


def build_sample_weak_expectancy_blocked_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    return build_sample_blocked_live_evidence_gap_gate_input()


def build_sample_rejected_expectancy_blocked_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    return build_sample_blocked_live_evidence_gap_gate_input()


def build_sample_unsafe_expectancy_blocked_input() -> OandaDemoLiveEvidenceBundleGapGateInput:
    return build_sample_unsafe_live_evidence_gap_gate_input()


def evaluate_oanda_demo_live_evidence_bundle_gap_gate(
    gate_input: OandaDemoLiveEvidenceBundleGapGateInput,
) -> OandaDemoLiveEvidenceBundleGapGateResult:
    mapper_classification = str(_mapper_value(gate_input.gap_mapper_result, "classification", ""))
    missing_items = tuple(_mapper_value(gate_input.gap_mapper_result, "missing_items", ()))
    owner_action_required_items = tuple(
        _mapper_value(gate_input.gap_mapper_result, "owner_action_required_items", ())
    )
    blocked_items = tuple(_mapper_value(gate_input.gap_mapper_result, "blocked_items", ()))
    gap_summary = str(_mapper_value(gate_input.gap_mapper_result, "exact_gap_summary", ""))
    if mapper_classification == MAPPER_READY:
        classification = CLASSIFICATION_OWNER_REVIEW_READY
        owner_gap_review_allowed = True
        requires_more_evidence = False
        blocked = False
        next_safe_action = (
            "Anthony may review the completed evidence gap bundle; live approval still remains false."
        )
    elif mapper_classification in (MAPPER_MISSING, MAPPER_PARTIAL):
        classification = CLASSIFICATION_REQUIRE_MORE_EVIDENCE
        owner_gap_review_allowed = False
        requires_more_evidence = True
        blocked = False
        next_safe_action = gate_input.config.next_safe_action
    elif mapper_classification == MAPPER_BLOCKED_UNSAFE:
        classification = CLASSIFICATION_BLOCKED_UNSAFE
        owner_gap_review_allowed = False
        requires_more_evidence = False
        blocked = True
        next_safe_action = "Stop and remove unsafe conditions before live evidence review."
    elif mapper_classification == MAPPER_BLOCKED_EXPECTANCY:
        classification = CLASSIFICATION_BLOCKED_EXPECTANCY
        owner_gap_review_allowed = False
        requires_more_evidence = False
        blocked = True
        next_safe_action = "Return to repeated demo expectancy proof collection."
    else:
        classification = CLASSIFICATION_BLOCKED_UNSAFE
        owner_gap_review_allowed = False
        requires_more_evidence = False
        blocked = True
        next_safe_action = "Stop because the mapper result is not recognized."
    preview = {
        "preview_only": True,
        "gap_mapper_result": _mapper_json(gate_input.gap_mapper_result),
        "owner_gap_review_allowed": owner_gap_review_allowed,
        "live_approval_still_false": True,
        "live_execution_allowed": False,
        "live_micro_trade_exception_allowed": False,
        "live_evidence_bundle_approved": False,
    }
    return OandaDemoLiveEvidenceBundleGapGateResult(
        version=VERSION,
        classification=classification,
        secondary_classifications=(CLASSIFICATION_LIVE_APPROVAL_STILL_FALSE,),
        owner_gap_review_allowed=owner_gap_review_allowed,
        requires_more_evidence=requires_more_evidence,
        blocked=blocked,
        live_approval_still_false=True,
        gap_summary=gap_summary,
        missing_items=missing_items,
        owner_action_required_items=owner_action_required_items,
        blocked_items=blocked_items,
        evidence_bundle_preview=preview,
        next_safe_action=next_safe_action,
        owner_warning=OWNER_WARNING,
        live_gap_warning=LIVE_GAP_WARNING,
        protected_permission_flags=dict(PERMISSION_DEFAULTS),
    )


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def oanda_demo_live_evidence_bundle_gap_gate_to_jsonable_dict(
    result: OandaDemoLiveEvidenceBundleGapGateResult,
) -> dict[str, Any]:
    return _jsonable(result)


def oanda_demo_live_evidence_bundle_gap_gate_to_operator_text(
    result: OandaDemoLiveEvidenceBundleGapGateResult,
) -> str:
    return "\n".join(
        (
            f"Live evidence bundle gap gate status: {result.classification}.",
            f"Gap summary: {result.gap_summary}",
            f"Owner gap review allowed: {result.owner_gap_review_allowed}.",
            "Live approval remains false.",
            result.owner_warning,
            result.live_gap_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "Live profitable execution remains blocked.",
            f"Next safe action: {result.next_safe_action}",
        )
    )


def oanda_demo_live_evidence_bundle_gap_gate_to_markdown(
    result: OandaDemoLiveEvidenceBundleGapGateResult,
) -> str:
    rows = [
        "# OANDA Demo Live Evidence Bundle Gap Gate V1",
        "",
        f"- Classification: {result.classification}",
        f"- Secondary classification: {', '.join(result.secondary_classifications)}",
        f"- Owner gap review allowed: {str(result.owner_gap_review_allowed).lower()}",
        f"- Requires more evidence: {str(result.requires_more_evidence).lower()}",
        f"- Blocked: {str(result.blocked).lower()}",
        "- Live approval remains false.",
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- Live profitable execution remains blocked.",
        f"- Gap summary: {result.gap_summary}",
        "",
        "## Permissions",
    ]
    for key in sorted(result.protected_permission_flags):
        rows.append(f"- `{key}`: {str(result.protected_permission_flags[key]).lower()}")
    rows.extend(("", f"Next safe action: {result.next_safe_action}"))
    return "\n".join(rows) + "\n"
