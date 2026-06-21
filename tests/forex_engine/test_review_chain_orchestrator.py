from __future__ import annotations

from copy import deepcopy

from automation.forex_engine.review_chain_orchestrator import (
    DEMO_CONTRACT_COMPLETE,
    DEMO_CONTRACT_REJECTED,
    LIVE_REVIEW_CERTIFICATE_REJECTED,
    LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
    ONE_SHOT_EXCEPTION_REJECTED,
    ONE_SHOT_EXCEPTION_REVIEW_READY,
    REVIEW_CHAIN_BLOCKED,
    REVIEW_CHAIN_INCOMPLETE,
    REVIEW_CHAIN_REJECTED,
    REVIEW_CHAIN_REVIEW_READY,
    orchestrate_forex_review_chain,
)


def _base_state() -> dict:
    return {
        "demo_validation_contract": {
            "demo_validation_contract_status": DEMO_CONTRACT_COMPLETE,
            "demo_validation_contract_completed": True,
            "live_readiness_candidate": True,
        },
        "one_shot_exception_package": {
            "exception_package_status": ONE_SHOT_EXCEPTION_REVIEW_READY,
            "exception_package_completed": True,
            "live_micro_trade_review_ready": True,
        },
        "live_review_readiness_certificate": {
            "certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
            "certificate_completed": True,
            "human_live_review_ready": True,
            "live_micro_trade_review_ready": True,
        },
        "live_readiness_candidate": True,
        "human_live_review_ready": True,
        "one_shot_controls": {
            "one_shot_only": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
            "manual_arming_required": True,
        },
    }


def _run(state_overrides: dict | None = None, *, exact_state: bool = True) -> dict:
    state = _base_state()
    if state_overrides is not None:
        if exact_state:
            return orchestrate_forex_review_chain(state_overrides)
        for key, value in state_overrides.items():
            if isinstance(value, dict) and isinstance(state.get(key), dict):
                merged = deepcopy(state[key])
                merged.update(value)
                state[key] = merged
            else:
                state[key] = value
        return orchestrate_forex_review_chain(state)
    return orchestrate_forex_review_chain(state)


def test_empty_state_blocks() -> None:
    result = _run({}, exact_state=True)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "missing_demo_validation_contract" in result["blockers"]


def test_complete_chain_returns_review_ready() -> None:
    result = _run()
    assert result["review_chain_status"] == REVIEW_CHAIN_REVIEW_READY
    assert result["human_live_review_ready"] is True
    assert result["live_micro_trade_review_ready"] is True
    assert result["review_chain_completed"] is True


def test_missing_demo_contract_blocks() -> None:
    state = _base_state()
    state.pop("demo_validation_contract")
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "missing_demo_validation_contract" in result["blockers"]


def test_incomplete_demo_contract_blocks() -> None:
    state = _base_state()
    state["demo_validation_contract"]["demo_validation_contract_status"] = "DEMO_CONTRACT_CONTINUE"
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "demo_validation_contract_not_complete" in result["blockers"]


def test_rejected_demo_contract_rejected() -> None:
    state = _base_state()
    state["demo_validation_contract"]["demo_validation_contract_status"] = DEMO_CONTRACT_REJECTED
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_REJECTED
    assert "demo_validation_contract_rejected" in result["blockers"]


def test_missing_one_shot_package_blocks() -> None:
    state = _base_state()
    state.pop("one_shot_exception_package")
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "missing_one_shot_exception_package" in result["blockers"]


def test_incomplete_one_shot_package_blocks() -> None:
    state = _base_state()
    state["one_shot_exception_package"]["exception_package_status"] = "ONE_SHOT_EXCEPTION_INCOMPLETE"
    state["one_shot_exception_package"]["live_micro_trade_review_ready"] = False
    state["one_shot_exception_package"]["exception_package_completed"] = False
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "one_shot_exception_package_not_review_ready" in result["blockers"]


