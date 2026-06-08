from __future__ import annotations

from datetime import datetime, timezone

from automation.orchestration.restart_safety.restart_guard import (
    APPLY_REPLAY_BLOCKED,
    BLOCKED_RESTART_MARKER_CORRUPT,
    SAFE_DRY_RUN_ONLY,
    STALE_RESTART_MARKER,
    WAITING_FOR_APPROVAL,
    classify_restart_marker,
)
from automation.orchestration.runtime.atomic_state import (
    CORRUPT_JSON,
    MISSING_JSON,
    VALID_JSON,
    atomic_write_json,
    read_json_tolerant,
)
from automation.validators.aios_weekend_readiness_validator import (
    score_readiness,
    validate_approvals,
    validate_locks,
    validate_queue,
)


def test_atomic_json_write_and_read(tmp_path):
    target = tmp_path / "runtime" / "state.json"
    atomic_write_json(target, {"status": "ok"})
    result = read_json_tolerant(target)
    assert result.status == VALID_JSON
    assert result.data == {"status": "ok"}


def test_atomic_json_missing_and_corrupt(tmp_path):
    assert read_json_tolerant(tmp_path / "missing.json").status == MISSING_JSON
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not json", encoding="utf-8")
    assert read_json_tolerant(corrupt).status == CORRUPT_JSON


def test_restart_marker_fail_closed_states(tmp_path):
    corrupt = tmp_path / "marker.json"
    corrupt.write_text("{bad", encoding="utf-8")
    assert classify_restart_marker(corrupt).status == BLOCKED_RESTART_MARKER_CORRUPT

    atomic_write_json(corrupt, {"status": "completed_apply", "updated_at": "2026-06-08T00:00:00Z"})
    assert classify_restart_marker(corrupt, now=datetime(2026, 6, 8, 0, 1, tzinfo=timezone.utc)).status == APPLY_REPLAY_BLOCKED

    atomic_write_json(corrupt, {"status": "waiting_for_approval", "updated_at": "2026-06-08T00:00:00Z"})
    assert classify_restart_marker(corrupt, now=datetime(2026, 6, 8, 0, 1, tzinfo=timezone.utc)).status == WAITING_FOR_APPROVAL

    atomic_write_json(corrupt, {"status": "completed_dry_run", "updated_at": "2026-06-08T00:00:00Z"})
    assert classify_restart_marker(corrupt, now=datetime(2026, 6, 8, 0, 1, tzinfo=timezone.utc)).status == SAFE_DRY_RUN_ONLY

    assert classify_restart_marker(corrupt, now=datetime(2026, 6, 8, 2, 1, tzinfo=timezone.utc)).status == STALE_RESTART_MARKER


def test_approval_queue_lock_reject_dangerous_shapes():
    approval = {
        "approval_id": "bad",
        "created_at": "2026-06-08T00:00:00Z",
        "expires_at": "2026-06-09T00:00:00Z",
        "requested_by_worker": "worker",
        "requested_action": "APPLY",
        "action_scope": "wild",
        "protected_paths": ["*"],
        "risk_flags": [],
        "approval_status": "approved",
        "apply_packet_preparation_approved": True,
        "apply_execution_approved": False,
        "operator_authority_marker": "Anthony",
        "allowed_actions": ["*"],
        "disallowed_actions": [],
        "evidence_links": [],
        "next_safe_action": "none",
    }
    assert {finding.code for finding in validate_approvals(approval)} >= {"AIOS-APPROVAL-WILDCARD", "AIOS-APPROVAL-APPLY-NOT-APPROVED"}

    queue = {"tasks": [
        {"task_id": "one", "title": "a", "lane": "x", "status": "running", "priority": 1, "created_at": "2026-06-08T00:00:00Z", "updated_at": "2026-06-08T00:00:00Z", "owner_worker": "a", "allowed_workers": ["a"], "branch": "b", "pr_number": None, "protected_paths": ["docs/x"], "required_approval_id": "", "lock_id": "", "validation_contract": [], "output_contract": "", "blocked_reason": "", "next_safe_action": "", "completion_evidence": [], "sos_policy": ""},
        {"task_id": "two", "title": "b", "lane": "x", "status": "running", "priority": 1, "created_at": "2026-06-08T00:00:00Z", "updated_at": "2026-06-08T00:00:00Z", "owner_worker": "b", "allowed_workers": ["b"], "branch": "b", "pr_number": None, "protected_paths": ["docs/x"], "required_approval_id": "", "lock_id": "", "validation_contract": [], "output_contract": "", "blocked_reason": "", "next_safe_action": "", "completion_evidence": [], "sos_policy": ""},
    ]}
    assert "AIOS-QUEUE-PATH-COLLISION" in {finding.code for finding in validate_queue(queue)}

    locks = {"locks": [
        {"lock_id": "one", "worker_id": "x", "worker_type": "Unknown", "lane": "x", "task_id": "one", "branch": "b", "pr_number": None, "protected_paths": ["*"], "acquired_at": "2026-06-08T00:00:00Z", "expires_at": "2099-01-01T00:00:00Z", "heartbeat_at": "2026-06-08T00:00:00Z", "status": "active", "allowed_actions": ["APPLY"], "disallowed_actions": [], "next_safe_action": "review"},
    ]}
    assert {"AIOS-LOCK-UNKNOWN-WORKER-APPLY", "AIOS-LOCK-BROAD-ROOT"} <= {finding.code for finding in validate_locks(locks)}


def test_scorecard_keeps_scheduler_safe_at_zero_until_all_gates_pass():
    score = score_readiness({"generated_output_clean": True, "tier0_watchdog": True, "tier1_restart_safety": True})
    assert score["scheduler_allowed"] is False
    assert score["scheduler_safe_score"] == 0.0
    assert "live_sos_last_mile" in score["blockers"]
