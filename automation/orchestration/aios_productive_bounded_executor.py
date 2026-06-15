from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable


SCHEMA = "AIOS_PRODUCTIVE_BOUNDED_EXECUTOR.v1"
SUPPORTED_GOALS = {"forex-paper-bot"}
SUPPORTED_ACTIONS = {"build_forex_risk_controls"}

FOREX_RISK_CONTROLS_PATH = Path("apps/trading_lab/trading_lab/forex_risk_controls.py")
FOREX_RISK_CONTROLS_TEST_PATH = Path("tests/trading_lab/test_forex_risk_controls.py")
FOREX_RISK_CONTROLS_DOC_PATH = Path("docs/orchestration/AIOS_FOREX_RISK_CONTROLS.md")

WRITE_ALLOWED_PATHS = {
    FOREX_RISK_CONTROLS_PATH.as_posix(),
    FOREX_RISK_CONTROLS_TEST_PATH.as_posix(),
    FOREX_RISK_CONTROLS_DOC_PATH.as_posix(),
}

HANDOFF_ALLOWED_PATHS = {
    *WRITE_ALLOWED_PATHS,
    "automation/orchestration/aios_autonomy_execute.py",
    "tests/orchestration/test_aios_autonomy_execute.py",
    "automation/orchestration/aios_wake_continue.py",
    "tests/orchestration/test_aios_wake_continue.py",
}

ValidatorRunner = Callable[[Path], dict[str, Any]]


def safety_flags() -> dict[str, bool]:
    return {
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "scheduler": False,
        "daemon": False,
        "background_runtime": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "chatgpt_api_call": False,
        "codex_launch": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "network_access": False,
    }


def approval_required() -> dict[str, bool]:
    return {
        "local_allowlisted_apply": False,
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
    }


def _repo_template_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _template_text(relative_path: Path) -> str:
    template_path = _repo_template_root() / relative_path
    return template_path.read_text(encoding="utf-8")


def risk_controls_files() -> dict[Path, str]:
    return {
        FOREX_RISK_CONTROLS_PATH: _template_text(FOREX_RISK_CONTROLS_PATH),
        FOREX_RISK_CONTROLS_TEST_PATH: _template_text(FOREX_RISK_CONTROLS_TEST_PATH),
        FOREX_RISK_CONTROLS_DOC_PATH: _template_text(FOREX_RISK_CONTROLS_DOC_PATH),
    }


def _is_bounded_relative_path(path_text: str, allowed_paths: set[str]) -> bool:
    if not path_text or "\\" in path_text:
        return False
    path = PurePosixPath(path_text)
    if path.is_absolute() or ".." in path.parts:
        return False
    return path_text in allowed_paths


def validate_handoff_scope(action: str, handoff: dict[str, Any] | None = None) -> tuple[bool, str, list[str]]:
    if action not in SUPPORTED_ACTIONS:
        return False, "unsupported_action", []

    if handoff is None:
        return True, "scope_valid", sorted(HANDOFF_ALLOWED_PATHS)

    allowed_paths = handoff.get("allowed_paths", [])
    if not isinstance(allowed_paths, list):
        return False, "allowed_paths_not_list", []
    allowed_paths_text = [str(path) for path in allowed_paths]
    if not allowed_paths_text:
        return False, "allowed_paths_missing", []
    if not all(_is_bounded_relative_path(path, HANDOFF_ALLOWED_PATHS) for path in allowed_paths_text):
        return False, "unbounded_path", allowed_paths_text
    if not WRITE_ALLOWED_PATHS.issubset(set(allowed_paths_text)):
        return False, "write_paths_not_authorized_by_handoff", allowed_paths_text
    return True, "scope_valid", allowed_paths_text


def write_text_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def write_risk_controls_files(repo_root: Path) -> list[str]:
    files_written: list[str] = []
    for relative_path, content in risk_controls_files().items():
        if relative_path.as_posix() not in WRITE_ALLOWED_PATHS:
            raise ValueError("write_path_not_allowlisted")
        target = repo_root / relative_path
        if write_text_if_changed(target, content):
            files_written.append(relative_path.as_posix())
    return files_written


def run_risk_controls_validator(repo_root: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        FOREX_RISK_CONTROLS_TEST_PATH.as_posix(),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": "forex_risk_controls_tests",
        "command": " ".join(command),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def _blocked_report(goal: str, action: str, mode: str, reason: str, allowed_paths: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": goal,
        "action": action,
        "mode": mode,
        "allowed_paths": allowed_paths or [],
        "files_written": [],
        "validators_run": [],
        "repair_attempts": 0,
        "result": "blocked",
        "blocked_reason": reason,
        "next_safe_action": "Stop and repair the bounded executor request before local apply.",
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }


def execute_productive_bounded_action(
    repo_root: Path,
    *,
    goal: str = "forex-paper-bot",
    action: str | None = None,
    handoff: dict[str, Any] | None = None,
    apply: bool = False,
    max_repairs: int = 0,
    validator_runner: ValidatorRunner | None = None,
) -> dict[str, Any]:
    if handoff is not None:
        goal = str(handoff.get("goal", goal))
        action = str(handoff.get("allowed_action", action or ""))
    action = action or ""
    mode = "APPLY" if apply else "DRY_RUN"

    if goal not in SUPPORTED_GOALS:
        return _blocked_report(goal, action, mode, "unsupported_goal")
    if max_repairs < 0:
        return _blocked_report(goal, action, mode, "max_repairs_must_be_non_negative")

    scope_valid, reason_code, allowed_paths = validate_handoff_scope(action, handoff)
    if not scope_valid:
        return _blocked_report(goal, action, mode, reason_code, allowed_paths)

    report = {
        "schema": SCHEMA,
        "goal": goal,
        "action": action,
        "mode": mode,
        "allowed_paths": allowed_paths,
        "files_written": [],
        "validators_run": [],
        "repair_attempts": 0,
        "result": "preview_only",
        "next_safe_action": "Run with --apply only inside the approved risk-controls write boundary.",
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }

    if not apply:
        return report

    runner = validator_runner or run_risk_controls_validator
    report["files_written"] = write_risk_controls_files(repo_root)
    validation = runner(repo_root)
    report["validators_run"].append(validation)

    while not validation.get("passed", False) and report["repair_attempts"] < max_repairs:
        report["repair_attempts"] += 1
        repaired_files = write_risk_controls_files(repo_root)
        for relative_path in repaired_files:
            if relative_path not in report["files_written"]:
                report["files_written"].append(relative_path)
        validation = runner(repo_root)
        report["validators_run"].append(validation)

    if validation.get("passed", False):
        report["result"] = "passed"
        report["next_safe_action"] = "Review the risk-controls diff. Staging, commit, push, and merge require Anthony approval."
    else:
        report["result"] = "failed"
        report["next_safe_action"] = "Inspect risk-controls validator output before another bounded repair."
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one productive bounded AIOS executor action.")
    parser.add_argument("--goal", required=True, help="Supported goal: forex-paper-bot.")
    parser.add_argument("--action", required=True, help="Supported action: build_forex_risk_controls.")
    parser.add_argument("--apply", action="store_true", help="Write allowlisted risk-control files and run validators.")
    parser.add_argument("--max-repairs", type=int, default=0, help="Maximum deterministic repair attempts.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root for tests.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    report = execute_productive_bounded_action(
        repo_root,
        goal=args.goal,
        action=args.action,
        apply=args.apply,
        max_repairs=args.max_repairs,
    )
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0 if report["result"] in {"passed", "preview_only"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
