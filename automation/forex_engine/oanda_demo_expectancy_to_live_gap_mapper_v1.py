"""Map repeated demo expectancy proof into live evidence bundle gaps."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_live_evidence_requirement_matrix_v1 import (
    ALLOWED_EVIDENCE_STATUSES,
    LIVE_GAP_WARNING,
    OWNER_WARNING,
    PERMISSION_DEFAULTS,
    OandaDemoLiveEvidenceRequirementMatrixResult,
    build_default_oanda_demo_live_evidence_requirements,
    build_oanda_demo_live_evidence_requirement_matrix,
    oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict,
)


OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAPPER_VERSION = (
    "oanda_demo_expectancy_to_live_gap_mapper_v1"
)
VERSION = OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAPPER_VERSION

CLASSIFICATION_MISSING = "OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAP_MISSING_LIVE_EVIDENCE"
CLASSIFICATION_PARTIAL = "OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAP_PARTIAL_LIVE_EVIDENCE"
CLASSIFICATION_READY = "OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAP_READY_FOR_OWNER_GAP_REVIEW"
CLASSIFICATION_BLOCKED_EXPECTANCY = "OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAP_BLOCKED_EXPECTANCY"
CLASSIFICATION_BLOCKED_UNSAFE = "OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAP_BLOCKED_UNSAFE"


@dataclass(frozen=True)
class OandaDemoExpectancyToLiveGapMapperConfig:
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)
    next_safe_action: str = (
        "Review each missing live evidence item; do not treat this preview as live approval."
    )


@dataclass(frozen=True)
class OandaDemoExpectancyToLiveGapMapperInput:
    expectancy_epic_result: Mapping[str, Any]
    requirement_matrix_result: OandaDemoLiveEvidenceRequirementMatrixResult | Mapping[str, Any]
    evidence_statuses: Mapping[str, str]
    config: OandaDemoExpectancyToLiveGapMapperConfig = field(
        default_factory=OandaDemoExpectancyToLiveGapMapperConfig
    )


@dataclass(frozen=True)
class OandaDemoExpectancyToLiveGapMapperResult:
    version: str
    classification: str
    expectancy_status: str
    expectancy_ready_for_owner_review: bool
    requirement_count: int
    present_count: int
    missing_count: int
    blocked_count: int
    owner_action_required_count: int
    evidence_statuses: Mapping[str, str]
    missing_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    owner_action_required_items: tuple[str, ...]
    live_evidence_bundle_preview: Mapping[str, Any]
    exact_gap_summary: str
    owner_warning: str
    live_gap_warning: str
    next_safe_action: str
    protected_permission_flags: Mapping[str, bool]
    present_ratio: Decimal


def _expectancy_ready(expectancy_epic_result: Mapping[str, Any]) -> bool:
    if bool(expectancy_epic_result.get("ready_for_owner_review")):
        return True
    for key in ("classification", "status", "expectancy_status"):
        value = str(expectancy_epic_result.get(key, ""))
        if "READY_FOR_OWNER_REVIEW" in value:
            return True
    return False


def _expectancy_unsafe(expectancy_epic_result: Mapping[str, Any]) -> bool:
    unsafe_keys = (
        "unsafe",
        "unsafe_flag",
        "blocked_unsafe",
        "credential_access_attempted",
        "broker_call_attempted",
        "live_trading_attempted",
    )
    if any(bool(expectancy_epic_result.get(key)) for key in unsafe_keys):
        return True
    for key in ("classification", "status", "safety_status"):
        value = str(expectancy_epic_result.get(key, ""))
        if "UNSAFE" in value:
            return True
    return False


def _expectancy_status(expectancy_epic_result: Mapping[str, Any]) -> str:
    for key in ("expectancy_status", "classification", "status"):
        value = str(expectancy_epic_result.get(key, "")).strip()
        if value:
            return value
    return "UNKNOWN_EXPECTANCY_STATUS"


def _requirement_ids(
    requirement_matrix_result: OandaDemoLiveEvidenceRequirementMatrixResult | Mapping[str, Any],
) -> tuple[str, ...]:
    if isinstance(requirement_matrix_result, OandaDemoLiveEvidenceRequirementMatrixResult):
        return tuple(requirement_matrix_result.required_item_ids)
    item_ids = requirement_matrix_result.get("required_item_ids")
    if item_ids:
        return tuple(str(item_id) for item_id in item_ids)
    requirements = requirement_matrix_result.get("requirements", ())
    resolved: list[str] = []
    for requirement in requirements:
        if isinstance(requirement, Mapping):
            resolved.append(str(requirement.get("item_id", "")))
        else:
            resolved.append(str(getattr(requirement, "item_id", "")))
    return tuple(item_id for item_id in resolved if item_id)


def _matrix_json(
    requirement_matrix_result: OandaDemoLiveEvidenceRequirementMatrixResult | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(requirement_matrix_result, OandaDemoLiveEvidenceRequirementMatrixResult):
        return oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict(requirement_matrix_result)
    return dict(requirement_matrix_result)


def _normalize_status(status: str) -> str:
    normalized = str(status or "MISSING").strip().upper()
    if normalized in ALLOWED_EVIDENCE_STATUSES:
        return normalized
    return "BLOCKED"


def _build_expectancy_result(
    status: str,
    ready: bool,
    unsafe: bool = False,
) -> Mapping[str, Any]:
    return {
        "classification": status,
        "expectancy_status": status,
        "ready_for_owner_review": ready,
        "unsafe": unsafe,
        "source": "deterministic_sample",
    }


def _default_matrix_result() -> OandaDemoLiveEvidenceRequirementMatrixResult:
    return build_oanda_demo_live_evidence_requirement_matrix()


def _statuses_all(status: str) -> dict[str, str]:
    return {
        requirement.item_id: status
        for requirement in build_default_oanda_demo_live_evidence_requirements()
    }


def _statuses_partial() -> dict[str, str]:
    item_ids = [requirement.item_id for requirement in build_default_oanda_demo_live_evidence_requirements()]
    statuses = {item_id: "MISSING" for item_id in item_ids}
    for item_id in item_ids[:8]:
        statuses[item_id] = "PRESENT"
    for item_id in item_ids[8:12]:
        statuses[item_id] = "OWNER_ACTION_REQUIRED"
    for item_id in item_ids[12:14]:
        statuses[item_id] = "BLOCKED"
    return statuses


def build_sample_missing_live_evidence_gap_mapper_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return OandaDemoExpectancyToLiveGapMapperInput(
        expectancy_epic_result=_build_expectancy_result(
            "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW",
            True,
        ),
        requirement_matrix_result=_default_matrix_result(),
        evidence_statuses=_statuses_all("MISSING"),
    )


def build_sample_partial_live_evidence_gap_mapper_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return OandaDemoExpectancyToLiveGapMapperInput(
        expectancy_epic_result=_build_expectancy_result(
            "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW",
            True,
        ),
        requirement_matrix_result=_default_matrix_result(),
        evidence_statuses=_statuses_partial(),
    )


def build_sample_ready_gap_mapper_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return OandaDemoExpectancyToLiveGapMapperInput(
        expectancy_epic_result=_build_expectancy_result(
            "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW",
            True,
        ),
        requirement_matrix_result=_default_matrix_result(),
        evidence_statuses=_statuses_all("PRESENT"),
    )


def build_sample_blocked_expectancy_gap_mapper_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return OandaDemoExpectancyToLiveGapMapperInput(
        expectancy_epic_result=_build_expectancy_result(
            "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REQUIRE_MORE_EVIDENCE",
            False,
        ),
        requirement_matrix_result=_default_matrix_result(),
        evidence_statuses=_statuses_all("PRESENT"),
    )


def build_sample_unsafe_gap_mapper_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return OandaDemoExpectancyToLiveGapMapperInput(
        expectancy_epic_result=_build_expectancy_result(
            "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_BLOCKED_UNSAFE",
            False,
            unsafe=True,
        ),
        requirement_matrix_result=_default_matrix_result(),
        evidence_statuses=_statuses_all("PRESENT"),
        config=OandaDemoExpectancyToLiveGapMapperConfig(unsafe_flags={"unsafe_sample": True}),
    )


def build_sample_strong_expectancy_missing_live_evidence_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return build_sample_missing_live_evidence_gap_mapper_input()


def build_sample_strong_expectancy_partial_live_evidence_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return build_sample_partial_live_evidence_gap_mapper_input()


def build_sample_weak_expectancy_blocked_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return build_sample_blocked_expectancy_gap_mapper_input()


def build_sample_rejected_expectancy_blocked_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return build_sample_blocked_expectancy_gap_mapper_input()


def build_sample_unsafe_expectancy_blocked_input() -> OandaDemoExpectancyToLiveGapMapperInput:
    return build_sample_unsafe_gap_mapper_input()


def map_oanda_demo_expectancy_to_live_evidence_gaps(
    mapper_input: OandaDemoExpectancyToLiveGapMapperInput,
) -> OandaDemoExpectancyToLiveGapMapperResult:
    item_ids = _requirement_ids(mapper_input.requirement_matrix_result)
    normalized_statuses = {
        item_id: _normalize_status(mapper_input.evidence_statuses.get(item_id, "MISSING"))
        for item_id in item_ids
    }
    present_items = tuple(
        item_id for item_id, status in normalized_statuses.items() if status == "PRESENT"
    )
    missing_items = tuple(
        item_id for item_id, status in normalized_statuses.items() if status == "MISSING"
    )
    blocked_items = tuple(
        item_id for item_id, status in normalized_statuses.items() if status == "BLOCKED"
    )
    owner_action_required_items = tuple(
        item_id
        for item_id, status in normalized_statuses.items()
        if status == "OWNER_ACTION_REQUIRED"
    )
    expectancy_status = _expectancy_status(mapper_input.expectancy_epic_result)
    expectancy_ready = _expectancy_ready(mapper_input.expectancy_epic_result)
    unsafe = _expectancy_unsafe(mapper_input.expectancy_epic_result) or any(
        bool(value) for value in mapper_input.config.unsafe_flags.values()
    )
    requirement_count = len(item_ids)
    if unsafe:
        classification = CLASSIFICATION_BLOCKED_UNSAFE
        next_safe_action = "Stop and remove unsafe conditions before any owner gap review."
    elif not expectancy_ready:
        classification = CLASSIFICATION_BLOCKED_EXPECTANCY
        next_safe_action = "Collect stronger repeated demo expectancy evidence before live gap review."
    elif requirement_count and len(present_items) == requirement_count:
        classification = CLASSIFICATION_READY
        next_safe_action = (
            "Anthony may review the completed gap map, but this still is not live trading approval."
        )
    elif not present_items:
        classification = CLASSIFICATION_MISSING
        next_safe_action = "Complete or reject each missing live evidence item before review."
    else:
        classification = CLASSIFICATION_PARTIAL
        next_safe_action = mapper_input.config.next_safe_action
    preview_items = [
        {
            "item_id": item_id,
            "status": normalized_statuses[item_id],
            "preview_only": True,
            "live_approval": False,
        }
        for item_id in item_ids
    ]
    exact_gap_summary = (
        f"{len(missing_items)} missing, {len(owner_action_required_items)} owner-action-required, "
        f"{len(blocked_items)} blocked, {len(present_items)} present."
    )
    live_evidence_bundle_preview = {
        "preview_only": True,
        "matrix": _matrix_json(mapper_input.requirement_matrix_result),
        "evidence_items": preview_items,
        "ready_gap_review_is_not_live_approval": True,
        "live_execution_allowed": False,
        "live_micro_trade_exception_allowed": False,
        "live_evidence_bundle_approved": False,
    }
    present_ratio = (
        Decimal(len(present_items)) / Decimal(requirement_count)
        if requirement_count
        else Decimal("0")
    )
    return OandaDemoExpectancyToLiveGapMapperResult(
        version=VERSION,
        classification=classification,
        expectancy_status=expectancy_status,
        expectancy_ready_for_owner_review=expectancy_ready,
        requirement_count=requirement_count,
        present_count=len(present_items),
        missing_count=len(missing_items),
        blocked_count=len(blocked_items),
        owner_action_required_count=len(owner_action_required_items),
        evidence_statuses=normalized_statuses,
        missing_items=missing_items,
        blocked_items=blocked_items,
        owner_action_required_items=owner_action_required_items,
        live_evidence_bundle_preview=live_evidence_bundle_preview,
        exact_gap_summary=exact_gap_summary,
        owner_warning=OWNER_WARNING,
        live_gap_warning=LIVE_GAP_WARNING,
        next_safe_action=next_safe_action,
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


def oanda_demo_expectancy_to_live_gap_mapper_to_jsonable_dict(
    result: OandaDemoExpectancyToLiveGapMapperResult,
) -> dict[str, Any]:
    return _jsonable(result)


def oanda_demo_expectancy_to_live_gap_mapper_to_operator_text(
    result: OandaDemoExpectancyToLiveGapMapperResult,
) -> str:
    return "\n".join(
        (
            f"Expectancy-to-live gap map status: {result.classification}.",
            f"Expectancy status: {result.expectancy_status}.",
            f"Gap summary: {result.exact_gap_summary}",
            "Ready gap review is not live approval.",
            result.owner_warning,
            result.live_gap_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "Live profitable execution remains blocked.",
            f"Next safe action: {result.next_safe_action}",
        )
    )


def oanda_demo_expectancy_to_live_gap_mapper_to_markdown(
    result: OandaDemoExpectancyToLiveGapMapperResult,
) -> str:
    rows = [
        "# OANDA Demo Expectancy To Live Gap Mapper V1",
        "",
        f"- Classification: {result.classification}",
        f"- Expectancy status: {result.expectancy_status}",
        f"- Requirement count: {result.requirement_count}",
        f"- Present: {result.present_count}",
        f"- Missing: {result.missing_count}",
        f"- Blocked: {result.blocked_count}",
        f"- Owner action required: {result.owner_action_required_count}",
        "- Ready gap review is not live approval.",
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- Live profitable execution remains blocked.",
        "",
        "## Missing Items",
    ]
    rows.extend(f"- `{item_id}`" for item_id in result.missing_items)
    rows.append("")
    rows.append("## Owner Action Required Items")
    rows.extend(f"- `{item_id}`" for item_id in result.owner_action_required_items)
    rows.append("")
    rows.append("## Blocked Items")
    rows.extend(f"- `{item_id}`" for item_id in result.blocked_items)
    rows.append("")
    rows.append("## Permissions")
    for key in sorted(result.protected_permission_flags):
        rows.append(f"- `{key}`: {str(result.protected_permission_flags[key]).lower()}")
    rows.extend(("", f"Next safe action: {result.next_safe_action}"))
    return "\n".join(rows) + "\n"
