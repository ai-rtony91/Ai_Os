from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


SCHEMA = "AIOS_WAKE_CONTINUE.v1"
SUPPORTED_GOALS = {"forex-paper-bot"}

AUTONOMY_EXECUTOR_PATH = Path("automation/orchestration/aios_autonomy_execute.py")
FOREX_BOT_PATH = Path("apps/trading_lab/trading_lab/forex_paper_bot.py")
FOREX_BOT_TEST_PATH = Path("tests/trading_lab/test_forex_paper_bot.py")
FOREX_BACKTEST_PATH = Path("apps/trading_lab/trading_lab/forex_backtest.py")
FOREX_BACKTEST_TEST_PATH = Path("tests/trading_lab/test_forex_backtest.py")
FOREX_LEDGER_PATH = Path("apps/trading_lab/trading_lab/forex_paper_ledger.py")
FOREX_LEDGER_TEST_PATH = Path("tests/trading_lab/test_forex_paper_ledger.py")
FOREX_STRATEGY_PATH = Path("apps/trading_lab/trading_lab/forex_strategy_rules.py")
FOREX_STRATEGY_TEST_PATH = Path("tests/trading_lab/test_forex_strategy_rules.py")
FOREX_DATA_IMPORT_PATH = Path("apps/trading_lab/trading_lab/forex_data_import.py")
FOREX_DATA_IMPORT_TEST_PATH = Path("tests/trading_lab/test_forex_data_import.py")
FOREX_REPORT_PATH = Path("apps/trading_lab/trading_lab/forex_report.py")
FOREX_REPORT_TEST_PATH = Path("tests/trading_lab/test_forex_report.py")
FOREX_DECISION_POLICY_PATH = Path("apps/trading_lab/trading_lab/forex_decision_policy.py")
FOREX_DECISION_POLICY_TEST_PATH = Path("tests/trading_lab/test_forex_decision_policy.py")
FOREX_GOAL_DECISION_BRIDGE_PATH = Path("automation/orchestration/aios_forex_goal_decision.py")
NEXT_BUILD_PLAN_ROUTER_PATH = Path("automation/orchestration/aios_next_build_plan.py")
BOUNDED_EXECUTOR_HANDOFF_PATH = Path("automation/orchestration/aios_bounded_executor_handoff.py")
RESUME_STATE_PATH = Path("automation/orchestration/aios_resume_state.py")
CLI_RESULT_INGEST_PATH = Path("automation/orchestration/aios_cli_result_ingest.py")
OPERATOR_RELAY_PATH = Path("automation/orchestration/aios_operator_relay.py")
LOCAL_RUNNER_BRIDGE_PATH = Path("automation/orchestration/aios_local_runner_bridge.py")
BOUNDED_EXECUTOR_READY_PATH = Path("automation/orchestration/aios_bounded_executor_ready.py")
CONTROL_PLANE_STATUS_PATH = Path("automation/orchestration/aios_control_plane_status.py")

CommandRunner = Callable[[list[str], Path], dict[str, Any]]


def safety_flags() -> dict[str, bool]:
    return {
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "delete_reset": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "runtime_launch": False,
        "scheduler": False,
        "daemon": False,
        "secrets": False,
        "broker": False,
        "live_trading": False,
        "real_orders": False,
    }


def approval_required() -> dict[str, bool]:
    return {
        "local_allowlisted_build": False,
        "commit": True,
        "push": True,
        "merge": True,
        "secrets": True,
        "broker_live_trading": True,
        "scheduler_activation": True,
        "destructive_action": True,
        "queue_mutation": True,
        "approval_mutation": True,
        "worker_dispatch": True,
    }


