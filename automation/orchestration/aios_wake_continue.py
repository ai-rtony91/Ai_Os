from __future__ import annotations

import argparse
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
            report["result"] = "DONE_FOR_CURRENT_GOAL"
            report["next_safe_action"] = "Forex paper bot, backtest, ledger, strategy rules, data import, report, and decision policy validated. Commit and push still require approval."
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    state_path = Path(args.state_path).resolve() if args.state_path else None
    report = run_wake_continue(
        repo_root,
        goal=args.goal,
        apply=args.apply,
        max_cycles=args.max_cycles,
        max_repairs=args.max_repairs,
        state_path=state_path,
    )
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0 if report["result"] in {"DONE_FOR_CURRENT_GOAL", "passed", "preview_only", "blocked", "max_cycles_reached"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
