"""Read-only owner-gated withdrawal plan composer for AIOS capital rails."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any


SCHEMA = "AIOS_CAPITAL_RAIL_WITHDRAWAL_PLAN_V1"
MODE = "READ_ONLY_OWNER_GATED_WITHDRAWAL_PLAN"


def evaluate_capital_rail_withdrawal_plan_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Compose an owner-gated withdrawal plan from purge, rail, cadence, and OANDA status."""

    source = payload if isinstance(payload, Mapping) else {}
    if _contains_sensitive_key(source):
        return {
            "schema": SCHEMA,
            "mode": MODE,
            "read_only": True,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "owner_decision_required": True,
            "withdrawal_plan_status": "BLOCKED_BY_SENSITIVE_DATA",
            "eligible_for_owner_review": False,
            "recommended_cadence": "no_withdrawal",
            "withdrawal_bucket": {},
            "protected_buckets": [],
            "reserve_summary": {},
            "rail_summary": {},
            "selected_review_rail": None,
            "fee_summary": {},
            "timing_summary": {},
            "withdrawal_hierarchy_review": {},
            "margin_call_review_required": False,
            "bucket_purge_required": False,
            "rail_proof_required": False,
            "owner_gate": _owner_gate(),
            "manual_execution_only": True,
            "blocked_reasons": ["sensitive_financial_data_provided"],
            "missing_information": ["remove_sensitive_financial_data"],
            "safe_next_action": (
                "Stop: sensitive financial fields were supplied. Remove credentials "
                "and rerun read-only plan generation."
            ),
            "audit_record": {
                "status": "BLOCKED_BY_SENSITIVE_DATA",
                "as_of": _as_text(source.get("as_of_date")),
            },
            "safety": _safety(),
        }

    bucket_payload = _coerce(source.get("bucket_purge_controller"), source)
    rail_payload = _coerce(source.get("rail_registry"), source)
    cadence_payload = _coerce(source.get("withdrawal_cadence_planner"), source)
    oanda_payload = _coerce(source.get("oanda_funding_rail_readiness"), source)

    reserve_summary = _extract_reserves(bucket_payload, rail_payload)
    bucket_summary = _extract_bucket(bucket_payload)
    rail_summary = _extract_rail_summary(rail_payload)
    cadence_summary = _extract_cadence_summary(cadence_payload)

    withdrawal_plan_status = _plan_status(
        bucket_payload=bucket_payload,
        rail_payload=rail_payload,
        cadence_payload=cadence_payload,
        oanda_payload=oanda_payload,
        reserve_summary=reserve_summary,
    )

    eligible_for_owner_review = withdrawal_plan_status == "READY_FOR_OWNER_REVIEW"
    recommended_cadence = cadence_summary.get("recommended_cadence", "no_withdrawal")

    selected_review_rail = None
    if isinstance(rail_payload.get("selected_review_rail"), Mapping):
        selected = rail_payload["selected_review_rail"]
        if _rail_is_eligible(selected, rail_payload):
            selected_review_rail = selected
    elif isinstance(cadence_payload.get("selected_review_rail"), Mapping):
        selected = cadence_payload["selected_review_rail"]
        if _rail_is_eligible(selected, rail_payload):
            selected_review_rail = selected
    if selected_review_rail is None:
        selected_review_rail = _best_rail_from_registry(
            rail_summary.get("eligible_rail_ids"),
            source_preference="lowest_cost",
        )

    blocked_reasons = _gather_blockers(
        bucket_payload=bucket_payload,
        rail_payload=rail_payload,
        cadence_payload=cadence_payload,
        oanda_payload=oanda_payload,
    )
    missing_information = _missing_information(
        bucket_payload=bucket_payload,
        rail_payload=rail_payload,
        cadence_payload=cadence_payload,
    )

    rail_proof_required = _rail_proof_required(rail_payload)

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "owner_decision_required": True,
        "withdrawal_plan_status": withdrawal_plan_status,
        "eligible_for_owner_review": eligible_for_owner_review,
        "recommended_cadence": recommended_cadence,
        "withdrawal_bucket": bucket_summary.get("withdrawal_bucket", {}),
        "protected_buckets": reserve_summary.get("protected_buckets", []),
        "reserve_summary": reserve_summary,
        "rail_summary": rail_summary,
        "selected_review_rail": selected_review_rail,
        "fee_summary": {
            "lowest_fee_rail": rail_summary.get("lowest_cost_rail"),
            "fastest_rail": rail_summary.get("fastest_rail"),
            "fee_estimates": rail_payload.get("fee_estimates", {}),
        },
        "timing_summary": {
            "next_review_day": cadence_summary.get("recommended_review_day"),
            "next_review_date": cadence_summary.get("next_review_date"),
            "bimonthly_timing": "every_2_to_4_weeks_after_approval",
            "monthly_timing": "every_4_to_8_weeks_after_approval",
            "weekly_timing": "every_week_after_owner_review",
        },
        "withdrawal_hierarchy_review": _withdrawal_hierarchy(bucket_payload, oanda_payload),
        "margin_call_review_required": bucket_payload.get("margin_call_review_required", False),
        "bucket_purge_required": bool(bucket_payload.get("stale_bucket_flags")),
        "rail_proof_required": rail_proof_required,
        "owner_gate": _owner_gate(),
        "manual_execution_only": True,
        "blocked_reasons": _unique(blocked_reasons),
        "missing_information": _unique(missing_information),
        "safe_next_action": _safe_next_action(
            withdrawal_plan_status=withdrawal_plan_status,
            blocked_reasons=blocked_reasons,
            recommended_cadence=recommended_cadence,
            eligible_for_owner_review=eligible_for_owner_review,
        ),
        "audit_record": {
            "status": withdrawal_plan_status,
            "as_of": _as_text(source.get("as_of_date")),
            "input_fields_seen": list(source.keys()),
            "readonly": True,
            "audit_reference": "owner_review_packet_v1_placeholder",
        },
        "safety": _safety(),
    }


