from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_ONE_ACTION_EXECUTE_GATE.v1"
EXECUTE_GATE_MODE = "EXPLICIT_ONE_ACTION_EXECUTE_GATE"
ONE_ACTION_APPLY_MODE = "ONE_ACTION_APPLY"
APPROVED_BY = "Anthony Meza"
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

REQUIRED_GATE_CHECKS = [
    "execute_gate_request.requested_true",
    "execute_gate_request.mode_EXPLICIT_ONE_ACTION_EXECUTE_GATE",
    "execute_gate_request.approved_by_Anthony_Meza",
    "execute_gate_request.approval_token_present_true",
    "selected_queue_item_present",
    "apply_approval.approval_status_approved",
    "local_apply_executor_bridge.bridge_status_ready",
    "single_action_executor.executor_status_ready",
    "single_action_executor.command_would_run_true",
    "one_action_execution_controller.controller_status_ready",
    "one_action_execution_controller.command_execution_allowed_true",
    "one_action_apply_runner.runner_status_preview_ready",
    "one_action_apply_runner.command_execution_allowed_true",
    "selected_action_matches_all_components",
    "command_to_run_present",
    "allowed_paths_bounded",
    "validators_present",
    "max_files_changed_no_more_than_five",
    "max_repairs_no_more_than_one",
    "protected_actions_blocked",
    "apply_result_verifier.pre_execution_ready_or_passed",
]

PRE_EXECUTION_VERIFIER_REASONS = {"command_not_executed", "validators_missing"}


