from __future__ import annotations

import json

from automation.orchestration.self_development.aios_governed_self_development_soak import (
    DEFAULT_CYCLES,
    SCHEMA,
    build_governed_self_development_soak_result,
)


def _governed_loop(status: str = "PASS", **safety_overrides: object) -> dict:
    safety = {
        "status": status,
        "writes_files": False,
        "writes_reports": False,
        "writes_telemetry": False,
        "writes_packet_drafts": False,
        "writes_proposed_packets": False,
        "outputs_packet_body": False,
        "creates_ready_stage": False,
        "mutates_registry": False,
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approvals": False,
        "writes_relay": False,
        "starts_runtime": False,
        "launches_workers": False,
        "scheduler_or_daemon": False,
        "protected_action_recommended": False,
        "secrets_or_env_access": False,
        "broker_or_live_trading": False,
    }
    safety.update(safety_overrides)
    return {
        "schema": "AIOS_GOVERNED_SELF_DEVELOPMENT_LOOP_RESULT.v1",
        "safety": safety,
        "stop_conditions": [] if status == "PASS" else ["TEST_BLOCKER"],
    }


def _hard_gate(status: str = "PASS", **safety_overrides: object) -> dict:
    safety = {
        "status": status,
        "writes_files": False,
        "writes_reports": False,
        "writes_telemetry": False,
        "writes_packet_drafts": False,
        "writes_proposed_packets": False,
        "outputs_packet_body": False,
        "creates_ready_stage": False,
        "mutates_registry": False,
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approvals": False,
        "writes_relay": False,
        "starts_runtime": False,
        "launches_workers": False,
        "scheduler_or_daemon": False,
        "protected_action_recommended": False,
        "secrets_or_env_access": False,
        "broker_or_live_trading": False,
    }
    safety.update(safety_overrides)
    return {
        "schema": "AIOS_APPROVAL_SOS_HARD_GATE_RESULT.v1",
        "safety": safety,
        "stop_conditions": [] if status == "PASS" else ["TEST_BLOCKER"],
    }


def _no_write(**overrides: object) -> dict:
    proof = {
        "changed": False,
        "git_state_changed": False,
        "forbidden_surface_changed": False,
    }
    proof.update(overrides)
    return proof


def _cycle(index: int, governed_loop: dict | None = None, hard_gate: dict | None = None, no_write: dict | None = None) -> dict:
    return {
        "cycle_index": index,
        "governed_loop_result": governed_loop or _governed_loop(),
        "approval_sos_hard_gate_result": hard_gate or _hard_gate(),
        "no_write_proof": no_write or _no_write(),
    }


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "cycles_requested": DEFAULT_CYCLES,
        "max_cycles": 10,
        "repo_state": {
            "branch": "feature/final-governed-autonomy-closure-v1",
            "expected_branch": "feature/final-governed-autonomy-closure-v1",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_soak_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "cycle_results": [_cycle(1), _cycle(2), _cycle(3)],
        "no_write_proof": _no_write(),
    }
    payload.update(overrides)
    return payload


def test_python_logic_emits_soak_schema() -> None:
    result = build_governed_self_development_soak_result(_payload())

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["aggregate_status"] == "PASS"


def test_default_cycles_are_three() -> None:
    result = build_governed_self_development_soak_result(_payload())

    assert DEFAULT_CYCLES == 3
    assert result["cycles_requested"] == 3
    assert result["cycles_completed"] == 3


def test_max_cycles_prevents_excessive_loops() -> None:
    result = build_governed_self_development_soak_result(
        _payload(cycles_requested=11, max_cycles=10, cycle_results=[])
    )

    assert result["aggregate_status"] == "BLOCKED"
    assert "CYCLES_REQUESTED_EXCEEDS_MAX" in result["stop_conditions"]
    assert result["cycles_completed"] == 0


def test_soak_blocks_if_any_cycle_reports_forbidden_surface_delta() -> None:
    result = build_governed_self_development_soak_result(
        _payload(cycle_results=[_cycle(1), _cycle(2, no_write=_no_write(changed=True, forbidden_surface_changed=True)), _cycle(3)])
    )

    assert result["aggregate_status"] == "BLOCKED_BY_WRITE_SURFACE_RISK"
    assert result["forbidden_surface_deltas"]
    assert "CYCLE_2_FORBIDDEN_SURFACE_DELTA_FORBIDDEN_ROOTS" in result["stop_conditions"]


def test_soak_blocks_if_governed_loop_is_not_pass() -> None:
    result = build_governed_self_development_soak_result(
        _payload(cycle_results=[_cycle(1), _cycle(2, governed_loop=_governed_loop("BLOCKED")), _cycle(3)])
    )

    assert result["aggregate_status"] == "BLOCKED"
    assert "CYCLE_2_GOVERNED_LOOP_NOT_PASS" in result["stop_conditions"]
    assert result["safety"]["governed_loop_pass"] is False


def test_soak_blocks_if_approval_sos_hard_gate_is_not_pass() -> None:
    result = build_governed_self_development_soak_result(
        _payload(cycle_results=[_cycle(1), _cycle(2, hard_gate=_hard_gate("BLOCKED")), _cycle(3)])
    )

    assert result["aggregate_status"] == "BLOCKED"
    assert "CYCLE_2_APPROVAL_SOS_HARD_GATE_NOT_PASS" in result["stop_conditions"]
    assert result["safety"]["approval_sos_hard_gate_pass"] is False


def test_soak_proves_no_runtime_worker_scheduler_daemon_launch() -> None:
    result = build_governed_self_development_soak_result(_payload())

    assert result["safety"]["starts_runtime"] is False
    assert result["safety"]["launches_workers"] is False
    assert result["safety"]["scheduler_or_daemon"] is False


def test_soak_proves_no_queue_lock_approval_mutation() -> None:
    result = build_governed_self_development_soak_result(_payload())

    assert result["safety"]["mutates_queue"] is False
    assert result["safety"]["mutates_locks"] is False
    assert result["safety"]["mutates_approvals"] is False


def test_soak_proves_no_reports_telemetry_relay_writes() -> None:
    result = build_governed_self_development_soak_result(_payload())

    assert result["safety"]["writes_reports"] is False
    assert result["safety"]["writes_telemetry"] is False
    assert result["safety"]["writes_relay"] is False


def test_soak_proves_no_secrets_env_or_broker_live_trading_path() -> None:
    result = build_governed_self_development_soak_result(_payload())

    assert result["safety"]["secrets_or_env_access"] is False
    assert result["safety"]["broker_or_live_trading"] is False


def test_result_does_not_emit_protected_action_command_text() -> None:
    result = build_governed_self_development_soak_result(_payload())
    encoded = json.dumps(result).lower()

    assert "git add" not in encoded
    assert "git commit" not in encoded
    assert "git push" not in encoded
    assert "gh pr" not in encoded
    assert "start-aios" not in encoded

