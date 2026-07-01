from automation.forex_engine.forex_vacation_mode_entry_authority_gate_v1 import (
    ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW,
    ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY,
    ENTRY_BLOCKED_BY_MARKET,
    ENTRY_BLOCKED_BY_OWNER_AUTHORITY,
    ENTRY_BLOCKED_BY_PRODUCT_POLICY,
    ENTRY_BLOCKED_BY_RISK,
    ENTRY_BLOCKED_BY_SETUP_SIGNAL,
    INCOMPLETE_INPUTS,
    evaluate_forex_vacation_mode_entry_authority_gate_v1,
)
import pytest


def _entry_payload(**overrides):
    payload = {
        "product_policy_state": {
            "policy_docs_present": True,
            "financial_risk_disclosure_present": True,
            "no_profit_guarantee_acknowledged": True,
            "no_passive_income_claim_acknowledged": True,
            "metadata_only_readiness_separated_from_live_authority": True,
            "owner_review_required_before_release": True,
            "play_store_ready_claimed": False,
            "legal_compliance_ready_claimed": False,
            "sell_ready_claimed": False,
            "profit_ready_claimed": False,
        },
        "owner_authority_state": {
            "owner_authority_approved": True,
            "owner_identity_confirmed": True,
            "owner_approval_current": True,
            "one_action_stop_acknowledged": True,
            "repeat_attempt_blocked_until_review": True,
            "live_execution_authorized": False,
            "live_trade_authorized": False,
            "next_trade_authorized": False,
            "repeat_trade_authorized": False,
        },
        "setup_signal_state": {
            "setup_signal_valid": True,
            "entry_review_candidate_present": True,
            "strategy_metadata_present": True,
            "owner_visible_reason_present": True,
        },
        "risk_state": {
            "risk_per_trade_limit_defined": True,
            "daily_loss_limit_defined": True,
            "risk_within_limits": True,
            "stop_loss_ready": True,
            "exit_plan_ready": True,
            "max_loss_visible_to_owner": True,
            "daily_loss_stop_active": False,
            "kill_switch_active": False,
        },
        "market_state": {
            "market_open": True,
            "calendar_ready": True,
            "spread_within_limit": True,
            "supervision_window_ready": True,
        },
        "broker_read_only_state": {
            "metadata_only": True,
            "read_only": True,
            "execution_permission_false": True,
            "execution_permission": False,
            "order_permission": False,
            "close_permission": False,
        },
        "proof_state": {
            "proof_ledger_ready": True,
            "receipt_contract_ready": True,
            "post_action_evidence_plan_ready": True,
            "sanitized_evidence_required": True,
        },
        "safety_policy": {
            "metadata_only": True,
            "no_trade_execution": True,
            "no_broker_call": True,
            "no_oanda_call": True,
            "no_credential_access": True,
            "no_account_identifier_access": True,
            "no_money_movement": True,
            "no_notification_send": True,
            "no_background_runtime": True,
            "trade_execution_allowed": False,
            "broker_call_allowed": False,
            "oanda_call_allowed": False,
        },
    }
    for section, values in overrides.items():
        payload[section].update(values)
    return payload


def test_incomplete_input_blocks():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1()

    assert result["status"] == INCOMPLETE_INPUTS


def test_blocks_without_product_policy_readiness():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(
        _entry_payload(product_policy_state={"policy_docs_present": False})
    )

    assert result["status"] == ENTRY_BLOCKED_BY_PRODUCT_POLICY


def test_blocks_without_owner_authority():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(
        _entry_payload(owner_authority_state={"owner_authority_approved": False})
    )

    assert result["status"] == ENTRY_BLOCKED_BY_OWNER_AUTHORITY


def test_blocks_without_valid_setup_signal():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(
        _entry_payload(setup_signal_state={"setup_signal_valid": False})
    )

    assert result["status"] == ENTRY_BLOCKED_BY_SETUP_SIGNAL


def test_blocks_risk_violation():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(
        _entry_payload(risk_state={"risk_within_limits": False})
    )

    assert result["status"] == ENTRY_BLOCKED_BY_RISK


def test_blocks_unsafe_market():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(
        _entry_payload(market_state={"market_open": False})
    )

    assert result["status"] == ENTRY_BLOCKED_BY_MARKET


def test_blocks_broker_execution_permission_true():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(
        _entry_payload(broker_read_only_state={"execution_permission": True})
    )

    assert result["status"] == ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY


def test_ready_state_does_not_place_order():
    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(_entry_payload())

    assert result["status"] == ENTRY_AUTHORITY_READY_FOR_OWNER_REVIEW
    assert result["order_placed"] is False
    assert result["broker_api_called_by_this_module"] is False


@pytest.mark.parametrize(
    "field",
    (
        "live_execution_authorized",
        "live_trade_authorized",
        "next_trade_authorized",
        "repeat_trade_authorized",
    ),
)
def test_live_execution_boundary_flags_missing_block_by_type(field):
    payload = _entry_payload()
    payload["owner_authority_state"].pop(field, None)

    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(payload)

    assert result["status"] == ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY
    assert f"{field}_required_bool" in result["blockers"]


@pytest.mark.parametrize(
    "field",
    (
        "live_execution_authorized",
        "live_trade_authorized",
        "next_trade_authorized",
        "repeat_trade_authorized",
    ),
)
def test_live_execution_boundary_flags_non_bool_block(field):
    payload = _entry_payload(owner_authority_state={field: "true"})

    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(payload)

    assert result["status"] == ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY
    assert f"{field}_required_bool" in result["blockers"]


@pytest.mark.parametrize(
    "field,value",
    (
        ("live_execution_authorized", 1),
        ("live_execution_authorized", "true"),
        ("live_trade_authorized", 1),
        ("live_trade_authorized", "true"),
        ("next_trade_authorized", 1),
        ("next_trade_authorized", "true"),
        ("repeat_trade_authorized", 1),
        ("repeat_trade_authorized", "true"),
    ),
)
def test_live_execution_boundary_truthy_non_bool_values_block(field, value):
    payload = _entry_payload(owner_authority_state={field: value})

    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(payload)

    assert result["status"] == ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY
    assert f"{field}_required_bool" in result["blockers"]


@pytest.mark.parametrize(
    "field",
    (
        "live_execution_authorized",
        "live_trade_authorized",
        "next_trade_authorized",
        "repeat_trade_authorized",
    ),
)
def test_live_execution_boundary_true_is_rejected(field):
    payload = _entry_payload(owner_authority_state={field: True})

    result = evaluate_forex_vacation_mode_entry_authority_gate_v1(payload)

    assert result["status"] == ENTRY_BLOCKED_BY_LIVE_EXECUTION_BOUNDARY
    assert f"{field}_must_remain_false" in result["blockers"]
