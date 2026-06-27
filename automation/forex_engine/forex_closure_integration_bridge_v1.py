"""Forex closure integration bridge V1.

The bridge orchestrates the six local convergence engines and aggregates their
results. It does not duplicate the engines' business logic and does not call
brokers, read secrets, mutate dashboards, submit orders, or approve execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine.broker_health_readonly_v1 import (
    BROKER_HEALTH_REVIEW_READY,
    build_sample_snapshot,
    evaluate_broker_health_readonly,
)
from automation.forex_engine.dashboard_truth_summary_v1 import (
    DASHBOARD_TRUTH_DISPLAY_READY,
    build_dashboard_truth_summary,
)
from automation.forex_engine.profitability_evidence_v1 import (
    PROFITABILITY_EVIDENCE_REVIEW_READY,
    build_sample_closed_trades,
    build_sample_replay_summaries,
    build_sample_thresholds,
    build_sample_walk_forward_summaries,
    evaluate_profitability_evidence,
)
from automation.forex_engine.risk_budget_engine_v1 import (
    RISK_BUDGET_ACCEPTED,
    build_sample_candidate as build_sample_risk_candidate,
    build_sample_risk_caps,
    evaluate_risk_budget,
)
from automation.forex_engine.stop_pause_resume_engine_v1 import (
    REVIEW_ONLY_RESUME,
    build_sample_dashboard_state,
    build_sample_operator_halt_state,
    evaluate_stop_pause_resume,
)
from automation.forex_engine.supervised_demo_intent_card_v1 import (
    DEMO_INTENT_OWNER_REVIEW_READY,
    evaluate_supervised_demo_intent_card,
)


FOREX_CLOSURE_INTEGRATION_BRIDGE_VERSION = "forex_closure_integration_bridge_v1"

FOREX_CLOSURE_CHAIN_REVIEW_READY = "FOREX_CLOSURE_CHAIN_REVIEW_READY"
FOREX_CLOSURE_CHAIN_BLOCKED = "FOREX_CLOSURE_CHAIN_BLOCKED"
FOREX_CLOSURE_CHAIN_INCOMPLETE = "FOREX_CLOSURE_CHAIN_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

READY_STAGE_STATUSES = {
    "risk": RISK_BUDGET_ACCEPTED,
    "broker": BROKER_HEALTH_REVIEW_READY,
    "profitability": PROFITABILITY_EVIDENCE_REVIEW_READY,
    "stop": REVIEW_ONLY_RESUME,
    "demo_intent": DEMO_INTENT_OWNER_REVIEW_READY,
    "dashboard_truth": DASHBOARD_TRUTH_DISPLAY_READY,
}


def build_sample_integration_input() -> dict[str, Any]:
    candidate = build_sample_risk_candidate()
    candidate.update(
        {
            "instrument": "EUR_USD_SANITIZED_REVIEW",
            "direction": "long_review",
            "max_evidence_age_days": 7,
        }
    )
    return {
        "candidate": candidate,
        "risk_caps": build_sample_risk_caps(),
        "broker_snapshot": build_sample_snapshot(),
        "closed_trade_evidence": build_sample_closed_trades(),
        "replay_summaries": build_sample_replay_summaries(),
        "walk_forward_summaries": build_sample_walk_forward_summaries(),
        "profitability_thresholds": build_sample_thresholds(),
        "dashboard_state": build_sample_dashboard_state(),
        "operator_halt_state": build_sample_operator_halt_state(),
    }


def run_forex_closure_integration_bridge(
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the local closure chain and aggregate stage results."""

    if payload is None:
        active = build_sample_integration_input()
    else:
        active = dict(payload)

    candidate = active.get("candidate")
    risk = evaluate_risk_budget(candidate, active.get("risk_caps"))
    broker = evaluate_broker_health_readonly(active.get("broker_snapshot"))
    profitability = evaluate_profitability_evidence(
        active.get("closed_trade_evidence"),
        active.get("replay_summaries"),
        active.get("walk_forward_summaries"),
        active.get("profitability_thresholds"),
    )
    stop = evaluate_stop_pause_resume(
        risk,
        broker,
        profitability,
        active.get("dashboard_state"),
        active.get("operator_halt_state"),
    )
    demo_intent = evaluate_supervised_demo_intent_card(
        candidate,
        risk,
        broker,
        profitability,
        stop,
    )
    dashboard_truth = build_dashboard_truth_summary(
        {
            "risk": risk,
            "broker": broker,
            "profitability": profitability,
            "stop": stop,
            "demo_intent": demo_intent,
        }
    )

    stage_results = {
        "risk": risk,
        "broker": broker,
        "profitability": profitability,
        "stop": stop,
        "demo_intent": demo_intent,
        "dashboard_truth": dashboard_truth,
    }
    stage_statuses = {
        name: str(result.get("status", ""))
        for name, result in stage_results.items()
    }
    blockers = _stage_blockers(stage_results)
    missing_or_incomplete = [
        name
        for name, status in stage_statuses.items()
        if "INCOMPLETE" in status or not status
    ]
    not_ready = [
        name
        for name, status in stage_statuses.items()
        if status != READY_STAGE_STATUSES[name]
    ]

    if missing_or_incomplete:
        status = FOREX_CLOSURE_CHAIN_INCOMPLETE
        next_safe_action = "Repair incomplete chain inputs before owner review."
    elif blockers or not_ready:
        status = FOREX_CLOSURE_CHAIN_BLOCKED
        next_safe_action = "Resolve chain blockers before final readiness review."
    else:
        status = FOREX_CLOSURE_CHAIN_REVIEW_READY
        next_safe_action = (
            "Run final readiness evidence checks; this chain authorizes no execution."
        )

    return {
        "engine_version": FOREX_CLOSURE_INTEGRATION_BRIDGE_VERSION,
        "status": status,
        "stage_statuses": stage_statuses,
        "stage_results": stage_results,
        "blockers": blockers,
        "not_ready_stages": not_ready,
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return _jsonable(dict(result))


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", FOREX_CLOSURE_CHAIN_INCOMPLETE))
    if status == FOREX_CLOSURE_CHAIN_REVIEW_READY:
        return "Forex closure chain is review-ready only. Final readiness evidence is still required."
    blockers = result.get("blockers") or ["closure chain incomplete"]
    return "Forex closure chain blocked: " + "; ".join(str(item) for item in blockers)


def _stage_blockers(stage_results: Mapping[str, Mapping[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for stage, result in stage_results.items():
        raw = result.get("blockers") or []
        if isinstance(raw, str):
            raw_values = [raw]
        elif isinstance(raw, (list, tuple, set)):
            raw_values = list(raw)
        else:
            raw_values = [raw] if raw else []
        blockers.extend(f"{stage}: {item}" for item in raw_values if str(item))
    return _dedupe(blockers)


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


__all__ = [
    "FOREX_CLOSURE_CHAIN_BLOCKED",
    "FOREX_CLOSURE_CHAIN_INCOMPLETE",
    "FOREX_CLOSURE_CHAIN_REVIEW_READY",
    "FOREX_CLOSURE_INTEGRATION_BRIDGE_VERSION",
    "build_sample_integration_input",
    "result_to_jsonable_dict",
    "result_to_operator_text",
    "run_forex_closure_integration_bridge",
]
