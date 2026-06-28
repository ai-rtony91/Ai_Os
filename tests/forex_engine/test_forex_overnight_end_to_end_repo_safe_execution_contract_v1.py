"""Tests for the overnight end-to-end repo-safe contract module."""

from pathlib import Path

from automation.forex_engine import forex_overnight_end_to_end_repo_safe_execution_contract_v1 as module


def test_default_owner_input_returns_expected_defaults():
    result = module.evaluate_forex_overnight_end_to_end_contract()
    assert result["overnight_contract_status"] == "OVERNIGHT_CONTRACT_BLOCKED_OWNER_INPUT_REQUIRED"
    assert result["overnight_contract_mode"] == "PAUSE_READY"
    assert result["anchor_status"] == "FLOW1_PR_1194_MERGED"
    assert result["owner_live_capital_intent_usd"] == 1000
    assert result["requested_max_open_positions"] == 4
    assert result["requested_quantity_scale"] == 4.0
    assert result["target_return_band"] == "100_TO_120_PERCENT"
    assert result["target_return_claim_status"] == "TARGET_NOT_YET_VERIFIED"
    assert result["runtime_objective"] == "22_HOURS_PER_DAY_6_DAYS_PER_WEEK"
    assert result["repo_safe_work_status"] == "READY_TO_CONTINUE"
    assert result["external_trading_authority_status"] == "BLOCKED"
    assert result["flow2_contract_status"] == "PREPARED"
    assert result["flow3_contract_status"] == "PREPARED"
    assert result["live_exception_contract_status"] == "PREPARED_NOT_AUTHORIZED"


def test_enforce_action_when_accepted_returns_ready_to_enforce():
    owner_input = {
        "overnight_action": "ENFORCE",
        "owner_attestation": True,
        "accepts_dependency_order": True,
        "accepts_flow2_contract": True,
        "accepts_flow3_contract": True,
        "accepts_live_exception_bridge": True,
        "accepts_no_false_claims": True,
        "accepts_external_gate_boundaries": True,
        "accepts_validator_truth": True,
    }
    result = module.evaluate_forex_overnight_end_to_end_contract(owner_input)
    assert result["overnight_contract_status"] == "OVERNIGHT_CONTRACT_READY_TO_ENFORCE_FLOW2"
    assert result["overnight_contract_mode"] == "ENFORCE_READY"


def test_bridge_action_populates_external_gate_registry():
    result = module.evaluate_forex_overnight_end_to_end_contract({"overnight_action": "BRIDGE"})
    assert result["overnight_contract_status"] == "OVERNIGHT_CONTRACT_EXTERNAL_GATE_BRIDGES_READY"
    assert result["overnight_contract_mode"] == "BRIDGE_READY"
    assert len(result["external_gate_registry"]) == 15


def test_pause_action_sets_pause_mode():
    result = module.evaluate_forex_overnight_end_to_end_contract({"overnight_action": "PAUSE"})
    assert result["overnight_contract_status"] == "OVERNIGHT_CONTRACT_PAUSED_BY_OWNER"
    assert result["overnight_contract_mode"] == "PAUSED"


def test_stop_action_sets_stop_mode():
    result = module.evaluate_forex_overnight_end_to_end_contract({"overnight_action": "STOP"})
    assert result["overnight_contract_status"] == "OVERNIGHT_CONTRACT_STOPPED_BY_OWNER"
    assert result["overnight_contract_mode"] == "STOPPED"


def test_dependency_order_has_four_items_and_starts_with_flow2():
    order = module.build_dependency_order()
    assert len(order) == 4
    assert order[0]["flow_id"] == "FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE"


def test_external_gate_registry_contains_required_gates():
    registry = module.build_external_gate_registry()
    names = {entry["gate_name"] for entry in registry}
    required = {
        "owner_input_gate",
        "broker_snapshot_gate",
        "broker_connection_gate",
        "credential_gate",
        "supervised_demo_execution_gate",
        "trade_evidence_capture_gate",
        "realized_pl_capture_gate",
        "profit_countdown_update_gate",
        "flow3_candidate_selection_gate",
        "live_exception_gate",
        "real_money_gate",
        "runtime_supervisor_gate",
        "sos_alert_gate",
        "vacation_mode_gate",
        "publish_clean_merge_gate",
    }
    assert required.issubset(names)


def test_flow2_contract_has_evidence_bundle_output():
    result = module.build_flow2_contract(module.evaluate_forex_overnight_end_to_end_contract())
    assert "evidence_bundle" in result["outputs"]


def test_flow3_contract_has_next_candidate_output():
    result = module.build_flow3_contract(module.evaluate_forex_overnight_end_to_end_contract())
    assert "next_candidate" in result["outputs"]


def test_live_exception_contract_does_not_authorize_live():
    result = module.build_live_exception_contract(
        module.evaluate_forex_overnight_end_to_end_contract()
    )
    assert result["live_authorized_by_this_contract"] is False
    assert result["real_money_authorized_by_this_contract"] is False


def test_generated_artifacts_exist_and_no_banned_tokens():
    module.generate_artifacts()
    outputs = [
        module.JSON_REPORT_PATH,
        module.REPORT_PATH,
        module.QUEUE_PATH,
        module.CONTINUATION_PATH,
        module.GATE_REGISTRY_PATH,
        module.FLOW2_CONTRACT_PATH,
        module.FLOW3_CONTRACT_PATH,
        module.LIVE_EXCEPTION_CONTRACT_PATH,
        module.NEXT_FLOW2_PACKET_PATH,
        module.NEXT_FLOW3_PACKET_PATH,
        module.NEXT_EXCEPTION_PACKET_PATH,
    ]
    for path in outputs:
        assert path.exists()
    report_text = module.REPORT_PATH.read_text(encoding="utf-8").lower()
    queue_text = module.QUEUE_PATH.read_text(encoding="utf-8").lower()
    registry_text = module.GATE_REGISTRY_PATH.read_text(encoding="utf-8").lower()
    for token in module.BANNED_OUTPUT_TOKENS:
        banned = token.lower()
        assert banned not in report_text
        assert banned not in queue_text
        assert banned not in registry_text


def test_validator_publish_and_next_packets_exist():
    assert Path(
        "scripts/forex_delivery/validate_forex_overnight_end_to_end_repo_safe_execution_contract_v1.ps1"
    ).exists()
    assert Path(
        "scripts/forex_delivery/publish_forex_overnight_end_to_end_repo_safe_execution_contract_v1.ps1"
    ).exists()
    assert module.NEXT_FLOW2_PACKET_PATH.exists()
    assert module.NEXT_FLOW3_PACKET_PATH.exists()
    assert module.NEXT_EXCEPTION_PACKET_PATH.exists()
