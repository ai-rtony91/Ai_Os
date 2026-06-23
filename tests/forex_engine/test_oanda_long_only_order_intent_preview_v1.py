from __future__ import annotations

import json

from automation.forex_engine import oanda_long_only_order_intent_preview_v1 as preview


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


def _blocked(intent):
    result = preview.build_oanda_long_only_order_intent_preview(intent)
    assert result["status"] == preview.ORDER_INTENT_PREVIEW_BLOCKED
    return result


def test_missing_intent_blocks():
    assert "missing_order_intent" in _blocked(None)["blockers"]


def test_wrong_broker_blocks():
    intent = _valid_intent()
    intent["broker_name"] = "other"
    assert "broker_name_not_oanda" in _blocked(intent)["blockers"]


def test_live_environment_blocks():
    intent = _valid_intent()
    intent["broker_environment"] = "live"
    assert "broker_environment_not_demo_sandbox_or_practice" in _blocked(intent)["blockers"]


def test_wrong_mode_blocks():
    intent = _valid_intent()
    intent["mode"] = "LIVE"
    assert "mode_not_demo_sandbox_or_preparation_only" in _blocked(intent)["blockers"]


def test_short_direction_blocks():
    intent = _valid_intent()
    intent["direction"] = "SHORT"
    assert "direction_not_long" in _blocked(intent)["blockers"]


def test_sell_side_blocks():
    intent = _valid_intent()
    intent["order_side"] = "SELL"
    assert "order_side_not_buy" in _blocked(intent)["blockers"]


def test_zero_units_blocks():
    intent = _valid_intent()
    intent["units"] = 0
    assert "invalid_units" in _blocked(intent)["blockers"]


def test_units_above_max_blocks():
    intent = _valid_intent()
    intent["units"] = 1001
    assert "units_exceed_max_units" in _blocked(intent)["blockers"]


def test_missing_stop_loss_blocks():
    intent = _valid_intent()
    intent["stop_loss_defined"] = False
    assert "stop_loss_defined_not_confirmed" in _blocked(intent)["blockers"]


def test_missing_take_profit_blocks():
    intent = _valid_intent()
    intent["take_profit_defined"] = False
    assert "take_profit_defined_not_confirmed" in _blocked(intent)["blockers"]


def test_one_order_only_false_blocks():
    intent = _valid_intent()
    intent["one_order_only"] = False
    assert "one_order_only_not_confirmed" in _blocked(intent)["blockers"]


def test_broker_proof_ready_false_blocks():
    intent = _valid_intent()
    intent["broker_proof_ready"] = False
    assert "broker_proof_ready_not_confirmed" in _blocked(intent)["blockers"]


def test_evidence_depth_ready_false_blocks():
    intent = _valid_intent()
    intent["evidence_depth_ready"] = False
    assert "evidence_depth_ready_not_confirmed" in _blocked(intent)["blockers"]


def test_risk_policy_ready_false_blocks():
    intent = _valid_intent()
    intent["risk_policy_ready"] = False
    assert "risk_policy_ready_not_confirmed" in _blocked(intent)["blockers"]


def test_credential_flag_false_blocks():
    intent = _valid_intent()
    intent["no_credentials_in_payload"] = False
    assert "no_credentials_in_payload_not_confirmed" in _blocked(intent)["blockers"]


def test_account_flag_false_blocks():
    intent = _valid_intent()
    intent["no_account_id_in_payload"] = False
    assert "no_account_id_in_payload_not_confirmed" in _blocked(intent)["blockers"]


def test_env_flag_false_blocks():
    intent = _valid_intent()
    intent["no_env_in_payload"] = False
    assert "no_env_in_payload_not_confirmed" in _blocked(intent)["blockers"]


def test_network_flag_false_blocks():
    intent = _valid_intent()
    intent["no_network_call"] = False
    assert "no_network_call_not_confirmed" in _blocked(intent)["blockers"]


def test_broker_mutation_flag_false_blocks():
    intent = _valid_intent()
    intent["no_broker_mutation"] = False
    assert "no_broker_mutation_not_confirmed" in _blocked(intent)["blockers"]


def test_order_execution_flag_false_blocks():
    intent = _valid_intent()
    intent["no_order_execution"] = False
    assert "no_order_execution_not_confirmed" in _blocked(intent)["blockers"]


def test_sensitive_material_blocks():
    intent = _valid_intent()
    intent["token"] = "redacted"
    assert "sensitive_material_detected" in _blocked(intent)["blockers"]


def test_valid_preview_returns_ready():
    result = preview.build_oanda_long_only_order_intent_preview(_valid_intent())
    assert result["status"] == preview.ORDER_INTENT_PREVIEW_READY
    assert result["preview_ready"] is True


def test_valid_preview_contains_no_endpoint():
    result = preview.build_oanda_long_only_order_intent_preview(_valid_intent())
    encoded = json.dumps(result["non_executable_preview"]).lower()
    assert "endpoint" not in encoded
    assert "url" not in encoded
    assert "api" not in encoded
    assert "request" not in encoded


def test_valid_preview_contains_no_account_id():
    result = preview.build_oanda_long_only_order_intent_preview(_valid_intent())
    encoded = json.dumps(result["non_executable_preview"]).lower()
    assert "account_id" not in encoded
    assert "accountid" not in encoded


def test_valid_preview_contains_no_authorization_field():
    result = preview.build_oanda_long_only_order_intent_preview(_valid_intent())
    encoded = json.dumps(result["non_executable_preview"]).lower()
    assert "authorization" not in encoded
    assert "token" not in encoded


def test_valid_preview_keeps_execution_allowed_false():
    result = preview.build_oanda_long_only_order_intent_preview(_valid_intent())
    assert result["execution_allowed"] is False
    assert result["ready_to_execute"] is False


def test_valid_preview_keeps_demo_order_allowed_false():
    result = preview.build_oanda_long_only_order_intent_preview(_valid_intent())
    assert result["demo_order_allowed"] is False


def test_valid_preview_keeps_live_autonomy_allowed_false():
    result = preview.build_oanda_long_only_order_intent_preview(_valid_intent())
    assert result["live_autonomy_allowed"] is False
    assert result["broker_mutation_allowed"] is False
    assert result["order_execution_allowed"] is False
