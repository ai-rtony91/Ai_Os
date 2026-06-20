"""Protected first-live-micro-trade proof checklist for AIOS Forex."""

from __future__ import annotations

from typing import Any, Mapping


PROOF_MODE = "FIRST_LIVE_MICRO_TRADE_PROOF_ONLY"
DECISION_PROOF_ONLY = "PROOF_ONLY"
DECISION_REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"

REASON_NONE = "none"
REASON_HUMAN_APPROVAL_MISSING = "human_approval_missing"
REASON_KILL_SWITCH_MISSING = "kill_switch_missing"
REASON_ROLLBACK_MISSING = "rollback_missing"
REASON_RECONCILIATION_MISSING = "reconciliation_missing"
REASON_EXCESSIVE_RISK = "excessive_risk"
REASON_MISSING_EVIDENCE = "missing_evidence"
REASON_ACCOUNT_ID_PRESENT = "account_id_present"
REASON_CREDENTIALS_PRESENT = "credentials_present"
REASON_BROKER_WRITE_ENABLED = "broker_write_enabled"
REASON_ORDER_SUBMIT_ENABLED = "order_submit_enabled"
REASON_LIVE_TRADING_ENABLED = "live_trading_enabled"
REASON_NETWORK_SUBMIT_ENABLED = "network_submit_enabled"


REQUIRED_EVIDENCE = (
    "live_readiness_review",
    "paper_to_demo_promotion",
    "demo_multi_trade_runner",
    "demo_reconciliation",
    "risk_limits",
    "human_approval_record",
    "kill_switch_proof",
    "rollback_plan",
)


def build_first_live_micro_trade_proof(
    live_readiness_review: Any,
    paper_to_demo_promotion: Any,
    demo_multi_trade_runner: Any,
    demo_reconciliation: Any,
    risk_limits: Any,
    human_approval_record: Any,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-executing proof packet for future human live exception review."""

    readiness = _as_mapping(live_readiness_review)
    promotion = _as_mapping(paper_to_demo_promotion)
    runner = _as_mapping(demo_multi_trade_runner)
    reconciliation = _as_mapping(demo_reconciliation)
    limits = _as_mapping(risk_limits)
    approval = _as_mapping(human_approval_record)

    blocked_reasons: list[str] = []
    missing_evidence: list[str] = []

    if not readiness or readiness.get("live_ready") is not True:
        missing_evidence.append("live_readiness_review")
    if not promotion or promotion.get("allowed") is not True:
        missing_evidence.append("paper_to_demo_promotion")
    if not runner or runner.get("allowed") is not True:
        missing_evidence.append("demo_multi_trade_runner")
    if not reconciliation or reconciliation.get("allowed") is not True or (
        reconciliation.get("matched") is not True and reconciliation.get("match_score") != 1.0
    ):
        missing_evidence.append("demo_reconciliation")
        blocked_reasons.append(REASON_RECONCILIATION_MISSING)
    if not limits:
        missing_evidence.append("risk_limits")
    if not approval or approval.get("approved") is not True:
        missing_evidence.append("human_approval_record")
        blocked_reasons.append(REASON_HUMAN_APPROVAL_MISSING)
    if not _kill_switch_present(approval, readiness, limits):
        missing_evidence.append("kill_switch_proof")
        blocked_reasons.append(REASON_KILL_SWITCH_MISSING)
    if not _rollback_present(approval, readiness, limits):
        missing_evidence.append("rollback_plan")
        blocked_reasons.append(REASON_ROLLBACK_MISSING)

    micro_trade_size_cap = _positive_float(limits.get("micro_trade_size_cap"))
    max_allowed_cap = _positive_float(limits.get("max_micro_trade_size_cap", 1.0)) or 1.0
    max_risk_pct = _positive_float(limits.get("max_risk_pct", limits.get("maximum_risk_pct")))
    if micro_trade_size_cap is None or micro_trade_size_cap > max_allowed_cap:
        blocked_reasons.append(REASON_EXCESSIVE_RISK)
    if max_risk_pct is None or max_risk_pct > 1.0:
        blocked_reasons.append(REASON_EXCESSIVE_RISK)

    if missing_evidence:
        blocked_reasons.append(REASON_MISSING_EVIDENCE)

    for payload in (readiness, promotion, runner, reconciliation, limits, approval):
        blocked_reasons.extend(_runtime_blockers(payload))

    blocked_reasons = _dedupe(blocked_reasons)
    missing_evidence = _dedupe(missing_evidence)
    proof_complete = not blocked_reasons

    return {
        "allowed": False,
        "decision": DECISION_REQUIRES_HUMAN_APPROVAL if proof_complete else DECISION_PROOF_ONLY,
        "blocked_reason": REASON_NONE if proof_complete else blocked_reasons[0],
        "blocked_reasons": [] if proof_complete else blocked_reasons,
        "warnings": [],
        "mode": PROOF_MODE,
        "proof_complete": proof_complete,
        "live_trade_allowed": False,
        "broker_submit_allowed": False,
        "required_evidence": list(REQUIRED_EVIDENCE),
        "missing_evidence": missing_evidence,
        "risk_limits": {
            "micro_trade_size_cap": micro_trade_size_cap,
            "max_micro_trade_size_cap": max_allowed_cap,
            "max_risk_pct": max_risk_pct,
        },
        "micro_trade_size_cap": micro_trade_size_cap,
        "kill_switch_required": True,
        "rollback_required": True,
        "approval_required": True,
        "safety": _safety_dict(),
        "next_safe_action": (
            "present_proof_packet_for_human_review"
            if proof_complete
            else "complete_missing_live_micro_trade_proof_evidence"
        ),
        "metadata": dict(metadata or {}),
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
    for payload in payloads:
        if (
            payload.get("kill_switch_proof") is True
            or payload.get("kill_switch_ok") is True
            or payload.get("kill_switch_verified") is True
        ):
            return True
    return False


def _rollback_present(*payloads: Mapping[str, Any]) -> bool:
    for payload in payloads:
        if (
            payload.get("rollback_plan") is True
            or payload.get("rollback_required") is True
            or payload.get("rollback_verified") is True
        ):
            return True
    return False


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


def _positive_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


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


def _safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "proof_only": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
