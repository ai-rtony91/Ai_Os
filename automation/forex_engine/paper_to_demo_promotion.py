"""Paper-to-demo promotion gate for AIOS Forex evidence."""

from __future__ import annotations

from typing import Any, Mapping


PROMOTION_MODE = "PAPER_TO_DEMO_PROMOTION_ONLY"
DECISION_ALLOWED = "allowed"
DECISION_BLOCKED = "blocked"

REASON_NONE = "none"
REASON_MISSING_REPLAY = "missing_session_replay"
REASON_MISSING_EVIDENCE = "missing_evidence_ledger"
REASON_TRADE_COUNT_LOW = "trade_count_below_threshold"
REASON_SESSION_COUNT_LOW = "session_count_below_threshold"
REASON_RISK_FAILURES_UNRESOLVED = "risk_failures_unresolved"
REASON_DRAWDOWN_TOO_HIGH = "drawdown_too_high"
REASON_READONLY_FAILED = "demo_readonly_failed"
REASON_MAPPING_FAILED = "demo_mapping_failed"
REASON_RECONCILIATION_FAILED = "demo_reconciliation_failed"
REASON_ACCOUNT_ID_PRESENT = "account_id_present"
REASON_CREDENTIALS_LOADED = "credentials_loaded"
REASON_BROKER_WRITE_ENABLED = "broker_write_enabled"
REASON_ORDER_SUBMIT_ENABLED = "order_submit_enabled"
REASON_NETWORK_SUBMIT_ENABLED = "network_submit_enabled"
REASON_LIVE_TRADING_ENABLED = "live_trading_enabled"
REASON_REQUESTED_LIVE_OR_BROKER_ACTION = "requested_live_or_broker_action"


