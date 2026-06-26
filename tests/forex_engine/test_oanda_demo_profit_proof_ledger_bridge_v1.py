from __future__ import annotations

import json

from automation.forex_engine import oanda_demo_profit_proof_ledger_bridge_v1 as b


PROTECTED_FLAGS = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)


def _json(input_obj=None):
    result = b.build_oanda_demo_profit_proof_ledger_bridge(
        input_obj or b.build_sample_profit_bridge_input()
    )
    return b.oanda_demo_profit_proof_ledger_bridge_to_jsonable_dict(result)


def test_bridge_ready_for_profit():
    data = _json(b.build_sample_profit_bridge_input())
    assert data["classification"] == "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING"
    assert data["proof_routing_allowed"] is True


def test_bridge_ready_for_loss():
    data = _json(b.build_sample_loss_bridge_input())
    assert data["classification"] == "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING"
    assert data["bridge_review_allowed"] is True
    assert data["proof_routing_allowed"] is False


def test_bridge_ready_for_breakeven():
    data = _json(b.build_sample_breakeven_bridge_input())
    assert data["classification"] == "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING"
    assert data["bridge_review_allowed"] is True


def test_bridge_blocked_incomplete():
    data = _json(b.build_sample_incomplete_bridge_input())
    assert data["classification"] == "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_RESULT_INCOMPLETE"
    assert data["bridge_review_allowed"] is False


def test_bridge_blocked_unsafe():
    data = _json(b.build_sample_unsafe_bridge_input())
    assert data["classification"] == "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_UNSAFE"
    assert data["bridge_review_allowed"] is False


def test_bridge_includes_profit_proof_ledger_target():
    assert "Profit Proof Ledger" in _json()["routing_targets"]


def test_bridge_includes_strategy_proof_engine_target():
    assert "Strategy Proof Engine" in _json()["routing_targets"]


def test_bridge_includes_expectancy_strength_router_target():
    assert "Expectancy Strength Router" in _json()["routing_targets"]


def test_bridge_includes_demo_review_engine_target():
    assert "Demo Review Engine" in _json()["routing_targets"]


def test_bridge_includes_strategy_promotion_router_target():
    assert "Strategy Promotion Router" in _json()["routing_targets"]


def test_bridge_includes_real_evidence_depth_engine_target():
    assert "Real Evidence Depth Engine" in _json()["routing_targets"]


def test_bridge_includes_result_bucket_target():
    assert "Result To Bucket And Next Allocation" in _json()["routing_targets"]


def test_bridge_includes_loss_gate_for_loss():
    assert "Loss To Next Profit Candidate Gate" in _json(
        b.build_sample_loss_bridge_input()
    )["routing_targets"]


def test_bridge_profit_bucket_recommendation_correct():
    assert _json()["bucket_recommendation"] == "PROFIT_SAMPLE_ACCEPTED_FOR_REVIEW"


def test_bridge_loss_bucket_recommendation_correct():
    assert _json(b.build_sample_loss_bridge_input())["bucket_recommendation"] == (
        "LOSS_SAMPLE_ACCEPTED_FOR_REVIEW"
    )


def test_bridge_breakeven_bucket_recommendation_correct():
    assert _json(b.build_sample_breakeven_bridge_input())["bucket_recommendation"] == (
        "BREAKEVEN_SAMPLE_ACCEPTED_FOR_REVIEW"
    )


def test_bridge_ledger_entry_preview_present():
    data = _json()["ledger_entry_preview"]
    assert data["preview_only"] is True
    assert data["planned_risk"] == "2.00"


def test_bridge_expectancy_sample_preview_present():
    data = _json()["expectancy_sample_preview"]
    assert data["preview_only"] is True
    assert data["can_claim_repeated_expectancy"] is False


def test_bridge_evidence_depth_preview_present():
    data = _json()["evidence_depth_preview"]
    assert data["preview_only"] is True
    assert data["evidence_type"] == "sanitized_read_only_pl_result"


