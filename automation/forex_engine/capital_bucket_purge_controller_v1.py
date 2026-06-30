"""Read-only capital bucket purge / rollover / sweep controller."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


SCHEMA = "AIOS_CAPITAL_BUCKET_PURGE_CONTROLLER_V1"
MODE = "READ_ONLY_BUCKET_PURGE_REVIEW"

SENSITIVE_KEYS = (
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


def evaluate_capital_bucket_purge_controller_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate stale-bucket control and withdrawal-readiness rules in read-only mode."""

    source = payload if isinstance(payload, Mapping) else {}

    if _contains_sensitive_key(source):
        return _sensitive_block_payload()

    as_of_date = _as_datetime(source.get("as_of_date"))
    now = datetime.now(timezone.utc)

    balance_bucket = _to_decimal(source.get("balance_bucket"), 0)
    profit_bucket = _to_decimal(source.get("profit_bucket"), 0)
    loss_bucket = _to_decimal(source.get("loss_bucket"), 0)
    tax_reserve_bucket = _to_decimal(source.get("tax_reserve_bucket"), 0)
    operating_reserve_bucket = _to_decimal(source.get("operating_reserve_bucket"), 0)
    withdrawal_bucket = _to_decimal(source.get("withdrawal_bucket"), 0)
    compounding_bucket = _to_decimal(source.get("compounding_bucket"), 0)
    pending_withdrawal_bucket = _to_decimal(source.get("pending_withdrawal_bucket"), 0)
    realized_profit_period = _to_decimal(source.get("realized_profit_period"), 0)
    realized_loss_period = _to_decimal(source.get("realized_loss_period"), 0)
    unrealized_pnl = _to_decimal(source.get("unrealized_pnl"), 0)
    margin_used = _to_decimal(source.get("margin_used"), 0)
    open_risk = _to_decimal(source.get("open_risk"), 0)
    daily_loss_used = _to_decimal(source.get("daily_loss_used"), 0)
    max_daily_loss = _to_decimal(source.get("max_daily_loss"), 0)
    max_drawdown_percent = _to_decimal(source.get("max_drawdown_percent"), None)

    purge_frequency_days = _to_int(source.get("purge_frequency_days"), 7)
    rollover_frequency_days = _to_int(source.get("rollover_frequency_days"), 30)
    min_operating_reserve_percent = _to_decimal(source.get("min_operating_reserve_percent"), 10)
    min_tax_reserve_percent = _to_decimal(source.get("min_tax_reserve_percent"), 10)
    min_withdrawal_threshold = _to_decimal(source.get("min_withdrawal_threshold"), 0)
    max_withdrawal_percent_of_profit = _to_decimal(
        source.get("max_withdrawal_percent_of_profit"),
        Decimal("50"),
    )
    owner_approved_purge = _as_truthy(source.get("owner_approved_purge"))
    owner_approved_rollover = _as_truthy(source.get("owner_approved_rollover"))
    owner_approved_sweep = _as_truthy(source.get("owner_approved_sweep"))

    stale_flags = _build_stale_flags(
        source=source,
        as_of=as_of_date,
        now=now,
        purge_frequency_days=purge_frequency_days,
        rollover_frequency_days=rollover_frequency_days,
    )

    blocked_reasons: list[str] = []
    missing_information: list[str] = []
    if as_of_date is None:
        missing_information.append("as_of_date")
    if source.get("bucket_last_purged_at") is None:
        missing_information.append("bucket_last_purged_at")
    if source.get("bucket_last_rolled_at") is None:
        missing_information.append("bucket_last_rolled_at")

    if balance_bucket < 0:
        blocked_reasons.append("balance_bucket_negative")

    if not owner_approved_purge:
        blocked_reasons.append("owner_approval_required_for_purge")
    if not owner_approved_rollover:
        blocked_reasons.append("owner_approval_required_for_rollover")
    if not owner_approved_sweep:
        blocked_reasons.append("owner_approval_required_for_sweep")

    reserve_requirements = _evaluate_reserve_requirements(
        balance_bucket=balance_bucket,
        operating_reserve_bucket=operating_reserve_bucket,
        tax_reserve_bucket=tax_reserve_bucket,
        min_operating_reserve_percent=min_operating_reserve_percent,
        min_tax_reserve_percent=min_tax_reserve_percent,
    )

    margin_or_open_risk_block = margin_used > 0 or open_risk > 0
    daily_loss_stop_active = max_daily_loss > 0 and daily_loss_used >= max_daily_loss

    if margin_or_open_risk_block:
        blocked_reasons.append("margin_or_open_risk_block")
    if daily_loss_stop_active:
        blocked_reasons.append("daily_loss_stop_active")
    if realized_loss_period > 0:
        blocked_reasons.append("realized_loss_requires_reserve_rebuild")

    if min_withdrawal_threshold > 0:
        # Keep missing threshold explicit only when numeric was supplied but blank.
        if str(source.get("min_withdrawal_threshold", "")).strip() == "":
            missing_information.append("min_withdrawal_threshold")

    withdrawal_eligible_amount = max(
        Decimal("0"),
        profit_bucket + realized_profit_period + unrealized_pnl - realized_loss_period,
    )
    if realized_loss_period > 0:
        withdrawal_eligible_amount *= Decimal("0.75")
    if max_withdrawal_percent_of_profit > 0:
        withdrawal_eligible_amount = min(
            withdrawal_eligible_amount,
            (profit_bucket + realized_profit_period)
            * (max_withdrawal_percent_of_profit / Decimal("100")),
        )
    if withdrawal_eligible_amount > 0 and min_withdrawal_threshold > 0:
        withdrawal_eligible_amount = max(
            Decimal("0"), withdrawal_eligible_amount - max(Decimal("0"), min_withdrawal_threshold * Decimal("0")),
        )
    if min_withdrawal_threshold > 0 and withdrawal_eligible_amount < min_withdrawal_threshold:
        blocked_reasons.append("withdrawal_eligible_below_min_threshold")
    if margin_or_open_risk_block or daily_loss_stop_active:
        withdrawal_eligible_amount = Decimal("0")

    purge_actions = _build_purge_actions(stale_flags, owner_approved_purge)
    rollover_actions = _build_rollover_actions(
        stale_flags=stale_flags,
        realized_profit_period=realized_profit_period,
        realized_loss_period=realized_loss_period,
        tax_reserve_bucket=tax_reserve_bucket,
        operating_reserve_bucket=operating_reserve_bucket,
        withdrawal_bucket=withdrawal_bucket,
        compounding_bucket=compounding_bucket,
        owner_approved_rollover=owner_approved_rollover,
    )
    sweep_actions = _build_sweep_actions(
        profit_bucket=profit_bucket,
        realized_profit_period=realized_profit_period,
        realized_loss_period=realized_loss_period,
        operating_reserve_bucket=operating_reserve_bucket,
        tax_reserve_bucket=tax_reserve_bucket,
        reserve_requirements=reserve_requirements,
        min_withdrawal_threshold=min_withdrawal_threshold,
        max_withdrawal_percent_of_profit=max_withdrawal_percent_of_profit,
        owner_approved_sweep=owner_approved_sweep,
    )

    if source.get("pending_withdrawal_bucket"):
        blocked_reasons.append("pending_withdrawal_bucket_present")

    withdrawal_bucket_status = {
        "status": "BLOCKED" if withdrawal_eligible_amount <= 0 else "REVIEW_ONLY",
        "pending_review_release": True,
        "protected": True,
        "pending_withdrawal_bucket": _to_float(pending_withdrawal_bucket),
        "eligible_amount": _to_float(withdrawal_eligible_amount),
        "margin_or_open_risk_block": margin_or_open_risk_block,
        "daily_loss_stop_active": daily_loss_stop_active,
    }

    tax_reserve_status = {
        "status": "BLOCKED" if not reserve_requirements["tax_reserve_met"] else "REVIEW_ONLY",
        "required_minimum": _to_float(reserve_requirements["tax_reserve_minimum"]),
        "current": _to_float(tax_reserve_bucket),
        "protected": True,
        "protected_rule": "tax_reserve_protected",
    }
    operating_reserve_status = {
        "status": (
            "BLOCKED" if not reserve_requirements["operating_reserve_met"] else "REVIEW_ONLY"
        ),
        "required_minimum": _to_float(reserve_requirements["operating_reserve_minimum"]),
        "current": _to_float(operating_reserve_bucket),
        "protected": True,
        "protected_rule": "operating_reserve_protected",
    }
    compounding_status = {
        "status": "REVIEW_ONLY",
        "no_capital_reduction": True,
        "holdback_current": _to_float(compounding_bucket),
        "no_auto_release": True,
    }

    safe_next_action = _safe_next_action(
        margin_or_open_risk_block=margin_or_open_risk_block,
        daily_loss_stop_active=daily_loss_stop_active,
        blocked_reasons=blocked_reasons,
        stale_flags=stale_flags,
    )

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "broker_api_allowed": False,
        "bank_access_allowed": False,
        "bucket_state": {
            "balance_bucket": _to_float(balance_bucket),
            "profit_bucket": _to_float(profit_bucket),
            "loss_bucket": _to_float(loss_bucket),
            "tax_reserve_bucket": _to_float(tax_reserve_bucket),
            "operating_reserve_bucket": _to_float(operating_reserve_bucket),
            "withdrawal_bucket": _to_float(withdrawal_bucket),
            "compounding_bucket": _to_float(compounding_bucket),
            "pending_withdrawal_bucket": _to_float(pending_withdrawal_bucket),
            "pending_withdrawal_bucket_never_auto_sent": True,
            "withdrawal_review_only": True,
            "tax_reserve_protected": True,
            "operating_reserve_protected": True,
        },
        "purge_policy": {
            "purge_frequency_days": purge_frequency_days,
            "rollover_frequency_days": rollover_frequency_days,
            "owner_review_only": True,
        },
        "purge_actions": purge_actions,
        "rollover_actions": rollover_actions,
        "sweep_actions": sweep_actions,
        "stale_bucket_flags": stale_flags,
        "reserve_requirements": {
            "operating_reserve_percent": _to_float(min_operating_reserve_percent),
            "tax_reserve_percent": _to_float(min_tax_reserve_percent),
            "operating_reserve_current": _to_float(operating_reserve_bucket),
            "tax_reserve_current": _to_float(tax_reserve_bucket),
            "operating_reserve_minimum": _to_float(reserve_requirements["operating_reserve_minimum"]),
            "tax_reserve_minimum": _to_float(reserve_requirements["tax_reserve_minimum"]),
            "operating_reserve_met": reserve_requirements["operating_reserve_met"],
            "tax_reserve_met": reserve_requirements["tax_reserve_met"],
            "operating_reserve_shortfall": _to_float(reserve_requirements["operating_reserve_shortfall"]),
            "tax_reserve_shortfall": _to_float(reserve_requirements["tax_reserve_shortfall"]),
            "protected_buckets": ["tax_reserve_bucket", "operating_reserve_bucket"],
        },
        "withdrawal_bucket_status": withdrawal_bucket_status,
        "tax_reserve_status": tax_reserve_status,
        "operating_reserve_status": operating_reserve_status,
        "compounding_status": compounding_status,
        "owner_decision_required": True,
        "missing_information": _unique(missing_information),
        "blocked_reasons": _unique(blocked_reasons),
        "safe_next_action": safe_next_action,
        "audit_record": {
            "as_of": _to_iso(as_of_date),
            "schema": SCHEMA,
            "mode": MODE,
            "input_fields_seen": _sorted_key_list(source),
            "stale_bucket_flags_count": len(stale_flags),
            "blocked_reasons": _unique(blocked_reasons),
            "purge_history_retained": True,
            "audit_history_deleted": False,
            "money_movement_blocked": True,
        },
        "safety": _safety(),
    }


