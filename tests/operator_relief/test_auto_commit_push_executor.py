from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.auto_commit_push_executor import (
    FEATURE_BRANCH,
    FEATURE_UPSTREAM,
    MODE_APPLY_COMMIT_PUSH,
    MODE_DRY_RUN,
    GitCommandResult,
    run_auto_commit_push_executor,
)
from automation.operator_relief.full_auto_policy import FullAutoTask


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = FEATURE_BRANCH
    git_status: str = f"## {FEATURE_BRANCH}...{FEATURE_UPSTREAM}\n M safe.md"
    dirty_state: str = "DIRTY"
    executable: bool = False


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "closeout-001",
        "description": "Safe operator relief closeout",
        "allowed_paths": ["safe.md"],
        "forbidden_paths": ["AGENTS.md", "README.md", "docs/governance/**"],
        "changed_paths": ["safe.md"],
        "requested_actions": [],
        "validator_targets": ["safe.md"],
        "expected_branch": FEATURE_BRANCH,
    }
    data.update(overrides)
    return FullAutoTask(**data)


def test_dry_run_reports_commands_only(tmp_path: Path) -> None:
    report = run_auto_commit_push_executor(
        _task(),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        validators_passed=True,
        mode=MODE_DRY_RUN,
    ).to_dict()

    assert report["status"] == "DRY_RUN_RECOMMENDED"
    assert report["commands"] == [
        ["git", "add", "--", "safe.md"],
        ["git", "commit", "-m", "operator relief: closeout-001"],
        ["git", "push", "origin", FEATURE_BRANCH],
    ]
    assert report["command_results"] == []
    assert report["push_target"] == FEATURE_UPSTREAM
    assert report["executable"] is False


