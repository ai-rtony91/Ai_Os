"""Roll up governed multi-pair burst readiness for Vacation Mode."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_basket_risk_exposure_governor_v1 import (
    BASKET_RISK_EXPOSURE_READY,
    evaluate_forex_basket_risk_exposure_governor_v1,
)
from automation.forex_engine.forex_burst_receipt_and_post_burst_review_v1 import (
    BURST_RECEIPT_AND_POST_BURST_REVIEW_READY,
    WAITING_FOR_BURST_RECEIPTS,
    evaluate_forex_burst_receipt_and_post_burst_review_v1,
)
from automation.forex_engine.forex_governed_burst_permission_engine_v1 import (
    READY_FOR_DEMO_BURST_RUNTIME_INTENT,
    READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW,
    READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT,
    BLOCKED_BY_PROOF_REQUIREMENT,
    evaluate_forex_governed_burst_permission_engine_v1,
)
from automation.forex_engine.forex_multi_pair_opportunity_batch_v1 import (
    MULTI_PAIR_OPPORTUNITY_BATCH_READY,
    evaluate_forex_multi_pair_opportunity_batch_v1,
)
from automation.forex_engine.forex_multi_pair_universe_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    MULTI_PAIR_UNIVERSE_READY,
    _governed_requested,
    _mapping,
    _unique,
    banking_focus_blockers,
    build_common_result,
    sensitive_data_blockers,
    evaluate_forex_multi_pair_universe_v1,
)

SCHEMA = "AIOS_FOREX_VACATION_MODE_MULTI_PAIR_BURST_ROLLUP_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_MULTI_PAIR_BURST_ROLLUP"

VACATION_MODE_MULTI_PAIR_BURST_READY_FOR_OWNER_REVIEW = (
    "VACATION_MODE_MULTI_PAIR_BURST_READY_FOR_OWNER_REVIEW"
)
READY_FOR_DEMO_MULTI_PAIR_BURST_INTENT = "READY_FOR_DEMO_MULTI_PAIR_BURST_INTENT"
READY_FOR_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW = (
    "READY_FOR_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW"
)
READY_FOR_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_INTENT = (
    "READY_FOR_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_INTENT"
)
WAITING_FOR_MULTI_PAIR_BURST_RECEIPTS = "WAITING_FOR_MULTI_PAIR_BURST_RECEIPTS"
CONTINUE_MULTI_PAIR_PROOF_CAPTURE = "CONTINUE_MULTI_PAIR_PROOF_CAPTURE"
BLOCKED_BY_PAIR_UNIVERSE = "BLOCKED_BY_PAIR_UNIVERSE"
BLOCKED_BY_OPPORTUNITY_BATCH = "BLOCKED_BY_OPPORTUNITY_BATCH"
BLOCKED_BY_BASKET_RISK = "BLOCKED_BY_BASKET_RISK"
BLOCKED_BY_BURST_PERMISSION = "BLOCKED_BY_BURST_PERMISSION"
BLOCKED_BY_BURST_RECEIPT_REVIEW = "BLOCKED_BY_BURST_RECEIPT_REVIEW"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_GOVERNED_MULTI_PAIR_BURST_VACATION_MODE_V1"


def evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the metadata-only governed burst readiness chain."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _rollup_result(
            source,
            BLOCKED_BY_SENSITIVE_DATA,
            False,
            sensitive_blockers,
            next_best_packet=NEXT_BEST_PACKET,
        )
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _rollup_result(
            source,
            BLOCKED_BY_BANKING_FOCUS,
            False,
            banking_blockers,
            next_best_packet=NEXT_BEST_PACKET,
        )
    if not source:
        return _rollup_result(source, INCOMPLETE_INPUTS, False, ("payload_missing",))

    pair_result = evaluate_forex_multi_pair_universe_v1(
        {
            "governed_burst_requested": _governed_requested(source),
            "pair_universe": _mapping(source.get("pair_universe")),
        }
    )
    if pair_result["status"] != MULTI_PAIR_UNIVERSE_READY:
        return _rollup_result(
            source,
            BLOCKED_BY_PAIR_UNIVERSE,
            False,
            pair_result.get("blockers", []),
            pair_universe_summary=pair_result,
        )

    opportunity_result = evaluate_forex_multi_pair_opportunity_batch_v1(
        {
            "governed_burst_requested": _governed_requested(source),
            "pair_universe_result": pair_result,
            "opportunity_batch": _mapping(source.get("opportunity_batch")),
        }
    )
    if opportunity_result["status"] != MULTI_PAIR_OPPORTUNITY_BATCH_READY:
        return _rollup_result(
            source,
            BLOCKED_BY_OPPORTUNITY_BATCH,
            False,
            opportunity_result.get("blockers", []),
            pair_universe_summary=pair_result,
            opportunity_batch_summary=opportunity_result,
        )

    basket_result = evaluate_forex_basket_risk_exposure_governor_v1(
        {
            "governed_burst_requested": _governed_requested(source),
            "opportunity_batch_result": opportunity_result,
            "risk_policy": _mapping(source.get("risk_policy")),
        }
    )
    if basket_result["status"] != BASKET_RISK_EXPOSURE_READY:
        return _rollup_result(
            source,
            BLOCKED_BY_BASKET_RISK,
            False,
            basket_result.get("blockers", []),
            pair_universe_summary=pair_result,
            opportunity_batch_summary=opportunity_result,
            basket_risk_summary=basket_result,
        )

    permission_result = evaluate_forex_governed_burst_permission_engine_v1(
        {
            "governed_burst_requested": _governed_requested(source),
            "basket_risk_result": basket_result,
            "permission": _mapping(source.get("permission")),
            "proof": _mapping(source.get("proof")),
            "runtime_boundary": _mapping(source.get("runtime_boundary")),
        }
    )
    permission_status = permission_result["status"]
    if permission_status == READY_FOR_DEMO_BURST_RUNTIME_INTENT:
        return _rollup_result(
            source,
            READY_FOR_DEMO_MULTI_PAIR_BURST_INTENT,
            True,
            (),
            pair_universe_summary=pair_result,
            opportunity_batch_summary=opportunity_result,
            basket_risk_summary=basket_result,
            burst_permission_summary=permission_result,
            next_best_packet="AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1",
        )
    if permission_status == READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW:
        return _rollup_result(
            source,
            READY_FOR_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW,
            True,
            (),
            pair_universe_summary=pair_result,
            opportunity_batch_summary=opportunity_result,
            basket_risk_summary=basket_result,
            burst_permission_summary=permission_result,
            next_best_packet="AIOS_FOREX_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW_V1",
        )
    if permission_status == READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT:
        receipt_payload_present = "burst_receipts" in source or "post_burst_review" in source
        if not receipt_payload_present:
            return _rollup_result(
                source,
                READY_FOR_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_INTENT,
                True,
                (),
                pair_universe_summary=pair_result,
                opportunity_batch_summary=opportunity_result,
                basket_risk_summary=basket_result,
                burst_permission_summary=permission_result,
                next_best_packet="AIOS_FOREX_OWNER_APPROVED_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1",
            )
        receipt_result = evaluate_forex_burst_receipt_and_post_burst_review_v1(
            {
                "governed_burst_requested": _governed_requested(source),
                "burst_intent": _mapping(permission_result.get("governed_burst_intent")),
                "burst_receipts": _mapping(source.get("burst_receipts")),
                "post_burst_review": _mapping(source.get("post_burst_review")),
            }
        )
        if receipt_result["status"] == WAITING_FOR_BURST_RECEIPTS:
            return _rollup_result(
                source,
                WAITING_FOR_MULTI_PAIR_BURST_RECEIPTS,
                False,
                receipt_result.get("blockers", []),
                pair_universe_summary=pair_result,
                opportunity_batch_summary=opportunity_result,
                basket_risk_summary=basket_result,
                burst_permission_summary=permission_result,
                burst_receipt_review_summary=receipt_result,
                next_best_packet="AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1",
            )
        if receipt_result["status"] == BURST_RECEIPT_AND_POST_BURST_REVIEW_READY:
            return _rollup_result(
                source,
                VACATION_MODE_MULTI_PAIR_BURST_READY_FOR_OWNER_REVIEW,
                True,
                (),
                pair_universe_summary=pair_result,
                opportunity_batch_summary=opportunity_result,
                basket_risk_summary=basket_result,
                burst_permission_summary=permission_result,
                burst_receipt_review_summary=receipt_result,
                next_best_packet="AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1",
            )
        return _rollup_result(
            source,
            BLOCKED_BY_BURST_RECEIPT_REVIEW,
            False,
            receipt_result.get("blockers", []),
            pair_universe_summary=pair_result,
            opportunity_batch_summary=opportunity_result,
            basket_risk_summary=basket_result,
            burst_permission_summary=permission_result,
            burst_receipt_review_summary=receipt_result,
        )

    if permission_status == BLOCKED_BY_PROOF_REQUIREMENT:
        return _rollup_result(
            source,
            CONTINUE_MULTI_PAIR_PROOF_CAPTURE,
            False,
            permission_result.get("blockers", []),
            pair_universe_summary=pair_result,
            opportunity_batch_summary=opportunity_result,
            basket_risk_summary=basket_result,
            burst_permission_summary=permission_result,
        )
    return _rollup_result(
        source,
        BLOCKED_BY_BURST_PERMISSION,
        False,
        permission_result.get("blockers", []),
        pair_universe_summary=pair_result,
        opportunity_batch_summary=opportunity_result,
        basket_risk_summary=basket_result,
        burst_permission_summary=permission_result,
    )


def _rollup_result(
    source: Mapping[str, Any],
    campaign_status: str,
    campaign_ready: bool,
    blockers: Sequence[str],
    *,
    pair_universe_summary: Mapping[str, Any] | None = None,
    opportunity_batch_summary: Mapping[str, Any] | None = None,
    basket_risk_summary: Mapping[str, Any] | None = None,
    burst_permission_summary: Mapping[str, Any] | None = None,
    burst_receipt_review_summary: Mapping[str, Any] | None = None,
    next_best_packet: str = NEXT_BEST_PACKET,
) -> dict[str, Any]:
    owner_action_queue = [
        {
            "action_id": campaign_status,
            "owner_decision_required": True,
            "blocked_by": list(_unique(blockers)),
            "next_best_packet": next_best_packet,
        }
    ]
    extra = {
        "campaign_status": campaign_status,
        "campaign_ready": bool(campaign_ready),
        "pair_universe_summary": dict(pair_universe_summary or {}),
        "opportunity_batch_summary": dict(opportunity_batch_summary or {}),
        "basket_risk_summary": dict(basket_risk_summary or {}),
        "burst_permission_summary": dict(burst_permission_summary or {}),
        "burst_receipt_review_summary": dict(burst_receipt_review_summary or {}),
        "governed_burst_destination_map": _destination_map(campaign_status),
        "owner_action_queue": owner_action_queue,
    }
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=campaign_status,
        ready=bool(campaign_ready),
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=bool(campaign_ready),
        blockers=blockers,
        next_best_packet=next_best_packet,
        safe_manual_next_action=_safe_manual_next_action(campaign_status),
        extra=extra,
        audit_extra={"campaign_status": campaign_status, "campaign_ready": bool(campaign_ready)},
    )


def _destination_map(status: str) -> dict[str, Any]:
    return {
        "pair universe -> opportunity batch": "READY_OR_BLOCKED_BY_CURRENT_STATUS",
        "opportunity batch -> basket risk governor": "READY_OR_BLOCKED_BY_CURRENT_STATUS",
        "basket risk governor -> burst permission engine": "READY_OR_BLOCKED_BY_CURRENT_STATUS",
        "burst permission engine -> demo burst intent OR live micro owner review OR protected live burst runtime intent": status,
        "protected runtime intent -> burst receipts": "RECEIPT_REQUIRED_AFTER_SEPARATE_RUNTIME",
        "burst receipts -> post-burst review": "POST_BURST_REVIEW_REQUIRED",
        "post-burst review -> repeatability evidence": "ROUTE_SANITIZED_JOURNAL",
        "repeatability evidence -> next governed burst decision": "NO_NEXT_BURST_WITHOUT_REVIEW",
    }


def _safe_manual_next_action(status: str) -> str:
    if status == READY_FOR_DEMO_MULTI_PAIR_BURST_INTENT:
        return "Owner may review the separate demo multi-pair burst runtime packet."
    if status == READY_FOR_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW:
        return "Owner may review live micro multi-pair burst evidence."
    if status == READY_FOR_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_INTENT:
        return "Owner may review protected live micro burst runtime intent; no execution occurs here."
    if status == WAITING_FOR_MULTI_PAIR_BURST_RECEIPTS:
        return "Wait for sanitized receipts from the separate runtime packet."
    if status == CONTINUE_MULTI_PAIR_PROOF_CAPTURE:
        return "Continue proof capture before live burst review."
    if status == VACATION_MODE_MULTI_PAIR_BURST_READY_FOR_OWNER_REVIEW:
        return "Owner may review completed burst evidence before another burst decision."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, or money-movement focus fields."
    return "Repair the blocking governed burst stage and rerun."
