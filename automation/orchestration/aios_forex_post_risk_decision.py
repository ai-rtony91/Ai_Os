from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_FOREX_POST_RISK_DECISION.v1"
SUPPORTED_GOAL = "forex-paper-bot"

COMPONENT_KEYS = [
    "forex_paper_bot",
    "forex_backtest",
    "forex_paper_ledger",
    "forex_strategy_rules",
    "forex_data_import",
    "forex_report",
    "forex_decision_policy",
    "forex_risk_controls",
    "forex_paper_execution_simulator",
]


def safety_flags() -> dict[str, bool]:
    return {
        "file_writes": False,
        "network_access": False,
        "command_execution": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
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
        "scheduler_activation": True,
        "broker_live_trading": True,
        "credentials": True,
        "real_orders": True,
        "real_webhooks": True,
    }


def _normalize_inventory(component_inventory: dict[str, Any] | None) -> dict[str, bool]:
    inventory = component_inventory if isinstance(component_inventory, dict) else {}
    return {key: bool(inventory.get(key, False)) for key in COMPONENT_KEYS}


def _decision_payload(
    *,
    goal: str,
    inventory: dict[str, bool],
    selected_next_component: str,
    selected_action: str,
    selected_packet_id: str,
    reason_code: str,
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": goal,
        "current_component_state": inventory,
        "selected_next_component": selected_next_component,
        "selected_action": selected_action,
        "selected_packet_id": selected_packet_id,
        "reason_code": reason_code,
        "decision_reasons": [reason_code],
        "next_safe_action": next_safe_action,
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }


def build_post_risk_decision(
    component_inventory: dict[str, Any] | None,
    *,
    goal: str = SUPPORTED_GOAL,
) -> dict[str, Any]:
    inventory = _normalize_inventory(component_inventory)
    if not inventory["forex_risk_controls"]:
        return _decision_payload(
            goal=goal,
            inventory=inventory,
            selected_next_component="forex_risk_controls",
            selected_action="build_forex_risk_controls",
            selected_packet_id="PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY",
            reason_code="risk_controls_missing",
            next_safe_action="Prepare the bounded paper-only Forex risk controls packet for Anthony review.",
        )
    if not inventory["forex_paper_execution_simulator"]:
        return _decision_payload(
            goal=goal,
            inventory=inventory,
            selected_next_component="forex_paper_execution_simulator",
            selected_action="build_forex_paper_execution_simulator",
            selected_packet_id="PKT-AIOS-FOREX-PAPER-EXECUTION-SIMULATOR-CONTINUATION-APPLY",
            reason_code="risk_controls_validated_execution_simulator_missing",
            next_safe_action="Prepare the bounded paper execution simulator packet for Anthony review.",
        )
    return _decision_payload(
        goal=goal,
        inventory=inventory,
        selected_next_component="none",
        selected_action="none",
        selected_packet_id="NONE",
        reason_code="current_inventory_complete_for_defined_scope",
        next_safe_action="Stop for Anthony review before defining another paper-only Forex component.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the next paper-only Forex component after risk controls.")
    parser.add_argument("--risk-controls", action="store_true", help="Mark forex_risk_controls as present.")
    parser.add_argument("--execution-simulator", action="store_true", help="Mark forex_paper_execution_simulator as present.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    inventory = {key: True for key in COMPONENT_KEYS if key != "forex_paper_execution_simulator"}
    inventory["forex_risk_controls"] = bool(args.risk_controls)
    inventory["forex_paper_execution_simulator"] = bool(args.execution_simulator)
    decision = build_post_risk_decision(inventory)
    print(json.dumps(decision, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
