from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.bounded_executor import MODE_APPLY_SIMULATION, run_bounded_executor
from automation.operator_relief.full_auto_policy import FullAutoTask


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"
    executable: bool = False

    def to_dict(self) -> dict[str, object]:
        return dict(self.__dict__)


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "bounded-001",
        "description": "Safe bounded executor task",
        "allowed_paths": ["safe.md"],
        "forbidden_paths": ["AGENTS.md", "README.md", "docs/governance/**"],
        "changed_paths": ["safe.md"],
        "requested_actions": [],
        "validator_targets": ["safe.md"],
        "expected_branch": None,
    }
    data.update(overrides)
    return FullAutoTask(**data)


def _safe_doc(tmp_path: Path) -> None:
    (tmp_path / "safe.md").write_text("# safe\n", encoding="utf-8")


def test_allowed_task_executes_only_allowed_internal_actions(tmp_path: Path) -> None:
    _safe_doc(tmp_path)
    report = run_bounded_executor(_task(), FakeRepoState(repo_root=str(tmp_path)), tmp_path).to_dict()

    assert report["status"] == "DRY_RUN_COMPLETE"
    assert report["actions_performed"] == [
        "validator_plan_ran",
        "handoff_summary_built",
        "packet_draft_built",
        "commit_push_recommendation_built",
    ]
    assert report["handoff_summary"]["executable"] is False
    assert report["packet_draft"]["executable"] is False
    assert report["safety"]["repo_files_mutated"] is False


def test_apply_simulation_remains_non_mutating(tmp_path: Path) -> None:
    _safe_doc(tmp_path)
    report = run_bounded_executor(
        _task(),
        FakeRepoState(repo_root=str(tmp_path)),
        tmp_path,
        mode=MODE_APPLY_SIMULATION,
    ).to_dict()

    assert report["status"] == "APPLY_SIMULATION_COMPLETE"
    assert report["safety"]["apply_simulated_only"] is True
    assert report["executable"] is False


def test_blocked_task_executes_nothing(tmp_path: Path) -> None:
    report = run_bounded_executor(_task(live_trading=True), FakeRepoState(repo_root=str(tmp_path)), tmp_path).to_dict()

    assert report["status"] == "STOPPED_BLOCKED"
    assert report["actions_performed"] == []
    assert report["handoff_summary"] is None
    assert report["packet_draft"] is None


def test_approval_required_task_executes_nothing(tmp_path: Path) -> None:
    repo_state = FakeRepoState(repo_root=str(tmp_path), dirty_state="DIRTY")
    report = run_bounded_executor(_task(), repo_state, tmp_path).to_dict()

    assert report["status"] == "STOPPED_APPROVAL_REQUIRED"
    assert report["approval"]["status"] == "APPROVAL_REQUIRED"
    assert report["actions_performed"] == []


def test_unsupported_validator_stops_execution(tmp_path: Path) -> None:
    task = _task(validator_targets=["unsafe.bin"])
    report = run_bounded_executor(task, FakeRepoState(repo_root=str(tmp_path)), tmp_path).to_dict()

    assert report["status"] == "STOPPED_BLOCKED"
    assert report["actions_performed"] == []
    assert report["validator_plan"]["status"] == "UNSUPPORTED_VALIDATOR"


def test_protected_path_stops_execution(tmp_path: Path) -> None:
    task = _task(
        allowed_paths=["docs/governance/source-of-truth-map.md"],
        changed_paths=["docs/governance/source-of-truth-map.md"],
        validator_targets=["docs/governance/source-of-truth-map.md"],
    )
    report = run_bounded_executor(task, FakeRepoState(repo_root=str(tmp_path)), tmp_path).to_dict()

    assert report["status"] in {"STOPPED_BLOCKED", "STOPPED_APPROVAL_REQUIRED"}
    assert report["actions_performed"] == []
    assert report["safety"]["protected_path_mutated"] is False


def test_commit_push_are_recommendations_only(tmp_path: Path) -> None:
    _safe_doc(tmp_path)
    report = run_bounded_executor(_task(), FakeRepoState(repo_root=str(tmp_path)), tmp_path).to_dict()

    assert report["commit_push_recommendation"]["commit_executed"] is False
    assert report["commit_push_recommendation"]["push_executed"] is False
    assert report["safety"]["commit_executed"] is False
    assert report["safety"]["push_executed"] is False


def test_final_report_has_executable_false(tmp_path: Path) -> None:
    _safe_doc(tmp_path)
    report = run_bounded_executor(_task(), FakeRepoState(repo_root=str(tmp_path)), tmp_path).to_dict()

    assert report["executable"] is False


def test_bounded_executor_source_has_no_forbidden_execution_markers() -> None:
    source = Path("automation/operator_relief/bounded_executor.py").read_text(encoding="utf-8")
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
