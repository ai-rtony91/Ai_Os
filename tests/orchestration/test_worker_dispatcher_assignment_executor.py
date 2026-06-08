from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.orchestration.dispatcher.assignment_executor import (
    build_dispatch_packet_preview,
    build_walkie_events,
    classify_candidates,
    load_state,
    normalize_candidates,
    sample_report,
    summarize_state,
)


def test_sample_report_treats_historical_queue_as_reference() -> None:
    report = sample_report()
    assert report["queue_state"]["historical_queue_treatment"] == "HISTORICAL_REFERENCE"
    assert report["active_state_contracts"]["queue"]["historical_queue_treatment"] == "HISTORICAL_REFERENCE"
    assert any(decision["decision"] == "HISTORICAL_REFERENCE" for decision in report["candidate_decisions"])


def test_sample_report_treats_empty_locks_as_no_active_locks() -> None:
    report = sample_report()
    assert report["lock_state"]["classification"] == "NO_ACTIVE_LOCKS"
    assert report["active_state_contracts"]["locks"]["contract_status"] == "EMPTY_ACTIVE_REGISTRY"


def test_completed_or_pending_approval_does_not_authorize_apply() -> None:
    report = sample_report()
    assert report["approval_state"]["future_apply_approved"] is False
    assert report["active_state_contracts"]["approval"]["approval_contract"] == "EVIDENCE_ONLY"
    assert report["active_state_contracts"]["validator_pass_is_approval"] is False
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


def test_walkie_events_are_internal_preview_only() -> None:
    report = sample_report()
    events = report["internal_walkie_events"]

    assert any(event["event_type"] == "DRY_RUN_ONLY" for event in events)
    for event in events:
        assert event["zero_external_wake_confirmation"] is True
        assert event["zero_worker_launch_confirmation"] is True
        assert "direct_anthony_wake" in event["blocked_actions"]
        assert "notification_send" in event["blocked_actions"]


def test_waiting_approval_routes_to_night_supervisor_and_approval_evidence() -> None:
    state = {
        "worker_inbox": {"status": "PRESENT", "payload": {"items": []}},
        "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL", "items": []}},
        "active_work_packets": {"packets": [{"packet_id": "approval", "status": "awaiting_approval", "owner_lane": "x"}]},
    }
    candidates = normalize_candidates(state)
    summary = {
        "queue_state": {"historical_queue_treatment": "HISTORICAL_REFERENCE"},
        "approval_state": {"inbox_status": "completed", "apply_gate_status": "pending_review", "future_apply_approved": False},
    }
    decisions, _ = classify_candidates(candidates, summary, {"status": "UNKNOWN", "open_prs": []})
    events = build_walkie_events(decisions, summary, [])

    event = next(item for item in events if item.event_type == "WAITING_APPROVAL")
    assert event.severity == "ACTION_REQUIRED"
    assert event.route_to == ["night_supervisor_review", "approval_inbox_evidence"]
    assert event.requires_anthony is True


def test_sos_candidate_routes_to_watchdog_without_external_wake() -> None:
    state = {
        "worker_inbox": {"status": "PRESENT", "payload": {"items": []}},
        "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL", "items": []}},
        "active_work_packets": {"packets": [{"packet_id": "live", "status": "active", "owner_lane": "x", "allowed_paths": ["broker/"]}]},
    }
    candidates = normalize_candidates(state)
    summary = {
        "queue_state": {"historical_queue_treatment": "HISTORICAL_REFERENCE"},
        "approval_state": {"inbox_status": "completed", "apply_gate_status": "pending_review", "future_apply_approved": False},
    }
    decisions, _ = classify_candidates(candidates, summary, {"status": "UNKNOWN", "open_prs": []})
    events = build_walkie_events(decisions, summary, [])

    event = next(item for item in events if item.event_type == "SOS_CANDIDATE")
    assert event.route_to == ["watchdog_pi5_review"]
    assert event.requires_anthony is True
    assert event.zero_external_wake_confirmation is True


