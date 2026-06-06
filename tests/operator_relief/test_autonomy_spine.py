from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.autonomy_approval_processor import BLOCKED, classify_approval
from automation.operator_relief.autonomy_commit_push_gate import (
    COMMIT_RECOMMENDED,
    PUSH_REQUIRES_HUMAN_APPROVAL,
    evaluate_commit_push_gate,
)
from automation.operator_relief.autonomy_controller import run_autonomy_controller
from automation.operator_relief.autonomy_loop import run_bounded_autonomy_loop
from automation.operator_relief.autonomy_packet_generator import build_autonomy_packet_draft
from automation.operator_relief.autonomy_scheduler import plan_next_run
from automation.operator_relief.autonomy_task_discovery import discover_tasks
from automation.operator_relief.autonomy_validator_orchestrator import build_validator_plan, run_validator_plan
from automation.operator_relief.full_auto_policy import FullAutoTask


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"
    git_status: str = "## feature/full-operator-relief-closed-loop-v1...origin/feature/full-operator-relief-closed-loop-v1"
    remote: str = "origin https://github.com/ai-rtony91/Ai_Os.git (fetch)"
    agents_md_present: bool = True
    readme_present: bool = True
    created_at: str = "2026-06-06T00:00:00+00:00"
    executable: bool = False

    def to_dict(self) -> dict[str, object]:
        return dict(self.__dict__)


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "spine-001",
        "description": "Safe workflow doc readback",
        "allowed_paths": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "forbidden_paths": ["AGENTS.md", "README.md", "docs/governance/**"],
        "changed_paths": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "requested_actions": [],
        "validator_targets": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "expected_branch": "feature/full-operator-relief-closed-loop-v1",
    }
    data.update(overrides)
    return FullAutoTask(**data)


def _write_task(path: Path, task: FullAutoTask) -> None:
    path.write_text(json.dumps(task.to_dict()), encoding="utf-8")


def test_task_discovery_accepts_safe_local_task_json(tmp_path: Path) -> None:
    task_path = tmp_path / "safe_task.json"
    _write_task(task_path, _task())

    result = discover_tasks(task_file=task_path)

    assert result.status == "DISCOVERED"
    assert result.tasks[0].task.task_id == "spine-001"
    assert result.executable is False


def test_task_discovery_rejects_malformed_task(tmp_path: Path) -> None:
    task_path = tmp_path / "broken.json"
    task_path.write_text("{not-json", encoding="utf-8")

    result = discover_tasks(task_file=task_path)

    assert result.status == "BLOCKED"
    assert "Malformed task JSON" in result.rejected[0]["reason"]


def test_task_discovery_rejects_forbidden_path(tmp_path: Path) -> None:
    task_path = tmp_path / "forbidden.json"
    _write_task(task_path, _task(allowed_paths=["docs/governance/source-of-truth-map.md"]))

    result = discover_tasks(task_file=task_path)

    assert result.status == "BLOCKED"
    assert "forbidden" in result.rejected[0]["reason"].lower()


def test_packet_generator_includes_required_fields_but_remains_non_executable(tmp_path: Path) -> None:
    packet = build_autonomy_packet_draft(_task(), FakeRepoState(repo_root=str(tmp_path)), ["manual_review_markdown"])
    text = packet.draft_text

    for required in [
        "CODEX-ONLY PROMPT",
        "AI_OS EXECUTION TOKEN: PLACEHOLDER_REQUIRES_ANTHONY_APPROVAL",
        "AI_OS BOOTSTRAP REQUIRED: YES",
        "MODE: DRY_RUN",
        "LANE:",
        "WORKTREE:",
        "BRANCH:",
        "ALLOWED PATHS:",
        "FORBIDDEN PATHS:",
        "APPROVAL AUTHORITY:",
        "VALIDATOR CHAIN:",
        "STOP POINT:",
        "FINAL REPORT FORMAT:",
    ]:
        assert required in text
    assert packet.executable is False


def test_validator_orchestration_plans_and_runs_only_allowed_validators(tmp_path: Path) -> None:
    doc = tmp_path / "safe.md"
    doc.write_text("# safe\n", encoding="utf-8")
    task = _task(
        allowed_paths=["safe.md"],
        changed_paths=["safe.md"],
        validator_targets=["safe.md"],
        expected_branch=None,
    )

    plan = build_validator_plan(task)
    result = run_validator_plan(task, repo_root=tmp_path)

    assert plan.status == "PLANNED"
    assert plan.plan[0].validator == "manual_review_markdown"
    assert result.status == "PASSED"
    assert result.results[0]["command"] is None