def _build_stale_flags(
    *,
    source: Mapping[str, Any],
    as_of: datetime | None,
    now: datetime,
    purge_frequency_days: int,
    rollover_frequency_days: int,
) -> list[str]:
    flags: list[str] = []

    if as_of is None:
        flags.append("missing_as_of_date")

    last_purged = _as_datetime(source.get("bucket_last_purged_at"))
    last_rolled = _as_datetime(source.get("bucket_last_rolled_at"))
    if last_purged is not None and purge_frequency_days > 0:
        if ((as_of or now) - last_purged).days >= purge_frequency_days:
            flags.append("balance_bucket_stale_for_purge")
    elif not source.get("bucket_last_purged_at"):
        flags.append("bucket_last_purged_at_missing")

    if last_rolled is not None and rollover_frequency_days > 0:
        if ((as_of or now) - last_rolled).days >= rollover_frequency_days:
            flags.append("balance_bucket_stale_for_rollover")
    elif not source.get("bucket_last_rolled_at"):
        flags.append("bucket_last_rolled_at_missing")

    if not flags:
        flags.append("buckets_are_current")
    return flags


def _build_purge_actions(
    stale_flags: Sequence[str],
    owner_approved_purge: bool,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    stale = [entry for entry in stale_flags if "stale" in entry]
    for flag in stale:
        actions.append(
            {
                "action": flag,
                "action_type": "read_only_purge",
                "scope": "metadata_and_review_state",
                "review_only": True,
                "proposed": True,
                "owner_review_state": (
                    "APPROVED" if owner_approved_purge else "PENDING_REVIEW_APPROVAL"
                ),
                "note": (
                    "Archive stale metadata and stale pending review states. "
                    "Do not delete audit history."
                ),
            }
        )
    return actions


def _build_rollover_actions(
    *,
    stale_flags: Sequence[str],
    realized_profit_period: Decimal,
    realized_loss_period: Decimal,
    tax_reserve_bucket: Decimal,
    operating_reserve_bucket: Decimal,
    withdrawal_bucket: Decimal,
    compounding_bucket: Decimal,
    owner_approved_rollover: bool,
) -> list[dict[str, Any]]:
    if not stale_flags:
        return []
    return [
        {
            "action": "close_review_period_and_carry_forward",
            "action_type": "read_only_rollover",
            "scope": "profit_loss_and_reserve_snapshot",
            "review_only": True,
            "proposed": True,
            "owner_review_state": (
                "APPROVED" if owner_approved_rollover else "PENDING_REVIEW_APPROVAL"
            ),
            "carry_forward": {
                "realized_profit": _to_float(realized_profit_period),
                "realized_loss": _to_float(realized_loss_period),
                "tax_reserve_bucket": _to_float(tax_reserve_bucket),
                "operating_reserve_bucket": _to_float(operating_reserve_bucket),
                "withdrawal_bucket": _to_float(withdrawal_bucket),
                "compounding_bucket": _to_float(compounding_bucket),
                "audit_reference": "rollover_audit_hash_placeholder",
            },
        }
    ]


def _build_sweep_actions(
    *,
    profit_bucket: Decimal,
    realized_profit_period: Decimal,
    realized_loss_period: Decimal,
    operating_reserve_bucket: Decimal,
    tax_reserve_bucket: Decimal,
    reserve_requirements: Mapping[str, Any],
    min_withdrawal_threshold: Decimal,
    max_withdrawal_percent_of_profit: Decimal,
    owner_approved_sweep: bool,
) -> list[dict[str, Any]]:
    total_profit = profit_bucket + realized_profit_period - realized_loss_period
    if total_profit <= 0:
        return []

    tax_gap = max(Decimal("0"), _to_decimal(reserve_requirements["tax_reserve_shortfall"]))
    operating_gap = max(Decimal("0"), _to_decimal(reserve_requirements["operating_reserve_shortfall"]))
    available = max(Decimal("0"), total_profit - tax_gap - operating_gap)
    candidate_withdrawal = max(Decimal("0"), total_profit * (max_withdrawal_percent_of_profit / Decimal("100")))
    if max_withdrawal_percent_of_profit <= 0:
        candidate_withdrawal = available

    if candidate_withdrawal < min_withdrawal_threshold and candidate_withdrawal > 0:
        candidate_withdrawal = min_withdrawal_threshold
    if min_withdrawal_threshold > 0 and candidate_withdrawal > available + min_withdrawal_threshold:
        candidate_withdrawal = available

    tax_delta = min(tax_gap, total_profit * Decimal("0.25"))
    remaining_after_tax = max(Decimal("0"), total_profit - tax_delta)
    operating_delta = min(
        operating_gap,
        max(Decimal("0"), remaining_after_tax - Decimal("0")),
    )
    remaining_after_operating = max(
        Decimal("0"),
        remaining_after_tax - operating_delta,
    )
    withdrawal_delta = min(remaining_after_operating, candidate_withdrawal)
    compounding_delta = max(
        Decimal("0"),
        total_profit
        - tax_delta
        - operating_delta
        - withdrawal_delta,
    )
    if withdrawal_delta == 0 and min_withdrawal_threshold > 0 and total_profit > 0:
        withdrawal_delta = min_withdrawal_threshold

    return [
        {
            "action": "proposed_bucket_allocation",
            "action_type": "read_only_sweep",
            "scope": "conceptual_buckets",
            "review_only": True,
            "proposed": True,
            "owner_review_state": (
                "APPROVED" if owner_approved_sweep else "PENDING_REVIEW_APPROVAL"
            ),
            "proposed_bucket_allocation": {
                "from_bucket": "profit_bucket",
                "tax_reserve_bucket_delta": _to_float(tax_delta),
                "operating_reserve_bucket_delta": _to_float(operating_delta),
                "withdrawal_bucket_delta": _to_float(withdrawal_delta),
                "compounding_bucket_delta": _to_float(compounding_delta),
            },
            "no_capital_reduction": True,
            "no_transfer": True,
            "note": (
                "Sweep action is a proposal only. No actual transfer or account "
                "mutation is performed."
            ),
        }
    ]


def _evaluate_reserve_requirements(
    *,
    balance_bucket: Decimal,
    operating_reserve_bucket: Decimal,
    tax_reserve_bucket: Decimal,
    min_operating_reserve_percent: Decimal,
    min_tax_reserve_percent: Decimal,
) -> dict[str, Decimal]:
    operating_min = max(Decimal("0"), balance_bucket * (min_operating_reserve_percent / Decimal("100")))
    tax_min = max(Decimal("0"), balance_bucket * (min_tax_reserve_percent / Decimal("100")))
    return {
        "operating_reserve_minimum": operating_min,
        "tax_reserve_minimum": tax_min,
        "operating_reserve_met": operating_reserve_bucket >= operating_min,
        "tax_reserve_met": tax_reserve_bucket >= tax_min,
        "operating_reserve_shortfall": max(Decimal("0"), operating_min - operating_reserve_bucket),
        "tax_reserve_shortfall": max(Decimal("0"), tax_min - tax_reserve_bucket),
    }


def _safe_next_action(
    *,
    margin_or_open_risk_block: bool,
    daily_loss_stop_active: bool,
    blocked_reasons: Sequence[str],
    stale_flags: Sequence[str],
) -> str:
    if margin_or_open_risk_block:
        return (
            "Owner must address margin/open-risk blockers. No withdrawal release; "
            "actions remain review-only."
        )
    if daily_loss_stop_active:
        return "Daily loss stop active. Rerun after risk reset."
    if "sensitive_financial_data_provided" in blocked_reasons:
        return (
            "Remove sensitive financial fields and rerun. AIOS does not move money."
        )
    if any("stale" in item for item in stale_flags):
        return "Purge/rollover/sweep recommendations are ready for owner review."
    return "No immediate action; preserve protected buckets and rerun on schedule."


def _sensitive_block_payload() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "broker_api_allowed": False,
        "bank_access_allowed": False,
        "bucket_state": {},
        "purge_policy": {},
        "purge_actions": [],
        "rollover_actions": [],
        "sweep_actions": [],
        "stale_bucket_flags": ["sensitive_financial_data_blocked"],
        "reserve_requirements": {},
        "withdrawal_bucket_status": {"status": "BLOCKED"},
        "tax_reserve_status": {"status": "REVIEW_ONLY", "protected": True},
        "operating_reserve_status": {"status": "REVIEW_ONLY", "protected": True},
        "compounding_status": {"status": "REVIEW_ONLY", "no_capital_reduction": True},
        "owner_decision_required": True,
        "missing_information": ["sensitive_financial_data_removed"],
        "blocked_reasons": ["sensitive_financial_data_provided"],
        "safe_next_action": (
            "Stop and remove sensitive financial fields from payload. "
            "No sensitive values are stored or echoed."
        ),
        "audit_record": {"status": "SENSITIVE_INPUT_BLOCKED", "audit_reference": SCHEMA},
        "safety": _safety(),
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


def _as_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            try:
                return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def _to_decimal(value: Any, default: Any = Decimal("0")) -> Decimal:
    if value is None or isinstance(value, bool):
        return _to_decimal(default) if not isinstance(default, Decimal) else default
    if isinstance(default, Decimal):
        fallback = default
    else:
        try:
            fallback = Decimal(str(default))
        except (TypeError, ValueError):
            fallback = Decimal("0")
    try:
        parsed = Decimal(str(value).strip().replace(",", ""))
    except (AttributeError, ValueError, TypeError, OverflowError):
        return fallback
    if not parsed.is_finite():
        return fallback
    return parsed


def _to_float(value: Decimal | int | float | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_iso(value: datetime | None) -> str | None:
    return value.isoformat() if isinstance(value, datetime) else None


def _as_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _unique(values: Sequence[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return out


def _sorted_key_list(source: Mapping[str, Any]) -> list[str]:
    return sorted(str(key) for key in source.keys())


def _safety() -> dict[str, bool]:
    return {
        "no_transfer_tool": True,
        "no_deposit_tool": True,
        "no_withdrawal_tool": True,
        "no_bank_automation": True,
        "no_broker_api_execution": True,
        "credentials_rejected": True,
        "credential_values_echoed": False,
        "manual_execution_only": True,
        "owner_only_money_decision": True,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }


__all__ = ["SCHEMA", "MODE", "evaluate_capital_bucket_purge_controller_v1"]
