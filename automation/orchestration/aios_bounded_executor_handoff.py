from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1"
INPUT_SCHEMA = "AIOS_NEXT_BUILD_PLAN.v1"

FOREX_RISK_CONTROLS_ALLOWED_PATHS = [
    "apps/trading_lab/trading_lab/forex_risk_controls.py",
    "tests/trading_lab/test_forex_risk_controls.py",
    "docs/orchestration/AIOS_FOREX_RISK_CONTROLS.md",
    "automation/orchestration/aios_autonomy_execute.py",
    "tests/orchestration/test_aios_autonomy_execute.py",
    "automation/orchestration/aios_wake_continue.py",
    "tests/orchestration/test_aios_wake_continue.py",
]

FOREX_PAPER_EXECUTION_SIMULATOR_ALLOWED_PATHS = [
    "apps/trading_lab/trading_lab/forex_paper_execution_simulator.py",
    "tests/trading_lab/test_forex_paper_execution_simulator.py",
    "docs/orchestration/AIOS_FOREX_PAPER_EXECUTION_SIMULATOR.md",
    "automation/orchestration/aios_productive_bounded_executor.py",
    "tests/orchestration/test_aios_productive_bounded_executor.py",
    "automation/orchestration/aios_wake_continue.py",
    "tests/orchestration/test_aios_wake_continue.py",
]

STRATEGY_REVIEW_ALLOWED_PATHS = [
    "apps/trading_lab/trading_lab/forex_strategy_rules.py",
    "tests/trading_lab/test_forex_strategy_rules.py",
    "docs/orchestration/AIOS_FOREX_STRATEGY_RULES.md",
]

DATA_QUALITY_REVIEW_ALLOWED_PATHS = [
    "apps/trading_lab/trading_lab/forex_data_import.py",
    "tests/trading_lab/test_forex_data_import.py",
    "docs/orchestration/AIOS_FOREX_DATA_IMPORT.md",
]

FOREX_RISK_CONTROLS_VALIDATORS = [
    "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_autonomy_execute.py tests/orchestration/test_aios_wake_continue.py tests/trading_lab/test_forex_risk_controls.py",
]

FOREX_PAPER_EXECUTION_SIMULATOR_VALIDATORS = [
    "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_productive_bounded_executor.py tests/orchestration/test_aios_wake_continue.py tests/trading_lab/test_forex_paper_execution_simulator.py",
]

STRATEGY_REVIEW_VALIDATORS = [
    "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_strategy_rules.py",
]

DATA_QUALITY_REVIEW_VALIDATORS = [
    "python -m pytest -p no:cacheprovider tests/trading_lab/test_forex_data_import.py",
]


def safety_flags() -> dict[str, bool]:
    return {
        "command_execution": False,
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
        "human_review_before_local_apply": True,
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


def _ready_handoff(
    next_build_plan: dict[str, Any],
    *,
    allowed_action: str,
    allowed_paths: list[str],
    validators: list[str],
) -> dict[str, Any]:
    next_component = str(next_build_plan.get("next_component", "none"))
    command_preview = [
        f"Review bounded APPLY packet for {allowed_action}.",
        *validators,
    ]
    next_safe_action = (
        "Prepare bounded paper execution simulator packet for Anthony review. "
        "Do not execute, stage, commit, push, or dispatch from this handoff."
        if allowed_action == "build_forex_paper_execution_simulator"
        else (
            f"Prepare the {allowed_action} APPLY packet for Anthony review. "
            "Do not execute, stage, commit, push, or dispatch from this handoff."
        )
    )
    return {
        "schema": SCHEMA,
        "goal": next_build_plan.get("goal", "forex-paper-bot"),
        "input_route": next_build_plan.get("route", "unknown"),
        "next_component": next_component,
        "next_packet_id": next_build_plan.get("next_packet_id", "NONE"),
        "handoff_status": "ready",
        "executor_mode": "local_apply_after_human_review",
        "allowed_action": allowed_action,
        "allowed_paths": allowed_paths,
        "validators": validators,
        "command_preview": command_preview,
        "approval_required": approval_required(),
        "safety": safety_flags(),
        "next_safe_action": next_safe_action,
    }


def _stopped_handoff(next_build_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": next_build_plan.get("goal", "forex-paper-bot"),
        "input_route": next_build_plan.get("route", "stop"),
        "next_component": "none",
        "next_packet_id": next_build_plan.get("next_packet_id", "NONE"),
        "handoff_status": "stopped",
        "executor_mode": "none",
        "allowed_action": "none",
        "allowed_paths": [],
        "validators": [],
        "command_preview": [],
        "approval_required": approval_required(),
        "safety": safety_flags(),
        "next_safe_action": "Stop for Anthony review before preparing another bounded executor handoff.",
    }


def _blocked_handoff(next_build_plan: dict[str, Any], reason_code: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": next_build_plan.get("goal", "forex-paper-bot"),
        "input_route": next_build_plan.get("route", "unknown"),
        "next_component": next_build_plan.get("next_component", "unknown"),
        "next_packet_id": next_build_plan.get("next_packet_id", "NONE"),
        "handoff_status": "blocked",
        "reason_code": reason_code,
        "executor_mode": "none",
        "allowed_action": "none",
        "allowed_paths": [],
        "validators": [],
        "command_preview": [],
        "approval_required": approval_required(),
        "safety": safety_flags(),
        "next_safe_action": "Stop and repair the unsupported next build plan before handoff.",
    }


def build_bounded_executor_handoff(next_build_plan: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(next_build_plan, dict):
        return _blocked_handoff({}, "invalid_next_build_plan")

    route = next_build_plan.get("route")
    next_component = next_build_plan.get("next_component")

    if route == "stop" or next_component == "none":
        return _stopped_handoff(next_build_plan)

    if next_component == "forex_risk_controls":
        return _ready_handoff(
            next_build_plan,
            allowed_action="build_forex_risk_controls",
            allowed_paths=FOREX_RISK_CONTROLS_ALLOWED_PATHS,
            validators=FOREX_RISK_CONTROLS_VALIDATORS,
        )
    if next_component == "forex_paper_execution_simulator":
        return _ready_handoff(
            next_build_plan,
            allowed_action="build_forex_paper_execution_simulator",
            allowed_paths=FOREX_PAPER_EXECUTION_SIMULATOR_ALLOWED_PATHS,
            validators=FOREX_PAPER_EXECUTION_SIMULATOR_VALIDATORS,
        )
    if next_component == "forex_strategy_rules_review":
        return _ready_handoff(
            next_build_plan,
            allowed_action="review_forex_strategy_rules",
            allowed_paths=STRATEGY_REVIEW_ALLOWED_PATHS,
            validators=STRATEGY_REVIEW_VALIDATORS,
        )
    if next_component == "forex_data_quality_review":
        return _ready_handoff(
            next_build_plan,
            allowed_action="review_forex_data_quality",
            allowed_paths=DATA_QUALITY_REVIEW_ALLOWED_PATHS,
            validators=DATA_QUALITY_REVIEW_VALIDATORS,
        )
    return _blocked_handoff(next_build_plan, "unsupported_component")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview one bounded AIOS executor handoff contract.")
    parser.add_argument("--component", default="forex_risk_controls", help="Next component to preview.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handoff = build_bounded_executor_handoff(
        {
            "schema": INPUT_SCHEMA,
            "goal": "forex-paper-bot",
            "route": "build_next_paper_component",
            "next_component": args.component,
            "next_packet_id": "PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY",
        }
    )
    print(json.dumps(handoff, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
