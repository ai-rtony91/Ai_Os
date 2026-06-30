from __future__ import annotations

from pathlib import Path

from automation.forex_engine.capital_operating_program_v2 import (
    ACTION_AUTO,
    ACTION_COMPOUND_IN_ACCOUNT,
    ACTION_NO_TRANSFER,
    ACTION_OWNER_REVIEW_BUCKET_PURGE,
    ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
    ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    SCHEMA,
    STATUS_BLOCKED_BY_APPROVAL_TOKEN,
    STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE,
    STATUS_BLOCKED_BY_DATA_QUALITY,
    STATUS_BLOCKED_BY_DEMO_PROOF,
    STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS,
    STATUS_BLOCKED_BY_LIVE_MODE_GATES,
    STATUS_BLOCKED_BY_OPEN_RISK,
    STATUS_BLOCKED_BY_PROFIT_THRESHOLD,
    STATUS_BLOCKED_BY_TRANSFER_CADENCE,
    STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
    STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF,
    STATUS_INCOMPLETE_INPUTS,
    STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW,
    evaluate_capital_operating_program_v2,
    MODE_DEMO_PROOF,
    MODE_LIVE_REVIEW,
    MODE_READ_ONLY_REVIEW,
)


def test_base_flags_are_permanently_false() -> None:
    result = evaluate_capital_operating_program_v2(_base_payload())
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    for field in (
        "money_movement_allowed",
        "bank_access_allowed",
        "broker_api_allowed",
        "deposit_allowed",
        "withdrawal_allowed",
        "ach_allowed",
        "wire_allowed",
        "card_transfer_allowed",
        "credential_storage_allowed",
        "credential_read_allowed",
        "live_capital_action_authorized",
    ):
        assert result[field] is False
    for field in ("owner_decision_required", "approval_token_required"):
        assert result[field] is True
    assert result["default_failure_prompt"]


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = evaluate_capital_operating_program_v2({})
    assert result["capital_program_status"] == STATUS_INCOMPLETE_INPUTS
    assert result["recommended_capital_action"] == ACTION_NO_TRANSFER
    assert result["audit_record"]["owner_name"] == "Anthony"


def test_sensitive_payload_blocked_and_not_echoed() -> None:
    payload = _base_payload()
    payload["account_state"]["routing_number"] = "000111222"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_DATA_QUALITY
    assert "sensitive_data_provided" in result["capital_blockers"]
    assert "000111222" not in repr(result)


def test_safety_boundary_keys_are_not_misclassified_as_sensitive() -> None:
    payload = _base_payload()
    payload["approval_token_required"] = False
    payload["approval_token_present"] = False
    payload["credential_read_allowed"] = False
    payload["broker_api_allowed"] = False
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] != STATUS_BLOCKED_BY_DATA_QUALITY


def test_generic_yes_does_not_pass_token() -> None:
    payload = _base_payload()
    payload["approval_token_evidence"]["approval_phrase_matches"] = False
    payload["approval_token_evidence"]["approval_phrase_present"] = True
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_APPROVAL_TOKEN


def test_voice_approval_requires_exact_token_metadata() -> None:
    payload = _base_payload()
    payload["approval_token_evidence"]["approval_channel"] = "VOICE"
    payload["requested_action"] = ACTION_OWNER_REVIEW_PROFIT_SWEEP
    payload["approval_token_evidence"]["approval_action"] = ACTION_OWNER_REVIEW_PROFIT_SWEEP
    assert evaluate_capital_operating_program_v2(payload)["capital_program_status"] == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW

    bad = _base_payload()
    bad["requested_action"] = ACTION_OWNER_REVIEW_PROFIT_SWEEP
    bad["approval_token_evidence"]["approval_channel"] = "VOICE"
    bad["approval_token_evidence"]["approval_phrase_matches"] = False
    bad["approval_token_evidence"]["approval_phrase_present"] = True
    assert evaluate_capital_operating_program_v2(bad)["capital_program_status"] == STATUS_BLOCKED_BY_APPROVAL_TOKEN


def test_owner_cancel_phrase_blocks_token() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_PROFIT_SWEEP
    payload["approval_token_evidence"]["owner_cancel_phrase_detected"] = True
    payload["approval_token_evidence"]["approval_action"] = ACTION_OWNER_REVIEW_PROFIT_SWEEP
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_APPROVAL_TOKEN
    assert "approval_token_failed" in result["capital_blockers"]


