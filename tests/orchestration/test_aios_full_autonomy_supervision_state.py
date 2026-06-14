from __future__ import annotations

import json

from automation.orchestration.self_development.aios_full_autonomy_supervision_state import (
    BLOCKED_WORKER_LANES,
    REQUESTED_AUTONOMY_LEVELS,
    SCHEMA,
    SAFE_WORKER_LANES,
    build_full_autonomy_supervision_state_result,
)


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "feature/semi-autonomy-idle-planner-v1",
            "expected_branch": "feature/semi-autonomy-idle-planner-v1",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_full_autonomy_supervision_state_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "authority_context": {"all_required_loaded": True},
        "file_presence": {},
        "requested_autonomy_level": "LEVEL_3_SUPERVISED_AUTONOMY",
        "operating_profile": "12H_SUPERVISED",
        "human_available": True,
        "weekend_mode": False,
        "vacation_mode": False,
        "sleep_window_active": False,
        "max_autonomy_hours": 12,
        "recent_validator_status": "PASS",
        "recent_sos_status": "CLEAR",
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
    }
    payload.update(overrides)
    return payload


def _result(**overrides: object) -> dict:
    return build_full_autonomy_supervision_state_result(_payload(**overrides))


def test_python_logic_emits_full_autonomy_supervision_schema() -> None:
    result = _result()

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["safety"]["status"] == "PASS"


def test_level_0_manual_reports_manual_only() -> None:
    result = _result(requested_autonomy_level="LEVEL_0_MANUAL")

    assert result["resolved_autonomy_level"] == "LEVEL_0_MANUAL"
    assert result["worker_supervision"]["worker_supervision_status"] == "MANUAL_ONLY"
    assert result["worker_supervision"]["recommended_worker_count"] == 0


def test_level_1_assisted_reports_recommendation_only() -> None:
    result = _result(requested_autonomy_level="LEVEL_1_ASSISTED")

    assert result["resolved_autonomy_level"] == "LEVEL_1_ASSISTED"
    assert result["worker_supervision"]["worker_supervision_status"] == "RECOMMENDATION_ONLY"
    assert result["worker_supervision"]["worker_launch_allowed"] is False


def test_level_2_semi_autonomous_allows_packet_and_validator_planning_only() -> None:
    result = _result(requested_autonomy_level="LEVEL_2_SEMI_AUTONOMOUS")

    lanes = set(result["worker_supervision"]["allowed_worker_lanes"])
    assert result["resolved_autonomy_level"] == "LEVEL_2_SEMI_AUTONOMOUS"
    assert {"packet_preview", "validator", "semi_autonomy_planning"}.issubset(lanes)
    assert result["safety"]["protected_actions_blocked"] is True


def test_level_3_supervised_autonomy_blocks_self_approval() -> None:
    result = _result(requested_autonomy_level="LEVEL_3_SUPERVISED_AUTONOMY")

    assert result["resolved_autonomy_level"] == "LEVEL_3_SUPERVISED_AUTONOMY"
    assert result["worker_supervision"]["autonomous_continuation_allowed"] is True
    assert result["approval_gate"]["self_approval_allowed"] is False
    assert result["safety"]["self_approval_allowed"] is False


def test_level_4_conditional_full_autonomy_remains_read_only() -> None:
    result = _result(requested_autonomy_level="LEVEL_4_CONDITIONAL_FULL_AUTONOMY")

    assert result["resolved_autonomy_level"] == "LEVEL_4_CONDITIONAL_FULL_AUTONOMY"
    assert result["full_autonomy_state"]["effective_autonomy_ceiling"] == "LEVEL_4_CONDITIONAL_FULL_AUTONOMY"
    assert result["safety"]["starts_runtime"] is False
    assert result["safety"]["launches_workers"] is False


def test_level_5_full_autonomy_requested_does_not_become_approved() -> None:
    result = _result(requested_autonomy_level="LEVEL_5_FULL_AUTONOMY_REQUESTED")

    assert result["resolved_autonomy_level"] == "FULL_AUTONOMY_REQUESTED_BUT_NOT_APPROVED"
    assert result["full_autonomy_state"]["true_full_autonomy_approved"] is False
    assert "explicit_human_owner_full_autonomy_approval" in result["full_autonomy_state"]["missing_prerequisites_for_true_full_autonomy"]
    assert result["safety"]["status"] == "REVIEW_REQUIRED"


def test_all_allowed_requested_levels_resolve_without_full_autonomy_approval() -> None:
    for level in REQUESTED_AUTONOMY_LEVELS:
        result = _result(requested_autonomy_level=level)
        assert result["requested_autonomy_level"] == level
        assert result["full_autonomy_state"]["self_approval_allowed"] is False


def test_12h_supervised_profile_resolves_bounded_supervised_mode() -> None:
    result = _result(operating_profile="12H_SUPERVISED")

    assert result["worker_supervision"]["worker_shift_mode"] == "BOUNDED_12H_SUPERVISED"
    assert result["worker_supervision"]["max_parallel_workers"] <= 2
    assert result["approval_gate"]["before_commit"] is True


