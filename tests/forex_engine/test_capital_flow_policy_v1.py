from pathlib import Path

from automation.forex_engine import capital_flow_policy_v1 as policy


def base_state(**overrides):
    state = {
        "trading_balance": 10_000,
        "reserve_balance": 5_000,
        "profit_vault_balance": 500,
        "tax_bucket_balance": 1_000,
        "operating_account_balance": 2_500,
        "minimum_trading_float": 8_000,
        "maximum_trading_float": 12_000,
        "sweep_threshold": 1_000,
        "resupply_threshold": 8_000,
        "compounding_threshold": 2_000,
        "compounding_target": 15_000,
        "max_withdrawal_per_event": 2_500,
        "max_deposit_per_event": 2_500,
        "cooldown_minutes": 60,
        "maintenance_window": True,
        "emergency_freeze": False,
        "daily_loss_lockout": False,
        "broker_proof_status": "CURRENT",
        "bank_proof_status": "CURRENT",
        "payment_rail_proof_status": "CURRENT",
        "live_trading_lock_status": "LIVE_LOCKED",
        "human_approval_status": "APPROVED_FOR_DRAFT",
        "last_transfer_request_timestamp": "UNKNOWN",
        "account_aliases": [
            "TRADING_FLOAT",
            "RESERVE_ACCOUNT",
            "TAX_BUCKET",
            "PROFIT_VAULT",
            "OPERATING_ACCOUNT",
        ],
    }
    state.update(overrides)
    return state


def test_capital_flow_defaults_to_display_only_policy_only():
    result = policy.run_capital_flow_policy()

    assert result["classifications"]["CAPITAL_FLOW_STATUS"] == policy.CAPITAL_FLOW_DISPLAY_ONLY
    assert result["classifications"]["TREASURY_AUTOMATION_STATUS"] == policy.TREASURY_AUTOMATION_POLICY_ONLY
    assert result["classifications"]["MONEY_RELEVANCE_STATUS"] == policy.MONEY_RELEVANT_VISIBLE
    assert result["money_ladder_status"] == policy.MONEY_LADDER_100K_GOAL_SIMULATION_ONLY
    assert result["money_ladder_doctrine"]["profit_guarantee"] is False
    assert result["transfer_completion_claimed"] is False


def test_zero_99_is_micro_test_and_never_live_transfer_ready():
    result = policy.run_capital_flow_policy(base_state(trading_balance=0.99))
    scenario = next(item for item in result["simulation_ladder"] if item["balance"] == "0.99")

    assert scenario["capital_tier"] == "MICRO_TEST"
    assert scenario["resupply_recommendation"] == policy.DRAFT_RESUPPLY_REQUEST
    assert scenario["live_transfer_ready"] is False
    assert scenario["transfer_authority"] is False


def test_100000_is_high_control_float_and_triggers_strict_caps():
    result = policy.run_capital_flow_policy(base_state(trading_balance=100_000))
    scenario = next(item for item in result["simulation_ladder"] if item["balance"] == "100000.00")

    assert scenario["capital_tier"] == "HIGH_CONTROL_FLOAT"
    assert scenario["trading_float_status"] == "ABOVE_CAP_STRICT_CONTROL"
    assert scenario["withdrawal_gate"] == "STRICT_CAP_REQUIRED"
    assert scenario["sweep_recommendation"] == policy.DRAFT_PROFIT_SWEEP_REQUEST
    assert scenario["goal_milestone_status"] == "SIMULATION_CEILING_NOT_GUARANTEE"
    assert scenario["profit_guarantee"] is False


def test_high_trading_balance_above_cap_creates_draft_sweep_recommendation():
    result = policy.run_capital_flow_policy(base_state(trading_balance=15_000))

    assert policy.DRAFT_PROFIT_SWEEP_REQUEST in result["recommendations"]
    assert result["classifications"]["SWEEP_STATUS"] == policy.PROFIT_SWEEP_DRAFT_READY
    assert result["request_previews"][0]["transfer_executed"] is False


def test_low_trading_balance_below_floor_creates_draft_resupply_recommendation():
    result = policy.run_capital_flow_policy(base_state(trading_balance=6_500))

    assert policy.DRAFT_RESUPPLY_REQUEST in result["recommendations"]
    assert result["classifications"]["RESUPPLY_STATUS"] == policy.RESUPPLY_REQUEST_DRAFT_READY


