from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_SINGLE_ACTION_EXECUTOR.v1"
SANDBOX_1312_MARKER = "createprocessasuserw failed: 1312"

PROTECTED_REQUEST_KEYS = {
    "git_add",
    "git_commit",
    "git_push",
    "merge",
    "scheduler",
    "scheduler_activation",
    "daemon",
    "daemon_activation",
    "worker_dispatch",
    "queue_mutation",
    "approval_mutation",
    "broker",
    "broker_order",
    "broker_live_trading",
    "live_trading",
    "live_execution",
    "credentials",
    "credential_use",
    "real_orders",
    "real_order",
    "real_webhooks",
    "webhook_url",
    "destructive_cleanup",
    "destructive_action",
    "background_runtime",
    "network",
    "network_access",
    "codex_launch",
    "chatgpt_api_call",
}

PROTECTED_ATTEMPT_KEYS = {
    "git_add_requested",
    "git_commit_requested",
    "git_push_requested",
    "merge_requested",
    "scheduler_activation_requested",
    "daemon_activation_requested",
    "worker_dispatch_requested",
    "queue_mutation_requested",
    "approval_mutation_requested",
    "broker_live_trading_requested",
    "credentials_requested",
    "real_orders_requested",
    "real_webhooks_requested",
    "destructive_cleanup_requested",
    "background_runtime_requested",
    "network_access_requested",
    "codex_launch_requested",
    "chatgpt_api_call_requested",
}


