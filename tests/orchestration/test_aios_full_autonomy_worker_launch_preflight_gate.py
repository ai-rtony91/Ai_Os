from __future__ import annotations

from automation.orchestration.self_development.aios_full_autonomy_worker_launch_preflight_gate import (
    BLOCKED_WORKER_LANES,
    SCHEMA,
    build_full_autonomy_worker_launch_preflight_gate_result,
)


def _repo_state(**overrides: object) -> dict:
    state = {
        "branch": "feature/full-autonomy-worker-launch-preflight-gate-v1",
        "expected_branch": "feature/full-autonomy-worker-launch-preflight-gate-v1",
        "branch_matches_expected": True,
        "dirty": False,
        "dirty_allowed_for_full_autonomy_worker_launch_preflight_gate_validation": False,
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
        "requested_autonomy_level": "LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
        "operating_profile": "24H_SUPERVISED",
        "requested_worker_posture": "READ_ONLY_VALIDATOR_CREW",
        "human_owner_worker_launch_approval": "",
        "identity_spine_status": "PASS",
        "validator_chain_status": "PASS",
        "approval_sos_status": "CLEAR",
        "governed_soak_status": "PASS",
        "activation_gate_status": "PASS",
        "worker_posture_bridge_status": "PASS",
        "lock_collision_status": "CLEAR",
        "allowed_lanes": ["validator", "self_audit", "readiness_review"],
        "requested_worker_count": 2,
        "max_parallel_workers": 3,
        "no_write_proof": _no_write(),
    }
    payload.update(overrides)
    return payload


def _result(**overrides: object) -> dict:
    return build_full_autonomy_worker_launch_preflight_gate_result(_payload(**overrides))


def _decision(result: dict) -> str:
    return result["preflight_decision"]["decision"]


def test_python_logic_emits_preflight_gate_schema() -> None:
    result = _result()

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["worker_launch_executed"] is False


def test_missing_human_owner_worker_launch_approval_blocks_launch() -> None:
    result = _result()

    assert _decision(result) == "PREFLIGHT_PASS_AWAITING_HUMAN_APPROVAL"
    assert result["worker_launch_allowed_for_future_step"] is False
    assert result["worker_launch_executed"] is False
    assert "human_owner_worker_launch_approval" in result["missing_requirements"]


def test_pass_evidence_with_approval_is_eligible_but_not_executed() -> None:
    result = _result(human_owner_worker_launch_approval="APPROVED_FOR_WORKER_LAUNCH_PREFLIGHT")

    assert _decision(result) == "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED"
    assert result["worker_launch_allowed_for_future_step"] is True
    assert result["worker_launch_executed"] is False
    assert result["safety"]["launches_workers"] is False
    assert "separate approved worker-launch packet" in result["next_safe_action"]


def test_sos_active_blocks_launch() -> None:
    result = _result(approval_sos_status="SOS_ACTIVE")

    assert _decision(result) == "BLOCKED_BY_SOS"
    assert result["worker_launch_allowed_for_future_step"] is False
    assert result["human_wake_policy"]["wake_required"] is True
    assert result["safety"]["status"] == "BLOCKED"


def test_identity_missing_blocks_launch() -> None:
    result = _result(identity_spine_status="UNKNOWN")

    assert _decision(result) == "BLOCKED_BY_IDENTITY"
    assert "identity_spine_pass" in result["missing_requirements"]
    assert "identity spine validator" in result["next_safe_action"].lower()


def test_validator_missing_blocks_launch() -> None:
    result = _result(validator_chain_status="UNKNOWN")

    assert _decision(result) == "BLOCKED_BY_VALIDATORS"
    assert "validator_chain_pass_or_warn_reviewed" in result["missing_requirements"]
    assert "orchestration validator chain" in result["next_safe_action"].lower()


def test_validator_warn_reviewed_is_accepted() -> None:
    result = _result(
        validator_chain_status="WARN_REVIEWED",
        human_owner_worker_launch_approval="APPROVED_FOR_WORKER_LAUNCH_PREFLIGHT",
    )

    assert _decision(result) == "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED"