def test_compounding_threshold_creates_draft_compound_in_place_recommendation():
    result = policy.run_capital_flow_policy(base_state(profit_vault_balance=2_500))

    assert policy.DRAFT_COMPOUND_IN_PLACE_REQUEST in result["recommendations"]
    assert result["classifications"]["COMPOUND_STATUS"] == policy.COMPOUND_IN_PLACE_DRAFT_READY


def test_emergency_freeze_blocks_withdrawals_resupply_compound_and_sweep():
    result = policy.run_capital_flow_policy(
        base_state(
            trading_balance=15_000,
            profit_vault_balance=3_000,
            withdrawal_intent_amount=1_000,
            emergency_freeze=True,
        )
    )

    assert result["classifications"]["CAPITAL_FLOW_STATUS"] == policy.CAPITAL_FLOW_FROZEN_BY_RISK
    assert result["recommendations"] == (policy.FREEZE_CAPITAL_FLOW,)
    assert result["request_previews"] == ()


def test_missing_connector_proof_blocks_live_transfer_claims():
    result = policy.run_capital_flow_policy(
        base_state(
            trading_balance=15_000,
            broker_proof_status="MISSING",
            bank_proof_status="MISSING",
            payment_rail_proof_status="MISSING",
        )
    )

    assert result["classifications"]["CAPITAL_FLOW_STATUS"] == policy.CAPITAL_FLOW_BLOCKED_BY_CONNECTOR_PROOF
    assert result["classifications"]["SWEEP_STATUS"] == policy.PROFIT_SWEEP_BLOCKED_BY_CONNECTOR_PROOF
    assert result["transfer_completion_claimed"] is False


def test_missing_human_approval_blocks_transfer_execution():
    result = policy.run_capital_flow_policy(
        base_state(trading_balance=15_000, human_approval_status="MISSING")
    )

    assert result["classifications"]["CAPITAL_FLOW_STATUS"] == policy.CAPITAL_FLOW_BLOCKED_BY_APPROVAL
    assert result["classifications"]["SWEEP_STATUS"] == policy.PROFIT_SWEEP_BLOCKED_BY_APPROVAL
    assert result["transfer_completion_claimed"] is False


def test_engine_never_requires_credentials_env_network_or_account_ids():
    result = policy.run_capital_flow_policy(
        base_state(account_id="not_allowed", credentials={"value": "not_allowed"})
    )

    assert result["safety_summary"]["credentials_read"] is False
    assert result["safety_summary"]["account_identifiers_read"] is False
    assert result["safety_summary"]["env_read"] is False
    assert result["safety_summary"]["network_call_performed"] is False
    assert "account_id" not in result["policy_inputs"]
    assert "credentials" not in result["policy_inputs"]


def test_write_reports_only_writes_allowed_report_paths(monkeypatch, tmp_path):
    reports_dir = tmp_path / "Reports" / "forex_delivery"
    monkeypatch.setattr(policy, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(
        policy,
        "REPORT_PATHS",
        {
            "money_goal_ladder": reports_dir / "AIOS_MONEY_COCKPIT_100K_GOAL_LADDER_V11.md",
            "simulation_range": reports_dir / "AIOS_CAPITAL_FLOW_POLICY_SIMULATION_RANGE_V11.md",
            "money_relevance": reports_dir / "AIOS_MONEY_RELEVANCE_DASHBOARD_RULE_V11.md",
        },
    )

    result = policy.run_capital_flow_policy(base_state(trading_balance=15_000), write_reports=True)
    written_names = {Path(path).name for path in result["reports"]["written"]}

    assert written_names == {path.name for path in policy.REPORT_PATHS.values()}


def test_maintenance_window_changes_recommendation_to_maintenance_safe_action():
    result = policy.run_capital_flow_policy(base_state(trading_balance=15_000, maintenance_window=False))

    assert result["classifications"]["CAPITAL_FLOW_STATUS"] == policy.CAPITAL_FLOW_MAINTENANCE_ONLY
    assert policy.NEEDS_MAINTENANCE_WINDOW in result["recommendations"]


def test_money_relevance_rule_collapses_or_hides_non_money_technical_detail():
    result = policy.run_capital_flow_policy()
    samples = result["money_relevance_rule"]["classification_samples"]

    assert samples["trading_float"] == policy.MONEY_RELEVANT_VISIBLE
    assert samples["validator_logs"] == policy.MONEY_RELEVANT_COLLAPSED
    assert samples["css_build_diagnostics"] == policy.MONEY_RELEVANT_COLLAPSED
    assert samples["repo_noise"] == policy.MONEY_RELEVANT_COLLAPSED
