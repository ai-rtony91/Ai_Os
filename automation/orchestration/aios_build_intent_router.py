from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_BUILD_INTENT_ROUTER.v1"

LIVE_OR_BROKER_TERMS = (
    "live trading",
    "live trade",
    "live broker",
    "broker",
    "real order",
    "real orders",
    "credential",
    "credentials",
    "webhook",
    "webhooks",
)


def safety_flags(*, broker_live_blocked: bool = False) -> dict[str, bool]:
    return {
        "broker": broker_live_blocked,
        "live_trading": broker_live_blocked,
        "real_orders": broker_live_blocked,
        "real_webhooks": broker_live_blocked,
        "credentials": broker_live_blocked,
        "scheduler": False,
        "daemon": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "destructive_action": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def approval_required(*, human_clarification: bool = False) -> dict[str, bool]:
    return {
        "human_clarification": human_clarification,
        "commit": True,
        "push": True,
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
    }


def _goal_text(user_goal: str | None) -> str:
    return str(user_goal or "").strip().lower().replace("-", " ")


def _registry_mode_status(mode_registry: dict[str, Any], mode_id: str) -> str:
    modes = mode_registry.get("modes", {}) if isinstance(mode_registry, dict) else {}
    mode = modes.get(mode_id, {}) if isinstance(modes, dict) else {}
    return str(mode.get("implementation_status") or mode.get("status") or "unknown")


def route_build_intent(
    user_goal: str,
    resume_state: dict[str, Any] | None = None,
    control_plane_status: dict[str, Any] | None = None,
    mode_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resume = resume_state if isinstance(resume_state, dict) else {}
    status = control_plane_status if isinstance(control_plane_status, dict) else {}
    registry = mode_registry if isinstance(mode_registry, dict) else {}
    text = _goal_text(user_goal)

    if any(term in text for term in LIVE_OR_BROKER_TERMS):
        return {
            "schema": SCHEMA,
            "user_goal": user_goal,
            "detected_mode": "forex" if "forex" in text else "unknown",
            "detected_goal": "blocked",
            "proof_target": False,
            "route_status": "blocked_live_trading",
            "next_action": "Stop. Broker, credential, live trading, real order, and webhook work remains blocked.",
            "reason_code": "broker_live_or_credential_wording_detected",
            "safety": safety_flags(broker_live_blocked=True),
            "approval_required": approval_required(human_clarification=True),
        }

    if "forex" in text or "fx" in text:
        next_action = status.get("next_action") or resume.get("next_safe_action") or "Continue forex-paper-bot safely."
        return {
            "schema": SCHEMA,
            "user_goal": user_goal,
            "detected_mode": "forex",
            "detected_goal": "forex-paper-bot",
            "proof_target": True,
            "route_status": "ready_for_forex_control_plane",
            "next_action": next_action,
            "reason_code": "forex_goal_detected",
            "safety": safety_flags(),
            "approval_required": approval_required(),
        }

    if "dashboard" in text:
        return {
            "schema": SCHEMA,
            "user_goal": user_goal,
            "detected_mode": "dashboard",
            "detected_goal": "dashboard",
            "proof_target": False,
            "route_status": "reserved_until_control_plane_reader",
            "next_action": "Stop for human review before dashboard mode implementation.",
            "reason_code": _registry_mode_status(registry, "dashboard"),
            "safety": safety_flags(),
            "approval_required": approval_required(human_clarification=True),
        }

    if "game" in text:
        return {
            "schema": SCHEMA,
            "user_goal": user_goal,
            "detected_mode": "game",
            "detected_goal": "game",
            "proof_target": False,
            "route_status": "future_mode_not_enabled",
            "next_action": "Stop for human review before enabling game mode.",
            "reason_code": _registry_mode_status(registry, "game"),
            "safety": safety_flags(),
            "approval_required": approval_required(human_clarification=True),
        }

    return {
        "schema": SCHEMA,
        "user_goal": user_goal,
        "detected_mode": "unknown",
        "detected_goal": "unknown",
        "proof_target": False,
        "route_status": "needs_human_clarification",
        "next_action": "Ask Anthony to choose an enabled AIOS mode and goal.",
        "reason_code": "goal_not_mapped_to_enabled_mode",
        "safety": safety_flags(),
        "approval_required": approval_required(human_clarification=True),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview one AIOS build-intent route.")
    parser.add_argument("--goal", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    route = route_build_intent(args.goal)
    print(json.dumps(route, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
