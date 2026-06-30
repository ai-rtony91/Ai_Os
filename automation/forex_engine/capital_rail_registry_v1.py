"""Read-only redacted capital rail registry for AIOS withdrawal planning."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SCHEMA = "AIOS_CAPITAL_RAIL_REGISTRY_V1"
MODE = "READ_ONLY_REDACTED_RAIL_REVIEW"

ALLOWED_RAIL_TYPES = {
    "oanda_debit_card",
    "oanda_ach",
    "oanda_domestic_wire",
    "oanda_international_wire",
    "personal_bank_ach",
    "personal_bank_wire",
    "unknown",
}

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


def evaluate_capital_rail_registry_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Build a redacted withdrawal/deposit rail inventory without credentials."""

    source = payload if isinstance(payload, Mapping) else {}
    rails_input = _as_sequence(source.get("rails"))
    third_party_payment = bool(source.get("third_party_payment", False))

    sensitive_data_blocked = False
    blocked_reasons: list[str] = []
    missing_information: list[str] = []
    rail_registry: list[dict[str, Any]] = []
    rails_by_type: dict[str, list[dict[str, Any]]] = {}
    eligible_rails: list[dict[str, Any]] = []
    blocked_rails: list[dict[str, Any]] = []

    for index, raw_rail in enumerate(rails_input):
        if not isinstance(raw_rail, Mapping):
            blocked_rails.append(
                {
                    "rail_id": f"rail_{index}",
                    "reason": "rail_payload_invalid",
                    "reasons": ["rail_payload_invalid"],
                }
            )
            continue
        rail = dict(raw_rail)
        rail_id = str(rail.get("rail_id", f"rail_{index}")).strip() or f"rail_{index}"
        rail_type = _normalized_key(rail.get("rail_type"))
        notes = []

        if third_party_payment is True:
            blocked_reasons.append("third_party_payment_blocked")
            blocked_rails.append(
                {
                    "rail_id": rail_id,
                    "rail_type": rail_type,
                    "reasons": ["third_party_payment_blocked"],
                }
            )
            continue

        if rail_type not in ALLOWED_RAIL_TYPES:
            blocked_reasons.append(f"unsupported_rail_type_{rail_type}")
            blocked_rails.append(
                {
                    "rail_id": rail_id,
                    "rail_type": rail_type,
                    "reasons": [f"unsupported_rail_type_{rail_type}"],
                }
            )
            continue

        if _contains_sensitive_key(rail):
            sensitive_data_blocked = True
            blocked_reasons.append("sensitive_financial_data_provided")
            blocked_rails.append(
                {
                    "rail_id": rail_id,
                    "rail_type": rail_type,
                    "reasons": ["sensitive_financial_data_provided"],
                }
            )
            continue

        active = _truthy(rail.get("active", True))
        withdrawal_supported = _truthy(rail.get("withdrawal_supported", False))
        deposit_supported = _truthy(rail.get("deposit_supported", False))
        same_name_verified = _truthy(rail.get("same_name_verified"))
        owner_verified = _truthy(rail.get("owner_verified", same_name_verified))
        owner_preferred = _truthy(rail.get("owner_preferred"))
        fee = _float_or_none(rail.get("fee_estimate_usd"), default=0.0)
        processing = _text(rail.get("processing_time_estimate"), "")
        min_limit = _float_or_none(rail.get("min_transfer_amount"), default=0.0)
        max_limit = _float_or_none(rail.get("max_transfer_amount"), default=0.0)
        institution_name = _text(rail.get("institution_name_redacted"), "")
        last4 = _text(rail.get("last4_only"), "")
        currency = _text(rail.get("currency"), "USD")

        if not institution_name:
            notes.append("institution_name_redacted_missing")

        sanitized = {
            "rail_id": rail_id,
            "rail_type": rail_type,
            "nickname": _text(rail.get("nickname")),
            "institution_name_redacted": institution_name,
            "last4_only": last4[:4] if last4 else "",
            "country": _text(rail.get("country"), "US"),
            "currency": currency,
            "same_name_verified": same_name_verified,
            "owner_verified": owner_verified,
            "fee_estimate_usd": fee,
            "processing_time_estimate": processing or "unknown",
            "min_transfer_amount": min_limit,
            "max_transfer_amount": max_limit,
            "withdrawal_supported": withdrawal_supported,
            "deposit_supported": deposit_supported,
            "preferred_for_withdrawal": _truthy(rail.get("preferred_for_withdrawal")),
            "preferred_for_deposit": _truthy(rail.get("preferred_for_deposit")),
            "active": active,
            "owner_preferred": owner_preferred,
            "notes_redacted": notes,
        }

        rail_registry.append(sanitized)
        rails_by_type.setdefault(rail_type, []).append(sanitized)

        if active and withdrawal_supported:
            if not same_name_verified:
                blocked_reasons.append("same_name_verification_missing")
            if same_name_verified:
                eligible_rails.append(sanitized)
        if active is False and withdrawal_supported:
            blocked_rails.append(
                {
                    "rail_id": rail_id,
                    "rail_type": rail_type,
                    "reasons": ["rail_inactive"],
                }
            )

    if not rail_registry:
        missing_information.append("rail_candidates")
        blocked_reasons.append("missing_rail_registry")

    same_name_proof_required = any(
        rail.get("withdrawal_supported") for rail in rail_registry
    ) or any(rail["withdrawal_supported"] for rail in eligible_rails)
    same_name_proof_status = {
        "required": bool(sensitive_data_blocked is False and rail_registry),
        "satisfied": all(
            rail["same_name_verified"] for rail in eligible_rails
        )
        if eligible_rails
        else False,
        "missing_rail_proofs": [
            rail["rail_id"]
            for rail in rail_registry
            if rail["withdrawal_supported"] and not rail["same_name_verified"]
        ],
    }

    fee_estimates: dict[str, float] = {
        rail["rail_id"]: rail["fee_estimate_usd"] for rail in eligible_rails
    }
    timing_estimates: dict[str, str] = {
        rail["rail_id"]: rail["processing_time_estimate"] for rail in eligible_rails
    }
    rail_limits = {
        rail["rail_id"]: {
            "min_transfer_amount": rail["min_transfer_amount"],
            "max_transfer_amount": rail["max_transfer_amount"],
        }
        for rail in eligible_rails
    }

    lowest_cost_rail = _select_lowest_cost(eligible_rails, tie_break_fastest=True)
    fastest_rail = _select_fastest(eligible_rails)
    preferred_withdrawal_rail = _select_preferred_withdrawal(
        eligible_rails,
        lowest_cost_rail,
        fastest_rail,
    )

    blocked_rails_reasons = _unique(
        [reason for rail in blocked_rails for reason in rail.get("reasons", [])]
    )
    if third_party_payment:
        blocked_rails_reasons.append("third_party_payment_blocked")
        if "third_party_payment_blocked" not in blocked_reasons:
            blocked_reasons.append("third_party_payment_blocked")

    if same_name_proof_required and not same_name_proof_status["satisfied"]:
        blocked_reasons.append("same_name_proof_required")
    blocked_reasons = _unique(blocked_reasons)
    missing_information = _unique(missing_information)

    if blocked_rails and not blocked_reasons:
        blocked_reasons.append("rail_restrictions")

    if third_party_payment:
        blocked_rails.extend(
            [
                {
                    "rail_id": rail["rail_id"],
                    "rail_type": rail.get("rail_type"),
                    "reasons": ["third_party_payment_blocked"],
                }
                for rail in rail_registry
            ]
        )
    owner_decision_required = True

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "rail_registry": rail_registry,
        "rails_by_type": rails_by_type,
        "eligible_rails": [rail["rail_id"] for rail in eligible_rails],
        "blocked_rails": blocked_rails,
        "lowest_cost_rail": lowest_cost_rail,
        "fastest_rail": fastest_rail,
        "preferred_withdrawal_rail": preferred_withdrawal_rail,
        "fee_estimates": fee_estimates,
        "timing_estimates": timing_estimates,
        "rail_limits": rail_limits,
        "same_name_proof_required": same_name_proof_required,
        "same_name_proof_status": same_name_proof_status,
        "third_party_payment_blocked": third_party_payment,
        "sensitive_data_blocked": sensitive_data_blocked,
        "missing_information": missing_information,
        "blocked_reasons": blocked_reasons + blocked_rails_reasons,
        "owner_decision_required": owner_decision_required,
        "safe_next_action": _safe_next_action(
            third_party_payment=third_party_payment,
            sensitive_data_blocked=sensitive_data_blocked,
            eligible_count=len(eligible_rails),
            blocked_count=len(blocked_rails),
        ),
        "safety": _safety(),
    }