def read_repo_state(repo_root: Path) -> dict[str, bool]:
    return {
        "autonomy_executor_exists": (repo_root / AUTONOMY_EXECUTOR_PATH).exists(),
        "forex_scaffold_exists": (repo_root / FOREX_BOT_PATH).exists(),
        "forex_scaffold_test_exists": (repo_root / FOREX_BOT_TEST_PATH).exists(),
        "forex_backtest_exists": (repo_root / FOREX_BACKTEST_PATH).exists(),
        "forex_backtest_test_exists": (repo_root / FOREX_BACKTEST_TEST_PATH).exists(),
        "forex_ledger_exists": (repo_root / FOREX_LEDGER_PATH).exists(),
        "forex_ledger_test_exists": (repo_root / FOREX_LEDGER_TEST_PATH).exists(),
        "forex_strategy_exists": (repo_root / FOREX_STRATEGY_PATH).exists(),
        "forex_strategy_test_exists": (repo_root / FOREX_STRATEGY_TEST_PATH).exists(),
        "forex_data_import_exists": (repo_root / FOREX_DATA_IMPORT_PATH).exists(),
        "forex_data_import_test_exists": (repo_root / FOREX_DATA_IMPORT_TEST_PATH).exists(),
        "forex_report_exists": (repo_root / FOREX_REPORT_PATH).exists(),
        "forex_report_test_exists": (repo_root / FOREX_REPORT_TEST_PATH).exists(),
        "forex_decision_policy_exists": (repo_root / FOREX_DECISION_POLICY_PATH).exists(),
        "forex_decision_policy_test_exists": (repo_root / FOREX_DECISION_POLICY_TEST_PATH).exists(),
    }


def select_next_action(goal: str, repo_state: dict[str, bool]) -> tuple[str, str | None]:
    if goal not in SUPPORTED_GOALS:
        return "blocked", "unsupported_goal"
    if not repo_state["autonomy_executor_exists"]:
        return "blocked", "autonomy_executor_missing"
    if not repo_state["forex_scaffold_exists"]:
        return "build_forex_scaffold", None
    if not repo_state["forex_scaffold_test_exists"]:
        return "blocked", "forex_scaffold_test_missing"
    if not repo_state["forex_backtest_exists"]:
        return "build_forex_backtest", None
    if not repo_state["forex_backtest_test_exists"]:
        return "blocked", "forex_backtest_test_missing"
    if not repo_state["forex_ledger_exists"]:
        return "build_forex_ledger", None
    if not repo_state["forex_ledger_test_exists"]:
        return "blocked", "forex_ledger_test_missing"
    if not repo_state["forex_strategy_exists"]:
        return "build_forex_strategy", None
    if not repo_state["forex_strategy_test_exists"]:
        return "blocked", "forex_strategy_test_missing"
    if not repo_state["forex_data_import_exists"]:
        return "build_forex_data_import", None
    if not repo_state["forex_data_import_test_exists"]:
        return "blocked", "forex_data_import_test_missing"
    if not repo_state["forex_report_exists"]:
        return "build_forex_report", None
    if not repo_state["forex_report_test_exists"]:
        return "blocked", "forex_report_test_missing"
    if not repo_state["forex_decision_policy_exists"]:
        return "build_forex_decision_policy", None
    if not repo_state["forex_decision_policy_test_exists"]:
        return "blocked", "forex_decision_policy_test_missing"
    return "validate_all_forex", None


def command_for_action(action: str, max_repairs: int) -> list[str]:
    if action == "build_forex_scaffold":
        return [
            sys.executable,
            AUTONOMY_EXECUTOR_PATH.as_posix(),
            "--goal",
            "forex-paper-bot",
            "--apply",
            "--max-repairs",
            str(max_repairs),
        ]
    if action in {
        "build_forex_backtest",
        "build_forex_ledger",
        "build_forex_strategy",
        "build_forex_data_import",
        "build_forex_report",
        "build_forex_decision_policy",
    }:
        return [
            sys.executable,
            AUTONOMY_EXECUTOR_PATH.as_posix(),
            "--goal",
            "forex-paper-bot",
            "--continue",
            "--apply",
            "--max-repairs",
            str(max_repairs),
        ]
    if action == "validate_all_forex":
        return [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            FOREX_BOT_TEST_PATH.as_posix(),
            FOREX_BACKTEST_TEST_PATH.as_posix(),
            FOREX_LEDGER_TEST_PATH.as_posix(),
            FOREX_STRATEGY_TEST_PATH.as_posix(),
            FOREX_DATA_IMPORT_TEST_PATH.as_posix(),
            FOREX_REPORT_TEST_PATH.as_posix(),
            FOREX_DECISION_POLICY_TEST_PATH.as_posix(),
        ]
    raise ValueError(f"unsupported action: {action}")


