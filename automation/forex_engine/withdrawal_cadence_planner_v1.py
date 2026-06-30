"""Read-only withdrawal cadence planner for capital review scheduling."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


SCHEMA = "AIOS_WITHDRAWAL_CADENCE_PLANNER_V1"
MODE = "READ_ONLY_WITHDRAWAL_CADENCE_REVIEW"

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


def evaluate_withdrawal_cadence_planner_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate weekly/monthly/bimonthly/no-withdrawal review cadence in read-only mode."""

    source = payload if isinstance(payload, Mapping) else {}
    if _contains_sensitive_key(source):
        return _sensitive_block_payload()

    if source is None:
        source = {}

    withdrawal_bucket_status = (
        source.get("withdrawal_bucket_status")
        if isinstance(source.get("withdrawal_bucket_status"), Mapping)
        else {}
    )
    withdrawal_eligible_amount = _decimal_or_zero(
        source.get("withdrawal_eligible_amount"),
        default=withdrawal_bucket_status.get("eligible_amount", Decimal("0")),
    )
    min_withdrawal_threshold = _decimal_or_zero(
        source.get("min_withdrawal_threshold"),
        default=Decimal("0"),
    )
    max_withdrawal_fee_tolerance = _decimal_or_zero(
        source.get("max_withdrawal_fee_tolerance"),
        default=Decimal("12"),
    )

    margin_used = _decimal_or_zero(source.get("margin_used"))
    open_risk = _decimal_or_zero(source.get("open_risk"))
    daily_loss_used = _decimal_or_zero(source.get("daily_loss_used"))
    max_daily_loss = _decimal_or_zero(source.get("max_daily_loss"), default=Decimal("0"))
    max_drawdown_percent = _decimal_or_zero(source.get("max_drawdown_percent"), default=Decimal("0"))
    max_drawdown_limit = _decimal_or_zero(source.get("max_drawdown_limit"), default=Decimal("20"))
    profit_consistency_score = _decimal_or_zero(
        source.get("profit_consistency_score"),
        default=Decimal("1"),
    )
    min_withdrawal_consistency_score = _decimal_or_zero(
        source.get("min_withdrawal_consistency_score"),
        default=Decimal("0.65"),
    )
    next_review_date = source.get("next_review_date")

    reserve_requirements = _extract_reserve_requirements(source)
    rail_readiness = _extract_rail_readiness(source.get("rail_registry"))
    reserved_ok = reserve_requirements["operating_reserve_met"] and reserve_requirements[
        "tax_reserve_met"
    ]

    margin_or_open_risk_block = margin_used > 0 or open_risk > 0
    daily_loss_stop_active = max_daily_loss > 0 and daily_loss_used >= max_daily_loss

    risk_blocks: list[str] = []
    if margin_or_open_risk_block:
        risk_blocks.append("margin_or_open_risk_block")
    if daily_loss_stop_active:
        risk_blocks.append("daily_loss_stop_active")
    if max_drawdown_percent > max_drawdown_limit and max_drawdown_limit >= 0:
        risk_blocks.append("drawdown_exceeded_limit")
    if not reserve_requirements["operating_reserve_met"]:
        risk_blocks.append("operating_reserve_underfunded")
    if not reserve_requirements["tax_reserve_met"]:
        risk_blocks.append("tax_reserve_underfunded")
    if not rail_readiness["same_name_proof_satisfied"]:
        risk_blocks.append("rail_proof_missing")
    if rail_readiness["info_present"] and not rail_readiness["eligible_count"]:
        risk_blocks.append("no_eligible_rails")

    fee_average = _decimal_or_zero(rail_readiness["average_fee_usd"])
    low_fee_preferred = fee_average <= max_withdrawal_fee_tolerance
    profit_consistent = (
        profit_consistency_score >= min_withdrawal_consistency_score
        and withdrawal_eligible_amount > 0
    )

    weekly_plan = _build_weekly_plan(
        withdrawal_eligible_amount=withdrawal_eligible_amount,
        min_withdrawal_threshold=min_withdrawal_threshold,
        profit_consistent=profit_consistent,
        reserved_ok=reserved_ok,
        same_name_proof_ok=rail_readiness["same_name_proof_satisfied"],
        low_fee_preferred=low_fee_preferred,
        no_risk=not risk_blocks,
        next_review_date=next_review_date,
    )
    monthly_plan = _build_monthly_plan(
        withdrawal_eligible_amount=withdrawal_eligible_amount,
        min_withdrawal_threshold=min_withdrawal_threshold,
        reserved_ok=reserved_ok,
        no_risk=not risk_blocks,
        next_review_date=next_review_date,
    )
    bimonthly_plan = _build_bimonthly_plan(
        withdrawal_eligible_amount=withdrawal_eligible_amount,
        min_withdrawal_threshold=min_withdrawal_threshold,
        risk_blocks=risk_blocks,
        fee_average=fee_average,
        max_withdrawal_fee_tolerance=max_withdrawal_fee_tolerance,
        profit_consistency_score=profit_consistency_score,
        min_withdrawal_consistency_score=min_withdrawal_consistency_score,
        next_review_date=next_review_date,
    )
    no_withdrawal_plan = _build_no_withdrawal_plan(
        withdrawal_eligible_amount=withdrawal_eligible_amount,
        min_withdrawal_threshold=min_withdrawal_threshold,
        risk_blocks=risk_blocks,
    )

    if weekly_plan["eligible"] and not risk_blocks and low_fee_preferred:
        recommended_cadence = "weekly"
    elif monthly_plan["eligible"] and not risk_blocks:
        recommended_cadence = "monthly"
    elif bimonthly_plan["eligible"] and not daily_loss_stop_active and not margin_or_open_risk_block:
        recommended_cadence = "bimonthly"
    else:
        recommended_cadence = "no_withdrawal"

    cadence_candidates: list[str] = ["no_withdrawal"]
    if weekly_plan["eligible"]:
        cadence_candidates.append("weekly")
    if monthly_plan["eligible"]:
        cadence_candidates.append("monthly")
    if bimonthly_plan["eligible"]:
        cadence_candidates.append("bimonthly")

    withdrawal_eligibility = {
        "eligible_for_owner_review": recommended_cadence != "no_withdrawal",
        "status": (
            "eligible_for_owner_review"
            if recommended_cadence != "no_withdrawal"
            else "not_eligible"
        ),
        "eligible_amount": _to_float(withdrawal_eligible_amount),
        "required_threshold": _to_float(min_withdrawal_threshold),
        "margin_or_open_risk_block": margin_or_open_risk_block,
        "daily_loss_stop_active": daily_loss_stop_active,
        "rail_proof_missing": not rail_readiness["same_name_proof_satisfied"],
    }

    missing_information: list[str] = []
    if "withdrawal_bucket_status" not in source and "withdrawal_eligible_amount" not in source:
        missing_information.append("withdrawal_eligible_amount")
    if "rail_registry" not in source:
        missing_information.append("rail_readiness")
    if source.get("min_withdrawal_threshold") is None:
        missing_information.append("min_withdrawal_threshold")

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "cadence_candidates": _unique(cadence_candidates),
        "recommended_cadence": recommended_cadence,
        "weekly_plan": weekly_plan,
        "monthly_plan": monthly_plan,
        "bimonthly_plan": bimonthly_plan,
        "no_withdrawal_plan": no_withdrawal_plan,
        "withdrawal_eligibility": withdrawal_eligibility,
        "reserve_requirements": _safe_reserve_output(reserve_requirements),
        "risk_blocks": _unique(risk_blocks),
        "fee_efficiency": {
            "fee_average_usd": _to_float(fee_average),
            "low_fee_threshold_usd": _to_float(max_withdrawal_fee_tolerance),
            "lowest_fee_rail": rail_readiness["lowest_cost_rail"],
            "fastest_rail": rail_readiness["fastest_rail"],
            "low_fee_preferred": low_fee_preferred,
        },
        "rail_readiness": {
            "eligible_count": rail_readiness["eligible_count"],
            "eligible_rails": rail_readiness["eligible_rails"],
            "same_name_proof_required": rail_readiness["same_name_proof_required"],
            "same_name_proof_satisfied": rail_readiness["same_name_proof_satisfied"],
            "blocked_reasons": rail_readiness["blocked_reasons"],
        },
        "owner_decision_required": True,
        "missing_information": _unique(missing_information),
        "blocked_reasons": _unique(
            [*risk_blocks, *weekly_plan["blocked_reasons"], *monthly_plan["blocked_reasons"]]
        ),
        "safe_next_action": _safe_next_action(
            recommended_cadence=recommended_cadence,
            risk_blocks=risk_blocks,
            withdrawal_eligible_amount=withdrawal_eligible_amount,
            min_withdrawal_threshold=min_withdrawal_threshold,
        ),
        "safety": {
            "no_transfer": True,
            "no_bank_automation": True,
            "no_broker_api_execution": True,
            "manual_execution_only": True,
            "owner_only_money_decision": True,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
        },
    }


def _build_weekly_plan(
    *,
    withdrawal_eligible_amount: Decimal,
    min_withdrawal_threshold: Decimal,
    profit_consistent: bool,
    reserved_ok: bool,
    same_name_proof_ok: bool,
    low_fee_preferred: bool,
    no_risk: bool,
    next_review_date: Any,
) -> dict[str, Any]:
    blocked: list[str] = []
    if not profit_consistent:
        blocked.append("profit_not_consistent")
    if not reserved_ok:
        blocked.append("reserve_requirement_not_met")
    if not same_name_proof_ok:
        blocked.append("rail_same_name_proof_missing")
    if not low_fee_preferred:
        blocked.append("weekly_fee_too_high")
    if not no_risk:
        blocked.append("risk_block")
    if withdrawal_eligible_amount < min_withdrawal_threshold:
        blocked.append("below_min_withdrawal_threshold")
    eligible = not blocked
    return {
        "cadence": "weekly",
        "eligible": eligible,
        "status": "REVIEW_ONLY_ELIGIBLE" if eligible else "BLOCKED",
        "selection_gate": (
            "eligible_for_owner_review" if eligible else "not_eligible"
        ),
        "withdrawal_recommendation": (
            "eligible_for_owner_review" if eligible else "not eligible for owner review"
        ),
        "recommended_amount": _to_float(min_withdrawal_threshold) if eligible else 0.0,
        "recommended_review_day": "Friday",
        "next_review_date": next_review_date,
        "blocked_reasons": blocked,
    }