def test_missing_broker_policy_blocks_transfer_like_actions() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_PROFIT_SWEEP
    payload.pop("broker_policy_snapshot", None)
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == "BLOCKED_BY_MISSING_POLICY_SNAPSHOT"

def test_missing_terms_acknowledgment_blocks_transfer_like_actions() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_WITHDRAW_PROFIT
    payload["broker_policy_snapshot"]["terms_acknowledged_by_owner"] = False
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE
    assert "terms_acknowledged_by_owner_false" in result["capital_blockers"]


def test_missing_policy_source_reference_blocks_transfer_like_actions() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_PROFIT_SWEEP
    payload["broker_policy_snapshot"]["policy_source_reference"] = ""
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE
    assert "policy_source_reference_missing" in result["capital_blockers"]


def test_monthly_withdrawal_cadence_exhausted() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_WITHDRAW_PROFIT
    payload["transfer_history"]["withdrawals_this_month"] = "4"
    payload["compounding_policy"]["max_withdrawals_per_month"] = "4"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE


def test_monthly_deposit_cadence_exhausted() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP
    payload["transfer_history"]["deposits_this_month"] = "4"
    payload["compounding_policy"]["max_deposits_per_month"] = "4"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE


def test_withdrawal_cooldown_blocks_withdrawal() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_WITHDRAW_PROFIT
    payload["transfer_history"]["last_withdrawal_days_ago"] = "2"
    payload["transfer_history"]["withdrawals_this_month"] = "1"
    payload["broker_policy_snapshot"]["withdrawal_cooldown_days"] = "7"
    payload["broker_policy_snapshot"]["withdrawal_cooldown_satisfied"] = False
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE


def test_deposit_cooldown_blocks_deposit_top_up() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP
    payload["transfer_history"]["last_deposit_days_ago"] = "2"
    payload["broker_policy_snapshot"]["deposit_cooldown_days"] = "7"
    payload["broker_policy_snapshot"]["deposit_cooldown_satisfied"] = False
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE


def test_open_positions_block_sweep_withdrawal() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_WITHDRAW_PROFIT
    payload["open_risk"]["open_positions_count"] = "3"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_OPEN_RISK


def test_margin_used_blocks_withdrawal_action() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_WITHDRAW_PROFIT
    payload["open_risk"]["margin_used"] = "110"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_OPEN_RISK


def test_pending_settlement_blocks_transfer_actions() -> None:
    payload = _base_payload()
    payload["requested_action"] = ACTION_OWNER_REVIEW_WITHDRAW_PROFIT
    payload["open_risk"]["pending_settlement"] = True
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_OPEN_RISK


def test_daily_loss_stop_blocks_all_capital_actions() -> None:
    payload = _base_payload()
    payload["open_risk"]["daily_loss_stop_active"] = True
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS


def test_kill_switch_blocks_all_capital_actions() -> None:
    payload = _base_payload()
    payload["open_risk"]["kill_switch_active"] = True
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS


def test_drawdown_exceeded_blocks_actions() -> None:
    payload = _base_payload()
    payload["account_state"]["drawdown_pct"] = "25"
    payload["compounding_policy"]["max_drawdown_pct_for_capital_action"] = "10"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS


def test_profit_below_compounding_threshold_is_blocked_or_no_transfer() -> None:
    payload = _base_payload()
    payload["account_state"]["realized_profit_month"] = "40"
    payload["compounding_policy"]["min_profit_to_compound"] = "100"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_PROFIT_THRESHOLD
    assert result["recommended_capital_action"] == ACTION_NO_TRANSFER


def test_profit_above_threshold_but_below_sweep_compounds() -> None:
    payload = _base_payload()
    payload["account_state"]["realized_profit_month"] = "220"
    payload["compounding_policy"]["min_profit_to_compound"] = "100"
    payload["compounding_policy"]["min_profit_to_sweep"] = "500"
    payload["bucket_state"]["profit_bucket"] = "100"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["recommended_capital_action"] == ACTION_COMPOUND_IN_ACCOUNT
    assert result["capital_program_status"] == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW


