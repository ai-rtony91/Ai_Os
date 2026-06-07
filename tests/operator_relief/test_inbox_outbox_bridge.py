from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.full_auto_policy import FullAutoTask
from automation.operator_relief.inbox_outbox_bridge import run_inbox_outbox_bridge


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"
    executable: bool = False


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "bridge-001",
        "description": "Safe inbox outbox task",
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


def test_valid_inbox_task_produces_outbox_json(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "task.json", _task())

    report = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "BRIDGE_COMPLETE"
    assert report["executor_report"]["status"] == "WRITE_COMPLETE"
    assert Path(report["outbox_path"]).is_file()
    assert "reports/operator_relief/outbox/task.result.json" in report["outbox_path"].replace("\\", "/")
    assert report["executable"] is False


def test_traversal_is_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    outside = repo / "reports/operator_relief/escape.json"
    outside.write_text("{}", encoding="utf-8")

    report = run_inbox_outbox_bridge(repo, outside, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "BRIDGE_BLOCKED"
    assert report["executor_report"] is None


def test_malformed_inbox_json_is_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = repo / "reports/operator_relief/inbox/broken.json"
    inbox.write_text("{not-json", encoding="utf-8")

    report = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "BRIDGE_BLOCKED"
    assert "Malformed task JSON" in report["reasons"][0]


def test_non_json_is_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = repo / "reports/operator_relief/inbox/task.txt"
    inbox.write_text("not json", encoding="utf-8")

    report = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "BRIDGE_BLOCKED"
    assert "must be a .json" in report["reasons"][0]


def test_overwrite_is_blocked_by_default(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "task.json", _task())

    first = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    second = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert first["status"] == "BRIDGE_COMPLETE"
    assert second["status"] == "BRIDGE_BLOCKED"
    assert second["executor_report"]["status"] == "WRITE_BLOCKED"


def test_blocked_task_writes_failure_report_only_when_explicitly_allowed(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "blocked.json", _task(live_trading=True))

    blocked = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()
    allowed = run_inbox_outbox_bridge(
        repo,
        inbox,
        outbox_path="reports/operator_relief/outbox/blocked-allowed.json",
        allow_failure_report=True,
        repo_state=FakeRepoState(repo_root=str(repo)),
    ).to_dict()

    assert blocked["status"] == "BRIDGE_BLOCKED"
    assert blocked["executor_report"]["status"] == "WRITE_SKIPPED"
    assert allowed["status"] == "BRIDGE_COMPLETE"
    assert Path(allowed["outbox_path"]).is_file()


def test_placeholder_task_is_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "placeholder.json", _task(description="TODO"))

    report = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "BRIDGE_BLOCKED"
    assert "placeholder" in report["reasons"][0].lower()


def test_broker_api_live_trading_path_is_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "broker.json", _task(allowed_paths=["api/order_execution.json"]))

    report = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["status"] == "BRIDGE_BLOCKED"
    assert "broker/api" in report["reasons"][0].lower()


def test_executable_false(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = _write_inbox(repo, "task.json", _task())

    report = run_inbox_outbox_bridge(repo, inbox, repo_state=FakeRepoState(repo_root=str(repo))).to_dict()

    assert report["executable"] is False
    assert report["safety"]["executable"] is False


def test_bridge_source_has_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/inbox_outbox_bridge.py").read_text(encoding="utf-8")
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
