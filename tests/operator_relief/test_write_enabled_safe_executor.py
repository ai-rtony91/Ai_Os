from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.full_auto_policy import FullAutoTask
from automation.operator_relief.write_enabled_safe_executor import run_write_enabled_safe_executor


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"
    executable: bool = False


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "write-safe-001",
        "description": "Safe write report task",
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
    return tmp_path


def test_report_writes_only_inside_reports_operator_relief(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(),
        FakeRepoState(repo_root=str(repo)),
        repo,
        "reports/operator_relief/report.json",
    ).to_dict()

    assert report["status"] == "WRITE_COMPLETE"
    assert report["write_performed"] is True
    assert Path(report["report_path"]).is_file()
    assert "reports/operator_relief/report.json" in report["report_path"].replace("\\", "/")


def test_path_traversal_is_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(),
        FakeRepoState(repo_root=str(repo)),
        repo,
        "reports/operator_relief/../escape.json",
    ).to_dict()

    assert report["status"] == "WRITE_BLOCKED"
    assert report["write_performed"] is False


def test_overwrite_is_blocked_by_default(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    output = "reports/operator_relief/report.json"
    first = run_write_enabled_safe_executor(_task(), FakeRepoState(repo_root=str(repo)), repo, output).to_dict()
    second = run_write_enabled_safe_executor(_task(), FakeRepoState(repo_root=str(repo)), repo, output).to_dict()

    assert first["status"] == "WRITE_COMPLETE"
    assert second["status"] == "WRITE_BLOCKED"
    assert second["write_performed"] is False


def test_overwrite_requires_explicit_flag(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    output = "reports/operator_relief/report.json"
    run_write_enabled_safe_executor(_task(), FakeRepoState(repo_root=str(repo)), repo, output)
    report = run_write_enabled_safe_executor(
        _task(),
        FakeRepoState(repo_root=str(repo)),
        repo,
        output,
        overwrite=True,
    ).to_dict()

    assert report["status"] == "WRITE_COMPLETE"
    assert report["write_performed"] is True


def test_source_file_write_is_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(),
        FakeRepoState(repo_root=str(repo)),
        repo,
        "automation/operator_relief/source.json",
    ).to_dict()

    assert report["status"] == "WRITE_BLOCKED"
    assert report["write_performed"] is False


def test_protected_paths_are_blocked(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(),
        FakeRepoState(repo_root=str(repo)),
        repo,
        "docs/governance/report.json",
    ).to_dict()

    assert report["status"] == "WRITE_BLOCKED"
    assert report["write_performed"] is False


def test_blocked_task_does_not_write_without_failure_evidence_flag(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(live_trading=True),
        FakeRepoState(repo_root=str(repo)),
        repo,
        "reports/operator_relief/blocked.json",
    ).to_dict()

    assert report["status"] == "WRITE_SKIPPED"
    assert report["write_performed"] is False


def test_blocked_task_can_write_report_only_failure_evidence_when_explicitly_allowed(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(live_trading=True),
        FakeRepoState(repo_root=str(repo)),
        repo,
        "reports/operator_relief/blocked.json",
        allow_failure_report=True,
    ).to_dict()

    assert report["status"] == "WRITE_COMPLETE"
    assert report["write_performed"] is True
    assert report["bounded_executor"]["status"] == "STOPPED_BLOCKED"


def test_approval_required_task_does_not_write_without_failure_evidence_flag(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(),
        FakeRepoState(repo_root=str(repo), dirty_state="DIRTY"),
        repo,
        "reports/operator_relief/approval.json",
    ).to_dict()

    assert report["status"] == "WRITE_SKIPPED"
    assert report["write_performed"] is False


def test_executable_false(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = run_write_enabled_safe_executor(
        _task(),
        FakeRepoState(repo_root=str(repo)),
        repo,
        "reports/operator_relief/report.json",
    ).to_dict()

    assert report["executable"] is False
    assert report["safety"]["executable"] is False


def test_write_enabled_source_has_no_forbidden_execution_paths() -> None:
    source = Path("automation/operator_relief/write_enabled_safe_executor.py").read_text(encoding="utf-8")
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
