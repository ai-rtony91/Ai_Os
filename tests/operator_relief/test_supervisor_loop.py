from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.cli_bridge import CliAvailability
from automation.operator_relief.full_auto_policy import FullAutoTask
from automation.operator_relief.runtime_bridge import run_runtime_bridge
from automation.operator_relief.supervisor_loop import run_supervisor_loop


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"
    executable: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "repo_root": self.repo_root,
            "branch": self.branch,
            "dirty_state": self.dirty_state,
            "executable": False,
        }


def _task() -> FullAutoTask:
    return FullAutoTask(
        task_id="resume-001",
        description="Safe approval resume task",
        allowed_paths=["safe.py"],
        forbidden_paths=["AGENTS.md", "README.md", "docs/governance/**"],
        changed_paths=["safe.py"],
        requested_actions=[],
        validator_targets=["safe.py"],
    )


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "safe.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "reports/operator_relief/inbox").mkdir(parents=True)
    (tmp_path / "reports/operator_relief/outbox").mkdir(parents=True)
    (tmp_path / "automation/operator_relief/approval_input").mkdir(parents=True)
    return tmp_path


def _cli() -> CliAvailability:
    return CliAvailability(codex_path="C:/bin/codex.exe", openai_path=None, status="CLI_AVAILABLE")


def test_supervisor_loop_exits_cleanly_on_routine_success(tmp_path: Path) -> None:
    report = run_supervisor_loop(tmp_path, repo_state=FakeRepoState(repo_root=str(tmp_path)), cli=_cli()).to_dict()

    assert report["status"] == "SUPERVISOR_LOOP_COMPLETE"
    assert report["selected_action"] == "PACKET_QUEUE_READY"
    assert report["notification_sent"] is False
    assert report["daemon_started"] is False
    assert report["executable"] is False


def test_supervisor_loop_selects_approval_resume_when_valid_approval_exists(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    inbox = repo / "reports/operator_relief/inbox/approval.json"
    inbox.write_text(json.dumps(_task().to_dict()), encoding="utf-8")
    runtime = run_runtime_bridge(repo, repo_state=FakeRepoState(repo_root=str(repo), dirty_state="DIRTY")).to_dict()
    decision = repo / "automation/operator_relief/approval_input/decision.json"
    decision.write_text(
        json.dumps(
            {
                "decision": "CONTINUE_MISSION",
                "task_id": "resume-001",
                "outbox_path": runtime["outbox_path"],
                "archive_path": runtime["archive_path"],
            }
        ),
        encoding="utf-8",
    )

    report = run_supervisor_loop(repo, repo_state=FakeRepoState(repo_root=str(repo), dirty_state="DIRTY"), cli=_cli()).to_dict()
    telemetry = json.loads(Path(report["engine_room_status_path"]).read_text(encoding="utf-8"))

    assert report["selected_action"] == "APPROVAL_RESUME"
    assert report["resume_status"] == "RESUME_TASK_QUEUED"
    assert telemetry["resume_status"] == "RESUME_TASK_QUEUED"
    assert report["notification_sent"] is False