def _build_monthly_plan(
    *,
    withdrawal_eligible_amount: Decimal,
    min_withdrawal_threshold: Decimal,
    reserved_ok: bool,
    no_risk: bool,
    next_review_date: Any,
) -> dict[str, Any]:
    blocked: list[str] = []
    if not reserved_ok:
        blocked.append("reserve_requirement_not_met")
    if not no_risk:
        blocked.append("risk_block")
    if withdrawal_eligible_amount < min_withdrawal_threshold:
        blocked.append("below_min_withdrawal_threshold")
    if not withdrawal_eligible_amount > 0:
        blocked.append("no_profit_to_withdraw")
    eligible = (
        not blocked
        and withdrawal_eligible_amount >= max(min_withdrawal_threshold, Decimal("0"))
        and not (withdrawal_eligible_amount == Decimal("0"))
    )
    return {
        "cadence": "monthly",
        "eligible": eligible,
        "status": "REVIEW_ONLY_ELIGIBLE" if eligible else "BLOCKED",
        "selection_gate": (
            "eligible_for_owner_review" if eligible else "not_eligible"
        ),
        "withdrawal_recommendation": (
            "eligible_for_owner_review" if eligible else "not eligible for owner review"
        ),
        "recommended_amount": _to_float(min_withdrawal_threshold * Decimal("2")) if eligible else 0.0,
        "recommended_review_day": "Monday",
        "next_review_date": next_review_date,
        "blocked_reasons": blocked,
    }