def test_profit_above_sweep_threshold_recommends_profit_sweep() -> None:
    payload = _base_payload()
    payload["account_state"]["realized_profit_month"] = "700"
    payload["bucket_state"]["profit_bucket"] = "550"
    result = evaluate_capital_operating_program_v2(payload)
    assert result["recommended_capital_action"] == ACTION_OWNER_REVIEW_PROFIT_SWEEP
    assert result["capital_program_status"] == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW


def test_stale_bucket_age_recommends_purge() -> None:
    payload = _base_payload()
    payload["bucket_state"]["stale_bucket_age_days"] = "25"
    payload["compounding_policy"]["bucket_purge_after_days"] = "10"
    payload["broker_policy_snapshot"]["terms_acknowledged_by_owner"] = True
    result = evaluate_capital_operating_program_v2(payload)
    assert result["recommended_capital_action"] == ACTION_OWNER_REVIEW_BUCKET_PURGE


def test_demo_proof_mode_ready_when_gates_pass() -> None:
    payload = _base_payload()
    payload["mode"] = MODE_DEMO_PROOF
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF


def test_live_review_without_demo_proof_blocks_live_exception() -> None:
    payload = _base_payload()
    payload["mode"] = MODE_LIVE_REVIEW
    payload["demo_proof"]["demo_proof_ready"] = False
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_DEMO_PROOF


def test_live_review_with_all_requirements_ready() -> None:
    payload = _base_payload()
    payload["mode"] = MODE_LIVE_REVIEW
    payload["demo_proof"]["demo_proof_ready"] = True
    payload["live_exception"] = {
        "live_review_requested": True,
        "demo_proof_ready": True,
        "owner_live_exception_approval": True,
        "broker_policy_snapshot_current": True,
        "compliance_evidence_complete": True,
        "no_open_risk": True,
        "live_exception_ready": True,
    }
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW


def test_live_capital_action_authorized_never_true() -> None:
    payload = _base_payload()
    payload["mode"] = MODE_LIVE_REVIEW
    payload["demo_proof"]["demo_proof_ready"] = True
    payload["live_exception"] = {
        "live_review_requested": True,
        "demo_proof_ready": True,
        "owner_live_exception_approval": True,
        "broker_policy_snapshot_current": True,
        "compliance_evidence_complete": True,
        "no_open_risk": True,
        "live_exception_ready": True,
    }
    result = evaluate_capital_operating_program_v2(payload)
    assert result["live_capital_action_authorized"] is False
    assert result["safety"]["live_capital_action_authorized"] is False


def test_default_failure_prompt_is_always_present() -> None:
    result = evaluate_capital_operating_program_v2(_base_payload())
    assert isinstance(result["default_failure_prompt"], str)
    blocked = evaluate_capital_operating_program_v2({})
    assert isinstance(blocked["default_failure_prompt"], str)
    assert "No money was moved" in blocked["default_failure_prompt"]


def test_default_failure_prompt_mentions_blocked_fields() -> None:
    payload = _base_payload()
    payload["open_risk"]["daily_loss_stop_active"] = True
    result = evaluate_capital_operating_program_v2(payload)
    assert "AIOS CAPITAL ACTION BLOCKED" in result["default_failure_prompt"]
    assert "Attempted action" in result["default_failure_prompt"]
    assert "No money was moved" in result["default_failure_prompt"]


