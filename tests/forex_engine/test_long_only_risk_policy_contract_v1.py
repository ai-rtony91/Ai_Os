from __future__ import annotations

from automation.forex_engine import long_only_risk_policy_contract_v1 as risk


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


def _blocked(policy):
    result = risk.evaluate_long_only_risk_policy_contract(policy)
    assert result["status"] == risk.RISK_POLICY_CONTRACT_BLOCKED
    return result


def test_missing_policy_blocks():
    assert "missing_risk_policy_contract" in _blocked(None)["blockers"]


def test_wrong_mode_blocks():
    policy = _valid_policy()
    policy["mode"] = "LIVE"
    assert "mode_not_demo_sandbox_or_preparation_only" in _blocked(policy)["blockers"]


def test_long_only_false_blocks():
    policy = _valid_policy()
    policy["long_only"] = False
    assert "long_only_not_confirmed" in _blocked(policy)["blockers"]


def test_short_side_disabled_false_blocks():
    policy = _valid_policy()
    policy["short_side_disabled"] = False
    assert "short_side_disabled_not_confirmed" in _blocked(policy)["blockers"]


def test_stop_loss_required_false_blocks():
    policy = _valid_policy()
    policy["stop_loss_required"] = False
    assert "stop_loss_required_not_confirmed" in _blocked(policy)["blockers"]


def test_take_profit_required_false_blocks():
    policy = _valid_policy()
    policy["take_profit_required"] = False
    assert "take_profit_required_not_confirmed" in _blocked(policy)["blockers"]


def test_one_order_only_false_blocks():
    policy = _valid_policy()
    policy["one_order_only"] = False
    assert "one_order_only_not_confirmed" in _blocked(policy)["blockers"]


def test_kill_switch_required_false_blocks():
    policy = _valid_policy()
    policy["kill_switch_required"] = False
    assert "kill_switch_required_not_confirmed" in _blocked(policy)["blockers"]


def test_daily_loss_limit_required_false_blocks():
    policy = _valid_policy()
    policy["daily_loss_limit_required"] = False
    assert "daily_loss_limit_required_not_confirmed" in _blocked(policy)["blockers"]


def test_max_drawdown_limit_required_false_blocks():
    policy = _valid_policy()
    policy["max_drawdown_limit_required"] = False
    assert "max_drawdown_limit_required_not_confirmed" in _blocked(policy)["blockers"]


def test_manual_owner_demo_approval_requirement_missing_blocks():
    policy = _valid_policy()
    policy["manual_owner_approval_required_for_demo_order"] = False
    assert "manual_owner_approval_required_for_demo_order_not_confirmed" in _blocked(policy)["blockers"]


def test_live_exception_requirement_missing_blocks():
    policy = _valid_policy()
    policy["live_exception_required_for_live_order"] = False
    assert "live_exception_required_for_live_order_not_confirmed" in _blocked(policy)["blockers"]


def test_broker_proof_ready_false_blocks():
    policy = _valid_policy()
    policy["broker_proof_ready"] = False
    assert "broker_proof_ready_not_confirmed" in _blocked(policy)["blockers"]


def test_evidence_depth_ready_false_blocks():
    policy = _valid_policy()
    policy["evidence_depth_ready"] = False
    assert "evidence_depth_ready_not_confirmed" in _blocked(policy)["blockers"]


def test_final_max_units_exceeds_policy_blocks():
    policy = _valid_policy()
    policy["final_max_units"] = 1001
    assert "final_max_units_exceeds_policy" in _blocked(policy)["blockers"]


def test_final_max_units_exceeds_broker_max_blocks():
    policy = _valid_policy()
    policy["broker_max_units"] = 999
    assert "final_max_units_exceeds_broker_max" in _blocked(policy)["blockers"]


def test_sensitive_material_blocks():
    policy = _valid_policy()
    policy["authorization"] = "Bearer redacted"
    assert "sensitive_material_detected" in _blocked(policy)["blockers"]


def test_valid_policy_returns_ready():
    result = risk.evaluate_long_only_risk_policy_contract(_valid_policy())
    assert result["status"] == risk.RISK_POLICY_CONTRACT_READY
    assert result["ready"] is True
    assert result["risk_policy_ready_for_demo_preparation"] is True


def test_valid_policy_keeps_execution_allowed_false():
    result = risk.evaluate_long_only_risk_policy_contract(_valid_policy())
    assert result["execution_allowed"] is False
    assert result["ready_to_execute"] is False
    assert result["demo_order_allowed"] is False
    assert result["live_autonomy_allowed"] is False
