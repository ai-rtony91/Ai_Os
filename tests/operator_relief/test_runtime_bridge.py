from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.full_auto_policy import FullAutoTask
from automation.operator_relief.runtime_bridge import main, run_runtime_bridge


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"
    executable: bool = False


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "runtime-001",
        "description": "Safe runtime bridge task",
        "allowed_paths": ["safe.md"],
        "forbidden_paths": ["AGENTS.md", "README.md", "docs/governance/**"],
        "changed_paths": ["safe.md"],
        "requested_actions": [],
        "validator_targets": ["safe.md"],
        "expected_branch": None,
    }
    data.update(overrides)
    return FullAutoTask(**data)


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "safe.md").write_text("# safe\n", encoding="utf-8")
    (tmp_path / "reports/operator_relief/inbox").mkdir(parents=True)
    (tmp_path / "reports/operator_relief/outbox").mkdir(parents=True)
    return tmp_path


def _write_inbox(repo: Path, name: str, task: FullAutoTask) -> Path:
    path = repo / "reports/operator_relief/inbox" / name
    path.write_text(json.dumps(task.to_dict()), encoding="utf-8")
    return path


def test_valid_inbox_task_produces_outbox_report(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "task.json", _task())

    report = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "RUNTIME_COMPLETE"
    assert report["processed_count"] == 1
    assert Path(report["outbox_path"]).is_file()
    assert report["bridge_report"]["executor_report"]["status"] == "WRITE_COMPLETE"
    assert report["executable"] is False


def test_processed_task_archived(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "task.json", _task())

    report = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert not inbox.exists()
    assert Path(report["archive_path"]).is_file()
    assert "reports/operator_relief/archive/processed/task.processed.json" in report["archive_path"].replace("\\", "/")
    assert report["safety"]["inbox_task_archived"] is True


def test_blocked_task_handled_correctly(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "blocked.json", _task(live_trading=True))

    report = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "RUNTIME_BLOCKED_REPORTED"
    assert Path(report["outbox_path"]).is_file()
    assert Path(report["archive_path"]).is_file()
    bounded = report["bridge_report"]["executor_report"]["bounded_executor"]
    assert bounded["status"] == "STOPPED_BLOCKED"
    assert bounded["executable"] is False


def test_approval_required_task_handled_correctly(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "approval.json", _task())

    report = run_runtime_bridge(
        repo,
        repo_state=FakeRepoState(repo_root=str(repo), dirty_state="DIRTY"),
    ).to_dict()

    assert report["status"] == "RUNTIME_APPROVAL_REQUIRED_REPORTED"
    assert Path(report["outbox_path"]).is_file()
    assert Path(report["archive_path"]).is_file()
    bounded = report["bridge_report"]["executor_report"]["bounded_executor"]
    assert bounded["status"] == "STOPPED_APPROVAL_REQUIRED"


def test_duplicate_output_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "task.json", _task())
    outbox = repo / "reports/operator_relief/outbox/task.result.json"
    outbox.write_text("{}", encoding="utf-8")

    report = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "RUNTIME_BLOCKED"
    assert inbox.exists()
    assert report["archive_path"] is None
    assert "overwrite is not allowed" in report["reasons"][0]


def test_traversal_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    outside = repo / "reports/operator_relief/escape.json"
    outside.write_text("{}", encoding="utf-8")

    report = run_runtime_bridge(
        repo,
        inbox_task_path=outside,
        repo_state=FakeRepoState(repo_root=str(repo)),
    ).to_dict()

    assert report["status"] == "RUNTIME_BLOCKED"
    assert report["processed_count"] == 0
    assert report["bridge_report"] is None


def test_malformed_json_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = repo / "reports/operator_relief/inbox/broken.json"
    inbox.write_text("{not-json", encoding="utf-8")

    report = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "RUNTIME_BLOCKED"
    assert inbox.exists()
    assert report["archive_path"] is None
    assert "Malformed task JSON" in report["reasons"][0]


def test_oldest_task_selected_first(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    newer = _write_inbox(repo, "newer.json", _task(task_id="newer"))
    older = _write_inbox(repo, "older.json", _task(task_id="older"))
    os.utime(newer, (2000, 2000))
    os.utime(older, (1000, 1000))

    report = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["selected_inbox_path"].replace("\\", "/").endswith("/older.json")
    assert (repo / "reports/operator_relief/inbox/newer.json").exists()
    assert not older.exists()


def test_executable_false(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "task.json", _task())

    report = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["executable"] is False
    assert report["safety"]["executable"] is False
    assert report["bridge_report"]["executable"] is False


def test_runtime_bridge_source_has_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/runtime_bridge.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "shell=True",
        "subprocess",
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


def test_runtime_bridge_cli_runs_one_task(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    _write_inbox(repo, "task.json", _task())
    monkeypatch.chdir(repo)
    import automation.operator_relief.runtime_bridge as runtime_bridge

    monkeypatch.setattr(runtime_bridge, "collect_repo_state", lambda _root: FakeRepoState(repo_root=str(repo)))

    assert main([]) == 0
    assert (repo / "reports/operator_relief/outbox/task.result.json").is_file()