def test_24h_supervised_allows_only_read_only_overnight_recommendations() -> None:
    result = _result(operating_profile="24H_SUPERVISED")

    assert result["worker_supervision"]["worker_shift_mode"] == "READ_ONLY_24H_MONITORING"
    assert result["worker_supervision"]["max_parallel_workers"] == 1
    assert result["worker_supervision"]["worker_launch_allowed"] is False


def test_weekend_lowers_intervention_and_blocks_protected_action() -> None:
    result = _result(operating_profile="WEEKEND", weekend_mode=True)

    assert result["human_wake_policy"]["wake_class"] == "WEEKEND_LOW_INTERVENTION"
    assert result["safety"]["protected_actions_blocked"] is True


def test_vacation_minimizes_disturbance_and_blocks_implementation_recommendations() -> None:
    result = _result(operating_profile="VACATION", vacation_mode=True)

    assert result["worker_supervision"]["recommended_worker_count"] == 0
    assert result["worker_supervision"]["max_parallel_workers"] == 0
    assert "Idle" in result["next_safe_action"]


def test_overnight_blocks_protected_action_and_recommends_read_only_health_checks() -> None:
    result = _result(operating_profile="OVERNIGHT")

    assert result["worker_supervision"]["worker_shift_mode"] == "READ_ONLY_OVERNIGHT"
    assert "read-only health checks" in result["next_safe_action"]
    assert result["safety"]["protected_actions_blocked"] is True


def test_emergency_review_activates_wake_policy_and_blocks_normal_work() -> None:
    result = _result(operating_profile="EMERGENCY_REVIEW")

    assert result["sos_gate"]["sos_hard_stop_active"] is True
    assert result["human_wake_policy"]["wake_required"] is True
    assert result["safety"]["status"] == "BLOCKED"


def test_full_autonomy_supervised_preserves_approval_gate() -> None:
    result = _result(operating_profile="FULL_AUTONOMY_SUPERVISED", requested_autonomy_level="LEVEL_4_CONDITIONAL_FULL_AUTONOMY")

    assert result["worker_supervision"]["worker_shift_mode"] == "FULL_AUTONOMY_SUPERVISED_PREVIEW"
    assert result["approval_gate"]["human_owner_required"] is True
    assert result["approval_gate"]["self_approval_allowed"] is False


def test_worker_launch_is_never_allowed_by_resolver() -> None:
    for profile in ("12H_SUPERVISED", "24H_SUPERVISED", "WEEKEND", "VACATION", "OVERNIGHT", "FULL_AUTONOMY_SUPERVISED"):
        result = _result(operating_profile=profile)
        assert result["worker_supervision"]["worker_launch_allowed"] is False
        assert result["safety"]["launches_workers"] is False


def test_recommended_workers_are_advisory_only_and_bounded() -> None:
    result = _result(operating_profile="FULL_AUTONOMY_SUPERVISED", requested_autonomy_level="LEVEL_4_CONDITIONAL_FULL_AUTONOMY")

    assert result["worker_supervision"]["recommended_worker_count"] <= result["worker_supervision"]["max_parallel_workers"]
    assert result["worker_supervision"]["max_parallel_workers"] <= 2
    assert result["worker_supervision"]["supervisor_review_required"] is True


def test_allowed_lanes_are_safe_review_validator_and_planning_lanes() -> None:
    result = _result(requested_autonomy_level="LEVEL_4_CONDITIONAL_FULL_AUTONOMY")

    assert set(result["worker_supervision"]["allowed_worker_lanes"]) == set(SAFE_WORKER_LANES)


def test_blocked_lanes_include_runtime_trading_broker_secrets_and_mutations() -> None:
    result = _result()
    blocked = set(result["worker_supervision"]["blocked_worker_lanes"])

    assert set(BLOCKED_WORKER_LANES).issubset(blocked)
    for lane in ("runtime_execution", "live_trading", "broker", "secrets", "queue_mutation", "lock_mutation", "approval_mutation", "registry_mutation"):
        assert lane in blocked


def test_max_parallel_workers_is_profile_aware() -> None:
    assert _result(operating_profile="VACATION")["worker_supervision"]["max_parallel_workers"] == 0
    assert _result(operating_profile="24H_SUPERVISED")["worker_supervision"]["max_parallel_workers"] == 1
    assert _result(operating_profile="12H_SUPERVISED")["worker_supervision"]["max_parallel_workers"] <= 2


def test_human_wake_policy_changes_by_profile() -> None:
    vacation = _result(operating_profile="VACATION", vacation_mode=True)
    weekend = _result(operating_profile="WEEKEND", weekend_mode=True)
    overnight = _result(operating_profile="OVERNIGHT", sleep_window_active=True)

    assert vacation["human_wake_policy"]["wake_class"] == "VACATION_CRITICAL_ONLY"
    assert weekend["human_wake_policy"]["wake_class"] == "WEEKEND_LOW_INTERVENTION"
    assert overnight["human_wake_policy"]["wake_class"] == "SLEEP_WINDOW_CRITICAL_ONLY"