def _base_safety() -> dict[str, bool]:
    return {
        "executor_only": True,
        "command_executed": False,
        "commands_executed": False,
        "files_written": False,
        "reports_written": False,
        "network_access": False,
        "codex_launch": False,
        "chatgpt_api_call": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
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
        "background_runtime": False,
        "protected_action_requested": False,
        "sandbox_1312_blocker": False,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _bounded_path(path_text: str) -> bool:
    parsed = PurePosixPath(path_text)
    return bool(path_text) and "\\" not in path_text and not parsed.is_absolute() and ".." not in parsed.parts


def _normalize_paths(paths: Any) -> list[str]:
    return [str(path) for path in _as_list(paths) if _bounded_path(str(path))]


def _iter_items(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str, Any]]:
    output: list[tuple[tuple[str, ...], str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            output.append((path, key_text, child))
            output.extend(_iter_items(child, (*path, key_text)))
    elif isinstance(value, list):
        for child in value:
            output.extend(_iter_items(child, path))
    return output


def _payload_text(*payloads: dict[str, Any]) -> str:
    return " ".join(json.dumps(payload, sort_keys=True).lower() for payload in payloads if payload)


def _protected_requested(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for path, raw_key, value in _iter_items(payload):
            path_lower = {part.lower() for part in path}
            if "protected_actions_blocked" in path_lower or "approval_required" in path_lower:
                continue
            key = raw_key.lower()
            if isinstance(value, dict) and key == "protected_action_flags":
                if any(bool(flag_value) for flag_value in value.values()):
                    return True
            if value is True and (key in PROTECTED_REQUEST_KEYS or key in PROTECTED_ATTEMPT_KEYS):
                return True
    return False


def _collect_safety(*payloads: dict[str, Any]) -> dict[str, bool]:
    safety = _base_safety()
    if SANDBOX_1312_MARKER in _payload_text(*payloads):
        safety["sandbox_1312_blocker"] = True
    if _protected_requested(*payloads):
        safety["protected_action_requested"] = True
    return safety


def _selected_action(queue_item: dict[str, Any], bridge: dict[str, Any], core: dict[str, Any]) -> str:
    bridge_action = str(bridge.get("selected_action", "") or "")
    if bridge_action and bridge_action != "none":
        return bridge_action
    core_action = str(core.get("selected_next_action", "") or "")
    if core_action and core_action != "none":
        return core_action
    return str(queue_item.get("action_id", "none"))


def build_self_build_single_action_executor(
    selected_queue_item: dict[str, Any] | None = None,
    apply_approval: dict[str, Any] | None = None,
    local_apply_executor_bridge: dict[str, Any] | None = None,
    core_status: dict[str, Any] | None = None,
    stop_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_item = _as_dict(selected_queue_item)
    approval = _as_dict(apply_approval)
    bridge = _as_dict(local_apply_executor_bridge)
    core = _as_dict(core_status)
    stop = _as_dict(stop_report)

    queue_action = str(queue_item.get("action_id", "none"))
    selected_action = _selected_action(queue_item, bridge, core)
    command_to_run = str(bridge.get("command_to_run", ""))
    queue_paths_raw = [str(path) for path in _as_list(queue_item.get("allowed_paths", []))]
    bridge_paths_raw = [str(path) for path in _as_list(bridge.get("allowed_paths", queue_paths_raw))]
    allowed_paths = _normalize_paths(queue_paths_raw)
    bridge_paths = _normalize_paths(bridge_paths_raw)
    validators = [str(validator) for validator in queue_item.get("validators", []) if str(validator)]
    if not validators:
        validators = [str(validator) for validator in bridge.get("validators", []) if str(validator)]
    max_repairs = int(bridge.get("max_repairs", 1) or 1)
    max_files_changed = int(bridge.get("max_files_changed", len(allowed_paths) or 1) or 1)
    approval_status = str(approval.get("approval_status", "review_required"))
    bridge_status = str(bridge.get("bridge_status", "blocked"))
    safety = _collect_safety(queue_item, approval, bridge, core, stop)

    rejection_reasons: list[str] = []
    block_reasons: list[str] = []
    if selected_action != queue_action:
        rejection_reasons.append("selected_action_mismatch")
    if not allowed_paths or len(allowed_paths) != len(queue_paths_raw):
        rejection_reasons.append("allowed_paths_unbounded_or_missing")
    if set(bridge_paths) - set(allowed_paths) or len(bridge_paths) != len(bridge_paths_raw):
        rejection_reasons.append("requested_paths_outside_allowed_scope")
    if not validators:
        rejection_reasons.append("validators_missing")
    if safety["protected_action_requested"]:
        rejection_reasons.append("protected_action_requested")
    if approval_status != "approved":
        block_reasons.append("apply_approval_not_approved")
    if bridge_status != "ready":
        block_reasons.append("local_apply_bridge_not_ready")
    if safety["sandbox_1312_blocker"]:
        block_reasons.append("sandbox_1312_runner_blocker")

    command_would_run = bool(
        not rejection_reasons
        and not block_reasons
        and approval_status == "approved"
        and bridge_status == "ready"
        and command_to_run
    )

    if rejection_reasons:
        executor_status = "rejected"
    elif block_reasons:
        executor_status = "blocked"
    else:
        executor_status = "ready"

    if command_would_run:
        execution_mode = "APPLY_ALLOWED_NOT_RUN"
        next_safe_action = "Single-action executor is ready. v1 reports command_would_run only; it does not execute."
    elif command_to_run:
        execution_mode = "APPLY_PREVIEW"
        if safety["sandbox_1312_blocker"]:
            next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
        else:
            next_safe_action = "Stop until approval and bridge readiness are both safe."
    else:
        execution_mode = "DRY_RUN"
        next_safe_action = "Stop until a bounded command preview is available."

    return {
        "schema": SCHEMA,
        "executor_status": executor_status,
        "execution_mode": execution_mode,
        "selected_action": selected_action,
        "command_to_run": command_to_run,
        "command_would_run": command_would_run,
        "command_executed": False,
        "allowed_paths": allowed_paths,
        "validators": validators,
        "max_repairs": max_repairs,
        "max_files_changed": max_files_changed,
        "approval_status": approval_status,
        "bridge_status": bridge_status,
        "rejection_reasons": rejection_reasons or block_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
    }


build_single_action_executor = build_self_build_single_action_executor
evaluate_self_build_single_action_executor = build_self_build_single_action_executor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate one approved AIOS self-build action without executing it.")
    parser.add_argument("--queue-item", default="{}")
    parser.add_argument("--apply-approval", default="{}")
    parser.add_argument("--local-apply-executor-bridge", default="{}")
    parser.add_argument("--core-status", default="{}")
    parser.add_argument("--stop-report", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        queue_item = json.loads(args.queue_item)
        approval = json.loads(args.apply_approval)
        bridge = json.loads(args.local_apply_executor_bridge)
        core = json.loads(args.core_status)
        stop = json.loads(args.stop_report)
    except json.JSONDecodeError:
        queue_item = {}
        approval = {}
        bridge = {}
        core = {}
        stop = {}
    print(
        json.dumps(
            build_self_build_single_action_executor(queue_item, approval, bridge, core, stop),
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
