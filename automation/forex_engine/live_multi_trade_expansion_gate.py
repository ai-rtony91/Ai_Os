"""Protected live multi-trade expansion gate for AIOS Forex."""

from __future__ import annotations

from typing import Any, Mapping


GATE_MODE = "LIVE_MULTI_TRADE_EXPANSION_REVIEW_ONLY"
DECISION_REVIEW_ONLY = "REVIEW_ONLY"
DECISION_REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"

REASON_NONE = "none"
REASON_HUMAN_APPROVAL_MISSING = "human_approval_missing"
REASON_FIRST_LIVE_MICRO_PROOF_MISSING = "first_live_micro_proof_missing"
REASON_LIVE_READINESS_REVIEW_MISSING = "live_readiness_review_missing"
REASON_KILL_SWITCH_MISSING = "kill_switch_missing"
REASON_ROLLBACK_MISSING = "rollback_missing"
REASON_RECONCILIATION_UNRESOLVED = "reconciliation_unresolved"
REASON_DRAWDOWN_TOO_HIGH = "drawdown_too_high"
REASON_RISK_FAILURES_UNRESOLVED = "risk_failures_unresolved"
REASON_EXCESSIVE_LIVE_TRADE_COUNT = "excessive_requested_live_trade_count"
REASON_EXCESSIVE_RISK_CAP = "excessive_risk_cap"
REASON_ACCOUNT_ID_PRESENT = "account_id_present"
REASON_CREDENTIALS_PRESENT = "credentials_present"
REASON_BROKER_WRITE_ENABLED = "broker_write_enabled"
REASON_ORDER_SUBMIT_ENABLED = "order_submit_enabled"
REASON_LIVE_TRADING_ENABLED = "live_trading_enabled"
REASON_NETWORK_SUBMIT_ENABLED = "network_submit_enabled"

REQUIRED_EVIDENCE = (
    "first_live_micro_trade_proof",
    "live_readiness_review",
    "paper_to_demo_promotion",
    "demo_multi_trade_runner",
    "demo_reconciliation",
    "session_replay",
    "risk_limits",
    "human_approval_record",
    "kill_switch_proof",
    "rollback_plan",
)


