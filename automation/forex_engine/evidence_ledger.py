"""Paper-only in-memory evidence ledger for Forex engine events."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

EVIDENCE_LEDGER_MODE = "PAPER_ONLY"
EVIDENCE_LEDGER_ALLOWED = "allowed"
EVIDENCE_LEDGER_BLOCKED = "blocked"

EVIDENCE_EVENT_TYPES = {
    "market_data_accepted",
    "market_data_rejected",
    "strategy_candidate_created",
    "candidate_rejected",
    "preview_created",
    "preview_rejected",
    "risk_accepted",
    "risk_rejected",
    "paper_trade_opened",
    "paper_trade_closed",
    "balance_updated",
    "kill_switch_triggered",
    "session_summary_generated",
}

EVIDENCE_REJECTION_REASONS = [
    "none",
    "invalid_event",
    "invalid_event_type",
    "missing_session_id",
    "missing_event_id",
    "missing_timestamp",
    "invalid_payload",
    "non_paper_mode",
    "live_trading_blocked",
    "duplicate_event_id",
    "evidence_chain_broken",
    "unsupported_replay_event",
    "evidence_path_invalid",
]


def _safe_is_evidence_path_valid(path: Any) -> bool:
    if path is None or path == "":
        return True
    if not isinstance(path, str):
        return False
    if path.startswith("/"):
        return False
    if len(path) >= 3 and path[1:3] == ":\\":
        return False
    return True


def _coerce_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _coerce_payload(payload: Any) -> Dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, Mapping):
        return dict(payload)
    return {}


def _payload_fingerprint(payload: Mapping[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def _make_safety_dict() -> Dict[str, Any]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _make_base_event(
    event_type: str,
    payload: Dict[str, Any],
    session_id: Any,
    event_id: Optional[str],
    timestamp: Optional[float],
    parent_event_id: Optional[str],
    sequence: int,
    evidence_path: Optional[str],
    metadata: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    deterministic_id_source = f"{event_type}|{session_id}|{timestamp}|{_payload_fingerprint(payload)}"
    resolved_id = event_id or hashlib.sha256(deterministic_id_source.encode("utf-8")).hexdigest()[:24]
    return {
        "event_id": resolved_id,
        "event_type": event_type,
        "session_id": session_id,
        "timestamp": timestamp,
        "parent_event_id": parent_event_id,
        "sequence": sequence,
        "payload": payload,
        "paper_only": True,
        "mode": EVIDENCE_LEDGER_MODE,
        "evidence_path": evidence_path,
        "safety": _make_safety_dict(),
        "metadata": dict(metadata or {}),
    }


def _validate_single_event(event: Any, existing_ids: Optional[set[str]] = None) -> List[str]:
    reasons: List[str] = []
    if not isinstance(event, Mapping):
        return ["invalid_event"]
    event_type = event.get("event_type")
    if event_type not in EVIDENCE_EVENT_TYPES:
        reasons.append("invalid_event_type")
    if not event.get("session_id"):
        reasons.append("missing_session_id")
    if not event.get("event_id"):
        reasons.append("missing_event_id")
    if _coerce_float(event.get("timestamp")) is None:
        reasons.append("missing_timestamp")
    if not isinstance(event.get("payload"), Mapping):
        reasons.append("invalid_payload")
    if event.get("paper_only") is False:
        reasons.append("non_paper_mode")
    mode = str(event.get("mode", "")).lower()
    if mode not in {"", EVIDENCE_LEDGER_MODE.lower()}:
        reasons.append("live_trading_blocked")
    if existing_ids is not None and event.get("event_id") in existing_ids:
        reasons.append("duplicate_event_id")
    parent_id = event.get("parent_event_id")
    if parent_id and existing_ids is not None and parent_id not in existing_ids:
        reasons.append("evidence_chain_broken")
    return reasons


def _validate_ordering_and_parent(ledger: Iterable[Mapping[str, Any]]) -> tuple[bool, List[str]]:
    seen_ids = set()
    reasons: List[str] = []
    sequence = 0
    for event in ledger:
        if not isinstance(event, Mapping):
            reasons.append("invalid_event")
            continue
        event_id = event.get("event_id")
        if not event_id:
            reasons.append("missing_event_id")
            continue
        if event_id in seen_ids:
            reasons.append("duplicate_event_id")
        seen_ids.add(event_id)
        event_sequence = event.get("sequence")
        if event_sequence not in {sequence, 0}:
            reasons.append("invalid_event")
        parent = event.get("parent_event_id")
        if parent and parent not in seen_ids:
            reasons.append("evidence_chain_broken")
        sequence += 1
    return (len(reasons) == 0, reasons)


def build_ledger_event(
    event_type: str,
    payload: Optional[Mapping[str, Any]] = None,
    session_id: Optional[str] = None,
    event_id: Optional[str] = None,
    timestamp: Optional[float] = None,
    parent_event_id: Optional[str] = None,
    evidence_path: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    event_type_value = str(event_type or "")
    if not _safe_is_evidence_path_valid(evidence_path):
        return {
            "event_id": None,
            "event_type": event_type_value,
            "session_id": session_id,
            "timestamp": _coerce_float(timestamp),
            "parent_event_id": parent_event_id,
            "sequence": -1,
            "payload": {},
            "paper_only": True,
            "mode": EVIDENCE_LEDGER_MODE,
            "evidence_path": evidence_path,
            "safety": _make_safety_dict(),
            "metadata": {"provided": dict(metadata or {})},
            "allowed": False,
            "decision": EVIDENCE_LEDGER_BLOCKED,
            "blocked_reason": "evidence_path_invalid",
            "blocked_reasons": ["evidence_path_invalid"],
            "warnings": [],
        }

    normalized_payload = _coerce_payload(payload)
    base_timestamp = _coerce_float(timestamp)
    if base_timestamp is None:
        base_timestamp = -1.0
    validated_reasons = []
    if event_type_value not in EVIDENCE_EVENT_TYPES:
        validated_reasons.append("invalid_event_type")
    if not session_id:
        validated_reasons.append("missing_session_id")
    if not normalized_payload and payload is not None and not isinstance(payload, Mapping):
        validated_reasons.append("invalid_payload")
    if _coerce_float(timestamp) is None:
        validated_reasons.append("missing_timestamp")

    event = _make_base_event(
        event_type=event_type_value,
        payload=normalized_payload,
        session_id=session_id,
        event_id=event_id,
        timestamp=base_timestamp,
        parent_event_id=parent_event_id,
        sequence=0,
        evidence_path=evidence_path,
        metadata=metadata,
    )

    if validated_reasons:
        event.update(
            {
                "allowed": False,
                "decision": EVIDENCE_LEDGER_BLOCKED,
                "blocked_reason": validated_reasons[0],
                "blocked_reasons": validated_reasons,
                "warnings": [],
            }
        )
    else:
        event.update(
            {
                "allowed": True,
                "decision": EVIDENCE_LEDGER_ALLOWED,
                "blocked_reason": "none",
                "blocked_reasons": ["none"],
                "warnings": [],
            }
        )
    return event


def append_ledger_event(
    ledger: Optional[Iterable[Mapping[str, Any]]],
    event: Mapping[str, Any],
) -> Dict[str, Any]:
    base_ledger = list(ledger or [])
    if not isinstance(ledger, Iterable):
        base_ledger = []
    # no in-place mutation.
    next_ledger = list(base_ledger)
    existing_ids = {str(item.get("event_id")) for item in next_ledger if isinstance(item, Mapping) and item.get("event_id")}

    if not isinstance(event, Mapping):
        return {
            "allowed": False,
            "decision": EVIDENCE_LEDGER_BLOCKED,
            "blocked_reason": "invalid_event",
            "blocked_reasons": ["invalid_event"],
            "warnings": [],
            "event": event,
            "ledger": next_ledger,
            "safety": _make_safety_dict(),
            "metadata": {},
            "next_sequence": len(next_ledger),
        }

    event_id = event.get("event_id")
    if not event_id:
        event_id = None
    prepared_payload = dict(event.get("payload", {})) if isinstance(event.get("payload"), Mapping) else {}
    sequence = len(next_ledger)

    validated = _validate_single_event(
        {
            "event_type": event.get("event_type"),
            "session_id": event.get("session_id"),
            "event_id": event_id,
            "timestamp": event.get("timestamp"),
            "payload": prepared_payload,
            "paper_only": event.get("paper_only", True),
            "mode": event.get("mode", EVIDENCE_LEDGER_MODE),
            "parent_event_id": event.get("parent_event_id"),
        },
        existing_ids=existing_ids,
    )

    reason_set = list(dict.fromkeys(validated))
    if reason_set:
        return {
            "allowed": False,
            "decision": EVIDENCE_LEDGER_BLOCKED,
            "blocked_reason": reason_set[0],
            "blocked_reasons": reason_set,
            "warnings": [],
            "event": event,
            "ledger": next_ledger,
            "safety": _make_safety_dict(),
            "metadata": dict(event.get("metadata", {})),
            "next_sequence": sequence,
        }

    normalized_event = _make_base_event(
        event_type=str(event.get("event_type")),
        payload=prepared_payload,
        session_id=event.get("session_id"),
        event_id=event_id,
        timestamp=_coerce_float(event.get("timestamp")),
        parent_event_id=event.get("parent_event_id"),
        sequence=sequence,
        evidence_path=event.get("evidence_path"),
        metadata=event.get("metadata"),
    )
    normalized_event["allowed"] = True
    normalized_event["decision"] = EVIDENCE_LEDGER_ALLOWED
    normalized_event["blocked_reason"] = "none"
    normalized_event["blocked_reasons"] = ["none"]
    normalized_event["warnings"] = []

    if event_id is not None and event_id not in existing_ids:
        normalized_event["event_id"] = event_id
    next_ledger.append(normalized_event)
    return {
        "allowed": True,
        "decision": EVIDENCE_LEDGER_ALLOWED,
        "blocked_reason": "none",
        "blocked_reasons": [],
        "warnings": [],
        "event": normalized_event,
        "ledger": next_ledger,
        "safety": _make_safety_dict(),
        "metadata": dict(event.get("metadata", {})),
        "next_sequence": len(next_ledger),
    }


def validate_ledger(
    ledger: Optional[Iterable[Mapping[str, Any]]],
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    events = list(ledger or [])
    if not isinstance(ledger, Iterable):
        return {
            "valid": False,
            "errors": ["invalid_event"],
            "warnings": [],
            "event_count": 0,
            "session_id": session_id,
            "paper_only": True,
            "mode": EVIDENCE_LEDGER_MODE,
            "safety": _make_safety_dict(),
            "metadata": {},
        }

    filtered_events = [
        e for e in events
        if isinstance(e, Mapping) and (session_id is None or e.get("session_id") == session_id)
    ]

    errors: List[str] = []
    if any(e.get("session_id") is None for e in filtered_events):
        errors.append("missing_session_id")
    if any(e.get("event_id") is None for e in filtered_events):
        errors.append("missing_event_id")

    # deterministic sequence and parent checks
    _, ordering_errors = _validate_ordering_and_parent(filtered_events)
    errors.extend(ordering_errors)

    for event in filtered_events:
        errors.extend(_validate_single_event(event))

    dedup_errors = []
    ids = set()
    for event in filtered_events:
        event_id = event.get("event_id")
        if event_id in ids:
            dedup_errors.append("duplicate_event_id")
        ids.add(event_id)
    errors.extend(dedup_errors)
    # validate parent references only inside provided session scope
    id_set = {e.get("event_id") for e in filtered_events if isinstance(e, Mapping)}
    for event in filtered_events:
        parent = event.get("parent_event_id")
        if parent and parent not in id_set:
            errors.append("evidence_chain_broken")

    normalized_errors = list(dict.fromkeys(errors))
    return {
        "valid": len(normalized_errors) == 0,
        "errors": normalized_errors,
        "warnings": [],
        "event_count": len(filtered_events),
        "session_id": session_id,
        "paper_only": True,
        "mode": EVIDENCE_LEDGER_MODE,
        "safety": _make_safety_dict(),
        "metadata": {},
    }


def replay_ledger(
    ledger: Optional[Iterable[Mapping[str, Any]]],
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    base = list(ledger or [])
    validation = validate_ledger(base, session_id=session_id)
    events = [e for e in base if isinstance(e, Mapping) and (session_id is None or e.get("session_id") == session_id)]

    counts_by_event_type: Dict[str, int] = {}
    for event in events:
        event_type = str(event.get("event_type", ""))
        counts_by_event_type[event_type] = counts_by_event_type.get(event_type, 0) + 1

    summary = {
        "total_events": len(events),
        "counts_by_event_type": counts_by_event_type,
        "accepted_market_data": counts_by_event_type.get("market_data_accepted", 0),
        "rejected_market_data": counts_by_event_type.get("market_data_rejected", 0),
        "candidates_created": counts_by_event_type.get("strategy_candidate_created", 0),
        "candidates_rejected": counts_by_event_type.get("candidate_rejected", 0),
        "previews_created": counts_by_event_type.get("preview_created", 0),
        "previews_rejected": counts_by_event_type.get("preview_rejected", 0),
        "risk_accepted": counts_by_event_type.get("risk_accepted", 0),
        "risk_rejected": counts_by_event_type.get("risk_rejected", 0),
        "trades_opened": counts_by_event_type.get("paper_trade_opened", 0),
        "trades_closed": counts_by_event_type.get("paper_trade_closed", 0),
        "balance_updates": counts_by_event_type.get("balance_updated", 0),
        "kill_switch_events": counts_by_event_type.get("kill_switch_triggered", 0),
        "session_summaries": counts_by_event_type.get("session_summary_generated", 0),
        "missing_parent_events": 0,
        "invalid_events": 0,
        "valid": validation["valid"],
        "validation_errors": validation["errors"],
        "allowed": validation["valid"],
        "decision": EVIDENCE_LEDGER_ALLOWED if validation["valid"] else EVIDENCE_LEDGER_BLOCKED,
        "blocked_reason": "none" if validation["valid"] else (validation["errors"][0] if validation["errors"] else "invalid_event"),
        "blocked_reasons": validation["errors"] if not validation["valid"] else [],
        "warnings": [],
        "event_sequence": [event.get("event_id") for event in events],
        "paper_only": True,
        "mode": EVIDENCE_LEDGER_MODE,
        "session_id": session_id,
        "safety": _make_safety_dict(),
        "metadata": {},
    }

    id_seen = set()
    for event in events:
        event_id = event.get("event_id")
        parent_event_id = event.get("parent_event_id")
        if event_id is None:
            summary["invalid_events"] += 1
            continue
        if event_id in id_seen:
            summary["invalid_events"] += 1
        id_seen.add(event_id)
        if parent_event_id and parent_event_id not in id_seen:
            summary["missing_parent_events"] += 1
            summary["invalid_events"] += 1

    if validation["errors"]:
        summary["decision"] = EVIDENCE_LEDGER_BLOCKED
        summary["blocked_reason"] = validation["errors"][0]
        summary["blocked_reasons"] = validation["errors"]
    return summary
