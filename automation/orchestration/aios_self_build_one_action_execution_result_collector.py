from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_RESULT_COLLECTOR.v1"
PREVIEW_LIMIT = 400
SANDBOX_1312_MARKER = "createprocessasuserw failed: 1312"
PRE_EXECUTION_VERIFIER_REASONS = {"command_not_executed", "validators_missing"}

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

COLLECTION_CHECKS = [
    "selected_queue_item_present",
    "apply_approval.approval_status_approved",
    "one_action_local_apply_executor.executor_status_executed",
    "one_action_local_apply_executor.command_executed_true",
    "command_returncode_zero",
    "apply_result_verifier.verifier_status_passed",
    "selected_action_matches_all_components",
    "changed_files_bounded_to_allowed_paths",
    "validators_present",
    "validators_passed",
    "protected_actions_blocked",
    "collector_writes_no_files",
    "collector_writes_no_reports",
]


def _base_safety() -> dict[str, bool]:
    return {
        "collector_only": True,
        "result_consumer_only": True,
        "commands_executed": False,
        "command_executed": False,
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


def _protected_requested(*payloads: Any) -> bool:
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


def _collect_safety(*payloads: Any) -> dict[str, bool]:
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


def _preview(value: Any) -> str:
    return str(value or "")[:PREVIEW_LIMIT]


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


def _component_actions(payload: dict[str, Any], *keys: str) -> list[str]:
    return [_first_action(payload.get(key)) for key in keys if _first_action(payload.get(key)) != "none"]


def _action_alignment_reasons(
    queue_item: dict[str, Any],
    approval: dict[str, Any],
    bridge: dict[str, Any],
    executor: dict[str, Any],
    controller: dict[str, Any],
    runner: dict[str, Any],
    gate: dict[str, Any],
    local_executor: dict[str, Any],
    verifier: dict[str, Any],
) -> list[str]:
    if not queue_item:
        return []
    reasons: list[str] = []
    queue_action = _first_action(queue_item.get("action_id"))
    if queue_action == "none":
        reasons.append("selected_action_missing")
        return reasons

    actions: list[str] = []
    actions.extend(_component_actions(approval, "requested_action", "selected_queue_action", "action_id"))
    actions.extend(_component_actions(bridge, "selected_action", "action_id"))
    actions.extend(_component_actions(executor, "selected_action", "action_id"))
    actions.extend(_component_actions(controller, "selected_action", "action_id"))
    actions.extend(_component_actions(runner, "selected_action", "action_id"))
    actions.extend(_component_actions(gate, "selected_action", "action_id"))
    actions.extend(_component_actions(local_executor, "selected_action", "action_id"))
    actions.extend(_component_actions(verifier, "selected_action", "action_id"))
    if any(action != queue_action for action in actions):
        reasons.append("selected_action_mismatch")
    return reasons


def _validator_records_from(value: Any) -> list[dict[str, Any]]:
    source = value
    if isinstance(source, dict):
        for key in ("validators", "validator_results", "validators_run", "post_validation_results"):
            if isinstance(source.get(key), list):
                source = source[key]
                break
    output: list[dict[str, Any]] = []
    for index, validator in enumerate(_as_list(source)):
        if isinstance(validator, dict):
            name = str(validator.get("name", validator.get("command", f"validator_{index + 1}")))
            command = str(validator.get("command", name))
            returncode = validator.get("returncode")
            passed = bool(validator.get("passed") is True or returncode == 0)
        else:
            name = str(validator)
            command = name
            returncode = None
            passed = None
        output.append(
            {
                "name": name,
                "command": command,
                "passed": passed,
                "returncode": returncode,
            }
        )
    return output


def _validator_records(*sources: Any) -> list[dict[str, Any]]:
    for source in sources:
        records = _validator_records_from(source)
        if records:
            return records
    return []


def _post_execution_evidence(local_executor: dict[str, Any]) -> dict[str, Any]:
    post = local_executor.get("post_execution_evidence", {})
    return post if isinstance(post, dict) else {}


def _changed_files(local_executor: dict[str, Any], verifier: dict[str, Any]) -> list[str]:
    post = _post_execution_evidence(local_executor)
    local_changed = _path_values(post, "changed_files", "files_changed", "files")
    verifier_changed = _path_values(verifier, "changed_files", "files_changed", "files")
    return _dedupe(local_changed or verifier_changed)


def _verifier_status_reasons(verifier: dict[str, Any]) -> tuple[list[str], list[str]]:
    block_reasons: list[str] = []
    rejection_reasons: list[str] = []
    if not verifier:
        block_reasons.append("apply_result_verifier_missing")
        return block_reasons, rejection_reasons

    verifier_status = str(verifier.get("verifier_status", "blocked"))
    verifier_reasons = [str(reason) for reason in _as_list(verifier.get("rejection_reasons", []))]
    if verifier_status == "passed":
        return block_reasons, rejection_reasons
    if verifier_status == "blocked":
        if verifier_reasons and set(verifier_reasons).issubset(PRE_EXECUTION_VERIFIER_REASONS):
            block_reasons.extend(verifier_reasons)
        else:
            block_reasons.append("apply_result_verifier_blocked")
        return block_reasons, rejection_reasons
    if verifier_status in {"failed", "rejected"}:
        rejection_reasons.append(f"apply_result_verifier_{verifier_status}")
    else:
        block_reasons.append("apply_result_verifier_unknown_status")
    return block_reasons, rejection_reasons


def build_self_build_one_action_execution_result_collector(
    selected_queue_item: dict[str, Any] | None = None,
    apply_approval: dict[str, Any] | None = None,
    local_apply_executor_bridge: dict[str, Any] | None = None,
    single_action_executor: dict[str, Any] | None = None,
    one_action_execution_controller: dict[str, Any] | None = None,
    one_action_apply_runner: dict[str, Any] | None = None,
    one_action_execute_gate: dict[str, Any] | None = None,
    one_action_local_apply_executor: dict[str, Any] | None = None,
    apply_result_verifier: dict[str, Any] | None = None,
    post_validation_results: Any = None,
) -> dict[str, Any]:
    queue_item = _as_dict(selected_queue_item)
    approval = _as_dict(apply_approval)
    bridge = _as_dict(local_apply_executor_bridge)
    executor = _as_dict(single_action_executor)
    controller = _as_dict(one_action_execution_controller)
    runner = _as_dict(one_action_apply_runner)
    gate = _as_dict(one_action_execute_gate)
    local_executor = _as_dict(one_action_local_apply_executor)
    verifier = _as_dict(apply_result_verifier)
    post_results = post_validation_results if post_validation_results is not None else []

    selected_action = _first_action(
        local_executor.get("selected_action"),
        verifier.get("selected_action"),
        gate.get("selected_action"),
        runner.get("selected_action"),
        controller.get("selected_action"),
        executor.get("selected_action"),
        bridge.get("selected_action"),
        approval.get("selected_queue_action"),
        approval.get("requested_action"),
        queue_item.get("action_id"),
    )
    allowed_paths_raw = [str(path) for path in _as_list(queue_item.get("allowed_paths", []))]
    allowed_paths = _normalize_paths(allowed_paths_raw)
    validators = _validators(queue_item, local_executor, gate, runner, controller, executor, bridge, verifier)
    changed_files_raw = _changed_files(local_executor, verifier)
    changed_files = _normalize_paths(changed_files_raw)
    unexpected_files = sorted(path for path in changed_files if path not in set(allowed_paths))
    validator_records = _validator_records(post_results, verifier, _post_execution_evidence(local_executor))
    verifier_validators_passed = _first_int(verifier.get("validators_passed"), default=0)
    verifier_validators_failed = _first_int(verifier.get("validators_failed"), default=0)
    validators_passed = (
        sum(1 for validator in validator_records if validator.get("passed") is True)
        if validator_records
        else verifier_validators_passed
    )
    validators_failed = (
        sum(1 for validator in validator_records if validator.get("passed") is False)
        if validator_records
        else verifier_validators_failed
    )
    max_files_changed = _first_int(
        local_executor.get("max_files_changed"),
        verifier.get("max_files_changed"),
        gate.get("max_files_changed"),
        runner.get("max_files_changed"),
        controller.get("max_files_changed"),
        executor.get("max_files_changed"),
        bridge.get("max_files_changed"),
        queue_item.get("max_files_changed"),
        default=len(allowed_paths) or 1,
    )

    approval_status = str(approval.get("approval_status", "review_required"))
    local_status = str(local_executor.get("executor_status", "blocked"))
    verifier_status = str(verifier.get("verifier_status", "blocked"))
    command_executed = bool(local_executor.get("command_executed") is True)
    command_returncode = local_executor.get("command_returncode")
    post_evidence = _post_execution_evidence(local_executor)
    safety = _collect_safety(
        queue_item,
        approval,
        bridge,
        executor,
        controller,
        runner,
        gate,
        local_executor,
        verifier,
        post_results,
    )

    block_reasons: list[str] = []
    rejection_reasons: list[str] = []
    if not queue_item:
        block_reasons.append("selected_queue_item_missing")
    if approval_status != "approved":
        block_reasons.append("apply_approval_not_approved")
    if not local_executor:
        block_reasons.append("one_action_local_apply_executor_missing")
    elif local_status == "rejected":
        rejection_reasons.append("one_action_local_apply_executor_rejected")
    elif local_status != "executed":
        block_reasons.append("one_action_local_apply_executor_not_executed")
    if not command_executed:
        block_reasons.append("command_not_executed")
    elif command_returncode != 0:
        rejection_reasons.append("command_returncode_nonzero")
    if safety["sandbox_1312_blocker"]:
        block_reasons.append("sandbox_1312_runner_blocker")
    if safety["protected_action_requested"]:
        rejection_reasons.append("protected_action_requested")

    verifier_blocks, verifier_rejections = _verifier_status_reasons(verifier)
    block_reasons.extend(verifier_blocks)
    rejection_reasons.extend(verifier_rejections)
    if queue_item:
        rejection_reasons.extend(
            _action_alignment_reasons(queue_item, approval, bridge, executor, controller, runner, gate, local_executor, verifier)
        )
        rejection_reasons.extend(
            _path_rejection_reasons(
                allowed_paths,
                allowed_paths_raw,
                changed_files_raw,
                _path_values(approval, "requested_write_paths", "write_paths", "allowed_paths"),
                _path_values(bridge, "allowed_paths"),
                _path_values(executor, "allowed_paths"),
                _path_values(controller, "allowed_paths"),
                _path_values(runner, "allowed_paths"),
                _path_values(gate, "allowed_paths"),
                _path_values(local_executor, "allowed_paths"),
                _path_values(verifier, "allowed_paths", "unexpected_files"),
            )
        )
        if unexpected_files:
            rejection_reasons.append("unexpected_files_outside_allowed_paths")
        if len(changed_files) != len(changed_files_raw):
            rejection_reasons.append("changed_files_unbounded")
        if len(changed_files) > max_files_changed:
            rejection_reasons.append("max_files_changed_exceeded")
        if not validators:
            rejection_reasons.append("validators_missing")
    if command_executed and verifier_status == "passed" and not validator_records and validators_passed == 0:
        rejection_reasons.append("validator_evidence_missing")
    if validators_failed:
        rejection_reasons.append("validators_failed")

    block_reasons = _dedupe(block_reasons)
    rejection_reasons = _dedupe(rejection_reasons)
    if rejection_reasons:
        collector_status = "rejected"
        result_decision = "rejected"
        next_safe_action = "Stop and report result collector rejection before any package, stage, commit, push, or merge."
    elif block_reasons:
        collector_status = "blocked"
        result_decision = "blocked"
        if safety["sandbox_1312_blocker"]:
            next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
        else:
            next_safe_action = "Stop until one bounded local APPLY has executed and verifier evidence passes."
    else:
        collector_status = "collected"
        result_decision = "report_result"
        next_safe_action = "Report the bounded execution result. Packaging, staging, commit, push, and merge still require approval."

    result_safe_to_report = collector_status in {"collected", "blocked", "rejected"}
    result_safe_to_package = collector_status == "collected" and verifier_status == "passed" and command_executed
    result_summary = {
        "selected_action": selected_action,
        "executor_status": local_status,
        "verifier_status": verifier_status,
        "command_executed": command_executed,
        "command_returncode": command_returncode,
        "changed_file_count": len(changed_files),
        "validators_passed": validators_passed,
        "validators_failed": validators_failed,
    }

    return {
        "schema": SCHEMA,
        "collector_status": collector_status,
        "result_decision": result_decision,
        "package_decision": "package_ready" if result_safe_to_package else "not_package_ready",
        "selected_action": selected_action,
        "command_executed": command_executed,
        "command_returncode": command_returncode,
        "command_stdout_preview": _preview(post_evidence.get("stdout_preview", local_executor.get("command_stdout_preview", ""))),
        "command_stderr_preview": _preview(post_evidence.get("stderr_preview", local_executor.get("command_stderr_preview", ""))),
        "changed_files": changed_files,
        "allowed_paths": allowed_paths,
        "unexpected_files": unexpected_files,
        "validators": validators,
        "validator_records": validator_records,
        "validators_passed": validators_passed,
        "validators_failed": validators_failed,
        "max_files_changed": max_files_changed,
        "collection_checks": COLLECTION_CHECKS.copy(),
        "result_summary": result_summary,
        "report_preview": result_summary.copy(),
        "result_safe_to_report": result_safe_to_report,
        "result_safe_to_package": result_safe_to_package,
        "files_written": False,
        "reports_written": False,
        "rejection_reasons": rejection_reasons or block_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
    }


build_one_action_execution_result_collector = build_self_build_one_action_execution_result_collector
evaluate_self_build_one_action_execution_result_collector = build_self_build_one_action_execution_result_collector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect one AIOS self-build execution result without side effects.")
    parser.add_argument("--queue-item", default="{}")
    parser.add_argument("--apply-approval", default="{}")
    parser.add_argument("--local-apply-executor-bridge", default="{}")
    parser.add_argument("--single-action-executor", default="{}")
    parser.add_argument("--one-action-execution-controller", default="{}")
    parser.add_argument("--one-action-apply-runner", default="{}")
    parser.add_argument("--one-action-execute-gate", default="{}")
    parser.add_argument("--one-action-local-apply-executor", default="{}")
    parser.add_argument("--apply-result-verifier", default="{}")
    parser.add_argument("--post-validation-results", default="[]")
    return parser


def _json_dict_arg(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _json_any_arg(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(
        json.dumps(
            build_self_build_one_action_execution_result_collector(
                _json_dict_arg(args.queue_item),
                _json_dict_arg(args.apply_approval),
                _json_dict_arg(args.local_apply_executor_bridge),
                _json_dict_arg(args.single_action_executor),
                _json_dict_arg(args.one_action_execution_controller),
                _json_dict_arg(args.one_action_apply_runner),
                _json_dict_arg(args.one_action_execute_gate),
                _json_dict_arg(args.one_action_local_apply_executor),
                _json_dict_arg(args.apply_result_verifier),
                _json_any_arg(args.post_validation_results),
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
