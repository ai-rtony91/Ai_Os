"""Protected live-readiness review for AIOS Forex evidence."""

from __future__ import annotations

from typing import Any, Mapping


REVIEW_MODE = "LIVE_READINESS_REVIEW_ONLY"
DECISION_REVIEW_ONLY = "REVIEW_ONLY"
DECISION_REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"

REASON_NONE = "none"
REASON_HUMAN_APPROVAL_MISSING = "human_approval_missing"
REASON_PAPER_EVIDENCE_INSUFFICIENT = "paper_evidence_insufficient"
REASON_DEMO_EVIDENCE_INSUFFICIENT = "demo_evidence_insufficient"
REASON_RECONCILIATION_MISSING = "reconciliation_missing"
REASON_DRAWDOWN_TOO_HIGH = "drawdown_too_high"
REASON_RISK_FAILURES_UNRESOLVED = "risk_failures_unresolved"
REASON_KILL_SWITCH_PROOF_MISSING = "kill_switch_proof_missing"
REASON_ACCOUNT_ID_PRESENT = "account_id_present"
REASON_CREDENTIALS_PRESENT = "credentials_present"
REASON_LIVE_TRADING_ENABLED = "live_trading_enabled"
REASON_ORDER_SUBMIT_ENABLED = "order_submit_enabled"
REASON_BROKER_WRITE_ENABLED = "broker_write_enabled"
REASON_NETWORK_SUBMIT_ENABLED = "network_submit_enabled"


def review_live_readiness(
    paper_to_demo_promotion: Any,
    demo_multi_trade_runner: Any,
    demo_reconciliation: Any,
    session_replay: Any,
    evidence_ledger: Any,
    risk_metrics: Any,
    kill_switch_proof: Any,
    human_approval: bool = False,
    limits: Any = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Review whether evidence is mature enough to request a future live exception."""

    promotion = _as_mapping(paper_to_demo_promotion)
    runner = _as_mapping(demo_multi_trade_runner)
    reconciliation = _as_mapping(demo_reconciliation)
    replay = _as_mapping(session_replay)
    ledger = _as_mapping(evidence_ledger)
    risk = _as_mapping(risk_metrics)
    kill_switch = _as_mapping(kill_switch_proof)
    limit_cfg = _limits(limits)

    blocked_reasons: list[str] = []
    warnings: list[str] = []

    if human_approval is not True:
        blocked_reasons.append(REASON_HUMAN_APPROVAL_MISSING)

    paper_evidence_ok = _paper_evidence_ok(promotion, replay, ledger)
    demo_evidence_ok = runner.get("allowed") is True and runner.get("mode") == "DEMO_RUN_PLAN_ONLY"
    reconciliation_ok = reconciliation.get("allowed") is True and (
        reconciliation.get("matched") is True or reconciliation.get("match_score") == 1.0
    )
    drawdown = _drawdown(risk, replay, promotion)
    risk_failures = _risk_failures(risk, replay, promotion, ledger)
    risk_ok = drawdown <= limit_cfg["maximum_drawdown_pct"] and not risk_failures
    kill_switch_ok = _kill_switch_ok(kill_switch)

    if not paper_evidence_ok:
        blocked_reasons.append(REASON_PAPER_EVIDENCE_INSUFFICIENT)
    if not demo_evidence_ok:
        blocked_reasons.append(REASON_DEMO_EVIDENCE_INSUFFICIENT)
    if not reconciliation_ok:
        blocked_reasons.append(REASON_RECONCILIATION_MISSING)
    if drawdown > limit_cfg["maximum_drawdown_pct"]:
        blocked_reasons.append(REASON_DRAWDOWN_TOO_HIGH)
    if risk_failures:
        blocked_reasons.append(REASON_RISK_FAILURES_UNRESOLVED)
    if not kill_switch_ok:
        blocked_reasons.append(REASON_KILL_SWITCH_PROOF_MISSING)

    for payload in (promotion, runner, reconciliation, replay, ledger, risk, kill_switch):
        blocked_reasons.extend(_runtime_blockers(payload))

    blocked_reasons = _dedupe(blocked_reasons)
    readiness_score = _score(
        paper_evidence_ok,
        demo_evidence_ok,
        reconciliation_ok,
        risk_ok,
        kill_switch_ok,
    )
    live_ready = human_approval is True and not blocked_reasons

    return {
        "allowed": live_ready,
        "decision": DECISION_REQUIRES_HUMAN_APPROVAL if live_ready else DECISION_REVIEW_ONLY,
        "blocked_reason": REASON_NONE if live_ready else blocked_reasons[0],
        "blocked_reasons": [] if live_ready else blocked_reasons,
        "warnings": warnings,
        "mode": REVIEW_MODE,
        "live_ready": live_ready,
        "readiness_score": readiness_score,
        "paper_evidence_ok": paper_evidence_ok,
        "demo_evidence_ok": demo_evidence_ok,
        "reconciliation_ok": reconciliation_ok,
        "risk_ok": risk_ok,
        "kill_switch_ok": kill_switch_ok,
        "approval_required": True,
        "next_safe_action": (
            "request_human_live_micro_trade_exception_review"
            if live_ready
            else "continue_paper_demo_evidence_collection"
        ),
        "safety": _safety_dict(),
        "metadata": {
            "human_approval": bool(human_approval),
            "drawdown_pct": drawdown,
            "risk_failures": risk_failures,
            "limits": dict(limit_cfg),
            **dict(metadata or {}),
        },
    }


def _paper_evidence_ok(
    promotion: Mapping[str, Any],
    replay: Mapping[str, Any],
    ledger: Mapping[str, Any],
) -> bool:
    return (
        promotion.get("allowed") is True
        and promotion.get("demo_promotion_ready") is True
        and bool(replay)
        and bool(ledger)
        and ledger.get("validation_passed") is not False
    )


def _kill_switch_ok(proof: Mapping[str, Any]) -> bool:
    return (
        proof.get("present") is True
        or proof.get("kill_switch_ok") is True
        or proof.get("verified") is True
    ) and proof.get("disabled") is not True


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


def _runtime_blockers(value: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key, nested in _walk(value):
        normalized = _normalize_key(key)
        if "account" in normalized and "id" in normalized and _present(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
        if "credential" in normalized and _present(nested):
            blockers.append(REASON_CREDENTIALS_PRESENT)
        if "live" in normalized and "trading" in normalized and _truthy(nested):
            blockers.append(REASON_LIVE_TRADING_ENABLED)
        if "order" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_ORDER_SUBMIT_ENABLED)
        if "broker" in normalized and "write" in normalized and _truthy(nested):
            blockers.append(REASON_BROKER_WRITE_ENABLED)
        if "network" in normalized and "submit" in normalized and _truthy(nested):
            blockers.append(REASON_NETWORK_SUBMIT_ENABLED)
        if isinstance(nested, str) and _looks_like_account_identifier(nested):
            blockers.append(REASON_ACCOUNT_ID_PRESENT)
    return blockers


def _limits(value: Any) -> dict[str, float]:
    raw = _as_mapping(value)
    return {"maximum_drawdown_pct": _number(raw.get("maximum_drawdown_pct"), 5.0)}


def _drawdown(*payloads: Mapping[str, Any]) -> float:
    for payload in payloads:
        for key in ("max_drawdown_pct", "drawdown_pct", "maximum_drawdown_pct"):
            value = payload.get(key)
            if value not in (None, ""):
                return _number(value, 0.0)
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
        "review_only": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }
