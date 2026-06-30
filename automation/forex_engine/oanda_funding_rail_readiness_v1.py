"""Read-only OANDA funding rail readiness evaluator for AIOS Forex.

This module only evaluates sanitized planning fields. It does not move money,
connect to OANDA, access a bank, access credentials, or authorize trading.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


SCHEMA = "AIOS_FOREX_OANDA_FUNDING_RAIL_READINESS_V1"
MODE = "READ_ONLY_FUNDING_RAIL_REVIEW"

DEPOSIT_METHODS = {
    "debit_card",
    "wire_domestic",
    "wire_international",
    "ach",
    "unknown",
}
WIRE_METHODS = {"wire_domestic", "wire_international"}
SENSITIVE_KEYS = {
    "routing_number",
    "account_number",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "token",
    "secret",
    "credential",
    "credentials",
}

PROCESSING_TIME_ESTIMATES = {
    "debit_card_deposit": "virtually instant",
    "debit_card_withdrawal": "up to 3 business days",
    "domestic_wire_deposit": "1 to 3 business days",
    "international_wire_deposit": "up to 5 business days",
    "ach_deposit": "up to 6 days",
    "us_wire_withdrawal": "1 to 2 business days",
    "international_wire_withdrawal": "up to 5 business days",
}

LIMITS = {
    "debit_card_monthly_deposit_limit_usd": 20000,
    "ach_per_transaction_limit_usd": 50000,
    "wire_deposit_min_limit": "none stated by OANDA source",
    "wire_deposit_max_limit": "none stated by OANDA source",
}


def evaluate_oanda_funding_rail_readiness_v1(
    payload: dict | None = None,
) -> dict:
    """Evaluate OANDA funding rail readiness from sanitized owner fields."""

    source = payload if isinstance(payload, Mapping) else {}
    method = _deposit_method(source)
    lump_sum_amount = _decimal_or_none(source.get("intended_lump_sum_amount"))
    amount_present = _present(source.get("intended_lump_sum_amount"))
    funding_date_present = _present(source.get("intended_funding_date"))
    account_name_match = source.get("account_name_match")
    same_name_proof_present = source.get("same_name_bank_proof_present") is True
    third_party_payment = source.get("third_party_payment") is True
    margin_used = _decimal_or_none(source.get("margin_used"))
    sensitive_data_present = _contains_sensitive_key(source)

    missing_information: list[str] = []
    blocked_reasons: list[str] = []

    if method == "unknown":
        blocked_reasons.append("missing_deposit_method")
        missing_information.append("intended_deposit_method")

    if third_party_payment:
        blocked_reasons.append("third_party_payment_blocked")

    if sensitive_data_present:
        blocked_reasons.append("sensitive_financial_data_provided")

    if not amount_present:
        missing_information.extend(
            ["intended_lump_sum_amount", "intended_funding_date"]
        )
    elif lump_sum_amount is None or lump_sum_amount <= 0:
        blocked_reasons.append("intended_lump_sum_amount_invalid")

    if amount_present and not funding_date_present:
        missing_information.append("intended_funding_date")

    if method in {"ach", *WIRE_METHODS} and account_name_match is False:
        blocked_reasons.append("account_name_match_required")
    if method in WIRE_METHODS and not same_name_proof_present:
        blocked_reasons.append("same_name_bank_proof_required")

    if method == "debit_card" and _amount_exceeds(lump_sum_amount, "20000"):
        blocked_reasons.append("debit_card_monthly_limit_exceeded")
    if method == "ach" and _amount_exceeds(lump_sum_amount, "50000"):
        blocked_reasons.append("ach_transaction_limit_exceeded")

    debit_card_blockers = _method_blockers(
        method,
        "debit_card",
        blocked_reasons,
        {
            "missing_deposit_method",
            "third_party_payment_blocked",
            "sensitive_financial_data_provided",
            "debit_card_monthly_limit_exceeded",
            "intended_lump_sum_amount_invalid",
        },
    )
    ach_blockers = _method_blockers(
        method,
        "ach",
        blocked_reasons,
        {
            "missing_deposit_method",
            "third_party_payment_blocked",
            "sensitive_financial_data_provided",
            "ach_transaction_limit_exceeded",
            "account_name_match_required",
            "intended_lump_sum_amount_invalid",
        },
    )
    wire_blockers = _method_blockers(
        method,
        WIRE_METHODS,
        blocked_reasons,
        {
            "missing_deposit_method",
            "third_party_payment_blocked",
            "sensitive_financial_data_provided",
            "account_name_match_required",
            "same_name_bank_proof_required",
            "intended_lump_sum_amount_invalid",
        },
    )

    deposit_readiness = {
        "status": _status_for(blocked_reasons),
        "intended_deposit_method": method,
        "allowed_methods": sorted(DEPOSIT_METHODS),
        "method_facts": {
            "debit_card": "virtually instant deposit; monthly cap applies",
            "wire_domestic": "domestic wire deposit processing is 1 to 3 business days",
            "wire_international": "international wire deposit processing is up to 5 business days",
            "ach": "ACH deposit processing is up to 6 days and transaction cap applies",
        },
        "blockers": _unique(
            reason
            for reason in blocked_reasons
            if reason
            in {
                "missing_deposit_method",
                "third_party_payment_blocked",
                "sensitive_financial_data_provided",
                "intended_lump_sum_amount_invalid",
                "account_name_match_required",
                "same_name_bank_proof_required",
                "debit_card_monthly_limit_exceeded",
                "ach_transaction_limit_exceeded",
            }
        ),
    }

    withdrawal_readiness = _withdrawal_readiness(
        source=source,
        method=method,
        margin_used=margin_used,
        sensitive_data_present=sensitive_data_present,
        third_party_payment=third_party_payment,
    )

    margin_call_review_required = margin_used is not None and margin_used > 0
    if margin_call_review_required:
        blocked_reasons.append("margin_used_review_required")
        withdrawal_readiness["blockers"].append("margin_used_review_required")

    fee_review_required = True
    lump_sum_readiness = _lump_sum_readiness(
        method=method,
        amount_present=amount_present,
        amount=lump_sum_amount,
        funding_date_present=funding_date_present,
        blocked_reasons=blocked_reasons,
    )

    blocked_reasons = _unique(blocked_reasons)
    missing_information = _unique(missing_information)

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "broker_api_allowed": False,
        "bank_access_allowed": False,
        "deposit_readiness": deposit_readiness,
        "withdrawal_readiness": withdrawal_readiness,
        "wire_readiness": {
            "status": _status_for(wire_blockers),
            "same_name_bank_proof_required": True,
            "same_name_bank_proof_present": same_name_proof_present,
            "fee_review_required": True,
            "no_stated_oanda_deposit_min_or_max": True,
            "blockers": _unique(wire_blockers),
        },
        "ach_readiness": {
            "status": _status_for(ach_blockers),
            "per_transaction_limit_usd": LIMITS[
                "ach_per_transaction_limit_usd"
            ],
            "fee": "no fee and no minimum stated by OANDA",
            "same_name_account_required": True,
            "blockers": _unique(ach_blockers),
        },
        "debit_card_readiness": {
            "status": _status_for(debit_card_blockers),
            "monthly_deposit_limit_usd": LIMITS[
                "debit_card_monthly_deposit_limit_usd"
            ],
            "deposit_processing": PROCESSING_TIME_ESTIMATES[
                "debit_card_deposit"
            ],
            "withdrawal_limit_rule": (
                "debit card withdrawals cannot exceed the total originally "
                "deposited using debit card"
            ),
            "blockers": _unique(debit_card_blockers),
        },
        "lump_sum_readiness": lump_sum_readiness,
        "same_name_bank_required": True,
        "third_party_payment_blocked": third_party_payment,
        "withdrawal_hierarchy": _withdrawal_hierarchy(),
        "processing_time_estimates": dict(PROCESSING_TIME_ESTIMATES),
        "limits": dict(LIMITS),
        "fee_review_required": fee_review_required,
        "margin_call_review_required": margin_call_review_required,
        "missing_information": missing_information,
        "blocked_reasons": blocked_reasons,
        "owner_decision_required": True,
        "safe_next_action": _safe_next_action(
            sensitive_data_present=sensitive_data_present,
            third_party_payment=third_party_payment,
            amount_present=amount_present,
            blocked_reasons=blocked_reasons,
        ),
        "safety": _safety(sensitive_data_present),
    }


def _withdrawal_readiness(
    *,
    source: Mapping[str, Any],
    method: str,
    margin_used: Decimal | None,
    sensitive_data_present: bool,
    third_party_payment: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    withdrawal_method = _normalized_key(source.get("intended_withdrawal_method"))
    withdrawal_amount = _decimal_or_none(source.get("intended_withdrawal_amount"))
    original_debit_card_deposit_total = _decimal_or_none(
        source.get("original_debit_card_deposit_total")
    )

    if sensitive_data_present:
        blockers.append("sensitive_financial_data_provided")
    if third_party_payment:
        blockers.append("third_party_payment_blocked")
    if withdrawal_method == "debit_card" and (
        withdrawal_amount is not None
        and original_debit_card_deposit_total is not None
        and withdrawal_amount > original_debit_card_deposit_total
    ):
        blockers.append("debit_card_withdrawal_original_deposit_limit_exceeded")

    return {
        "status": _status_for(blockers),
        "general_method_rule": "withdrawal method generally follows deposit method",
        "intended_deposit_method": method,
        "available_withdrawal_rule": "account balance minus margin used",
        "margin_used_present": margin_used is not None,
        "margin_used_review_required": margin_used is not None and margin_used > 0,
        "keep_sufficient_funds_warning": (
            "owner must keep sufficient funds to avoid margin calls on open trades"
        ),
        "same_name_bank_required_for_wire": True,
        "profits_or_remaining_funds_rule": (
            "profits or remaining funds may need an alternative method such as bank wire"
        ),
        "blockers": blockers,
    }


def _lump_sum_readiness(
    *,
    method: str,
    amount_present: bool,
    amount: Decimal | None,
    funding_date_present: bool,
    blocked_reasons: Sequence[str],
) -> dict[str, Any]:
    if not amount_present:
        return {
            "status": "PLANNING_ONLY",
            "amount_review": "owner_has_not_provided_amount",
            "funding_date_present": funding_date_present,
            "approval": "not_approved_not_recommended",
            "route_constraints_only": True,
            "blockers": [],
        }

    blockers = [
        reason
        for reason in blocked_reasons
        if reason
        in {
            "debit_card_monthly_limit_exceeded",
            "ach_transaction_limit_exceeded",
            "same_name_bank_proof_required",
            "account_name_match_required",
            "intended_lump_sum_amount_invalid",
            "third_party_payment_blocked",
            "sensitive_financial_data_provided",
        }
    ]
    return {
        "status": "BLOCKED_ROUTE_CONSTRAINTS" if blockers else "ROUTE_CONSTRAINTS_ONLY",
        "amount_review": "present_not_approved_not_recommended",
        "funding_date_present": funding_date_present,
        "intended_deposit_method": method,
        "approval": "not_approved_not_recommended",
        "route_constraints_only": True,
        "no_deposit_amount_recommendation": True,
        "blockers": _unique(blockers),
    }


def _withdrawal_hierarchy() -> dict[str, Any]:
    return {
        "multiple_method_rule": (
            "if multiple methods were used, debit card deposit amounts must be "
            "exhausted first, then bank wire"
        ),
        "debit_card_cap_rule": (
            "debit card withdrawals cannot exceed the total originally deposited "
            "using debit card"
        ),
        "profits_or_remaining_funds_rule": (
            "remaining funds or profits may be withdrawn by an alternative method "
            "such as bank wire"
        ),
        "wire_same_name_bank_required": True,
        "available_withdrawal_rule": "account balance minus margin used",
    }


def _safety(sensitive_data_present: bool) -> dict[str, bool]:
    return {
        "no_transfer_tool": True,
        "no_deposit_tool": True,
        "no_withdrawal_tool": True,
        "no_bank_automation": True,
        "no_broker_api_execution": True,
        "no_live_trading": True,
        "no_financial_advice": True,
        "credentials_rejected": sensitive_data_present,
        "credential_values_echoed": False,
        "owner_only_money_decision": True,
    }


def _safe_next_action(
    *,
    sensitive_data_present: bool,
    third_party_payment: bool,
    amount_present: bool,
    blocked_reasons: Sequence[str],
) -> str:
    if sensitive_data_present:
        return (
            "Owner must remove sensitive financial data and use only redacted "
            "readiness fields before rerunning; do not initiate money movement."
        )
    if third_party_payment:
        return (
            "Stop: third-party payments are blocked; use only same-name owner "
            "readiness review fields."
        )
    if not amount_present:
        return (
            "owner must decide amount/date outside AIOS and rerun readiness; "
            "AIOS must not recommend an amount or initiate money movement."
        )
    if blocked_reasons:
        return (
            "Resolve blocked readiness fields and verify OANDA and bank fees, "
            "timing, same-name proof, and margin impact before any owner decision."
        )
    return (
        "Owner may review route constraints and ask OANDA or the bank verification "
        "questions; AIOS does not approve or initiate funding."
    )


def _method_blockers(
    method: str,
    target_method: str | set[str],
    blocked_reasons: Sequence[str],
    relevant_reasons: set[str],
) -> list[str]:
    if method == "unknown":
        return ["missing_deposit_method"]
    target_methods = {target_method} if isinstance(target_method, str) else target_method
    if method not in target_methods:
        return []
    return [reason for reason in blocked_reasons if reason in relevant_reasons]


def _deposit_method(source: Mapping[str, Any]) -> str:
    method = _normalized_key(source.get("intended_deposit_method"))
    return method if method in DEPOSIT_METHODS else "unknown"


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            if _normalized_key(raw_key) in SENSITIVE_KEYS:
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _amount_exceeds(value: Decimal | None, threshold: str) -> bool:
    return value is not None and value > Decimal(threshold)


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    return parsed if parsed.is_finite() else None


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _status_for(blockers: Sequence[str]) -> str:
    return "BLOCKED" if blockers else "REVIEW_ONLY_READY"


def _normalized_key(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


__all__ = [
    "LIMITS",
    "MODE",
    "PROCESSING_TIME_ESTIMATES",
    "SCHEMA",
    "evaluate_oanda_funding_rail_readiness_v1",
]