def _coerce(value: Any, fallback: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(fallback, Mapping):
        return dict(fallback)
    return {}


def _plan_status(
    *,
    bucket_payload: Mapping[str, Any],
    rail_payload: Mapping[str, Any],
    cadence_payload: Mapping[str, Any],
    oanda_payload: Mapping[str, Any],
    reserve_summary: Mapping[str, Any],
) -> str:
    if _contains_sensitive_key(bucket_payload) or _contains_sensitive_key(rail_payload):
        return "BLOCKED_BY_SENSITIVE_DATA"

    if (
        bucket_payload.get("margin_or_open_risk_block", False)
        or bucket_payload.get("daily_loss_stop_active", False)
    ):
        return "BLOCKED_BY_RISK"

    if _rail_blocked(rail_payload):
        return "BLOCKED_BY_RAIL"

    if not reserve_summary.get("operating_reserve_met", True):
        return "BLOCKED_BY_RESERVE"
    if not reserve_summary.get("tax_reserve_met", True):
        return "BLOCKED_BY_RESERVE"

    if not reserve_summary.get("bucket_eligibility", True):
        return "BLOCKED_BY_RESERVE"

    if not _cadence_ready(cadence_payload):
        return "BLOCKED_BY_RISK"

    if oanda_payload and isinstance(oanda_payload, Mapping):
        status = str(oanda_payload.get("withdrawal_readiness", {}).get("status", "")).upper()
        if status == "BLOCKED":
            return "BLOCKED_BY_RISK"

    bucket_ready = not bucket_payload.get("blocked_reasons") or _is_eligible_bucket(
        bucket_payload
    )
    if not bucket_ready:
        return "BLOCKED_BY_RISK"
    if bucket_payload.get("withdrawal_bucket_status", {}).get("status") == "BLOCKED":
        return "BLOCKED_BY_RISK"

    if cadence_payload.get("recommended_cadence") == "no_withdrawal":
        return "BLOCKED_BY_RISK"
    return "READY_FOR_OWNER_REVIEW"


def _extract_reserves(
    bucket_payload: Mapping[str, Any],
    rail_payload: Mapping[str, Any],
) -> dict[str, Any]:
    bucket_state = bucket_payload.get("reserve_requirements", {})
    if not isinstance(bucket_state, Mapping) or not bucket_state:
        return {
            "operating_reserve_current": None,
            "tax_reserve_current": None,
            "operating_reserve_percent": None,
            "tax_reserve_percent": None,
            "operating_reserve_met": False,
            "tax_reserve_met": False,
            "protected_buckets": ["operating_reserve_bucket", "tax_reserve_bucket"],
            "bucket_eligibility": False,
            "protected_buckets_ok": False,
        }

    operating_current = bucket_state.get("operating_reserve_current")
    tax_current = bucket_state.get("tax_reserve_current")
    operating_met = bool(bucket_state.get("operating_reserve_met"))
    tax_met = bool(bucket_state.get("tax_reserve_met"))
    return {
        "operating_reserve_current": operating_current,
        "tax_reserve_current": tax_current,
        "operating_reserve_percent": bucket_state.get("operating_reserve_percent"),
        "tax_reserve_percent": bucket_state.get("tax_reserve_percent"),
        "operating_reserve_minimum": bucket_state.get("operating_reserve_minimum"),
        "tax_reserve_minimum": bucket_state.get("tax_reserve_minimum"),
        "operating_reserve_met": operating_met,
        "tax_reserve_met": tax_met,
        "bucket_eligibility": operating_met and tax_met,
        "protected_buckets": ["operating_reserve_bucket", "tax_reserve_bucket"],
        "protected_buckets_ok": operating_met and tax_met,
    }


def _extract_bucket(bucket_payload: Mapping[str, Any]) -> dict[str, Any]:
    bucket_state = bucket_payload.get("bucket_state", {})
    if not isinstance(bucket_state, Mapping):
        return {"withdrawal_bucket": {}}
    return {
        "withdrawal_bucket": {
            "status": bucket_payload.get("withdrawal_bucket_status", {}).get("status"),
            "eligible_amount": bucket_payload.get("withdrawal_bucket_status", {}).get(
                "eligible_amount",
            ),
            "pending_withdrawal_bucket": bucket_state.get("pending_withdrawal_bucket"),
            "withdrawal_bucket_current": bucket_state.get("withdrawal_bucket"),
            "read_only": True,
        },
        "bucket_state": bucket_state,
    }


def _extract_rail_summary(rail_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "eligible_rail_ids": list(rail_payload.get("eligible_rails", [])),
        "blocked_rail_count": len(rail_payload.get("blocked_rails", []))
        if isinstance(rail_payload.get("blocked_rails"), Sequence)
        else 0,
        "rail_count": len(rail_payload.get("rail_registry", []))
        if isinstance(rail_payload.get("rail_registry"), list)
        else 0,
        "lowest_cost_rail": rail_payload.get("lowest_cost_rail"),
        "fastest_rail": rail_payload.get("fastest_rail"),
        "preferred_withdrawal_rail": rail_payload.get("preferred_withdrawal_rail"),
        "same_name_proof_required": bool(
            rail_payload.get("same_name_proof_required", True)
        ),
        "same_name_proof_status": rail_payload.get("same_name_proof_status", {}),
        "sensitivity_blocked": bool(rail_payload.get("sensitive_data_blocked", False)),
        "third_party_payment_blocked": bool(
            rail_payload.get("third_party_payment_blocked", False)
        ),
    }


def _extract_cadence_summary(cadence_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "recommended_cadence": cadence_payload.get("recommended_cadence", "no_withdrawal"),
        "risk_blocks": list(cadence_payload.get("risk_blocks", [])),
        "recommended_review_day": (
            cadence_payload.get("weekly_plan", {}).get("recommended_review_day")
            or cadence_payload.get("monthly_plan", {}).get("recommended_review_day")
            or cadence_payload.get("bimonthly_plan", {}).get("recommended_review_day")
        ),
        "next_review_date": (
            cadence_payload.get("weekly_plan", {}).get("next_review_date")
            or cadence_payload.get("monthly_plan", {}).get("next_review_date")
            or cadence_payload.get("bimonthly_plan", {}).get("next_review_date")
        ),
        "blocked_reasons": list(cadence_payload.get("blocked_reasons", [])),
        "no_withdrawal_plan": cadence_payload.get("no_withdrawal_plan"),
    }


def _withdrawal_hierarchy(bucket_payload: Mapping[str, Any], oanda_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "priority": [
            "oanda_card_or_wire_when_same_name_supported",
            "verified_personal_bank_wire_for_higher_amounts",
            "all_manual_checks_required_before_external_action",
        ],
        "oanda_readiness_present": bool(oanda_payload),
        "oanda_blocked": bool(
            oanda_payload
            and oanda_payload.get("same_name_bank_required")
        ) and bool(oanda_payload.get("blocked_reasons", [])),
        "bucket_state_hint": bucket_payload.get("withdrawal_bucket_status", {}),
    }


def _best_rail_from_registry(
    eligible_rail_ids: Sequence[str],
    source_preference: str = "lowest_cost",
) -> dict[str, Any] | None:
    if not eligible_rail_ids:
        return None
    if source_preference == "lowest_cost":
        return {"rail_id": eligible_rail_ids[0]}
    return {"rail_id": eligible_rail_ids[0]}


def _rail_is_eligible(rail: Any, rail_payload: Mapping[str, Any]) -> bool:
    if not isinstance(rail, Mapping):
        return False
    rail_id = str(rail.get("rail_id", "")).strip()
    eligible = set(rail_payload.get("eligible_rails", []))
    return rail_id in eligible


def _rail_blocked(rail_payload: Mapping[str, Any]) -> bool:
    blocked = bool(rail_payload.get("sensitive_data_blocked", False))
    blocked = blocked or bool(rail_payload.get("third_party_payment_blocked", False))
    if rail_payload.get("same_name_proof_required", False):
        proof_status = rail_payload.get("same_name_proof_status", {})
        if proof_status.get("satisfied") is False:
            blocked = True
    if rail_payload.get("eligible_rails") in (None, [], 0):
        blocked = True
    if isinstance(rail_payload.get("eligible_rails"), Sequence):
        blocked = blocked or not bool(rail_payload.get("eligible_rails"))
    if _contains_sensitive_key(rail_payload):
        blocked = True
    return blocked

def _is_eligible_bucket(bucket_payload: Mapping[str, Any]) -> bool:
    status = str(bucket_payload.get("withdrawal_bucket_status", {}).get("status", ""))
    return status in {"REVIEW_ONLY", "READY", "READY_FOR_REVIEW"}


def _cadence_ready(cadence_payload: Mapping[str, Any]) -> bool:
    if cadence_payload.get("recommended_cadence") == "no_withdrawal":
        return False
    if cadence_payload.get("withdrawal_eligibility", {}).get("eligible_for_owner_review"):
        return True
    return False


def _rail_proof_required(rail_payload: Mapping[str, Any]) -> bool:
    if not rail_payload.get("same_name_proof_required", False):
        return False
    proof_status = rail_payload.get("same_name_proof_status", {})
    if not proof_status:
        return True
    return proof_status.get("satisfied") is False


def _safe_next_action(
    *,
    withdrawal_plan_status: str,
    blocked_reasons: list[str],
    recommended_cadence: str,
    eligible_for_owner_review: bool,
) -> str:
    if withdrawal_plan_status == "READY_FOR_OWNER_REVIEW" and eligible_for_owner_review:
        return (
            "Owner may review withdrawal plan manually. AIOS does not move money; "
            "execute only outside AIOS after confirming amount, rail, timing, and reserves."
        )
    if blocked_reasons:
        return (
            "Required blockers: "
            + ", ".join(blocked_reasons)
            + ". Resolve blockers and rerun the owner-gated plan."
        )
    return (
        f"No-ready plan for {recommended_cadence}. Continue review and rerun "
        "before any manual execution."
    )


def _gather_blockers(
    *,
    bucket_payload: Mapping[str, Any],
    rail_payload: Mapping[str, Any],
    cadence_payload: Mapping[str, Any],
    oanda_payload: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    blockers.extend(_as_list(bucket_payload.get("blocked_reasons")))
    blockers.extend(_as_list(rail_payload.get("blocked_reasons")))
    blockers.extend(_as_list(cadence_payload.get("blocked_reasons")))
    blockers.extend(_as_list(oanda_payload.get("blocked_reasons")))
    if rail_payload.get("sensitive_data_blocked"):
        blockers.append("sensitive_financial_data_provided")
    if bucket_payload.get("margin_or_open_risk_block"):
        blockers.append("margin_or_open_risk_block")
    if bucket_payload.get("daily_loss_stop_active"):
        blockers.append("daily_loss_stop_active")
    if not _bucket_reserves_ok(bucket_payload.get("reserve_requirements", {})):
        blockers.append("bucket_reserves_underfunded")
    if _contains_sensitive_key(bucket_payload) or _contains_sensitive_key(rail_payload):
        blockers.append("sensitive_financial_data_provided")
    return blockers


def _bucket_reserves_ok(reserve_requirements: Any) -> bool:
    if not isinstance(reserve_requirements, Mapping):
        return False
    return bool(reserve_requirements.get("operating_reserve_met")) and bool(
        reserve_requirements.get("tax_reserve_met")
    )


def _missing_information(
    *,
    bucket_payload: Mapping[str, Any],
    rail_payload: Mapping[str, Any],
    cadence_payload: Mapping[str, Any],
) -> list[str]:
    missing: list[str] = []
    if not bucket_payload.get("bucket_state"):
        missing.append("bucket_purge_controller_payload")
    if not rail_payload.get("rail_registry"):
        missing.append("rail_registry")
    if not cadence_payload.get("recommended_cadence"):
        missing.append("cadence_plan_payload")
    return missing


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            key = str(raw_key).strip().lower()
            if any(
                token in key
                for token in (
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
                )
            ):
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _owner_gate() -> dict[str, Any]:
    return {
        "owner_name": "Anthony",
        "approval_required": True,
        "approval_scope": "manual external withdrawal review only",
        "approval_expires_at": None,
        "execution_allowed": False,
    }


def _safety() -> dict[str, bool]:
    return {
        "no_transfer_tool": True,
        "no_deposit_tool": True,
        "no_withdrawal_tool": True,
        "no_bank_automation": True,
        "no_broker_api_execution": True,
        "manual_execution_only": True,
        "owner_only_money_decision": True,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }


def _as_float(value: Any) -> float:
    if isinstance(value, Decimal):
        return float(value)
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _as_text(value: Any) -> str:
    return str(value) if value is not None else ""


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


__all__ = [
    "MODE",
    "SCHEMA",
    "evaluate_capital_rail_withdrawal_plan_v1",
]
