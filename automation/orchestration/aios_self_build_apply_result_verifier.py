from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.v1"
SANDBOX_1312_MARKER = "createprocessasuserw failed: 1312"


def _base_safety() -> dict[str, bool]:
    return {
        "verifier_only": True,
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


def _payload_text(*payloads: Any) -> str:
    return " ".join(json.dumps(payload, sort_keys=True).lower() for payload in payloads if payload is not None)


def _status_paths(status: Any) -> list[str]:
    if isinstance(status, dict):
        for key in ("changed_files", "files_changed", "files", "paths"):
            value = status.get(key)
            if isinstance(value, list):
                return _normalize_paths(value)
        status = status.get("status_text", status.get("stdout", ""))
    if isinstance(status, list):
        return _normalize_paths(status)
    output: list[str] = []
    for raw_line in str(status or "").splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("##"):
            continue
        path_text = line[3:].strip() if len(line) > 3 else line.strip()
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1].strip()
        if _bounded_path(path_text):
            output.append(path_text)
    return sorted(set(output))


def _changed_files(before_git_status: Any, after_git_status: Any) -> list[str]:
    before = set(_status_paths(before_git_status))
    after = set(_status_paths(after_git_status))
    if before:
        return sorted(after - before)
    return sorted(after)


def _validator_list(validator_results: Any) -> list[dict[str, Any]]:
    source = validator_results
    if isinstance(source, dict):
        for key in ("validators", "validator_results", "validators_run"):
            if isinstance(source.get(key), list):
                source = source[key]
                break
    output: list[dict[str, Any]] = []
    for index, validator in enumerate(_as_list(source)):
        if isinstance(validator, dict):
            name = str(validator.get("name", validator.get("command", f"validator_{index + 1}")))
            command = str(validator.get("command", name))
            passed = bool(validator.get("passed") is True or validator.get("returncode") == 0)
            returncode = validator.get("returncode")
        else:
            name = str(validator)
            command = name
            passed = False
            returncode = None
        output.append(
            {
                "name": name,
                "command": command,
                "passed": passed,
                "returncode": returncode,
            }
        )
    return output


def build_self_build_apply_result_verifier(
    selected_queue_item: dict[str, Any] | None = None,
    single_action_executor: dict[str, Any] | None = None,
    before_git_status: Any = None,
    after_git_status: Any = None,
    validator_results: Any = None,
    allowed_paths: list[str] | None = None,
    max_files_changed: int | None = None,
) -> dict[str, Any]:
    queue_item = _as_dict(selected_queue_item)
    executor = _as_dict(single_action_executor)
    selected_action = str(executor.get("selected_action", queue_item.get("action_id", "none")))
    allowed = _normalize_paths(allowed_paths if allowed_paths is not None else queue_item.get("allowed_paths", []))
    changed_files = _changed_files(before_git_status, after_git_status)
    unexpected_files = sorted(path for path in changed_files if path not in set(allowed))
    validators = _validator_list(validator_results)
    validators_passed = sum(1 for validator in validators if validator["passed"] is True)
    validators_failed = sum(1 for validator in validators if validator["passed"] is not True)
    max_changed = int(max_files_changed if max_files_changed is not None else executor.get("max_files_changed", len(allowed) or 1))
    file_count_ok = len(changed_files) <= max_changed
    allowed_paths_ok = bool(allowed) and not unexpected_files
    command_executed = bool(executor.get("command_executed") is True)
    safety = _base_safety()
    if SANDBOX_1312_MARKER in _payload_text(
        selected_queue_item,
        single_action_executor,
        before_git_status,
        after_git_status,
        validator_results,
    ):
        safety["sandbox_1312_blocker"] = True

    rejection_reasons: list[str] = []
    if not command_executed:
        rejection_reasons.append("command_not_executed")
    if safety["sandbox_1312_blocker"]:
        rejection_reasons.append("sandbox_1312_runner_blocker")
    if unexpected_files:
        rejection_reasons.append("unexpected_files_outside_allowed_paths")
    if not file_count_ok:
        rejection_reasons.append("max_files_changed_exceeded")
    if not validators:
        rejection_reasons.append("validators_missing")
    elif validators_failed:
        rejection_reasons.append("validators_failed")

    if not command_executed or safety["sandbox_1312_blocker"]:
        verifier_status = "blocked"
    elif unexpected_files or not file_count_ok or not validators or validators_failed:
        verifier_status = "failed"
    else:
        verifier_status = "passed"

    result_safe_to_report = verifier_status in {"passed", "failed", "blocked"}
    result_safe_to_package = verifier_status == "passed"
    if verifier_status == "passed":
        next_safe_action = "Result verified. Report the bounded APPLY result; staging, commit, push, and merge still require approval."
    elif safety["sandbox_1312_blocker"]:
        next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
    elif verifier_status == "blocked":
        next_safe_action = "Stop until a bounded local APPLY has executed and produced validator evidence."
    else:
        next_safe_action = "Stop and report verifier failure before any package, stage, commit, push, or merge."

    return {
        "schema": SCHEMA,
        "verifier_status": verifier_status,
        "selected_action": selected_action,
        "changed_files": changed_files,
        "allowed_paths": allowed,
        "unexpected_files": unexpected_files,
        "validators": validators,
        "validators_passed": validators_passed,
        "validators_failed": validators_failed,
        "max_files_changed": max_changed,
        "file_count_ok": file_count_ok,
        "allowed_paths_ok": allowed_paths_ok,
        "result_safe_to_report": result_safe_to_report,
        "result_safe_to_package": result_safe_to_package,
        "rejection_reasons": rejection_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
    }


verify_self_build_apply_result = build_self_build_apply_result_verifier
build_apply_result_verifier = build_self_build_apply_result_verifier


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify one AIOS self-build APPLY result without side effects.")
    parser.add_argument("--queue-item", default="{}")
    parser.add_argument("--single-action-executor", default="{}")
    parser.add_argument("--before-git-status", default="")
    parser.add_argument("--after-git-status", default="")
    parser.add_argument("--validator-results", default="[]")
    parser.add_argument("--allowed-paths", default="[]")
    parser.add_argument("--max-files-changed", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        queue_item = json.loads(args.queue_item)
        executor = json.loads(args.single_action_executor)
        validators = json.loads(args.validator_results)
        allowed_paths = json.loads(args.allowed_paths)
    except json.JSONDecodeError:
        queue_item = {}
        executor = {}
        validators = []
        allowed_paths = []
    print(
        json.dumps(
            build_self_build_apply_result_verifier(
                queue_item,
                executor,
                args.before_git_status,
                args.after_git_status,
                validators,
                allowed_paths,
                args.max_files_changed,
            ),
            indent=2,
            sort_keys=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
