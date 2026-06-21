from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict, List, Mapping, Sequence

DEMO_CANDIDATE_CREATED = "DEMO_CANDIDATE_CREATED"
DEMO_CANDIDATE_ACTIVE = "DEMO_CANDIDATE_ACTIVE"
DEMO_CANDIDATE_PAUSED = "DEMO_CANDIDATE_PAUSED"
DEMO_CANDIDATE_REVOKED = "DEMO_CANDIDATE_REVOKED"
DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION = "DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION"

CAMPAIGN_DEMO_CANDIDATE = "CAMPAIGN_DEMO_CANDIDATE"
CAMPAIGN_MORE_EVIDENCE_REQUIRED = "CAMPAIGN_MORE_EVIDENCE_REQUIRED"
CAMPAIGN_BLOCKED = "CAMPAIGN_BLOCKED"
CAMPAIGN_REJECTED = "CAMPAIGN_REJECTED"


def _to_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _state_hash(*parts: Any) -> str:
    material = "|".join(_to_str(item) for item in parts)
    return sha256(material.encode("utf-8")).hexdigest()


def _read_numeric_metrics(campaign: Mapping[str, Any]) -> Dict[str, Any]:
    metrics = campaign.get("campaign_metrics", {})
    if not isinstance(metrics, Mapping):
        metrics = {}

    return {
        "trade_count": _to_int(metrics.get("trade_count", campaign.get("trade_count", 0))),
        "session_count": _to_int(metrics.get("session_count", campaign.get("session_count", 0))),
        "expectancy": _to_float(metrics.get("expectancy", campaign.get("expectancy", 0.0))),
        "profit_factor": _to_float(metrics.get("profit_factor", campaign.get("profit_factor", 0.0))),
        "drawdown": _to_float(metrics.get("drawdown", campaign.get("max_drawdown", campaign.get("drawdown", 0.0)))),
        "evidence_score": _to_float(metrics.get("evidence_score", campaign.get("evidence_score", 0.0))),
        "campaign_status": _to_str(campaign.get("campaign_status", "")),
        "promotion_timestamp": _to_str(campaign.get("campaign_next_safe_action", metrics.get("promotion_timestamp", ""))),
    }


def _transition(
    current_state: str,
    requested_transition: str,
    candidate_record_exists: bool,
) -> tuple[str, str]:
    request = (requested_transition or "").strip().upper()

    if current_state == DEMO_CANDIDATE_REVOKED:
        return current_state, f"no_transition_from_{current_state}"

    if request == "":
        if not candidate_record_exists:
            return DEMO_CANDIDATE_CREATED, "created_from_campaign_signal"
        return current_state, "state_unchanged"

    if current_state == DEMO_CANDIDATE_CREATED:
        if request == "ACTIVATE":
            return DEMO_CANDIDATE_ACTIVE, "created_to_active"
        if request == "REVOKE":
            return DEMO_CANDIDATE_REVOKED, "created_to_revoked"
        return current_state, f"invalid_transition_{current_state}_to_{request}"

    if current_state == DEMO_CANDIDATE_ACTIVE:
        if request == "APPROVE":
            return DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION, "active_to_approved"
        if request == "PAUSE":
            return DEMO_CANDIDATE_PAUSED, "active_to_paused"
        if request == "REVOKE":
            return DEMO_CANDIDATE_REVOKED, "active_to_revoked"
        return current_state, f"invalid_transition_{current_state}_to_{request}"

    if current_state == DEMO_CANDIDATE_PAUSED:
        if request == "ACTIVATE":
            return DEMO_CANDIDATE_ACTIVE, "paused_to_active"
        if request == "REVOKE":
            return DEMO_CANDIDATE_REVOKED, "paused_to_revoked"
        return current_state, f"invalid_transition_{current_state}_to_{request}"

    if current_state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION:
        if request in {"REVOKE", "PAUSE"}:
            return DEMO_CANDIDATE_REVOKED if request == "REVOKE" else current_state, (
                "approved_to_paused_blocked" if request == "PAUSE" else "approved_to_revoked"
            )
        return current_state, f"invalid_transition_{current_state}_to_{request}"

    return current_state, "invalid_previous_state"


def _next_action(state: str) -> str:
    if state == DEMO_CANDIDATE_CREATED:
        return "activate_candidate"
    if state == DEMO_CANDIDATE_ACTIVE:
        return "approve_or_pause_candidate"
    if state == DEMO_CANDIDATE_PAUSED:
        return "investigate_and_resume_or_revoke"
    if state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION:
        return "start_demo_validation"
    if state == DEMO_CANDIDATE_REVOKED:
        return "investigate_reactivation_request_manually"
    return "create_candidate"


def _candidate_id(metadata: Mapping[str, Any], campaign: Mapping[str, Any]) -> str:
    return _state_hash(
        _to_str(metadata.get("strategy_id", "unknown")),
        _to_str(metadata.get("strategy_name", "unknown")),
        _to_str(campaign.get("campaign_status", "")),
    )[:24]


def _coerce_history(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence):
        return []
    out: List[Dict[str, Any]] = []
    for item in value:
        if isinstance(item, Mapping):
            out.append(dict(item))
    return out


