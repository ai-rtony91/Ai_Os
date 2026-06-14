from __future__ import annotations

from automation.orchestration.self_development.aios_full_autonomy_activation_gate import (
    build_full_autonomy_activation_gate_result,
)
from automation.orchestration.self_development.aios_full_autonomy_worker_posture_bridge import (
    BLOCKED_WORKER_LANES,
    SCHEMA,
    build_full_autonomy_worker_posture_bridge_result,
)


def _repo_state() -> dict:
    return {
        "branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
        "expected_branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
        "branch_matches_expected": True,
        "dirty": False,
        "dirty_allowed_for_full_autonomy_worker_posture_bridge_validation": False,
        "fail_on_dirty_worktree": True,
    }


def _no_write(**overrides: object) -> dict:
    proof = {
        "changed": False,
        "git_state_changed": False,
        "forbidden_surface_changed": False,
    }
    proof.update(overrides)
    return proof


def _activation(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
            "expected_branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_full_autonomy_activation_gate_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "requested_autonomy_level": "LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
        "operating_profile": "12H_SUPERVISED",
        "human_owner_approval_evidence": "",
        "identity_spine_status": "PASS",
        "validator_chain_status": "PASS",
        "approval_sos_status": "CLEAR",
        "governed_soak_status": "PASS",
        "no_write_proof": _no_write(),
    }
    payload.update(overrides)
    return build_full_autonomy_activation_gate_result(payload)


def _result(**overrides: object) -> dict:
    activation = overrides.pop("activation_gate_result", _activation(operating_profile=overrides.get("operating_profile", "12H_SUPERVISED")))
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": _repo_state(),
        "operating_profile": "12H_SUPERVISED",
        "activation_gate_result": activation,
        "no_write_proof": _no_write(),
    }
    payload.update(overrides)
    return build_full_autonomy_worker_posture_bridge_result(payload)


def test_python_logic_emits_worker_posture_schema() -> None:
    result = _result()

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["worker_launch_allowed"] is False


def test_12h_profile_gives_bounded_advisory_workers() -> None:
    activation = _activation(operating_profile="12H_SUPERVISED", human_owner_approval_evidence="APPROVED_FOR_SUPERVISED_REVIEW")
    result = _result(operating_profile="12H_SUPERVISED", activation_gate_result=activation)

    assert result["worker_posture"] == "SUPERVISED_DAY_CREW_12H"
    assert result["max_parallel_workers"] <= 2
    assert set(result["allowed_worker_lanes"]) == {"validator", "self_audit", "packet_preview", "readiness_review"}
    assert result["worker_launch_allowed"] is False


def test_24h_profile_gives_advisory_monitoring_posture() -> None:
    activation = _activation(operating_profile="24H_SUPERVISED", human_owner_approval_evidence="APPROVED_FOR_SUPERVISED_REVIEW")
    result = _result(operating_profile="24H_SUPERVISED", activation_gate_result=activation)

    assert result["worker_posture"] == "SUPERVISED_DAY_NIGHT_CREW_24H"
    assert result["max_parallel_workers"] <= 3
    assert {"validator", "no_ready_stage_discovery", "packet_preview", "approval_sos_review"}.issubset(set(result["allowed_worker_lanes"]))
    assert result["worker_launch_allowed"] is False
    assert "Wake only for SOS" in result["human_wake_policy"]


def test_24h_without_approval_stays_read_only_validator_crew() -> None:
    activation = _activation(operating_profile="24H_SUPERVISED")
    result = _result(operating_profile="24H_SUPERVISED", activation_gate_result=activation)

    assert result["worker_posture"] == "READ_ONLY_VALIDATOR_CREW"
    assert result["recommended_worker_count"] <= 1
    assert result["worker_launch_allowed"] is False


def test_weekend_gives_low_touch_posture() -> None:
    activation = _activation(operating_profile="WEEKEND", human_owner_approval_evidence="APPROVED_FOR_SUPERVISED_REVIEW")
    result = _result(operating_profile="WEEKEND", activation_gate_result=activation)

    assert result["worker_posture"] == "WEEKEND_LOW_TOUCH_CREW"
    assert result["max_parallel_workers"] <= 1
    assert set(result["allowed_worker_lanes"]) == {"validator", "status_review"}
    assert "Low-touch weekend" in result["human_wake_policy"]


