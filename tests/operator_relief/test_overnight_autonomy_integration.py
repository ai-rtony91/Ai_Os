from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.adb_alert_smoke_harness import run_adb_alert_smoke_harness
from automation.operator_relief.adb_escalation import MODE_APPLY_ADB_ALERT, AdbAlertCommandResult
from automation.operator_relief.auto_commit_push_executor import FEATURE_BRANCH, GitCommandResult
from automation.operator_relief.commit_push_smoke_harness import MODE_APPLY_SMOKE, run_commit_push_smoke_harness
from automation.operator_relief.merge_approval_gate import (
    MERGE_READY_FOR_HUMAN,
    MERGE_REQUIRES_APPROVAL,
    evaluate_merge_approval_gate,
)
from automation.operator_relief.overnight_scheduler import MODE_APPLY_SCHEDULE_PLAN, ScheduleCommandResult, plan_overnight_schedule
from automation.operator_relief.approval_station import read_approval_decision


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = FEATURE_BRANCH
    dirty_state: str = "CLEAN"
    executable: bool = False


def test_commit_push_smoke_harness_blocks_unless_explicit_safe_mode(tmp_path: Path) -> None:
    blocked = run_commit_push_smoke_harness(tmp_path, mode="APPLY_COMMIT_PUSH").to_dict()
    apply_without_runner = run_commit_push_smoke_harness(tmp_path, mode=MODE_APPLY_SMOKE).to_dict()

    assert blocked["status"] == "SMOKE_BLOCKED"
    assert apply_without_runner["status"] == "SMOKE_BLOCKED"
    assert blocked["executable"] is False
    assert apply_without_runner["executable"] is False


def test_commit_push_smoke_harness_stages_exact_approved_file_only(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def runner(_root: Path, command: list[str]) -> GitCommandResult:
        commands.append(command)
        return GitCommandResult(command, 0, "ok", "")

    report = run_commit_push_smoke_harness(tmp_path, mode=MODE_APPLY_SMOKE, command_runner=runner).to_dict()

    assert report["status"] == "SMOKE_APPLY_COMPLETE"
    assert commands[0] == ["git", "add", "--", "automation/operator_relief/generated_smoke/auto_commit_push_smoke.txt"]
    assert commands[2] == ["git", "push", "origin", FEATURE_BRANCH]
    assert report["executable"] is True


def test_adb_alert_harness_defaults_dry_run() -> None:
    report = run_adb_alert_smoke_harness().to_dict()

    assert report["status"] == "ADB_SMOKE_DRY_RUN"
    assert report["mode"] == "DRY_RUN"
    assert report["escalation_report"]["command_result"] is None
    assert report["executable"] is False


def test_adb_alert_apply_mode_is_gated_and_calls_only_existing_wake_script_path() -> None:
    commands: list[list[str]] = []

    def runner(command: list[str]) -> AdbAlertCommandResult:
        commands.append(command)
        return AdbAlertCommandResult(command, 0, "sent", "")

    report = run_adb_alert_smoke_harness(mode=MODE_APPLY_ADB_ALERT, command_runner=runner).to_dict()

    assert report["status"] == "ADB_SMOKE_APPLY_COMPLETE"
    assert commands == [["powershell", "-ExecutionPolicy", "Bypass", "-File", "tools/android/Send-AiosAdbSosWake.ps1"]]
    assert report["network_listener_started"] is False
    assert report["port_opened"] is False
    assert report["executable"] is True


def test_approval_station_accepts_approve_reject_hold_from_local_json(tmp_path: Path) -> None:
    root = tmp_path / "automation/operator_relief/approval_input"
    root.mkdir(parents=True)
    for decision in ("APPROVE", "REJECT", "HOLD"):
        path = root / f"{decision.lower()}.json"
        path.write_text(json.dumps({"decision": decision, "task_id": "overnight"}), encoding="utf-8")

        report = read_approval_decision(tmp_path, path).to_dict()

        assert report["status"] == "APPROVAL_DECISION_ACCEPTED"
        assert report["decision"] == decision
        assert report["network_listener_started"] is False


def test_approval_station_rejects_traversal_malformed_unknown_action(tmp_path: Path) -> None:
    outside = tmp_path / "approval.json"
    outside.write_text(json.dumps({"decision": "APPROVE"}), encoding="utf-8")
    root = tmp_path / "automation/operator_relief/approval_input"
    root.mkdir(parents=True)
    malformed = root / "malformed.json"
    malformed.write_text("{not-json", encoding="utf-8")
    unknown = root / "unknown.json"
    unknown.write_text(json.dumps({"decision": "LAUNCH"}), encoding="utf-8")

    assert read_approval_decision(tmp_path, outside).status == "APPROVAL_BLOCKED"
    assert read_approval_decision(tmp_path, malformed).status == "APPROVAL_BLOCKED"
    assert read_approval_decision(tmp_path, unknown).status == "APPROVAL_BLOCKED"


def test_scheduler_produces_task_plan_without_registering_by_default() -> None:
    report = plan_overnight_schedule(max_cycles=3).to_dict()

    assert report["status"] == "SCHEDULE_PLAN_READY"
    assert report["launch_command"] == [".\\aios.ps1", "-Mode", "night-mission", "-MaxCycles", "3"]
    assert report["command_result"] is None
    assert report["daemon_started"] is False
    assert report["watcher_started"] is False
    assert report["background_service_started"] is False
    assert report["executable"] is False


def test_scheduler_apply_mode_is_gated() -> None:
    commands: list[list[str]] = []

    def runner(command: list[str]) -> ScheduleCommandResult:
        commands.append(command)
        return ScheduleCommandResult(command, 0, "planned", "")

    report = plan_overnight_schedule(max_cycles=3, mode=MODE_APPLY_SCHEDULE_PLAN, schedule_runner=runner).to_dict()

    assert report["status"] == "SCHEDULE_PLAN_APPLIED"
    assert report["command_result"] is not None
    assert commands[0][0] == "schtasks.exe"
    assert report["daemon_started"] is False
    assert report["watcher_started"] is False


def test_merge_gate_never_executes_merge_and_requires_human_approval(tmp_path: Path) -> None:
    state = FakeRepoState(repo_root=str(tmp_path))
    requires = evaluate_merge_approval_gate(state, validators_passed=True, pr_ready=True).to_dict()
    ready = evaluate_merge_approval_gate(
        state,
        validators_passed=True,
        pr_ready=True,
        human_approval_present=True,
    ).to_dict()

    assert requires["status"] == MERGE_REQUIRES_APPROVAL
    assert ready["status"] == MERGE_READY_FOR_HUMAN
    assert requires["merge_executed"] is False
    assert ready["merge_executed"] is False
    assert ready["executable"] is False


def test_overnight_integration_sources_have_no_forbidden_runtime_markers() -> None:
    files = [
        Path("automation/operator_relief/commit_push_smoke_harness.py"),
        Path("automation/operator_relief/adb_alert_smoke_harness.py"),
        Path("automation/operator_relief/overnight_scheduler.py"),
        Path("automation/operator_relief/merge_approval_gate.py"),
    ]
    source = "\n".join(path.read_text(encoding="utf-8") for path in files)
    forbidden_markers = [
        "OPENAI_API_KEY",
        "OpenAI(",
        "openai.",
        "Codex(",
        "socket.",
        "HTTPServer",
        "TCPServer",
        ".bind(",
        ".listen(",
        "live_trading",
        "order_execution",
        "--force",
        "git rebase",
        "git merge",
    ]
    for marker in forbidden_markers:
        assert marker not in source
