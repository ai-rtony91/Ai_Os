from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.full_auto_policy import FullAutoTask
from automation.operator_relief.run_full_auto_dry_run import run_full_auto_dry_run


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str = "C:\\Dev\\Ai.Os"
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
        "task_id": "full-auto-dry-run-001",
        "description": "Safe workflow doc update",
        "allowed_paths": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "forbidden_paths": ["AGENTS.md", "README.md", "docs/governance/**"],
        "changed_paths": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "requested_actions": [],
        "validator_targets": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "expected_branch": "feature/full-operator-relief-closed-loop-v1",
    }
    data.update(overrides)
    return FullAutoTask(**data)


def test_allowed_task_produces_dry_run_handoff_summary() -> None:
    report = run_full_auto_dry_run(_task(), FakeRepoState()).to_dict()

    assert report["mode"] == "DRY_RUN"
    assert report["final_status"] == "DRY_RUN_READY"
    assert report["handoff_summary"]["task_id"] == "full-auto-dry-run-001"
    assert report["handoff_summary"]["executable"] is False
    assert report["safety"]["repo_files_written"] is False


def test_blocked_task_does_not_produce_executable_handoff() -> None:
    report = run_full_auto_dry_run(_task(live_trading=True), FakeRepoState()).to_dict()

    assert report["final_status"] == "DRY_RUN_BLOCKED"
    assert report["blocked"] is True
    assert report["handoff_summary"] is None
    assert report["executable"] is False


def test_approval_required_task_reports_approval_needed() -> None:
    repo_state = FakeRepoState(dirty_state="DIRTY")
    report = run_full_auto_dry_run(_task(), repo_state).to_dict()

    assert report["final_status"] == "DRY_RUN_REQUIRES_APPROVAL"
    assert report["approval_needed"] is True
    assert report["handoff_summary"]["human_review_required"] is True


def test_runner_has_no_commit_push_merge_or_recursive_codex_path() -> None:
    source = Path("automation/operator_relief/run_full_auto_dry_run.py").read_text(encoding="utf-8")

    forbidden_runtime_markers = [
        "subprocess.run",
        "git commit",
        "git push",
        "git merge",
        "openai.",
        "OpenAI(",
        "Codex(",
        "run_operator_relief_loop",
        "append_evidence",
        "write_approval_item",
    ]
    for marker in forbidden_runtime_markers:
        assert marker not in source
