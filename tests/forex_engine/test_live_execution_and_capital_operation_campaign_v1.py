from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.live_execution_and_capital_operation_campaign_v1 import (  # noqa: E402
    BLOCKED_BY_22H_6D_READINESS,
    BLOCKED_BY_CAPITAL_POLICY,
    BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY,
    BLOCKED_BY_OWNER_APPROVAL_TOKEN,
    BLOCKED_BY_PROTECTED_EXECUTION_GATE,
    BLOCKED_BY_RISK_GATES,
    BLOCKED_BY_SENSITIVE_DATA,
    CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW,
    HARD_FALSE_FIELDS,
    INCOMPLETE_INPUTS,
    MODE,
    READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW,
    READY_FOR_OWNER_VALUE_ENTRY_REVIEW,
    READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET,
    READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE,
    SAFETY_FALSE_FIELDS,
    SCHEMA,
    evaluate_live_execution_and_capital_operation_campaign_v1,
)


MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "live_execution_and_capital_operation_campaign_v1.py"
)


def _clone(value):
    if isinstance(value, dict):
        return {key: _clone(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_clone(child) for child in value]
    return value


def _strong_payload() -> dict:
    return {
        "credential_session_boundary": _credential_boundary(),
        "owner_live_approval_token_metadata": _approval_token(),
        "oanda_mode_declaration": {
            "broker_name": "OANDA",
            "mode": "OANDA_DEMO",
            "account_id_provided": False,
        },
        "one_order_policy": {
            "one_order_only": True,
            "max_order_count_this_packet": 1,
            "duplicate_order_detected": False,
            "existing_open_order_for_candidate": False,
            "next_order_blocked_until_review": True,
        },
        "risk_limits": {
            "max_risk_per_trade_pct": "0.01",
            "max_daily_loss_pct": "0.03",
            "stop_loss_present": True,
            "take_profit_present": True,
            "max_spread_pips": "2.5",
            "max_slippage_pips": "0.5",
        },
        "execution_controls": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
        },
        "protected_runtime_execution_result": {
            "status": "PROTECTED_ONE_ORDER_GATE_CLEARED",
            "real_broker_call_allowed": False,
            "broker_api_called": False,
            "live_trade_executed": False,
            "demo_trade_executed": False,
            "money_moved": False,
        },
        "post_execution_review_loop": _post_review(),
        "capital_policy": {
            "requested_recommendation": "NO_CAPITAL_ACTION_RECOMMENDED",
            "transfer_review_requested": False,
            "all_in_requested": False,
            "evidence_quality_stronger": False,
        },
        "capital_state": {"profit_reserve_ready": False},
        "open_risk": {
            "open_positions_count": 0,
            "margin_used": 0,
            "open_risk_present": False,
            "pending_settlement": False,
            "unsettled_pnl": False,
        },
        "broker_policy_snapshot": {"broker_policy_present": True},
        "cooldown_state": {"cooldown_active": False},
        "drawdown_state": {
            "drawdown_active": False,
            "daily_loss_active": False,
            "daily_loss_stop_active": False,
        },
        "sos_reminder_packet": {"sos_ready": True, "alerts_enabled": True},
        "twenty_two_hour_six_day_readiness_index": _readiness_index(True),
    }


def _credential_boundary() -> dict:
    return {
        "owner_enters_credentials_outside_repo_chat": True,
        "runtime_only_credential_handoff": True,
        "no_stored_api_key": True,
        "no_stored_account_id": True,
        "no_master_password": True,
        "no_vault_password": True,
        "no_raw_token": True,
        "secret_scan_required": True,
        "redaction_required": True,
        "session_expiry_required": True,
        "session_unexpired": True,
        "one_order_session_scope": True,
        "credential_values_provided": False,
        "credential_values_persisted": False,
        "credential_values_logged": False,
        "credential_values_requested_by_aios": False,
        "repo_secret_storage_allowed": False,
        "chat_secret_sharing_allowed": False,
        "env_var_read_allowed": False,
        "account_id_provided": False,
    }


