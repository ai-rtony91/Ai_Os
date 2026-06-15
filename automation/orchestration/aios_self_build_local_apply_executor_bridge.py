from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.v1"
WORKING_DIRECTORY = "C:\\Dev\\Ai.Os"
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
    "commands_executed",
    "command_execution",
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
        "bridge_only": True,
        "commands_executed": False,
        "command_to_run_executed": False,
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


def _normalize_paths(paths: Any) -> list[str]:
    output: list[str] = []
    for path in _as_list(paths):
        path_text = str(path)
        parsed = PurePosixPath(path_text)
        if path_text and "\\" not in path_text and not parsed.is_absolute() and ".." not in parsed.parts:
            output.append(path_text)
    return output


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


def _first_command(local_apply_preview: dict[str, Any]) -> str:
    command_preview = local_apply_preview.get("command_preview", [])
    if isinstance(command_preview, list) and command_preview:
        return str(command_preview[0])
    if isinstance(command_preview, str):
        return command_preview
    return ""


def _selected_action(queue_item: dict[str, Any], core_status: dict[str, Any]) -> str:
    core_action = str(core_status.get("selected_next_action", "") or "")
    if core_action and core_action != "none":
        return core_action
    return str(queue_item.get("action_id", "none"))


def build_self_build_local_apply_executor_bridge(
    selected_queue_item: dict[str, Any] | None = None,
    local_apply_preview: dict[str, Any] | None = None,
    apply_approval: dict[str, Any] | None = None,
    core_status: dict[str, Any] | None = None,
    stop_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_item = _as_dict(selected_queue_item)
    local_preview = _as_dict(local_apply_preview)
    approval = _as_dict(apply_approval)
    core = _as_dict(core_status)
    stop = _as_dict(stop_report)

    queue_action = str(queue_item.get("action_id", "none"))
    selected_action = _selected_action(queue_item, core)
    allowed_paths = _normalize_paths(queue_item.get("allowed_paths", []))
    preview_paths = _normalize_paths(local_preview.get("allowed_paths", allowed_paths))
    validators = [str(validator) for validator in queue_item.get("validators", []) if str(validator)]
    if not validators:
        validators = [str(validator) for validator in local_preview.get("validators", []) if str(validator)]
    command_to_run = _first_command(local_preview)
    safety = _collect_safety(queue_item, local_preview, approval, core, stop)

    rejection_reasons: list[str] = []
    block_reasons: list[str] = []
    if selected_action != queue_action:
        rejection_reasons.append("selected_action_mismatch")
    if not allowed_paths or set(preview_paths) - set(allowed_paths):
        rejection_reasons.append("requested_paths_outside_allowed_paths")
    if not validators:
        rejection_reasons.append("validators_missing")
    if safety["protected_action_requested"]:
        rejection_reasons.append("protected_action_requested")
    if not command_to_run:
        rejection_reasons.append("command_preview_missing")

    approval_status = str(approval.get("approval_status", "review_required"))
    local_allowlisted_apply_allowed = bool(approval.get("local_allowlisted_apply_allowed") is True)
    if approval_status != "approved":
        block_reasons.append("apply_approval_not_approved")
    if not local_allowlisted_apply_allowed:
        block_reasons.append("local_allowlisted_apply_not_allowed")
    if safety["sandbox_1312_blocker"]:
        block_reasons.append("sandbox_1312_runner_blocker")

    if rejection_reasons:
        bridge_status = "rejected"
    elif block_reasons:
        bridge_status = "blocked"
    else:
        bridge_status = "ready"

    if bridge_status == "ready":
        next_safe_action = "Bridge is ready. Review command_to_run; v1 still does not execute it."
    elif safety["sandbox_1312_blocker"]:
        next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
    elif bridge_status == "blocked":
        next_safe_action = "Stop until Anthony approval and local allowlisted APPLY conditions are satisfied."
    else:
        next_safe_action = "Stop and repair the rejected bridge inputs before preparing local APPLY."

    return {
        "schema": SCHEMA,
        "bridge_status": bridge_status,
        "selected_action": selected_action,
        "working_directory": str(local_preview.get("working_directory", WORKING_DIRECTORY) or WORKING_DIRECTORY),
        "command_to_run": command_to_run,
        "allowed_paths": allowed_paths,
        "validators": validators,
        "max_repairs": int(local_preview.get("max_repairs", 1) or 1),
        "max_files_changed": int(local_preview.get("max_files_changed", len(allowed_paths) or 1) or 1),
        "approval_status": approval_status,
        "local_allowlisted_apply_allowed": local_allowlisted_apply_allowed,
        "execution_status": "prepared_not_executed",
        "rejection_reasons": rejection_reasons or block_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
    }


build_local_apply_executor_bridge = build_self_build_local_apply_executor_bridge
prepare_self_build_local_apply = build_self_build_local_apply_executor_bridge


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare an AIOS self-build local APPLY bridge preview.")
    parser.add_argument("--queue-item", default="{}")
    parser.add_argument("--local-apply-preview", default="{}")
    parser.add_argument("--apply-approval", default="{}")
    parser.add_argument("--core-status", default="{}")
    parser.add_argument("--stop-report", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        queue_item = json.loads(args.queue_item)
        local_preview = json.loads(args.local_apply_preview)
        approval = json.loads(args.apply_approval)
        core = json.loads(args.core_status)
        stop = json.loads(args.stop_report)
    except json.JSONDecodeError:
        queue_item = {}
        local_preview = {}
        approval = {}
        core = {}
        stop = {}
    print(
        json.dumps(
            build_self_build_local_apply_executor_bridge(
                queue_item,
                local_preview,
                approval,
                core,
                stop,
            ),
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
