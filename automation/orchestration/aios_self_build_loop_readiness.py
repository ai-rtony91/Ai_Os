from __future__ import annotations

import argparse
import json
import re
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_LOOP_READINESS.v1"

PROTECTED_ACTIONS = {
    "git_add": True,
    "git_commit": True,
    "git_push": True,
    "merge": True,
    "scheduler_activation": True,
    "daemon_activation": True,
    "worker_dispatch": True,
    "queue_mutation": True,
    "approval_mutation": True,
    "broker_live_trading": True,
    "credentials": True,
    "real_orders": True,
    "real_webhooks": True,
    "destructive_cleanup": True,
}

HARD_SAFETY_FLAGS = {
    "broker",
    "live_trading",
    "real_orders",
    "real_webhooks",
    "credentials",
    "scheduler",
    "daemon",
    "worker_dispatch",
    "queue_mutation",
    "approval_mutation",
    "delete_reset",
    "destructive_action",
}


def _base_safety() -> dict[str, bool]:
    return {
        "broker": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "credentials": False,
        "scheduler": False,
        "daemon": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "destructive_action": False,
    }


def _collect_safety(*contracts: dict[str, Any] | None) -> dict[str, bool]:
    safety = _base_safety()
    for contract in contracts:
        if not isinstance(contract, dict):
            continue
        source = contract.get("safety", contract.get("safety_summary", {}))
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if key in safety:
                safety[key] = safety[key] or bool(value)
    return safety


def _validator_pass_count(validators: list[Any]) -> int:
    count = 0
    for validator in validators:
        if not isinstance(validator, dict):
            continue
        stdout = str(validator.get("stdout", ""))
        match = re.search(r"(\d+)\s+passed", stdout)
        if match:
            count += int(match.group(1))
        elif validator.get("passed") is True:
            count += 1
    return count


def _latest_validated_chain(wake_report: dict[str, Any]) -> str:
    selected_action = str(wake_report.get("selected_action", "unknown"))
    if selected_action == "validate_all_forex_with_session_controller":
        return "forex_paper_session_controller"
    if selected_action == "validate_all_forex_with_portfolio_state":
        return "forex_portfolio_state"
    if selected_action == "validate_all_forex_with_execution_ledger_integration":
        return "forex_execution_ledger_integration"
    if selected_action == "validate_all_forex_with_risk_controls_and_execution_simulator":
        return "forex_paper_execution_simulator"
    if selected_action == "validate_all_forex_with_risk_controls":
        return "forex_risk_controls"
    if selected_action == "validate_all_forex":
        return "forex_base_chain"
    return selected_action


def _missing_capabilities(readiness_status: str, reason_code: str) -> list[str]:
    if readiness_status == "ready":
        return []
    if reason_code == "forex_session_chain_complete_review_required":
        return ["anthony_self_build_loop_review", "approved_next_non_forex_build_scope"]
    if reason_code == "wake_result_blocked":
        return ["passing_wake_validation"]
    if reason_code == "safety_blocker_present":
        return ["safety_blocker_clearance"]
    return ["human_review"]


def build_self_build_loop_readiness(wake_report: dict[str, Any] | None) -> dict[str, Any]:
    wake = wake_report if isinstance(wake_report, dict) else {}
    control = wake.get("control_plane_status") if isinstance(wake.get("control_plane_status"), dict) else {}
    continuation = wake.get("continuation_controller") if isinstance(wake.get("continuation_controller"), dict) else {}
    sos = wake.get("sos_escalation") if isinstance(wake.get("sos_escalation"), dict) else {}
    ready = wake.get("bounded_executor_ready") if isinstance(wake.get("bounded_executor_ready"), dict) else {}
    handoff = wake.get("bounded_executor_handoff") if isinstance(wake.get("bounded_executor_handoff"), dict) else {}
    plan = wake.get("next_build_plan") if isinstance(wake.get("next_build_plan"), dict) else {}

    validators = wake.get("validators_run", [])
    if not isinstance(validators, list):
        validators = []
    tests_passed_count = _validator_pass_count(validators)

    safety = _collect_safety(wake, control, continuation, sos, ready, handoff)
    safety_blocked = any(safety.get(flag) is True for flag in HARD_SAFETY_FLAGS)
    sos_required = bool(sos.get("sos_required") is True or continuation.get("sos_required") is True)
    route = str(plan.get("route", "unknown"))
    next_component = str(plan.get("next_component", "unknown"))
    wake_result = str(wake.get("result", "unknown"))
    latest_chain = _latest_validated_chain(wake)
    handoff_status = str(handoff.get("handoff_status", "unknown"))
    ready_status = str(ready.get("status", "unknown"))

    if safety_blocked or sos_required:
        readiness_status = "not_ready"
        route_status = "blocked"
        reason_code = "safety_blocker_present"
        next_action = "stop_for_sos_or_safety_review"
    elif wake_result in {"BLOCKED", "blocked", "failed", "FAILED"}:
        readiness_status = "not_ready"
        route_status = "blocked"
        reason_code = "wake_result_blocked"
        next_action = "repair_wake_continue_before_self_build"
    elif (
        latest_chain == "forex_paper_session_controller"
        and wake_result == "REVIEW_REQUIRED"
        and route == "stop"
        and next_component == "none"
    ):
        readiness_status = "review_required"
        route_status = "stopped_for_review"
        reason_code = "forex_session_chain_complete_review_required"
        next_action = "self_build_loop_readiness_review"
    elif (
        wake_result == "DONE_FOR_CURRENT_GOAL"
        and route == "build_next_paper_component"
        and handoff_status == "ready"
        and ready_status == "ready_for_human_review"
    ):
        readiness_status = "ready"
        route_status = "ready_for_bounded_self_build"
        reason_code = "bounded_next_component_ready"
        next_action = str(handoff.get("allowed_action", "review_bounded_handoff"))
    else:
        readiness_status = "review_required"
        route_status = "review_required"
        reason_code = "human_review_required"
        next_action = "self_build_loop_readiness_review"

    return {
        "schema": SCHEMA,
        "readiness_status": readiness_status,
        "current_goal": wake.get("goal", "unknown"),
        "latest_validated_chain": latest_chain,
        "tests_passed_count": tests_passed_count,
        "route_status": route_status,
        "reason_code": reason_code,
        "missing_capabilities": _missing_capabilities(readiness_status, reason_code),
        "next_allowed_self_build_action": next_action,
        "codex_packet_required": bool(continuation.get("codex_packet_required") is True),
        "local_runner_available": bool(continuation.get("local_runner_available") is True),
        "productive_executor_available": bool(continuation.get("productive_executor_available") is True),
        "sos_required": sos_required,
        "protected_actions_blocked": PROTECTED_ACTIONS.copy(),
        "safety": safety,
        "next_safe_action": (
            "Stop Forex feature expansion and review AIOS self-build loop readiness with Anthony."
            if readiness_status == "review_required"
            else "Continue only through the bounded self-build gate."
            if readiness_status == "ready"
            else "Stop and repair blockers before continuing AIOS self-build work."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate AIOS self-build loop readiness from wake JSON.")
    parser.add_argument("--status", default="{}", help="Wake/control-plane status JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(args.status)
    except json.JSONDecodeError:
        payload = {}
    print(json.dumps(build_self_build_loop_readiness(payload), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
