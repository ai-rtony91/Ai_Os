"""Pure local Review-Ready Candidate Selector V1 for AIOS Forex.

The selector accepts candidate dictionaries, filters review-ready evidence,
scores eligible candidates deterministically, and returns a safe review result.
It does not import external execution modules, read or write files, start
automation, or authorize any trade action.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


SELECTOR_VERSION = "forex_review_ready_candidate_selector_v1"

REVIEW_READY_STATUSES = frozenset(
    ("REVIEW_READY", "READY_FOR_REVIEW", "REVIEW_READY_CANDIDATE")
)
BLOCKED_STATUS_FRAGMENTS = frozenset(
    ("REJECT", "BLOCKED", "FAIL", "FAILED", "NOT_READY")
)

BLOCKED_ACTIONS = (
    "broker_access",
    "credential_access",
    "account_access",
    "live_trade",
    "demo_trade",
    "paper_trade",
    "order_placement",
    "order_closure",
    "production_activation",
)

UNSAFE_TRUE_FIELDS = (
    "broker_access_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "live_trade_allowed",
    "demo_trade_allowed",
    "paper_trade_allowed",
    "order_placement_allowed",
    "order_closure_allowed",
    "production_activation_allowed",
    "execution_allowed",
    "trade_action_allowed",
)

TIE_BREAKERS = (
    "higher total_score",
    "higher evidence_depth_score",
    "higher statistical_profit_score",
    "higher profit_factor",
    "higher expectancy",
    "lower max_drawdown",
    "higher sample_size",
    "lexicographically smallest candidate_id",
)

NO_SELECTION_NEXT_SAFE_ACTION = (
    "Repair candidate evidence and rerun this local selector before any "
    "separate owner-gated demo trade review."
)
SELECTION_NEXT_SAFE_ACTION = (
    "Prepare an operator review packet for the selected review-ready "
    "candidate; do not place or route any trade."
)


def select_review_ready_candidate(
    candidates: list[dict], *, min_score: float = 0.0
) -> dict:
    """Select the best review-ready candidate from local candidate dictionaries.

    Invalid candidate lists return a no-selection result instead of raising.
    Candidate ranking is deterministic. Ties are resolved in this order:
    higher total score, higher evidence depth, higher statistical profit,
    higher profit factor, higher expectancy, lower max drawdown, higher sample
    size, then lexicographically smallest candidate ID.
    """

    threshold = _number_or_default(min_score, Decimal("0"))
    if threshold < Decimal("0"):
        threshold = Decimal("0")

    if not isinstance(candidates, list):
        return _result(
            selected_candidate=None,
            ranking=[],
            rejection_reasons={
                "input": ["candidates must be provided as a list of dictionaries"]
            },
            input_count=0,
            min_score=threshold,
        )

    eligible_records: list[dict[str, Any]] = []
    rejection_reasons: dict[str, list[str]] = {}

    for index, raw_candidate in enumerate(candidates):
        if not isinstance(raw_candidate, dict):
            candidate_id = f"candidate-{index:06d}"
            rejection_reasons[candidate_id] = ["candidate is not a dictionary"]
            continue

        candidate = _normalize_candidate(raw_candidate, index)
        reasons = _rejection_reasons(candidate)
        if reasons:
            rejection_reasons[candidate["candidate_id"]] = reasons
            continue

        scored = _score_candidate(candidate)
        scored["threshold_passed"] = scored["total_score_decimal"] >= threshold
        eligible_records.append(scored)

    ranking_records = sorted(eligible_records, key=_ranking_key)
    ranking = [_ranking_entry(record, rank) for rank, record in enumerate(ranking_records, 1)]

    selected_candidate = ranking_records[0] if ranking_records else None
    if selected_candidate is not None and selected_candidate["total_score_decimal"] < threshold:
        for record in ranking_records:
            rejection_reasons.setdefault(record["candidate_id"], []).append(
                f"total_score below min_score {float(threshold):.6f}"
            )
        selected_candidate = None

    return _result(
        selected_candidate=selected_candidate,
        ranking=ranking,
        rejection_reasons=rejection_reasons,
        input_count=len(candidates),
        min_score=threshold,
    )


def _normalize_candidate(candidate: Mapping[str, Any], index: int) -> dict[str, Any]:
    candidate_id = _text(_first(candidate, "candidate_id", "id"))
    if not candidate_id:
        candidate_id = f"candidate-{index:06d}"

    blocked_reasons = _reason_list(_first(candidate, "blocked_reasons", "blockers"))
    proof_flags = _mapping_or_empty(candidate.get("proof_flags"))
    metadata = _mapping_or_empty(candidate.get("metadata"))

    return {
        "candidate_id": candidate_id,
        "strategy": _text(_first(candidate, "strategy", "strategy_id")),
        "symbol": _text(_first(candidate, "symbol", "instrument")),
        "direction": _text(candidate.get("direction")),
        "review_ready": _truthy(candidate.get("review_ready")),
        "status": _text(candidate.get("status")),
        "gate_status": _text(candidate.get("gate_status")),
        "readiness_status": _text(candidate.get("readiness_status")),
        "evidence_depth_score": _decimal_or_none(
            candidate.get("evidence_depth_score")
        ),
        "statistical_profit_score": _decimal_or_none(
            candidate.get("statistical_profit_score")
        ),
        "profit_factor": _decimal_or_none(candidate.get("profit_factor")),
        "expectancy": _decimal_or_none(candidate.get("expectancy")),
        "max_drawdown": _decimal_or_none(candidate.get("max_drawdown")),
        "drawdown_score": _decimal_or_none(candidate.get("drawdown_score")),
        "sample_size": _decimal_or_none(candidate.get("sample_size")),
        "risk_score": _decimal_or_none(candidate.get("risk_score")),
        "recency_score": _decimal_or_none(candidate.get("recency_score")),
        "blocked": _truthy(candidate.get("blocked")),
        "unsafe": _truthy(candidate.get("unsafe")),
        "blocked_reasons": blocked_reasons,
        "proof_flags": proof_flags,
        "metadata": metadata,
        "input_index": index,
    }


def _rejection_reasons(candidate: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []

    if not _is_review_ready(candidate):
        reasons.append("candidate is not review-ready")
    if candidate["blocked"]:
        reasons.append("candidate is explicitly blocked")
    if candidate["unsafe"]:
        reasons.append("candidate is marked unsafe")
    if candidate["blocked_reasons"]:
        reasons.extend(
            f"blocked reason: {reason}" for reason in candidate["blocked_reasons"]
        )
    blocked_statuses = _blocked_statuses(candidate)
    if blocked_statuses:
        reasons.extend(
            f"gate/readiness status blocks review: {status}"
            for status in blocked_statuses
        )

    sample_size = candidate["sample_size"]
    if sample_size is None:
        reasons.append("sample_size is missing")
    elif sample_size <= Decimal("0"):
        reasons.append("sample_size must be greater than zero")

    evidence_depth_score = candidate["evidence_depth_score"]
    if evidence_depth_score is None:
        reasons.append("evidence_depth_score is missing")
    elif evidence_depth_score <= Decimal("0"):
        reasons.append("evidence_depth_score must be greater than zero")

    unsafe_flags = _unsafe_true_flags(candidate)
    if unsafe_flags:
        reasons.extend(f"unsafe proof flag true: {flag}" for flag in unsafe_flags)

    return reasons


def _is_review_ready(candidate: Mapping[str, Any]) -> bool:
    if candidate["review_ready"]:
        return True
    return _canonical_status(candidate["status"]) in REVIEW_READY_STATUSES


def _contains_blocked_status(status: str) -> bool:
    canonical = _canonical_status(status)
    return any(fragment in canonical for fragment in BLOCKED_STATUS_FRAGMENTS)


def _blocked_statuses(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        status
        for status in (candidate["gate_status"], candidate["readiness_status"])
        if status and _contains_blocked_status(status)
    )


def _score_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    statistical_profit = candidate["statistical_profit_score"] or Decimal("0")
    evidence_depth = candidate["evidence_depth_score"] or Decimal("0")
    profit_factor = candidate["profit_factor"] or Decimal("0")
    expectancy = candidate["expectancy"] or Decimal("0")
    sample_size = candidate["sample_size"] or Decimal("0")
    risk_score = candidate["risk_score"] or Decimal("0")
    recency_score = candidate["recency_score"] or Decimal("0")
    drawdown_score = candidate["drawdown_score"] or Decimal("0")
    max_drawdown = candidate["max_drawdown"] or Decimal("0")

    components = {
        "statistical_profit_score": statistical_profit * Decimal("5.0"),
        "evidence_depth_score": evidence_depth * Decimal("4.0"),
        "profit_factor": profit_factor * Decimal("3.0"),
        "expectancy": expectancy * Decimal("3.0"),
        "sample_size": sample_size * Decimal("0.10"),
        "risk_score": risk_score * Decimal("2.0"),
        "recency_score": recency_score,
        "drawdown_score": drawdown_score,
        "max_drawdown_penalty": max_drawdown * Decimal("2.0"),
    }
    total_score = (
        components["statistical_profit_score"]
        + components["evidence_depth_score"]
        + components["profit_factor"]
        + components["expectancy"]
        + components["sample_size"]
        + components["risk_score"]
        + components["recency_score"]
        + components["drawdown_score"]
        - components["max_drawdown_penalty"]
    )

    scored = dict(candidate)
    scored["score_components"] = {
        key: _decimal_float(value) for key, value in components.items()
    }
    scored["total_score_decimal"] = total_score
    scored["total_score"] = _decimal_float(total_score)
    scored["selection_reasons"] = _selection_reasons(scored)
    return scored


def _ranking_key(record: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        -record["total_score_decimal"],
        -(record["evidence_depth_score"] or Decimal("0")),
        -(record["statistical_profit_score"] or Decimal("0")),
        -(record["profit_factor"] or Decimal("0")),
        -(record["expectancy"] or Decimal("0")),
        record["max_drawdown"] or Decimal("0"),
        -(record["sample_size"] or Decimal("0")),
        record["candidate_id"],
    )


def _ranking_entry(record: Mapping[str, Any], rank: int) -> dict[str, Any]:
    return {
        "rank": rank,
        "candidate_id": record["candidate_id"],
        "strategy": record["strategy"],
        "symbol": record["symbol"],
        "direction": record["direction"],
        "total_score": record["total_score"],
        "threshold_passed": record["threshold_passed"],
        "evidence_depth_score": _decimal_float(record["evidence_depth_score"]),
        "statistical_profit_score": _decimal_float(record["statistical_profit_score"]),
        "profit_factor": _decimal_float(record["profit_factor"]),
        "expectancy": _decimal_float(record["expectancy"]),
        "max_drawdown": _decimal_float(record["max_drawdown"]),
        "sample_size": _decimal_float(record["sample_size"]),
        "risk_score": _decimal_float(record["risk_score"]),
        "recency_score": _decimal_float(record["recency_score"]),
        "selection_reasons": list(record["selection_reasons"]),
    }


def _selected_candidate_payload(record: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if record is None:
        return None
    return {
        "candidate_id": record["candidate_id"],
        "strategy": record["strategy"],
        "symbol": record["symbol"],
        "direction": record["direction"],
        "total_score": record["total_score"],
        "evidence_depth_score": _decimal_float(record["evidence_depth_score"]),
        "statistical_profit_score": _decimal_float(record["statistical_profit_score"]),
        "profit_factor": _decimal_float(record["profit_factor"]),
        "expectancy": _decimal_float(record["expectancy"]),
        "max_drawdown": _decimal_float(record["max_drawdown"]),
        "sample_size": _decimal_float(record["sample_size"]),
        "risk_score": _decimal_float(record["risk_score"]),
        "recency_score": _decimal_float(record["recency_score"]),
        "proof_flags": _json_safe(record["proof_flags"]),
        "metadata": _json_safe(record["metadata"]),
        "score_components": dict(record["score_components"]),
        "selection_reasons": list(record["selection_reasons"]),
    }


def _selection_reasons(record: Mapping[str, Any]) -> list[str]:
    return [
        "candidate passed review-ready eligibility checks",
        f"total_score {record['total_score']:.6f}",
        "ranking uses deterministic tie-breakers: " + ", ".join(TIE_BREAKERS),
        "result is review selection only and authorizes no execution",
    ]


def _result(
    *,
    selected_candidate: Mapping[str, Any] | None,
    ranking: list[dict[str, Any]],
    rejection_reasons: Mapping[str, list[str]],
    input_count: int,
    min_score: Decimal,
) -> dict:
    selected = selected_candidate is not None
    selected_candidate_id = (
        selected_candidate["candidate_id"] if selected_candidate is not None else None
    )
    total_score = (
        selected_candidate["total_score"] if selected_candidate is not None else None
    )
    return {
        "selector_version": SELECTOR_VERSION,
        "selected": selected,
        "selected_candidate_id": selected_candidate_id,
        "selected_candidate": _selected_candidate_payload(selected_candidate),
        "selected_reasons": (
            list(selected_candidate["selection_reasons"])
            if selected_candidate is not None
            else []
        ),
        "total_score": total_score,
        "min_score": _decimal_float(min_score),
        "input_count": input_count,
        "eligible_count": len(ranking),
        "rejected_count": len(rejection_reasons),
        "ranking": ranking,
        "rejection_reasons": {
            candidate_id: list(reasons)
            for candidate_id, reasons in sorted(rejection_reasons.items())
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "execution_allowed": False,
        "broker_access_allowed": False,
        "credential_access_allowed": False,
        "account_access_allowed": False,
        "trade_action_allowed": False,
        "live_trade_allowed": False,
        "demo_trade_allowed": False,
        "paper_trade_allowed": False,
        "order_placement_allowed": False,
        "order_closure_allowed": False,
        "production_activation_allowed": False,
        "next_safe_action": (
            SELECTION_NEXT_SAFE_ACTION if selected else NO_SELECTION_NEXT_SAFE_ACTION
        ),
    }


def _unsafe_true_flags(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    flags: list[str] = []
    for field_name in UNSAFE_TRUE_FIELDS:
        if _truthy(candidate["proof_flags"].get(field_name)):
            flags.append(field_name)
    return tuple(flags)


def _first(source: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in source:
            return source[name]
    return None


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _reason_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = _text(value)
        return [text] if text else []
    if isinstance(value, Mapping):
        return [
            _text(key)
            for key, active in value.items()
            if active and _text(key)
        ]
    if isinstance(value, (list, tuple, set)):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    return [text] if text else []


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "y")
    return False


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def _canonical_status(value: Any) -> str:
    return _text(value).upper().replace("-", "_").replace(" ", "_")


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _number_or_default(value: Any, default: Decimal) -> Decimal:
    number = _decimal_or_none(value)
    return default if number is None else number


def _decimal_float(value: Any) -> float | None:
    if value is None:
        return None
    number = _decimal_or_none(value)
    if number is None:
        return None
    return float(round(number, 6))


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Decimal):
        return _decimal_float(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
