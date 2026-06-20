"""Canonical deterministic strategy evaluation harness for paper evidence."""
from __future__ import annotations

import math
from typing import Any, Mapping

from automation.forex_engine.paper_session_sample_generator import generate_paper_session_sample

MODE = "STRATEGY_EVALUATION_HARNESS_ONLY"
STATUS_DEMO_REVIEW_CANDIDATE = "DEMO_REVIEW_CANDIDATE"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "strategy_evaluation_only": True,
        "broker_api_access": False,
        "credentials_access": False,
        "orders_submitted": False,
        "live_trades_placed": False,
        "capital_allocation_modified": False,
        "production_deployment_active": False,
        "demo_execution_active": False,
        "network_api_access": False,
    }


def _finite_float(value: Any) -> tuple[float, bool]:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0, False
    if not math.isfinite(result):
        return 0.0, False
    return round(result, 8), True


def _first_present(source: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in source:
            return source[key]
    return None


def _promotion_status(status: Any) -> str:
    if str(status) == "DEMO_CANDIDATE":
        return STATUS_DEMO_REVIEW_CANDIDATE
    return str(status or "MORE_EVIDENCE_REQUIRED")


def _evidence_references(sample_result: Mapping[str, Any] | None = None) -> dict[str, Any]:
    sample = sample_result if isinstance(sample_result, Mapping) else {}
    ledger = sample.get("paper_trade_ledger") if isinstance(sample.get("paper_trade_ledger"), Mapping) else {}
    replay = sample.get("replay_evidence") if isinstance(sample.get("replay_evidence"), Mapping) else {}
    workflow = sample.get("workflow_result") if isinstance(sample.get("workflow_result"), Mapping) else {}
    workflow_refs = workflow.get("evidence_references") if isinstance(workflow.get("evidence_references"), Mapping) else {}
    return {
        "session_id": str(sample.get("session_id") or ledger.get("session_id") or replay.get("session_id") or ""),
        "ledger_event_count": len(ledger.get("events", [])) if isinstance(ledger.get("events"), list) else 0,
        "closed_trade_count": len(sample.get("closed_trades", [])) if isinstance(sample.get("closed_trades"), list) else 0,
        "replay_present": bool(replay),
        "session_metrics_present": isinstance(sample.get("session_metrics"), Mapping),
        "balance_history_points": len(sample.get("balance_history", [])) if isinstance(sample.get("balance_history"), list) else 0,
        "workflow_evidence_references": dict(workflow_refs),
    }


def _blocked_result(strategy_name: str, strategy_version: str, total_trades: int, blocked_reasons: list[str]) -> dict[str, Any]:
    unique_reasons = list(dict.fromkeys(reason for reason in blocked_reasons if reason))
    profitability_result = {
        "allowed": False,
        "profitability_ready": False,
        "sample_size_met": False,
        "expectancy_per_trade": 0.0,
        "expectancy_r": 0.0,
        "profit_factor": 0.0,
        "risk_quality_passed": False,
        "evidence_quality_passed": False,
        "blocked_reasons": unique_reasons,
    }
    promotion_result = {
        "allowed": False,
        "promotion_status": "MORE_EVIDENCE_REQUIRED",
        "demo_candidate": False,
        "blocked_reasons": unique_reasons,
        "next_safe_action": "continue_paper_trading_collect_more_evidence",
        "safety": _safety(),
    }
    return {
        "strategy_name": strategy_name,
        "strategy_version": strategy_version,
        "total_trades": total_trades,
        "profitability_result": profitability_result,
        "promotion_result": promotion_result,
        "promotion_status": "MORE_EVIDENCE_REQUIRED",
        "demo_candidate": False,
        "blocked_reasons": unique_reasons,
        "next_safe_action": "continue_paper_trading_collect_more_evidence",
        "evidence_references": _evidence_references(),
        "safety": _safety(),
        "mode": MODE,
    }


def _candidate_to_sample(candidate: Any, index: int) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(candidate, Mapping):
        return None, ["malformed_strategy_candidate"]

    pnl, pnl_valid = _finite_float(_first_present(candidate, ("realized_pl", "pnl", "pnl_usd")))
    entry, entry_valid = _finite_float(candidate.get("entry", 1.1))
    stop, stop_valid = _finite_float(candidate.get("stop", 1.09))
    target, target_valid = _finite_float(candidate.get("target", 1.12))
    risk_percent, risk_valid = _finite_float(candidate.get("risk_percent", 1.0))
    spread, spread_valid = _finite_float(candidate.get("spread", 0.0001))
    direction = str(candidate.get("direction", "buy")).lower()

    reasons: list[str] = []
    if not pnl_valid:
        reasons.append("malformed_strategy_candidate")
    if not entry_valid or not stop_valid or not target_valid or entry <= 0 or stop <= 0 or target <= 0 or entry == stop:
        reasons.append("malformed_strategy_candidate")
    if direction not in {"buy", "sell"}:
        reasons.append("malformed_strategy_candidate")
    if not risk_valid or risk_percent <= 0:
        reasons.append("malformed_strategy_candidate")
    if not spread_valid or spread < 0:
        reasons.append("malformed_strategy_candidate")

    if reasons:
        return None, list(dict.fromkeys(reasons))

    return {
        "trade_id": str(candidate.get("trade_id", f"strategy-trade-{index:04d}")),
        "symbol": str(candidate.get("symbol", "EURUSD")),
        "direction": direction,
        "entry": entry,
        "stop": stop,
        "target": target,
        "risk_percent": risk_percent,
        "spread": spread,
        "realized_pl": pnl,
        "timestamp": str(candidate.get("timestamp", "2026-01-01T00:00:00Z")),
    }, []


def evaluate_strategy(
    strategy_name: str,
    strategy_version: str = "v1",
    strategy_trade_candidates: list[Any] | None = None,
    *,
    paper_session_evidence: Mapping[str, Any] | None = None,
    session_id: str | None = None,
    starting_balance: float = 10000.0,
    evaluator_limits: Mapping[str, Any] | None = None,
    promotion_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate deterministic strategy trade candidates through paper promotion evidence."""
    normalized_name = str(strategy_name or "").strip()
    normalized_version = str(strategy_version or "").strip()
    if not normalized_name:
        return _blocked_result("", normalized_version, 0, ["missing_strategy_name", "evidence_quality_failed"])
    if not normalized_version:
        return _blocked_result(normalized_name, "", 0, ["missing_strategy_version", "evidence_quality_failed"])

    evidence = paper_session_evidence if isinstance(paper_session_evidence, Mapping) else {}
    evidence_candidates = evidence.get("trade_candidates", evidence.get("deterministic_trade_outcomes", []))
    candidates = list(strategy_trade_candidates if strategy_trade_candidates is not None else evidence_candidates or [])
    samples: list[dict[str, Any]] = []
    blocked_reasons: list[str] = []
    for index, candidate in enumerate(candidates, start=1):
        sample, reasons = _candidate_to_sample(candidate, index)
        blocked_reasons.extend(reasons)
        if sample is not None:
            samples.append(sample)

    if blocked_reasons:
        blocked_reasons.append("evidence_quality_failed")
        return _blocked_result(normalized_name, normalized_version, len(samples), blocked_reasons)

    sample_result = generate_paper_session_sample(
        samples,
        session_id=session_id or f"strategy-evaluation-{normalized_name.lower().replace(' ', '-')}-{normalized_version.lower().replace(' ', '-')}",
        starting_balance=starting_balance,
        evaluator_limits=evaluator_limits,
        promotion_limits=promotion_limits,
    )
    promotion_status = _promotion_status(sample_result["promotion_status"])
    return {
        "strategy_name": normalized_name,
        "strategy_version": normalized_version,
        "total_trades": len(sample_result["closed_trades"]),
        "profitability_result": sample_result["profitability_result"],
        "promotion_result": sample_result["promotion_result"],
        "promotion_status": promotion_status,
        "demo_candidate": sample_result["demo_candidate"],
        "blocked_reasons": sample_result["blocked_reasons"],
        "next_safe_action": sample_result["next_safe_action"],
        "evidence_references": _evidence_references(sample_result),
        "safety": _safety(),
        "mode": MODE,
    }
