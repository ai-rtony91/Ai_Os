from __future__ import annotations

from pathlib import Path

from automation.orchestration.self_development.aios_approved_autonomy_worker_launch_controller import (
    APPROVAL,
    SCHEMA,
    build_approved_autonomy_worker_launch_result,
)


def _repo_state(**overrides: object) -> dict:
    state = {
        "branch": "feature/approved-autonomy-worker-launch-forex-research-v1",
        "expected_branch": "feature/approved-autonomy-worker-launch-forex-research-v1",
        "branch_matches_expected": True,
        "dirty": False,
        "dirty_allowed_for_approved_autonomy_worker_launch_validation": False,
        "fail_on_dirty_worktree": True,
    }
    state.update(overrides)
    return state


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": _repo_state(),
        "mode": "DRY_RUN",
        "human_owner_worker_launch_approval": APPROVAL,
        "worker_posture": "READ_ONLY_VALIDATOR_CREW",
        "operating_profile": "24H_SUPERVISED",
        "worker_count": 2,
        "max_parallel_workers": 3,
        "allowed_lanes": ["validator", "self_audit", "forex_research"],
        "timebox_minutes": 30,
        "stop_on_first_failure": True,
        "identity_spine_status": "PASS",
        "validator_chain_status": "PASS",
        "approval_sos_status": "PASS",
        "preflight_decision": "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED",
        "launch_guard_decision": "LAUNCH_APPROVED_FOR_FUTURE_PACKET_NOT_EXECUTED",
        "research_plan": "Continue synthetic Forex research.",
        "write_ledger": False,
    }
    payload.update(overrides)
    return payload


def _result(**overrides: object) -> dict:
    return build_approved_autonomy_worker_launch_result(_payload(**overrides))


def test_missing_human_owner_worker_launch_approval_blocks_apply() -> None:
    result = _result(mode="APPLY", human_owner_worker_launch_approval="")

    assert result["schema"] == SCHEMA
    assert result["launch_decision"] == "LAUNCH_APPROVAL_MISSING"
    assert "human_owner_worker_launch_approval" in result["missing_requirements"]
    assert result["executed_task_count"] == 0


def test_wrong_approval_string_blocks_apply() -> None:
    result = _result(mode="APPLY", human_owner_worker_launch_approval="APPROVED_BUT_WRONG")

    assert result["launch_decision"] == "LAUNCH_APPROVAL_MISSING"
    assert result["safety"]["runs_local_simulation_tasks"] is False


def test_correct_approval_plus_passing_evidence_allows_launch_apply_ready() -> None:
    result = _result(mode="DRY_RUN")

    assert result["launch_decision"] == "LAUNCH_APPLY_READY"
    assert result["safety"]["status"] == "PASS"
    assert result["executed_task_count"] == 0


def test_apply_executes_only_local_deterministic_approved_tasks(tmp_path: Path) -> None:
    result = _result(
        mode="APPLY",
        output_root=str(tmp_path / "ledger"),
        repo_root=str(tmp_path),
        write_ledger=True,
    )

    assert result["launch_decision"] == "LAUNCH_APPLY_EXECUTED"
    assert result["executed_task_count"] == 2
    assert [task["status"] for task in result["worker_tasks"]] == ["PASS", "PASS"]
    assert {task["task_type"] for task in result["worker_tasks"]} <= {"VALIDATOR_SUMMARY", "SELF_AUDIT_SUMMARY"}
    assert result["safety"]["runs_local_simulation_tasks"] is True
    assert result["safety"]["launches_workers"] is False
    assert result["run_ledger"]["written"] is True


def test_worker_count_above_max_blocks() -> None:
    result = _result(worker_count=3, max_parallel_workers=3)

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_WORKER_LIMIT"
    assert "worker_count_within_posture_cap" in result["missing_requirements"]


def test_empty_lanes_block() -> None:
    result = _result(allowed_lanes=[])

    assert result["launch_decision"] == "LAUNCH_REVIEW_REQUIRED"
    assert "allowed_lanes_non_empty" in result["missing_requirements"]


def test_protected_lanes_block() -> None:
    result = _result(allowed_lanes=["validator", "runtime_execution"])

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_PROTECTED_LANE"
    assert "remove_protected_lane:runtime_execution" in result["missing_requirements"]


def test_timebox_outside_range_blocks() -> None:
    result = _result(timebox_minutes=4)

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_TIMEBOX"
    assert "timebox_between_5_and_240_minutes" in result["missing_requirements"]


def test_sos_active_blocks() -> None:
    result = _result(approval_sos_status="SOS_ACTIVE")

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_SOS"
    assert result["human_wake_policy"]["wake_required"] is True


def test_identity_not_pass_blocks() -> None:
    result = _result(identity_spine_status="UNKNOWN")

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_VALIDATORS"
    assert "identity_spine_pass" in result["missing_requirements"]


def test_validator_not_pass_or_warn_reviewed_blocks() -> None:
    result = _result(validator_chain_status="UNKNOWN")

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_VALIDATORS"
    assert "validator_chain_pass_or_warn_reviewed" in result["missing_requirements"]


def test_validator_warn_reviewed_passes() -> None:
    result = _result(validator_chain_status="WARN_REVIEWED")

    assert result["launch_decision"] == "LAUNCH_APPLY_READY"


def test_preflight_not_pass_blocks() -> None:
    result = _result(preflight_decision="PREFLIGHT_PASS_AWAITING_HUMAN_APPROVAL")

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_VALIDATORS"
    assert "worker_launch_preflight_pass" in result["missing_requirements"]


def test_launch_guard_not_pass_blocks() -> None:
    result = _result(launch_guard_decision="LAUNCH_DENIED")

    assert result["launch_decision"] == "LAUNCH_REVIEW_REQUIRED"
    assert "launch_guard_approved_for_future_packet" in result["missing_requirements"]


def test_no_runtime_scheduler_daemon_launch() -> None:
    safety = _result()["safety"]

    assert safety["starts_runtime"] is False
    assert safety["enables_scheduler"] is False
    assert safety["starts_daemon"] is False


def test_no_queue_lock_approval_registry_mutation() -> None:
    safety = _result()["safety"]

    assert safety["mutates_queue"] is False
    assert safety["mutates_locks"] is False
    assert safety["mutates_approval"] is False
    assert safety["mutates_registry"] is False


def test_no_secrets_env_broker_or_live_trading() -> None:
    result = _result(allowed_lanes=["validator", "oanda"])

    assert result["launch_decision"] == "LAUNCH_BLOCKED_BY_SECRET_OR_LIVE_TRADING_BOUNDARY"
    assert result["safety"]["touches_secrets_or_env"] is False
    assert result["safety"]["broker_or_live_trading"] is False


def test_ledger_path_traversal_blocked(tmp_path: Path) -> None:
    result = _result(
        mode="APPLY",
        output_root=str(tmp_path / ".." / "bad"),
        repo_root=str(tmp_path),
        write_ledger=True,
    )

    assert result["launch_decision"] == "LAUNCH_APPLY_PARTIAL_STOPPED"
    assert "LEDGER_OUTPUT_ROOT_BLOCKED" in result["stop_reason"]


def test_safety_invariants() -> None:
    result = _result()
    safety = result["safety"]

    assert safety["launches_workers"] is False
    assert safety["launches_external_workers"] is False
    assert safety["creates_ready_stage"] is False
    assert safety["writes_reports"] is False
    assert safety["writes_telemetry"] is False
    assert safety["writes_relay"] is False
    assert safety["protected_actions_blocked"] is True
    assert safety["valid_for_live_trading"] is False
