from __future__ import annotations

from automation.forex_engine.one_shot_exception_assembler import (
    ONE_SHOT_EXCEPTION_BLOCKED,
    ONE_SHOT_EXCEPTION_INCOMPLETE,
    ONE_SHOT_EXCEPTION_REJECTED,
    ONE_SHOT_EXCEPTION_REVIEW_READY,
    assemble_one_shot_exception_package,
)


def _base_state() -> dict:
    return {
        "demo_validation_contract": {
            "demo_validation_contract_status": "DEMO_CONTRACT_COMPLETE",
            "live_readiness_candidate": True,
            "metric_summary": {
                "validation_expectancy": 0.12,
                "validation_profit_factor": 1.2,
                "validation_max_drawdown": 2.0,
                "validation_evidence_score": 0.85,
            },
        },
        "live_readiness_candidate": {
            "live_readiness_candidate": True,
        },
        "approval_trace": {
            "approval_window_active": True,
            "approval_window_status": "ACTIVE",
        },
        "risk_limits": {
            "maximum_loss": 1000.0,
            "daily_loss_cap": 300.0,
            "stop_loss": 20.0,
            "order_type": "market",
            "units_or_notional_limit": 0.05,
        },
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"verified": True},
        "reconciliation_proof": {"present": True},
        "external_runtime_connector_proof": {"present": True},
        "credential_boundary_proof": {"present": True},
        "account_boundary_proof": {"present": True},
        "one_shot_controls": {
            "one_order_only": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
            "manual_arming_required": True,
            "timeout_required": True,
            "final_disarm_required": True,
            "operator_review_required": True,
        },
        "evidence_freshness": {"evidence_fresh": True},
        "replayability_proof": {"verified": True},
        "final_disarm_proof": {"present": True},
        "post_trade_journal_path": "/tmp/journal.jsonl",
    }


def _run(state_overrides: dict | None = None, *, exact_state: bool = False) -> dict:
    state = _base_state()
    if state_overrides:
        if exact_state:
            state = state_overrides
        else:
            for key, value in state_overrides.items():
                if isinstance(value, dict) and isinstance(state.get(key), dict):
                    merged = state[key].copy()
                    merged.update(value)
                    state[key] = merged
                else:
                    state[key] = value
    return assemble_one_shot_exception_package(state)


def test_empty_state_blocks() -> None:
    result = assemble_one_shot_exception_package({})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert result["blockers"][0] == "missing_demo_validation_contract"


def test_complete_package_returns_review_ready() -> None:
    result = _run()
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_REVIEW_READY
    assert result["live_micro_trade_review_ready"] is True
    assert result["exception_package_completed"] is True


def test_missing_demo_contract_blocks() -> None:
    state = _base_state()
    state.pop("demo_validation_contract")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "missing_demo_validation_contract" in result["blockers"]


def test_incomplete_demo_contract_blocks() -> None:
    state = _base_state()
    state["demo_validation_contract"]["demo_validation_contract_status"] = "DEMO_CONTRACT_CONTINUE"
    state["demo_validation_contract"]["live_readiness_candidate"] = False
    result = _run(state)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "demo_contract_not_complete" in result["blockers"]


def test_missing_live_readiness_candidate_blocks() -> None:
    state = _base_state()
    state.pop("live_readiness_candidate")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "missing_live_readiness_candidate" in result["blockers"]


def test_missing_approval_trace_blocks() -> None:
    state = _base_state()
    state.pop("approval_trace")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "missing_approval_trace" in result["blockers"]


def test_missing_maximum_loss_blocks() -> None:
    state = _base_state()
    state["risk_limits"].pop("maximum_loss")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_maximum_loss" in result["blockers"]


def test_missing_daily_loss_cap_blocks() -> None:
    state = _base_state()
    state["risk_limits"].pop("daily_loss_cap")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_daily_loss_cap" in result["blockers"]


def test_missing_stop_loss_blocks() -> None:
    state = _base_state()
    state["risk_limits"].pop("stop_loss")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_stop_loss" in result["blockers"]


def test_missing_order_type_blocks() -> None:
    state = _base_state()
    state["risk_limits"].pop("order_type")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_order_type" in result["blockers"]


def test_missing_units_or_notional_limit_blocks() -> None:
    state = _base_state()
    state["risk_limits"].pop("units_or_notional_limit")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_units_or_notional_limit" in result["blockers"]