def _build_bimonthly_plan(
    *,
    withdrawal_eligible_amount: Decimal,
    min_withdrawal_threshold: Decimal,
    risk_blocks: Sequence[str],
    fee_average: Decimal,
    max_withdrawal_fee_tolerance: Decimal,
    profit_consistency_score: Decimal,
    min_withdrawal_consistency_score: Decimal,
    next_review_date: Any,
) -> dict[str, Any]:
    blocked: list[str] = []
    if not withdrawal_eligible_amount or withdrawal_eligible_amount < min_withdrawal_threshold:
        blocked.append("below_min_withdrawal_threshold")
    fee_pressure = fee_average > max_withdrawal_fee_tolerance
    evidence_pressure = profit_consistency_score < min_withdrawal_consistency_score
    if not (fee_pressure or evidence_pressure):
        blocked.append("fees_and_evidence_support_faster_frequency")
    if any(
        item in {"margin_or_open_risk_block", "daily_loss_stop_active", "drawdown_exceeded_limit"}
        for item in risk_blocks
    ):
        blocked.append("risk_block")
    eligible = not blocked and withdrawal_eligible_amount > 0
    return {
        "cadence": "bimonthly",
        "eligible": eligible,
        "status": "REVIEW_ONLY_ELIGIBLE" if eligible else "BLOCKED",
        "selection_gate": (
            "eligible_for_owner_review" if eligible else "not_eligible"
        ),
        "withdrawal_recommendation": (
            "eligible_for_owner_review" if eligible else "not eligible for owner review"
        ),
        "recommended_amount": _to_float(withdrawal_eligible_amount) if eligible else 0.0,
        "recommended_review_day": "Wednesday",
        "next_review_date": next_review_date,
        "fee_pressure": "fees_high_or_evidence_weak_prefer_bimonthly" if fee_pressure or evidence_pressure else "no_fee_or_evidence_pressure",
        "blocked_reasons": blocked,
    }


def _build_no_withdrawal_plan(
    *,
    withdrawal_eligible_amount: Decimal,
    min_withdrawal_threshold: Decimal,
    risk_blocks: Sequence[str],
) -> dict[str, Any]:
    blocked: list[str] = []
    if withdrawal_eligible_amount <= 0:
        blocked.append("no_profit_or_below_minimum")
    elif withdrawal_eligible_amount < min_withdrawal_threshold:
        blocked.append("below_min_withdrawal_threshold")
    blocked.extend(risk_blocks)
    if not blocked:
        blocked.append("manual_no_withdrawal")
    return {
        "cadence": "no_withdrawal",
        "eligible": False,
        "status": "NO_WITHDRAWAL_REVIEW",
        "selection_gate": "not_eligible",
        "withdrawal_recommendation": "not_eligible",
        "recommended_amount": 0.0,
        "recommended_review_day": None,
        "next_review_date": None,
        "blocked_reasons": _unique(blocked),
    }


def _extract_reserve_requirements(source: Mapping[str, Any]) -> dict[str, Decimal | bool]:
    balance_bucket = _decimal_or_zero(source.get("balance_bucket"), default=Decimal("0"))
    operating_reserve_bucket = _decimal_or_zero(
        source.get("operating_reserve_bucket"), default=Decimal("0")
    )
    tax_reserve_bucket = _decimal_or_zero(source.get("tax_reserve_bucket"), default=Decimal("0"))
    operating_percent = (
        _decimal_or_zero(source.get("operating_reserve_percent"), default=Decimal("10"))
        if source.get("operating_reserve_percent") is not None
        else None
    )
    tax_percent = (
        _decimal_or_zero(source.get("tax_reserve_percent"), default=Decimal("10"))
        if source.get("tax_reserve_percent") is not None
        else None
    )
    operating_minimum = (
        (balance_bucket * operating_percent / Decimal("100"))
        if operating_percent is not None
        else Decimal("0")
    )
    tax_minimum = (
        (balance_bucket * tax_percent / Decimal("100"))
        if tax_percent is not None
        else Decimal("0")
    )
    return {
        "operating_reserve_current": operating_reserve_bucket,
        "tax_reserve_current": tax_reserve_bucket,
        "operating_reserve_percent": operating_percent or Decimal("0"),
        "tax_reserve_percent": tax_percent or Decimal("0"),
        "operating_reserve_minimum": operating_minimum,
        "tax_reserve_minimum": tax_minimum,
        "operating_reserve_met": operating_reserve_bucket >= operating_minimum,
        "tax_reserve_met": tax_reserve_bucket >= tax_minimum,
        "protected_buckets": ["tax_reserve_bucket", "operating_reserve_bucket"],
    }


