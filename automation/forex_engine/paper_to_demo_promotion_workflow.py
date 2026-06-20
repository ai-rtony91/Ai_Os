"""Paper-to-demo promotion workflow for paper profitability evidence."""
from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine.paper_evidence_promotion_gate import evaluate_paper_evidence_promotion
from automation.forex_engine.paper_profitability_evaluator import evaluate_paper_profitability

MODE = "PAPER_TO_DEMO_PROMOTION_WORKFLOW_ONLY"


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _as_events(value: Any) -> list[Any]:
    if isinstance(value, Mapping):
        events = value.get("events", [])
        return list(events) if isinstance(events, list) else []
    return list(value) if isinstance(value, list) else []


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_review_only": True,
        "submit_orders": False,
        "broker_access": False,
        "credentials_access": False,
        "network_api_access": False,
        "demo_execution_active": False,
        "live_execution_active": False,
        "capital_allocation_modified": False,
        "real_orders": False,
    }


def _evidence_references(
    paper_trade_ledger: Any,
    replay_evidence: Any,
    session_metrics: Any,
    balance_history: Any,
) -> dict[str, Any]:
    replay = _as_mapping(replay_evidence)
    session = _as_mapping(session_metrics)
    return {
        "ledger_event_count": len(_as_events(paper_trade_ledger)),
        "replay_present": replay is not None,
        "session_metrics_present": session is not None,
        "balance_history_points": len(balance_history) if isinstance(balance_history, list) else 0,
        "session_id": (replay or {}).get("session_id") or (session or {}).get("session_id") or "",
    }


def run_paper_to_demo_promotion_workflow(
    paper_trade_ledger: Any = None,
    replay_evidence: Any = None,
    session_metrics: Any = None,
    balance_history: Any = None,
    profitability_result: Mapping[str, Any] | None = None,
    evaluator_limits: Mapping[str, Any] | None = None,
    promotion_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run paper evidence through profitability evaluation and promotion gating."""
    evaluated = (
        dict(profitability_result)
        if isinstance(profitability_result, Mapping)
        else evaluate_paper_profitability(
            paper_trade_ledger=paper_trade_ledger,
            replay_evidence=replay_evidence,
            session_metrics=session_metrics,
            balance_history=balance_history,
            limits=evaluator_limits,
        )
    )
    promoted = evaluate_paper_evidence_promotion(evaluated, limits=promotion_limits)
    blocked_reasons = _ordered_unique(
        [str(reason) for reason in evaluated.get("blocked_reasons", [])]
        + [str(reason) for reason in promoted.get("blocked_reasons", [])]
    )
    return {
        "workflow_completed": True,
        "profitability_result": evaluated,
        "promotion_result": promoted,
        "promotion_status": str(promoted.get("promotion_status", promoted.get("decision", ""))),
        "next_safe_action": str(promoted.get("next_safe_action", "continue_paper_trading_collect_more_evidence")),
        "demo_candidate": bool(promoted.get("demo_candidate", False)),
        "blocked_reasons": blocked_reasons,
        "safety": _safety(),
        "mode": MODE,
        "evidence_references": _evidence_references(
            paper_trade_ledger,
            replay_evidence,
            session_metrics,
            balance_history,
        ),
    }