def test_vacation_gives_emergency_only_posture() -> None:
    activation = _activation(operating_profile="VACATION", human_owner_approval_evidence="APPROVED_FOR_SUPERVISED_REVIEW")
    result = _result(operating_profile="VACATION", activation_gate_result=activation)

    assert result["worker_posture"] == "VACATION_EMERGENCY_ONLY_CREW"
    assert result["recommended_worker_count"] == 0
    assert result["max_parallel_workers"] == 0
    assert "emergency-only" in result["next_safe_action"].lower()


def test_full_autonomy_supervised_is_advisory_unless_approved() -> None:
    activation = _activation(
        requested_autonomy_level="LEVEL_5_FULL_AUTONOMY_REQUESTED",
        operating_profile="FULL_AUTONOMY_SUPERVISED",
    )
    result = _result(operating_profile="FULL_AUTONOMY_SUPERVISED", activation_gate_result=activation)

    assert result["worker_posture"] == "BLOCKED_BY_APPROVAL"
    assert result["worker_launch_allowed"] is False
    assert result["safety"]["advisory_only"] is True


def test_full_autonomy_supervised_lower_level_stays_preview_validation() -> None:
    activation = _activation(
        requested_autonomy_level="LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
        operating_profile="FULL_AUTONOMY_SUPERVISED",
    )
    result = _result(operating_profile="FULL_AUTONOMY_SUPERVISED", activation_gate_result=activation)

    assert result["worker_posture"] == "PACKET_PREVIEW_CREW"
    assert result["max_parallel_workers"] <= 3
    assert result["worker_launch_allowed"] is False


def test_blocked_lanes_include_runtime_scheduler_daemon_trading_broker_secrets_and_mutations() -> None:
    result = _result()
    blocked = set(result["blocked_worker_lanes"])

    for lane in (
        "runtime",
        "scheduler",
        "daemon",
        "trading",
        "broker",
        "secrets",
        "queue",
        "lock",
        "approval",
        "registry",
    ):
        assert lane in blocked
    assert set(BLOCKED_WORKER_LANES).issubset(blocked)


def test_worker_launch_allowed_is_false_by_default() -> None:
    for profile in ("12H_SUPERVISED", "24H_SUPERVISED", "WEEKEND", "VACATION", "FULL_AUTONOMY_SUPERVISED"):
        activation = _activation(operating_profile=profile)
        result = _result(operating_profile=profile, activation_gate_result=activation)
        assert result["worker_launch_allowed"] is False
        assert result["safety"]["launches_workers"] is False


def test_wake_policy_changes_by_profile() -> None:
    profiles = {
        "12H_SUPERVISED": "protected action",
        "24H_SUPERVISED": "Wake only for SOS",
        "WEEKEND": "Low-touch weekend",
        "VACATION": "Vacation mode",
    }

    for profile, expected in profiles.items():
        activation = _activation(operating_profile=profile, human_owner_approval_evidence="APPROVED_FOR_SUPERVISED_REVIEW")
        result = _result(operating_profile=profile, activation_gate_result=activation)
        assert expected in result["human_wake_policy"]


def test_sos_activation_maps_to_blocked_by_sos() -> None:
    activation = _activation(approval_sos_status="SOS_ACTIVE")
    result = _result(activation_gate_result=activation)

    assert result["worker_posture"] == "BLOCKED_BY_SOS"
    assert result["max_parallel_workers"] == 0
    assert result["worker_launch_allowed"] is False


def test_validation_review_maps_to_blocked_by_validation() -> None:
    activation = _activation(identity_spine_status="UNKNOWN")
    result = _result(activation_gate_result=activation)

    assert result["worker_posture"] == "BLOCKED_BY_VALIDATION"
    assert result["worker_launch_allowed"] is False
    assert "Run the recommended validators" in result["next_safe_action"]


def test_no_queue_lock_approval_registry_runtime_or_trading_mutation() -> None:
    result = _result()

    assert result["safety"]["mutates_queue"] is False
    assert result["safety"]["mutates_locks"] is False
    assert result["safety"]["mutates_approval"] is False
    assert result["safety"]["mutates_approvals"] is False
    assert result["safety"]["mutates_registry"] is False
    assert result["safety"]["starts_runtime"] is False
    assert result["safety"]["enables_scheduler"] is False
    assert result["safety"]["starts_daemon"] is False
    assert result["safety"]["secrets_or_env_access"] is False
    assert result["safety"]["broker_or_live_trading"] is False