def test_active_packet_without_apply_approval_is_dry_run_only() -> None:
    report = sample_report()
    assert any(decision["task_id"] == "dry-run-next" and decision["decision"] == "DRY_RUN_ONLY" for decision in report["candidate_decisions"])


def test_historical_dispatcher_queue_does_not_produce_active_candidate() -> None:
    report = sample_report()

    historical = [
        decision
        for decision in report["candidate_decisions"]
        if decision["source"] == "historical_dispatcher_queue"
    ]

    assert historical
    assert all(decision["decision"] == "HISTORICAL_REFERENCE" for decision in historical)


def test_work_packets_active_is_canonical_active_candidate_source() -> None:
    report = sample_report()

    assert report["active_state_contracts"]["work_packets"]["contract_status"] == "ACTIVE_CONTRACT"
    assert any(decision["source"] == "active_work_packet" for decision in report["candidate_decisions"])


def test_apply_candidate_without_exact_approval_waits_for_approval() -> None:
    state = {
        "worker_inbox": {"status": "PRESENT", "payload": {"items": []}},
        "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL", "items": []}},
        "active_work_packets": {"packets": [{"packet_id": "apply", "status": "active", "mode": "APPLY", "owner_lane": "x"}]},
    }
    candidates = normalize_candidates(state)
    summary = {"approval_state": {"future_apply_approved": False}}

    decisions, _ = classify_candidates(candidates, summary, {"status": "UNKNOWN", "open_prs": []})

    assert decisions[0].decision == "WAITING_APPROVAL"
    assert "apply_mode_without_exact_future_apply_approval" in decisions[0].reasons


def test_proposed_backlog_is_not_active_queue() -> None:
    report = sample_report()

    assert report["active_state_contracts"]["work_packets"]["proposed_backlog_contract"] == "PROPOSED_BACKLOG"
    assert all(decision["source"] != "proposed_backlog" for decision in report["candidate_decisions"])


def test_missing_lock_surface_requires_review(tmp_path: Path) -> None:
    state = load_state(tmp_path)
    summary = summarize_state(state)

    assert summary["lock_state"]["contract_status"] == "MISSING"
    assert summary["lock_state"]["classification"] == "MISSING"


def test_malformed_lock_surface_requires_review(tmp_path: Path) -> None:
    lock_dir = tmp_path / "automation/orchestration/locks"
    lock_dir.mkdir(parents=True)
    (lock_dir / "FILE_LOCK_REGISTRY.json").write_text("{", encoding="utf-8")

    state = load_state(tmp_path)
    summary = summarize_state(state)

    assert summary["lock_state"]["contract_status"] == "MALFORMED"
    assert summary["lock_state"]["classification"] == "MALFORMED"


def test_completed_worker_inbox_item_is_not_active_work() -> None:
    report = sample_report()
    inbox_decisions = [decision for decision in report["candidate_decisions"] if decision["source"] == "worker_inbox"]

    assert inbox_decisions
    assert all(decision["decision"] == "COMPLETE_OR_SUPERSEDED" for decision in inbox_decisions)


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


def test_active_lock_path_overlap_blocks_candidate() -> None:
    state = {
        "worker_inbox": {"status": "PRESENT", "payload": {"items": []}},
        "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL", "items": []}},
        "active_work_packets": {"packets": [{"packet_id": "locked", "status": "active", "owner_lane": "x", "allowed_paths": ["docs/AI_OS/worker_dispatcher/file.md"]}]},
    }
    candidates = normalize_candidates(state)
    summary = {
        "approval_state": {"future_apply_approved": False},
        "lock_state": {"active_lock_paths": ["docs/AI_OS/worker_dispatcher/"]},
    }

    decisions, _ = classify_candidates(candidates, summary, {"status": "UNKNOWN", "open_prs": []})

    assert decisions[0].decision == "BLOCKED_BY_LOCK"
    assert "active_lock_path_overlap" in decisions[0].reasons


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
