from __future__ import annotations

from automation.orchestration.self_development.aios_full_autonomy_worker_launch_commander import (
    SCHEMA,
    build_full_autonomy_worker_launch_command_result,
)


def _repo_state(**overrides: object) -> dict:
    state = {
        "branch": "feature/full-autonomy-worker-launch-commander-v1",
        "expected_branch": "feature/full-autonomy-worker-launch-commander-v1",
        "branch_matches_expected": True,
        "dirty": False,
        "dirty_allowed_for_full_autonomy_worker_launch_commander_validation": False,
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
        "preflight_decision": "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED",
        "requested_worker_posture": "READ_ONLY_VALIDATOR_CREW",
        "operating_profile": "24H_SUPERVISED",
        "requested_worker_count": 2,
        "max_parallel_workers": 3,
        "allowed_lanes": ["validator", "self_audit", "readiness_review"],
        "human_owner_worker_launch_approval": "",
        "launch_timebox_minutes": 90,
        "stop_on_first_failure": True,
        "no_write_proof": _no_write(),
    }
    payload.update(overrides)
    return payload


def _result(**overrides: object) -> dict:
    return build_full_autonomy_worker_launch_command_result(_payload(**overrides))


def test_python_logic_emits_command_schema() -> None:
    result = _result()

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["launch_executed"] is False


def test_non_pass_preflight_blocks_command() -> None:
    result = _result(preflight_decision="BLOCKED_BY_SOS")

    assert result["command_decision"] == "COMMAND_PREVIEW_BLOCKED"
    assert result["worker_launch_command_preview"]["emitted"] is False
    assert "preflight_pass_worker_launch_eligible" in result["missing_requirements"]


def test_review_required_preflight_creates_review_required_command_decision() -> None:
    result = _result(preflight_decision="REVIEW_REQUIRED")

    assert result["command_decision"] == "COMMAND_PREVIEW_REVIEW_REQUIRED"
    assert result["worker_launch_command_preview"]["emitted"] is False


def test_missing_approval_creates_awaiting_approval_command_preview() -> None:
    result = _result()

    assert result["command_decision"] == "COMMAND_PREVIEW_READY_AWAITING_APPROVAL"
    assert result["worker_launch_command_preview"]["emitted"] is True
    assert result["worker_launch_command_preview"]["executable_in_this_packet"] is False
    assert "human_owner_worker_launch_approval" in result["missing_requirements"]


def test_approval_plus_passing_preflight_creates_approved_but_not_executed_preview() -> None:
    result = _result(human_owner_worker_launch_approval="APPROVED_FOR_WORKER_LAUNCH")

    assert result["command_decision"] == "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED"
    assert result["worker_launch_command_preview"]["emitted"] is True
    assert result["launch_executed"] is False
    assert result["safety"]["launches_workers"] is False


def test_command_preview_includes_worker_count_lanes_posture_timebox_and_stop_conditions() -> None:
    result = _result(human_owner_worker_launch_approval="APPROVED_FOR_WORKER_LAUNCH")
    preview = result["worker_launch_command_preview"]

    assert result["worker_count"] == 2
    assert result["worker_posture"] == "READ_ONLY_VALIDATOR_CREW"
    assert result["allowed_lanes"] == ["validator", "self_audit", "readiness_review"]
    assert result["timebox_minutes"] == 90
    assert result["stop_conditions"] == []
    assert preview["worker_count"] == 2
    assert preview["allowed_lanes"] == ["validator", "self_audit", "readiness_review"]
    assert preview["timebox_minutes"] == 90


def test_command_line_preview_does_not_include_forbidden_mutation_commands() -> None:
    result = _result(human_owner_worker_launch_approval="APPROVED_FOR_WORKER_LAUNCH")
    command = result["worker_launch_command_preview"]["command_line_preview"].lower()

    for forbidden in (
        "queue_mutation",
        "lock_mutation",
        "approval_mutation",
        "registry_mutation",
        "reports_write",
        "telemetry_write",
        "relay_write",
        ".env",
        "broker",
        "oanda",
        "live_trading",
    ):
        assert forbidden not in command


def test_launch_executed_is_always_false() -> None:
    for approval in ("", "APPROVED_FOR_WORKER_LAUNCH"):
        result = _result(human_owner_worker_launch_approval=approval)
        assert result["launch_executed"] is False
        assert result["worker_launch_command_preview"]["launch_executed"] is False
        assert result["safety"]["launch_executed"] is False


def test_protected_lanes_are_blocked() -> None:
    result = _result(allowed_lanes=["validator", "runtime_execution"])

    assert result["command_decision"] == "COMMAND_PREVIEW_BLOCKED"
    assert "remove_protected_lane:runtime_execution" in result["missing_requirements"]
    assert result["worker_launch_command_preview"]["emitted"] is False


def test_secret_or_broker_lanes_are_blocked() -> None:
    result = _result(allowed_lanes=["validator", "broker"])

    assert result["command_decision"] == "COMMAND_PREVIEW_BLOCKED"
    assert "remove_secret_or_broker_lane:broker" in result["missing_requirements"]


def test_empty_allowed_lanes_blocks_command() -> None:
    result = _result(allowed_lanes=[])

    assert result["command_decision"] == "COMMAND_PREVIEW_BLOCKED"
    assert "allowed_lanes_non_empty" in result["missing_requirements"]


def test_worker_count_above_max_requires_review() -> None:
    result = _result(requested_worker_count=4, max_parallel_workers=3)

    assert result["command_decision"] == "COMMAND_PREVIEW_REVIEW_REQUIRED"
    assert "worker_count_within_max_parallel_workers" in result["missing_requirements"]


def test_dirty_repo_blocks_command_preview() -> None:
    result = _result(
        repo_state=_repo_state(
            dirty=True,
            dirty_allowed_for_full_autonomy_worker_launch_commander_validation=False,
        )
    )

    assert result["command_decision"] == "COMMAND_PREVIEW_BLOCKED"
    assert "DIRTY_WORKTREE" in result["stop_conditions"]
    assert result["safety"]["status"] == "BLOCKED"


def test_safety_invariants_never_launch_or_mutate() -> None:
    result = _result(human_owner_worker_launch_approval="APPROVED_FOR_WORKER_LAUNCH")
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