def evaluate_paper_to_demo_promotion(
    session_replay: Any,
    evidence_ledger: Any,
    long_run_supervisor: Any,
    self_improvement_review: Any,
    demo_connector_readonly: Any,
    demo_order_mapping: Any,
    demo_reconciliation: Any,
    limits: Any = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Decide whether mature paper evidence may proceed to demo-only workflows."""

    replay = _as_mapping(session_replay)
    ledger = _as_mapping(evidence_ledger)
    supervisor = _as_mapping(long_run_supervisor)
    improvement = _as_mapping(self_improvement_review)
    readonly = _as_mapping(demo_connector_readonly)
    mapping = _as_mapping(demo_order_mapping)
    reconciliation = _as_mapping(demo_reconciliation)
    limit_cfg = _limits(limits)

    blocked_reasons: list[str] = []
    missing_requirements: list[str] = []

    if not replay:
        blocked_reasons.append(REASON_MISSING_REPLAY)
        missing_requirements.append("session_replay")
    if not ledger or ledger.get("allowed") is False or ledger.get("validation_passed") is False:
        blocked_reasons.append(REASON_MISSING_EVIDENCE)
        missing_requirements.append("evidence_ledger")

    trade_count = _count(replay, "trade_count", "total_trades", "completed_trades", "replayed_trades", list_key="trades")
    session_count = _count(replay, "session_count", "total_sessions", "replayed_sessions", list_key="sessions")
    if replay and session_count == 0:
        session_count = _count(supervisor, "session_count", "total_sessions", "completed_sessions", list_key="sessions")

    minimum_trade_count_met = trade_count >= limit_cfg["minimum_trade_count"]
    minimum_session_count_met = session_count >= limit_cfg["minimum_session_count"]
    if not minimum_trade_count_met:
        blocked_reasons.append(REASON_TRADE_COUNT_LOW)
        missing_requirements.append("minimum_trade_count")
    if not minimum_session_count_met:
        blocked_reasons.append(REASON_SESSION_COUNT_LOW)
        missing_requirements.append("minimum_session_count")

    risk_failures = _risk_failures(replay, ledger, supervisor, improvement)
    risk_compliance_met = not risk_failures
    if not risk_compliance_met:
        blocked_reasons.append(REASON_RISK_FAILURES_UNRESOLVED)
        missing_requirements.append("risk_compliance")

    drawdown = _drawdown(replay, ledger, supervisor)
    drawdown_within_limit = drawdown <= limit_cfg["maximum_drawdown_pct"]
    if not drawdown_within_limit:
        blocked_reasons.append(REASON_DRAWDOWN_TOO_HIGH)
        missing_requirements.append("drawdown_within_limit")

    readonly_ready = readonly.get("allowed") is True
    mapping_ready = mapping.get("allowed") is True
    reconciliation_ready = reconciliation.get("allowed") is True and (
        reconciliation.get("matched") is True or reconciliation.get("match_score") == 1.0
    )
    if not readonly_ready:
        blocked_reasons.append(REASON_READONLY_FAILED)
        missing_requirements.append("demo_readonly")
    if not mapping_ready:
        blocked_reasons.append(REASON_MAPPING_FAILED)
        missing_requirements.append("demo_order_mapping")
    if not reconciliation_ready:
        blocked_reasons.append(REASON_RECONCILIATION_FAILED)
        missing_requirements.append("demo_reconciliation")

    for payload in (replay, ledger, supervisor, improvement, readonly, mapping, reconciliation):
        blocked_reasons.extend(_runtime_blockers(payload))

    blocked_reasons = _dedupe(blocked_reasons)
    missing_requirements = _dedupe(missing_requirements)
    evidence_score = _score(
        bool(replay),
        bool(ledger) and REASON_MISSING_EVIDENCE not in blocked_reasons,
        minimum_trade_count_met,
        minimum_session_count_met,
        risk_compliance_met,
        drawdown_within_limit,
        readonly_ready,
        mapping_ready,
        reconciliation_ready,
    )
    allowed = not blocked_reasons

    return {
        "allowed": allowed,
        "decision": DECISION_ALLOWED if allowed else DECISION_BLOCKED,
        "blocked_reason": REASON_NONE if allowed else blocked_reasons[0],
        "blocked_reasons": [] if allowed else blocked_reasons,
        "warnings": [],
        "mode": PROMOTION_MODE,
        "paper_only": True,
        "demo_promotion_ready": allowed,
        "evidence_score": evidence_score,
        "minimum_trade_count_met": minimum_trade_count_met,
        "minimum_session_count_met": minimum_session_count_met,
        "risk_compliance_met": risk_compliance_met,
        "drawdown_within_limit": drawdown_within_limit,
        "reconciliation_ready": reconciliation_ready,
        "readonly_ready": readonly_ready,
        "mapping_ready": mapping_ready,
        "missing_requirements": missing_requirements,
        "safety": _safety_dict(),
        "next_safe_action": "proceed_to_demo_readonly_mapping_reconciliation" if allowed else "continue_paper_evidence_collection",
        "metadata": {
            "trade_count": trade_count,
            "session_count": session_count,
            "drawdown_pct": drawdown,
            "risk_failures": risk_failures,
            "limits": dict(limit_cfg),
            **dict(metadata or {}),
        },
    }


def _runtime_blockers(value: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key, nested in _walk(value):
        normalized = _normalize_key(key)
        if "account" in normalized and "id" in normalized and _present(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
        if "credential" in normalized and "load" in normalized and _truthy(nested):
            blockers.append(REASON_CREDENTIALS_LOADED)
        if "broker" in normalized and "write" in normalized and _truthy(nested):
            blockers.append(REASON_BROKER_WRITE_ENABLED)
        if "order" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_ORDER_SUBMIT_ENABLED)
        if "network" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_NETWORK_SUBMIT_ENABLED)
        if "live" in normalized and "trading" in normalized and _truthy(nested):
            blockers.append(REASON_LIVE_TRADING_ENABLED)
        if "requested" in normalized and _requests_live_or_broker(nested):
            blockers.append(REASON_REQUESTED_LIVE_OR_BROKER_ACTION)
        if isinstance(nested, str) and _looks_like_account_identifier(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
    return blockers


def _limits(value: Any) -> dict[str, float]:
    raw = _as_mapping(value)
    return {
        "minimum_trade_count": _number(raw.get("minimum_trade_count"), 20.0),
        "minimum_session_count": _number(raw.get("minimum_session_count"), 3.0),
        "maximum_drawdown_pct": _number(raw.get("maximum_drawdown_pct"), 10.0),
    }


def _risk_failures(*payloads: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for payload in payloads:
        for key in ("risk_failures", "unresolved_risk_failures", "risk_blockers", "blocked_reasons"):
            value = payload.get(key)
            if isinstance(value, list):
                failures.extend(str(item) for item in value if str(item))
        if payload.get("risk_compliance_met") is False:
            failures.append("risk_compliance_false")
        if payload.get("risk_status") in {"failed", "blocked", "FAIL", "BLOCKED"}:
            failures.append(str(payload.get("risk_status")))
    return _dedupe(failures)


def _drawdown(*payloads: Mapping[str, Any]) -> float:
    for payload in payloads:
        for key in ("max_drawdown_pct", "drawdown_pct", "maximum_drawdown_pct"):
            value = payload.get(key)
            if value not in (None, ""):
                return _number(value, 0.0)
    return 0.0


def _count(payload: Mapping[str, Any], *keys: str, list_key: str) -> float:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return _number(value, 0.0)
    value = payload.get(list_key)
    if isinstance(value, list):
        return float(len(value))
    return 0.0


def _score(*checks: bool) -> float:
    if not checks:
        return 0.0
    return round(sum(1 for item in checks if item) / len(checks), 6)


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _walk(value: Any) -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            out.append((str(key), nested))
            out.extend(_walk(nested))
    elif isinstance(value, list):
        for nested in value:
            out.extend(_walk(nested))
    return out


def _number(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    return False


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _requests_live_or_broker(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        return False
    text = value.strip().lower()
    return any(marker in text for marker in ("live", "broker", "submit", "order", "write"))


def _looks_like_account_identifier(value: str) -> bool:
    parts = value.strip().split("-")
    return len(parts) >= 3 and all(part.isdigit() for part in parts)


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _dedupe(items: list[str]) -> list[str]:
    ordered: list[str] = []
    for item in items:
        if item and item not in ordered:
            ordered.append(item)
    return ordered


def _safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_promotion_only": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
