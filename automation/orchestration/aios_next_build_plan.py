from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_NEXT_BUILD_PLAN.v1"
INPUT_SCHEMA = "AIOS_FOREX_GOAL_DECISION.v1"
POST_RISK_INPUT_SCHEMA = "AIOS_FOREX_POST_RISK_DECISION.v1"

ROUTES = {
    "continue_build": {
        "route": "build_next_paper_component",
        "next_component": "forex_risk_controls",
        "next_packet_id": "PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY",
        "next_safe_action": "Prepare a bounded paper-only Forex risk controls build packet.",
    },
    "improve_strategy": {
        "route": "improve_strategy_rules",
        "next_component": "forex_strategy_rules_review",
        "next_packet_id": "PKT-AIOS-FOREX-STRATEGY-RULES-REVIEW-APPLY",
        "next_safe_action": "Prepare a bounded paper-only strategy rules review packet.",
    },
    "improve_data": {
        "route": "improve_data_quality",
        "next_component": "forex_data_quality_review",
        "next_packet_id": "PKT-AIOS-FOREX-DATA-QUALITY-REVIEW-APPLY",
        "next_safe_action": "Prepare a bounded paper-only data quality review packet.",
    },
    "improve_risk_controls": {
        "route": "build_risk_controls",
        "next_component": "forex_risk_controls",
        "next_packet_id": "PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY",
        "next_safe_action": "Prepare a bounded paper-only Forex risk controls build packet.",
    },
    "stop_for_human_review": {
        "route": "stop",
        "next_component": "none",
        "next_packet_id": "NONE",
        "next_safe_action": "Stop for Anthony review before preparing another build packet.",
    },
}

POST_RISK_ROUTES = {
    "forex_risk_controls": {
        "route": "build_next_paper_component",
        "next_component": "forex_risk_controls",
        "next_packet_id": "PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY",
        "next_safe_action": "Prepare a bounded paper-only Forex risk controls build packet.",
    },
    "forex_paper_execution_simulator": {
        "route": "build_next_paper_component",
        "next_component": "forex_paper_execution_simulator",
        "next_packet_id": "PKT-AIOS-FOREX-PAPER-EXECUTION-SIMULATOR-CONTINUATION-APPLY",
        "next_safe_action": "Prepare bounded paper execution simulator packet for Anthony review.",
    },
    "none": {
        "route": "stop",
        "next_component": "none",
        "next_packet_id": "NONE",
        "next_safe_action": "Stop for Anthony review before defining another paper-only Forex component.",
    },
}


def safety_flags() -> dict[str, bool]:
    return {
        "file_writes": False,
        "network_access": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "runtime_launch": False,
        "scheduler": False,
        "daemon": False,
        "broker": False,
        "credentials": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def approval_required() -> dict[str, bool]:
    return {
        "local_plan_preview": False,
        "commit": True,
        "push": True,
        "merge": True,
        "queue_mutation": True,
        "approval_mutation": True,
        "worker_dispatch": True,
        "runtime_launch": True,
        "scheduler_activation": True,
        "broker_live_trading": True,
    }


def _input_decision(goal_decision: dict[str, Any]) -> str:
    decision = goal_decision.get("decision")
    return decision if isinstance(decision, str) and decision else "invalid_decision"


def _build_post_risk_next_build_plan(post_risk_decision: dict[str, Any]) -> dict[str, Any]:
    goal = post_risk_decision.get("goal", "forex-paper-bot")
    selected_next_component = post_risk_decision.get("selected_next_component", "none")
    if not isinstance(selected_next_component, str) or not selected_next_component:
        selected_next_component = "none"
    reason_code = post_risk_decision.get("reason_code", "invalid_post_risk_decision")
    decision_reasons = post_risk_decision.get("decision_reasons", [])
    if not isinstance(decision_reasons, list):
        decision_reasons = [str(decision_reasons)]

    route_info = POST_RISK_ROUTES.get(selected_next_component)
    if route_info is None:
        route_info = POST_RISK_ROUTES["none"]
        selected_next_component = "none"
        reason_code = "invalid_post_risk_decision"
        decision_reasons = ["invalid_post_risk_decision"]

    route = route_info["route"]
    return {
        "schema": SCHEMA,
        "goal": goal,
        "input_decision": str(post_risk_decision.get("selected_action", "none")),
        "route": route,
        "next_component": route_info["next_component"],
        "next_packet_id": route_info["next_packet_id"],
        "reason_code": reason_code,
        "plan_reasons": [*decision_reasons, f"route:{route}"],
        "next_safe_action": route_info["next_safe_action"],
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }


def build_next_build_plan(goal_decision: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(goal_decision, dict):
        goal_decision = {}
    if goal_decision.get("schema") == POST_RISK_INPUT_SCHEMA:
        return _build_post_risk_next_build_plan(goal_decision)

    goal = goal_decision.get("goal", "forex-paper-bot")
    input_decision = _input_decision(goal_decision)
    reason_code = goal_decision.get("reason_code", "invalid_decision")
    decision_reasons = goal_decision.get("decision_reasons", [])
    if not isinstance(decision_reasons, list):
        decision_reasons = [str(decision_reasons)]

    route_info = ROUTES.get(input_decision)
    if route_info is None:
        route_info = ROUTES["stop_for_human_review"]
        input_decision = "invalid_decision"
        reason_code = "invalid_decision"
        decision_reasons = ["invalid_decision"]

    route = route_info["route"]
    plan_reasons = [*decision_reasons, f"route:{route}"]

    return {
        "schema": SCHEMA,
        "goal": goal,
        "input_decision": input_decision,
        "route": route,
        "next_component": route_info["next_component"],
        "next_packet_id": route_info["next_packet_id"],
        "reason_code": reason_code,
        "plan_reasons": plan_reasons,
        "next_safe_action": route_info["next_safe_action"],
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Route a deterministic AIOS goal decision into a next build plan.")
    parser.add_argument("--decision", default="continue_build", help="Decision to route for local preview.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = build_next_build_plan(
        {
            "schema": INPUT_SCHEMA,
            "goal": "forex-paper-bot",
            "decision": args.decision,
            "reason_code": "manual_preview",
            "decision_reasons": ["manual_preview"],
        }
    )
    print(json.dumps(plan, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