def test_bridge_next_allocation_hint_present():
    assert _json()["next_allocation_hint"] == (
        "add to repeated expectancy sample before any live review"
    )


def test_bridge_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_bridge_markdown_title():
    result = b.build_oanda_demo_profit_proof_ledger_bridge(
        b.build_sample_profit_bridge_input()
    )
    assert b.oanda_demo_profit_proof_ledger_bridge_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo Profit Proof Ledger Bridge V1"
    )


def test_bridge_operator_text_plain():
    result = b.build_oanda_demo_profit_proof_ledger_bridge(
        b.build_sample_profit_bridge_input()
    )
    text = b.oanda_demo_profit_proof_ledger_bridge_to_operator_text(result)
    assert "Profit proof ledger bridge status:" in text
    assert "No trade placed by this packet." in text


def test_bridge_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_bridge_never_mutates_existing_ledger_file():
    assert _json()["mutates_existing_ledger_file"] is False


def test_bridge_produces_preview_only():
    data = _json()
    assert data["preview_only"] is True
    assert data["ledger_entry_preview"]["preview_only"] is True


def test_unsafe_sample_never_routes():
    data = _json(b.build_sample_unsafe_bridge_input())
    assert data["bridge_review_allowed"] is False
    assert data["proof_routing_allowed"] is False


def test_incomplete_sample_never_routes():
    data = _json(b.build_sample_incomplete_bridge_input())
    assert data["bridge_review_allowed"] is False
    assert data["proof_routing_allowed"] is False


def test_bridge_targets_missing_classification():
    sample = b.build_sample_profit_bridge_input()
    data = _json(
        b.OandaDemoProfitProofLedgerBridgeInput(
            intake_result=sample.intake_result,
            quality_result=sample.quality_result,
            routing_targets_present=False,
        )
    )
    assert data["classification"] == (
        "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_ROUTING_TARGETS_MISSING"
    )
    assert data["routing_targets"] == []


def test_bridge_result_bucket_profit():
    assert _json()["result_bucket"] == "PROFIT"


def test_bridge_result_bucket_loss():
    assert _json(b.build_sample_loss_bridge_input())["result_bucket"] == "LOSS"


def test_bridge_result_bucket_breakeven():
    assert _json(b.build_sample_breakeven_bridge_input())["result_bucket"] == "BREAKEVEN"


def test_bridge_realized_pl_present():
    assert _json()["realized_pl"] == "1.20"


def test_bridge_realized_r_multiple_present():
    assert _json()["realized_r_multiple"] == "0.6000"


def test_bridge_strategy_candidate_instrument_direction_present():
    data = _json()
    assert data["strategy_id"] == "strategy_supertrend_review_ready_v1"
    assert data["candidate_id"] == "candidate_oanda_demo_pl_001"
    assert data["instrument"] == "EUR_USD"
    assert data["direction"] == "BUY"


def test_bridge_owner_warning_present():
    assert _json()["owner_warning"] == "Do not execute unless Anthony explicitly approves."


def test_bridge_read_only_warning_present():
    assert _json()["read_only_warning"] == (
        "Read-only P/L evidence intake only. Codex is not authorized to execute, "
        "call a broker, access credentials, or place orders."
    )


def test_bridge_no_raw_account_data_output():
    assert "RAW_ACCOUNT" not in json.dumps(_json(), sort_keys=True)


def test_bridge_no_raw_credential_data_output():
    payload = json.dumps(_json(), sort_keys=True)
    assert "RAW_CREDENTIAL" not in payload
    assert "sk-" not in payload


def test_bridge_no_raw_broker_order_id_output():
    assert "RAW_BROKER_ORDER" not in json.dumps(_json(), sort_keys=True)


def test_bridge_live_execution_not_approved():
    payload = json.dumps(_json(), sort_keys=True).lower()
    assert "live execution approved" not in payload
    assert '"live_trading_allowed": true' not in payload


def test_bridge_version_constant_present():
    assert b.VERSION == "oanda_demo_profit_proof_ledger_bridge_v1"
    assert b.OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_VERSION == b.VERSION