def test_rejected_one_shot_package_rejected() -> None:
    state = _base_state()
    state["one_shot_exception_package"]["exception_package_status"] = ONE_SHOT_EXCEPTION_REJECTED
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_REJECTED
    assert "one_shot_exception_package_rejected" in result["blockers"]


def test_missing_certificate_blocks() -> None:
    state = _base_state()
    state.pop("live_review_readiness_certificate")
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "missing_live_review_readiness_certificate" in result["blockers"]


def test_incomplete_certificate_blocks() -> None:
    state = _base_state()
    state["live_review_readiness_certificate"]["certificate_status"] = "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"
    state["live_review_readiness_certificate"]["human_live_review_ready"] = False
    state["live_review_readiness_certificate"]["certificate_completed"] = False
    state["live_review_readiness_certificate"]["live_micro_trade_review_ready"] = False
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "live_review_certificate_not_review_ready" in result["blockers"]


def test_rejected_certificate_rejected() -> None:
    state = _base_state()
    state["live_review_readiness_certificate"]["certificate_status"] = LIVE_REVIEW_CERTIFICATE_REJECTED
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_REJECTED
    assert "live_review_certificate_rejected" in result["blockers"]


def test_missing_candidate_readiness_blocks() -> None:
    state = _base_state()
    state["live_readiness_candidate"] = False
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "missing_live_readiness_candidate" in result["blockers"]


def test_missing_human_review_readiness_blocks() -> None:
    state = _base_state()
    state["human_live_review_ready"] = False
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "missing_human_review_ready" in result["blockers"]


def test_cross_stage_conflict_blocks() -> None:
    state = _base_state()
    state["one_shot_exception_package"]["exception_package_status"] = "ONE_SHOT_EXCEPTION_INCOMPLETE"
    state["live_review_readiness_certificate"]["certificate_status"] = LIVE_REVIEW_CERTIFICATE_REVIEW_READY
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "cross_stage_status_conflict" in result["blockers"]


def test_review_ready_without_demo_completion_blocks() -> None:
    state = _base_state()
    state["demo_validation_contract"]["demo_validation_contract_status"] = "DEMO_CONTRACT_CONTINUE"
    state["human_live_review_ready"] = True
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "review_ready_without_demo_completion" in result["blockers"]


def test_review_ready_without_exception_package_blocks() -> None:
    state = _base_state()
    state["one_shot_exception_package"]["exception_package_status"] = "ONE_SHOT_EXCEPTION_INCOMPLETE"
    state["one_shot_exception_package"]["exception_package_completed"] = False
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "review_ready_without_exception_package" in result["blockers"]


def test_review_ready_without_certificate_blocks() -> None:
    state = _base_state()
    state["live_review_readiness_certificate"]["certificate_status"] = "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"
    state["live_review_readiness_certificate"]["certificate_completed"] = False
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_INCOMPLETE
    assert "review_ready_without_certificate" in result["blockers"]


def test_live_trading_authorization_flag_blocks() -> None:
    result = _run({"live_trading_authorization_detected": True})
    assert result["review_chain_status"] == REVIEW_CHAIN_BLOCKED
    assert "live_trading_authorization_detected" in result["blockers"]


def test_execution_authority_flag_blocks() -> None:
    result = _run({"execution_authority_detected": True})
    assert result["review_chain_status"] == REVIEW_CHAIN_BLOCKED
    assert "execution_authority_detected" in result["blockers"]


def test_broker_connection_flag_blocks() -> None:
    result = _run({"unsafe_broker_connection_detected": True})
    assert result["review_chain_status"] == REVIEW_CHAIN_BLOCKED
    assert "broker_connection_active" in result["blockers"]


def test_credential_access_flag_blocks() -> None:
    result = _run({"unsafe_credential_access_detected": True})
    assert result["review_chain_status"] == REVIEW_CHAIN_BLOCKED
    assert "credential_access_detected" in result["blockers"]


