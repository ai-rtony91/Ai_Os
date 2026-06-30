"""Read-only Forex capital operating decision engine."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

SCHEMA = "AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2"
MODE = "READ_ONLY_FOREX_CAPITAL_OPERATING_PROGRAM"

MODE_READ_ONLY_REVIEW = "READ_ONLY_REVIEW"
MODE_DEMO_PROOF = "DEMO_PROOF"
MODE_LIVE_REVIEW = "LIVE_REVIEW"

ACTION_AUTO = "AUTO"
ACTION_NO_TRANSFER = "NO_TRANSFER"
ACTION_COMPOUND_IN_ACCOUNT = "COMPOUND_IN_ACCOUNT"
ACTION_OWNER_REVIEW_PROFIT_SWEEP = "OWNER_REVIEW_PROFIT_SWEEP"
ACTION_OWNER_REVIEW_WITHDRAW_PROFIT = "OWNER_REVIEW_WITHDRAW_PROFIT"
ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP = "OWNER_REVIEW_DEPOSIT_TOP_UP"
ACTION_OWNER_REVIEW_RESERVE_REALLOCATION = "OWNER_REVIEW_RESERVE_REALLOCATION"
ACTION_OWNER_REVIEW_BUCKET_PURGE = "OWNER_REVIEW_BUCKET_PURGE"

TRANSFER_LIKE_ACTIONS = {
    ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
    ACTION_OWNER_REVIEW_RESERVE_REALLOCATION,
    ACTION_OWNER_REVIEW_BUCKET_PURGE,
}
SWEEP_WITHDRAW_ACTIONS = {
    ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
    ACTION_OWNER_REVIEW_RESERVE_REALLOCATION,
    ACTION_OWNER_REVIEW_BUCKET_PURGE,
}
DEPOSIT_ACTIONS = {ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP}

STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF = "CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF"
STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW = "CAPITAL_ACTION_READY_FOR_OWNER_REVIEW"
STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW = "READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW"
STATUS_NO_CAPITAL_ACTION_RECOMMENDED = "NO_CAPITAL_ACTION_RECOMMENDED"
STATUS_BLOCKED_BY_MISSING_POLICY_SNAPSHOT = "BLOCKED_BY_MISSING_POLICY_SNAPSHOT"
STATUS_BLOCKED_BY_BROKER_POLICY = "BLOCKED_BY_BROKER_POLICY"
STATUS_BLOCKED_BY_TRANSFER_CADENCE = "BLOCKED_BY_TRANSFER_CADENCE"
STATUS_BLOCKED_BY_OPEN_RISK = "BLOCKED_BY_OPEN_RISK"
STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS = "BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS"
STATUS_BLOCKED_BY_PROFIT_THRESHOLD = "BLOCKED_BY_PROFIT_THRESHOLD"
STATUS_BLOCKED_BY_OWNER_APPROVAL = "BLOCKED_BY_OWNER_APPROVAL"
STATUS_BLOCKED_BY_APPROVAL_TOKEN = "BLOCKED_BY_APPROVAL_TOKEN"
STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE = "BLOCKED_BY_COMPLIANCE_EVIDENCE"
STATUS_BLOCKED_BY_DEMO_PROOF = "BLOCKED_BY_DEMO_PROOF"
STATUS_BLOCKED_BY_LIVE_MODE_GATES = "BLOCKED_BY_LIVE_MODE_GATES"
STATUS_BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
STATUS_INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_DEFAULT = "AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2"
NEXT_PACKET_DEMO_PROOF = "AIOS_FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1"
NEXT_PACKET_OWNER_REVIEW = "AIOS_FOREX_OWNER_REVIEW_CAPITAL_ACTION_PACKET_V1"
NEXT_PACKET_LIVE_EXCEPTION = "AIOS_FOREX_LIVE_CAPITAL_RAIL_EXCEPTION_GATE_V1"

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

BLOCKED_STATUS_SET = {
    STATUS_BLOCKED_BY_MISSING_POLICY_SNAPSHOT,
    STATUS_BLOCKED_BY_BROKER_POLICY,
    STATUS_BLOCKED_BY_TRANSFER_CADENCE,
    STATUS_BLOCKED_BY_OPEN_RISK,
    STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS,
    STATUS_BLOCKED_BY_PROFIT_THRESHOLD,
    STATUS_BLOCKED_BY_OWNER_APPROVAL,
    STATUS_BLOCKED_BY_APPROVAL_TOKEN,
    STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE,
    STATUS_BLOCKED_BY_DEMO_PROOF,
    STATUS_BLOCKED_BY_LIVE_MODE_GATES,
    STATUS_BLOCKED_BY_DATA_QUALITY,
    STATUS_INCOMPLETE_INPUTS,
}

REQUIRED_OWNER_ACTION_IDS = (
    "REVIEW_ACCOUNT_STATE",
    "REVIEW_BUCKET_STATE",
    "REVIEW_COMPOUNDING_POLICY",
    "REVIEW_BROKER_POLICY_SNAPSHOT",
    "REVIEW_RAIL_REGISTRY",
    "REVIEW_TRANSFER_CADENCE",
    "REVIEW_OPEN_RISK",
    "REVIEW_COMPLIANCE_EVIDENCE",
    "REVIEW_APPROVAL_TOKEN",
    "REVIEW_DEMO_PROOF",
    "REVIEW_LIVE_EXCEPTION",
    "REVIEW_DEFAULT_FAILURE_PROMPT",
    "REVIEW_NEXT_PACKET",
)


def evaluate_capital_operating_program_v2(payload: dict | None = None) -> dict[str, Any]:
    source = payload if isinstance(payload, Mapping) else {}
    owner_name = _as_text(source.get("owner_name"), default="Anthony")
    mode = _normalize_mode(source.get("mode"))
    requested_raw = source.get("requested_action", ACTION_AUTO)
    requested_action = _normalize_requested_action(requested_raw)

    if _contains_sensitive_key(source):
        return _blocked_output(
            source=source,
            owner_name=owner_name,
            mode=mode,
            requested_action=requested_raw,
            status=STATUS_BLOCKED_BY_DATA_QUALITY,
            blockers=["sensitive_data_provided"],
            missing_evidence=["sensitive data was provided and must be removed"],
            policy_source_reference="NONE",
            approval_gate=_empty_approval_gate(),
            approval_action=requested_action,
        )

    account_state = _as_mapping(source.get("account_state"))
    bucket_state = _as_mapping(source.get("bucket_state"))
    compounding_policy = _as_mapping(source.get("compounding_policy"))
    broker_policy_snapshot = _as_mapping(source.get("broker_policy_snapshot"))
    transfer_history = _as_mapping(source.get("transfer_history"))
    open_risk = _as_mapping(source.get("open_risk"))
    compliance_evidence = _as_mapping(source.get("compliance_evidence"))
    owner_approval = _as_mapping(source.get("owner_approval"))
    approval_token_evidence = _as_mapping(source.get("approval_token_evidence"))
    demo_proof = _as_mapping(source.get("demo_proof"))
    live_exception = _as_mapping(source.get("live_exception"))
    rail_registry = _as_mapping(source.get("rail_registry"))

    missing_inputs = _collect_missing_core_inputs(
        account_state=account_state,
        bucket_state=bucket_state,
        compounding_policy=compounding_policy,
        open_risk=open_risk,
        owner_approval=owner_approval,
    )
    if missing_inputs:
        return _blocked_output(
            source=source,
            owner_name=owner_name,
            mode=mode,
            requested_action=requested_raw,
            status=STATUS_INCOMPLETE_INPUTS,
            blockers=missing_inputs,
            missing_evidence=missing_inputs,
            policy_source_reference="NONE",
            approval_gate=_empty_approval_gate(),
            approval_action=requested_action,
        )

    realized_profit_month = _to_decimal(account_state.get("realized_profit_month"), Decimal("0"))
    min_profit_to_compound = _to_decimal(compounding_policy.get("min_profit_to_compound"), Decimal("0"))
    min_profit_to_sweep = _to_decimal(compounding_policy.get("min_profit_to_sweep"), Decimal("0"))
    profit_bucket = _to_decimal(bucket_state.get("profit_bucket"), Decimal("0"))

    derived_action, derived_status = _derive_recommendation(
        realized_profit_month=realized_profit_month,
        min_profit_to_compound=min_profit_to_compound,
        min_profit_to_sweep=min_profit_to_sweep,
        profit_bucket=profit_bucket,
    )
    action = derived_action if requested_action == ACTION_AUTO else requested_action
    status = derived_status

    stale_bucket_age_days = _to_int(bucket_state.get("stale_bucket_age_days"), default=0)
    bucket_purge_after_days = _to_int(compounding_policy.get("bucket_purge_after_days"), default=30)
    if (
        action != ACTION_NO_TRANSFER
        and stale_bucket_age_days >= bucket_purge_after_days
        and bucket_purge_after_days > 0
    ):
        action = ACTION_OWNER_REVIEW_BUCKET_PURGE
        if status in {STATUS_NO_CAPITAL_ACTION_RECOMMENDED, ""}:
            status = ""

    capital_blockers: list[str] = []

    if status == "":
        action_is_transfer_like = action in TRANSFER_LIKE_ACTIONS
        if action_is_transfer_like:
            blockers = _evaluate_drawdown_gate(
                open_risk=open_risk,
                account_state=account_state,
                compounding_policy=compounding_policy,
            )
            if blockers:
                capital_blockers.extend(blockers)
                status = STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS
            else:
                if not broker_policy_snapshot:
                    capital_blockers.append("broker_policy_snapshot_missing")
                    status = STATUS_BLOCKED_BY_MISSING_POLICY_SNAPSHOT
                else:
                    compliance_gate = _evaluate_compliance_gate(
                        broker_policy_snapshot=broker_policy_snapshot,
                        compliance_evidence=compliance_evidence,
                    )
                    if compliance_gate:
                        capital_blockers.extend(compliance_gate)
                        status = STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE
                    else:
                        cadence_gate = _evaluate_transfer_cadence_gate(
                            action=action,
                            compounding_policy=compounding_policy,
                            broker_policy_snapshot=broker_policy_snapshot,
                            transfer_history=transfer_history,
                        )
                        if cadence_gate:
                            capital_blockers.extend(cadence_gate)
                            status = STATUS_BLOCKED_BY_TRANSFER_CADENCE
                        else:
                            open_risk_gate = _evaluate_open_risk_gate(
                                action=action,
                                open_risk=open_risk,
                                compounding_policy=compounding_policy,
                            )
                            if open_risk_gate:
                                capital_blockers.extend(open_risk_gate)
                                status = STATUS_BLOCKED_BY_OPEN_RISK

        elif action == ACTION_NO_TRANSFER:
            pass
        else:
            blockers = _evaluate_drawdown_gate(
                open_risk=open_risk,
                account_state=account_state,
                compounding_policy=compounding_policy,
            )
            if blockers:
                capital_blockers.extend(blockers)
                status = STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS

    approval_gate = _evaluate_approval_gate(
        owner_name=owner_name,
        action=action,
        owner_approval=owner_approval,
        approval_token_evidence=approval_token_evidence,
        mode=mode,
    )
    if action != ACTION_NO_TRANSFER and status not in BLOCKED_STATUS_SET:
        if not approval_gate["owner_approval_passed"]:
            capital_blockers.append("owner_approval_failed")
            status = STATUS_BLOCKED_BY_OWNER_APPROVAL
        elif not approval_gate["approval_token_passed"]:
            capital_blockers.append("approval_token_failed")
            status = STATUS_BLOCKED_BY_APPROVAL_TOKEN

    if action == ACTION_NO_TRANSFER:
        if status == "":
            status = STATUS_NO_CAPITAL_ACTION_RECOMMENDED
        # keep status as is for BLOCKED_BY_PROFIT_THRESHOLD cases
    elif status.startswith("BLOCKED_BY"):
        pass
    else:
        if mode == MODE_DEMO_PROOF:
            if not status:
                status = STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF
        elif mode == MODE_LIVE_REVIEW:
            live_gate_blockers, live_ready = _evaluate_live_review_gates(
                action=action,
                live_exception=live_exception,
                demo_proof=demo_proof,
                approval_gate=approval_gate,
                capital_blockers=capital_blockers,
            )
            if live_ready:
                status = STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW
            else:
                capital_blockers.extend([b for b in live_gate_blockers if b not in capital_blockers])
                status = (
                    STATUS_BLOCKED_BY_DEMO_PROOF
                    if "demo_proof_ready_false" in live_gate_blockers
                    else STATUS_BLOCKED_BY_LIVE_MODE_GATES
                )
        else:
            status = STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW

    policy_source_reference = _as_text(broker_policy_snapshot.get("policy_source_reference"), default="NONE")
    if status.startswith("BLOCKED_") and not capital_blockers:
        capital_blockers = ["unclassified_block"]

    default_failure_prompt = _failure_prompt(
        requested_action=requested_raw,
        status=status,
        blockers=capital_blockers,
        missing_evidence=missing_inputs if missing_inputs else [],
        policy_source_reference=policy_source_reference,
        approval_status=_approval_token_status(approval_gate, action),
        next_safe_action=_next_safe_action(status, capital_blockers),
    )

    next_best_packet = NEXT_PACKET_DEFAULT
    if status == STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF:
        next_best_packet = NEXT_PACKET_DEMO_PROOF
    elif status == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW:
        next_best_packet = NEXT_PACKET_OWNER_REVIEW
    elif status == STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW:
        next_best_packet = NEXT_PACKET_LIVE_EXCEPTION

    return {
        "schema": SCHEMA,
        "mode": mode,
        "read_only": True,
        "legal_advice_provided": False,
        "financial_advice_provided": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "deposit_allowed": False,
        "withdrawal_allowed": False,
        "ach_allowed": False,
        "wire_allowed": False,
        "card_transfer_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "live_capital_action_authorized": False,
        "owner_decision_required": True,
        "approval_token_required": True,
        "capital_program_status": status,
        "recommended_capital_action": action,
        "requested_action_summary": {
            "requested_action_raw": requested_raw,
            "requested_action_normalized": requested_action,
        },
        "account_state_summary": _summarize_account_state(account_state),
        "bucket_state_summary": _summarize_bucket_state(bucket_state),
        "compounding_decision_summary": {
            "derived_action": derived_action,
            "derived_status": derived_status or STATUS_NO_CAPITAL_ACTION_RECOMMENDED,
            "realized_profit_month": realized_profit_month,
            "min_profit_to_compound": min_profit_to_compound,
            "min_profit_to_sweep": min_profit_to_sweep,
            "profit_bucket": profit_bucket,
            "stale_bucket_age_days": stale_bucket_age_days,
            "bucket_purge_after_days": bucket_purge_after_days,
        },
        "broker_policy_summary": _summarize_broker_policy_snapshot(broker_policy_snapshot),
        "rail_cadence_summary": _summarize_rail_and_cadence(
            rail_registry=rail_registry,
            transfer_history=transfer_history,
            compounding_policy=compounding_policy,
            broker_policy_snapshot=broker_policy_snapshot,
        ),
        "transfer_history_summary": _summarize_transfer_history(transfer_history),
        "open_risk_summary": _summarize_open_risk(open_risk),
        "compliance_summary": _summarize_compliance_evidence(compliance_evidence),
        "approval_token_summary": _summarize_approval_token_evidence(approval_token_evidence),
        "demo_proof_summary": _summarize_demo_proof(demo_proof),
        "live_exception_summary": _summarize_live_exception(live_exception),
        "capital_action_plan": {
            "recommended_action": action,
            "capital_blockers": capital_blockers,
            "owner_decision_required": True,
            "approval_token_required": True,
            "live_capital_action_authorized": False,
            "ready_for_owner_review": status == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
            "ready_for_demo_proof": status == STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF,
            "ready_for_live_exception": status == STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW,
            "as_of_date": _as_text(source.get("as_of_date"), default=datetime.now(timezone.utc).date().isoformat()),
        },
        "default_failure_prompt": default_failure_prompt,
        "capital_blockers": capital_blockers,
        "owner_action_queue": _build_owner_action_queue(
            status=status,
            blockers=capital_blockers,
            missing_evidence=missing_inputs,
            next_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "audit_record": {
            "schema": SCHEMA,
            "mode": mode,
            "owner_name": owner_name,
            "requested_action": requested_raw,
            "recommendation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "capital_program_status": status,
            "capital_blockers": capital_blockers,
            "approval_token_id": _as_text(approval_token_evidence.get("approval_token_id")),
        },
        "safety": {
            "read_only": True,
            "legal_advice_provided": False,
            "financial_advice_provided": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "live_capital_action_authorized": False,
            "deposit_allowed": False,
            "withdrawal_allowed": False,
            "ach_allowed": False,
            "wire_allowed": False,
            "card_transfer_allowed": False,
            "credential_storage_allowed": False,
            "credential_read_allowed": False,
            "owner_gate_required": True,
            "approval_token_required": True,
            "demo_proof_required_before_live": True,
            "broker_policy_snapshot_required": True,
            "fixed_return_target_promised": False,
            "profit_claim_authorized": False,
        },
    }


def _blocked_output(
    source: Mapping[str, Any],
    owner_name: str,
    mode: str,
    requested_action: Any,
    status: str,
    blockers: list[str],
    missing_evidence: list[str],
    policy_source_reference: str,
    approval_gate: Mapping[str, Any],
    approval_action: str,
) -> dict[str, Any]:
    # Rebuild with safe defaults so sensitive content never echoes.
    requested_raw = requested_action
    failure_prompt = _failure_prompt(
        requested_action=requested_raw,
        status=status,
        blockers=blockers,
        missing_evidence=missing_evidence,
        policy_source_reference=policy_source_reference,
        approval_status=_approval_token_status(approval_gate, approval_action),
        next_safe_action=_next_safe_action(status, blockers),
    )
    return {
        "schema": SCHEMA,
        "mode": mode,
        "read_only": True,
        "legal_advice_provided": False,
        "financial_advice_provided": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "deposit_allowed": False,
        "withdrawal_allowed": False,
        "ach_allowed": False,
        "wire_allowed": False,
        "card_transfer_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "live_capital_action_authorized": False,
        "owner_decision_required": True,
        "approval_token_required": True,
        "capital_program_status": status,
        "recommended_capital_action": ACTION_NO_TRANSFER,
        "requested_action_summary": {
            "requested_action_raw": requested_raw,
            "requested_action_normalized": ACTION_AUTO,
        },
        "account_state_summary": _summarize_account_state(_as_mapping(source.get("account_state"))),
        "bucket_state_summary": _summarize_bucket_state(_as_mapping(source.get("bucket_state"))),
        "compounding_decision_summary": {},
        "broker_policy_summary": _summarize_broker_policy_snapshot(_as_mapping(source.get("broker_policy_snapshot"))),
        "rail_cadence_summary": {},
        "transfer_history_summary": _summarize_transfer_history(_as_mapping(source.get("transfer_history"))),
        "open_risk_summary": _summarize_open_risk(_as_mapping(source.get("open_risk"))),
        "compliance_summary": _summarize_compliance_evidence(_as_mapping(source.get("compliance_evidence"))),
        "approval_token_summary": _summarize_approval_token_evidence(_as_mapping(source.get("approval_token_evidence"))),
        "demo_proof_summary": _summarize_demo_proof(_as_mapping(source.get("demo_proof"))),
        "live_exception_summary": _summarize_live_exception(_as_mapping(source.get("live_exception"))),
        "capital_action_plan": {
            "recommended_action": ACTION_NO_TRANSFER,
            "capital_blockers": blockers,
            "owner_decision_required": True,
            "approval_token_required": True,
            "live_capital_action_authorized": False,
            "ready_for_owner_review": False,
            "ready_for_demo_proof": False,
            "ready_for_live_exception": False,
            "as_of_date": _as_text(source.get("as_of_date"), default=datetime.now(timezone.utc).date().isoformat()),
        },
        "default_failure_prompt": failure_prompt,
        "capital_blockers": blockers,
        "owner_action_queue": _build_owner_action_queue(
            status=status,
            blockers=blockers,
            missing_evidence=missing_evidence,
            next_packet=NEXT_PACKET_DEFAULT,
        ),
        "next_best_packet": NEXT_PACKET_DEFAULT,
        "audit_record": {
            "schema": SCHEMA,
            "mode": mode,
            "owner_name": owner_name,
            "requested_action": requested_raw,
            "recommendation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "capital_program_status": status,
            "capital_blockers": blockers,
            "approval_token_id": _as_text(_as_mapping(source.get("approval_token_evidence")).get("approval_token_id")),
        },
        "safety": {
            "read_only": True,
            "legal_advice_provided": False,
            "financial_advice_provided": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "live_capital_action_authorized": False,
            "deposit_allowed": False,
            "withdrawal_allowed": False,
            "ach_allowed": False,
            "wire_allowed": False,
            "card_transfer_allowed": False,
            "credential_storage_allowed": False,
            "credential_read_allowed": False,
            "owner_gate_required": True,
            "approval_token_required": True,
            "demo_proof_required_before_live": True,
            "broker_policy_snapshot_required": True,
            "fixed_return_target_promised": False,
            "profit_claim_authorized": False,
        },
    }


def _collect_missing_core_inputs(
    account_state: Mapping[str, Any],
    bucket_state: Mapping[str, Any],
    compounding_policy: Mapping[str, Any],
    open_risk: Mapping[str, Any],
    owner_approval: Mapping[str, Any],
) -> list[str]:
    missing: list[str] = []
    if not account_state:
        missing.append("account_state")
    else:
        for key in (
            "balance",
            "equity",
            "month_start_balance",
            "realized_profit_month",
            "unrealized_pnl",
            "open_positions_count",
            "margin_used",
            "drawdown_pct",
            "daily_loss_pct",
            "closed_trade_count_month",
        ):
            if key not in account_state:
                missing.append(f"account_state.{key}")
    if not bucket_state:
        missing.append("bucket_state")
    else:
        for key in (
            "principal_bucket",
            "profit_bucket",
            "reserve_bucket",
            "tax_reserve_bucket",
            "compounding_bucket",
            "sweep_bucket",
            "stale_bucket_age_days",
        ):
            if key not in bucket_state:
                missing.append(f"bucket_state.{key}")
    if not compounding_policy:
        missing.append("compounding_policy")
    else:
        for key in (
            "compound_profit_pct",
            "sweep_profit_pct",
            "reserve_profit_pct",
            "min_profit_to_compound",
            "min_profit_to_sweep",
            "max_account_growth_before_sweep_pct",
            "retain_min_equity_buffer_pct",
            "max_drawdown_pct_for_capital_action",
            "max_daily_loss_pct_for_capital_action",
            "require_no_open_positions_for_withdrawal",
            "require_no_open_positions_for_deposit",
            "bucket_purge_after_days",
        ):
            if key not in compounding_policy:
                missing.append(f"compounding_policy.{key}")
    if not open_risk:
        missing.append("open_risk")
    else:
        for key in (
            "open_positions_count",
            "margin_used",
            "kill_switch_active",
            "daily_loss_stop_active",
            "duplicate_order_detected",
            "pending_settlement",
            "unsettled_pnl",
        ):
            if key not in open_risk:
                missing.append(f"open_risk.{key}")
    if not owner_approval:
        missing.append("owner_approval")
    return missing


def _derive_recommendation(
    realized_profit_month: Decimal,
    min_profit_to_compound: Decimal,
    min_profit_to_sweep: Decimal,
    profit_bucket: Decimal,
) -> tuple[str, str]:
    if realized_profit_month <= Decimal("0"):
        return ACTION_NO_TRANSFER, STATUS_NO_CAPITAL_ACTION_RECOMMENDED
    if realized_profit_month < min_profit_to_compound:
        return ACTION_NO_TRANSFER, STATUS_BLOCKED_BY_PROFIT_THRESHOLD
    if profit_bucket >= min_profit_to_sweep:
        return ACTION_OWNER_REVIEW_PROFIT_SWEEP, ""
    return ACTION_COMPOUND_IN_ACCOUNT, ""


def _evaluate_drawdown_gate(
    open_risk: Mapping[str, Any],
    account_state: Mapping[str, Any],
    compounding_policy: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if _to_bool(open_risk.get("kill_switch_active"), False):
        blockers.append("kill_switch_active")
    if _to_bool(open_risk.get("daily_loss_stop_active"), False):
        blockers.append("daily_loss_stop_active")
    drawdown_pct = _to_decimal(account_state.get("drawdown_pct"), Decimal("0"))
    max_drawdown_pct = _to_decimal(compounding_policy.get("max_drawdown_pct_for_capital_action"), Decimal("1000"))
    if drawdown_pct > max_drawdown_pct:
        blockers.append("drawdown_pct_exceeded")
    daily_loss_pct = _to_decimal(account_state.get("daily_loss_pct"), Decimal("0"))
    max_daily_loss_pct = _to_decimal(compounding_policy.get("max_daily_loss_pct_for_capital_action"), Decimal("1000"))
    if daily_loss_pct > max_daily_loss_pct:
        blockers.append("daily_loss_pct_exceeded")
    return blockers

def _evaluate_compliance_gate(
    broker_policy_snapshot: Mapping[str, Any],
    compliance_evidence: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if not _to_bool(broker_policy_snapshot.get("terms_acknowledged_by_owner"), False):
        blockers.append("terms_acknowledged_by_owner_false")
    if not _as_text(broker_policy_snapshot.get("policy_source_reference")):
        blockers.append("policy_source_reference_missing")
    if not _as_text(broker_policy_snapshot.get("jurisdiction")):
        blockers.append("jurisdiction_missing")
    if _to_bool(broker_policy_snapshot.get("kyc_required"), False):
        if _as_text(compliance_evidence.get("kyc_status"), "").upper() != "COMPLETE":
            blockers.append("kyc_status_incomplete")
    if _to_bool(broker_policy_snapshot.get("tax_review_required"), False):
        if not _to_bool(compliance_evidence.get("tax_review_complete"), False):
            blockers.append("tax_review_incomplete")
    if _to_bool(compliance_evidence.get("legal_review_required"), False):
        if not _to_bool(compliance_evidence.get("legal_review_complete"), False):
            blockers.append("legal_review_incomplete")
    return blockers


def _evaluate_transfer_cadence_gate(
    action: str,
    compounding_policy: Mapping[str, Any],
    broker_policy_snapshot: Mapping[str, Any],
    transfer_history: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []

    withdrawal_cooldown_satisfied = _to_bool(broker_policy_snapshot.get("withdrawal_cooldown_satisfied"), True)
    deposit_cooldown_satisfied = _to_bool(broker_policy_snapshot.get("deposit_cooldown_satisfied"), True)
    withdrawal_cooldown_days = _to_int(broker_policy_snapshot.get("withdrawal_cooldown_days"), default=0)
    deposit_cooldown_days = _to_int(broker_policy_snapshot.get("deposit_cooldown_days"), default=0)
    last_withdrawal_days_ago = _to_int(transfer_history.get("last_withdrawal_days_ago"), default=10**6)
    last_deposit_days_ago = _to_int(transfer_history.get("last_deposit_days_ago"), default=10**6)

    withdrawals_this_month = max(
        _to_int(transfer_history.get("withdrawals_this_month"), default=0),
        _to_int(broker_policy_snapshot.get("withdrawals_used_this_month"), default=0),
    )
    deposits_this_month = max(
        _to_int(transfer_history.get("deposits_this_month"), default=0),
        _to_int(broker_policy_snapshot.get("deposits_used_this_month"), default=0),
    )
    max_withdrawals_per_month = max(
        _to_int(compounding_policy.get("max_withdrawals_per_month"), default=0),
        _to_int(broker_policy_snapshot.get("max_withdrawals_per_month"), default=0),
    )
    max_deposits_per_month = max(
        _to_int(compounding_policy.get("max_deposits_per_month"), default=0),
        _to_int(broker_policy_snapshot.get("max_deposits_per_month"), default=0),
    )

    if _is_sweep_withdraw_action(action):
        if max_withdrawals_per_month and withdrawals_this_month >= max_withdrawals_per_month:
            blockers.append("withdrawal_cadence_exhausted")
        if not withdrawal_cooldown_satisfied:
            blockers.append("withdrawal_cooldown_unsatisfied")
        if last_withdrawal_days_ago < withdrawal_cooldown_days:
            blockers.append("withdrawal_recently_transferred")
    if _is_deposit_action(action):
        if max_deposits_per_month and deposits_this_month >= max_deposits_per_month:
            blockers.append("deposit_cadence_exhausted")
        if not deposit_cooldown_satisfied:
            blockers.append("deposit_cooldown_unsatisfied")
        if last_deposit_days_ago < deposit_cooldown_days:
            blockers.append("deposit_recently_transferred")
    return blockers


def _evaluate_open_risk_gate(
    action: str,
    open_risk: Mapping[str, Any],
    compounding_policy: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    open_positions_count = _to_int(open_risk.get("open_positions_count"), default=0)
    margin_used = _to_decimal(open_risk.get("margin_used"), Decimal("0"))
    require_no_open_positions_for_withdrawal = _to_bool(
        compounding_policy.get("require_no_open_positions_for_withdrawal"),
        False,
    )
    require_no_open_positions_for_deposit = _to_bool(
        compounding_policy.get("require_no_open_positions_for_deposit"),
        False,
    )

    if _is_sweep_withdraw_action(action) and require_no_open_positions_for_withdrawal and open_positions_count > 0:
        blockers.append("open_positions_block_transfer")
    if _is_deposit_action(action) and require_no_open_positions_for_deposit and open_positions_count > 0:
        blockers.append("open_positions_block_deposit")
    if _is_sweep_withdraw_action(action) and margin_used > Decimal("0"):
        blockers.append("margin_used")
    if _to_bool(open_risk.get("pending_settlement"), False):
        blockers.append("pending_settlement")
    if _to_bool(open_risk.get("unsettled_pnl"), False):
        blockers.append("unsettled_pnl")
    if _to_bool(open_risk.get("duplicate_order_detected"), False):
        blockers.append("duplicate_order_detected")
    return blockers


def _evaluate_approval_gate(
    owner_name: str,
    action: str,
    owner_approval: Mapping[str, Any],
    approval_token_evidence: Mapping[str, Any],
    mode: str,
) -> dict[str, Any]:
    owner_approval_required = _to_bool(owner_approval.get("owner_approval_required"), True)
    owner_approval_true = _to_bool(owner_approval.get("owner_accepts_action"), False)
    owner_accepts_policy_snapshot = _to_bool(owner_approval.get("owner_accepts_policy_snapshot"), False)
    owner_accepts_risk_state = _to_bool(owner_approval.get("owner_accepts_risk_state"), False)
    owner_accepts_no_autonomous_money_movement = _to_bool(
        owner_approval.get("owner_accepts_no_autonomous_money_movement"),
        False,
    )
    owner_accepts_name_ok = owner_name.strip().upper() == _as_text(owner_approval.get("owner_name"), default="Anthony").strip().upper()

    owner_passed = False
    if action == ACTION_NO_TRANSFER:
        owner_passed = True
    elif (
        owner_approval_required
        and owner_accepts_name_ok
        and owner_approval_true
        and owner_accepts_policy_snapshot
        and owner_accepts_risk_state
        and owner_accepts_no_autonomous_money_movement
    ):
        owner_passed = True

    approval_phrase_present = _to_bool(approval_token_evidence.get("approval_phrase_present"), False)
    approval_phrase_matches = _to_bool(approval_token_evidence.get("approval_phrase_matches"), False)
    approval_amount_matches = _to_bool(approval_token_evidence.get("approval_amount_matches"), False)
    approval_balance_matches = _to_bool(approval_token_evidence.get("approval_balance_matches"), False)
    approval_action_matches = _to_bool(approval_token_evidence.get("approval_action_matches"), False)
    approval_mode_matches = _to_bool(approval_token_evidence.get("approval_mode_matches"), False)
    approval_token_unexpired = _to_bool(approval_token_evidence.get("approval_token_unexpired"), False)
    approval_token_unused = _to_bool(approval_token_evidence.get("approval_token_unused"), False)
    approval_timestamp_present = _to_bool(approval_token_evidence.get("approval_timestamp_present"), False)
    approval_challenge_hash_present = _to_bool(approval_token_evidence.get("approval_challenge_hash_present"), False)
    owner_cancel_phrase_detected = _to_bool(approval_token_evidence.get("owner_cancel_phrase_detected"), False)
    approval_channel = _as_text(approval_token_evidence.get("approval_channel"))
    token_checks = [
        approval_phrase_present,
        approval_phrase_matches,
        approval_amount_matches,
        approval_balance_matches,
        approval_action_matches,
        approval_mode_matches,
        approval_token_unexpired,
        approval_token_unused,
        approval_timestamp_present,
        approval_challenge_hash_present,
        not owner_cancel_phrase_detected,
    ]
    token_passed = action == ACTION_NO_TRANSFER or all(token_checks)

    return {
        "owner_approval_required": owner_approval_required,
        "approval_token_required": action != ACTION_NO_TRANSFER,
        "owner_name_ok": owner_accepts_name_ok,
        "owner_approval_passed": owner_passed,
        "approval_token_passed": token_passed,
        "approval_phrase_present": approval_phrase_present,
        "approval_phrase_matches": approval_phrase_matches,
        "approval_amount_matches": approval_amount_matches,
        "approval_balance_matches": approval_balance_matches,
        "approval_action_matches": approval_action_matches,
        "approval_mode_matches": approval_mode_matches,
        "approval_token_unexpired": approval_token_unexpired,
        "approval_token_unused": approval_token_unused,
        "approval_timestamp_present": approval_timestamp_present,
        "approval_challenge_hash_present": approval_challenge_hash_present,
        "owner_cancel_phrase_detected": owner_cancel_phrase_detected,
        "approval_channel": approval_channel,
        "approval_token_id": _as_text(approval_token_evidence.get("approval_token_id")),
        "approval_action": _as_text(approval_token_evidence.get("approval_action")),
        "approval_mode": _as_text(approval_token_evidence.get("approval_mode")),
    }


def _evaluate_live_review_gates(
    action: str,
    live_exception: Mapping[str, Any],
    demo_proof: Mapping[str, Any],
    approval_gate: Mapping[str, Any],
    capital_blockers: list[str],
) -> tuple[list[str], bool]:
    blockers: list[str] = []
    if action == ACTION_NO_TRANSFER:
        blockers.append("no_action")
        return blockers, False

    if not _to_bool(demo_proof.get("demo_proof_ready"), False):
        blockers.append("demo_proof_ready_false")
    if not _to_bool(live_exception.get("broker_policy_snapshot_current"), False):
        blockers.append("broker_policy_snapshot_not_current")
    if not _to_bool(live_exception.get("compliance_evidence_complete"), False):
        blockers.append("compliance_evidence_complete_false")
    if not _to_bool(live_exception.get("no_open_risk"), False):
        blockers.append("no_open_risk_false")
    if not _to_bool(live_exception.get("owner_live_exception_approval"), False):
        blockers.append("owner_live_exception_approval_false")
    if not approval_gate.get("owner_approval_passed", False):
        blockers.append("owner_approval_failed")
    if not approval_gate.get("approval_token_passed", False):
        blockers.append("approval_token_failed")
    if capital_blockers:
        blockers.extend(capital_blockers)

    return blockers, not bool(blockers)


def _summarize_account_state(account_state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "balance": _to_decimal(account_state.get("balance"), Decimal("0")),
        "equity": _to_decimal(account_state.get("equity"), Decimal("0")),
        "month_start_balance": _to_decimal(account_state.get("month_start_balance"), Decimal("0")),
        "realized_profit_month": _to_decimal(account_state.get("realized_profit_month"), Decimal("0")),
        "unrealized_pnl": _to_decimal(account_state.get("unrealized_pnl"), Decimal("0")),
        "open_positions_count": _to_int(account_state.get("open_positions_count"), default=0),
        "margin_used": _to_decimal(account_state.get("margin_used"), Decimal("0")),
        "drawdown_pct": _to_decimal(account_state.get("drawdown_pct"), Decimal("0")),
        "daily_loss_pct": _to_decimal(account_state.get("daily_loss_pct"), Decimal("0")),
        "closed_trade_count_month": _to_int(account_state.get("closed_trade_count_month"), default=0),
    }


def _summarize_bucket_state(bucket_state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "principal_bucket": _to_decimal(bucket_state.get("principal_bucket"), Decimal("0")),
        "profit_bucket": _to_decimal(bucket_state.get("profit_bucket"), Decimal("0")),
        "reserve_bucket": _to_decimal(bucket_state.get("reserve_bucket"), Decimal("0")),
        "tax_reserve_bucket": _to_decimal(bucket_state.get("tax_reserve_bucket"), Decimal("0")),
        "compounding_bucket": _to_decimal(bucket_state.get("compounding_bucket"), Decimal("0")),
        "sweep_bucket": _to_decimal(bucket_state.get("sweep_bucket"), Decimal("0")),
        "stale_bucket_age_days": _to_int(bucket_state.get("stale_bucket_age_days"), default=0),
    }


def _summarize_broker_policy_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker_name": _as_text(snapshot.get("broker_name")),
        "document_title": _as_text(snapshot.get("document_title")),
        "policy_source_reference": _as_text(snapshot.get("policy_source_reference"), default="NONE"),
        "policy_reviewed_date": _as_text(snapshot.get("policy_reviewed_date")),
        "terms_acknowledged_by_owner": _to_bool(snapshot.get("terms_acknowledged_by_owner"), False),
        "max_withdrawals_per_month": _to_int(snapshot.get("max_withdrawals_per_month"), default=0),
        "withdrawals_used_this_month": _to_int(snapshot.get("withdrawals_used_this_month"), default=0),
        "max_deposits_per_month": _to_int(snapshot.get("max_deposits_per_month"), default=0),
        "deposits_used_this_month": _to_int(snapshot.get("deposits_used_this_month"), default=0),
        "jurisdiction": _as_text(snapshot.get("jurisdiction")),
    }


def _summarize_rail_and_cadence(
    rail_registry: Mapping[str, Any],
    transfer_history: Mapping[str, Any],
    compounding_policy: Mapping[str, Any],
    broker_policy_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "rail_label": _as_text(rail_registry.get("rail_label")),
        "rail_type": _as_text(rail_registry.get("rail_type")),
        "rail_allowed_by_policy": _to_bool(rail_registry.get("rail_allowed_by_policy"), False),
        "rail_owner_verified": _to_bool(rail_registry.get("rail_owner_verified"), False),
        "no_sensitive_identifiers_present": _to_bool(rail_registry.get("no_sensitive_identifiers_present"), False),
        "prohibited_rails": _as_text(broker_policy_snapshot.get("prohibited_rails")),
        "allowed_rails": _as_text(broker_policy_snapshot.get("allowed_rails")),
        "withdrawal_cooldown_days": _to_int(compounding_policy.get("withdrawal_cooldown_days"), default=0),
        "deposit_cooldown_days": _to_int(compounding_policy.get("deposit_cooldown_days"), default=0),
        "estimated_fees": _as_text(broker_policy_snapshot.get("estimated_fees")),
        "withdrawals_this_month": _to_int(transfer_history.get("withdrawals_this_month"), default=0),
        "deposits_this_month": _to_int(transfer_history.get("deposits_this_month"), default=0),
    }


def _summarize_transfer_history(transfer_history: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "withdrawals_this_month": _to_int(transfer_history.get("withdrawals_this_month"), default=0),
        "deposits_this_month": _to_int(transfer_history.get("deposits_this_month"), default=0),
        "last_withdrawal_days_ago": _to_int(transfer_history.get("last_withdrawal_days_ago"), default=0),
        "last_deposit_days_ago": _to_int(transfer_history.get("last_deposit_days_ago"), default=0),
        "last_transfer_status": _as_text(transfer_history.get("last_transfer_status")),
    }


def _summarize_open_risk(open_risk: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "open_positions_count": _to_int(open_risk.get("open_positions_count"), default=0),
        "margin_used": _to_decimal(open_risk.get("margin_used"), Decimal("0")),
        "kill_switch_active": _to_bool(open_risk.get("kill_switch_active"), False),
        "daily_loss_stop_active": _to_bool(open_risk.get("daily_loss_stop_active"), False),
        "pending_settlement": _to_bool(open_risk.get("pending_settlement"), False),
        "unsettled_pnl": _to_bool(open_risk.get("unsettled_pnl"), False),
        "duplicate_order_detected": _to_bool(open_risk.get("duplicate_order_detected"), False),
    }


def _summarize_compliance_evidence(compliance_evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "terms_acknowledged_by_owner": _to_bool(compliance_evidence.get("terms_acknowledged_by_owner"), False),
        "jurisdiction_present": _to_bool(compliance_evidence.get("jurisdiction_present"), False),
        "kyc_status": _as_text(compliance_evidence.get("kyc_status")),
        "tax_review_complete": _to_bool(compliance_evidence.get("tax_review_complete"), False),
        "policy_source_reference_present": _to_bool(compliance_evidence.get("policy_source_reference_present"), False),
        "user_agreement_reviewed": _to_bool(compliance_evidence.get("user_agreement_reviewed"), False),
        "legal_review_required": _to_bool(compliance_evidence.get("legal_review_required"), False),
        "legal_review_complete": _to_bool(compliance_evidence.get("legal_review_complete"), False),
    }


def _summarize_approval_token_evidence(approval_token_evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "approval_token_id": _as_text(approval_token_evidence.get("approval_token_id")),
        "approval_channel": _as_text(approval_token_evidence.get("approval_channel")),
        "approval_phrase_present": _to_bool(approval_token_evidence.get("approval_phrase_present"), False),
        "approval_phrase_matches": _to_bool(approval_token_evidence.get("approval_phrase_matches"), False),
        "approval_amount_matches": _to_bool(approval_token_evidence.get("approval_amount_matches"), False),
        "approval_balance_matches": _to_bool(approval_token_evidence.get("approval_balance_matches"), False),
        "approval_action_matches": _to_bool(approval_token_evidence.get("approval_action_matches"), False),
        "approval_mode_matches": _to_bool(approval_token_evidence.get("approval_mode_matches"), False),
        "approval_token_unexpired": _to_bool(approval_token_evidence.get("approval_token_unexpired"), False),
        "approval_token_unused": _to_bool(approval_token_evidence.get("approval_token_unused"), False),
        "approval_timestamp_present": _to_bool(approval_token_evidence.get("approval_timestamp_present"), False),
        "owner_cancel_phrase_detected": _to_bool(approval_token_evidence.get("owner_cancel_phrase_detected"), False),
        "approval_challenge_hash_present": _to_bool(approval_token_evidence.get("approval_challenge_hash_present"), False),
        "approval_balance_snapshot": _as_text(approval_token_evidence.get("approval_balance_snapshot")),
        "approval_amount": _to_decimal(approval_token_evidence.get("approval_amount"), Decimal("0")),
        "approval_action": _as_text(approval_token_evidence.get("approval_action")),
        "approval_mode": _as_text(approval_token_evidence.get("approval_mode")),
    }


def _summarize_demo_proof(demo_proof: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "demo_mode_used": _to_bool(demo_proof.get("demo_mode_used"), False),
        "simulated_transfer_count": _to_int(demo_proof.get("simulated_transfer_count"), default=0),
        "simulated_compound_count": _to_int(demo_proof.get("simulated_compound_count"), default=0),
        "simulated_sweep_count": _to_int(demo_proof.get("simulated_sweep_count"), default=0),
        "simulated_block_count": _to_int(demo_proof.get("simulated_block_count"), default=0),
        "failed_gate_distribution": _as_text(demo_proof.get("failed_gate_distribution"), default="{}"),
        "last_demo_result_status": _as_text(demo_proof.get("last_demo_result_status")),
        "demo_proof_ready": _to_bool(demo_proof.get("demo_proof_ready"), False),
    }


def _summarize_live_exception(live_exception: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "live_review_requested": _to_bool(live_exception.get("live_review_requested"), False),
        "demo_proof_ready": _to_bool(live_exception.get("demo_proof_ready"), False),
        "owner_live_exception_approval": _to_bool(live_exception.get("owner_live_exception_approval"), False),
        "broker_policy_snapshot_current": _to_bool(live_exception.get("broker_policy_snapshot_current"), False),
        "compliance_evidence_complete": _to_bool(live_exception.get("compliance_evidence_complete"), False),
        "no_open_risk": _to_bool(live_exception.get("no_open_risk"), False),
        "live_exception_ready": _to_bool(live_exception.get("live_exception_ready"), False),
    }


def _build_owner_action_queue(
    status: str,
    blockers: list[str],
    missing_evidence: list[str],
    next_packet: str,
) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for action_id in REQUIRED_OWNER_ACTION_IDS:
        entry = {
            "owner_action_id": action_id,
            "owner_decision_required": True,
            "money_movement_allowed": False,
            "live_capital_action_authorized": False,
            "blocked_by": blockers,
            "safe_action": "Review packet evidence and update evidence records.",
        }
        if action_id == "REVIEW_NEXT_PACKET":
            entry["safe_action"] = f"Route to next packet {next_packet}"
            entry["next_packet"] = next_packet
        if status.startswith("BLOCKED_") or missing_evidence:
            entry["next_action"] = "Collect missing evidence and request owner re-evaluation."
        queue.append(entry)
    return queue


def _failure_prompt(
    requested_action: Any,
    status: str,
    blockers: list[str],
    missing_evidence: list[str],
    policy_source_reference: str,
    approval_status: str,
    next_safe_action: str,
) -> str:
    if status == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW:
        return (
            "AIOS CAPITAL ACTION READY FOR OWNER REVIEW.\n"
            f"Recommended action: {requested_action}.\n"
            f"Approval token: {approval_status}.\n"
            "Amount/balance/action/mode must match exactly.\n"
            "No money has been moved. Owner must separately execute any broker or bank portal action if desired."
        )
    if status == STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW:
        return (
            "AIOS LIVE CAPITAL EXCEPTION READY FOR OWNER REVIEW.\n"
            "No live capital action is authorized by this packet. A separate live exception packet is required."
        )
    return (
        "AIOS CAPITAL ACTION BLOCKED.\n"
        f"Attempted action: {requested_action}.\n"
        f"Status: {status}.\n"
        f"Failed gates: {', '.join(blockers) if blockers else 'None'}.\n"
        f"Missing evidence: {', '.join(missing_evidence) if missing_evidence else 'None'}.\n"
        f"Policy evidence used: {policy_source_reference}.\n"
        f"Approval token status: {approval_status}.\n"
        "No money was moved. No credentials were used. No broker or bank API was accessed.\n"
        f"Next owner action: {next_safe_action}."
    )


def _next_safe_action(status: str, blockers: list[str]) -> str:
    if status == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW:
        return "Upload exact owner phrase, amount, action, and mode evidence and wait for owner approval."
    if status == STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF:
        return "Upload demo proof and rerun packet."
    if status == STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW:
        return "Open live exception ticket packet and wait for owner review."
    if blockers:
        return blockers[0].replace("_", " ")
    if status.startswith("BLOCKED_"):
        return "Submit required evidence and rerun this packet."
    return "No action required."


def _approval_token_status(approval_gate: Mapping[str, Any], action: str) -> str:
    if action == ACTION_NO_TRANSFER:
        return "not_required"
    if approval_gate.get("owner_approval_passed") and approval_gate.get("approval_token_passed"):
        return "valid"
    if approval_gate.get("owner_approval_passed") or approval_gate.get("approval_token_passed"):
        return "invalid"
    return "missing"


def _contains_sensitive_key(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if not isinstance(key, str):
                continue
            key_lower = key.lower()
            if key_lower in BOUNDARY_SAFE_KEY_EXCEPTIONS:
                continue
            if any(part in key_lower for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(value):
                return True
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for item in payload:
            if _contains_sensitive_key(item):
                return True
    return False


def _normalize_mode(mode: Any) -> str:
    normalized = _as_text(mode, default=MODE_READ_ONLY_REVIEW).strip().upper()
    if normalized not in {MODE_READ_ONLY_REVIEW, MODE_DEMO_PROOF, MODE_LIVE_REVIEW}:
        return MODE_READ_ONLY_REVIEW
    return normalized


def _normalize_requested_action(raw_action: Any) -> str:
    action = _as_text(raw_action, default=ACTION_AUTO).strip().upper().replace("-", "_")
    if action in (
        ACTION_AUTO,
        ACTION_NO_TRANSFER,
        ACTION_COMPOUND_IN_ACCOUNT,
        ACTION_OWNER_REVIEW_PROFIT_SWEEP,
        ACTION_OWNER_REVIEW_WITHDRAW_PROFIT,
        ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP,
        ACTION_OWNER_REVIEW_RESERVE_REALLOCATION,
        ACTION_OWNER_REVIEW_BUCKET_PURGE,
    ):
        return action
    return ACTION_AUTO


def _is_sweep_withdraw_action(action: str) -> bool:
    return action in SWEEP_WITHDRAW_ACTIONS


def _is_deposit_action(action: str) -> bool:
    return action in DEPOSIT_ACTIONS


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_text(value: Any, default: str | None = None) -> str:
    if value is None:
        return default or ""
    return str(value)


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in {"true", "1", "y", "yes", "on"}:
        return True
    if text in {"false", "0", "n", "no", "off"}:
        return False
    return default


def _to_decimal(value: Any, default: Decimal) -> Decimal:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return Decimal("1") if value else Decimal("0")
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return int(value)
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _empty_approval_gate() -> dict[str, Any]:
    return {
        "owner_approval_required": False,
        "approval_token_required": False,
        "owner_name_ok": False,
        "owner_approval_passed": False,
        "approval_token_passed": False,
        "approval_phrase_present": False,
        "approval_phrase_matches": False,
        "approval_amount_matches": False,
        "approval_balance_matches": False,
        "approval_action_matches": False,
        "approval_mode_matches": False,
        "approval_token_unexpired": False,
        "approval_token_unused": False,
        "approval_timestamp_present": False,
        "approval_challenge_hash_present": False,
        "owner_cancel_phrase_detected": False,
        "approval_channel": None,
        "approval_token_id": None,
        "approval_action": None,
        "approval_mode": None,
    }


def _is_transfer_like_action(action: str) -> bool:
    return action in TRANSFER_LIKE_ACTIONS


__all__ = [
    "SCHEMA",
    "MODE",
    "ACTION_AUTO",
    "ACTION_NO_TRANSFER",
    "ACTION_COMPOUND_IN_ACCOUNT",
    "ACTION_OWNER_REVIEW_PROFIT_SWEEP",
    "ACTION_OWNER_REVIEW_WITHDRAW_PROFIT",
    "ACTION_OWNER_REVIEW_DEPOSIT_TOP_UP",
    "ACTION_OWNER_REVIEW_RESERVE_REALLOCATION",
    "ACTION_OWNER_REVIEW_BUCKET_PURGE",
    "STATUS_CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF",
    "STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW",
    "STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW",
    "STATUS_NO_CAPITAL_ACTION_RECOMMENDED",
    "STATUS_BLOCKED_BY_MISSING_POLICY_SNAPSHOT",
    "STATUS_BLOCKED_BY_BROKER_POLICY",
    "STATUS_BLOCKED_BY_TRANSFER_CADENCE",
    "STATUS_BLOCKED_BY_OPEN_RISK",
    "STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS",
    "STATUS_BLOCKED_BY_PROFIT_THRESHOLD",
    "STATUS_BLOCKED_BY_OWNER_APPROVAL",
    "STATUS_BLOCKED_BY_APPROVAL_TOKEN",
    "STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE",
    "STATUS_BLOCKED_BY_DEMO_PROOF",
    "STATUS_BLOCKED_BY_LIVE_MODE_GATES",
    "STATUS_BLOCKED_BY_DATA_QUALITY",
    "STATUS_INCOMPLETE_INPUTS",
    "MODE_READ_ONLY_REVIEW",
    "MODE_DEMO_PROOF",
    "MODE_LIVE_REVIEW",
    "evaluate_capital_operating_program_v2",
]