def test_apply_mode_stages_only_approved_files(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def runner(_root: Path, command: list[str]) -> GitCommandResult:
        commands.append(command)
        return GitCommandResult(command, 0, "ok", "")

    report = run_auto_commit_push_executor(
        _task(),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        validators_passed=True,
        mode=MODE_APPLY_COMMIT_PUSH,
        command_runner=runner,
    ).to_dict()

    assert report["status"] == "APPLY_COMMIT_PUSH_COMPLETE"
    assert commands[0] == ["git", "add", "--", "safe.md"]
    assert commands[1] == ["git", "commit", "-m", "operator relief: closeout-001"]
    assert commands[2] == ["git", "push", "origin", FEATURE_BRANCH]
    assert report["safety"]["commit_executed"] is True
    assert report["safety"]["push_executed"] is True
    assert report["executable"] is True


def test_dirty_unexpected_file_blocks(tmp_path: Path) -> None:
    state = FakeRepoState(repo_root=str(tmp_path), git_status=f"## {FEATURE_BRANCH}...{FEATURE_UPSTREAM}\n M safe.md\n M extra.md")

    report = run_auto_commit_push_executor(_task(), state, tmp_path, validators_passed=True).to_dict()

    assert report["status"] == "BLOCKED"
    assert "Dirty files must exactly match approved changed paths." in report["reasons"]


def test_protected_path_blocks(tmp_path: Path) -> None:
    task = _task(
        allowed_paths=["docs/governance/source-of-truth-map.md"],
        changed_paths=["docs/governance/source-of-truth-map.md"],
        validator_targets=["docs/governance/source-of-truth-map.md"],
    )
    state = FakeRepoState(
        repo_root=str(tmp_path),
        git_status=f"## {FEATURE_BRANCH}...{FEATURE_UPSTREAM}\n M docs/governance/source-of-truth-map.md",
    )

    report = run_auto_commit_push_executor(task, state, tmp_path, validators_passed=True).to_dict()

    assert report["status"] == "BLOCKED"
    assert any("Protected path is blocked" in reason for reason in report["reasons"])


def test_forbidden_path_blocks(tmp_path: Path) -> None:
    task = _task(
        allowed_paths=["safe.md"],
        forbidden_paths=["safe.md"],
        changed_paths=["safe.md"],
    )

    report = run_auto_commit_push_executor(task, FakeRepoState(repo_root=str(tmp_path)), tmp_path, validators_passed=True).to_dict()

    assert report["status"] == "BLOCKED"
    assert any("forbidden paths" in reason for reason in report["reasons"])


def test_failed_validators_block(tmp_path: Path) -> None:
    report = run_auto_commit_push_executor(_task(), FakeRepoState(repo_root=str(tmp_path)), tmp_path, validators_passed=False).to_dict()

    assert report["status"] == "BLOCKED"
    assert "Validators must pass before commit and push can run." in report["reasons"]


def test_main_branch_blocks(tmp_path: Path) -> None:
    state = FakeRepoState(repo_root=str(tmp_path), branch="main", git_status="## main...origin/main\n M safe.md")

    report = run_auto_commit_push_executor(_task(), state, tmp_path, validators_passed=True).to_dict()

    assert report["status"] == "BLOCKED"
    assert any(FEATURE_BRANCH in reason for reason in report["reasons"])


def test_branch_mismatch_blocks(tmp_path: Path) -> None:
    state = FakeRepoState(
        repo_root=str(tmp_path),
        git_status=f"## {FEATURE_BRANCH}...origin/other-branch\n M safe.md",
    )

    report = run_auto_commit_push_executor(_task(), state, tmp_path, validators_passed=True).to_dict()

    assert report["status"] == "BLOCKED"
    assert f"Upstream must be {FEATURE_UPSTREAM}." in report["reasons"]


def test_force_push_marker_blocked(tmp_path: Path) -> None:
    report = run_auto_commit_push_executor(
        _task(requested_actions=["force_push"]),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        validators_passed=True,
    ).to_dict()

    assert report["status"] == "BLOCKED"
    assert any("force-push" in reason for reason in report["reasons"])


def test_merge_rebase_blocked(tmp_path: Path) -> None:
    for action in ("merge", "rebase"):
        report = run_auto_commit_push_executor(
            _task(requested_actions=[action]),
            FakeRepoState(repo_root=str(tmp_path)),
            tmp_path,
            validators_passed=True,
        ).to_dict()

        assert report["status"] == "BLOCKED"


def test_push_target_must_be_current_feature_branch(tmp_path: Path) -> None:
    report = run_auto_commit_push_executor(
        _task(),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        validators_passed=True,
    ).to_dict()

    assert report["commands"][2] == ["git", "push", "origin", FEATURE_BRANCH]
    assert report["push_target"] == FEATURE_UPSTREAM


def test_executable_false_unless_successful_apply(tmp_path: Path) -> None:
    dry_run = run_auto_commit_push_executor(
        _task(),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        validators_passed=True,
    ).to_dict()
    blocked = run_auto_commit_push_executor(
        _task(),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        validators_passed=False,
    ).to_dict()

    def runner(_root: Path, command: list[str]) -> GitCommandResult:
        return GitCommandResult(command, 0, "ok", "")

    applied = run_auto_commit_push_executor(
        _task(),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        validators_passed=True,
        mode=MODE_APPLY_COMMIT_PUSH,
        command_runner=runner,
    ).to_dict()

    assert dry_run["executable"] is False
    assert blocked["executable"] is False
    assert applied["executable"] is True


def test_source_scan_blocks_broad_add_and_unsafe_git_paths() -> None:
    source = Path("automation/operator_relief/auto_commit_push_executor.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "shell=True",
        "os.system",
        "Popen",
        '"git", "add", "."',
        '"git", "add", "-A"',
        "'git', 'add', '.'",
        "'git', 'add', '-A'",
        "git merge",
        "git rebase",
        "git push --force",
        "git push origin main",
        "git push --tags",
    ]
    for marker in forbidden_markers:
        assert marker not in source
