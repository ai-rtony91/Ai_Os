"""Candidate selector for review-ready Forex remaining closure."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

REVIEW_READY = "REVIEW_READY"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
REJECT_UNSAFE = "REJECT_UNSAFE"
REJECT_NEGATIVE_EXPECTANCY = "REJECT_NEGATIVE_EXPECTANCY"
REJECT_LOW_SAMPLE = "REJECT_LOW_SAMPLE"
EXTERNAL_EVIDENCE_REQUIRED = "EXTERNAL_EVIDENCE_REQUIRED"
REJECT_LOW_PROFIT_FACTOR = "REJECT_LOW_PROFIT_FACTOR"
REJECT_HIGH_DRAWDOWN = "REJECT_HIGH_DRAWDOWN"
SELECTOR_VERSION = "1.0"
REJECT_NEGATIVE_EXPECTANCENCY = REJECT_NEGATIVE_EXPECTANCY

BLOCKED_ACTIONS = (
    "broker_api_access",
    "credential_access",
    "account_access",
    "trade_action",
    "live_trade",
    "demo_trade",
    "paper_trade",
    "production_activation",
    "order_placement",
    "money_movement",
)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _safe_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return str(
        candidate.get("candidate_id")
        or candidate.get("id")
        or candidate.get("name")
        or "unknown-candidate",
    )


def _normalized_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(candidate)
    normalized["candidate_id"] = _candidate_id(candidate)
    normalized["strategy"] = candidate.get("strategy") or candidate.get("strategy_id")
    normalized["symbol"] = candidate.get("symbol") or candidate.get("instrument")
    if "sample_size" not in normalized and "sample_count" in candidate:
        normalized["sample_size"] = candidate.get("sample_count")
    if "evidence_depth_score" not in normalized and "evidence_completeness" in candidate:
        normalized["evidence_depth_score"] = candidate.get("evidence_completeness")
    if "risk_score" not in normalized and "risk_control_score" in candidate:
        normalized["risk_score"] = candidate.get("risk_control_score")
    return normalized


def _field_value(candidate: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in candidate:
            return candidate.get(name)
    return default


def _is_ready_alias(candidate: Mapping[str, Any]) -> bool:
    values = [
        candidate.get("status"),
        candidate.get("readiness_status"),
        candidate.get("gate_status"),
    ]
    ready_tokens = {
        "READY",
        "READY_FOR_REVIEW",
        "REVIEW_READY",
        "PASSED",
        "PASS",
        "GATE_PASSED",
    }
    return any(str(value).upper() in ready_tokens for value in values if value is not None)


def score_candidate(candidate: Mapping[str, Any]) -> int:
    normalized = _normalized_candidate(candidate)
    completeness = max(
        0.0,
        min(
            1.0,
            _coerce_float(
                _field_value(normalized, "evidence_depth_score", "evidence_completeness", default=0.5),
                0.5,
            ),
        ),
    )
    sample_size = _coerce_int(candidate.get("sample_count", candidate.get("sample_size", 0)))
    sample_score = min(1.0, max(0.0, sample_size / 120.0))
    expectancy = _coerce_float(candidate.get("expectancy", 0.0))
    profit_factor = _coerce_float(candidate.get("profit_factor", 1.0))
    drawdown = max(0.0, _coerce_float(candidate.get("drawdown", candidate.get("max_drawdown", 0.0))))
    risk_score = max(
        0.0,
        min(1.0, _coerce_float(_field_value(normalized, "risk_score", "risk_control_score", default=0.5), 0.5)),
    )
    statistical_profit_score = max(
        0.0,
        min(1.0, _coerce_float(candidate.get("statistical_profit_score", 0.5), 0.5)),
    )
    recency_score = max(0.0, min(1.0, _coerce_float(candidate.get("recency_score", 0.5), 0.5)))
    audit_score = max(0.0, min(1.0, _coerce_float(candidate.get("auditability", candidate.get("auditability_score", 0.5)), 0.5)))
    broker_ready = 1.0 if bool(candidate.get("broker_evidence_ready", False)) else 0.0
    owner_ok = 1.0 if bool(candidate.get("owner_approval_ready", True)) else 0.0
    expectancy_component = (expectancy + 2.0) / 4.0
    drawdown_component = max(0.0, min(1.0, (0.35 - drawdown) / 0.35))
    raw = (
        completeness * 22.0
        + statistical_profit_score * 20.0
        + sample_score * 12.0
        + expectancy_component * 12.0
        + min(profit_factor, 4.0) / 4.0 * 10.0
        + drawdown_component * 8.0
        + risk_score * 8.0
        + recency_score * 4.0
        + audit_score * 3.0
        + broker_ready * 1.0
        + owner_ok * 0.0
    )
    return round(raw)


def explain_candidate_decision(candidate: Mapping[str, Any], *, min_score: float = 60.0) -> dict[str, Any]:
    candidate = _normalized_candidate(candidate)
    candidate_id = _candidate_id(candidate)
    reasons: list[str] = []
    sample_raw = _field_value(candidate, "sample_size", "sample_count")
    evidence_raw = _field_value(candidate, "evidence_depth_score", "evidence_completeness")
    sample_size = _coerce_int(sample_raw)
    drawdown = _coerce_float(candidate.get("drawdown", candidate.get("max_drawdown", 0.0)))
    expectancy = _coerce_float(candidate.get("expectancy", 0.0))
    profit_factor = _coerce_float(candidate.get("profit_factor", 1.0))
    status_values = " ".join(
        str(candidate.get(name, ""))
        for name in ("status", "readiness_status", "gate_status")
    ).upper()

    if bool(candidate.get("blocked")):
        reasons.append("candidate is explicitly blocked")
        return {
            "route": REJECT_UNSAFE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    blocked_reasons = list(candidate.get("blocked_reasons") or [])
    if blocked_reasons:
        reasons.extend([f"candidate blocked: {reason}" for reason in blocked_reasons])
        return {
            "route": REJECT_UNSAFE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if any(token in status_values for token in ("REJECT", "BLOCK", "FAIL", "NOT_READY")):
        reasons.append("candidate status is not review ready")
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if bool(candidate.get("unsafe")) or bool(candidate.get("safety_blocked")):
        return {
            "route": REJECT_UNSAFE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": ["candidate flagged as unsafe"],
            "decision_timestamp": _safe_time(),
        }
    if candidate.get("external_blocker", False):
        return {
            "route": EXTERNAL_EVIDENCE_REQUIRED,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": ["external evidence blocker flagged"],
            "decision_timestamp": _safe_time(),
        }
    if candidate.get("owner_approval_required", False):
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": ["owner approval evidence missing"],
            "decision_timestamp": _safe_time(),
        }
    if sample_raw is None:
        return {
            "route": REJECT_LOW_SAMPLE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": ["sample_size is missing"],
            "decision_timestamp": _safe_time(),
        }
    if evidence_raw is None:
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": ["evidence_depth_score is missing"],
            "decision_timestamp": _safe_time(),
        }
    if candidate.get("review_ready") is False and not _is_ready_alias(candidate):
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": ["review_ready flag is false"],
            "decision_timestamp": _safe_time(),
        }
    if expectancy < 0:
        reasons.append("negative expectancy")
        return {
            "route": REJECT_NEGATIVE_EXPECTANCY,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if sample_size < 30:
        reasons.append("sample too small")
        return {
            "route": REJECT_LOW_SAMPLE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if drawdown > 0.30:
        reasons.append("high drawdown")
        return {
            "route": REJECT_HIGH_DRAWDOWN,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if profit_factor < 1.2:
        reasons.append("profit factor too low")
        return {
            "route": REJECT_LOW_PROFIT_FACTOR,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if _coerce_float(evidence_raw) < 0.70:
        reasons.append("incomplete evidence")
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if score_candidate(candidate) < min_score:
        reasons.append("total_score below min_score")
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "total_score": score_candidate(candidate),
            "candidate_id": candidate_id,
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    return {
        "route": REVIEW_READY,
        "score": score_candidate(candidate),
        "total_score": score_candidate(candidate),
        "candidate_id": candidate_id,
        "reasons": ["candidate passes readiness filters"],
        "decision_timestamp": _safe_time(),
    }


def select_review_ready_candidate(
    candidate_summaries: Iterable[Mapping[str, Any]] | None,
    *,
    strict: bool = False,
    min_score: float = 60.0,
) -> dict[str, Any]:
    if candidate_summaries is None:
        return _empty_selection({"input": ["candidate list is missing"]}, route=NEEDS_MORE_EVIDENCE)
    candidates = [dict(candidate) for candidate in candidate_summaries if isinstance(candidate, Mapping)]
    if not candidates and list(candidate_summaries or []) != candidates:
        return _empty_selection({"input": ["candidate list contains no valid records"]}, route=NEEDS_MORE_EVIDENCE)
    decisions: list[dict[str, Any]] = []
    route_counts: dict[str, int] = {}
    for candidate in candidates:
        normalized = _normalized_candidate(candidate)
        decision = explain_candidate_decision(normalized, min_score=min_score)
        decision["candidate_id"] = _candidate_id(normalized)
        decision["candidate"] = normalized
        decisions.append(decision)
        route_counts[decision["route"]] = route_counts.get(decision["route"], 0) + 1
    ready = sorted(
        [entry for entry in decisions if entry["route"] == REVIEW_READY],
        key=lambda entry: (-int(entry["total_score"]), str(entry["candidate_id"])),
    )
    if ready:
        selected = dict(ready[0]["candidate"])
        final_route = REVIEW_READY
    else:
        selected = None
        if not decisions:
            final_route = NEEDS_MORE_EVIDENCE
        elif strict:
            final_route = NEEDS_MORE_EVIDENCE
        elif any(dec["route"] == REJECT_UNSAFE for dec in decisions):
            final_route = REJECT_UNSAFE
        elif any(dec["route"] == EXTERNAL_EVIDENCE_REQUIRED for dec in decisions):
            final_route = EXTERNAL_EVIDENCE_REQUIRED
        elif any(dec["route"] == REJECT_NEGATIVE_EXPECTANCY for dec in decisions):
            final_route = REJECT_NEGATIVE_EXPECTANCY
        elif any(dec["route"] == REJECT_LOW_SAMPLE for dec in decisions):
            final_route = REJECT_LOW_SAMPLE
        elif any(dec["route"] == REJECT_HIGH_DRAWDOWN for dec in decisions):
            final_route = REJECT_HIGH_DRAWDOWN
        elif any(dec["route"] == REJECT_LOW_PROFIT_FACTOR for dec in decisions):
            final_route = REJECT_LOW_PROFIT_FACTOR
        else:
            final_route = NEEDS_MORE_EVIDENCE
    ranking = [
        {
            "candidate_id": entry["candidate_id"],
            "total_score": entry["total_score"],
            "route": entry["route"],
        }
        for entry in ready
    ]
    rejection_reasons = {
        str(entry["candidate_id"]): list(entry.get("reasons", []))
        for entry in decisions
        if entry["route"] != REVIEW_READY
    }
    return {
        "selector_version": SELECTOR_VERSION,
        "generated_at": _safe_time(),
        "route": final_route,
        "selected": selected is not None,
        "selected_candidate_id": selected.get("candidate_id") if selected else None,
        "selected_candidate": selected,
        "ranking": ranking,
        "eligible_count": len(ranking),
        "rejection_reasons": rejection_reasons,
        "scores": [entry["score"] for entry in decisions],
        "route_counts": route_counts,
        "candidate_decisions": decisions,
        **_blocked_boundary_fields(),
    }


def _blocked_boundary_fields() -> dict[str, Any]:
    return {
        "blocked_actions": list(BLOCKED_ACTIONS),
        "execution_allowed": False,
        "broker_access_allowed": False,
        "credential_access_allowed": False,
        "account_access_allowed": False,
        "trade_action_allowed": False,
        "live_trade_allowed": False,
        "demo_trade_allowed": False,
        "paper_trade_allowed": False,
        "production_activation_allowed": False,
    }


def _empty_selection(rejection_reasons: Mapping[str, list[str]], *, route: str) -> dict[str, Any]:
    return {
        "selector_version": SELECTOR_VERSION,
        "generated_at": _safe_time(),
        "route": route,
        "selected": False,
        "selected_candidate_id": None,
        "selected_candidate": None,
        "ranking": [],
        "eligible_count": 0,
        "rejection_reasons": dict(rejection_reasons),
        "scores": [],
        "route_counts": {},
        "candidate_decisions": [],
        **_blocked_boundary_fields(),
    }


def candidate_selector_to_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Review-Ready Candidate Selector V1",
        f"Generated: {result.get('generated_at')}",
        f"Route: {result.get('route')}",
        f"Selected candidate: {result.get('selected_candidate_id') or 'none'}",
        "",
    ]
    for entry in result.get("candidate_decisions", []):
        lines.append(f"- {entry.get('candidate_id')} -> {entry.get('route')} (score {entry.get('score')})")
        lines.append(f"  - reasons: {', '.join(entry.get('reasons', []))}")
    return "\n".join(lines)


def candidate_selector_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "selector_version": result.get("selector_version", SELECTOR_VERSION),
        "generated_at": result.get("generated_at"),
        "route": result.get("route"),
        "selected": bool(result.get("selected", False)),
        "selected_candidate_id": result.get("selected_candidate_id"),
        "selected_candidate": dict(result.get("selected_candidate") or {}),
        "ranking": list(result.get("ranking", [])),
        "eligible_count": int(result.get("eligible_count", 0)),
        "rejection_reasons": dict(result.get("rejection_reasons", {})),
        "scores": list(result.get("scores", [])),
        "route_counts": dict(result.get("route_counts", {})),
        "candidate_decisions": list(result.get("candidate_decisions", [])),
        "blocked_actions": list(result.get("blocked_actions", BLOCKED_ACTIONS)),
        "execution_allowed": bool(result.get("execution_allowed", False)),
        "broker_access_allowed": bool(result.get("broker_access_allowed", False)),
        "credential_access_allowed": bool(result.get("credential_access_allowed", False)),
        "account_access_allowed": bool(result.get("account_access_allowed", False)),
        "trade_action_allowed": bool(result.get("trade_action_allowed", False)),
        "live_trade_allowed": bool(result.get("live_trade_allowed", False)),
        "demo_trade_allowed": bool(result.get("demo_trade_allowed", False)),
        "paper_trade_allowed": bool(result.get("paper_trade_allowed", False)),
        "production_activation_allowed": bool(result.get("production_activation_allowed", False)),
    }


__all__ = [
    "REVIEW_READY",
    "SELECTOR_VERSION",
    "NEEDS_MORE_EVIDENCE",
    "REJECT_UNSAFE",
    "REJECT_NEGATIVE_EXPECTANCENCY",
    "REJECT_NEGATIVE_EXPECTANCY",
    "REJECT_LOW_SAMPLE",
    "REJECT_LOW_PROFIT_FACTOR",
    "REJECT_HIGH_DRAWDOWN",
    "EXTERNAL_EVIDENCE_REQUIRED",
    "BLOCKED_ACTIONS",
    "score_candidate",
    "explain_candidate_decision",
    "select_review_ready_candidate",
    "candidate_selector_to_markdown",
    "candidate_selector_to_jsonable_dict",
]