def _extract_rail_readiness(rail_payload: Any) -> dict[str, Any]:
    if not isinstance(rail_payload, Mapping):
        return {
            "eligible_count": 0,
            "eligible_rails": [],
            "lowest_cost_rail": None,
            "fastest_rail": None,
            "average_fee_usd": Decimal("0"),
            "info_present": False,
            "same_name_proof_required": False,
            "same_name_proof_satisfied": True,
            "blocked_reasons": [],
        }

    registry = rail_payload.get("rail_registry", [])
    all_ids = [str(rail.get("rail_id")) for rail in registry if isinstance(rail, Mapping)]
    eligible_ids = [
        str(item)
        for item in rail_payload.get("eligible_rails", [])
        if isinstance(item, str) or isinstance(item, int)
    ]
    if not eligible_ids and rail_payload.get("eligible_rails") is not None:
        eligible_ids = [str(item) for item in all_ids if isinstance(item, str)]
    registry_map = {
        str(item.get("rail_id")): item
        for item in registry
        if isinstance(item, Mapping) and item.get("rail_id") is not None
    }
    eligible = [
        registry_map[rail_id]
        for rail_id in eligible_ids
        if str(rail_id) in registry_map
    ]
    fees = [_decimal_or_zero(rail.get("fee_estimate_usd"), default=Decimal("0")) for rail in eligible]
    average_fee = sum(fees) / len(fees) if fees else Decimal("0")
    same_name_required = bool(
        _to_bool(rail_payload.get("same_name_proof_required", False))
        or any(
            (
                isinstance(rail, Mapping)
                and bool(rail.get("withdrawal_supported"))
                and not bool(rail.get("same_name_verified"))
            )
            for rail in eligible
        )
    )
    proof_status = rail_payload.get("same_name_proof_status", {})
    proof_satisfied = bool(proof_status.get("satisfied", True)) if proof_status else not same_name_required
    if not proof_status and same_name_required:
        proof_satisfied = False

    lowest = None
    fastest = None
    if eligible:
        lowest = min(
            eligible,
            key=lambda rail: (
                _decimal_or_zero(rail.get("fee_estimate_usd"), default=Decimal("999999")),
                _processing_time_to_days(
                    rail.get("processing_time_estimate"),
                ),
                str(rail.get("rail_id")),
            ),
        )
        fastest = min(
            eligible,
            key=lambda rail: (
                _processing_time_to_days(rail.get("processing_time_estimate")),
                _decimal_or_zero(rail.get("fee_estimate_usd"), default=Decimal("999999")),
                str(rail.get("rail_id")),
            ),
        )

    same_name_proof_required = bool(same_name_required)
    blocked_reasons = []
    if same_name_required and not proof_satisfied:
        blocked_reasons.append("rail_proof_missing")

    return {
        "eligible_count": len(eligible),
        "eligible_rails": eligible,
        "info_present": True,
        "lowest_cost_rail": {"rail_id": str(lowest["rail_id"])} if isinstance(lowest, Mapping) else None,
        "fastest_rail": {"rail_id": str(fastest["rail_id"])} if isinstance(fastest, Mapping) else None,
        "average_fee_usd": average_fee,
        "same_name_proof_required": same_name_proof_required,
        "same_name_proof_satisfied": proof_satisfied,
        "blocked_reasons": blocked_reasons,
    }


def _processing_time_to_days(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).lower() if value is not None else ""
    if "instant" in text:
        return 0.0
    if "same" in text and "day" in text:
        return 0.5
    if "1" in text and "day" in text:
        return 1.0
    if "2" in text and "day" in text:
        return 2.0
    if "3" in text and "day" in text:
        return 3.0
    if "5" in text and "day" in text:
        return 5.0
    if "business day" in text:
        return 2.0
    return 2.0


