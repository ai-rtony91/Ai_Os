"""Decide whether a basket may become a governed burst intent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_basket_risk_exposure_governor_v1 import (
    BASKET_RISK_EXPOSURE_READY,
)
from automation.forex_engine.forex_multi_pair_universe_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    _bool,
    _governed_requested,
    _mapping,
    _number,
    banking_focus_blockers,
    build_common_result,
    sensitive_data_blockers,
)

SCHEMA = "AIOS_FOREX_GOVERNED_BURST_PERMISSION_ENGINE_V1"
MODE = "READ_ONLY_METADATA_ONLY_GOVERNED_BURST_PERMISSION_ENGINE"

GOVERNED_BURST_PERMISSION_READY = "GOVERNED_BURST_PERMISSION_READY"
READY_FOR_DEMO_BURST_RUNTIME_INTENT = "READY_FOR_DEMO_BURST_RUNTIME_INTENT"
READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW = "READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW"
READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT = (
    "READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT"
)
BLOCKED_BY_BASKET_RISK = "BLOCKED_BY_BASKET_RISK"
BLOCKED_BY_OWNER_GATE = "BLOCKED_BY_OWNER_GATE"
BLOCKED_BY_RUNTIME_BOUNDARY = "BLOCKED_BY_RUNTIME_BOUNDARY"
BLOCKED_BY_PROOF_REQUIREMENT = "BLOCKED_BY_PROOF_REQUIREMENT"
BLOCKED_BY_REVIEW_LOCK = "BLOCKED_BY_REVIEW_LOCK"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_GOVERNED_MULTI_PAIR_BURST_VACATION_MODE_V1"
VALID_MODES = frozenset({"DEMO_BURST", "LIVE_MICRO_REVIEW", "LIVE_MICRO_RUNTIME_INTENT"})

REQUIRED_PERMISSION_FIELDS = (
    "mode",
    "owner_review_required",
    "owner_live_approval_required_for_live",
    "runtime_credentials_required_for_execution",
    "proof_required_for_live",
    "previous_burst_review_complete",
    "receipt_required",
    "post_burst_review_required",
    "may_execute_by_this_module",
    "may_call_broker_by_this_module",
)


def evaluate_forex_governed_burst_permission_engine_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare governed burst intent metadata only."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _permission_result(source, BLOCKED_BY_SENSITIVE_DATA, sensitive_blockers)
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _permission_result(source, BLOCKED_BY_BANKING_FOCUS, banking_blockers)

    basket_result = _mapping(source.get("basket_risk_result"))
    if basket_result.get("status") != BASKET_RISK_EXPOSURE_READY or basket_result.get("ready") is not True:
        return _permission_result(source, BLOCKED_BY_BASKET_RISK, ("basket_risk_result_not_ready",))
    approved_basket = basket_result.get("approved_basket")
    if not isinstance(approved_basket, Sequence) or isinstance(approved_basket, (str, bytes, bytearray)) or not approved_basket:
        return _permission_result(source, BLOCKED_BY_BASKET_RISK, ("approved_basket_empty",))

    permission = _mapping(source.get("permission"))
    proof = _mapping(source.get("proof"))
    runtime = _mapping(source.get("runtime_boundary"))
    if not permission:
        return _permission_result(source, INCOMPLETE_INPUTS, ("permission_missing",))
    missing = tuple(field for field in REQUIRED_PERMISSION_FIELDS if field not in permission)
    if missing:
        return _permission_result(source, INCOMPLETE_INPUTS, tuple(f"missing_{field}" for field in missing))

    mode = str(permission.get("mode", "")).upper()
    if mode not in VALID_MODES:
        return _permission_result(source, INCOMPLETE_INPUTS, ("permission_mode_invalid",))
    if not _bool(permission.get("owner_review_required")):
        return _permission_result(source, BLOCKED_BY_OWNER_GATE, ("owner_review_required_false",))
    if not _bool(permission.get("previous_burst_review_complete")):
        return _permission_result(source, BLOCKED_BY_REVIEW_LOCK, ("previous_burst_review_incomplete",))
    if not _bool(permission.get("receipt_required")) or not _bool(permission.get("post_burst_review_required")):
        return _permission_result(source, BLOCKED_BY_REVIEW_LOCK, ("receipt_or_post_burst_review_requirement_missing",))
    if permission.get("may_execute_by_this_module") is not False or permission.get("may_call_broker_by_this_module") is not False:
        return _permission_result(source, BLOCKED_BY_RUNTIME_BOUNDARY, ("module_execution_or_broker_call_flag_not_false",))

    if mode == "DEMO_BURST":
        status = READY_FOR_DEMO_BURST_RUNTIME_INTENT
    elif mode == "LIVE_MICRO_REVIEW":
        if not _live_proof_ready(proof):
            return _permission_result(source, BLOCKED_BY_PROOF_REQUIREMENT, ("live_micro_proof_not_ready",))
        status = READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW
    else:
        if not _live_proof_ready(proof):
            return _permission_result(source, BLOCKED_BY_PROOF_REQUIREMENT, ("live_micro_proof_not_ready",))
        if not _bool(permission.get("owner_live_approval_metadata_present")):
            return _permission_result(source, BLOCKED_BY_OWNER_GATE, ("owner_live_approval_metadata_missing",))
        if not _runtime_boundary_ready(runtime):
            return _permission_result(source, BLOCKED_BY_RUNTIME_BOUNDARY, ("runtime_boundary_not_ready",))
        status = READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT

    intent = _governed_burst_intent(
        mode=mode,
        basket_result=basket_result,
        approved_basket=approved_basket,
    )
    extra = {"governed_burst_intent": intent}
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=True,
        governed_burst_requested=_governed_requested(source) or True,
        multi_pair_enabled=True,
        blockers=(),
        next_best_packet=_next_packet(status),
        safe_manual_next_action=_safe_manual_next_action(status),
        extra=extra,
    )


def _live_proof_ready(proof: Mapping[str, Any]) -> bool:
    return (
        _bool(proof.get("demo_proof_ready"))
        and _bool(proof.get("live_micro_review_ready"))
        and _number(proof.get("repeatability_score")) >= 70
    )


def _runtime_boundary_ready(runtime: Mapping[str, Any]) -> bool:
    return (
        _bool(runtime.get("runtime_session_available"))
        and runtime.get("credential_values_in_payload") is False
        and runtime.get("account_id_in_payload") is False
        and _bool(runtime.get("no_stored_credentials"))
    )


def _governed_burst_intent(
    *,
    mode: str,
    basket_result: Mapping[str, Any],
    approved_basket: Sequence[Any],
) -> dict[str, Any]:
    basket = [dict(item) for item in approved_basket if isinstance(item, Mapping)]
    return {
        "mode": mode,
        "approved_basket": basket,
        "order_count": len(basket),
        "pairs": [str(item.get("pair", "")) for item in basket],
        "total_burst_risk_pct": basket_result.get("total_burst_risk_pct", 0.0),
        "receipt_required": True,
        "post_burst_review_required": True,
        "execute_by_this_module": False,
        "call_broker_by_this_module": False,
        "no_next_burst_without_review": True,
    }


def _permission_result(source: Mapping[str, Any], status: str, blockers: Sequence[str]) -> dict[str, Any]:
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=False,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=False,
        blockers=blockers,
        next_best_packet=NEXT_BEST_PACKET,
        safe_manual_next_action=_safe_manual_next_action(status),
        extra={"governed_burst_intent": {}},
    )


def _next_packet(status: str) -> str:
    if status == READY_FOR_DEMO_BURST_RUNTIME_INTENT:
        return "AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1"
    if status == READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW:
        return "AIOS_FOREX_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW_V1"
    if status == READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT:
        return "AIOS_FOREX_OWNER_APPROVED_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1"
    return NEXT_BEST_PACKET


def _safe_manual_next_action(status: str) -> str:
    if status == READY_FOR_DEMO_BURST_RUNTIME_INTENT:
        return "Owner may review a separate demo multi-pair burst runtime packet."
    if status == READY_FOR_LIVE_MICRO_BURST_OWNER_REVIEW:
        return "Owner may review live micro multi-pair burst evidence."
    if status == READY_FOR_PROTECTED_LIVE_MICRO_BURST_RUNTIME_INTENT:
        return "Owner may review protected live micro burst runtime intent; no execution occurs here."
    if status == BLOCKED_BY_BASKET_RISK:
        return "Repair basket risk result before burst permission review."
    if status == BLOCKED_BY_OWNER_GATE:
        return "Repair owner review or live approval metadata."
    if status == BLOCKED_BY_RUNTIME_BOUNDARY:
        return "Repair runtime boundary metadata without credentials or account values."
    if status == BLOCKED_BY_PROOF_REQUIREMENT:
        return "Continue proof capture before live burst review."
    if status == BLOCKED_BY_REVIEW_LOCK:
        return "Complete previous burst review before another burst."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, or money-movement focus fields."
    return "Provide complete governed burst permission metadata."
