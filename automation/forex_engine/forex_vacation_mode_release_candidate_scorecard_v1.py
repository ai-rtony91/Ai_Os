"""Release-candidate scorecard for AIOS Forex Vacation Mode."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    base_hard_false_fields,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_RELEASE_CANDIDATE_SCORECARD_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_RELEASE_CANDIDATE_SCORECARD"

SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW = "SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW"
SCORECARD_BLOCKED_BY_PRODUCT_POLICY = "SCORECARD_BLOCKED_BY_PRODUCT_POLICY"
SCORECARD_BLOCKED_BY_CONTROL_PLANE = "SCORECARD_BLOCKED_BY_CONTROL_PLANE"
SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE = "SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE"
SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE = "SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE"
SCORECARD_BLOCKED_BY_MOBILE_PACKAGING = "SCORECARD_BLOCKED_BY_MOBILE_PACKAGING"
SCORECARD_BLOCKED_BY_FINAL_RELEASE_CANDIDATE_READINESS = (
    "SCORECARD_BLOCKED_BY_FINAL_RELEASE_CANDIDATE_READINESS"
)
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

SCORE_AREAS = (
    "product_policy_readiness",
    "financial_risk_disclosure_readiness",
    "privacy_data_safety_readiness",
    "permissions_model_readiness",
    "store_claims_policy_readiness",
    "owner_consent_readiness",
    "entry_gate_readiness",
    "position_supervisor_readiness",
    "exit_gate_readiness",
    "alerting_readiness",
    "evidence_bundle_readiness",
    "broker_receipt_readiness",
    "realized_pnl_reconciliation_readiness",
    "legal_compliance_review_readiness",
    "mobile_control_plane_readiness",
    "release_packaging_readiness",
    "final_release_candidate_readiness",
)

PRODUCT_POLICY_AREAS = (
    "product_policy_readiness",
    "financial_risk_disclosure_readiness",
    "privacy_data_safety_readiness",
    "permissions_model_readiness",
    "store_claims_policy_readiness",
    "owner_consent_readiness",
)
CONTROL_PLANE_AREAS = (
    "entry_gate_readiness",
    "position_supervisor_readiness",
    "exit_gate_readiness",
    "alerting_readiness",
    "mobile_control_plane_readiness",
)
EXTERNAL_EVIDENCE_AREAS = (
    "evidence_bundle_readiness",
    "broker_receipt_readiness",
    "realized_pnl_reconciliation_readiness",
)
MOBILE_AREAS = ("release_packaging_readiness",)


def evaluate_forex_vacation_mode_release_candidate_scorecard_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score metadata readiness without claiming final release readiness."""

    source = _mapping(payload)
    if not source:
        return _scorecard_result(INCOMPLETE_INPUTS, ("payload_missing",), {})
    missing = tuple(f"{area}_missing" for area in SCORE_AREAS if not _mapping(source.get(area)))
    if missing:
        return _scorecard_result(INCOMPLETE_INPUTS, missing, source)

    area_statuses = {area: _area_status(_mapping(source.get(area))) for area in SCORE_AREAS}
    area_ready = {area: area_statuses[area] == "READY" for area in SCORE_AREAS}

    final_release_ready = all(area_ready.values())
    area_ready["final_release_candidate_readiness"] = final_release_ready
    area_statuses["final_release_candidate_readiness"] = (
        "READY" if final_release_ready else "BLOCKED"
    )

    if _blocked(area_ready, PRODUCT_POLICY_AREAS):
        status = SCORECARD_BLOCKED_BY_PRODUCT_POLICY
        blockers = _blocked_area_names(area_ready, PRODUCT_POLICY_AREAS)
    elif _blocked(area_ready, CONTROL_PLANE_AREAS):
        status = SCORECARD_BLOCKED_BY_CONTROL_PLANE
        blockers = _blocked_area_names(area_ready, CONTROL_PLANE_AREAS)
    elif _blocked(area_ready, EXTERNAL_EVIDENCE_AREAS):
        status = SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE
        blockers = _blocked_area_names(area_ready, EXTERNAL_EVIDENCE_AREAS)
    elif not area_ready["legal_compliance_review_readiness"]:
        status = SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE
        blockers = ("legal_compliance_review_readiness",)
    elif _blocked(area_ready, MOBILE_AREAS):
        status = SCORECARD_BLOCKED_BY_MOBILE_PACKAGING
        blockers = _blocked_area_names(area_ready, MOBILE_AREAS)
    elif area_ready.get("final_release_candidate_readiness") is not True:
        status = SCORECARD_BLOCKED_BY_FINAL_RELEASE_CANDIDATE_READINESS
        blockers = ("final_release_candidate_readiness",)
    else:
        status = SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW
        blockers = ()

    return _scorecard_result(status, blockers, source, area_statuses, area_ready)