def test_governed_soak_missing_blocks_launch() -> None:
    result = _result(governed_soak_status="UNKNOWN")

    assert _decision(result) == "BLOCKED_BY_VALIDATORS"
    assert "governed_soak_pass" in result["missing_requirements"]
    assert "governed self-development soak" in result["next_safe_action"].lower()


def test_activation_gate_unsafe_status_requires_review() -> None:
    result = _result(activation_gate_status="DENIED")

    assert _decision(result) == "REVIEW_REQUIRED"
    assert "activation_gate_safe_ceiling" in result["missing_requirements"]


def test_worker_posture_bridge_blocked_requires_review() -> None:
    result = _result(worker_posture_bridge_status="BLOCKED")

    assert _decision(result) == "REVIEW_REQUIRED"
    assert "worker_posture_bridge_pass" in result["missing_requirements"]


def test_lock_collision_blocks_launch() -> None:
    result = _result(lock_collision_status="COLLISION")

    assert _decision(result) == "BLOCKED_BY_LOCK_COLLISION"
    assert "lock_collision_clear" in result["missing_requirements"]


def test_empty_allowed_lanes_block_launch() -> None:
    result = _result(allowed_lanes=[])

    assert _decision(result) == "BLOCKED_BY_EMPTY_ALLOWED_LANES"
    assert "allowed_lanes_non_empty" in result["missing_requirements"]


def test_protected_lane_blocks_launch() -> None:
    result = _result(allowed_lanes=["validator", "runtime_execution"])

    assert _decision(result) == "BLOCKED_BY_PROTECTED_LANE"
    assert "remove_protected_lane:runtime_execution" in result["missing_requirements"]


def test_secret_or_broker_lane_blocks_launch() -> None:
    result = _result(allowed_lanes=["validator", "broker"])

    assert _decision(result) == "BLOCKED_BY_SECRETS_OR_BROKER_BOUNDARY"
    assert "remove_secret_or_broker_lane:broker" in result["missing_requirements"]


def test_lane_not_allowed_for_posture_blocks_launch() -> None:
    result = _result(
        requested_worker_posture="WEEKEND_LOW_TOUCH_CREW",
        allowed_lanes=["validator", "packet_preview"],
    )

    assert _decision(result) == "BLOCKED_BY_PROTECTED_LANE"
    assert "lane_not_allowed_for_posture:packet_preview" in result["missing_requirements"]


def test_dirty_repo_outside_approved_files_blocks_launch() -> None:
    result = _result(
        repo_state=_repo_state(
            dirty=True,
            dirty_allowed_for_full_autonomy_worker_launch_preflight_gate_validation=False,
        )
    )

    assert _decision(result) == "BLOCKED_BY_REPO_STATE"
    assert "DIRTY_WORKTREE" in result["stop_conditions"]
    assert result["safety"]["status"] == "BLOCKED"


def test_no_write_surface_delta_blocks_launch() -> None:
    result = _result(no_write_proof=_no_write(changed=True, forbidden_surface_changed=True))

    assert _decision(result) == "BLOCKED_BY_REPO_STATE"
    assert "WRITE_SURFACE_RISK" in result["stop_conditions"]
    assert result["safety"]["status"] == "BLOCKED_BY_WRITE_SURFACE_RISK"


def test_no_workers_posture_is_advisory_only() -> None:
    result = _result(requested_worker_posture="NO_WORKERS", allowed_lanes=[])

    assert _decision(result) == "PREFLIGHT_PASS_ADVISORY_ONLY"
    assert result["worker_launch_allowed_for_future_step"] is False
    assert result["max_parallel_workers"] == 0


def test_read_only_validator_crew_caps_workers() -> None:
    result = _result(
        requested_worker_posture="READ_ONLY_VALIDATOR_CREW",
        allowed_lanes=["validator", "self_audit", "readiness_review", "approval_sos_review"],
        requested_worker_count=9,
        max_parallel_workers=9,
    )

    assert result["max_parallel_workers"] <= 2
    assert result["recommended_worker_count"] <= 2


def test_packet_preview_crew_caps_workers() -> None:
    result = _result(
        requested_worker_posture="PACKET_PREVIEW_CREW",
        allowed_lanes=["packet_preview", "validator", "readiness_review"],
        requested_worker_count=9,
        max_parallel_workers=9,
    )

    assert result["max_parallel_workers"] <= 2
    assert result["recommended_worker_count"] <= 2


