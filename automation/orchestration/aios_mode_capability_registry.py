from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_MODE_CAPABILITY_REGISTRY.v1"

MODES = (
    "forex",
    "platform",
    "dashboard",
    "game",
    "automation",
    "security",
    "infrastructure",
)

HARD_BLOCKED_ACTIONS = [
    "live_broker_execution",
    "real_order_submission",
    "credential_use",
    "real_webhook_dispatch",
    "scheduler_activation",
    "daemon_activation",
    "worker_dispatch",
    "queue_mutation",
    "approval_mutation",
    "destructive_cleanup",
]

FOREX_ALLOWED_ACTIONS = [
    "build_forex_risk_controls",
    "build_forex_paper_execution_simulator",
]


def safety_policy(mode_id: str) -> dict[str, Any]:
    return {
        "mode_id": mode_id,
        "external_effects": "blocked",
        "human_approval_required_for_protected_actions": True,
        "broker_live_trading": "blocked",
        "credential_use": "blocked",
        "scheduler_daemon_worker_activation": "blocked",
        "queue_or_approval_mutation": "blocked",
    }


def _mode_contract(
    mode_id: str,
    *,
    label: str,
    status: str,
    allowed_actions: list[str] | None = None,
    implementation_status: str,
) -> dict[str, Any]:
    return {
        "mode_id": mode_id,
        "label": label,
        "status": status,
        "allowed_actions": list(allowed_actions or []),
        "blocked_actions": list(HARD_BLOCKED_ACTIONS),
        "safety_policy": safety_policy(mode_id),
        "implementation_status": implementation_status,
    }


def build_mode_capability_registry(
    *,
    active_mode: str = "forex",
    active_goal: str = "forex-paper-bot",
) -> dict[str, Any]:
    modes = {
        "forex": _mode_contract(
            "forex",
            label="Forex Paper Bot",
            status="active_proof_target",
            allowed_actions=FOREX_ALLOWED_ACTIONS,
            implementation_status="control_plane_ready_for_paper_components",
        ),
        "platform": _mode_contract(
            "platform",
            label="AIOS Platform",
            status="reserved",
            implementation_status="reserved_for_control_plane_expansion",
        ),
        "dashboard": _mode_contract(
            "dashboard",
            label="Dashboard",
            status="reserved",
            implementation_status="reserved_until_control_plane_reader",
        ),
        "game": _mode_contract(
            "game",
            label="Game",
            status="future",
            implementation_status="future_mode_not_enabled",
        ),
        "automation": _mode_contract(
            "automation",
            label="Automation",
            status="reserved",
            implementation_status="reserved_until_scheduler_governance_exists",
        ),
        "security": _mode_contract(
            "security",
            label="Security",
            status="future",
            implementation_status="future_mode_not_enabled",
        ),
        "infrastructure": _mode_contract(
            "infrastructure",
            label="Infrastructure",
            status="future",
            implementation_status="future_mode_not_enabled",
        ),
    }
    return {
        "schema": SCHEMA,
        "active_mode": active_mode,
        "active_goal": active_goal,
        "proof_targets": {"forex": active_goal},
        "hard_blocked_actions": list(HARD_BLOCKED_ACTIONS),
        "modes": modes,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the AIOS mode/capability registry.")
    parser.add_argument("--active-mode", default="forex")
    parser.add_argument("--active-goal", default="forex-paper-bot")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = build_mode_capability_registry(active_mode=args.active_mode, active_goal=args.active_goal)
    print(json.dumps(registry, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