def test_owner_action_queue_has_review_next_packet() -> None:
    result = evaluate_capital_operating_program_v2(_base_payload())
    actions = {item["owner_action_id"] for item in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in actions


def test_next_packet_routing_for_statuses() -> None:
    base = _base_payload()
    base["mode"] = MODE_DEMO_PROOF
    assert (
        evaluate_capital_operating_program_v2(base)["next_best_packet"]
        == "AIOS_FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1"
    )

    blocked = evaluate_capital_operating_program_v2({})
    assert (
        blocked["next_best_packet"]
        == "AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2"
    )

    live = _base_payload()
    live["mode"] = MODE_LIVE_REVIEW
    live["demo_proof"]["demo_proof_ready"] = True
    live["live_exception"] = {
        "live_review_requested": True,
        "demo_proof_ready": True,
        "owner_live_exception_approval": True,
        "broker_policy_snapshot_current": True,
        "compliance_evidence_complete": True,
        "no_open_risk": True,
        "live_exception_ready": True,
    }
    assert (
        evaluate_capital_operating_program_v2(live)["next_best_packet"]
        == "AIOS_FOREX_LIVE_CAPITAL_RAIL_EXCEPTION_GATE_V1"
    )

    owner_review = evaluate_capital_operating_program_v2(_base_payload())
    assert (
        owner_review["next_best_packet"]
        == "AIOS_FOREX_OWNER_REVIEW_CAPITAL_ACTION_PACKET_V1"
    )


def test_source_code_has_no_forbidden_runtime_or_api_tokens() -> None:
    source_text = Path("automation/forex_engine/capital_operating_program_v2.py").read_text(encoding="utf-8")
    forbidden = (
        "re" + "quests",
        "so" + "cket",
        "ur" + "llib",
        "sub" + "process",
        "os." + "environ",
        "broker_" + "sdk",
        "schedule." + "every",
        "start-" + "process",
    )
    lowered = source_text.lower()
    for phrase in forbidden:
        assert phrase not in lowered


def test_result_does_not_include_hardcoded_policy_limits() -> None:
    source_text = Path("automation/forex_engine/capital_operating_program_v2.py").read_text(encoding="utf-8")
    forbidden_patterns = [
        "".join(["100", "-", "120"]),
        "".join(["100", " to ", "120"]),
        "".join(["100", "%", " return"]),
        "".join(["guaranteed ", "return"]),
        "".join(["guaranteed ", "profit"]),
        "".join(["trade ", "now"]),
        "".join(["withdraw ", "now"]),
        "".join(["move ", "money"]),
        "".join(["autonomous ", "withdrawal"]),
        "".join(["autonomous ", "deposit"]),
    ]
    lowered = source_text.lower()
    for pattern in forbidden_patterns:
        assert pattern not in lowered


def test_breaching_compliance_evidence_required_for_live_exception() -> None:
    payload = _base_payload()
    payload["mode"] = MODE_LIVE_REVIEW
    payload["demo_proof"]["demo_proof_ready"] = True
    payload["live_exception"] = {
        "live_review_requested": True,
        "demo_proof_ready": True,
        "owner_live_exception_approval": True,
        "broker_policy_snapshot_current": False,
        "compliance_evidence_complete": False,
        "no_open_risk": True,
        "live_exception_ready": False,
    }
    result = evaluate_capital_operating_program_v2(payload)
    assert result["capital_program_status"] == STATUS_BLOCKED_BY_LIVE_MODE_GATES


def test_all_output_fields_exist() -> None:
    result = evaluate_capital_operating_program_v2(_base_payload())
    required_fields = [
        "schema", "mode", "read_only", "legal_advice_provided", "financial_advice_provided",
        "money_movement_allowed", "bank_access_allowed", "broker_api_allowed", "deposit_allowed",
        "withdrawal_allowed", "ach_allowed", "wire_allowed", "card_transfer_allowed",
        "credential_storage_allowed", "credential_read_allowed", "live_capital_action_authorized",
        "owner_decision_required", "approval_token_required", "capital_program_status",
        "recommended_capital_action", "requested_action_summary", "account_state_summary",
        "bucket_state_summary", "compounding_decision_summary", "broker_policy_summary",
        "rail_cadence_summary", "transfer_history_summary", "open_risk_summary",
        "compliance_summary", "approval_token_summary", "demo_proof_summary",
        "live_exception_summary", "capital_action_plan", "default_failure_prompt",
        "capital_blockers", "owner_action_queue", "next_best_packet", "audit_record", "safety",
    ]
    for key in required_fields:
        assert key in result


def _base_payload() -> dict:
    return {
        "mode": MODE_READ_ONLY_REVIEW,
        "owner_name": "Anthony",
        "requested_action": ACTION_AUTO,
        "as_of_date": "2026-06-30",
        "account_state": {
            "balance": "12000",
            "equity": "12500",
            "month_start_balance": "11000",
            "realized_profit_month": "550",
            "unrealized_pnl": "40",
            "open_positions_count": "0",
            "margin_used": "0",
            "drawdown_pct": "1",
            "daily_loss_pct": "0.5",
            "closed_trade_count_month": "9",
        },
        "bucket_state": {
            "principal_bucket": "9000",
            "profit_bucket": "550",
            "reserve_bucket": "800",
            "tax_reserve_bucket": "200",
            "compounding_bucket": "110",
            "sweep_bucket": "12",
            "stale_bucket_age_days": "1",
        },
        "compounding_policy": {
            "compound_profit_pct": "0.4",
            "sweep_profit_pct": "0.6",
            "reserve_profit_pct": "0.1",
            "min_profit_to_compound": "100",
            "min_profit_to_sweep": "500",
            "max_account_growth_before_sweep_pct": "50",
            "retain_min_equity_buffer_pct": "10",
            "max_drawdown_pct_for_capital_action": "10",
            "max_daily_loss_pct_for_capital_action": "8",
            "require_no_open_positions_for_withdrawal": True,
            "require_no_open_positions_for_deposit": True,
            "bucket_purge_after_days": "20",
            "max_withdrawals_per_month": "4",
            "max_deposits_per_month": "4",
            "withdrawal_cooldown_days": "7",
            "deposit_cooldown_days": "7",
            "withdrawal_cooldown_satisfied": True,
            "deposit_cooldown_satisfied": True,
        },
        "rail_registry": {
            "rail_label": "BANK_ACH",
            "rail_type": "ACH",
            "verification_status": "VERIFIED",
            "rail_allowed_by_policy": True,
            "rail_owner_verified": True,
            "no_sensitive_identifiers_present": True,
        },
        "transfer_history": {
            "withdrawals_this_month": "1",
            "deposits_this_month": "1",
            "last_withdrawal_days_ago": "10",
            "last_deposit_days_ago": "11",
            "last_transfer_status": "COMPLETED",
        },
        "open_risk": {
            "open_positions_count": "0",
            "margin_used": "0",
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "duplicate_order_detected": False,
            "pending_settlement": False,
            "unsettled_pnl": False,
        },
        "broker_policy_snapshot": {
            "broker_name": "OANDA-PAPER",
            "document_title": "Forex policy",
            "policy_source_reference": "policy-2026-06",
            "policy_reviewed_date": "2026-06-10",
            "terms_acknowledged_by_owner": True,
            "max_withdrawals_per_month": "4",
            "withdrawals_used_this_month": "1",
            "max_deposits_per_month": "4",
            "deposits_used_this_month": "1",
            "withdrawal_cooldown_days": "7",
            "deposit_cooldown_days": "7",
            "withdrawal_cooldown_satisfied": True,
            "deposit_cooldown_satisfied": True,
            "settlement_days": "2",
            "jurisdiction": "US",
            "kyc_required": True,
            "tax_review_required": True,
            "allowed_rails": "ACH|WIRE",
            "prohibited_rails": "CARD",
            "estimated_fees": "N/A",
        },
        "compliance_evidence": {
            "terms_acknowledged_by_owner": True,
            "jurisdiction_present": True,
            "kyc_status": "COMPLETE",
            "tax_review_complete": True,
            "policy_source_reference_present": True,
            "user_agreement_reviewed": True,
            "legal_review_required": False,
            "legal_review_complete": False,
        },
        "owner_approval": {
            "owner_approval_required": True,
            "owner_accepts_action": True,
            "owner_accepts_policy_snapshot": True,
            "owner_accepts_risk_state": True,
            "owner_accepts_no_autonomous_money_movement": True,
        },
        "approval_token_evidence": {
            "approval_channel": "TEXT",
            "approval_token_id": "tok-001",
            "approval_phrase_present": True,
            "approval_phrase_matches": True,
            "approval_amount": "550",
            "approval_amount_matches": True,
            "approval_balance_snapshot": "12000",
            "approval_balance_matches": True,
            "approval_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
            "approval_action_matches": True,
            "approval_mode": MODE_READ_ONLY_REVIEW,
            "approval_mode_matches": True,
            "approval_token_unexpired": True,
            "approval_token_unused": True,
            "approval_timestamp_present": True,
            "approval_challenge_hash_present": True,
        },
        "demo_proof": {
            "demo_mode_used": True,
            "simulated_transfer_count": 2,
            "simulated_compound_count": 1,
            "simulated_sweep_count": 1,
            "simulated_block_count": 0,
            "failed_gate_distribution": {},
            "last_demo_result_status": "PASS",
            "demo_proof_ready": True,
        },
        "live_exception": {
            "live_review_requested": False,
            "demo_proof_ready": False,
            "owner_live_exception_approval": False,
            "broker_policy_snapshot_current": False,
            "compliance_evidence_complete": False,
            "no_open_risk": True,
            "live_exception_ready": False,
        },
    }