def test_full_autonomy_prerequisites_are_emitted() -> None:
    result = _result()
    prereqs = result["full_autonomy_prerequisites"]

    for key in (
        "repo_clean",
        "main_or_expected_branch_confirmed",
        "authority_files_present",
        "identity_spine_passed_or_required",
        "validator_chain_passed_or_required",
        "approval_sos_hard_gate_present",
        "governed_soak_present",
        "no_ready_stage_discovery_available",
        "protected_action_gate_present",
        "broker_live_trading_blocked",
        "secrets_env_blocked",
    ):
        assert key in prereqs


def test_missing_approval_prevents_true_full_autonomy() -> None:
    result = _result(requested_autonomy_level="LEVEL_5_FULL_AUTONOMY_REQUESTED")

    assert result["full_autonomy_state"]["explicit_human_owner_approval_evidence_present"] is False
    assert result["full_autonomy_state"]["true_full_autonomy_approved"] is False


def test_hard_gate_and_soak_prerequisites_are_recognized() -> None:
    result = _result()

    assert result["full_autonomy_prerequisites"]["approval_sos_hard_gate_present"]["satisfied"] is True
    assert result["full_autonomy_prerequisites"]["governed_soak_present"]["satisfied"] is True


def test_broker_live_trading_and_secrets_remain_blocked() -> None:
    result = _result()

    assert result["full_autonomy_prerequisites"]["broker_live_trading_blocked"]["satisfied"] is True
    assert result["full_autonomy_prerequisites"]["secrets_env_blocked"]["satisfied"] is True
    assert result["safety"]["broker_or_live_trading"] is False
    assert result["safety"]["touches_secrets_or_env"] is False


def test_protected_actions_remain_blocked_and_human_owner_required() -> None:
    result = _result()

    assert result["safety"]["protected_actions_blocked"] is True
    assert result["safety"]["human_owner_required_before_protected_action"] is True
    assert result["approval_gate"]["before_apply"] is True
    assert result["approval_gate"]["before_commit"] is True
    assert result["approval_gate"]["before_push"] is True
    assert result["approval_gate"]["before_merge"] is True


def test_sos_hard_stop_overrides_profiles() -> None:
    result = _result(operating_profile="24H_SUPERVISED", recent_sos_status="SOS_HARD_STOP")

    assert result["sos_gate"]["sos_hard_stop_active"] is True
    assert result["safety"]["status"] == "BLOCKED"
    assert "SOS_HARD_STOP" in result["stop_conditions"]


def test_approval_gate_warn_is_review_required_not_fail() -> None:
    result = _result(recent_validator_status="APPROVAL_GATE_WARN")

    assert result["safety"]["status"] == "REVIEW_REQUIRED"
    assert result["approval_gate"]["status"] == "REVIEW_REQUIRED"
    assert result["safety"]["status"] != "FAIL"


def test_commit_package_warn_is_review_required_not_fail() -> None:
    result = _result(recent_validator_status="COMMIT_PACKAGE_WARN")

    assert result["safety"]["status"] == "REVIEW_REQUIRED"
    assert result["approval_gate"]["status"] == "REVIEW_REQUIRED"
    assert result["safety"]["status"] != "FAIL"


def test_no_mutations_reports_telemetry_relay_dashboard_or_runtime_are_selected() -> None:
    result = _result()

    assert result["safety"]["mutates_queue"] is False
    assert result["safety"]["mutates_locks"] is False
    assert result["safety"]["mutates_approval"] is False
    assert result["safety"]["mutates_registry"] is False
    assert result["safety"]["writes_reports"] is False
    assert result["safety"]["writes_telemetry"] is False
    assert result["safety"]["writes_relay"] is False
    assert result["safety"]["starts_runtime"] is False
    assert result["safety"]["enables_scheduler"] is False
    assert result["safety"]["starts_daemon"] is False
    assert "dashboard_ui" not in result["worker_supervision"]["allowed_worker_lanes"]
    assert "dashboard_ui" in result["worker_supervision"]["blocked_worker_lanes"]


def test_dirty_worktree_outside_approved_files_blocks_logic() -> None:
    result = _result(
        repo_state={
            "branch": "feature/semi-autonomy-idle-planner-v1",
            "expected_branch": "feature/semi-autonomy-idle-planner-v1",
            "branch_matches_expected": True,
            "dirty": True,
            "dirty_allowed_for_full_autonomy_supervision_state_validation": False,
            "fail_on_dirty_worktree": True,
        }
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "DIRTY_WORKTREE" in result["stop_conditions"]


def test_result_does_not_emit_protected_action_command_text() -> None:
    result = _result()
    encoded = json.dumps(result).lower()

    for phrase in ("git add", "git commit", "git push", "gh pr", "git merge", "start-aios", "open-aiosworker"):
        assert phrase not in encoded
