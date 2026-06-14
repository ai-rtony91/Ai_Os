from __future__ import annotations

from automation.orchestration.self_development.aios_full_autonomy_worker_launch_guard import (
    SCHEMA,
    build_full_autonomy_worker_launch_guard_result,
)


def _repo_state(**overrides: object) -> dict:
    state = {
        "branch": "feature/full-autonomy-worker-launch-commander-v1",
        "expected_branch": "feature/full-autonomy-worker-launch-commander-v1",
        "branch_matches_expected": True,
        "dirty": False,
        "dirty_allowed_for_full_autonomy_worker_launch_guard_validation": False,
        "fail_on_dirty_worktree": True,
    }
    state.update(overrides)
    return state


def _no_write(**overrides: object) -> dict:
    proof = {
        "changed": False,
        "git_state_changed": False,
        "forbidden_surface_changed": False,
    }
    proof.update(overrides)
    return proof


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": _repo_state(),
        "command_decision": "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED",
        "human_owner_worker_launch_approval": "APPROVED_FOR_WORKER_LAUNCH",
        "identity_spine_status": "PASS",
        "validator_chain_status": "PASS",
        "approval_sos_status": "CLEAR",
        "preflight_decision": "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED",
        "allowed_lanes": ["validator", "self_audit", "readiness_review"],
        "requested_worker_count": 2,
        "max_parallel_workers": 3,
        "no_write_proof": _no_write(),
    }
    payload.update(overrides)
    return payload


def _result(**overrides: object) -> dict:
    return build_full_autonomy_worker_launch_guard_result(_payload(**overrides))


def test_python_logic_emits_guard_schema() -> None:
    result = _result()

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["launch_executed"] is False


def test_missing_approval_blocks_launch() -> None:
    result = _result(human_owner_worker_launch_approval="")

    assert result["guard_decision"] == "LAUNCH_AWAITING_HUMAN_APPROVAL"
    assert result["launch_allowed_for_future_packet"] is False
    assert "human_owner_worker_launch_approval" in result["missing_requirements"]


def test_sos_blocks_launch() -> None:
    result = _result(approval_sos_status="SOS_ACTIVE")

    assert result["guard_decision"] == "BLOCKED_BY_SOS"
    assert result["sos_state"]["wake_required"] is True
    assert result["launch_allowed_for_future_packet"] is False
    assert result["safety"]["status"] == "BLOCKED"


def test_identity_not_pass_blocks_launch() -> None:
    result = _result(identity_spine_status="UNKNOWN")

    assert result["guard_decision"] == "BLOCKED_BY_VALIDATORS"
    assert "identity_spine_pass" in result["missing_requirements"]
    assert result["validator_state"]["identity_spine_pass"] is False


def test_validator_not_pass_or_warn_reviewed_blocks_launch() -> None:
    result = _result(validator_chain_status="UNKNOWN")

    assert result["guard_decision"] == "BLOCKED_BY_VALIDATORS"
    assert "validator_chain_pass_or_warn_reviewed" in result["missing_requirements"]
    assert result["validator_state"]["validator_chain_pass_or_warn_reviewed"] is False


def test_validator_warn_reviewed_is_accepted() -> None:
    result = _result(validator_chain_status="WARN_REVIEWED")

    assert result["guard_decision"] == "LAUNCH_APPROVED_FOR_FUTURE_PACKET_NOT_EXECUTED"
    assert result["launch_allowed_for_future_packet"] is True


def test_preflight_not_pass_blocks_launch() -> None:
    result = _result(preflight_decision="BLOCKED_BY_SOS")

    assert result["guard_decision"] == "LAUNCH_REVIEW_REQUIRED"
    assert "preflight_pass_worker_launch_eligible" in result["missing_requirements"]


def test_empty_allowed_lanes_blocks_launch() -> None:
    result = _result(allowed_lanes=[])

    assert result["guard_decision"] == "BLOCKED_BY_LANES"
    assert "allowed_lanes_non_empty" in result["missing_requirements"]


def test_protected_lanes_block_launch() -> None:
    result = _result(allowed_lanes=["validator", "runtime_execution"])

    assert result["guard_decision"] == "BLOCKED_BY_LANES"
    assert "remove_protected_lane:runtime_execution" in result["missing_requirements"]
    assert result["lane_state"]["protected_lane_hits"] == ["runtime_execution"]


def test_secret_or_broker_lanes_block_launch() -> None:
    result = _result(allowed_lanes=["validator", "broker"])

    assert result["guard_decision"] == "BLOCKED_BY_LANES"
    assert "remove_protected_lane:broker" in result["missing_requirements"]


def test_worker_count_above_max_blocks_launch() -> None:
    result = _result(requested_worker_count=4, max_parallel_workers=3)

    assert result["guard_decision"] == "BLOCKED_BY_WORKER_COUNT"
    assert "worker_count_within_max_parallel_workers" in result["missing_requirements"]
    assert result["worker_count_state"]["within_limit"] is False


def test_command_decision_not_ready_requires_review() -> None:
    result = _result(command_decision="COMMAND_PREVIEW_BLOCKED")

    assert result["guard_decision"] == "LAUNCH_REVIEW_REQUIRED"
    assert "command_preview_ready" in result["missing_requirements"]


def test_all_pass_resolves_to_future_packet_approved_not_executed() -> None:
    result = _result()

    assert result["guard_decision"] == "LAUNCH_APPROVED_FOR_FUTURE_PACKET_NOT_EXECUTED"
    assert result["launch_allowed_for_future_packet"] is True
    assert result["launch_executed"] is False
    assert result["safety"]["status"] == "PASS"


def test_launch_executed_is_always_false() -> None:
    for approval in ("", "APPROVED_FOR_WORKER_LAUNCH"):
        result = _result(human_owner_worker_launch_approval=approval)
        assert result["launch_executed"] is False
        assert result["safety"]["launch_executed"] is False
        assert result["safety"]["launches_workers"] is False


def test_dirty_repo_outside_approved_files_blocks() -> None:
    result = _result(
        repo_state=_repo_state(
            dirty=True,
            dirty_allowed_for_full_autonomy_worker_launch_guard_validation=False,
        )
    )

    assert result["guard_decision"] == "BLOCKED_BY_REPO_STATE"
    assert "DIRTY_WORKTREE" in result["stop_conditions"]
    assert result["safety"]["status"] == "BLOCKED"


def test_no_write_surface_delta_blocks() -> None:
    result = _result(no_write_proof=_no_write(changed=True, forbidden_surface_changed=True))

    assert result["guard_decision"] == "BLOCKED_BY_REPO_STATE"
    assert "WRITE_SURFACE_RISK" in result["stop_conditions"]
    assert result["safety"]["status"] == "BLOCKED_BY_WRITE_SURFACE_RISK"


def test_safety_invariants_never_launch_or_mutate() -> None:
    result = _result()
    safety = result["safety"]

    assert safety["writes_files"] is False
    assert safety["starts_runtime"] is False
    assert safety["launches_workers"] is False
    assert safety["enables_scheduler"] is False
    assert safety["starts_daemon"] is False
    assert safety["mutates_queue"] is False
    assert safety["mutates_locks"] is False
    assert safety["mutates_approval"] is False
    assert safety["mutates_registry"] is False
    assert safety["writes_reports"] is False
    assert safety["writes_telemetry"] is False
    assert safety["writes_relay"] is False
    assert safety["touches_secrets_or_env"] is False
    assert safety["broker_or_live_trading"] is False
    assert safety["protected_actions_blocked"] is True
    assert safety["human_owner_required_before_worker_launch"] is True