def test_approval_processor_blocks_protected_paths(tmp_path: Path) -> None:
    task = _task(
        allowed_paths=["docs/governance/source-of-truth-map.md"],
        changed_paths=["docs/governance/source-of-truth-map.md"],
        validator_targets=["docs/governance/source-of-truth-map.md"],
    )

    decision = classify_approval(task, FakeRepoState(repo_root=str(tmp_path)))

    assert decision.status == BLOCKED


def test_execution_controller_stops_on_blocked_task(tmp_path: Path) -> None:
    report = run_autonomy_controller(_task(live_trading=True), FakeRepoState(repo_root=str(tmp_path)), tmp_path)

    assert report.status == "STOPPED_BLOCKED"
    assert report.executable is False


def test_execution_controller_stops_on_approval_required_task(tmp_path: Path) -> None:
    repo_state = FakeRepoState(repo_root=str(tmp_path), dirty_state="DIRTY")
    report = run_autonomy_controller(_task(), repo_state, tmp_path)

    assert report.status == "STOPPED_APPROVAL_REQUIRED"
    assert report.approval["status"] == "APPROVAL_REQUIRED"
    assert report.validator_plan["results"] == []


def test_execution_controller_handles_allowed_task_through_validator_plan(tmp_path: Path) -> None:
    doc = tmp_path / "safe.md"
    doc.write_text("# safe\n", encoding="utf-8")
    task = _task(
        allowed_paths=["safe.md"],
        changed_paths=["safe.md"],
        validator_targets=["safe.md"],
        expected_branch=None,
    )

    report = run_autonomy_controller(task, FakeRepoState(repo_root=str(tmp_path)), tmp_path)

    assert report.status == "DRY_RUN_COMPLETE"
    assert report.validator_plan["status"] == "PASSED"
    assert report.commit_push_gate["status"] == COMMIT_RECOMMENDED


def test_scheduler_scaffold_does_not_start_daemon_or_service() -> None:
    schedule = plan_next_run(max_steps=2).to_dict()

    assert schedule["mode"] == "SCAFFOLD_ONLY"
    assert schedule["daemon_started"] is False
    assert schedule["service_registered"] is False
    assert schedule["background_watcher_started"] is False


def test_commit_push_gate_never_executes_git_commit_or_push(tmp_path: Path) -> None:
    push_decision = evaluate_commit_push_gate(
        _task(requested_actions=["push"], push_allowed=True),
        FakeRepoState(repo_root=str(tmp_path)),
        validators_passed=True,
    )

    assert push_decision.status == PUSH_REQUIRES_HUMAN_APPROVAL
    assert push_decision.commit_executed is False
    assert push_decision.push_executed is False


def test_multi_step_loop_stops_at_max_steps(tmp_path: Path) -> None:
    doc = tmp_path / "safe.md"
    doc.write_text("# safe\n", encoding="utf-8")
    task = _task(
        allowed_paths=["safe.md"],
        changed_paths=["safe.md"],
        validator_targets=["safe.md"],
        expected_branch=None,
    )

    report = run_bounded_autonomy_loop([task, task, task], FakeRepoState(repo_root=str(tmp_path)), tmp_path, max_steps=2)

    assert report.processed_count == 2
    assert report.stop_reason == "MAX_STEPS_REACHED"


def test_multi_step_loop_stops_on_first_blocked_task(tmp_path: Path) -> None:
    report = run_bounded_autonomy_loop(
        [_task(live_trading=True), _task()],
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        max_steps=3,
    )

    assert report.processed_count == 1
    assert report.stop_reason == "STOPPED_BLOCKED"


def test_autonomy_spine_source_has_no_unbounded_execution_paths() -> None:
    files = [
        Path("automation/operator_relief/autonomy_task_discovery.py"),
        Path("automation/operator_relief/autonomy_packet_generator.py"),
        Path("automation/operator_relief/autonomy_validator_orchestrator.py"),
        Path("automation/operator_relief/autonomy_approval_processor.py"),
        Path("automation/operator_relief/autonomy_commit_push_gate.py"),
        Path("automation/operator_relief/autonomy_scheduler.py"),
        Path("automation/operator_relief/autonomy_controller.py"),
        Path("automation/operator_relief/autonomy_loop.py"),
    ]
    source = "\n".join(path.read_text(encoding="utf-8") for path in files)

    forbidden_markers = [
        "shell=True",
        "os.system",
        "Popen",
        "OpenAI(",
        "openai.",
        "Codex(",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "Start-Process",
        "Task Scheduler",
        "cron",
    ]
    for marker in forbidden_markers:
        assert marker not in source
