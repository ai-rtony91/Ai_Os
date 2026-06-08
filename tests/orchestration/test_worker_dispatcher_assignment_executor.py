from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.orchestration.dispatcher.assignment_executor import (
    build_dispatch_packet_preview,
    classify_candidates,
    normalize_candidates,
    sample_report,
    summarize_state,
)


def test_sample_report_treats_historical_queue_as_reference() -> None:
    report = sample_report()
    assert report["queue_state"]["historical_queue_treatment"] == "HISTORICAL_REFERENCE"
    assert any(decision["decision"] == "HISTORICAL_REFERENCE" for decision in report["candidate_decisions"])


def test_sample_report_treats_empty_locks_as_no_active_locks() -> None:
    report = sample_report()
    assert report["lock_state"]["classification"] == "NO_ACTIVE_LOCKS"


def test_completed_or_pending_approval_does_not_authorize_apply() -> None:
    report = sample_report()
    assert report["approval_state"]["future_apply_approved"] is False
    preview = report["dispatch_packet_previews"][0]
    assert preview["apply_execution_approved"] is False
    assert preview["approval_authority"] == "Anthony"


def test_dispatch_preview_is_non_executable_and_zero_launch() -> None:
    report = sample_report()
    assert report["zero_launch_confirmation"]["zero_workers_launched"] is True
    assert report["zero_launch_confirmation"]["zero_scheduler_started"] is True
    preview = report["dispatch_packet_previews"][0]
    assert preview["contains_execution_token"] is False
    assert preview["worker_launch_approved"] is False


def test_active_packet_without_apply_approval_is_dry_run_only() -> None:
    report = sample_report()
    assert any(decision["task_id"] == "dry-run-next" and decision["decision"] == "DRY_RUN_ONLY" for decision in report["candidate_decisions"])


def test_path_collision_blocks_active_candidates() -> None:
    state = {
        "worker_inbox": {"status": "PRESENT", "payload": {"items": []}},
        "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL", "items": []}},
        "active_work_packets": {
            "packets": [
                {"packet_id": "one", "status": "active", "owner_lane": "a", "allowed_paths": ["docs/AI_OS/worker_dispatcher/"]},
                {"packet_id": "two", "status": "active", "owner_lane": "b", "allowed_paths": ["docs/AI_OS/worker_dispatcher/file.md"]},
            ]
        },
    }
    candidates = normalize_candidates(state)
    summary = {"approval_state": {"future_apply_approved": False}}
    decisions, collisions = classify_candidates(candidates, summary, {"status": "UNKNOWN", "open_prs": []})
    assert collisions
    assert {decision.decision for decision in decisions} == {"BLOCKED_BY_COLLISION"}


def test_protected_runtime_path_blocks_candidate() -> None:
    state = {
        "worker_inbox": {"status": "PRESENT", "payload": {"items": []}},
        "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL", "items": []}},
        "active_work_packets": {"packets": [{"packet_id": "live", "status": "active", "owner_lane": "x", "allowed_paths": ["broker/"]}]},
    }
    candidates = normalize_candidates(state)
    decisions, _ = classify_candidates(candidates, {"approval_state": {"future_apply_approved": False}}, {"status": "UNKNOWN", "open_prs": []})
    assert decisions[0].decision == "BLOCKED_BY_PROTECTED_PATH"


def test_validator_cli_sample_check_passes() -> None:
    result = subprocess.run(
        ["python", "automation/validators/aios_worker_dispatcher_assignment_executor_validator.py", "--sample-check", "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"status": "PASS"' in result.stdout