def _scorecard_result(
    status: str,
    blockers: Sequence[str],
    source: Mapping[str, Any],
    area_statuses: Mapping[str, str] | None = None,
    area_ready: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    statuses = dict(area_statuses or {})
    ready_map = dict(area_ready or {})
    ready_count = sum(1 for area in SCORE_AREAS if ready_map.get(area) is True)
    total = len(SCORE_AREAS)
    percent = round((ready_count / total) * 100, 2) if total else 0.0
    unique_blockers = _unique(blockers)
    ready = (
        status == SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW
        and ready_map.get("final_release_candidate_readiness") is True
        and not unique_blockers
    )
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "metadata_only": True,
        "read_only": True,
        "score_areas": {
            area: {
                "status": statuses.get(area, "MISSING"),
                "ready": ready_map.get(area) is True,
            }
            for area in SCORE_AREAS
        },
        "ready_area_count": ready_count,
        "total_area_count": total,
        "final_release_candidate_readiness_percent": percent,
        "final_release_candidate_ready": ready_map.get("final_release_candidate_readiness") is True,
        "legal_compliance_review_ready": ready_map.get("legal_compliance_review_readiness") is True,
        "broker_live_evidence_ready": all(
            ready_map.get(area) is True for area in EXTERNAL_EVIDENCE_AREAS
        ),
        "sell_ready_claimed": False,
        "blockers": unique_blockers,
        "owner_next_action": _next_action(status),
        "source_sections_seen": sorted(str(key) for key in source.keys()),
        **base_hard_false_fields(),
    }


def _area_status(area: Mapping[str, Any]) -> str:
    if area.get("ready") is True:
        return "READY"
    return str(area.get("status", "BLOCKED"))


def _blocked(area_ready: Mapping[str, bool], areas: Sequence[str]) -> bool:
    return any(area_ready.get(area) is not True for area in areas)


def _blocked_area_names(area_ready: Mapping[str, bool], areas: Sequence[str]) -> tuple[str, ...]:
    return tuple(area for area in areas if area_ready.get(area) is not True)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _next_action(status: str) -> str:
    return {
        SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW: (
            "Review metadata control-plane readiness; final release still needs owner review."
        ),
        SCORECARD_BLOCKED_BY_PRODUCT_POLICY: "Complete product policy readiness areas.",
        SCORECARD_BLOCKED_BY_CONTROL_PLANE: "Complete control-plane readiness areas.",
        SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE: "Complete sanitized external evidence readiness.",
        SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE: "Complete owner legal/compliance review.",
        SCORECARD_BLOCKED_BY_MOBILE_PACKAGING: "Complete mobile packaging review.",
        SCORECARD_BLOCKED_BY_FINAL_RELEASE_CANDIDATE_READINESS: (
            "Complete final release-candidate readiness review."
        ),
    }.get(status, "Provide all scorecard areas.")


__all__ = [
    "SCORE_AREAS",
    "SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW",
    "SCORECARD_BLOCKED_BY_PRODUCT_POLICY",
    "SCORECARD_BLOCKED_BY_CONTROL_PLANE",
    "SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE",
    "SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE",
    "SCORECARD_BLOCKED_BY_MOBILE_PACKAGING",
    "SCORECARD_BLOCKED_BY_FINAL_RELEASE_CANDIDATE_READINESS",
    "INCOMPLETE_INPUTS",
    "evaluate_forex_vacation_mode_release_candidate_scorecard_v1",
]
