from __future__ import annotations

from datetime import datetime, timezone
import json

from automation.forex_engine import long_only_demo_readiness_orchestrator_v1 as orchestrator


def _valid_broker_proof():
    return {
        "broker_name": "OANDA",
        "broker_environment": "practice",
        "asset_class": "forex",
        "account_type": "practice_margin",
        "account_currency": "USD",
        "margin_available_confirmed": True,
        "effective_leverage_limit": 2.0,
        "long_permission": True,
        "short_permission": False,
        "fifo_required": True,
        "hedging_available": False,
        "instrument_tradable": True,
        "instrument": "EUR_USD",
        "max_units": 1000,
        "stop_loss_supported": True,
        "take_profit_supported": True,
        "order_type_supported": ["market"],
        "one_order_only_supported": True,
        "demo_sandbox_order_preview_supported": True,
        "broker_house_restrictions": [],
        "proof_timestamp": datetime.now(timezone.utc).isoformat(),
        "proof_source": "anthony_sanitized_oanda_practice_permission_proof",
        "sanitized_evidence_only": True,
        "no_credentials_in_payload": True,
        "no_account_id_in_payload": True,
        "no_env_in_payload": True,
        "no_network_call": True,
        "no_broker_mutation": True,
        "no_order_execution": True,
    }


def _valid_evidence():
    return {
        "candidate_id": "c1-eur-buy",
        "strategy_id": "long-only-eur-usd-v1",
        "instrument": "EUR_USD",
        "direction": "LONG",
        "evidence_source": "deterministic_paper_demo_review",
        "evidence_timestamp": "2026-06-23T00:00:00+00:00",
        "sample_size": 30,
        "closed_trades": 30,
        "winning_trades": 19,
        "losing_trades": 9,
        "breakeven_trades": 2,
        "expectancy": 0.18,
        "profit_factor": 1.35,
        "max_drawdown": 0.04,
        "max_drawdown_allowed": 0.08,
        "walk_forward_folds": 4,
        "out_of_sample_folds": 3,
        "out_of_sample_folds_passed": 3,
        "min_required_trades": 30,
        "min_required_walk_forward_folds": 3,
        "min_required_out_of_sample_folds": 3,
        "min_expectancy": 0.0,
        "min_profit_factor": 1.2,
        "negative_expectancy": False,
        "mitigation_worsened": False,
        "overfit_flag": False,
        "risk_gate_cleared": True,
        "evidence_gate_cleared": True,
        "long_only": True,
        "short_side_disabled": True,
        "sanitized_evidence_only": True,
    }


def _valid_policy():
    return {
        "policy_name": "aios_long_only_demo_preparation_policy",
        "policy_version": "1",
        "mode": "DEMO_SANDBOX_ONLY",
        "long_only": True,
        "short_side_disabled": True,
        "instrument": "EUR_USD",
        "max_units_policy": 1000,
        "broker_max_units": 1000,
        "final_max_units": 1000,
        "stop_loss_required": True,
        "take_profit_required": True,
        "one_order_only": True,
        "kill_switch_required": True,
        "daily_loss_limit_required": True,
        "max_drawdown_limit_required": True,
        "manual_owner_approval_required_for_demo_order": True,
        "live_exception_required_for_live_order": True,
        "broker_proof_ready": True,
        "evidence_depth_ready": True,
        "no_credentials_required": True,
        "no_account_id_required": True,
        "no_network_required": True,
        "no_order_execution": True,
        "sanitized_policy_only": True,
    }


def _valid_intent():
    return {
        "candidate_id": "c1-eur-buy",
        "strategy_id": "long-only-eur-usd-v1",
        "broker_name": "OANDA",
        "broker_environment": "practice",
        "mode": "DEMO_SANDBOX_ONLY",
        "instrument": "EUR_USD",
        "direction": "LONG",
        "units": 1000,
        "max_units": 1000,
        "order_side": "BUY",
        "order_type": "market",
        "stop_loss_required": True,
        "stop_loss_defined": True,
        "take_profit_required": True,
        "take_profit_defined": True,
        "one_order_only": True,
        "broker_proof_ready": True,
        "evidence_depth_ready": True,
        "risk_policy_ready": True,
        "owner_demo_order_approval_present": False,
        "owner_live_exception_present": False,
        "no_credentials_in_payload": True,
        "no_account_id_in_payload": True,
        "no_env_in_payload": True,
        "no_network_call": True,
        "no_broker_mutation": True,
        "no_order_execution": True,
        "sanitized_intent_only": True,
    }


