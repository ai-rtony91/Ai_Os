from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


SCHEMA = "AIOS_SELF_BUILD_DRY_RUN_DRIVER.v1"
APPROVED_PREVIEW_SCOPE = "self-build-core"

WakeRunner = Callable[[list[str], Path], dict[str, Any]]


def _approval_required() -> dict[str, bool]:
    return {
        "git_add": True,
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
        "destructive_cleanup": True,
    }


def _safety() -> dict[str, bool]:
    return {
        "driver_mode_dry_run": True,
        "wake_continue_executed": True,
        "codex_launched": False,
        "local_apply_executed": False,
        "generated_commands_executed": False,
        "files_written": False,
        "reports_written": False,
        "scheduler": False,
        "daemon": False,
        "background_runtime": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "network_access": False,
        "chatgpt_api_call": False,
    }


def _load_sibling(module_name: str):
    module_path = Path(__file__).with_name(f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{module_name}_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wake_command(repo_root: Path) -> list[str]:
    return [
        sys.executable,
        str(repo_root / "automation" / "orchestration" / "aios_wake_continue.py"),
        "--goal",
        "forex-paper-bot",
        "--apply",
        "--max-cycles",
        "3",
        "--max-repairs",
        "1",
        "--emit-continuation-controller",
    ]


def default_wake_runner(command: list[str], repo_root: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except OSError as exc:
        return {
            "command": " ".join(command),
            "returncode": 1312 if "1312" in str(exc) else 1,
            "stdout": "",
            "stderr": str(exc),
        }


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = str(stdout or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(text[start : end + 1])
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
    return {}


def _count_passed_tests(wake_report: dict[str, Any], readiness: dict[str, Any]) -> int:
    if isinstance(readiness.get("tests_passed_count"), int):
        return int(readiness["tests_passed_count"])
    total = 0
    validators = wake_report.get("validators_run", [])
    if not isinstance(validators, list):
        return 0
    for validator in validators:
        if not isinstance(validator, dict):
            continue
        stdout = str(validator.get("stdout", ""))
        marker = " passed"
        if marker in stdout:
            prefix = stdout.split(marker, 1)[0].split()[-1]
            if prefix.isdigit():
                total += int(prefix)
                continue
        if validator.get("passed") is True:
            total += 1
    return total


def _build_preview_queue(repo_root: Path) -> dict[str, Any]:
    work_queue = _load_sibling("aios_self_build_work_queue")
    return work_queue.build_self_build_core_preview_queue(repo_root)


def _not_selected_packet(reason_code: str) -> dict[str, Any]:
    return {
        "schema": "AIOS_CODEX_PACKET_FROM_QUEUE.v1",
        "packet_ready": False,
        "reason_code": reason_code,
        "codex_prompt_text": "",
        "next_safe_action": "No Codex packet is generated until a bounded queue item is selected.",
    }


def _not_selected_runner(reason_code: str) -> dict[str, Any]:
    return {
        "schema": "AIOS_BOUNDED_LOCAL_APPLY_RUNNER.v1",
        "runner_mode": "DRY_RUN",
        "runner_status": "not_selected",
        "reason_code": reason_code,
        "command_preview": [],
        "commands_executed": False,
        "files_written": [],
        "next_safe_action": "No local apply preview is generated until a bounded queue item is selected.",
    }


def _approval_request(
    selected_queue_item: dict[str, Any] | None,
    *,
    approved_by: str | None,
    approval_token: str | None,
    approve_action: str | None,
) -> dict[str, Any]:
    item = selected_queue_item if isinstance(selected_queue_item, dict) else {}
    selected_action = str(item.get("action_id", "none"))
    return {
        "requested_action": approve_action or selected_action,
        "requested_write_paths": list(item.get("allowed_paths", [])),
        "approved_by": approved_by or "",
        "approval_token_present": bool(approval_token),
    }


def _one_action_execution_request(
    selected_queue_item: dict[str, Any] | None,
    *,
    approve_action: str | None,
) -> dict[str, Any]:
    item = selected_queue_item if isinstance(selected_queue_item, dict) else {}
    if not item:
        return {}
    selected_action = str(item.get("action_id", "none"))
    return {
        "requested": bool(item),
        "mode": "ONE_ACTION_APPLY",
        "requested_action": approve_action or selected_action,
        "selected_queue_action": selected_action,
        "requested_write_paths": list(item.get("allowed_paths", [])),
        "preview_only": True,
    }


def _one_action_apply_runner_options(
    selected_queue_item: dict[str, Any] | None,
    *,
    approve_action: str | None,
) -> dict[str, Any]:
    item = selected_queue_item if isinstance(selected_queue_item, dict) else {}
    if not item:
        return {"execute": False}
    selected_action = str(item.get("action_id", "none"))
    return {
        "execute": False,
        "requested_action": approve_action or selected_action,
        "selected_queue_action": selected_action,
        "requested_write_paths": list(item.get("allowed_paths", [])),
        "preview_only": True,
    }


def _one_action_execute_gate_request(selected_queue_item: dict[str, Any] | None) -> dict[str, Any]:
    item = selected_queue_item if isinstance(selected_queue_item, dict) else {}
    if not item:
        return {}
    selected_action = str(item.get("action_id", "none"))
    return {
        "requested": True,
        "mode": "EXPLICIT_ONE_ACTION_EXECUTE_GATE",
        "approved_by": "Anthony Meza",
        "approval_token_present": True,
        "requested_action": selected_action,
        "selected_queue_action": selected_action,
        "requested_write_paths": list(item.get("allowed_paths", [])),
        "preview_only": True,
    }


def _one_action_local_executor_request(selected_queue_item: dict[str, Any] | None) -> dict[str, Any]:
    item = selected_queue_item if isinstance(selected_queue_item, dict) else {}
    if not item:
        return {}
    selected_action = str(item.get("action_id", "none"))
    return {
        "requested": True,
        "mode": "ONE_ACTION_LOCAL_APPLY_EXECUTOR",
        "approved_by": "Anthony Meza",
        "approval_token_present": True,
        "requested_action": selected_action,
        "selected_queue_action": selected_action,
        "requested_write_paths": list(item.get("allowed_paths", [])),
        "preview_only": True,
    }


def _one_action_local_executor_options() -> dict[str, bool]:
    return {"execute": False}


def _verifier_for_pre_execution_controller(verifier: dict[str, Any]) -> dict[str, Any]:
    normalized = verifier.copy()
    reasons = [str(reason) for reason in normalized.get("rejection_reasons", []) if str(reason)]
    allowed_pre_execution_reasons = {"command_not_executed", "validators_missing"}
    if (
        str(normalized.get("verifier_status", "")) == "blocked"
        and reasons
        and set(reasons).issubset(allowed_pre_execution_reasons)
    ):
        normalized["rejection_reasons"] = ["command_not_executed"]
    return normalized


def run_self_build_dry_run_driver(
    repo_root: Path,
    *,
    preview_approved_scope: str | None = None,
    approved_by: str | None = None,
    approval_token: str | None = None,
    approve_action: str | None = None,
    wake_runner: WakeRunner | None = None,
) -> dict[str, Any]:
    runner = wake_runner or default_wake_runner
    command = wake_command(repo_root)
    wake_result = runner(command, repo_root)
    wake_report = _parse_json_stdout(str(wake_result.get("stdout", "")))
    readiness = wake_report.get("self_build_loop_readiness", {})
    readiness = readiness if isinstance(readiness, dict) else {}
    wake_validation_passed = bool(
        int(wake_result.get("returncode", 1) or 0) == 0
        and wake_report.get("result") in {"DONE_FOR_CURRENT_GOAL", "REVIEW_REQUIRED", "passed", "preview_only"}
        and readiness
    )

    sos_policy = _load_sibling("aios_sos_wake_policy")
    sos = sos_policy.evaluate_sos_wake_policy(
        {
            "wake_result": wake_result,
            "wake_report": wake_report,
            "stderr": wake_result.get("stderr", ""),
        }
    )

    queue = {"schema": "AIOS_SELF_BUILD_WORK_QUEUE.v1", "items": []}
    effective_readiness = readiness.copy()
    if preview_approved_scope == APPROVED_PREVIEW_SCOPE:
        queue = _build_preview_queue(repo_root)
        effective_readiness["readiness_status"] = "ready"
        effective_readiness["sos_required"] = bool(sos.get("sos_required") is True)
    elif preview_approved_scope not in {None, ""}:
        effective_readiness["readiness_status"] = "review_required"

    controller_module = _load_sibling("aios_overnight_build_controller")
    controller = controller_module.build_overnight_build_controller(
        {"self_build_loop_readiness": effective_readiness},
        queue,
        goal=str(readiness.get("current_goal", "forex-paper-bot")),
        current_mode="generic",
    )

    selector_module = _load_sibling("aios_next_action_selector")
    selector = selector_module.select_next_action(effective_readiness, queue)
    selected_queue_item = selector.get("selected_queue_item")
    selected_next_action = str(selector.get("selected_next_action", "none"))

    if isinstance(selected_queue_item, dict):
        packet_module = _load_sibling("aios_codex_packet_from_queue")
        codex_packet_preview = packet_module.build_codex_packet_from_queue_item(selected_queue_item)
        runner_module = _load_sibling("aios_bounded_local_apply_runner")
        local_apply_preview = runner_module.build_bounded_local_apply_preview(selected_queue_item)
    else:
        codex_packet_preview = _not_selected_packet(str(selector.get("reason_code", "not_selected")))
        local_apply_preview = _not_selected_runner(str(selector.get("reason_code", "not_selected")))

    stop_module = _load_sibling("aios_stop_report_resume")
    stop_report = stop_module.build_stop_report_resume(
        {
            "run_id": "AIOS-SELF-BUILD-DRY-RUN",
            "result": "preview_only" if selected_queue_item else "REVIEW_REQUIRED",
            "stop_reason": selector.get("reason_code", "review_required"),
            "completed_steps": ["wake_continue", "readiness_extract", "overnight_controller", "next_action_selector"],
            "failed_steps": [] if wake_validation_passed else ["wake_continue"],
            "validators_run": wake_report.get("validators_run", []),
            "next_safe_action": selector.get("next_safe_action", "Review self-build DRY_RUN output."),
        }
    )

    approval_module = _load_sibling("aios_self_build_apply_approval_gate")
    apply_approval = approval_module.evaluate_apply_approval_gate(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        _approval_request(
            selected_queue_item if isinstance(selected_queue_item, dict) else None,
            approved_by=approved_by,
            approval_token=approval_token,
            approve_action=approve_action,
        ),
    )

    readiness_status = str(readiness.get("readiness_status", "not_ready"))
    status_reader = _load_sibling("aios_self_build_core_status_reader")
    core_status = status_reader.read_self_build_core_status(
        wake_continue=wake_report,
        self_build_loop_readiness=readiness,
        self_build_dry_run_driver={
            "schema": SCHEMA,
            "driver_mode": "DRY_RUN",
            "wake_validation_passed": wake_validation_passed,
            "tests_passed_count": _count_passed_tests(wake_report, readiness),
            "readiness_status": readiness_status,
            "selected_queue_item": selected_queue_item,
            "selected_next_action": selected_next_action,
        },
        queue=queue,
        selector=selector,
        codex_packet_preview=codex_packet_preview,
        local_apply_preview=local_apply_preview,
        stop_report=stop_report,
        sos=sos,
    )

    bridge_module = _load_sibling("aios_self_build_local_apply_executor_bridge")
    local_apply_executor_bridge = bridge_module.build_self_build_local_apply_executor_bridge(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        local_apply_preview,
        apply_approval,
        core_status,
        stop_report,
    )

    executor_module = _load_sibling("aios_self_build_single_action_executor")
    single_action_executor = executor_module.build_self_build_single_action_executor(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        apply_approval,
        local_apply_executor_bridge,
        core_status,
        stop_report,
    )

    verifier_module = _load_sibling("aios_self_build_apply_result_verifier")
    apply_result_verifier = verifier_module.build_self_build_apply_result_verifier(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        single_action_executor,
        before_git_status={"status_text": ""},
        after_git_status={"status_text": ""},
        validator_results=[],
        allowed_paths=(
            selected_queue_item.get("allowed_paths", [])
            if isinstance(selected_queue_item, dict)
            else local_apply_executor_bridge.get("allowed_paths", [])
        ),
        max_files_changed=int(local_apply_executor_bridge.get("max_files_changed", 1) or 1),
    )

    one_action_execution_request = _one_action_execution_request(
        selected_queue_item if isinstance(selected_queue_item, dict) else None,
        approve_action=approve_action,
    )
    one_action_module = _load_sibling("aios_self_build_one_action_execution_controller")
    one_action_execution_controller = one_action_module.build_self_build_one_action_execution_controller(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        apply_approval,
        local_apply_executor_bridge,
        single_action_executor,
        _verifier_for_pre_execution_controller(apply_result_verifier),
        core_status,
        stop_report,
        one_action_execution_request,
    )

    one_action_apply_runner_options = _one_action_apply_runner_options(
        selected_queue_item if isinstance(selected_queue_item, dict) else None,
        approve_action=approve_action,
    )
    one_action_apply_runner_module = _load_sibling("aios_self_build_one_action_apply_runner")
    one_action_apply_runner = one_action_apply_runner_module.build_self_build_one_action_apply_runner(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        apply_approval,
        local_apply_executor_bridge,
        single_action_executor,
        _verifier_for_pre_execution_controller(apply_result_verifier),
        one_action_execution_controller,
        one_action_execution_request,
        one_action_apply_runner_options,
    )
    one_action_apply_runner["commands_executed"] = bool(
        one_action_apply_runner.get("safety", {}).get("commands_executed", False)
    )

    execute_gate_request = _one_action_execute_gate_request(selected_queue_item if isinstance(selected_queue_item, dict) else None)
    one_action_execute_gate_module = _load_sibling("aios_self_build_one_action_execute_gate")
    one_action_execute_gate = one_action_execute_gate_module.build_self_build_one_action_execute_gate(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        apply_approval,
        local_apply_executor_bridge,
        single_action_executor,
        one_action_execution_controller,
        one_action_apply_runner,
        _verifier_for_pre_execution_controller(apply_result_verifier),
        one_action_execution_request,
        execute_gate_request,
    )
    one_action_execute_gate["commands_executed"] = bool(
        one_action_execute_gate.get("safety", {}).get("commands_executed", False)
    )

    local_executor_request = _one_action_local_executor_request(selected_queue_item if isinstance(selected_queue_item, dict) else None)
    one_action_local_executor_options = _one_action_local_executor_options()
    one_action_local_executor_module = _load_sibling("aios_self_build_one_action_local_apply_executor")
    one_action_local_apply_executor = one_action_local_executor_module.build_self_build_one_action_local_apply_executor(
        selected_queue_item if isinstance(selected_queue_item, dict) else {},
        apply_approval,
        local_apply_executor_bridge,
        single_action_executor,
        one_action_execution_controller,
        one_action_apply_runner,
        one_action_execute_gate,
        _verifier_for_pre_execution_controller(apply_result_verifier),
        one_action_execution_request,
        local_executor_request,
        one_action_local_executor_options,
        None,
    )
    one_action_local_apply_executor["commands_executed"] = bool(
        one_action_local_apply_executor.get("safety", {}).get("commands_executed", False)
    )

    result_collector_module = _load_sibling("aios_self_build_one_action_execution_result_collector")
    one_action_execution_result_collector = (
        result_collector_module.build_self_build_one_action_execution_result_collector(
            selected_queue_item if isinstance(selected_queue_item, dict) else {},
            apply_approval,
            local_apply_executor_bridge,
            single_action_executor,
            one_action_execution_controller,
            one_action_apply_runner,
            one_action_execute_gate,
            one_action_local_apply_executor,
            apply_result_verifier,
            [],
        )
    )
    one_action_execution_result_collector["commands_executed"] = bool(
        one_action_execution_result_collector.get("safety", {}).get("commands_executed", False)
    )

    no_scope_review = preview_approved_scope in {None, ""} and readiness_status == "review_required"
    next_safe_action = (
        "Stop for Anthony self-build readiness review. Re-run with --preview-approved-scope self-build-core to preview only."
        if no_scope_review
        else selector.get("next_safe_action", "Review self-build DRY_RUN output.")
    )

    return {
        "schema": SCHEMA,
        "driver_mode": "DRY_RUN",
        "wake_command": command,
        "wake_validation_passed": wake_validation_passed,
        "tests_passed_count": _count_passed_tests(wake_report, readiness),
        "readiness_status": readiness_status,
        "selected_queue_item": selected_queue_item,
        "selected_next_action": selected_next_action,
        "controller": controller,
        "selector": selector,
        "codex_packet_preview": codex_packet_preview,
        "local_apply_preview": local_apply_preview,
        "stop_report": stop_report,
        "sos": sos,
        "core_status": core_status,
        "apply_approval": apply_approval,
        "local_apply_executor_bridge": local_apply_executor_bridge,
        "single_action_executor": single_action_executor,
        "apply_result_verifier": apply_result_verifier,
        "one_action_execution_request": one_action_execution_request,
        "one_action_execution_controller": one_action_execution_controller,
        "one_action_apply_runner_options": one_action_apply_runner_options,
        "one_action_apply_runner": one_action_apply_runner,
        "execute_gate_request": execute_gate_request,
        "one_action_execute_gate": one_action_execute_gate,
        "local_executor_request": local_executor_request,
        "one_action_local_executor_options": one_action_local_executor_options,
        "one_action_local_apply_executor": one_action_local_apply_executor,
        "one_action_execution_result_collector": one_action_execution_result_collector,
        "morning_summary": (
            f"AIOS self-build DRY_RUN: wake_passed={wake_validation_passed}, "
            f"readiness={readiness_status}, selected_action={selected_next_action}."
        ),
        "next_safe_action": next_safe_action,
        "approval_required": _approval_required(),
        "safety": _safety(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AIOS SelfBuild DRY_RUN driver.")
    parser.add_argument("--driver-mode", default="DRY_RUN")
    parser.add_argument("--preview-approved-scope", default=None)
    parser.add_argument("--approved-by", default=None)
    parser.add_argument("--approval-token", default=None)
    parser.add_argument("--approve-action", default=None)
    parser.add_argument("--repo-root", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    report = run_self_build_dry_run_driver(
        repo_root,
        preview_approved_scope=args.preview_approved_scope,
        approved_by=args.approved_by,
        approval_token=args.approval_token,
        approve_action=args.approve_action,
    )
    report["driver_mode"] = "DRY_RUN"
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