def evaluate_live_multi_trade_expansion_gate(
    first_live_micro_trade_proof: Any,
    live_readiness_review: Any,
    paper_to_demo_promotion: Any,
    demo_multi_trade_runner: Any,
    demo_reconciliation: Any,
    session_replay: Any,
    risk_limits: Any,
    human_approval_record: Any,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Review whether evidence can request future multi-trade expansion review."""

    proof = _as_mapping(first_live_micro_trade_proof)
    readiness = _as_mapping(live_readiness_review)
    promotion = _as_mapping(paper_to_demo_promotion)
    runner = _as_mapping(demo_multi_trade_runner)
    reconciliation = _as_mapping(demo_reconciliation)
    replay = _as_mapping(session_replay)
    limits = _as_mapping(risk_limits)
    approval = _as_mapping(human_approval_record)

    blocked_reasons: list[str] = []
    missing_evidence: list[str] = []

    if approval.get("approved") is not True:
        blocked_reasons.append(REASON_HUMAN_APPROVAL_MISSING)
        missing_evidence.append("human_approval_record")
    if proof.get("proof_complete") is not True:
        blocked_reasons.append(REASON_FIRST_LIVE_MICRO_PROOF_MISSING)
        missing_evidence.append("first_live_micro_trade_proof")
    if readiness.get("live_ready") is not True:
        blocked_reasons.append(REASON_LIVE_READINESS_REVIEW_MISSING)
        missing_evidence.append("live_readiness_review")
    if not _kill_switch_present(proof, readiness, limits, approval):
        blocked_reasons.append(REASON_KILL_SWITCH_MISSING)
        missing_evidence.append("kill_switch_proof")
    if not _rollback_present(proof, readiness, limits, approval):
        blocked_reasons.append(REASON_ROLLBACK_MISSING)
        missing_evidence.append("rollback_plan")

    reconciliation_ok = reconciliation.get("allowed") is True and (
        reconciliation.get("matched") is True or reconciliation.get("match_score") == 1.0
    )
    if not reconciliation_ok:
        blocked_reasons.append(REASON_RECONCILIATION_UNRESOLVED)
        missing_evidence.append("demo_reconciliation")

    if promotion.get("allowed") is not True:
        missing_evidence.append("paper_to_demo_promotion")
    if runner.get("allowed") is not True:
        missing_evidence.append("demo_multi_trade_runner")
    if not replay:
        missing_evidence.append("session_replay")
    if not limits:
        missing_evidence.append("risk_limits")

    max_live_trades_requested = _positive_int(
        limits.get("max_live_trades_requested", approval.get("max_live_trades_requested")),
        1,
    )
    max_live_trades_allowed_review_only = _positive_int(
        limits.get("max_live_trades_allowed_review_only"),
        1,
    )
    risk_cap = _positive_float(limits.get("risk_cap", limits.get("max_risk_pct")))
    max_risk_cap = _positive_float(limits.get("max_risk_cap", 1.0)) or 1.0
    drawdown = _drawdown(replay, limits, readiness, promotion)
    max_drawdown = _positive_float(limits.get("maximum_drawdown_pct", 5.0)) or 5.0
    risk_failures = _risk_failures(replay, limits, readiness, promotion)

    if max_live_trades_requested > max_live_trades_allowed_review_only:
        blocked_reasons.append(REASON_EXCESSIVE_LIVE_TRADE_COUNT)
    if risk_cap is None or risk_cap > max_risk_cap:
        blocked_reasons.append(REASON_EXCESSIVE_RISK_CAP)
    if drawdown > max_drawdown:
        blocked_reasons.append(REASON_DRAWDOWN_TOO_HIGH)
    if risk_failures:
        blocked_reasons.append(REASON_RISK_FAILURES_UNRESOLVED)

    for payload in (proof, readiness, promotion, runner, reconciliation, replay, limits, approval):
        blocked_reasons.extend(_runtime_blockers(payload))

    blocked_reasons = _ordered_blockers(blocked_reasons)
    missing_evidence = _dedupe(missing_evidence)
    expansion_ready = not blocked_reasons

    return {
        "allowed": expansion_ready,
        "decision": DECISION_REQUIRES_HUMAN_APPROVAL if expansion_ready else DECISION_REVIEW_ONLY,
        "expansion_ready": expansion_ready,
        "live_multi_trade_allowed": False,
        "broker_submit_allowed": False,
        "max_live_trades_requested": max_live_trades_requested,
        "max_live_trades_allowed_review_only": max_live_trades_allowed_review_only,
        "risk_cap": risk_cap,
        "kill_switch_required": True,
        "rollback_required": True,
        "required_evidence": list(REQUIRED_EVIDENCE),
        "missing_evidence": missing_evidence,
        "blocked_reason": REASON_NONE if expansion_ready else blocked_reasons[0],
        "blocked_reasons": [] if expansion_ready else blocked_reasons,
        "warnings": [],
        "mode": GATE_MODE,
        "safety": _safety_dict(),
        "next_safe_action": (
            "present_live_multi_trade_expansion_review_packet"
            if expansion_ready
            else "complete_live_multi_trade_expansion_evidence"
        ),
        "metadata": {
            "drawdown_pct": drawdown,
            "maximum_drawdown_pct": max_drawdown,
            "risk_failures": risk_failures,
            **dict(metadata or {}),
        },
    }


def _runtime_blockers(value: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key, nested in _walk(value):
        normalized = _normalize_key(key)
        if "account" in normalized and "id" in normalized and _present(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
        if "credential" in normalized and _present(nested):
            blockers.append(REASON_CREDENTIALS_PRESENT)
        if "broker" in normalized and "write" in normalized and _truthy(nested):
            blockers.append(REASON_BROKER_WRITE_ENABLED)
        if "order" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_ORDER_SUBMIT_ENABLED)
        if "live" in normalized and "trading" in normalized and _truthy(nested):
            blockers.append(REASON_LIVE_TRADING_ENABLED)
        if "network" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_NETWORK_SUBMIT_ENABLED)
        if isinstance(nested, str) and _looks_like_account_identifier(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
    return blockers


def _kill_switch_present(*payloads: Mapping[str, Any]) -> bool:
    return any(
        payload.get("kill_switch_proof") is True
        or payload.get("kill_switch_verified") is True
        for payload in payloads
    )


def _rollback_present(*payloads: Mapping[str, Any]) -> bool:
    return any(
        payload.get("rollback_plan") is True
        or payload.get("rollback_required") is True
        or payload.get("rollback_verified") is True
        for payload in payloads
    )


def _risk_failures(*payloads: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for payload in payloads:
        for key in ("risk_failures", "unresolved_risk_failures", "risk_blockers", "blocked_reasons"):
            value = payload.get(key)
            if isinstance(value, list):
                failures.extend(str(item) for item in value if str(item))
        if payload.get("risk_ok") is False or payload.get("risk_compliance_met") is False:
            failures.append("risk_compliance_false")
        if str(payload.get("risk_status", "")).lower() in {"failed", "blocked"}:
            failures.append(str(payload.get("risk_status")))
    return _dedupe(failures)


def _drawdown(*payloads: Mapping[str, Any]) -> float:
    for payload in payloads:
        for key in ("max_drawdown_pct", "drawdown_pct", "maximum_drawdown_pct"):
            value = payload.get(key)
            if value not in (None, ""):
                return _float(value, 0.0)
    return 0.0


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


def _positive_int(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _positive_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _float(value: Any, default: float) -> float:
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


def _ordered_blockers(items: list[str]) -> list[str]:
    priority = [
        REASON_HUMAN_APPROVAL_MISSING,
        REASON_FIRST_LIVE_MICRO_PROOF_MISSING,
        REASON_LIVE_READINESS_REVIEW_MISSING,
        REASON_KILL_SWITCH_MISSING,
        REASON_ROLLBACK_MISSING,
        REASON_RECONCILIATION_UNRESOLVED,
        REASON_DRAWDOWN_TOO_HIGH,
        REASON_RISK_FAILURES_UNRESOLVED,
        REASON_EXCESSIVE_LIVE_TRADE_COUNT,
        REASON_EXCESSIVE_RISK_CAP,
    ]
    unique = _dedupe(items)
    ordered = [reason for reason in priority if reason in unique]
    ordered.extend(reason for reason in unique if reason not in ordered)
    return ordered


def _safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "review_only": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
