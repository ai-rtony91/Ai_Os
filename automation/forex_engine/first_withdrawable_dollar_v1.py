"""Canonical evidence and prioritization contract for AI_OS's primary anchor."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

SCHEMA = "AIOS_FIRST_WITHDRAWABLE_DOLLAR.v1"
ANCHOR_ID = "FIRST_WITHDRAWABLE_DOLLAR"
MINIMUM_NET_REALIZED_PROFIT = Decimal("1.00")

def _money(value: Any) -> Decimal | None:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return amount if amount.is_finite() else None

def evaluate_first_withdrawable_dollar(evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(evidence or {})
    gross, costs, net = (_money(source.get(key)) for key in ("gross_realized_profit", "fees_and_costs", "net_realized_profit"))
    calculated_net = gross - costs if gross is not None and costs is not None else None
    checks = {
        "evidence_valid": source.get("evidence_genuine") is True and source.get("evidence_sanitized") is True and source.get("evidence_reproducible") is True,
        "real_owner_approved_oanda_trade": source.get("trade_is_real") is True and source.get("owner_approved_trade") is True and str(source.get("broker", "")).upper() == "OANDA",
        "trade_closed": source.get("trade_closed") is True,
        "net_profit_verified": net is not None and calculated_net is not None and net == calculated_net and net >= MINIMUM_NET_REALIZED_PROFIT,
        "funds_withdrawable": source.get("withdrawable_confirmed") is True,
        "linked_destination_confirmed": source.get("linked_bank_destination_confirmed") is True,
        "withdrawal_owner_approved": source.get("withdrawal_owner_approved") is True,
        "withdrawal_submitted": source.get("withdrawal_submitted") is True,
    }
    ordered = (
        ("evidence_valid", "PROVIDE_GENUINE_SANITIZED_REPRODUCIBLE_EVIDENCE", "REAL_TRADE_EVIDENCE"),
        ("real_owner_approved_oanda_trade", "OWNER_APPROVE_AND_EXECUTE_ONE_GOVERNED_OANDA_TRADE", "REAL_TRADE_EVIDENCE"),
        ("trade_closed", "OWNER_APPROVE_TRADE_CLOSURE", "CLOSED_TRADE_EVIDENCE"),
        ("net_profit_verified", "PROVE_NET_REALIZED_PROFIT_AT_LEAST_1_USD_AFTER_COSTS", "NET_REALIZED_PROFIT_EVIDENCE"),
        ("funds_withdrawable", "VERIFY_FUNDS_ARE_WITHDRAWABLE_UNDER_BROKER_RULES", "WITHDRAWABLE_FUNDS_EVIDENCE"),
        ("linked_destination_confirmed", "VERIFY_ALREADY_LINKED_BANK_DESTINATION_WITHOUT_EXPOSING_DETAILS", "WITHDRAWABLE_FUNDS_EVIDENCE"),
        ("withdrawal_owner_approved", "OWNER_APPROVE_EXACT_WITHDRAWAL", "OWNER_WITHDRAWAL_APPROVAL"),
        ("withdrawal_submitted", "OWNER_SUBMIT_APPROVED_WITHDRAWAL", "WITHDRAWAL_SUBMISSION_EVIDENCE"),
    )
    next_blocker, stage = "NONE", "COMPLETE"
    for check, blocker, check_stage in ordered:
        if not checks[check]:
            next_blocker, stage = blocker, check_stage
            break
    complete = all(checks.values())
    return {"schema": SCHEMA, "anchor_id": ANCHOR_ID, "anchor_complete": complete, "current_stage": stage, "next_verified_blocker": next_blocker, "net_realized_profit": str(net) if net is not None else None, "minimum_net_realized_profit": str(MINIMUM_NET_REALIZED_PROFIT), "checks": checks, "lower_level_milestones_are_dependencies": True, "claims_allowed": complete, "protected_actions": {key: False for key in ("credential_connection", "live_trading_activation", "real_order_placement", "real_order_modification_or_closure", "withdrawal_submission", "money_movement")}}

def anchor_rank(candidate: Mapping[str, Any]) -> tuple[bool, float]:
    if "verified_anchor_distance" not in candidate:
        return False, 0.0
    try:
        distance = max(0.0, float(candidate["verified_anchor_distance"]))
    except (TypeError, ValueError):
        return True, -1.0
    score = 1_000_000.0 - distance * 10_000.0
    if candidate.get("removes_verified_anchor_dependency") is True:
        score += 5_000.0
    if str(candidate.get("lane", "")).lower().startswith("governance") and candidate.get("governance_directly_blocks_anchor") is not True:
        score -= 2_000_000.0
    return True, score
