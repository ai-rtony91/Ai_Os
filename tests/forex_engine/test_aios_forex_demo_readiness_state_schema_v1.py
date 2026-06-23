from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from automation.forex_engine.long_only_demo_readiness_orchestrator_v1 import (
    AUTONOMOUS_BLOCKED_BY_BROKER_GATE,
    AUTONOMOUS_DEMO_READY_PREVIEW_ONLY,
    evaluate_long_only_demo_readiness,
)

SCHEMA_PATH = Path("schemas/aios/forex/AIOS_FOREX_DEMO_READINESS_STATE.v1.schema.json")


def _schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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


def _ready_preview_sample():
    return evaluate_long_only_demo_readiness(
        broker_proof=_valid_broker_proof(),
        candidate_evidence=_valid_evidence(),
        risk_policy=_valid_policy(),
        order_intent=_valid_intent(),
    )


def _blocked_broker_sample():
    return evaluate_long_only_demo_readiness()


def _validate(instance, schema):
    required = schema["required"]
    for field in required:
        if field not in instance:
            return False
    if schema.get("additionalProperties") is False:
        if set(instance) - set(schema["properties"]):
            return False
    status_schema = schema["properties"]["status"]
    if instance["status"] not in status_schema["enum"]:
        return False
    for field, field_schema in schema["properties"].items():
        if "const" in field_schema and instance.get(field) != field_schema["const"]:
            return False
    for field in ("blockers", "warnings"):
        if not isinstance(instance.get(field), list):
            return False
    return True


def test_schema_file_exists():
    assert SCHEMA_PATH.exists()


def test_schema_is_valid_json():
    assert _schema()["title"] == "AIOS Forex Demo Readiness State V1"


def test_orchestrator_ready_preview_only_sample_satisfies_schema():
    sample = _ready_preview_sample()
    assert sample["status"] == AUTONOMOUS_DEMO_READY_PREVIEW_ONLY
    assert _validate(sample, _schema())


def test_blocked_broker_gate_sample_satisfies_schema():
    sample = _blocked_broker_sample()
    assert sample["status"] == AUTONOMOUS_BLOCKED_BY_BROKER_GATE
    assert _validate(sample, _schema())


def test_schema_rejects_execution_allowed_true():
    sample = _ready_preview_sample()
    sample["execution_allowed"] = True
    assert _validate(sample, _schema()) is False


def test_schema_rejects_ready_to_execute_true():
    sample = _ready_preview_sample()
    sample["ready_to_execute"] = True
    assert _validate(sample, _schema()) is False


def test_schema_rejects_demo_order_allowed_true():
    sample = _ready_preview_sample()
    sample["demo_order_allowed"] = True
    assert _validate(sample, _schema()) is False


def test_schema_rejects_live_autonomy_allowed_true():
    sample = _ready_preview_sample()
    sample["live_autonomy_allowed"] = True
    assert _validate(sample, _schema()) is False


def test_schema_rejects_short_side_enabled_true():
    sample = _ready_preview_sample()
    sample["short_side_enabled"] = True
    assert _validate(sample, _schema()) is False


def test_schema_rejects_broker_mutation_allowed_true():
    sample = _ready_preview_sample()
    sample["broker_mutation_allowed"] = True
    assert _validate(sample, _schema()) is False


def test_schema_rejects_order_execution_allowed_true():
    sample = _ready_preview_sample()
    sample["order_execution_allowed"] = True
    assert _validate(sample, _schema()) is False


def test_schema_rejects_unknown_final_status():
    sample = _ready_preview_sample()
    sample["status"] = "PROFITABLE_LIVE_BOT_READY"
    assert _validate(sample, _schema()) is False