def test_missing_kill_switch_proof_blocks() -> None:
    state = _base_state()
    state.pop("kill_switch_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_kill_switch_proof" in result["blockers"]


def test_missing_rollback_proof_blocks() -> None:
    state = _base_state()
    state.pop("rollback_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_rollback_proof" in result["blockers"]


def test_missing_reconciliation_proof_blocks() -> None:
    state = _base_state()
    state.pop("reconciliation_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_reconciliation_proof" in result["blockers"]


def test_missing_external_runtime_connector_proof_blocks() -> None:
    state = _base_state()
    state.pop("external_runtime_connector_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_external_runtime_connector_proof" in result["blockers"]


def test_missing_credential_boundary_proof_blocks() -> None:
    state = _base_state()
    state.pop("credential_boundary_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_credential_boundary_proof" in result["blockers"]


def test_missing_account_boundary_proof_blocks() -> None:
    state = _base_state()
    state.pop("account_boundary_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_account_boundary_proof" in result["blockers"]


def test_missing_one_shot_controls_blocks() -> None:
    state = _base_state()
    state.pop("one_shot_controls")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_one_shot_controls" in result["blockers"]


def test_expired_approval_window_blocks() -> None:
    state = _base_state()
    state["approval_trace"]["approval_window_active"] = False
    state["approval_trace"]["approval_window_status"] = "EXPIRED"
    result = _run(state)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "approval_window_expired" in result["blockers"]


def test_stale_evidence_blocks() -> None:
    state = _base_state()
    state["evidence_freshness"] = {"evidence_age_minutes": 120}
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_evidence_freshness" in result["blockers"]


def test_missing_replayability_proof_blocks() -> None:
    state = _base_state()
    state.pop("replayability_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_replayability_proof" in result["blockers"]


def test_missing_final_disarm_proof_blocks() -> None:
    state = _base_state()
    state.pop("final_disarm_proof")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_final_disarm_proof" in result["blockers"]


def test_missing_post_trade_journal_path_blocks() -> None:
    state = _base_state()
    state.pop("post_trade_journal_path")
    result = _run(state, exact_state=True)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_INCOMPLETE
    assert "missing_post_trade_journal_path" in result["blockers"]


def test_retry_loop_detected_blocks() -> None:
    result = _run({"retry_loop_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "retry_loop_detected" in result["blockers"]


def test_autonomous_reentry_detected_blocks() -> None:
    result = _run({"autonomous_reentry_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "autonomous_reentry_detected" in result["blockers"]


def test_unsafe_broker_connection_blocks() -> None:
    result = _run({"unsafe_broker_connection_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "unsafe_broker_connection_detected" in result["blockers"]


def test_unsafe_network_access_blocks() -> None:
    result = _run({"unsafe_network_access_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "unsafe_network_access_detected" in result["blockers"]


def test_unsafe_credential_access_blocks() -> None:
    result = _run({"unsafe_credential_access_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "unsafe_credential_access_detected" in result["blockers"]


def test_unsafe_account_identifier_access_blocks() -> None:
    result = _run({"unsafe_account_identifier_access_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "unsafe_account_identifier_access_detected" in result["blockers"]


def test_unsafe_order_execution_blocks() -> None:
    result = _run({"unsafe_order_execution_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "unsafe_order_execution_detected" in result["blockers"]


def test_unsafe_live_trading_blocks() -> None:
    result = _run({"unsafe_live_trading_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "unsafe_live_trading_detected" in result["blockers"]


def test_unsafe_capital_allocation_blocks() -> None:
    result = _run({"unsafe_capital_allocation_detected": True})
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_BLOCKED
    assert "unsafe_capital_allocation_detected" in result["blockers"]


def test_rejected_demo_state_returns_rejected() -> None:
    state = _base_state()
    state["demo_validation_contract"]["metric_summary"]["validation_expectancy"] = -0.25
    result = _run(state)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_REJECTED


def test_next_safe_action_deterministic() -> None:
    incomplete_state = _base_state()
    incomplete_state["demo_validation_contract"]["demo_validation_contract_status"] = "DEMO_CONTRACT_CONTINUE"
    incomplete = _run(incomplete_state, exact_state=True)
    assert incomplete["next_safe_action"] == "collect_missing_proofs"
    assert incomplete["required_next_packets"] == ["collect_missing_proof_inputs", "refresh_evidence_freshness", "refresh_risk_and_replay_controls"]

    rejected = _run({"demo_validation_contract": {"demo_validation_contract_status": "DEMO_CONTRACT_REJECTED", "metric_summary": {"validation_expectancy": -0.2}}}
    )
    assert rejected["next_safe_action"] == "rework_demo_performance_and_risk"


def test_required_next_packets_ranked() -> None:
    blocked = _run({"unsafe_live_trading_detected": True})
    assert blocked["required_next_packets"] == ["clear_unsafe_conditions", "revalidate_evidence_inputs", "restore_authorization_controls"]


def test_safety_never_authorizes_live_trading() -> None:
    result = _run()
    assert result["safety"]["live_trading_authorized"] is False
    assert result["safety"]["order_execution_enabled"] is False


def test_safety_never_enables_order_execution() -> None:
    state = _run({"unsafe_order_execution_detected": True})
    assert state["safety"]["live_trading_authorized"] is False
    assert state["safety"]["order_execution_enabled"] is False


def test_alias_aware_proof_keys_work() -> None:
    state = _base_state()
    state["risk_limits"] = {"max_loss": 10, "daily_cap": 2, "stop_loss_limit": 1, "order_type_allowed": "market", "max_units": 1}
    state["live_readiness_candidate"] = {"ready": True}
    state["evidence_freshness"] = {"age_minutes": 30}
    state["one_shot_controls"] = {"one_order_only": "yes", "no_retry_loop": "1", "no_autonomous_reentry": "on", "manual_arming_required": "true", "timeout_required": "true", "final_disarm_required": "yes", "operator_review_required": "true"}
    result = _run(state)
    assert result["exception_package_status"] == ONE_SHOT_EXCEPTION_REVIEW_READY