def _evaluate(**overrides):
    payload = {
        "broker_proof": _valid_broker_proof(),
        "candidate_evidence": _valid_evidence(),
        "risk_policy": _valid_policy(),
        "order_intent": _valid_intent(),
        "supervisor_state": {"status": "AUTONOMOUS_BLOCKED_BY_BROKER_GATE"},
    }
    payload.update(overrides)
    return orchestrator.evaluate_long_only_demo_readiness(**payload)


def test_missing_all_inputs_blocks_by_broker_gate():
    result = orchestrator.evaluate_long_only_demo_readiness()
    assert result["status"] == orchestrator.AUTONOMOUS_BLOCKED_BY_BROKER_GATE
    assert result["execution_allowed"] is False


def test_blocked_broker_proof_produces_broker_gate_status():
    proof = _valid_broker_proof()
    proof["broker_environment"] = "live"
    result = _evaluate(broker_proof=proof)
    assert result["status"] == orchestrator.AUTONOMOUS_BLOCKED_BY_BROKER_GATE


def test_ready_broker_proof_but_blocked_evidence_produces_evidence_depth_status():
    evidence = _valid_evidence()
    evidence["sample_size"] = 29
    result = _evaluate(candidate_evidence=evidence)
    assert result["status"] == orchestrator.AUTONOMOUS_BLOCKED_BY_EVIDENCE_DEPTH


def test_ready_broker_evidence_but_blocked_risk_produces_risk_status():
    policy = _valid_policy()
    policy["kill_switch_required"] = False
    result = _evaluate(risk_policy=policy)
    assert result["status"] == orchestrator.AUTONOMOUS_BLOCKED_BY_RISK


def test_ready_broker_evidence_risk_and_missing_preview_produces_preparation_ready():
    result = _evaluate(order_intent=None)
    assert result["status"] == orchestrator.AUTONOMOUS_DEMO_PREPARATION_READY
    assert result["demo_preparation_ready"] is True
    assert result["demo_preview_ready"] is False


def test_ready_broker_evidence_risk_preview_produces_preview_only_ready():
    result = _evaluate()
    assert result["status"] == orchestrator.AUTONOMOUS_DEMO_READY_PREVIEW_ONLY
    assert result["demo_preparation_ready"] is True
    assert result["demo_preview_ready"] is True


def test_integrated_supervisor_remains_prepare_only():
    result = _evaluate(supervisor_state={"status": "AUTONOMOUS_BLOCKED_BY_POLICY"})
    assert result["supervisor_status"] == "AUTONOMOUS_BLOCKED_BY_POLICY"
    assert result["status"] == orchestrator.AUTONOMOUS_DEMO_READY_PREVIEW_ONLY


def test_integrated_result_keeps_execution_allowed_false():
    assert _evaluate()["execution_allowed"] is False


def test_integrated_result_keeps_ready_to_execute_false():
    assert _evaluate()["ready_to_execute"] is False


def test_integrated_result_keeps_demo_order_allowed_false():
    assert _evaluate()["demo_order_allowed"] is False


def test_integrated_result_keeps_live_autonomy_allowed_false():
    assert _evaluate()["live_autonomy_allowed"] is False


def test_integrated_result_keeps_short_side_enabled_false():
    assert _evaluate()["short_side_enabled"] is False


def test_integrated_result_blocks_sensitive_material():
    proof = _valid_broker_proof()
    proof["token"] = "redacted"
    result = _evaluate(broker_proof=proof)
    assert result["status"] == orchestrator.AUTONOMOUS_BLOCKED_BY_BROKER_GATE
    assert "sensitive_material_detected" in result["blockers"]


def test_integrated_result_is_json_serializable():
    json.dumps(_evaluate(), sort_keys=True)
