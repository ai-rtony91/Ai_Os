from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA = "AIOS_BOUNDED_EXECUTOR_READY.v1"

ACTION_ALLOWLIST = {
    "build_forex_risk_controls": {
        "paths": {
            "apps/trading_lab/trading_lab/forex_risk_controls.py",
            "tests/trading_lab/test_forex_risk_controls.py",
            "docs/orchestration/AIOS_FOREX_RISK_CONTROLS.md",
            "automation/orchestration/aios_autonomy_execute.py",
            "tests/orchestration/test_aios_autonomy_execute.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        },
        "validator_prefix": "python -m pytest -p no:cacheprovider",
    },
    "build_forex_paper_execution_simulator": {
        "paths": {
            "apps/trading_lab/trading_lab/forex_paper_execution_simulator.py",
            "tests/trading_lab/test_forex_paper_execution_simulator.py",
            "docs/orchestration/AIOS_FOREX_PAPER_EXECUTION_SIMULATOR.md",
            "automation/orchestration/aios_productive_bounded_executor.py",
            "tests/orchestration/test_aios_productive_bounded_executor.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        },
        "validator_prefix": "python -m pytest -p no:cacheprovider",
    },
    "build_forex_execution_ledger_integration": {
        "paths": {
            "apps/trading_lab/trading_lab/forex_execution_ledger_integration.py",
            "tests/trading_lab/test_forex_execution_ledger_integration.py",
            "docs/orchestration/AIOS_FOREX_EXECUTION_LEDGER_INTEGRATION.md",
            "automation/orchestration/aios_productive_bounded_executor.py",
            "tests/orchestration/test_aios_productive_bounded_executor.py",
            "automation/orchestration/aios_wake_continue.py",
            "tests/orchestration/test_aios_wake_continue.py",
        },
        "validator_prefix": "python -m pytest -p no:cacheprovider",
    },
}


def safety_flags() -> dict[str, bool]:
    return {
        "command_execution": False,
        "executed": False,
        "network_access": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "scheduler": False,
        "daemon": False,
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
        "human_review_before_local_apply": True,
        "command_execution": True,
        "commit": True,
        "push": True,
        "merge": True,
        "queue_mutation": True,
        "approval_mutation": True,
        "worker_dispatch": True,
        "scheduler_activation": True,
        "broker_live_trading": True,
    }


def _path_is_bounded(path_text: str, allowed_paths: set[str]) -> bool:
    if not path_text or "\\" in path_text:
        return False
    path = PurePosixPath(path_text)
    if path.is_absolute() or ".." in path.parts:
        return False
    return path_text in allowed_paths


def _validator_is_bounded(command: str, validator_prefix: str, allowed_paths: set[str]) -> bool:
    if not command.startswith(validator_prefix):
        return False
    if any(token in command for token in (";", "&&", "||", "|", ">", "<")):
        return False
    referenced_paths = [part for part in command.split() if part.endswith(".py")]
    return bool(referenced_paths) and all(_path_is_bounded(path, allowed_paths) for path in referenced_paths)


def build_bounded_executor_ready(bounded_executor_handoff: dict[str, Any] | None) -> dict[str, Any]:
    handoff = bounded_executor_handoff if isinstance(bounded_executor_handoff, dict) else {}
    allowed_action = str(handoff.get("allowed_action", "none"))
    handoff_status = str(handoff.get("handoff_status", "blocked"))
    action_contract = ACTION_ALLOWLIST.get(allowed_action)

    allowed_paths = handoff.get("allowed_paths", [])
    validators = handoff.get("validators", [])
    if not isinstance(allowed_paths, list):
        allowed_paths = []
    if not isinstance(validators, list):
        validators = []
    allowed_paths_text = [str(path) for path in allowed_paths]
    validators_text = [str(command) for command in validators]

    if handoff_status != "ready":
        status = "not_ready"
        reason_code = f"handoff_{handoff_status}"
        allowed_paths_bounded = False
        validators_bounded = False
    elif action_contract is None:
        status = "blocked"
        reason_code = "allowed_action_not_allowlisted"
        allowed_paths_bounded = False
        validators_bounded = False
    else:
        allowed_set = action_contract["paths"]
        allowed_paths_bounded = bool(allowed_paths_text) and all(
            _path_is_bounded(path, allowed_set) for path in allowed_paths_text
        )
        validators_bounded = bool(validators_text) and all(
            _validator_is_bounded(command, action_contract["validator_prefix"], allowed_set)
            for command in validators_text
        )
        if allowed_paths_bounded and validators_bounded:
            status = "ready_for_human_review"
            reason_code = "bounded_handoff_ready"
        else:
            status = "blocked"
            reason_code = "handoff_scope_not_bounded"

    return {
        "schema": SCHEMA,
        "input_schema": handoff.get("schema", "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1"),
        "status": status,
        "reason_code": reason_code,
        "allowed_action": allowed_action,
        "allowed_paths": allowed_paths_text,
        "allowed_paths_bounded": allowed_paths_bounded,
        "validators": validators_text,
        "validators_bounded": validators_bounded,
        "command_execution": False,
        "executed": False,
        "commit_push_merge_human_approved_only": True,
        "approval_required": approval_required(),
        "safety": safety_flags(),
        "next_safe_action": (
            "Prepare/apply the bounded risk controls packet only after Anthony approval."
            if status == "ready_for_human_review" and allowed_action == "build_forex_risk_controls"
            else "Prepare/apply the bounded paper execution simulator packet only after Anthony approval."
            if status == "ready_for_human_review" and allowed_action == "build_forex_paper_execution_simulator"
            else "Prepare/apply the bounded execution-ledger integration packet only after Anthony approval."
            if status == "ready_for_human_review" and allowed_action == "build_forex_execution_ledger_integration"
            else "Stop and repair bounded executor readiness before execution."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a bounded executor handoff for readiness only.")
    parser.add_argument("--action", default="build_forex_risk_controls", help="Allowed action preview.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ready = build_bounded_executor_ready({"handoff_status": "ready", "allowed_action": args.action})
    print(json.dumps(ready, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