def _select_preferred_withdrawal(
    eligible_rails: Sequence[Mapping[str, Any]],
    lowest_cost_rail: Mapping[str, Any] | None,
    fastest_rail: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    if not eligible_rails:
        return None
    # Lowest cost and same-name verified rails are the primary candidates.
    candidates = [
        rail
        for rail in eligible_rails
        if rail.get("withdrawal_supported")
        and rail.get("same_name_verified")
        and rail.get("active")
    ]
    if not candidates:
        return None

    def _rank(rail: Mapping[str, Any]) -> tuple[float, float, int]:
        fee = float(rail.get("fee_estimate_usd", 10_000.0))
        processing_seconds = _processing_seconds_rank(rail.get("processing_time_estimate"))
        preferred = 0 if _truthy(rail.get("owner_preferred")) else 1
        return (fee, processing_seconds, preferred)

    return sorted(candidates, key=_rank)[0]

def _select_lowest_cost(
    eligible_rails: Sequence[Mapping[str, Any]],
    *,
    tie_break_fastest: bool = False,
) -> Mapping[str, Any] | None:
    if not eligible_rails:
        return None
    if tie_break_fastest:
        return sorted(
            eligible_rails,
            key=lambda rail: (
                float(rail.get("fee_estimate_usd", 10_000.0)),
                _processing_seconds_rank(rail.get("processing_time_estimate")),
                str(rail.get("rail_id")),
            ),
        )[0]
    return min(
        eligible_rails,
        key=lambda rail: (float(rail.get("fee_estimate_usd", 10_000.0))),
    )


def _select_fastest(
    eligible_rails: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    if not eligible_rails:
        return None
    return min(
        eligible_rails,
        key=lambda rail: (
            _processing_seconds_rank(rail.get("processing_time_estimate")),
            float(rail.get("fee_estimate_usd", 10_000.0)),
            str(rail.get("rail_id")),
        ),
    )


def _processing_seconds_rank(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return 99_999.0
    text = str(value).lower().strip()
    if "instant" in text:
        return 0.25
    if "same" in text and "day" in text:
        return 1.0
    if "business day" in text:
        return 2.0
    if "3" in text and "day" in text:
        return 3.0
    if "5" in text and "day" in text:
        return 5.0
    return 2.0


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for raw_key, item in value.items():
            key = str(raw_key).strip().lower()
            if key in SENSITIVE_KEYS or any(token in key for token in SENSITIVE_KEYS):
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _safe_next_action(
    *,
    third_party_payment: bool,
    sensitive_data_blocked: bool,
    eligible_count: int,
    blocked_count: int,
) -> str:
    if third_party_payment:
        return (
            "Third-party rails are blocked. Use owner-verified same-name rails only "
            "and rerun with owner-approved redacted rail registry."
        )
    if sensitive_data_blocked:
        return (
            "Remove sensitive rail fields (account/routing/card/credential/token) and rerun. "
            "AIOS does not initiate bank or broker connections."
        )
    if eligible_count > 0:
        return (
            "Review eligible redacted rails for owner approval. "
            "Selected rail is review-only and no transfer occurs."
        )
    if blocked_count > 0:
        return (
            "No active eligible rails cleared. Repair proof, status, and activity checks, "
            "then rerun."
        )
    return "Add redacted rail candidates and rerun."


def _safety() -> dict[str, bool]:
    return {
        "no_transfer_tool": True,
        "no_deposit_tool": True,
        "no_withdrawal_tool": True,
        "no_bank_connection": True,
        "no_broker_connection": True,
        "no_credentials_required": True,
        "owner_only_money_decision": True,
        "manual_execution_only": True,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }


def _as_sequence(value: Any) -> list[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return list(value)


def _normalized_key(value: Any) -> str:
    if value is None:
        return "unknown"
    return (
        str(value)
        .strip()
        .replace("-", "_")
        .replace(" ", "_")
        .lower()
    )


def _text(value: Any, default: str = "") -> str:
    if value in (None, "", {}, []):
        return default
    return str(value).strip()


def _float_or_none(value: Any, *, default: float | None = None) -> float | None:
    if value is None or isinstance(value, bool):
        return default
    try:
        candidate = float(str(value).strip().replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default
    if candidate != candidate or candidate in {float("inf"), float("-inf")}:
        return default
    return candidate


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


__all__ = [
    "ALLOWED_RAIL_TYPES",
    "MODE",
    "SCHEMA",
    "evaluate_capital_rail_registry_v1",
]