def test_account_identifier_flag_blocks() -> None:
    result = _run({"unsafe_account_identifier_access_detected": True})
    assert result["review_chain_status"] == REVIEW_CHAIN_BLOCKED
    assert "account_identifier_access_detected" in result["blockers"]


def test_network_access_flag_blocks() -> None:
    result = _run({"unsafe_network_access_detected": True})
    assert result["review_chain_status"] == REVIEW_CHAIN_BLOCKED
    assert "network_access_detected" in result["blockers"]


def test_capital_allocation_flag_blocks() -> None:
    result = _run({"unsafe_capital_allocation_detected": True})
    assert result["review_chain_status"] == REVIEW_CHAIN_BLOCKED
    assert "capital_allocation_detected" in result["blockers"]


def test_alias_aware_demo_contract_inputs() -> None:
    state = {
        "demo_contract": {
            "demo_contract_status": DEMO_CONTRACT_COMPLETE,
            "demo_contract_completed": True,
            "candidate_ready": True,
        },
        "exception_package": {
            "one_shot_status": ONE_SHOT_EXCEPTION_REVIEW_READY,
            "exception_package_completed": True,
            "review_ready": True,
        },
        "certificate": {
            "certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
            "certificate_completed": True,
            "human_review_ready": True,
            "live_micro_trade_review_ready": True,
            "review_ready": True,
        },
        "candidate_ready": True,
        "human_review_ready": True,
        "one_shot_controls": {
            "one_shot_only": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
            "manual_arming_required": True,
        },
    }
    result = _run(state, exact_state=True)
    assert result["review_chain_status"] == REVIEW_CHAIN_REVIEW_READY


def test_alias_aware_exception_package_inputs() -> None:
    state = _base_state()
    state.pop("one_shot_exception_package")
    state["exception_package"] = {
        "one_shot_status": ONE_SHOT_EXCEPTION_REVIEW_READY,
        "exception_package_completed": True,
        "review_ready": True,
    }
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_REVIEW_READY


def test_alias_aware_certificate_inputs() -> None:
    state = _base_state()
    state.pop("live_review_readiness_certificate")
    state["readiness_certificate"] = {
        "certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
        "certificate_completed": True,
        "human_live_review_ready": True,
        "live_micro_trade_review_ready": True,
    }
    result = _run(state)
    assert result["review_chain_status"] == REVIEW_CHAIN_REVIEW_READY


def test_next_safe_action_deterministic() -> None:
    first = _run()
    second = _run()
    assert first["next_safe_action"] == second["next_safe_action"]


def test_required_next_packets_deterministic() -> None:
    first = _run()
    second = _run()
    assert first["required_next_packets"] == second["required_next_packets"]


def test_review_chain_never_authorizes_live_trading() -> None:
    result = _run()
    assert result["live_trading_authorized"] is False
    assert result["safety"]["live_trading_authorized"] is False


def test_review_chain_never_grants_execution_authority() -> None:
    result = _run()
    assert result["safety"]["execution_authority_granted"] is False


def test_safety_invariants_preserved() -> None:
    result = _run()
    safety = result["safety"]
    assert safety["broker_connection_active"] is False
    assert safety["network_access"] is False
    assert safety["credentials_accessed"] is False
    assert safety["account_identifiers_accessed"] is False
    assert safety["order_execution_enabled"] is False
    assert safety["capital_allocated"] is False
    assert safety["operator_review_required"] is True


def test_blocker_deduplication_works() -> None:
    state = {
        "unsafe_broker_connection_detected": True,
        "broker_connection_active": True,
        "live_trading_authorization_detected": True,
        "unsafe_live_trading_detected": True,
    }
    result = _run(state, exact_state=True)
    assert len(result["blockers"]) == len(set(result["blockers"]))


def test_review_chain_only_true() -> None:
    result = _run()
    assert result["safety"]["review_chain_only"] is True


def test_operator_review_required_true() -> None:
    result = _run()
    assert result["safety"]["operator_review_required"] is True