def test_supervised_day_crew_12h_caps_workers() -> None:
    result = _result(
        requested_worker_posture="SUPERVISED_DAY_CREW_12H",
        allowed_lanes=["validator", "self_audit", "packet_preview", "readiness_review"],
        requested_worker_count=9,
        max_parallel_workers=9,
    )

    assert result["max_parallel_workers"] <= 2
    assert result["recommended_worker_count"] <= 2


def test_supervised_day_night_crew_24h_caps_workers() -> None:
    result = _result(
        requested_worker_posture="SUPERVISED_DAY_NIGHT_CREW_24H",
        allowed_lanes=["validator", "no_ready_stage_discovery", "packet_preview", "approval_sos_review"],
        requested_worker_count=9,
        max_parallel_workers=9,
    )

    assert result["max_parallel_workers"] <= 3
    assert result["recommended_worker_count"] <= 3


def test_weekend_low_touch_crew_caps_workers() -> None:
    result = _result(
        requested_worker_posture="WEEKEND_LOW_TOUCH_CREW",
        allowed_lanes=["validator", "status_review"],
        requested_worker_count=9,
        max_parallel_workers=9,
    )

    assert result["max_parallel_workers"] <= 1
    assert result["recommended_worker_count"] <= 1


def test_vacation_emergency_only_crew_caps_workers_and_blocks_implementation() -> None:
    result = _result(
        requested_worker_posture="VACATION_EMERGENCY_ONLY_CREW",
        allowed_lanes=["approval_sos_review", "security_boundary_review"],
        requested_worker_count=9,
        max_parallel_workers=9,
    )

    assert result["max_parallel_workers"] <= 1
    assert result["recommended_worker_count"] <= 1
    assert "packet_preview" not in result["allowed_worker_lanes"]
    assert "self_audit" not in result["allowed_worker_lanes"]


def test_full_autonomy_supervised_crew_caps_workers_and_requires_approval() -> None:
    result = _result(
        requested_worker_posture="FULL_AUTONOMY_SUPERVISED_CREW",
        allowed_lanes=["validator", "packet_preview", "full_autonomy_prerequisite_review", "approval_sos_review"],
        requested_worker_count=9,
        max_parallel_workers=9,
    )

    assert result["max_parallel_workers"] <= 3
    assert result["recommended_worker_count"] <= 3
    assert _decision(result) == "PREFLIGHT_PASS_AWAITING_HUMAN_APPROVAL"
    assert "human_owner_worker_launch_approval" in result["missing_requirements"]


def test_blocked_lanes_include_protected_boundaries() -> None:
    blocked = set(_result()["blocked_worker_lanes"])

    for lane in (
        "runtime_execution",
        "scheduler",
        "daemon",
        "live_trading",
        "broker",
        "secrets",
        "queue_mutation",
        "lock_mutation",
        "approval_mutation",
        "registry_mutation",
        "reports_write",
        "telemetry_write",
        "relay_write",
        "dashboard_ui",
        "trading_lab",
        "forex",
        "oanda",
        "webhook",
        "orders",
    ):
        assert lane in blocked
    assert set(BLOCKED_WORKER_LANES).issubset(blocked)


def test_safety_invariants_never_launch_or_mutate() -> None:
    result = _result(human_owner_worker_launch_approval="APPROVED_FOR_WORKER_LAUNCH_PREFLIGHT")
    safety = result["safety"]

    assert safety["writes_files"] is False
    assert safety["mutates_registry"] is False
    assert safety["creates_ready_stage"] is False
    assert safety["mutates_queue"] is False
    assert safety["mutates_locks"] is False
    assert safety["mutates_approval"] is False
    assert safety["writes_reports"] is False
    assert safety["writes_telemetry"] is False
    assert safety["writes_relay"] is False
    assert safety["starts_runtime"] is False
    assert safety["launches_workers"] is False
    assert safety["enables_scheduler"] is False
    assert safety["starts_daemon"] is False
    assert safety["touches_secrets_or_env"] is False
    assert safety["broker_or_live_trading"] is False
    assert safety["protected_actions_blocked"] is True
    assert safety["human_owner_required_before_worker_launch"] is True
    assert safety["worker_launch_executed"] is False