def _required_history_entry(
    previous_state: str,
    new_state: str,
    reason: str,
    campaign_status: str,
) -> Dict[str, Any]:
    return {
        "timestamp": _state_hash(previous_state, new_state, reason, campaign_status),
        "previous_state": previous_state,
        "new_state": new_state,
        "reason": reason,
        "campaign_status": campaign_status,
    }


def evaluate_demo_candidate_lifecycle(
    campaign_supervisor_result: Mapping[str, Any] | None,
    candidate_metadata: Mapping[str, Any] | None,
    optional_previous_lifecycle_record: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    campaign = campaign_supervisor_result or {}
    metadata = candidate_metadata or {}
    previous = optional_previous_lifecycle_record or {}

    campaign_status = _to_str(campaign.get("campaign_status", ""))
    blockers: List[str] = []
    history: List[Dict[str, Any]] = _coerce_history(previous.get("candidate_history"))

    if not campaign:
        blockers.append("missing_campaign_result")
        return {
            "lifecycle_completed": False,
            "candidate_id": "",
            "candidate_state": _to_str(previous.get("candidate_state", "")),
            "candidate_created": False,
            "candidate_approved": False,
            "candidate_blockers": blockers,
            "candidate_reason": "missing_campaign_supervisor_result",
            "candidate_history": history,
            "candidate_next_safe_action": "submit_missing_campaign_result",
            "operator_review_required": True,
            "safety": {
                "paper_only": True,
                "broker_connection_active": False,
                "network_access": False,
                "credentials_accessed": False,
                "order_execution_enabled": False,
                "demo_execution_active": False,
                "live_trading_authorized": False,
                "capital_allocated": False,
                "capital_allocation_modified": False,
                "operator_review_required": True,
            },
            "candidate_metrics": {
                "trade_count": 0,
                "session_count": 0,
                "expectancy": 0.0,
                "profit_factor": 0.0,
                "drawdown": 0.0,
                "evidence_score": 0.0,
                "campaign_status": campaign_status,
                "promotion_timestamp": "",
            },
        }

    if campaign_status != CAMPAIGN_DEMO_CANDIDATE:
        blockers.append(f"campaign_status_not_demo_candidate:{campaign_status}")
        current_state = _to_str(previous.get("candidate_state", ""))
        return {
            "lifecycle_completed": True,
            "candidate_id": _candidate_id(metadata, campaign),
            "candidate_state": current_state,
            "candidate_created": bool(previous.get("candidate_created", False)),
            "candidate_approved": bool(previous.get("candidate_approved", False)),
            "candidate_blockers": blockers,
            "candidate_reason": "campaign_not_demo_candidate",
            "candidate_history": history,
            "candidate_next_safe_action": "wait_for_demo_candidate_status",
            "operator_review_required": True,
            "safety": {
                "paper_only": True,
                "broker_connection_active": False,
                "network_access": False,
                "credentials_accessed": False,
                "order_execution_enabled": False,
                "demo_execution_active": False,
                "live_trading_authorized": False,
                "capital_allocated": False,
                "capital_allocation_modified": False,
                "operator_review_required": True,
            },
            "candidate_metrics": _read_numeric_metrics(campaign),
        }

    previous_state = _to_str(previous.get("candidate_state"))
    if not previous_state:
        previous_state = ""

    requested_transition = ""
    if "requested_transition" in metadata and metadata["requested_transition"] is not None:
        requested_transition = _to_str(metadata["requested_transition"])
    elif "requested_action" in metadata and metadata["requested_action"] is not None:
        requested_transition = _to_str(metadata["requested_action"])

    effective_current = previous_state
    has_record = bool(previous_state)
    if not has_record and requested_transition:
        effective_current = DEMO_CANDIDATE_CREATED
        has_record = True

    new_state, reason = _transition(effective_current, requested_transition, has_record)

    if new_state != effective_current:
        history.append(_required_history_entry(effective_current, new_state, reason, campaign_status))

    if not history:
        history.append(_required_history_entry("", new_state, "initial_record", campaign_status))

    lifecycle_completed = new_state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION
    candidate_created = new_state == DEMO_CANDIDATE_CREATED and not previous
    candidate_approved = new_state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION
    reason_msg = reason

    if reason.startswith("invalid_transition_"):
        blockers.append("invalid_transition")
        lifecycle_completed = False

    if "no_transition_from_DEMO_CANDIDATE_REVOKED" in reason:
        blockers.append("candidate_revoked")
        lifecycle_completed = True

    return {
        "lifecycle_completed": lifecycle_completed,
        "candidate_id": _candidate_id(metadata, campaign),
        "candidate_state": new_state,
        "candidate_created": candidate_created,
        "candidate_approved": candidate_approved,
        "candidate_blockers": blockers,
        "candidate_reason": reason_msg,
        "candidate_history": history,
        "candidate_next_safe_action": _next_action(new_state),
        "operator_review_required": True,
        "safety": {
            "paper_only": True,
            "broker_connection_active": False,
            "network_access": False,
            "credentials_accessed": False,
            "order_execution_enabled": False,
            "demo_execution_active": False,
            "live_trading_authorized": False,
            "capital_allocated": False,
            "capital_allocation_modified": False,
            "operator_review_required": True,
        },
        "candidate_metrics": _read_numeric_metrics(campaign),
    }
