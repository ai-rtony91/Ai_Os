"""Paper-only Trading Watchtower V1.

This module ranks caller-supplied or local JSON candidates for review. It does
not call brokers, submit orders, use API keys, start workers, or write files.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


RESULT_SCHEMA = "AIOS_TRADING_WATCHTOWER_RESULT.v1"
CANDIDATE_SCHEMA = "AIOS_TRADING_WATCHTOWER_CANDIDATE.v1"
COMPONENT = "trading_watchtower"
MODE = "PAPER_ONLY_READ_ONLY"

WATCHTOWER_STATES = {
    "NO_SETUP",
    "WATCHING",
    "CANDIDATE_FOUND",
    "HIGH_PRIORITY",
    "INVALIDATED",
    "REVIEW_REQUIRED",
}
REGIME_LABELS = {"TREND_UP", "TREND_DOWN", "RANGE", "HIGH_VOL", "LOW_VOL", "UNKNOWN"}
VALID_DIRECTIONS = {"LONG", "SHORT"}
HIGH_PRIORITY_THRESHOLD = 75.0
CANDIDATE_THRESHOLD = 45.0

PAPER_ONLY_AUTHORITY = {
    "paper_only": True,
    "read_only": True,
    "execution_allowed": False,
    "broker_allowed": False,
    "order_submission_allowed": False,
    "live_trading_allowed": False,
}

UNSAFE_TRUE_FIELDS = {
    "broker_allowed",
    "broker_execution",
    "execution_allowed",
    "live_execution",
    "live_trading",
    "live_trading_allowed",
    "network_access",
    "order_submission",
    "order_submission_allowed",
    "real_order",
    "real_orders",
    "submit_order",
}
UNSAFE_VALUE_FIELDS = {
    "api_key",
    "broker_credentials",
    "credentials",
    "oanda_credentials",
    "secret",
    "token",
    "webhook_url",
}
STOP_STATES = {"STOP", "SOS", "REVIEW_REQUIRED", "BLOCKED"}
STOP_CLASSIFICATIONS = {
    "SECURITY_SOS_DIRTY",
    "PROTECTED_AUTHORITY_DIRTY",
    "UNKNOWN_DIRTY",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _number(value: Any, default: float = 0.0) -> float:
    try:
        if value is True or value is False:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _ratio(value: Any, default: float = 0.0) -> float:
    raw = _number(value, default)
    if raw > 1.0:
        raw = raw / 100.0
    return _clamp(raw)


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _normalize_direction(value: Any) -> str:
    raw = str(value or "").strip().upper()
    if raw in {"BUY", "BULL", "BULLISH", "LONG"}:
        return "LONG"
    if raw in {"SELL", "BEAR", "BEARISH", "SHORT"}:
        return "SHORT"
    return raw


def _normalize_regime(value: Any) -> str:
    raw = str(value or "UNKNOWN").strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "UPTREND": "TREND_UP",
        "BULL": "TREND_UP",
        "BULLISH": "TREND_UP",
        "DOWNTREND": "TREND_DOWN",
        "BEAR": "TREND_DOWN",
        "BEARISH": "TREND_DOWN",
        "RANGING": "RANGE",
        "SIDEWAYS": "RANGE",
        "HIGH_VOLATILITY": "HIGH_VOL",
        "LOW_VOLATILITY": "LOW_VOL",
    }
    normalized = aliases.get(raw, raw)
    return normalized if normalized in REGIME_LABELS else "UNKNOWN"


def _iter_candidates(candidate_data: Any) -> tuple[list[Any], str]:
    if candidate_data is None:
        return [], "UNKNOWN"
    if isinstance(candidate_data, list):
        return candidate_data, "UNKNOWN"
    if isinstance(candidate_data, Mapping):
        market_regime = _normalize_regime(candidate_data.get("market_regime"))
        for key in ("candidates", "candidate_targets", "signals", "setups"):
            value = candidate_data.get(key)
            if isinstance(value, list):
                return value, market_regime
        if candidate_data.get("symbol") or candidate_data.get("direction") or candidate_data.get("signal"):
            return [candidate_data], market_regime
    return [], "UNKNOWN"


def _truthy_present(value: Any) -> bool:
    return value not in (None, "", False, [], {})


def _unsafe_candidate_reason(candidate: Mapping[str, Any]) -> str | None:
    for field in sorted(UNSAFE_TRUE_FIELDS):
        if candidate.get(field) is True:
            return f"{field}_blocked"
    for field in sorted(UNSAFE_VALUE_FIELDS):
        if _truthy_present(candidate.get(field)):
            return f"{field}_blocked"
    return None


def _is_invalidated(candidate: Mapping[str, Any]) -> bool:
    status = str(candidate.get("status") or candidate.get("state") or "").strip().upper()
    return candidate.get("invalidated") is True or status == "INVALIDATED"


def _evidence_quality(candidate: Mapping[str, Any]) -> tuple[float, list[str]]:
    penalties: list[str] = []
    explicit = candidate.get("evidence_quality", candidate.get("evidence_score"))
    if explicit is not None:
        quality = _ratio(explicit, 0.0)
    else:
        evidence = candidate.get("evidence")
        evidence_count = int(_number(candidate.get("evidence_count"), 0))
        if isinstance(evidence, list):
            evidence_count = max(evidence_count, len(evidence))
        if evidence_count >= 3:
            quality = 0.85
        elif evidence_count > 0 or isinstance(evidence, Mapping):
            quality = 0.65
        elif str(candidate.get("reason") or "").strip():
            quality = 0.45
            penalties.append("missing_structured_evidence")
        else:
            quality = 0.25
            penalties.append("missing_evidence")
    if candidate.get("stale") is True or _number(candidate.get("age_minutes"), 0) > 240:
        quality = max(0.0, quality - 0.25)
        penalties.append("stale_evidence")
    return quality, penalties


def _regime_alignment(regime: str, direction: str, market_regime: str) -> tuple[float, list[str]]:
    penalties: list[str] = []
    if regime == "UNKNOWN":
        return 0.35, ["unknown_regime"]
    if market_regime != "UNKNOWN" and regime == market_regime:
        return 1.0, penalties
    if direction == "LONG" and regime == "TREND_UP":
        return 0.9, penalties
    if direction == "SHORT" and regime == "TREND_DOWN":
        return 0.9, penalties
    if regime == "RANGE":
        return 0.65, penalties
    if regime == "LOW_VOL":
        return 0.6, penalties
    if regime == "HIGH_VOL":
        return 0.5, penalties
    return 0.4, penalties


def _stop_quality(candidate: Mapping[str, Any]) -> tuple[float, list[str]]:
    invalidation = candidate.get("invalidation_level", candidate.get("stop_loss"))
    stop_distance = candidate.get("stop_distance_pct", candidate.get("stop_distance"))
    if _truthy_present(invalidation):
        distance = _number(stop_distance, 0)
        if 0 < distance <= 5:
            return 0.95, []
        return 0.85, []
    return 0.25, ["missing_invalidation_level"]


def _volatility_context(candidate: Mapping[str, Any], regime: str) -> tuple[float, list[str]]:
    explicit = candidate.get("volatility_score", candidate.get("volatility_context_score"))
    if explicit is not None:
        return _ratio(explicit, 0.5), []
    context = str(candidate.get("volatility_context") or "").strip().upper().replace("-", "_").replace(" ", "_")
    if context in {"NORMAL", "ALIGNED", "STABLE"}:
        return 0.8, []
    if context in {"EXTREME", "SPIKE", "UNKNOWN"}:
        return 0.35, [f"volatility_{context.lower()}"]
    if regime == "HIGH_VOL":
        return 0.45, ["high_vol_regime"]
    if regime == "LOW_VOL":
        return 0.65, []
    return 0.55, []


def _score_candidate(candidate: Mapping[str, Any], regime: str, direction: str, market_regime: str) -> tuple[float, dict[str, float], list[str]]:
    confidence = _ratio(candidate.get("confidence", candidate.get("confidence_score")), 0.0)
    risk_score = _ratio(candidate.get("risk_score", candidate.get("risk")), 0.5)
    evidence, evidence_penalties = _evidence_quality(candidate)
    regime_score, regime_penalties = _regime_alignment(regime, direction, market_regime)
    stop_score, stop_penalties = _stop_quality(candidate)
    volatility_score, volatility_penalties = _volatility_context(candidate, regime)
    risk_component = 1.0 - risk_score
    total = (
        confidence * 0.30
        + evidence * 0.20
        + regime_score * 0.18
        + stop_score * 0.17
        + volatility_score * 0.10
        + risk_component * 0.05
    )
    penalties = evidence_penalties + regime_penalties + stop_penalties + volatility_penalties
    if "stale_evidence" in penalties:
        total -= 0.12
    if "missing_evidence" in penalties:
        total -= 0.07
    if "unknown_regime" in penalties:
        total -= 0.05
    breakdown = {
        "confidence": round(confidence, 4),
        "evidence_quality": round(evidence, 4),
        "regime_alignment": round(regime_score, 4),
        "stop_quality": round(stop_score, 4),
        "volatility_context": round(volatility_score, 4),
        "risk_component": round(risk_component, 4),
    }
    return round(_clamp(total) * 100.0, 2), breakdown, penalties


def _normalize_candidate(raw: Any, index: int, market_regime: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(raw, Mapping):
        return None, {"index": index, "reason_code": "not_an_object", "safe_to_rank": False}
    symbol = _normalize_symbol(raw.get("symbol") or raw.get("ticker") or raw.get("instrument"))
    direction = _normalize_direction(raw.get("direction") or raw.get("signal") or raw.get("side"))
    if not symbol:
        return None, {"index": index, "reason_code": "missing_symbol", "safe_to_rank": False}
    if direction not in VALID_DIRECTIONS:
        return None, {"index": index, "symbol": symbol, "reason_code": "unsupported_direction", "safe_to_rank": False}
    unsafe_reason = _unsafe_candidate_reason(raw)
    if unsafe_reason:
        return None, {"index": index, "symbol": symbol, "reason_code": unsafe_reason, "safe_to_rank": False}
    if _is_invalidated(raw):
        return None, {"index": index, "symbol": symbol, "reason_code": "invalidated", "safe_to_rank": False}

    regime = _normalize_regime(raw.get("regime") or raw.get("market_regime"))
    score, breakdown, penalties = _score_candidate(raw, regime, direction, market_regime)
    candidate = {
        "schema": CANDIDATE_SCHEMA,
        "symbol": symbol,
        "direction": direction,
        "confidence": round(_ratio(raw.get("confidence", raw.get("confidence_score")), 0.0), 4),
        "risk_score": round(_ratio(raw.get("risk_score", raw.get("risk")), 0.5), 4),
        "regime": regime,
        "reason": str(raw.get("reason") or raw.get("setup") or raw.get("notes") or "Paper-only candidate normalized by Watchtower.").strip(),
        "invalidation_level": raw.get("invalidation_level", raw.get("stop_loss")),
        "priority_rank": 0,
        "total_score": score,
        "score_breakdown": breakdown,
        "penalties": penalties,
        "status": "WATCHING",
        "next_safe_action": "Review this paper-only candidate; do not route it to broker execution or order submission.",
        **PAPER_ONLY_AUTHORITY,
    }
    return candidate, None


def _extract_security_payloads(candidate_data: Any, security_evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    if isinstance(security_evidence, Mapping):
        payloads.update(security_evidence)
    if isinstance(candidate_data, Mapping):
        for key in ("security_evidence", "preemptive_security", "dirty_tree", "decision_governor"):
            value = candidate_data.get(key)
            if isinstance(value, Mapping):
                if key == "security_evidence":
                    payloads.update(value)
                else:
                    payloads[key] = value
    return payloads


def _blocked_action_indicates_review(actions: Iterable[Any]) -> bool:
    for action in actions:
        normalized = str(action).strip().lower()
        if "protected" in normalized or "security" in normalized or "git commit" in normalized or "git push" in normalized:
            return True
    return False


def _evidence_requires_review(name: str, payload: Any) -> tuple[bool, str | None]:
    if not isinstance(payload, Mapping):
        return False, None
    schema = str(payload.get("schema") or "").upper()
    component = str(payload.get("component") or name or "").lower()
    state = str(
        payload.get("overall_state")
        or payload.get("state")
        or payload.get("status")
        or payload.get("decision")
        or payload.get("classification")
        or ""
    ).strip().upper()
    classification = str(payload.get("overall_classification") or payload.get("classification") or "").strip().upper()
    blocked_reason = str(payload.get("blocked_reason") or payload.get("stop_reason") or "").strip().lower()
    blocked_actions = payload.get("blocked_actions")

    if state in STOP_STATES:
        return True, f"{name}_state_{state.lower()}"
    if classification in STOP_CLASSIFICATIONS:
        return True, f"{name}_classification_{classification.lower()}"
    if payload.get("sos_required") is True or payload.get("stop_required") is True:
        return True, f"{name}_stop_required"
    if payload.get("protected_stop_required") is True:
        return True, f"{name}_protected_stop_required"
    if payload.get("review_required") is True and ("security" in schema or "dirty" in schema or "security" in component):
        return True, f"{name}_security_review_required"
    if "protected" in blocked_reason or "security" in blocked_reason or "sos" in blocked_reason:
        return True, f"{name}_blocked_{blocked_reason}"
    if isinstance(blocked_actions, list) and _blocked_action_indicates_review(blocked_actions):
        return True, f"{name}_blocked_protected_action"
    return False, None


def _security_integration(candidate_data: Any, security_evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    payloads = _extract_security_payloads(candidate_data, security_evidence)
    triggers: list[str] = []
    for name, payload in sorted(payloads.items()):
        requires_review, reason = _evidence_requires_review(str(name), payload)
        if requires_review and reason:
            triggers.append(reason)
    return {
        "evidence_present": bool(payloads),
        "review_required": bool(triggers),
        "triggers": triggers,
        "next_safe_action": (
            "Stop and review security evidence before using Watchtower ranking."
            if triggers
            else "Continue paper-only watchtower review; security evidence did not require a stop."
        ),
    }


def _status_for_score(total_score: float) -> str:
    if total_score >= HIGH_PRIORITY_THRESHOLD:
        return "HIGH_PRIORITY"
    if total_score >= CANDIDATE_THRESHOLD:
        return "CANDIDATE_FOUND"
    return "WATCHING"


def _watchtower_status(
    *,
    security_review_required: bool,
    candidate_count: int,
    valid_count: int,
    rejected: list[dict[str, Any]],
    top_score: float,
) -> str:
    if security_review_required:
        return "REVIEW_REQUIRED"
    if valid_count == 0 and candidate_count > 0 and rejected and all(item.get("reason_code") == "invalidated" for item in rejected):
        return "INVALIDATED"
    if valid_count == 0:
        return "NO_SETUP"
    return _status_for_score(top_score)


def build_watchtower_result(
    candidate_data: Any = None,
    *,
    security_evidence: Mapping[str, Any] | None = None,
    as_of_utc: str | None = None,
) -> dict[str, Any]:
    raw_candidates, payload_market_regime = _iter_candidates(candidate_data)
    security = _security_integration(candidate_data, security_evidence)
    normalized: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for index, raw in enumerate(raw_candidates):
        candidate, rejection = _normalize_candidate(raw, index, payload_market_regime)
        if candidate is not None:
            normalized.append(candidate)
        elif rejection is not None:
            rejected.append(rejection)

    normalized.sort(key=lambda item: item["total_score"], reverse=True)
    for rank, candidate in enumerate(normalized, start=1):
        candidate["priority_rank"] = rank
        candidate["status"] = _status_for_score(candidate["total_score"])

    top = normalized[0] if normalized else None
    market_regime = payload_market_regime if payload_market_regime != "UNKNOWN" else (top["regime"] if top else "UNKNOWN")
    status = _watchtower_status(
        security_review_required=security["review_required"],
        candidate_count=len(raw_candidates),
        valid_count=len(normalized),
        rejected=rejected,
        top_score=top["total_score"] if top else 0.0,
    )
    priority_targets = [candidate for candidate in normalized if candidate["total_score"] >= HIGH_PRIORITY_THRESHOLD]
    next_best_setup = None if security["review_required"] else top
    market_radar = [
        {
            "symbol": candidate["symbol"],
            "direction": candidate["direction"],
            "regime": candidate["regime"],
            "priority_rank": candidate["priority_rank"],
            "total_score": candidate["total_score"],
            "status": candidate["status"],
        }
        for candidate in normalized[:10]
    ]
    next_safe_action = (
        security["next_safe_action"]
        if security["review_required"]
        else "Review the top paper-only setup; no broker, order, live-trading, worker, scheduler, or dashboard action is authorized."
    )

    return {
        "schema": RESULT_SCHEMA,
        "generated_at_utc": as_of_utc or utc_now(),
        "component": COMPONENT,
        "mode": MODE,
        **PAPER_ONLY_AUTHORITY,
        "candidate_count": len(raw_candidates),
        "valid_candidate_count": len(normalized),
        "rejected_candidate_count": len(rejected),
        "rejected_candidates": rejected,
        "market_radar": market_radar,
        "candidate_targets": normalized,
        "priority_targets": priority_targets,
        "market_regime": market_regime,
        "watchtower_status": status,
        "next_best_setup": next_best_setup,
        "security_integration": security,
        "ranking": {
            "ranking_method": "confidence/evidence/regime/stop/volatility/risk weighted paper-only score",
            "highest_total_score_first": True,
            "high_priority_threshold": HIGH_PRIORITY_THRESHOLD,
            "candidate_threshold": CANDIDATE_THRESHOLD,
            "penalizes_stale_missing_unknown_evidence": True,
        },
        "safety": {
            **PAPER_ONLY_AUTHORITY,
            "writes_outputs_by_default": False,
            "requires_api_keys": False,
            "broker_modules_called": False,
            "paper_orders_submitted": False,
            "live_orders_submitted": False,
            "network_access": False,
            "external_webhooks": False,
            "dashboard_mutation": False,
            "scheduler_activation": False,
            "daemon_activation": False,
            "worker_launch": False,
        },
        "next_safe_action": next_safe_action,
    }


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit paper-only Trading Watchtower V1 JSON.")
    parser.add_argument("--candidate-json", default="", help="Local JSON file containing a candidate, list, or payload with candidates.")
    parser.add_argument("--security-json", action="append", default=[], help="Optional local security evidence JSON file. May be repeated.")
    parser.add_argument("--as-of-utc", default="", help="Optional generated_at_utc override for deterministic tests.")
    args = parser.parse_args(argv)

    candidate_data = load_json(args.candidate_json) if args.candidate_json else []
    security_payloads: dict[str, Any] = {}
    for index, path in enumerate(args.security_json):
        payload = load_json(path)
        if isinstance(payload, Mapping):
            key = str(payload.get("component") or payload.get("schema") or f"security_{index}")
            security_payloads[key] = payload

    result = build_watchtower_result(
        candidate_data,
        security_evidence=security_payloads,
        as_of_utc=args.as_of_utc or None,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
