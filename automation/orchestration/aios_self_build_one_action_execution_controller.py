from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_CONTROLLER.v1"
ONE_ACTION_APPLY_MODE = "ONE_ACTION_APPLY"
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
    "command_execution",
    "commands_executed",
    "command_executed",
    "protected_action_requested",
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

REQUIRED_PRE_EXECUTION_CHECKS = [
    "execution_request.requested_true",
    "execution_request.mode_ONE_ACTION_APPLY",
    "apply_approval.approval_status_approved",
    "local_apply_executor_bridge.bridge_status_ready",
    "single_action_executor.executor_status_ready",
    "single_action_executor.command_would_run_true",
    "selected_action_matches_queue_approval_bridge_executor",
    "allowed_paths_bounded",
    "validators_present",
    "protected_actions_blocked",
    "core_status.can_apply_without_human_false",
    "apply_result_verifier.pre_execution_ready_or_passed",
]


def _base_safety() -> dict[str, bool]:
    return {
        "controller_only": True,
        "decision_only": True,
        "command_execution_allowed_by_controller": False,
        "command_executed": False,
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


def _bounded_path(path_text: str) -> bool:
    parsed = PurePosixPath(path_text)
    return bool(path_text) and "\\" not in path_text and not parsed.is_absolute() and ".." not in parsed.parts


def _normalize_paths(paths: Any) -> list[str]:
    return [str(path) for path in _as_list(paths) if _bounded_path(str(path))]


def _dedupe(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def _append_once(values: list[str], reason: str) -> None:
    if reason not in values:
        values.append(reason)


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


def _payload_text(*payloads: Any) -> str:
    return " ".join(json.dumps(payload, sort_keys=True).lower() for payload in payloads if payload is not None)


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


def _first_action(*values: Any) -> str:
    for value in values:
        action = str(value or "")
        if action and action != "none":
            return action
    return "none"


def _validators(*payloads: dict[str, Any]) -> list[str]:
    for payload in payloads:
        validators = [str(validator) for validator in _as_list(payload.get("validators", [])) if str(validator)]
        if validators:
            return validators
    return []


def _first_int(*values: Any, default: int) -> int:
    for value in values:
        if value in (None, ""):
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return default


def _path_values(payload: dict[str, Any], *keys: str) -> list[str]:
    output: list[str] = []
    for key in keys:
        output.extend(str(path) for path in _as_list(payload.get(key, [])))
    return output


def _path_rejection_reasons(allowed_paths: list[str], *path_groups: list[str]) -> list[str]:
    reasons: list[str] = []
    allowed = set(allowed_paths)
    if not allowed_paths:
        _append_once(reasons, "allowed_paths_unbounded_or_missing")
    for raw_paths in path_groups:
        if not raw_paths:
            continue
        normalized = _normalize_paths(raw_paths)
        if len(normalized) != len(raw_paths) or set(normalized) - allowed:
            _append_once(reasons, "requested_paths_outside_allowed_paths")
    return reasons


def _action_alignment_reasons(
    queue_item: dict[str, Any],
    approval: dict[str, Any],
    bridge: dict[str, Any],
    executor: dict[str, Any],
    core: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    queue_action = _first_action(queue_item.get("action_id"))
    approval_actions = [
        action
        for action in (
            _first_action(approval.get("requested_action")),
            _first_action(approval.get("selected_queue_action")),
            _first_action(approval.get("action_id")),
        )
        if action != "none"
    ]
    bridge_action = _first_action(bridge.get("selected_action"))
    executor_action = _first_action(executor.get("selected_action"))
    core_action = _first_action(core.get("selected_next_action"))

    if queue_action == "none":
        _append_once(reasons, "selected_action_missing")
    if not approval_actions:
        _append_once(reasons, "selected_action_mismatch")
    elif any(action != queue_action for action in approval_actions):
        _append_once(reasons, "selected_action_mismatch")
    if bridge_action == "none" or bridge_action != queue_action:
        _append_once(reasons, "selected_action_mismatch")
    if executor_action == "none" or executor_action != queue_action:
        _append_once(reasons, "selected_action_mismatch")
    if core_action != "none" and core_action != queue_action:
        _append_once(reasons, "selected_action_mismatch")
    return reasons


def _verifier_gate_reasons(verifier: dict[str, Any]) -> tuple[list[str], list[str]]:
    block_reasons: list[str] = []
    rejection_reasons: list[str] = []
    if not verifier:
        block_reasons.append("apply_result_verifier_missing")
        return block_reasons, rejection_reasons

    verifier_status = str(verifier.get("verifier_status", "blocked"))
    verifier_reasons = [str(reason) for reason in _as_list(verifier.get("rejection_reasons", []))]
    if verifier_status == "blocked":
        if len(verifier_reasons) == 1 and verifier_reasons[0] == "command_not_executed":
            return block_reasons, rejection_reasons
        block_reasons.append("apply_result_verifier_blocked")
    elif verifier_status in {"failed", "rejected"}:
        rejection_reasons.append(f"apply_result_verifier_{verifier_status}")
    elif verifier_status not in {"passed", "ready"}:
        block_reasons.append("apply_result_verifier_unknown_status")
    return block_reasons, rejection_reasons


def build_self_build_one_action_execution_controller(
    selected_queue_item: dict[str, Any] | None = None,
    apply_approval: dict[str, Any] | None = None,
    local_apply_executor_bridge: dict[str, Any] | None = None,
    single_action_executor: dict[str, Any] | None = None,
    apply_result_verifier: dict[str, Any] | None = None,
    core_status: dict[str, Any] | None = None,
    stop_report: dict[str, Any] | None = None,
    execution_request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_item = _as_dict(selected_queue_item)
    approval = _as_dict(apply_approval)
    bridge = _as_dict(local_apply_executor_bridge)
    executor = _as_dict(single_action_executor)
    verifier = _as_dict(apply_result_verifier)
    core = _as_dict(core_status)
    stop = _as_dict(stop_report)
    request = _as_dict(execution_request)

    selected_action = _first_action(
        executor.get("selected_action"),
        bridge.get("selected_action"),
        approval.get("selected_queue_action"),
        approval.get("requested_action"),
        core.get("selected_next_action"),
        queue_item.get("action_id"),
    )
    command_to_run = str(executor.get("command_to_run") or bridge.get("command_to_run") or request.get("command_to_run") or "")
    allowed_paths_raw = [str(path) for path in _as_list(queue_item.get("allowed_paths", []))]
    allowed_paths = _normalize_paths(allowed_paths_raw)
    validators = _validators(queue_item, bridge, executor)
    max_repairs = _first_int(executor.get("max_repairs"), bridge.get("max_repairs"), queue_item.get("max_repairs"), default=1)
    max_files_changed = _first_int(
        executor.get("max_files_changed"),
        bridge.get("max_files_changed"),
        verifier.get("max_files_changed"),
        queue_item.get("max_files_changed"),
        default=len(allowed_paths) or 1,
    )
    approval_status = str(approval.get("approval_status", "review_required"))
    bridge_status = str(bridge.get("bridge_status", "blocked"))
    executor_status = str(executor.get("executor_status", "blocked"))
    verifier_status = str(verifier.get("verifier_status", "blocked"))
    safety = _collect_safety(queue_item, approval, bridge, executor, verifier, core, stop, request)

    rejection_reasons: list[str] = []
    block_reasons: list[str] = []

    request_missing = not request
    if request_missing:
        block_reasons.append("execution_request_missing")
    else:
        if request.get("requested") is not True:
            block_reasons.append("execution_request_not_requested")
        if str(request.get("mode", "")) != ONE_ACTION_APPLY_MODE:
            block_reasons.append("execution_request_mode_not_one_action_apply")

    if approval_status != "approved":
        block_reasons.append("apply_approval_not_approved")
    if bridge_status != "ready":
        block_reasons.append("local_apply_bridge_not_ready")
    if executor_status != "ready":
        block_reasons.append("single_action_executor_not_ready")
    if executor.get("command_would_run") is not True:
        block_reasons.append("command_would_run_false")
    if not command_to_run:
        block_reasons.append("command_to_run_missing")
    if safety["sandbox_1312_blocker"]:
        block_reasons.append("sandbox_1312_runner_blocker")

    if not request_missing:
        rejection_reasons.extend(_action_alignment_reasons(queue_item, approval, bridge, executor, core))
        rejection_reasons.extend(
            _path_rejection_reasons(
                allowed_paths,
                allowed_paths_raw,
                _path_values(approval, "requested_write_paths", "write_paths", "allowed_paths"),
                _path_values(bridge, "allowed_paths"),
                _path_values(executor, "allowed_paths"),
                _path_values(verifier, "allowed_paths", "changed_files", "unexpected_files"),
                _path_values(request, "requested_write_paths", "write_paths", "allowed_paths", "paths"),
            )
        )
        if not validators:
            rejection_reasons.append("validators_missing")
    if safety["protected_action_requested"]:
        rejection_reasons.append("protected_action_requested")
    if core.get("can_apply_without_human") is True:
        rejection_reasons.append("core_apply_without_human_not_allowed")

    if not request_missing:
        verifier_blocks, verifier_rejections = _verifier_gate_reasons(verifier)
        block_reasons.extend(verifier_blocks)
        rejection_reasons.extend(verifier_rejections)

    rejection_reasons = _dedupe(rejection_reasons)
    block_reasons = _dedupe(block_reasons)
    if rejection_reasons:
        controller_status = "rejected"
        execution_decision = "rejected"
        next_safe_action = "Stop and repair rejected controller inputs before any one-action APPLY."
    elif block_reasons:
        controller_status = "blocked"
        execution_decision = "blocked"
        if safety["sandbox_1312_blocker"]:
            next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
        else:
            next_safe_action = "Stop until execution request, approval, bridge, executor, and verifier readiness are satisfied."
    else:
        controller_status = "ready"
        execution_decision = "execute_one_action_allowed"
        next_safe_action = "One-action APPLY is execution-ready. Run command_to_run only in a separately approved executor; this controller does not execute it."

    command_execution_allowed = controller_status == "ready"
    safety["command_execution_allowed_by_controller"] = command_execution_allowed

    return {
        "schema": SCHEMA,
        "controller_status": controller_status,
        "execution_decision": execution_decision,
        "selected_action": selected_action,
        "command_to_run": command_to_run,
        "command_execution_allowed": command_execution_allowed,
        "command_executed": False,
        "allowed_paths": allowed_paths,
        "validators": validators,
        "max_repairs": max_repairs,
        "max_files_changed": max_files_changed,
        "approval_status": approval_status,
        "bridge_status": bridge_status,
        "executor_status": executor_status,
        "verifier_status": verifier_status,
        "required_pre_execution_checks": REQUIRED_PRE_EXECUTION_CHECKS.copy(),
        "rejection_reasons": rejection_reasons or block_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
    }


build_one_action_execution_controller = build_self_build_one_action_execution_controller
evaluate_self_build_one_action_execution_controller = build_self_build_one_action_execution_controller


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Decide whether one approved AIOS self-build APPLY command may run.")
    parser.add_argument("--queue-item", default="{}")
    parser.add_argument("--apply-approval", default="{}")
    parser.add_argument("--local-apply-executor-bridge", default="{}")
    parser.add_argument("--single-action-executor", default="{}")
    parser.add_argument("--apply-result-verifier", default="{}")
    parser.add_argument("--core-status", default="{}")
    parser.add_argument("--stop-report", default="{}")
    parser.add_argument("--execution-request", default="{}")
    return parser


def _json_arg(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(
        json.dumps(
            build_self_build_one_action_execution_controller(
                _json_arg(args.queue_item),
                _json_arg(args.apply_approval),
                _json_arg(args.local_apply_executor_bridge),
                _json_arg(args.single_action_executor),
                _json_arg(args.apply_result_verifier),
                _json_arg(args.core_status),
                _json_arg(args.stop_report),
                _json_arg(args.execution_request),
            ),
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