def default_command_runner(command: list[str], repo_root: Path) -> dict[str, Any]:
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
        "passed": completed.returncode == 0,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def build_goal_decision(repo_root: Path, goal: str) -> dict[str, Any]:
    bridge_path = Path(__file__).with_name("aios_forex_goal_decision.py")
    spec = importlib.util.spec_from_file_location("aios_forex_goal_decision", bridge_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_FOREX_GOAL_DECISION.v1",
            "goal": goal,
            "decision_bridge_passed": False,
            "decision": "stop_for_human_review",
            "reason_code": "goal_decision_bridge_unavailable",
            "decision_reasons": ["goal_decision_bridge_unavailable"],
            "next_safe_action": "Stop and repair the missing Forex goal decision bridge.",
            "safety": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_goal_decision(repo_root, goal=goal)


def build_next_build_plan(goal_decision: dict[str, Any]) -> dict[str, Any]:
    router_path = Path(__file__).with_name("aios_next_build_plan.py")
    spec = importlib.util.spec_from_file_location("aios_next_build_plan", router_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_NEXT_BUILD_PLAN.v1",
            "goal": goal_decision.get("goal", "forex-paper-bot"),
            "input_decision": goal_decision.get("decision", "invalid_decision"),
            "route": "stop",
            "next_component": "none",
            "next_packet_id": "NONE",
            "reason_code": "next_build_plan_router_unavailable",
            "plan_reasons": ["next_build_plan_router_unavailable"],
            "next_safe_action": "Stop and repair the missing next build plan router.",
            "approval_required": approval_required(),
            "safety": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_next_build_plan(goal_decision)


def build_bounded_executor_handoff(next_build_plan: dict[str, Any]) -> dict[str, Any]:
    handoff_path = Path(__file__).with_name("aios_bounded_executor_handoff.py")
    spec = importlib.util.spec_from_file_location("aios_bounded_executor_handoff", handoff_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
            "goal": next_build_plan.get("goal", "forex-paper-bot"),
            "input_route": next_build_plan.get("route", "unknown"),
            "next_component": next_build_plan.get("next_component", "unknown"),
            "next_packet_id": next_build_plan.get("next_packet_id", "NONE"),
            "handoff_status": "blocked",
            "reason_code": "bounded_executor_handoff_unavailable",
            "executor_mode": "none",
            "allowed_action": "none",
            "allowed_paths": [],
            "validators": [],
            "command_preview": [],
            "approval_required": approval_required(),
            "safety": safety_flags(),
            "next_safe_action": "Stop and repair the missing bounded executor handoff builder.",
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_bounded_executor_handoff(next_build_plan)


def build_resume_state(wake_report: dict[str, Any]) -> dict[str, Any]:
    resume_path = Path(__file__).with_name("aios_resume_state.py")
    spec = importlib.util.spec_from_file_location("aios_resume_state", resume_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_RESUME_STATE.v1",
            "goal": wake_report.get("goal", "forex-paper-bot"),
            "result": wake_report.get("result", "BLOCKED"),
            "resume_ready": False,
            "resume_reason_code": "resume_state_builder_unavailable",
            "next_safe_action": "Stop and repair the missing resume-state builder.",
            "safety": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_resume_state(wake_report)


def build_cli_result_ingest(cli_report: dict[str, Any]) -> dict[str, Any]:
    ingest_path = Path(__file__).with_name("aios_cli_result_ingest.py")
    spec = importlib.util.spec_from_file_location("aios_cli_result_ingest", ingest_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_CLI_RESULT_INGEST.v1",
            "status": "BLOCKED",
            "validation_passed": False,
            "blockers": ["cli_result_ingest_unavailable"],
            "next_safe_action": "Stop and repair the missing CLI result ingest builder.",
            "safety_summary": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_cli_result_ingest(cli_report)


def build_operator_relay(
    resume_state: dict[str, Any],
    cli_result_ingest: dict[str, Any],
    next_build_plan: dict[str, Any],
) -> dict[str, Any]:
    relay_path = Path(__file__).with_name("aios_operator_relay.py")
    spec = importlib.util.spec_from_file_location("aios_operator_relay", relay_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_OPERATOR_RELAY.v1",
            "relay_status": "blocked",
            "human_action_required": True,
            "codex_prompt_ready": False,
            "next_safe_action": "Stop and repair the missing operator relay builder.",
            "safety": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_operator_relay(resume_state, cli_result_ingest, next_build_plan)


def build_local_runner_bridge(bounded_executor_handoff: dict[str, Any]) -> dict[str, Any]:
    bridge_path = Path(__file__).with_name("aios_local_runner_bridge.py")
    spec = importlib.util.spec_from_file_location("aios_local_runner_bridge", bridge_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_LOCAL_RUNNER_BRIDGE.v1",
            "runner_status": "blocked",
            "command_preview": [],
            "working_directory": str(Path(__file__).resolve().parents[2]),
            "validation_commands": [],
            "forbidden_actions": [],
            "approval_required": approval_required(),
            "safety": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_local_runner_bridge(bounded_executor_handoff)


def build_bounded_executor_ready(bounded_executor_handoff: dict[str, Any]) -> dict[str, Any]:
    ready_path = Path(__file__).with_name("aios_bounded_executor_ready.py")
    spec = importlib.util.spec_from_file_location("aios_bounded_executor_ready", ready_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_BOUNDED_EXECUTOR_READY.v1",
            "status": "blocked",
            "reason_code": "bounded_executor_ready_unavailable",
            "command_execution": False,
            "executed": False,
            "next_safe_action": "Stop and repair the missing bounded executor readiness builder.",
            "safety": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_bounded_executor_ready(bounded_executor_handoff)


def build_control_plane_status(
    resume_state: dict[str, Any],
    cli_result_ingest: dict[str, Any],
    operator_relay: dict[str, Any],
    local_runner_bridge: dict[str, Any],
    bounded_executor_ready: dict[str, Any],
) -> dict[str, Any]:
    status_path = Path(__file__).with_name("aios_control_plane_status.py")
    spec = importlib.util.spec_from_file_location("aios_control_plane_status", status_path)
    if spec is None or spec.loader is None:
        return {
            "schema": "AIOS_CONTROL_PLANE_STATUS.v1",
            "loop_status": "blocked",
            "resume_ready": False,
            "blockers": ["control_plane_status_unavailable"],
            "dashboard_ready": False,
            "next_action": "Stop and repair the missing control-plane status builder.",
            "safety": safety_flags(),
        }
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_control_plane_status(
        resume_state=resume_state,
        cli_result_ingest=cli_result_ingest,
        operator_relay=operator_relay,
        local_runner_bridge=local_runner_bridge,
        bounded_executor_ready=bounded_executor_ready,
    )


def write_resume_state(repo_root: Path, resume_state: dict[str, Any], resume_state_dir: Path | None) -> dict[str, Any]:
    resume_path = Path(__file__).with_name("aios_resume_state.py")
    spec = importlib.util.spec_from_file_location("aios_resume_state", resume_path)
    if spec is None or spec.loader is None:
        raise ValueError("resume_state_builder_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.write_resume_state(repo_root, resume_state, output_dir=resume_state_dir)


def write_control_plane_status(
    repo_root: Path,
    control_plane_status: dict[str, Any],
    control_plane_dir: Path | None,
) -> dict[str, Any]:
    status_path = Path(__file__).with_name("aios_control_plane_status.py")
    spec = importlib.util.spec_from_file_location("aios_control_plane_status", status_path)
    if spec is None or spec.loader is None:
        raise ValueError("control_plane_status_builder_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.write_control_plane_status(repo_root, control_plane_status, output_dir=control_plane_dir)


def default_state_path() -> Path:
    return Path(tempfile.gettempdir()) / "AIOS_WAKE_CONTINUE_STATE.json"


def base_report(goal: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": goal,
        "selected_action": None,
        "commands_run": [],
        "validators_run": [],
        "repair_attempts": 0,
        "goal_decision": None,
        "next_build_plan": None,
        "bounded_executor_handoff": None,
        "cli_result_ingest": None,
        "operator_relay": None,
        "local_runner_bridge": None,
        "bounded_executor_ready": None,
        "control_plane_status": None,
        "control_plane_status_path": None,
        "resume_state": None,
        "resume_state_paths": None,
        "result": "blocked",
        "next_safe_action": "Inspect the blocked reason before continuing.",
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }


def write_state(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def run_wake_continue(
    repo_root: Path,
    *,
    goal: str,
    apply: bool = False,
    max_cycles: int = 1,
    max_repairs: int = 0,
    state_path: Path | None = None,
    command_runner: CommandRunner | None = None,
    write_resume_state_requested: bool = False,
    resume_state_dir: Path | None = None,
    write_control_plane_status_requested: bool = False,
    control_plane_dir: Path | None = None,
) -> dict[str, Any]:
    report = base_report(goal)
    state_path = state_path or default_state_path()
    report["state_path"] = str(state_path)

    if max_cycles < 1:
        report["blocked_reason"] = "max_cycles_must_be_at_least_one"
        write_state(state_path, report)
        return report
    if max_repairs < 0:
        report["blocked_reason"] = "max_repairs_must_be_non_negative"
        write_state(state_path, report)
        return report

    runner = command_runner or default_command_runner

    for _cycle in range(max_cycles):
        repo_state = read_repo_state(repo_root)
        selected_action, blocked_reason = select_next_action(goal, repo_state)
        report["selected_action"] = selected_action

        if blocked_reason:
            report["blocked_reason"] = blocked_reason
            report["result"] = "blocked"
            write_state(state_path, report)
            return report

        if not apply:
            report["result"] = "preview_only"
            report["next_safe_action"] = "Run with --apply to execute the selected allowlisted action."
            write_state(state_path, report)
            return report

        command = command_for_action(selected_action, max_repairs)
        command_result = runner(command, repo_root)
        report["commands_run"].append(command_result)
        if selected_action.startswith("validate_"):
            report["validators_run"].append(command_result)

        if command_result.get("passed", False):
            if selected_action.startswith("build_"):
                continue
            cli_result_ingest = build_cli_result_ingest(command_result)
            report["cli_result_ingest"] = cli_result_ingest
            goal_decision = build_goal_decision(repo_root, goal)
            report["goal_decision"] = goal_decision
            if not goal_decision.get("decision_bridge_passed", False):
                report["result"] = "blocked"
                report["blocked_reason"] = goal_decision.get("reason_code", "goal_decision_bridge_failed")
                report["next_safe_action"] = goal_decision.get(
                    "next_safe_action",
                    "Inspect the blocked Forex goal decision bridge output.",
                )
                write_state(state_path, report)
                return report
            next_build_plan = build_next_build_plan(goal_decision)
            report["next_build_plan"] = next_build_plan
            bounded_executor_handoff = build_bounded_executor_handoff(next_build_plan)
            report["bounded_executor_handoff"] = bounded_executor_handoff
            local_runner_bridge = build_local_runner_bridge(bounded_executor_handoff)
            report["local_runner_bridge"] = local_runner_bridge
            bounded_executor_ready = build_bounded_executor_ready(bounded_executor_handoff)
            report["bounded_executor_ready"] = bounded_executor_ready
            handoff_status = bounded_executor_handoff.get("handoff_status")
            if (
                handoff_status == "ready"
                and local_runner_bridge.get("runner_status") == "preview_ready"
                and bounded_executor_ready.get("status") == "ready_for_human_review"
            ):
                report["result"] = "DONE_FOR_CURRENT_GOAL"
            elif handoff_status == "stopped":
                report["result"] = "REVIEW_REQUIRED"
            else:
                report["result"] = "BLOCKED"
                report["blocked_reason"] = bounded_executor_ready.get(
                    "reason_code",
                    bounded_executor_handoff.get("reason_code", "bounded_executor_handoff_blocked"),
                )
            report["next_safe_action"] = bounded_executor_handoff["next_safe_action"]
            resume_state = build_resume_state(report)
            report["resume_state"] = resume_state
            operator_relay = build_operator_relay(resume_state, cli_result_ingest, next_build_plan)
            report["operator_relay"] = operator_relay
            control_plane_status = build_control_plane_status(
                resume_state,
                cli_result_ingest,
                operator_relay,
                local_runner_bridge,
                bounded_executor_ready,
            )
            report["control_plane_status"] = control_plane_status
            report["next_safe_action"] = control_plane_status.get(
                "next_action",
                bounded_executor_handoff["next_safe_action"],
            )
            if report["result"] == "DONE_FOR_CURRENT_GOAL" and control_plane_status.get("dashboard_ready") is not True:
                report["result"] = "BLOCKED"
                report["blocked_reason"] = "control_plane_not_dashboard_ready"
                resume_state = build_resume_state(report)
                report["resume_state"] = resume_state
                operator_relay = build_operator_relay(resume_state, cli_result_ingest, next_build_plan)
                report["operator_relay"] = operator_relay
                control_plane_status = build_control_plane_status(
                    resume_state,
                    cli_result_ingest,
                    operator_relay,
                    local_runner_bridge,
                    bounded_executor_ready,
                )
                report["control_plane_status"] = control_plane_status
                report["next_safe_action"] = control_plane_status.get(
                    "next_action",
                    bounded_executor_handoff["next_safe_action"],
                )
            if write_resume_state_requested:
                try:
                    resume_state = write_resume_state(repo_root, resume_state, resume_state_dir)
                except (FileExistsError, ValueError) as exc:
                    report["result"] = "BLOCKED"
                    report["blocked_reason"] = str(exc)
                    report["next_safe_action"] = "Stop and repair resume-state persistence before continuing."
                    write_state(state_path, report)
                    return report
                report["resume_state"] = resume_state
                report["resume_state_paths"] = resume_state.get("resume_state_paths")
            if write_control_plane_status_requested:
                try:
                    control_plane_status = write_control_plane_status(
                        repo_root,
                        report["control_plane_status"],
                        control_plane_dir,
                    )
                except ValueError as exc:
                    report["result"] = "BLOCKED"
                    report["blocked_reason"] = str(exc)
                    report["next_safe_action"] = "Stop and repair control-plane status persistence before continuing."
                    write_state(state_path, report)
                    return report
                report["control_plane_status"] = control_plane_status
                report["control_plane_status_path"] = control_plane_status.get("control_plane_status_path")
            write_state(state_path, report)
            return report

        while report["repair_attempts"] < max_repairs:
            report["repair_attempts"] += 1
            repair_command = command_for_action("build_forex_decision_policy", max_repairs)
            repair_result = runner(repair_command, repo_root)
            report["commands_run"].append(repair_result)
            retry_result = runner(command, repo_root)
            report["commands_run"].append(retry_result)
            if selected_action.startswith("validate_"):
                report["validators_run"].append(retry_result)
            if retry_result.get("passed", False):
                report["result"] = "passed"
                report["next_safe_action"] = "Review local changes. Commit and push still require approval."
                write_state(state_path, report)
                return report

        report["result"] = "failed"
        report["next_safe_action"] = "Inspect command output before another bounded repair."
        write_state(state_path, report)
        return report

    report["result"] = "max_cycles_reached"
    report["next_safe_action"] = "Run another bounded cycle after reviewing state."
    write_state(state_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one bounded AIOS wake/continue cycle.")
    parser.add_argument("--goal", required=True, help="Supported goal: forex-paper-bot.")
    parser.add_argument("--apply", action="store_true", help="Execute the selected allowlisted action.")
    parser.add_argument("--max-cycles", type=int, default=1, help="Maximum cycles before stopping.")
    parser.add_argument("--max-repairs", type=int, default=0, help="Maximum repair attempts.")
    parser.add_argument("--repo-root", default=None, help="Optional repo root for tests.")
    parser.add_argument("--state-path", default=None, help="Optional JSON state output path.")
    parser.add_argument("--write-resume-state", action="store_true", help="Write sanitized resume state under Reports/aios_resume.")
    parser.add_argument("--resume-state-dir", default=None, help="Optional resume-state output dir under Reports/aios_resume.")
    parser.add_argument("--write-control-plane-status", action="store_true", help="Write control-plane latest status under Reports/aios_control_plane.")
    parser.add_argument("--control-plane-dir", default=None, help="Optional output dir under Reports/aios_control_plane.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    state_path = Path(args.state_path).resolve() if args.state_path else None
    resume_state_dir = Path(args.resume_state_dir) if args.resume_state_dir else None
    control_plane_dir = Path(args.control_plane_dir) if args.control_plane_dir else None
    report = run_wake_continue(
        repo_root,
        goal=args.goal,
        apply=args.apply,
        max_cycles=args.max_cycles,
        max_repairs=args.max_repairs,
        state_path=state_path,
        write_resume_state_requested=args.write_resume_state,
        resume_state_dir=resume_state_dir,
        write_control_plane_status_requested=args.write_control_plane_status,
        control_plane_dir=control_plane_dir,
    )
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0 if report["result"] in {"DONE_FOR_CURRENT_GOAL", "REVIEW_REQUIRED", "passed", "preview_only", "blocked", "BLOCKED", "max_cycles_reached"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
