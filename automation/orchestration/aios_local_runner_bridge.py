from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_LOCAL_RUNNER_BRIDGE.v1"
REPO_ROOT_TEXT = r"C:\Dev\Ai.Os"
SUPPORTED_ACTIONS = {"build_forex_risk_controls"}


def safety_flags() -> dict[str, bool]:
    return {
        "command_execution": False,
        "scheduler": False,
        "daemon": False,
        "background_task": False,
        "network_access": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "broker": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "credentials": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def approval_required() -> dict[str, bool]:
    return {
        "human_review_before_execution": True,
        "local_apply": True,
        "commit": True,
        "push": True,
        "merge": True,
        "scheduler_activation": True,
        "worker_dispatch": True,
        "broker_live_trading": True,
    }


def _validation_commands(handoff: dict[str, Any]) -> list[str]:
    validators = handoff.get("validators", [])
    if not isinstance(validators, list):
        return []
    return [str(item) for item in validators]


def build_local_runner_bridge(bounded_executor_handoff: dict[str, Any] | None) -> dict[str, Any]:
    handoff = bounded_executor_handoff if isinstance(bounded_executor_handoff, dict) else {}
    allowed_action = str(handoff.get("allowed_action", "none"))
    handoff_status = str(handoff.get("handoff_status", "blocked"))
    validation_commands = _validation_commands(handoff)

    if handoff_status == "ready" and allowed_action in SUPPORTED_ACTIONS:
        runner_status = "preview_ready"
        command_preview = [
            f"Set-Location -LiteralPath '{REPO_ROOT_TEXT}'",
            *validation_commands,
        ]
    elif handoff_status == "stopped":
        runner_status = "stopped_for_human_review"
        command_preview = []
    else:
        runner_status = "blocked"
        command_preview = []

    return {
        "schema": SCHEMA,
        "runner_status": runner_status,
        "command_preview": command_preview,
        "working_directory": REPO_ROOT_TEXT,
        "validation_commands": validation_commands,
        "forbidden_actions": [
            "command_execution",
            "scheduler_activation",
            "daemon_activation",
            "background_runtime",
            "queue_mutation",
            "approval_mutation",
            "worker_dispatch",
            "codex_launch",
            "chatgpt_api_call",
            "broker_execution",
            "live_trading",
            "real_orders",
            "real_webhooks",
            "credentials",
            "git_add",
            "git_commit",
            "git_push",
            "git_merge",
        ],
        "approval_required": approval_required(),
        "safety": safety_flags(),
        "next_safe_action": handoff.get(
            "next_safe_action",
            "Review the local runner preview. Do not execute commands from this bridge automatically.",
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a PowerShell local-runner bridge contract.")
    parser.add_argument("--action", default="build_forex_risk_controls", help="Allowed action preview.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bridge = build_local_runner_bridge(
        {
            "handoff_status": "ready",
            "allowed_action": args.action,
            "validators": [
                "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_wake_continue.py",
            ],
        }
    )
    print(json.dumps(bridge, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
