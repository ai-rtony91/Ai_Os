from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from automation.operator_relief.adb_escalation import MODE_DRY_RUN, plan_adb_escalation
from automation.operator_relief.approval_station import read_approval_decision
from automation.operator_relief.mission_scheduler import plan_mission_schedule
from automation.operator_relief.runtime_bridge import RuntimeBridgeReport
from automation.operator_relief.unattended_mission_runner import run_unattended_mission


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"
    executable: bool = False


def _runtime_report(status: str, processed_count: int = 0) -> RuntimeBridgeReport:
    return RuntimeBridgeReport(
        status=status,
        selected_inbox_path=None,
        outbox_path=None,
        archive_path=None,
        bridge_report=None,
        pipeline=["task_discovery"],
        processed_count=processed_count,
        reasons=[],
        safety={"executable": False},
        executable=False,
    )


def test_scheduler_returns_metadata_and_starts_no_background_process() -> None:
    now = datetime(2026, 6, 7, 0, 0, tzinfo=timezone.utc)

    plan = plan_mission_schedule(interval_minutes=30, max_cycles=2, now=now).to_dict()

    assert plan["mode"] == "SCAFFOLD_ONLY"
    assert plan["next_run_at"] == "2026-06-07T00:30:00+00:00"
    assert plan["task_scheduler_registered"] is False
    assert plan["background_process_started"] is False
    assert plan["executable"] is False


def test_approval_station_accepts_valid_decision_json(tmp_path: Path) -> None:
    approval_root = tmp_path / "automation/operator_relief/approval_input"
    approval_root.mkdir(parents=True)
    decision = approval_root / "decision.json"
    decision.write_text(json.dumps({"decision": "APPROVE", "task_id": "task-1"}), encoding="utf-8")

    report = read_approval_decision(tmp_path, decision).to_dict()

    assert report["status"] == "APPROVAL_DECISION_ACCEPTED"
    assert report["decision"] == "APPROVE"
    assert report["network_listener_started"] is False
    assert report["port_opened"] is False
    assert report["executable"] is False


def test_approval_station_rejects_traversal(tmp_path: Path) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"decision": "APPROVE"}), encoding="utf-8")

    report = read_approval_decision(tmp_path, outside).to_dict()

    assert report["status"] == "APPROVAL_BLOCKED"
    assert "must stay inside" in report["reasons"][0]


def test_approval_station_rejects_malformed_json(tmp_path: Path) -> None:
    approval_root = tmp_path / "automation/operator_relief/approval_input"
    approval_root.mkdir(parents=True)
    decision = approval_root / "broken.json"
    decision.write_text("{not-json", encoding="utf-8")

    report = read_approval_decision(tmp_path, decision).to_dict()

    assert report["status"] == "APPROVAL_BLOCKED"
    assert "Malformed approval JSON" in report["reasons"][0]


def test_approval_station_rejects_unknown_decision(tmp_path: Path) -> None:
    approval_root = tmp_path / "automation/operator_relief/approval_input"
    approval_root.mkdir(parents=True)
    decision = approval_root / "unknown.json"
    decision.write_text(json.dumps({"decision": "ESCALATE"}), encoding="utf-8")

    report = read_approval_decision(tmp_path, decision).to_dict()

    assert report["status"] == "APPROVAL_BLOCKED"
    assert "Unknown approval decision." in report["reasons"]


def test_adb_escalation_plans_alert_on_required_triggers() -> None:
    for trigger in ("approval_required", "blocked", "validator_failed"):
        report = plan_adb_escalation(trigger).to_dict()

        assert report["status"] == "ADB_ALERT_PLANNED"
        assert report["alert_required"] is True
        assert "tools/android/Send-AiosAdbSosWake.ps1" in report["script_path"]
        assert report["external_messaging_dependency"] is False
        assert report["executable"] is False


def test_adb_escalation_does_not_execute_by_default() -> None:
    report = plan_adb_escalation("blocked", mode=MODE_DRY_RUN).to_dict()

    assert report["command_result"] is None
    assert report["executable"] is False


def test_unattended_mission_runner_stops_on_no_inbox_task(tmp_path: Path) -> None:
    report = run_unattended_mission(
        tmp_path,
        runtime_runner=lambda _root, _state: _runtime_report("RUNTIME_NO_TASKS"),
        repo_state_provider=lambda root: FakeRepoState(repo_root=str(root)),
    ).to_dict()

    assert report["status"] == "MISSION_STOPPED"
    assert report["stop_reason"] == "NO_INBOX_TASK"
    assert report["processed_cycles"] == 1
    assert report["executable"] is False


def test_unattended_mission_runner_stops_on_approval_required(tmp_path: Path) -> None:
    report = run_unattended_mission(
        tmp_path,
        runtime_runner=lambda _root, _state: _runtime_report("RUNTIME_APPROVAL_REQUIRED_REPORTED", 1),
        repo_state_provider=lambda root: FakeRepoState(repo_root=str(root)),
    ).to_dict()

    assert report["stop_reason"] == "RUNTIME_APPROVAL_REQUIRED_REPORTED"
    assert report["adb_escalation"]["status"] == "ADB_ALERT_PLANNED"
    assert report["adb_escalation"]["trigger"] == "approval_required"


def test_unattended_mission_runner_honors_max_cycles(tmp_path: Path) -> None:
    report = run_unattended_mission(
        tmp_path,
        max_cycles=2,
        runtime_runner=lambda _root, _state: _runtime_report("RUNTIME_COMPLETE", 1),
        repo_state_provider=lambda root: FakeRepoState(repo_root=str(root)),
    ).to_dict()

    assert report["stop_reason"] == "MAX_CYCLES_REACHED"
    assert report["processed_cycles"] == 2


def test_unattended_mission_runner_does_not_commit_push_or_merge_by_default(tmp_path: Path) -> None:
    report = run_unattended_mission(
        tmp_path,
        runtime_runner=lambda _root, _state: _runtime_report("RUNTIME_NO_TASKS"),
        repo_state_provider=lambda root: FakeRepoState(repo_root=str(root)),
    ).to_dict()

    assert report["commit_push_attempted"] is False
    assert report["commit_executed"] is False
    assert report["push_executed"] is False
    assert report["protected_git_action_executed"] is False


def test_night_mission_sources_have_no_unbounded_runtime_paths() -> None:
    files = [
        Path("automation/operator_relief/mission_scheduler.py"),
        Path("automation/operator_relief/approval_station.py"),
        Path("automation/operator_relief/adb_escalation.py"),
        Path("automation/operator_relief/unattended_mission_runner.py"),
    ]
    source = "\n".join(path.read_text(encoding="utf-8") for path in files)
    forbidden_markers = [
        "socket.",
        "HTTPServer",
        "TCPServer",
        ".bind(",
        ".listen(",
        "OPENAI_API_KEY",
        "OpenAI(",
        "openai.",
        "Codex(",
        "Start-Job",
        "Register-ScheduledTask",
        "New-Service",
        "git merge",
        "git rebase",
        "force_push",
        "--force",
    ]
    for marker in forbidden_markers:
        assert marker not in source
