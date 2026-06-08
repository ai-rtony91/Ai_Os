from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from automation.operator_relief.approval_resume_loop import run_approval_resume_loop
from automation.operator_relief.autonomy_approval_processor import AUTO_ALLOWED, APPROVAL_REQUIRED, classify_approval
from automation.operator_relief.full_auto_policy import FullAutoTask
from automation.operator_relief.runtime_bridge import run_runtime_bridge


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "DIRTY"
    executable: bool = False


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "resume-001",
        "description": "Safe approval resume task",
        "allowed_paths": ["safe.py"],
        "forbidden_paths": ["AGENTS.md", "README.md", "docs/governance/**"],
        "changed_paths": ["safe.py"],
        "requested_actions": [],
        "validator_targets": ["safe.py"],
        "expected_branch": None,
    }
    data.update(overrides)
    return FullAutoTask(**data)


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "safe.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "reports/operator_relief/inbox").mkdir(parents=True)
    (tmp_path / "reports/operator_relief/outbox").mkdir(parents=True)
    (tmp_path / "automation/operator_relief/approval_input").mkdir(parents=True)
    return tmp_path


def _write_inbox(repo: Path, name: str, task: FullAutoTask) -> Path:
    path = repo / "reports/operator_relief/inbox" / name
    path.write_text(json.dumps(task.to_dict()), encoding="utf-8")
    return path


def _write_decision(repo: Path, runtime_report: dict, **overrides) -> Path:
    path = repo / "automation/operator_relief/approval_input/decision.json"
    payload = {
        "decision": "CONTINUE_MISSION",
        "task_id": "resume-001",
        "outbox_path": runtime_report["outbox_path"],
        "archive_path": runtime_report["archive_path"],
    }
    payload.update(overrides)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_resume_loop_requeues_approval_required_archived_task(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "approval.json", _task())
    runtime = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    decision = _write_decision(repo, runtime)

    report = run_approval_resume_loop(repo, decision).to_dict()

    assert report["status"] == "RESUME_TASK_QUEUED"
    assert Path(report["resume_inbox_path"]).is_file()
    resume_task = json.loads(Path(report["resume_inbox_path"]).read_text(encoding="utf-8"))
    assert resume_task["metadata"]["approval_resume"]["human_approved"] is True
    assert resume_task["metadata"]["approval_resume"]["validator_pass_is_not_approval"] is True
    assert report["safety"]["approval_files_mutated"] is False
    assert report["safety"]["resume_report_written"] is True
    assert report["executable"] is False


def test_resume_metadata_allows_non_protected_dirty_state_continuation(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    task = _task(
        metadata={
            "approval_resume": {
                "human_approved": True,
                "decision": "CONTINUE_MISSION",
                "task_id": "resume-001",
            }
        }
    )

    decision = classify_approval(task, FakeRepoState(repo_root=str(repo))).to_dict()

    assert decision["status"] == AUTO_ALLOWED
    assert decision["human_approval_required"] is False


def test_resume_metadata_does_not_allow_push(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    task = _task(
        requested_actions=["push"],
        metadata={
            "approval_resume": {
                "human_approved": True,
                "decision": "CONTINUE_MISSION",
                "task_id": "resume-001",
            }
        },
    )

    decision = classify_approval(task, FakeRepoState(repo_root=str(repo))).to_dict()

    assert decision["status"] == APPROVAL_REQUIRED
    assert decision["human_approval_required"] is True


def test_requeued_resume_task_can_complete_runtime_bridge_with_same_dirty_state(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "approval.json", _task())
    first = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    decision = _write_decision(repo, first)
    resume = run_approval_resume_loop(repo, decision).to_dict()

    second = run_runtime_bridge(
        repo,
        inbox_task_path=resume["resume_inbox_path"],
        repo_state=FakeRepoState(repo_root=str(repo)),
    ).to_dict()

    assert second["status"] == "RUNTIME_COMPLETE"
    bounded = second["bridge_report"]["executor_report"]["bounded_executor"]
    assert bounded["approval"]["status"] == AUTO_ALLOWED


def test_resume_blocks_replay_when_resume_output_exists(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "approval.json", _task())
    runtime = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    decision = _write_decision(repo, runtime)

    first = run_approval_resume_loop(repo, decision).to_dict()
    second = run_approval_resume_loop(repo, decision).to_dict()

    assert first["status"] == "RESUME_TASK_QUEUED"
    assert second["status"] == "RESUME_BLOCKED"
    assert "already exists" in second["reasons"][0]


def test_resume_blocks_consumed_approval(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "approval.json", _task())
    runtime = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    decision = _write_decision(repo, runtime, consumed=True)

    report = run_approval_resume_loop(repo, decision).to_dict()

    assert report["status"] == "RESUME_BLOCKED"
    assert "already consumed" in report["reasons"][0]


def test_resume_blocks_expired_approval(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "approval.json", _task())
    runtime = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    expired = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    decision = _write_decision(repo, runtime, expires_at=expired)

    report = run_approval_resume_loop(repo, decision).to_dict()

    assert report["status"] == "RESUME_BLOCKED"
    assert "expired" in report["reasons"][0]


def test_resume_accepts_unexpired_approval(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "approval.json", _task())
    runtime = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    unexpired = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    decision = _write_decision(repo, runtime, expires_at=unexpired)

    report = run_approval_resume_loop(repo, decision).to_dict()

    assert report["status"] == "RESUME_TASK_QUEUED"


def test_resume_blocks_when_outbox_was_not_approval_required(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "complete.json", _task())
    runtime = run_runtime_bridge(
        repo,
        repo_state=FakeRepoState(repo_root=str(repo), dirty_state="CLEAN"),
    ).to_dict()
    decision = _write_decision(repo, runtime)

    report = run_approval_resume_loop(repo, decision).to_dict()

    assert report["status"] == "RESUME_BLOCKED"
    assert "not stopped at approval-required" in report["reasons"][0]


def test_resume_source_has_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/approval_resume_loop.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "subprocess",
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
    ]
    for marker in forbidden_markers:
        assert marker not in source