def _safe_reserve_output(requirements: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "operating_reserve_current": _to_float(requirements["operating_reserve_current"]),
        "tax_reserve_current": _to_float(requirements["tax_reserve_current"]),
        "operating_reserve_percent": _to_float(requirements["operating_reserve_percent"]),
        "tax_reserve_percent": _to_float(requirements["tax_reserve_percent"]),
        "operating_reserve_minimum": _to_float(requirements["operating_reserve_minimum"]),
        "tax_reserve_minimum": _to_float(requirements["tax_reserve_minimum"]),
        "operating_reserve_met": bool(requirements["operating_reserve_met"]),
        "tax_reserve_met": bool(requirements["tax_reserve_met"]),
        "protected_buckets": requirements.get("protected_buckets", []),
    }


def _safe_next_action(
    *,
    recommended_cadence: str,
    risk_blocks: Sequence[str],
    withdrawal_eligible_amount: Decimal,
    min_withdrawal_threshold: Decimal,
) -> str:
    if risk_blocks:
        return (
            "Owner review only. Resolve risk/rail/reserve blockers and rerun "
            "withdrawal cadence planning. AIOS does not move money."
        )
    if recommended_cadence == "no_withdrawal":
        return (
            "No-withdrawal recommendation. Continue monitoring and rerun when conditions improve."
        )
    if withdrawal_eligible_amount < min_withdrawal_threshold:
        return (
            "Amount below minimum threshold. Continue monitoring and rerun when threshold is met."
        )
    return (
        f"Owner may review {recommended_cadence} plan. AIOS does not initiate movement."
    )


def _sensitive_block_payload() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "cadence_candidates": ["no_withdrawal"],
        "recommended_cadence": "no_withdrawal",
        "weekly_plan": {"cadence": "weekly", "eligible": False, "selection_gate": "not_eligible"},
        "monthly_plan": {"cadence": "monthly", "eligible": False, "selection_gate": "not_eligible"},
        "bimonthly_plan": {
            "cadence": "bimonthly",
            "eligible": False,
            "selection_gate": "not_eligible",
        },
        "no_withdrawal_plan": {
            "cadence": "no_withdrawal",
            "eligible": False,
            "selection_gate": "not_eligible",
        },
        "withdrawal_eligibility": {
            "eligible_for_owner_review": False,
            "status": "not_eligible",
        },
        "reserve_requirements": {},
        "risk_blocks": ["sensitive_financial_data_provided"],
        "fee_efficiency": {},
        "rail_readiness": {"eligible_count": 0},
        "owner_decision_required": True,
        "missing_information": ["sensitive_financial_data_removed"],
        "blocked_reasons": ["sensitive_financial_data_provided"],
        "safe_next_action": (
            "Stop and remove sensitive financial fields. AIOS only reviews after sanitization."
        ),
        "safety": {
            "no_transfer": True,
            "no_bank_automation": True,
            "no_broker_api_execution": True,
            "manual_execution_only": True,
            "owner_only_money_decision": True,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
        },
    }


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            key = str(raw_key).strip().lower()
            if any(token in key for token in SENSITIVE_KEYS):
                return True
            if _contains_sensitive_key(nested):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _decimal_or_zero(value: Any, default: Decimal | None = None) -> Decimal:
    if value is None:
        return default if default is not None else Decimal("0")
    if isinstance(value, bool):
        return default if default is not None else Decimal("0")
    try:
        parsed = Decimal(str(value).strip().replace(",", "").replace("%", ""))
    except (InvalidOperation, ValueError, AttributeError, TypeError):
        return default if default is not None else Decimal("0")
    if parsed.is_nan() or parsed.is_infinite():
        return default if default is not None else Decimal("0")
    return parsed


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _to_float(value: Decimal | int | float | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


__all__ = ["SCHEMA", "MODE", "evaluate_withdrawal_cadence_planner_v1"]