def _approval_token() -> dict:
    return {
        "approval_token_required": True,
        "approval_token_metadata_present": True,
        "approval_token_id_present": True,
        "approval_phrase_present": True,
        "approval_phrase_matches": True,
        "approval_action_matches": True,
        "approval_mode_matches": True,
        "approval_instrument_matches": True,
        "approval_units_matches": True,
        "approval_risk_matches": True,
        "approval_token_unexpired": True,
        "approval_token_unused": True,
        "approval_challenge_hash_present": True,
        "approval_timestamp_present": True,
        "generic_yes_detected": False,
        "raw_approval_phrase_stored": False,
    }


def _post_review() -> dict:
    return {
        "post_trade_review_required": True,
        "post_trade_review_completed": True,
        "sanitized_execution_receipt_present": True,
        "pnl_review_recorded": True,
        "not_applicable_for_metadata_only": False,
        "next_order_blocked_until_review": True,
        "owner_review_required": True,
    }


def _readiness_index(value: bool) -> dict:
    return {
        "broker_session_readiness": value,
        "monitoring_readiness": value,
        "kill_switch_readiness": value,
        "post_trade_review_readiness": value,
        "audit_readiness": value,
        "capital_planner_readiness": value,
        "sos_readiness": value,
        "owner_approval_readiness": value,
        "credential_boundary_readiness": value,
        "recovery_readiness": value,
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_live_execution_and_capital_operation_campaign_v1(payload)


def test_empty_payload_incomplete() -> None:
    result = _run({})
    assert result["schema"] == SCHEMA
    assert result["mode"] == MODE
    assert result["campaign_status"] == INCOMPLETE_INPUTS
    assert result["campaign_ready"] is False


def test_sensitive_data_blocked_and_value_not_echoed() -> None:
    payload = _strong_payload()
    payload["nested"] = {"password": "DO-NOT-ECHO"}
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert result["sensitive_data_detected"] is True
    assert "DO-NOT-ECHO" not in repr(result)


def test_master_password_blocked() -> None:
    payload = _strong_payload()
    payload["master_password"] = "hidden-master"
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "hidden-master" not in repr(result)


def test_api_key_value_blocked() -> None:
    payload = _strong_payload()
    payload["api_key"] = "api-key-value"
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "api-key-value" not in repr(result)


def test_account_id_blocked() -> None:
    payload = _strong_payload()
    payload["oanda_account_id"] = "acct-123"
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "acct-123" not in repr(result)


def test_safe_metadata_not_blocked_as_sensitive() -> None:
    payload = {
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "credential_request_allowed": False,
        "account_id_provided": False,
        "no_stored_api_key": True,
        "no_master_password": True,
        "no_vault_password": True,
        "secret_scan_required": True,
    }
    result = _run(payload)
    assert result["sensitive_data_detected"] is False
    assert result["campaign_status"] != BLOCKED_BY_SENSITIVE_DATA


def test_safe_owner_value_entry_metadata_routes_to_review() -> None:
    result = _run(
        {
            "owner_value_entry_workflow": {
                "account_balance_snapshot": "12000",
                "equity_snapshot": "12100",
                "risk_amount": "25",
                "max_loss_amount": "25",
                "instrument": "EUR_USD",
                "units": "100",
            }
        }
    )
    assert result["campaign_status"] == READY_FOR_OWNER_VALUE_ENTRY_REVIEW
    assert result["next_best_packet"] == "AIOS_FOREX_OWNER_VALUE_ENTRY_REVIEW_PACKET_V1"


def test_owner_value_entry_secret_like_instrument_blocks_without_echo() -> None:
    result = _run({"owner_value_entry_workflow": {"instrument": "sk-secret"}})
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-secret" not in repr(result)
    assert result["owner_value_entry_workflow"]["sanitized_values"] == {}


def test_owner_value_entry_normal_instrument_allowed() -> None:
    result = _run({"owner_value_entry_workflow": {"instrument": "EUR_USD"}})
    assert result["campaign_status"] == READY_FOR_OWNER_VALUE_ENTRY_REVIEW
    assert result["sensitive_data_detected"] is False
    assert result["owner_value_entry_workflow"]["sanitized_values"]["instrument"] == "EUR_USD"


def test_credential_bridge_metadata_routes_to_bridge_review() -> None:
    payload = {"credential_session_boundary": _credential_boundary()}
    payload["credential_session_boundary"]["bridge_ready_for_review"] = True
    result = _run(payload)
    assert result["campaign_status"] == READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE
    assert result["next_best_packet"] == (
        "AIOS_FOREX_OWNER_LIVE_EXCEPTION_AND_RUNTIME_SECRET_SESSION_BRIDGE_V1"
    )


def test_strong_protected_execution_payload_reaches_campaign_ready() -> None:
    result = _run(_strong_payload())
    assert result["campaign_status"] == CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW
    assert result["campaign_ready"] is True
    assert result["next_best_packet"] == (
        "AIOS_FOREX_OWNER_LIVE_EXCEPTION_AND_RUNTIME_SECRET_SESSION_BRIDGE_V1"
    )


def test_missing_credential_boundary_blocks() -> None:
    payload = _strong_payload()
    payload.pop("credential_session_boundary")
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY


def test_expired_credential_session_blocks() -> None:
    payload = _strong_payload()
    payload["credential_session_boundary"]["session_unexpired"] = False
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY
    assert "session_unexpired_false" in result["campaign_blockers"]


def test_generic_yes_approval_blocks() -> None:
    payload = _strong_payload()
    payload["owner_live_approval_token_metadata"]["generic_yes_detected"] = True
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_OWNER_APPROVAL_TOKEN
    assert "generic_yes_detected_true" in result["campaign_blockers"]


def test_exact_approval_token_metadata_passes() -> None:
    result = _run(_strong_payload())
    token = result["live_execution_readiness_gate"]["owner_live_approval_token_metadata"]
    assert token["ready"] is True
    assert token["approval_phrase_matches"] is True
    assert token["approval_token_unexpired"] is True


def test_risk_over_limit_blocks() -> None:
    payload = _strong_payload()
    payload["risk_limits"]["max_risk_per_trade_pct"] = "0.02"
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_RISK_GATES
    assert "max_risk_per_trade_pct_above_limit" in result["campaign_blockers"]


def test_missing_stop_loss_blocks() -> None:
    payload = _strong_payload()
    payload["risk_limits"]["stop_loss_present"] = False
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_RISK_GATES
    assert "stop_loss_present_missing_or_false" in result["campaign_blockers"]


def test_missing_take_profit_blocks() -> None:
    payload = _strong_payload()
    payload["risk_limits"]["take_profit_present"] = False
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_RISK_GATES
    assert "take_profit_present_missing_or_false" in result["campaign_blockers"]


def test_kill_switch_blocks() -> None:
    payload = _strong_payload()
    payload["execution_controls"]["kill_switch_active"] = True
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_RISK_GATES
    assert "kill_switch_active_true" in result["campaign_blockers"]


def test_daily_loss_stop_blocks() -> None:
    payload = _strong_payload()
    payload["execution_controls"]["daily_loss_stop_active"] = True
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_RISK_GATES
    assert "daily_loss_stop_active_true" in result["campaign_blockers"]


def test_duplicate_order_blocks_protected_execution_gate() -> None:
    payload = _strong_payload()
    payload["one_order_policy"]["duplicate_order_detected"] = True
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_PROTECTED_EXECUTION_GATE
    assert "duplicate_order_detected_true" in result["campaign_blockers"]


def test_capital_redistribution_never_moves_money() -> None:
    result = _run(_strong_payload())
    planner = result["capital_redistribution_planner"]
    assert planner["money_movement_allowed"] is False
    assert planner["bank_access_allowed"] is False
    assert result["money_moved"] is False
    assert result["deposit_allowed"] is False
    assert result["withdrawal_allowed"] is False


def test_capital_can_recommend_compound_same_pair_without_money_movement() -> None:
    payload = _strong_payload()
    payload["capital_policy"]["requested_recommendation"] = "COMPOUND_INTO_SAME_PAIR"
    payload["capital_policy"]["evidence_quality_stronger"] = True
    result = _run(payload)
    planner = result["capital_redistribution_planner"]
    assert planner["recommended_capital_action"] == "COMPOUND_INTO_SAME_PAIR"
    assert planner["money_movement_allowed"] is False
    assert result["campaign_status"] == READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW


def test_capital_can_recommend_allowed_pair_basket_without_money_movement() -> None:
    payload = _strong_payload()
    payload["pair_allocation_targets"] = {"EUR_USD": "0.50", "GBP_USD": "0.50"}
    result = _run(payload)
    planner = result["capital_redistribution_planner"]
    assert planner["recommended_capital_action"] == "REDISTRIBUTE_INTO_ALLOWED_PAIR_BASKET"
    assert planner["money_movement_allowed"] is False
    assert result["campaign_status"] == READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW


def test_capital_redistribution_blocks_all_in_allocation() -> None:
    payload = _strong_payload()
    payload["pair_allocation_targets"] = {"EUR_USD": "1"}
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_CAPITAL_POLICY
    assert "all_in_allocation_blocked" in result["campaign_blockers"]


def test_transfer_like_review_blocks_when_broker_policy_missing() -> None:
    payload = _strong_payload()
    payload["capital_policy"]["requested_recommendation"] = "OWNER_REVIEW_WITHDRAWAL"
    payload.pop("broker_policy_snapshot")
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_CAPITAL_POLICY
    assert result["capital_redistribution_planner"]["recommended_capital_action"] == (
        "BLOCKED_BY_BROKER_POLICY"
    )


def test_transfer_like_review_blocks_when_open_risk_exists() -> None:
    payload = _strong_payload()
    payload["capital_policy"]["requested_recommendation"] = "OWNER_REVIEW_WITHDRAWAL"
    payload["open_risk"]["open_positions_count"] = 1
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_CAPITAL_POLICY
    assert result["capital_redistribution_planner"]["recommended_capital_action"] == (
        "BLOCKED_BY_OPEN_RISK"
    )


def test_bank_and_debit_card_rail_labels_are_allowed() -> None:
    result = _run(
        {
            "owner_value_entry_workflow": {
                "bank_or_card_rail_label": "DEBIT_CARD_REVIEW_RAIL",
                "instrument": "EUR_USD",
            }
        }
    )
    assert result["campaign_status"] == READY_FOR_OWNER_VALUE_ENTRY_REVIEW
    assert result["sensitive_data_detected"] is False
    assert (
        result["owner_value_entry_workflow"]["sanitized_values"]["bank_or_card_rail_label"]
        == "DEBIT_CARD_REVIEW_RAIL"
    )


def test_bank_and_debit_card_numbers_are_blocked() -> None:
    payload = {
        "owner_value_entry_workflow": {
            "bank_or_card_rail_label": "BANK_REVIEW_RAIL_123456789",
        }
    }
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "123456789" not in repr(result)


def test_sos_reminder_generated_for_missing_approval() -> None:
    payload = _strong_payload()
    payload["owner_live_approval_token_metadata"]["approval_token_id_present"] = False
    result = _run(payload)
    reminder_ids = {
        item["reminder_id"] for item in result["sos_reminder_packet"]["reminders"]
    }
    assert "APPROVAL_TOKEN_REVIEW" in reminder_ids


def test_sos_reminder_generated_for_expired_session() -> None:
    payload = _strong_payload()
    payload["credential_session_boundary"]["session_unexpired"] = False
    result = _run(payload)
    reminder_ids = {
        item["reminder_id"] for item in result["sos_reminder_packet"]["reminders"]
    }
    assert "CREDENTIAL_SESSION_EXPIRED" in reminder_ids


def test_sos_reminder_generated_for_post_trade_review_missing() -> None:
    payload = _strong_payload()
    payload["post_execution_review_loop"]["post_trade_review_completed"] = False
    result = _run(payload)
    reminder_ids = {
        item["reminder_id"] for item in result["sos_reminder_packet"]["reminders"]
    }
    assert "POST_TRADE_REVIEW_REQUIRED" in reminder_ids


def test_sos_reminder_generated_for_capital_block() -> None:
    payload = _strong_payload()
    payload["capital_policy"]["requested_recommendation"] = "OWNER_REVIEW_WITHDRAWAL"
    payload.pop("broker_policy_snapshot")
    result = _run(payload)
    reminder_ids = {
        item["reminder_id"] for item in result["sos_reminder_packet"]["reminders"]
    }
    assert "CAPITAL_REDISTRIBUTION_BLOCKED" in reminder_ids


def test_readiness_index_blocks_when_incomplete() -> None:
    payload = _strong_payload()
    payload["twenty_two_hour_six_day_readiness_index"]["recovery_readiness"] = False
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_22H_6D_READINESS
    assert result["twenty_two_hour_six_day_readiness_index"]["total_score"] == 90


def test_readiness_index_passes_when_all_metadata_true() -> None:
    result = _run(_strong_payload())
    index = result["twenty_two_hour_six_day_readiness_index"]
    assert index["total_score"] == 100
    assert index["readiness_passed"] is True


def test_all_hard_false_fields_remain_false() -> None:
    result = _run(_strong_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False
    for field in SAFETY_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_next_best_packet_routes_for_key_statuses() -> None:
    ready = _run(_strong_payload())
    assert ready["next_best_packet"] == (
        "AIOS_FOREX_OWNER_LIVE_EXCEPTION_AND_RUNTIME_SECRET_SESSION_BRIDGE_V1"
    )

    sensitive = _run({"api_key": "blocked"})
    assert sensitive["next_best_packet"] == SCHEMA

    value_entry = _run({"owner_value_entry_workflow": {"instrument": "EUR_USD"}})
    assert value_entry["next_best_packet"] == "AIOS_FOREX_OWNER_VALUE_ENTRY_REVIEW_PACKET_V1"

    bridge_payload = {"credential_session_boundary": _credential_boundary()}
    bridge_payload["credential_session_boundary"]["bridge_ready_for_review"] = True
    bridge = _run(bridge_payload)
    assert bridge["next_best_packet"] == (
        "AIOS_FOREX_OWNER_LIVE_EXCEPTION_AND_RUNTIME_SECRET_SESSION_BRIDGE_V1"
    )

    protected_demo_payload = _strong_payload()
    protected_demo_payload.pop("protected_runtime_execution_result")
    protected_demo = _run(protected_demo_payload)
    assert protected_demo["campaign_status"] == READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET
    assert protected_demo["next_best_packet"] == (
        "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1"
    )

    capital_payload = _strong_payload()
    capital_payload["capital_policy"]["requested_recommendation"] = (
        "COMPOUND_INTO_SAME_PAIR"
    )
    capital_payload["capital_policy"]["evidence_quality_stronger"] = True
    capital = _run(capital_payload)
    assert capital["next_best_packet"] == (
        "AIOS_FOREX_CAPITAL_REDISTRIBUTION_OWNER_REVIEW_PACKET_V1"
    )

    blocked = _strong_payload()
    blocked["risk_limits"]["max_risk_per_trade_pct"] = "0.02"
    assert _run(blocked)["next_best_packet"] == SCHEMA


def test_production_source_has_no_forbidden_runtime_source_markers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    forbidden = (
        "re" + "quests",
        "so" + "cket",
        "ur" + "llib",
        "sub" + "process",
        "os." + "environ",
        "broker" + "_sdk",
        "schedule" + ".every",
        "start" + "-process",
    )
    for marker in forbidden:
        assert marker not in source
