"""Demo-only proof harness for the Forex capital operating program."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from automation.forex_engine.capital_operating_program_v2 import (
    ACTION_COMPOUND_IN_ACCOUNT,
    ACTION_NO_TRANSFER,
    ACTION_OWNER_REVIEW_BUCKET_PURGE,
    ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
    ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    evaluate_capital_operating_program_v2,
)

SCHEMA = "AIOS_FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1"
MODE = "READ_ONLY_DEMO_CAPITAL_CADENCE_PROOF"

DEMO_CAPITAL_CADENCE_PROOF_PASSED = "DEMO_CAPITAL_CADENCE_PROOF_PASSED"
DEMO_CAPITAL_CADENCE_PROOF_FAILED = "DEMO_CAPITAL_CADENCE_PROOF_FAILED"
DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS = "DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS"
BLOCKED_BY_UNEXPECTED_CAPITAL_AUTHORITY = "BLOCKED_BY_UNEXPECTED_CAPITAL_AUTHORITY"
BLOCKED_BY_SCENARIO_MISMATCH = "BLOCKED_BY_SCENARIO_MISMATCH"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_LIVE_AUTHORIZATION = "BLOCKED_BY_LIVE_AUTHORIZATION"

DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE = "COMPOUND_ELIGIBLE"
DEMO_SCENARIO_ID_PROFIT_SWEEP_ELIGIBLE = "PROFIT_SWEEP_ELIGIBLE"
DEMO_SCENARIO_ID_DEPOSIT_TOP_UP_OWNER_REVIEW = "DEPOSIT_TOP_UP_OWNER_REVIEW"
DEMO_SCENARIO_ID_BUCKET_PURGE_ELIGIBLE = "BUCKET_PURGE_ELIGIBLE"
DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER = "BELOW_THRESHOLD_NO_TRANSFER"
DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED = "WITHDRAWAL_CADENCE_EXHAUSTED"
DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED = "DEPOSIT_CADENCE_EXHAUSTED"
DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED = "WITHDRAWAL_COOLDOWN_BLOCKED"
DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED = "DEPOSIT_COOLDOWN_BLOCKED"
DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED = "OPEN_POSITION_BLOCKED"
DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED = "MARGIN_USED_BLOCKED"
DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED = "PENDING_SETTLEMENT_BLOCKED"
DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED = "DRAWDOWN_BLOCKED"
DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED = "DAILY_LOSS_STOP_BLOCKED"
DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED = "KILL_SWITCH_BLOCKED"
DEMO_SCENARIO_ID_BROKER_POLICY_MISSING_BLOCKED = "BROKER_POLICY_MISSING_BLOCKED"
DEMO_SCENARIO_ID_TERMS_NOT_ACKNOWLEDGED_BLOCKED = "TERMS_NOT_ACKNOWLEDGED_BLOCKED"
DEMO_SCENARIO_ID_APPROVAL_TOKEN_MISMATCH_BLOCKED = "APPROVAL_TOKEN_MISMATCH_BLOCKED"
DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED = "GENERIC_VOICE_YES_BLOCKED"
DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED = "EXACT_VOICE_TOKEN_ACCEPTED"
DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED = "LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED"
DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY = "LIVE_REVIEW_WITH_DEMO_PROOF_READY_FOR_EXCEPTION"

DEMO_POLICY_BROKER = "DEMO_POLICY_BROKER"
DEMO_POLICY_FIXTURE = "DEMO_POLICY_FIXTURE"

MODE_READ_ONLY_REVIEW = "READ_ONLY_REVIEW"
MODE_DEMO_PROOF = "DEMO_PROOF"
MODE_LIVE_REVIEW = "LIVE_REVIEW"

STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF = "CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF"
STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW = "CAPITAL_ACTION_READY_FOR_OWNER_REVIEW"
STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW = "READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW"
STATUS_BLOCKED_BY_MISSING_POLICY_SNAPSHOT = "BLOCKED_BY_MISSING_POLICY_SNAPSHOT"
STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE = "BLOCKED_BY_COMPLIANCE_EVIDENCE"
STATUS_BLOCKED_BY_TRANSFER_CADENCE = "BLOCKED_BY_TRANSFER_CADENCE"
STATUS_BLOCKED_BY_OPEN_RISK = "BLOCKED_BY_OPEN_RISK"
STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS = "BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS"
STATUS_BLOCKED_BY_PROFIT_THRESHOLD = "BLOCKED_BY_PROFIT_THRESHOLD"
STATUS_BLOCKED_BY_APPROVAL_TOKEN = "BLOCKED_BY_APPROVAL_TOKEN"
STATUS_BLOCKED_BY_DEMO_PROOF = "BLOCKED_BY_DEMO_PROOF"

NEXT_PACKET_PASS = "AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1"
NEXT_PACKET_FAIL = "AIOS_FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1"

REQUIRED_OWNER_ACTION_IDS = (
    "REVIEW_DEMO_SCENARIOS",
    "REVIEW_EXPECTED_STATUS_MATRIX",
    "REVIEW_FAILED_GATE_DISTRIBUTION",
    "REVIEW_ACTION_DISTRIBUTION",
    "REVIEW_LIVE_EXCEPTION_PROBE",
    "REVIEW_SAFETY_HARD_FALSES",
    "REVIEW_NEXT_PACKET",
)

REQUIRED_SCENARIO_OUTCOMES: dict[str, dict[str, str]] = {
    DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE: {
        "expected_status": STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
        "expected_action": ACTION_COMPOUND_IN_ACCOUNT,
    },
    DEMO_SCENARIO_ID_PROFIT_SWEEP_ELIGIBLE: {
        "expected_status": STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_DEPOSIT_TOP_UP_OWNER_REVIEW: {
        "expected_status": STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
        "expected_action": ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
    },
    DEMO_SCENARIO_ID_BUCKET_PURGE_ELIGIBLE: {
        "expected_status": STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
        "expected_action": ACTION_OWNER_REVIEW_BUCKET_PURGE,
    },
    DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER: {
        "expected_status": STATUS_BLOCKED_BY_PROFIT_THRESHOLD,
        "expected_action": ACTION_NO_TRANSFER,
    },
    DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED: {
        "expected_status": STATUS_BLOCKED_BY_TRANSFER_CADENCE,
        "expected_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    },
    DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED: {
        "expected_status": STATUS_BLOCKED_BY_TRANSFER_CADENCE,
        "expected_action": ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
    },
    DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_TRANSFER_CADENCE,
        "expected_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    },
    DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_TRANSFER_CADENCE,
        "expected_action": ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
    },
    DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_OPEN_RISK,
        "expected_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    },
    DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_OPEN_RISK,
        "expected_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    },
    DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_OPEN_RISK,
        "expected_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    },
    DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_BROKER_POLICY_MISSING_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_MISSING_POLICY_SNAPSHOT,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_TERMS_NOT_ACKNOWLEDGED_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_APPROVAL_TOKEN_MISMATCH_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_APPROVAL_TOKEN,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_APPROVAL_TOKEN,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED: {
        "expected_status": STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED: {
        "expected_status": STATUS_BLOCKED_BY_DEMO_PROOF,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
    DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY: {
        "expected_status": STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW,
        "expected_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    },
}

SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "token_value",
    "secret",
    "broker_token",
    "access_token",
)

BOUNDARY_SAFE_KEY_EXCEPTIONS = {
    "approval_token_required",
    "approval_token_present",
    "approval_token_matches",
    "bank_access_allowed",
    "broker_api_allowed",
    "money_movement_allowed",
    "credential_read_allowed",
    "credential_storage_allowed",
    "withdrawal_allowed",
    "deposit_allowed",
    "ach_allowed",
    "wire_allowed",
    "card_transfer_allowed",
    "live_capital_action_authorized",
}

OWNER_REVIEW_TRANSFER_ACTIONS = frozenset(
    {
        ACTION_OWNER_REVIEW_PROFIT_SWEEP,
        ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
        ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
        ACTION_OWNER_REVIEW_BUCKET_PURGE,
    },
)

DEMO_CAPITAL_CADENCE_SCENARIO_COUNT = 21


def run_demo_capital_cadence_proof_v1(payload: dict | None = None) -> dict[str, Any]:
    source = payload if isinstance(payload, Mapping) else {}
    owner_name = _as_text(source.get("owner_name"), "Anthony")
    as_of_date = _as_text(source.get("as_of_date"), _utc_today())
    strict_mode = bool(source.get("strict_mode", True))

    if _contains_sensitive_key(source):
        return _blocked_output(
            status=BLOCKED_BY_SENSITIVE_DATA,
            owner_name=owner_name,
            as_of_date=as_of_date,
            reason="sensitive_data_provided",
            proof_blockers=["sensitive_data_provided"],
            strict_blocked=True,
        )

    scenario_set = _normalize_scenario_set(source.get("scenario_set"))
    if scenario_set is None:
        scenario_set = _build_default_scenarios()
        scenario_set_was_provided = False
    else:
        scenario_set_was_provided = True
        if not scenario_set:
            return _blocked_output(
                status=DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS,
                owner_name=owner_name,
                as_of_date=as_of_date,
                reason="empty_scenario_set",
                proof_blockers=["missing_scenarios"],
                strict_blocked=True,
            )

    base_payload = _build_base_payload(owner_name=owner_name, as_of_date=as_of_date)
    scenario_results: list[dict[str, Any]] = []
    status_counter: Counter[str] = Counter()
    action_counter: Counter[str] = Counter()
    blocker_counter: Counter[str] = Counter()
    proof_mismatch = False
    unexpected_authority = False
    scenario_live_auth = False

    for scenario in scenario_set:
        scenario_id = _as_text(scenario.get("scenario_id"), default="UNSPECIFIED_SCENARIO")
        description = _as_text(scenario.get("description"), default="Demo scenario")
        expected = REQUIRED_SCENARIO_OUTCOMES.get(scenario_id)
        expected_status = _as_text(scenario.get("expected_status"), default=expected.get("expected_status", "") if expected else "")
        expected_action = _as_text(scenario.get("expected_action"), default=expected.get("expected_action", "") if expected else "")

        if (not expected_status or not expected_action) and strict_mode:
            proof_mismatch = True
            if not expected_status:
                expected_status = "MISSING_EXPECTED_STATUS"
            if not expected_action:
                expected_action = "MISSING_EXPECTED_ACTION"

        scenario_payload = _extract_scenario_payload(scenario)
        scenario_payload = _deep_merge(base_payload, scenario_payload)

        requested_action = _as_text(scenario_payload.get("requested_action"), default=ACTION_NO_TRANSFER)
        requested_mode = _as_text(scenario_payload.get("mode"), default=MODE_READ_ONLY_REVIEW)
        scenario_payload["requested_action"] = requested_action
        scenario_payload["mode"] = requested_mode
        _inject_owner_gate_metadata(
            scenario_payload,
            owner_name=owner_name,
            action=requested_action,
            mode=requested_mode,
        )

        if scenario_id == DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED:
            scenario_payload["mode"] = MODE_LIVE_REVIEW
            scenario_payload["demo_proof"] = {"demo_proof_ready": False}
            scenario_payload.setdefault("live_exception", {})
            scenario_payload["live_exception"].update(
                {
                    "live_review_requested": True,
                    "owner_live_exception_approval": True,
                },
            )

        if scenario_id == DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY:
            scenario_payload["mode"] = MODE_LIVE_REVIEW
            scenario_payload["demo_proof"] = {"demo_proof_ready": True}
            scenario_payload.setdefault("live_exception", {})
            scenario_payload["live_exception"].update(
                {
                    "live_review_requested": True,
                    "owner_live_exception_approval": True,
                    "broker_policy_snapshot_current": True,
                    "compliance_evidence_complete": True,
                    "no_open_risk": True,
                    "live_exception_ready": True,
                },
            )

        result = evaluate_capital_operating_program_v2(scenario_payload)

        actual_status = _as_text(result.get("capital_program_status"))
        actual_action = _as_text(result.get("recommended_capital_action"))
        status_counter[actual_status] += 1
        action_counter[actual_action] += 1
        blocker_counter[f"status:{actual_status}"] += 1

        scenario_blockers = _as_sequence_text(result.get("capital_blockers"))
        for blocker in scenario_blockers:
            blocker_counter[f"blocker:{blocker}"] += 1

        unexpected = _has_unexpected_authority(result)
        live_authorized = _as_bool(result.get("live_capital_action_authorized"), default=False)
        unexpected_authority = unexpected_authority or unexpected
        scenario_live_auth = scenario_live_auth or live_authorized

        status_match = _match_expected_status(expected_status, actual_status)
        action_match = _match_expected_action(expected_action, actual_action)
        passed = status_match and action_match and not unexpected and not live_authorized
        if not passed:
            proof_mismatch = True

        scenario_results.append(
            {
                "scenario_id": scenario_id,
                "description": description,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "expected_action": expected_action,
                "actual_action": actual_action,
                "passed": passed,
                "capital_blockers": scenario_blockers,
                "next_best_packet": result.get("next_best_packet", NEXT_PACKET_FAIL),
                "safety_snapshot": _snapshot_from_program_result(result),
            },
        )

    if scenario_live_auth:
        demo_status = BLOCKED_BY_LIVE_AUTHORIZATION
        proof_passed = False
        proof_blockers = ["live_capital_action_authorized_in_result"]
    elif unexpected_authority:
        demo_status = BLOCKED_BY_UNEXPECTED_CAPITAL_AUTHORITY
        proof_passed = False
        proof_blockers = ["unexpected_capital_authority"]
    elif proof_mismatch:
        demo_status = DEMO_CAPITAL_CADENCE_PROOF_FAILED
        proof_passed = False
        proof_blockers = [BLOCKED_BY_SCENARIO_MISMATCH]
    elif not scenario_set_was_provided and len(scenario_results) < 20:
        demo_status = DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS
        proof_passed = False
        proof_blockers = ["scenario_count_below_minimum"]
    elif scenario_set_was_provided and strict_mode and len(scenario_results) < 20:
        demo_status = DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS
        proof_passed = False
        proof_blockers = ["scenario_count_below_minimum"]
    else:
        demo_status = DEMO_CAPITAL_CADENCE_PROOF_PASSED
        proof_passed = True
        proof_blockers = []

    if not demo_status == DEMO_CAPITAL_CADENCE_PROOF_PASSED:
        proof_passed = False

    demo_transfer_count = sum(
        count for action, count in action_counter.items() if action in OWNER_REVIEW_TRANSFER_ACTIONS
    )
    demo_compound_count = action_counter.get(ACTION_COMPOUND_IN_ACCOUNT, 0)
    demo_sweep_count = action_counter.get(ACTION_OWNER_REVIEW_PROFIT_SWEEP, 0)
    demo_block_count = sum(1 for result in scenario_results if result["actual_status"].startswith("BLOCKED_"))

    live_exception_probe = {
        result["scenario_id"]: {
            "actual_status": result["actual_status"],
            "actual_action": result["actual_action"],
            "safety_snapshot": result["safety_snapshot"],
        }
        for result in scenario_results
        if result["scenario_id"].startswith("LIVE_REVIEW_")
    }

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "demo_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "live_capital_action_authorized": False,
        "demo_proof_status": demo_status,
        "scenario_count": len(scenario_results),
        "scenario_results": scenario_results,
        "expected_status_summary": dict(Counter(r["expected_status"] for r in scenario_results)),
        "failed_gate_distribution": dict(blocker_counter),
        "simulated_action_distribution": dict(action_counter),
        "demo_transfer_count": demo_transfer_count,
        "demo_compound_count": demo_compound_count,
        "demo_sweep_count": demo_sweep_count,
        "demo_block_count": demo_block_count,
        "live_exception_probe": live_exception_probe,
        "proof_passed": proof_passed,
        "proof_blockers": proof_blockers,
        "owner_action_queue": _build_owner_action_queue(proof_blockers=proof_blockers),
        "next_best_packet": NEXT_PACKET_PASS if proof_passed else NEXT_PACKET_FAIL,
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "owner_name": owner_name,
            "as_of_date": as_of_date,
            "scenario_count": len(scenario_results),
            "proof_passed": proof_passed,
            "demo_proof_status": demo_status,
        },
        "safety": {
            "read_only": True,
            "demo_only": True,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "credential_storage_allowed": False,
            "credential_read_allowed": False,
            "live_capital_action_authorized": False,
            "demo_proof_required_before_live": True,
            "broker_policy_snapshot_required": True,
            "owner_gate_required": True,
            "approval_token_required": True,
            "fixed_return_target_promised": False,
            "profit_claim_authorized": False,
        },
    }


def _build_owner_action_queue(*, proof_blockers: Sequence[str]) -> list[dict[str, Any]]:
    return [
        {
            "owner_action_id": owner_action_id,
            "owner_decision_required": True,
            "money_movement_allowed": False,
            "live_capital_action_authorized": False,
            "safe_action": "Review scenario outcome and evidence boundaries.",
            "blocked_by": list(proof_blockers),
        }
        for owner_action_id in REQUIRED_OWNER_ACTION_IDS
    ]


def _build_base_payload(*, owner_name: str, as_of_date: str) -> dict[str, Any]:
    return {
        "mode": MODE_READ_ONLY_REVIEW,
        "as_of_date": as_of_date,
        "owner_name": owner_name,
        "requested_action": ACTION_NO_TRANSFER,
        "account_state": {
            "balance": 10000,
            "equity": 10000,
            "month_start_balance": 9000,
            "realized_profit_month": 500,
            "unrealized_pnl": 0,
            "open_positions_count": 0,
            "margin_used": 0,
            "drawdown_pct": 3,
            "daily_loss_pct": 1,
            "closed_trade_count_month": 10,
        },
        "bucket_state": {
            "principal_bucket": 8200,
            "profit_bucket": 500,
            "reserve_bucket": 800,
            "tax_reserve_bucket": 200,
            "compounding_bucket": 300,
            "sweep_bucket": 0,
            "stale_bucket_age_days": 2,
        },
        "compounding_policy": {
            "compound_profit_pct": 50,
            "sweep_profit_pct": 70,
            "reserve_profit_pct": 70,
            "min_profit_to_compound": 100,
            "min_profit_to_sweep": 300,
            "max_account_growth_before_sweep_pct": 25,
            "retain_min_equity_buffer_pct": 30,
            "max_drawdown_pct_for_capital_action": 15,
            "max_daily_loss_pct_for_capital_action": 10,
            "require_no_open_positions_for_withdrawal": True,
            "require_no_open_positions_for_deposit": True,
            "bucket_purge_after_days": 30,
        },
        "broker_policy_snapshot": {
            "broker_name": DEMO_POLICY_BROKER,
            "document_title": "DEMO POLICY SNAPSHOT",
            "policy_source_reference": DEMO_POLICY_FIXTURE,
            "policy_reviewed_date": "2026-06-01",
            "terms_acknowledged_by_owner": True,
            "max_withdrawals_per_month": 4,
            "withdrawals_used_this_month": 1,
            "max_deposits_per_month": 5,
            "deposits_used_this_month": 1,
            "min_withdrawal_amount": 100,
            "min_deposit_amount": 100,
            "withdrawal_cooldown_days": 7,
            "deposit_cooldown_days": 7,
            "withdrawal_cooldown_satisfied": True,
            "deposit_cooldown_satisfied": True,
            "settlement_days": 2,
            "allowed_rails": ["DEMO_WIRE"],
            "prohibited_rails": [],
            "estimated_fees": 0,
            "jurisdiction": "US",
            "kyc_required": False,
            "tax_review_required": False,
        },
        "rail_registry": [
            {
                "rail_label": "DEMO_WIRE",
                "rail_type": "wire",
                "verification_status": "verified",
                "rail_allowed_by_policy": True,
                "rail_owner_verified": True,
                "no_sensitive_identifiers_present": True,
            },
        ],
        "transfer_history": {
            "withdrawals_this_month": 1,
            "deposits_this_month": 1,
            "last_withdrawal_days_ago": 14,
            "last_deposit_days_ago": 14,
            "last_transfer_status": "settled",
        },
        "open_risk": {
            "open_positions_count": 0,
            "margin_used": 0,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "duplicate_order_detected": False,
            "pending_settlement": False,
            "unsettled_pnl": False,
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
        "approval_token_evidence": {
            "approval_channel": "TEXT",
            "approval_token_id": "DEMO-TOKEN-001",
            "approval_phrase_present": True,
            "approval_phrase_matches": True,
            "approval_amount": 560,
            "approval_amount_matches": True,
            "approval_balance_snapshot": 10000,
            "approval_balance_matches": True,
            "approval_action": ACTION_NO_TRANSFER,
            "approval_action_matches": True,
            "approval_mode": MODE_READ_ONLY_REVIEW,
            "approval_mode_matches": True,
            "approval_token_unexpired": True,
            "approval_token_unused": True,
            "approval_timestamp_present": True,
            "approval_challenge_hash_present": True,
            "owner_cancel_phrase_detected": False,
        },
        "owner_approval": {
            "owner_name": owner_name,
            "owner_approval_required": True,
            "owner_accepts_action": True,
            "owner_accepts_policy_snapshot": True,
            "owner_accepts_risk_state": True,
            "owner_accepts_no_autonomous_money_movement": True,
        },
        "demo_proof": {
            "demo_mode_used": True,
            "simulated_transfer_count": 0,
            "simulated_compound_count": 0,
            "simulated_sweep_count": 0,
            "simulated_block_count": 0,
            "failed_gate_distribution": {},
            "last_demo_result_status": "READY",
            "demo_proof_ready": True,
        },
        "live_exception": {
            "live_review_requested": False,
            "demo_proof_ready": True,
            "owner_live_exception_approval": False,
            "broker_policy_snapshot_current": False,
            "compliance_evidence_complete": False,
            "no_open_risk": False,
            "live_exception_ready": False,
        },
    }


def _build_default_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "scenario_id": DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE,
            "description": "Compounding is eligible.",
            "payload": {
                "requested_action": "AUTO",
                "account_state": {"realized_profit_month": 250},
                "bucket_state": {"profit_bucket": 150},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_PROFIT_SWEEP_ELIGIBLE,
            "description": "Sweep-eligible profit should route owner review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "account_state": {"realized_profit_month": 900},
                "bucket_state": {"profit_bucket": 450},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_PROFIT_SWEEP_ELIGIBLE],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_DEPOSIT_TOP_UP_OWNER_REVIEW,
            "description": "Deposit top-up should be owner review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
                "transfer_history": {"deposits_this_month": 1},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_DEPOSIT_TOP_UP_OWNER_REVIEW],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_BUCKET_PURGE_ELIGIBLE,
            "description": "Bucket purge is eligible by stale bucket age.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_BUCKET_PURGE,
                "bucket_state": {"stale_bucket_age_days": 45},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_BUCKET_PURGE_ELIGIBLE],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER,
            "description": "Below threshold results in no-transfer.",
            "payload": {
                "requested_action": "AUTO",
                "account_state": {"realized_profit_month": 10},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED,
            "description": "Withdrawal cadence exhausted blocks withdraw.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
                "transfer_history": {"withdrawals_this_month": 1},
                "broker_policy_snapshot": {"max_withdrawals_per_month": 1, "withdrawals_used_this_month": 1},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED,
            "description": "Deposit cadence exhausted blocks deposit top-up.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
                "transfer_history": {"deposits_this_month": 1},
                "broker_policy_snapshot": {"max_deposits_per_month": 1, "deposits_used_this_month": 1},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED,
            "description": "Withdrawal cooldown blocks withdraw.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
                "broker_policy_snapshot": {"withdrawal_cooldown_satisfied": False},
                "transfer_history": {"last_withdrawal_days_ago": 1},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED,
            "description": "Deposit cooldown blocks deposit top-up.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
                "broker_policy_snapshot": {"deposit_cooldown_satisfied": False},
                "transfer_history": {"last_deposit_days_ago": 1},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED,
            "description": "Open position blocks withdraw review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
                "open_risk": {"open_positions_count": 2},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED,
            "description": "Margin usage blocks withdraw review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
                "open_risk": {"margin_used": 120},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED,
            "description": "Pending settlement blocks withdraw review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
                "open_risk": {"pending_settlement": True},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED,
            "description": "Drawdown gate blocks review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "account_state": {"drawdown_pct": 99},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED,
            "description": "Daily loss stop blocks review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "open_risk": {"daily_loss_stop_active": True},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED,
            "description": "Kill switch blocks review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "open_risk": {"kill_switch_active": True},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_BROKER_POLICY_MISSING_BLOCKED,
            "description": "Missing policy snapshot blocks.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "broker_policy_snapshot": None,
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_BROKER_POLICY_MISSING_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_TERMS_NOT_ACKNOWLEDGED_BLOCKED,
            "description": "Terms not acknowledged blocks review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "broker_policy_snapshot": {"terms_acknowledged_by_owner": False},
                "compliance_evidence": {"terms_acknowledged_by_owner": False},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_TERMS_NOT_ACKNOWLEDGED_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_APPROVAL_TOKEN_MISMATCH_BLOCKED,
            "description": "Approval-token mismatch blocks review.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "approval_token_evidence": {"approval_phrase_matches": False},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_APPROVAL_TOKEN_MISMATCH_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED,
            "description": "Generic voice confirmation is not accepted.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "approval_token_evidence": {
                    "approval_channel": "VOICE",
                    "approval_phrase_present": True,
                    "approval_phrase_matches": False,
                },
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED,
            "description": "Exact voice token metadata is accepted.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "approval_token_evidence": {
                    "approval_channel": "VOICE",
                    "approval_phrase_present": True,
                    "approval_phrase_matches": True,
                    "approval_amount_matches": True,
                    "approval_balance_matches": True,
                    "approval_action_matches": True,
                    "approval_mode_matches": True,
                    "approval_token_unexpired": True,
                    "approval_token_unused": True,
                    "approval_timestamp_present": True,
                    "approval_challenge_hash_present": True,
                    "owner_cancel_phrase_detected": False,
                },
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED,
            "description": "Live review without proof is blocked.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "demo_proof": {"demo_proof_ready": False},
                "approval_token_evidence": {
                    "approval_channel": "TEXT",
                    "approval_mode_matches": True,
                    "approval_action_matches": True,
                    "approval_mode": MODE_LIVE_REVIEW,
                    "approval_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                },
                "live_exception": {
                    "live_review_requested": True,
                    "owner_live_exception_approval": True,
                },
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED],
        },
        {
            "scenario_id": DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY,
            "description": "Live review with demo proof can move to exception packet.",
            "payload": {
                "requested_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                "demo_proof": {"demo_proof_ready": True},
                "approval_token_evidence": {
                    "approval_channel": "TEXT",
                    "approval_mode": MODE_LIVE_REVIEW,
                    "approval_mode_matches": True,
                    "approval_action_matches": True,
                    "approval_action": ACTION_OWNER_REVIEW_PROFIT_SWEEP,
                },
                "live_exception": {
                    "live_review_requested": True,
                    "owner_live_exception_approval": True,
                    "broker_policy_snapshot_current": True,
                    "compliance_evidence_complete": True,
                    "no_open_risk": True,
                    "live_exception_ready": True,
                },
                "broker_policy_snapshot": {"policy_source_reference": DEMO_POLICY_FIXTURE},
                "compliance_evidence": {"legal_review_required": False},
            },
            **REQUIRED_SCENARIO_OUTCOMES[DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY],
        },
    ]


def _normalize_scenario_set(value: Any) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _extract_scenario_payload(scenario: Mapping[str, Any]) -> dict[str, Any]:
    reserved = {"scenario_id", "description", "expected_status", "expected_action"}
    payload = scenario.get("payload")
    if isinstance(payload, Mapping):
        return dict(payload)
    payload_updates = scenario.get("payload_updates")
    if isinstance(payload_updates, Mapping):
        return dict(payload_updates)
    extracted = dict(scenario)
    for key in reserved:
        extracted.pop(key, None)
    return extracted


def _inject_owner_gate_metadata(
    payload: dict[str, Any],
    *,
    owner_name: str,
    action: str,
    mode: str,
) -> None:
    owner_approval = payload.get("owner_approval")
    if not isinstance(owner_approval, Mapping):
        owner_approval = {}
    owner_approval = {
        **{
            "owner_name": owner_name,
            "owner_approval_required": True,
            "owner_accepts_action": True,
            "owner_accepts_policy_snapshot": True,
            "owner_accepts_risk_state": True,
            "owner_accepts_no_autonomous_money_movement": True,
        },
        **dict(owner_approval),
    }
    payload["owner_approval"] = owner_approval

    approval_token_evidence = payload.get("approval_token_evidence")
    if not isinstance(approval_token_evidence, Mapping):
        approval_token_evidence = {}
    account_balance = _as_text(payload.get("account_state", {}).get("balance"), default="10000")
    merged = {
        "approval_channel": "TEXT",
        "approval_token_id": "DEMO-TOKEN-001",
        "approval_phrase_present": True,
        "approval_phrase_matches": True,
        "approval_amount": 560,
        "approval_amount_matches": True,
        "approval_balance_snapshot": account_balance,
        "approval_balance_matches": True,
        "approval_action": action,
        "approval_action_matches": True,
        "approval_mode": mode,
        "approval_mode_matches": True,
        "approval_token_unexpired": True,
        "approval_token_unused": True,
        "approval_timestamp_present": True,
        "approval_challenge_hash_present": True,
        "owner_cancel_phrase_detected": False,
    }
    merged.update(dict(approval_token_evidence))
    payload["approval_token_evidence"] = merged


def _has_unexpected_authority(program_result: Mapping[str, Any]) -> bool:
    return (
        _as_bool(program_result.get("money_movement_allowed"), default=False)
        or _as_bool(program_result.get("bank_access_allowed"), default=False)
        or _as_bool(program_result.get("broker_api_allowed"), default=False)
        or _as_bool(program_result.get("credential_storage_allowed"), default=False)
        or _as_bool(program_result.get("credential_read_allowed"), default=False)
        or _as_bool(program_result.get("live_capital_action_authorized"), default=False)
    )


def _snapshot_from_program_result(program_result: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "read_only": _as_bool(program_result.get("read_only"), default=True),
        "money_movement_allowed": _as_bool(program_result.get("money_movement_allowed"), default=False),
        "bank_access_allowed": _as_bool(program_result.get("bank_access_allowed"), default=False),
        "broker_api_allowed": _as_bool(program_result.get("broker_api_allowed"), default=False),
        "credential_storage_allowed": _as_bool(program_result.get("credential_storage_allowed"), default=False),
        "credential_read_allowed": _as_bool(program_result.get("credential_read_allowed"), default=False),
        "live_capital_action_authorized": _as_bool(program_result.get("live_capital_action_authorized"), default=False),
    }


def _match_expected_status(expected_status: str, actual_status: str) -> bool:
    if expected_status == "ANY_BLOCKED":
        return actual_status.startswith("BLOCKED_")
    return expected_status == actual_status


def _match_expected_action(expected_action: str, actual_action: str) -> bool:
    if expected_action == "ANY_BLOCKED":
        return actual_action in OWNER_REVIEW_TRANSFER_ACTIONS or actual_action == ACTION_NO_TRANSFER
    return expected_action == actual_action


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                continue
            lowered = key.lower()
            if lowered in BOUNDARY_SAFE_KEY_EXCEPTIONS:
                continue
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(nested):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            if _contains_sensitive_key(item):
                return True
    return False


def _as_sequence_text(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_as_text(item) for item in value]
    return []


def _as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value != 0
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "on", "y"}:
        return True
    if normalized in {"false", "0", "no", "off", "n"}:
        return False
    return default


def _deep_merge(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(left))
    for key, value in right.items():
        if key in result and isinstance(result[key], Mapping) and isinstance(value, Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _blocked_output(
    *,
    status: str,
    owner_name: str,
    as_of_date: str,
    reason: str,
    proof_blockers: list[str],
    strict_blocked: bool,
) -> dict[str, Any]:
    blockers = list(proof_blockers)
    if reason:
        blockers.append(reason)
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "demo_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "live_capital_action_authorized": False,
        "demo_proof_status": status,
        "scenario_count": 0,
        "scenario_results": [],
        "expected_status_summary": {},
        "failed_gate_distribution": {status: 1},
        "simulated_action_distribution": {},
        "demo_transfer_count": 0,
        "demo_compound_count": 0,
        "demo_sweep_count": 0,
        "demo_block_count": 0,
        "live_exception_probe": {},
        "proof_passed": False,
        "proof_blockers": blockers,
        "owner_action_queue": _build_owner_action_queue(proof_blockers=blockers),
        "next_best_packet": NEXT_PACKET_FAIL,
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "owner_name": owner_name,
            "as_of_date": as_of_date,
            "scenario_count": 0,
            "proof_passed": False,
            "demo_proof_status": status,
            "strict_mode": strict_blocked,
        },
        "safety": {
            "read_only": True,
            "demo_only": True,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "credential_storage_allowed": False,
            "credential_read_allowed": False,
            "live_capital_action_authorized": False,
            "demo_proof_required_before_live": True,
            "broker_policy_snapshot_required": True,
            "owner_gate_required": True,
            "approval_token_required": True,
            "fixed_return_target_promised": False,
            "profit_claim_authorized": False,
        },
    }


__all__ = [
    "SCHEMA",
    "MODE",
    "DEMO_CAPITAL_CADENCE_PROOF_PASSED",
    "DEMO_CAPITAL_CADENCE_PROOF_FAILED",
    "DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS",
    "BLOCKED_BY_UNEXPECTED_CAPITAL_AUTHORITY",
    "BLOCKED_BY_SCENARIO_MISMATCH",
    "BLOCKED_BY_SENSITIVE_DATA",
    "BLOCKED_BY_LIVE_AUTHORIZATION",
    "run_demo_capital_cadence_proof_v1",
    "REQUIRED_SCENARIO_OUTCOMES",
    "REQUIRED_OWNER_ACTION_IDS",
    "DEMO_CAPITAL_CADENCE_SCENARIO_COUNT",
    "NEXT_PACKET_PASS",
    "NEXT_PACKET_FAIL",
    "DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE",
    "DEMO_SCENARIO_ID_PROFIT_SWEEP_ELIGIBLE",
    "DEMO_SCENARIO_ID_DEPOSIT_TOP_UP_OWNER_REVIEW",
    "DEMO_SCENARIO_ID_BUCKET_PURGE_ELIGIBLE",
    "DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER",
    "DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED",
    "DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED",
    "DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED",
    "DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED",
    "DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED",
    "DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED",
    "DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED",
    "DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED",
    "DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED",
    "DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED",
    "DEMO_SCENARIO_ID_BROKER_POLICY_MISSING_BLOCKED",
    "DEMO_SCENARIO_ID_TERMS_NOT_ACKNOWLEDGED_BLOCKED",
    "DEMO_SCENARIO_ID_APPROVAL_TOKEN_MISMATCH_BLOCKED",
    "DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED",
    "DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED",
    "DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED",
    "DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY",
    "STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW",
    "STATUS_BLOCKED_BY_TRANSFER_CADENCE",
    "STATUS_BLOCKED_BY_OPEN_RISK",
    "STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS",
    "STATUS_BLOCKED_BY_PROFIT_THRESHOLD",
    "STATUS_BLOCKED_BY_MISSING_POLICY_SNAPSHOT",
    "STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE",
    "STATUS_BLOCKED_BY_APPROVAL_TOKEN",
    "STATUS_BLOCKED_BY_DEMO_PROOF",
    "ACTION_COMPOUND_IN_ACCOUNT",
    "ACTION_OWNER_REVIEW_PROFIT_SWEEP",
    "ACTION_OWNER_REVIEW_WITHDRAW_PROFIT",
    "ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP",
    "ACTION_OWNER_REVIEW_BUCKET_PURGE",
    "ACTION_NO_TRANSFER",
]