def _base_safety() -> dict[str, bool]:
    return {
        "gate_only": True,
        "arms_without_execution": True,
        "command_execution_allowed_by_gate": False,
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


def _has_int(*values: Any) -> bool:
    for value in values:
        if value in (None, ""):
            continue
        try:
            int(value)
        except (TypeError, ValueError):
            continue
        return True
    return False


def _path_values(payload: dict[str, Any], *keys: str) -> list[str]:
    output: list[str] = []
    for key in keys:
        output.extend(str(path) for path in _as_list(payload.get(key, [])))
    return output


def _path_rejection_reasons(allowed_paths: list[str], *path_groups: list[str]) -> list[str]:
    reasons: list[str] = []
    allowed = set(allowed_paths)
    if not allowed_paths:
        _append_once(reasons, "allowed_paths_missing")
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
    controller: dict[str, Any],
    runner: dict[str, Any],
    execution_request: dict[str, Any],
    gate_request: dict[str, Any],
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
    component_actions = [
        _first_action(bridge.get("selected_action")),
        _first_action(executor.get("selected_action")),
        _first_action(controller.get("selected_action")),
        _first_action(runner.get("selected_action")),
    ]
    request_actions = [
        _first_action(execution_request.get("requested_action"), execution_request.get("selected_action"), execution_request.get("action_id")),
        _first_action(gate_request.get("requested_action"), gate_request.get("selected_action"), gate_request.get("action_id")),
    ]

    if queue_action == "none":
        _append_once(reasons, "selected_action_missing")
    if str(approval.get("approval_status", "")) == "approved":
        if not approval_actions or any(action != queue_action for action in approval_actions):
            _append_once(reasons, "selected_action_mismatch")
    if any(action == "none" or action != queue_action for action in component_actions):
        _append_once(reasons, "selected_action_mismatch")
    if any(action != "none" and action != queue_action for action in request_actions):
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
        if verifier_reasons and set(verifier_reasons) <= PRE_EXECUTION_VERIFIER_REASONS:
            return block_reasons, rejection_reasons
        block_reasons.append("apply_result_verifier_blocked")
    elif verifier_status in {"failed", "rejected"}:
        rejection_reasons.append(f"apply_result_verifier_{verifier_status}")
    elif verifier_status not in {"passed", "ready"}:
        block_reasons.append("apply_result_verifier_unknown_status")
    return block_reasons, rejection_reasons


def build_self_build_one_action_execute_gate(
    selected_queue_item: dict[str, Any] | None = None,
    apply_approval: dict[str, Any] | None = None,
    local_apply_executor_bridge: dict[str, Any] | None = None,
    single_action_executor: dict[str, Any] | None = None,
    one_action_execution_controller: dict[str, Any] | None = None,
    one_action_apply_runner: dict[str, Any] | None = None,
    apply_result_verifier: dict[str, Any] | None = None,
    execution_request: dict[str, Any] | None = None,
    execute_gate_request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_item = _as_dict(selected_queue_item)
    approval = _as_dict(apply_approval)
    bridge = _as_dict(local_apply_executor_bridge)
    executor = _as_dict(single_action_executor)
    controller = _as_dict(one_action_execution_controller)
    runner = _as_dict(one_action_apply_runner)
    verifier = _as_dict(apply_result_verifier)
    execution = _as_dict(execution_request)
    gate_request = _as_dict(execute_gate_request)

    selected_action = _first_action(
        runner.get("selected_action"),
        controller.get("selected_action"),
        executor.get("selected_action"),
        bridge.get("selected_action"),
        approval.get("selected_queue_action"),
        approval.get("requested_action"),
        gate_request.get("requested_action"),
        execution.get("requested_action"),
        queue_item.get("action_id"),
    )
    command_to_run = str(
        runner.get("command_to_run")
        or controller.get("command_to_run")
        or executor.get("command_to_run")
        or bridge.get("command_to_run")
        or gate_request.get("command_to_run")
        or execution.get("command_to_run")
        or ""
    )
    allowed_paths_raw = [str(path) for path in _as_list(queue_item.get("allowed_paths", []))]
    allowed_paths = _normalize_paths(allowed_paths_raw)
    validators = _validators(queue_item, runner, controller, executor, bridge)
    max_repairs_values = (
        runner.get("max_repairs"),
        controller.get("max_repairs"),
        executor.get("max_repairs"),
        bridge.get("max_repairs"),
        queue_item.get("max_repairs"),
    )
    max_files_changed_values = (
        runner.get("max_files_changed"),
        controller.get("max_files_changed"),
        executor.get("max_files_changed"),
        bridge.get("max_files_changed"),
        verifier.get("max_files_changed"),
        queue_item.get("max_files_changed"),
    )
    max_repairs_present = _has_int(*max_repairs_values)
    max_files_changed_present = _has_int(*max_files_changed_values)
    max_repairs = _first_int(*max_repairs_values, default=1)
    max_files_changed = _first_int(*max_files_changed_values, default=len(allowed_paths) or 1)

    approval_status = str(approval.get("approval_status", "review_required"))
    bridge_status = str(bridge.get("bridge_status", "blocked"))
    executor_status = str(executor.get("executor_status", "blocked"))
    controller_status = str(controller.get("controller_status", "blocked"))
    runner_status = str(runner.get("runner_status", "blocked"))
    safety = _collect_safety(queue_item, approval, bridge, executor, controller, runner, verifier, execution, gate_request)

    rejection_reasons: list[str] = []
    block_reasons: list[str] = []

    gate_request_missing = not gate_request
    if gate_request_missing:
        block_reasons.append("execute_gate_request_missing")
    else:
        if gate_request.get("requested") is not True:
            block_reasons.append("execute_gate_request_not_requested")
        if str(gate_request.get("mode", "")) != EXECUTE_GATE_MODE:
            block_reasons.append("execute_gate_request_mode_not_explicit_execute_gate")
        if str(gate_request.get("approved_by", "")) != APPROVED_BY:
            block_reasons.append("execute_gate_request_approved_by_invalid")
        if gate_request.get("approval_token_present") is not True:
            block_reasons.append("execute_gate_request_approval_token_missing")

    if not queue_item:
        block_reasons.append("selected_queue_item_missing")
    if approval_status != "approved":
        block_reasons.append("apply_approval_not_approved")
    if bridge_status != "ready":
        block_reasons.append("local_apply_bridge_not_ready")
    if executor_status != "ready":
        block_reasons.append("single_action_executor_not_ready")
    if executor.get("command_would_run") is not True:
        block_reasons.append("command_would_run_false")
    if controller_status != "ready":
        block_reasons.append("one_action_execution_controller_not_ready")
    if controller.get("command_execution_allowed") is not True:
        block_reasons.append("one_action_execution_controller_not_allowed")
    if runner_status != "preview_ready":
        block_reasons.append("one_action_apply_runner_not_preview_ready")
    if runner.get("command_execution_allowed") is not True:
        block_reasons.append("one_action_apply_runner_not_allowed")
    if safety["sandbox_1312_blocker"]:
        block_reasons.append("sandbox_1312_runner_blocker")

    if not gate_request_missing:
        rejection_reasons.extend(
            _action_alignment_reasons(queue_item, approval, bridge, executor, controller, runner, execution, gate_request)
        )
        rejection_reasons.extend(
            _path_rejection_reasons(
                allowed_paths,
                allowed_paths_raw,
                _path_values(approval, "requested_write_paths", "write_paths", "allowed_paths"),
                _path_values(bridge, "allowed_paths"),
                _path_values(executor, "allowed_paths"),
                _path_values(controller, "allowed_paths"),
                _path_values(runner, "allowed_paths"),
                _path_values(verifier, "allowed_paths", "changed_files", "unexpected_files"),
                _path_values(execution, "requested_write_paths", "write_paths", "allowed_paths", "paths"),
                _path_values(gate_request, "requested_write_paths", "write_paths", "allowed_paths", "paths"),
            )
        )
        if not validators:
            rejection_reasons.append("validators_missing")
        if not command_to_run:
            rejection_reasons.append("command_to_run_missing")
        if not max_files_changed_present:
            rejection_reasons.append("max_files_changed_missing")
        elif max_files_changed > 5:
            rejection_reasons.append("max_files_changed_exceeds_five")
        if not max_repairs_present:
            rejection_reasons.append("max_repairs_missing")
        elif max_repairs > 1:
            rejection_reasons.append("max_repairs_exceeds_one")

    if safety["protected_action_requested"]:
        rejection_reasons.append("protected_action_requested")

    if not gate_request_missing:
        verifier_blocks, verifier_rejections = _verifier_gate_reasons(verifier)
        block_reasons.extend(verifier_blocks)
        rejection_reasons.extend(verifier_rejections)

    rejection_reasons = _dedupe(rejection_reasons)
    block_reasons = _dedupe(block_reasons)
    if rejection_reasons:
        gate_status = "rejected"
        execution_gate_decision = "rejected"
        next_safe_action = "Stop and repair rejected execute-gate inputs before any one-action execution path."
    elif block_reasons:
        gate_status = "blocked"
        execution_gate_decision = "blocked"
        if safety["sandbox_1312_blocker"]:
            next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
        else:
            next_safe_action = "Stop until explicit execute-gate request, approval, bridge, executor, controller, and runner readiness are satisfied."
    else:
        gate_status = "armed"
        execution_gate_decision = "one_action_execution_armed"
        next_safe_action = "Execution is armed by this gate, but v1 does not execute command_to_run. A separate approved executor is required."

    command_execution_allowed = gate_status == "armed"
    safety["command_execution_allowed_by_gate"] = command_execution_allowed

    return {
        "schema": SCHEMA,
        "gate_status": gate_status,
        "execution_gate_decision": execution_gate_decision,
        "selected_action": selected_action,
        "command_to_run": command_to_run,
        "command_execution_allowed": command_execution_allowed,
        "command_executed": False,
        "allowed_paths": allowed_paths,
        "validators": validators,
        "max_repairs": max_repairs,
        "max_files_changed": max_files_changed,
        "required_gate_checks": REQUIRED_GATE_CHECKS.copy(),
        "rejection_reasons": rejection_reasons or block_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
    }


build_one_action_execute_gate = build_self_build_one_action_execute_gate
evaluate_self_build_one_action_execute_gate = build_self_build_one_action_execute_gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Arm one approved AIOS self-build APPLY command without executing it.")
    parser.add_argument("--queue-item", default="{}")
    parser.add_argument("--apply-approval", default="{}")
    parser.add_argument("--local-apply-executor-bridge", default="{}")
    parser.add_argument("--single-action-executor", default="{}")
    parser.add_argument("--one-action-execution-controller", default="{}")
    parser.add_argument("--one-action-apply-runner", default="{}")
    parser.add_argument("--apply-result-verifier", default="{}")
    parser.add_argument("--execution-request", default="{}")
    parser.add_argument("--execute-gate-request", default="{}")
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
            build_self_build_one_action_execute_gate(
                _json_arg(args.queue_item),
                _json_arg(args.apply_approval),
                _json_arg(args.local_apply_executor_bridge),
                _json_arg(args.single_action_executor),
                _json_arg(args.one_action_execution_controller),
                _json_arg(args.one_action_apply_runner),
                _json_arg(args.apply_result_verifier),
                _json_arg(args.execution_request),
                _json_arg(args.execute_gate_request),
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
