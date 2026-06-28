"""Candidate selector for review-ready Forex remaining closure."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional

REVIEW_READY = "REVIEW_READY"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
REJECT_UNSAFE = "REJECT_UNSAFE"
REJECT_NEGATIVE_EXPECTANCY = "REJECT_NEGATIVE_EXPECTANCY"
REJECT_LOW_SAMPLE = "REJECT_LOW_SAMPLE"
EXTERNAL_EVIDENCE_REQUIRED = "EXTERNAL_EVIDENCE_REQUIRED"
REJECT_LOW_PROFIT_FACTOR = "REJECT_LOW_PROFIT_FACTOR"
REJECT_HIGH_DRAWDOWN = "REJECT_HIGH_DRAWDOWN"


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


def score_candidate(candidate: Mapping[str, Any]) -> int:
    completeness = max(0.0, min(1.0, _coerce_float(candidate.get("evidence_completeness", 0.5), 0.5)))
    sample_size = _coerce_int(candidate.get("sample_count", candidate.get("sample_size", 0)))
    sample_score = min(1.0, max(0.0, sample_size / 120.0))
    expectancy = _coerce_float(candidate.get("expectancy", 0.0))
    profit_factor = _coerce_float(candidate.get("profit_factor", 1.0))
    drawdown = max(0.0, _coerce_float(candidate.get("drawdown", candidate.get("max_drawdown", 0.0))))
    risk_score = max(0.0, min(1.0, _coerce_float(candidate.get("risk_control_score", 0.5), 0.5)))
    audit_score = max(0.0, min(1.0, _coerce_float(candidate.get("auditability", candidate.get("auditability_score", 0.5)), 0.5)))
    broker_ready = 1.0 if bool(candidate.get("broker_evidence_ready", False)) else 0.0
    owner_ok = 1.0 if bool(candidate.get("owner_approval_ready", True)) else 0.0
    expectancy_component = (expectancy + 2.0) / 4.0
    drawdown_component = max(0.0, min(1.0, (0.35 - drawdown) / 0.35))
    raw = (
        completeness * 16.0
        + sample_score * 14.0
        + expectancy_component * 18.0
        + min(profit_factor, 4.0) / 4.0 * 16.0
        + drawdown_component * 14.0
        + risk_score * 12.0
        + audit_score * 8.0
        + broker_ready * 2.0
        + owner_ok * 0.0
    )
    return round(raw)


def explain_candidate_decision(candidate: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    sample_size = _coerce_int(candidate.get("sample_count", candidate.get("sample_size", 0)))
    drawdown = _coerce_float(candidate.get("drawdown", candidate.get("max_drawdown", 0.0)))
    expectancy = _coerce_float(candidate.get("expectancy", 0.0))
    profit_factor = _coerce_float(candidate.get("profit_factor", 1.0))

    if bool(candidate.get("unsafe")) or bool(candidate.get("safety_blocked")):
        return {
            "route": REJECT_UNSAFE,
            "score": score_candidate(candidate),
                       "reasons": ["candidate flagged as unsafe"],
            "decision_timestamp": _safe_time(),
        }
    if candidate.get("external_blocker", False):
        return {
            "route": EXTERNAL_EVIDENCE_REQUIRED,
            "score": score_candidate(candidate),
            "reasons": ["external evidence blocker flagged"],
            "decision_timestamp": _safe_time(),
        }
    if candidate.get("owner_approval_required", False):
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "reasons": ["owner approval evidence missing"],
            "decision_timestamp": _safe_time(),
        }
    if expectancy < 0:
        reasons.append("negative expectancy")
        return {
            "route": REJECT_NEGATIVE_EXPECTANCY,
            "score": score_candidate(candidate),
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if sample_size < 30:
        reasons.append("sample too small")
        return {
            "route": REJECT_LOW_SAMPLE,
            "score": score_candidate(candidate),
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if drawdown > 0.30:
        reasons.append("high drawdown")
        return {
            "route": REJECT_HIGH_DRAWDOWN,
            "score": score_candidate(candidate),
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if profit_factor < 1.2:
        reasons.append("profit factor too low")
        return {
            "route": REJECT_LOW_PROFIT_FACTOR,
            "score": score_candidate(candidate),
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if _coerce_float(candidate.get("evidence_completeness", 0.0)) < 0.70:
        reasons.append("incomplete evidence")
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    if score_candidate(candidate) < 64:
        reasons.append("overall readiness score below threshold")
        return {
            "route": NEEDS_MORE_EVIDENCE,
            "score": score_candidate(candidate),
            "reasons": reasons,
            "decision_timestamp": _safe_time(),
        }
    return {
        "route": REVIEW_READY,
        "score": score_candidate(candidate),
        "reasons": ["candidate passes readiness filters"],
        "decision_timestamp": _safe_time(),
    }


def select_review_ready_candidate(
    candidate_summaries: Iterable[Mapping[str, Any]],
    *,
    strict: bool = False,
) -> dict[str, Any]:
    candidates = list(candidate_summaries)
    decisions = []
    selected: Optional[Mapping[str, Any]] = None
    route_counts: dict[str, int] = {}
    for candidate in candidates:
        decision = explain_candidate_decision(candidate)
        decision["candidate_id"] = candidate.get("candidate_id", candidate.get("name"))
        decision["candidate"] = dict(candidate)
        decisions.append(decision)
        route_counts[decision["route"]] = route_counts.get(decision["route"], 0) + 1
    ready = [entry for entry in decisions if entry["route"] == REVIEW_READY]
    if ready:
        selected = ready[0]["candidate"]
        final_route = REVIEW_READY
    else:
        if strict:
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
    if final_route != REVIEW_READY and strict and selected is None:
        selected = candidates[0] if candidates else None
    return {
        "selector_version": "1.0",
        "generated_at": _safe_time(),
        "route": final_route,
        "selected_candidate": selected,
        "scores": [entry["score"] for entry in decisions],
        "route_counts": route_counts,
        "candidate_decisions": decisions,
    }


def candidate_selector_to_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Review-Ready Candidate Selector V1",
        f"Generated: {result.get('generated_at')}",
        f"Route: {result.get('route')}",
        f"Selected candidate: {result.get('selected_candidate', {}).get('candidate_id') if result.get('selected_candidate') else 'none'}",
        "",
    ]
    for entry in result.get("candidate_decisions", []):
        lines.append(f"- {entry.get('candidate_id')} -> {entry.get('route')} (score {entry.get('score')})")
        lines.append(f"  - reasons: {', '.join(entry.get('reasons', []))}")
    return "\n".join(lines)


def candidate_selector_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "selector_version": result.get("selector_version"),
        "generated_at": result.get("generated_at"),
        "route": result.get("route"),
        "selected_candidate": dict(result.get("selected_candidate") or {}),
        "scores": list(result.get("scores", [])),
        "route_counts": dict(result.get("route_counts", {})),
        "candidate_decisions": list(result.get("candidate_decisions", [])),
    }


__all__ = [
    "REVIEW_READY",
    "NEEDS_MORE_EVIDENCE",
    "REJECT_UNSAFE",
    "REJECT_NEGATIVE_EXPECTANCENCY",
    "REJECT_LOW_SAMPLE",
    "REJECT_LOW_PROFIT_FACTOR",
    "REJECT_HIGH_DRAWDOWN",
    "EXTERNAL_EVIDENCE_REQUIRED",
    "score_candidate",
    "explain_candidate_decision",
    "select_review_ready_candidate",
    "candidate_selector_to_markdown",
    "candidate_selector_to_jsonable_dict",
]
