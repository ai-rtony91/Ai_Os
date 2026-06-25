from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence


PACKET_ID = "AIOS-FOREX-BROKER-BALANCE-BUCKET-EQUITY-SEPARATION-V1"
SEPARATION_VERSION = "v1"

BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY = (
    "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY"
)
BLOCKED_INVALID_ACCOUNT_SNAPSHOT = "BLOCKED_INVALID_ACCOUNT_SNAPSHOT"
BLOCKED_INVALID_BUCKET_RISK_POLICY = "BLOCKED_INVALID_BUCKET_RISK_POLICY"
REJECTED_LIVE_TRADING = "REJECTED_LIVE_TRADING"
REJECTED_UNSAFE_AUTHORITY = "REJECTED_UNSAFE_AUTHORITY"

EXECUTION_AUTHORITY_FIELDS = (
    "network_allowed",
    "broker_call_allowed",
    "credential_access_allowed",
    "order_placement_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "live_endpoint_allowed",
    "live_trading_allowed",
    "raw_broker_payload_persistence_allowed",
)

SAFETY_PROOF_FIELDS = (
    "network_call_performed",
    "broker_network_call_performed",
    "broker_api_call_performed",
    "credential_read_performed",
    "account_id_read_performed",
    "dotenv_read",
    "env_read",
    "order_placement_performed",
    "order_close_performed",
    "order_mutation_performed",
    "trade_mutation_performed",
    "position_mutation_performed",
    "live_endpoint_used",
    "raw_broker_payload_persisted",
    "file_persistence_performed",
)


def evaluate_broker_balance_bucket_equity_separation_v1(
    account_snapshot: Mapping[str, Any] | None = None,
    bucket_risk_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    account = _mapping(account_snapshot)
    policy = _mapping(bucket_risk_policy)

    account_values = _account_values(account)
    policy_values = _policy_values(policy)
    account_blockers = _account_blockers(account, account_values)
    policy_blockers = _policy_blockers(policy, policy_values, account_values)
    unsafe_blockers = _authority_blockers(account, "account_snapshot")
    unsafe_blockers.extend(_authority_blockers(policy, "bucket_risk_policy"))

    live_trading_requested = policy.get("live_trading") is True
    blockers = _unique(unsafe_blockers + account_blockers + policy_blockers)
    status = _status(
        unsafe_blockers=unsafe_blockers,
        live_trading_requested=live_trading_requested,
        account_blockers=account_blockers,
        policy_blockers=policy_blockers,
    )

    broker_balance = account_values["balance"]
    broker_nav = account_values["nav"]
    unrealized_pl = account_values["unrealized_pl"]
    realized_pl = account_values["realized_pl"]
    account_equity = (
        broker_nav
        if broker_nav is not None
        else _decimal_or_default(broker_balance) + _decimal_or_default(unrealized_pl)
    )
    trade_bucket = policy_values["configured_trade_bucket_balance"]
    max_single_trade_risk_amount = _risk_amount(
        trade_bucket,
        policy_values["max_single_trade_risk_pct"],
    )
    max_next_trade_risk_amount = _risk_amount(
        trade_bucket,
        policy_values["max_next_trade_risk_pct"],
    )

    open_exposure_present = (
        account_values["open_trade_count"] > 0
        or account_values["open_position_count"] > 0
    )
    pending_order_present = account_values["pending_order_count"] > 0
    next_trade_blockers = _next_trade_blockers(
        status=status,
        open_exposure_present=open_exposure_present,
        pending_order_present=pending_order_present,
        policy=policy,
    )
    next_trade_allowed = not next_trade_blockers

    compound_blockers = _compound_blockers(
        open_exposure_present=open_exposure_present,
        unrealized_pl=unrealized_pl,
        compounding_enabled=policy.get("compounding_enabled") is True,
    )
    withdraw_blockers = _withdraw_blockers(
        open_exposure_present=open_exposure_present,
        unrealized_pl=unrealized_pl,
    )

    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "separation_version": SEPARATION_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": _warnings(status),
        "broker_reported_balance": _as_float_or_none(broker_balance),
        "broker_reported_nav": _as_float_or_none(broker_nav),
        "account_equity": _as_float_or_none(account_equity),
        "unrealized_pl": _as_float_or_none(unrealized_pl),
        "realized_pl_lifetime_or_account": _as_float_or_none(realized_pl),
        "aios_trade_bucket_balance": _as_float_or_none(trade_bucket),
        "max_single_trade_risk_amount": _as_float_or_none(
            max_single_trade_risk_amount
        ),
        "max_next_trade_risk_amount": _as_float_or_none(max_next_trade_risk_amount),
        "risk_available_balance": _as_float_or_none(trade_bucket),
        "open_exposure_present": open_exposure_present,
        "pending_order_present": pending_order_present,
        "next_trade_allowed": next_trade_allowed,
        "next_trade_blockers": next_trade_blockers,
        "live_allocation_allowed": False,
        "no_live_allocation": True,
        "compound_allowed": False,
        "compound_blockers": compound_blockers,
        "withdraw_allowed": False,
        "withdraw_blockers": withdraw_blockers,
        "realized_pl_applied_to_bucket_here": False,
        "bucket_update_deferred_to_result_bucket_step": True,
        "account_snapshot_summary": _account_summary(account_values),
        "bucket_risk_policy_summary": _policy_summary(policy, policy_values),
        "decision_summary": _decision_summary(
            broker_balance=broker_balance,
            broker_nav=broker_nav,
            account_equity=account_equity,
            unrealized_pl=unrealized_pl,
            trade_bucket=trade_bucket,
            open_exposure_present=open_exposure_present,
            next_trade_allowed=next_trade_allowed,
        ),
        "execution_authority": _execution_authority(),
        "safety_proof": _safety_proof(),
        "next_safe_action": _next_safe_action(status, next_trade_blockers),
    }
    result.update(_safety_proof())
    return result


def _status(
    *,
    unsafe_blockers: Sequence[str],
    live_trading_requested: bool,
    account_blockers: Sequence[str],
    policy_blockers: Sequence[str],
) -> str:
    if unsafe_blockers:
        return REJECTED_UNSAFE_AUTHORITY
    if live_trading_requested:
        return REJECTED_LIVE_TRADING
    if account_blockers:
        return BLOCKED_INVALID_ACCOUNT_SNAPSHOT
    if policy_blockers:
        return BLOCKED_INVALID_BUCKET_RISK_POLICY
    return BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY


def _account_values(account: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "balance": _decimal_or_none(_first_present(account, "balance")),
        "nav": _decimal_or_none(_first_present(account, "NAV", "nav", "netAssetValue")),
        "unrealized_pl": _decimal_or_none(
            _first_present(account, "unrealizedPL", "unrealized_pl")
        ),
        "realized_pl": _decimal_or_none(
            _first_present(
                account,
                "pl",
                "realizedPL",
                "realized_pl",
                "realized_pl_lifetime_or_account",
            )
        ),
        "margin_used": _decimal_or_none(
            _first_present(account, "marginUsed", "margin_used")
        ),
        "margin_available": _decimal_or_none(
            _first_present(account, "marginAvailable", "margin_available")
        ),
        "open_trade_count": _count_or_zero(
            _first_present(account, "openTradeCount", "open_trade_count")
        ),
        "open_position_count": _count_or_zero(
            _first_present(account, "openPositionCount", "open_position_count")
        ),
        "pending_order_count": _count_or_zero(
            _first_present(account, "pendingOrderCount", "pending_order_count")
        ),
    }


def _policy_values(policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "configured_trade_bucket_balance": _decimal_or_none(
            policy.get("configured_trade_bucket_balance")
        ),
        "max_single_trade_risk_pct": _decimal_or_none(
            policy.get("max_single_trade_risk_pct")
        ),
        "max_next_trade_risk_pct": _decimal_or_none(
            policy.get("max_next_trade_risk_pct")
        ),
    }


def _account_blockers(
    account: Mapping[str, Any],
    values: Mapping[str, Any],
) -> list[str]:
    if not account:
        return ["missing_account_snapshot"]

    blockers: list[str] = []
    if values["balance"] is None or values["balance"] < 0:
        blockers.append("account_balance_must_be_numeric_non_negative")
    nav_input = _first_present(account, "NAV", "nav", "netAssetValue")
    if nav_input is not None and (values["nav"] is None or values["nav"] < 0):
        blockers.append("account_nav_must_be_numeric_non_negative")
    for source_key, value_key in (
        ("unrealizedPL", "unrealized_pl"),
        ("pl", "realized_pl"),
    ):
        if _first_present(account, source_key, value_key) is not None and values[
            value_key
        ] is None:
            blockers.append(f"account_{value_key}_must_be_numeric")
    for source_key, value_key in (
        ("marginUsed", "margin_used"),
        ("marginAvailable", "margin_available"),
    ):
        if _first_present(account, source_key, value_key) is not None:
            value = values[value_key]
            if value is None or value < 0:
                blockers.append(f"account_{value_key}_must_be_numeric_non_negative")
    for source_key, value_key in (
        ("openTradeCount", "open_trade_count"),
        ("openPositionCount", "open_position_count"),
        ("pendingOrderCount", "pending_order_count"),
    ):
        if _first_present(account, source_key, value_key) is not None and values[
            value_key
        ] < 0:
            blockers.append(f"account_{value_key}_must_be_non_negative_integer")
    return blockers


def _policy_blockers(
    policy: Mapping[str, Any],
    values: Mapping[str, Any],
    account_values: Mapping[str, Any],
) -> list[str]:
    if not policy:
        return ["missing_bucket_risk_policy"]

    blockers: list[str] = []
    if not _text(policy.get("bucket_currency")):
        blockers.append("bucket_policy_currency_required")

    trade_bucket = values["configured_trade_bucket_balance"]
    if trade_bucket is None or trade_bucket < 0:
        blockers.append(
            "configured_trade_bucket_balance_must_be_numeric_non_negative"
        )
    elif (
        account_values["balance"] is not None
        and trade_bucket == account_values["balance"]
        and policy.get("allow_bucket_to_equal_broker_balance") is not True
    ):
        blockers.append(
            "bucket_balance_matches_broker_balance_without_explicit_policy"
        )

    single_risk = values["max_single_trade_risk_pct"]
    next_risk = values["max_next_trade_risk_pct"]
    if single_risk is None or single_risk <= 0:
        blockers.append("max_single_trade_risk_pct_must_be_numeric_gt_zero")
    elif single_risk > 100:
        blockers.append("max_single_trade_risk_pct_must_be_lte_one_hundred")
    if next_risk is None or next_risk <= 0:
        blockers.append("max_next_trade_risk_pct_must_be_numeric_gt_zero")
    elif next_risk > 100:
        blockers.append("max_next_trade_risk_pct_must_be_lte_one_hundred")
    if (
        single_risk is not None
        and next_risk is not None
        and single_risk > 0
        and next_risk > single_risk
    ):
        blockers.append("max_next_trade_risk_pct_must_not_exceed_single_trade_limit")

    if policy.get("demo_only") is not True:
        blockers.append("bucket_policy_demo_only_required")
    if policy.get("live_trading") is True:
        blockers.append("bucket_policy_live_trading_must_be_false")
    if policy.get("one_order_only") is not True:
        blockers.append("bucket_policy_one_order_only_required")
    if policy.get("require_owner_approval_for_next_trade") is not True:
        blockers.append("bucket_policy_owner_approval_for_next_trade_required")
    if not isinstance(policy.get("allow_next_trade_while_open_position"), bool):
        blockers.append(
            "allow_next_trade_while_open_position_must_be_boolean"
        )
    if not isinstance(policy.get("compounding_enabled"), bool):
        blockers.append("compounding_enabled_must_be_boolean")
    if policy.get("no_live_allocation") is False:
        blockers.append("bucket_policy_no_live_allocation_must_remain_true")
    if policy.get("live_allocation_allowed") is True:
        blockers.append("bucket_policy_live_allocation_must_remain_false")
    return blockers


def _next_trade_blockers(
    *,
    status: str,
    open_exposure_present: bool,
    pending_order_present: bool,
    policy: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if status != BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY:
        blockers.append("separation_inputs_not_ready")
    if policy.get("live_trading") is True:
        blockers.append("live_trading_rejected")
    if policy.get("one_order_only") is True and (
        open_exposure_present or pending_order_present
    ):
        blockers.append("one_order_only_blocks_additional_trade")
    if (
        open_exposure_present
        and policy.get("allow_next_trade_while_open_position") is not True
    ):
        blockers.append("open_trade_or_position_blocks_next_trade")
    if pending_order_present:
        blockers.append("pending_order_blocks_next_trade")
    if policy.get("require_owner_approval_for_next_trade") is True:
        blockers.append("owner_approval_required_for_next_trade")
    return _unique(blockers)


def _compound_blockers(
    *,
    open_exposure_present: bool,
    unrealized_pl: Decimal | None,
    compounding_enabled: bool,
) -> list[str]:
    blockers = ["compounding_deferred_to_result_bucket_step"]
    if open_exposure_present:
        blockers.append("open_trade_or_position_has_unrealized_pl_risk")
    if unrealized_pl is not None and unrealized_pl != 0:
        blockers.append("unrealized_pl_not_compoundable")
    if not compounding_enabled:
        blockers.append("policy_compounding_disabled")
    return _unique(blockers)


def _withdraw_blockers(
    *,
    open_exposure_present: bool,
    unrealized_pl: Decimal | None,
) -> list[str]:
    blockers = ["withdrawal_not_authorized_by_balance_separation_v1"]
    if open_exposure_present:
        blockers.append("open_trade_or_position_has_unrealized_pl_risk")
    if unrealized_pl is not None and unrealized_pl != 0:
        blockers.append("unrealized_pl_not_withdrawable")
    return _unique(blockers)


def _account_summary(values: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "balance_present": values["balance"] is not None,
        "nav_present": values["nav"] is not None,
        "unrealized_pl_present": values["unrealized_pl"] is not None,
        "realized_pl_present": values["realized_pl"] is not None,
        "margin_used": _as_float_or_none(values["margin_used"]),
        "margin_available": _as_float_or_none(values["margin_available"]),
        "open_trade_count": values["open_trade_count"],
        "open_position_count": values["open_position_count"],
        "pending_order_count": values["pending_order_count"],
    }


def _policy_summary(
    policy: Mapping[str, Any],
    values: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "bucket_currency": _text(policy.get("bucket_currency"), "MISSING"),
        "configured_trade_bucket_balance": _as_float_or_none(
            values["configured_trade_bucket_balance"]
        ),
        "max_single_trade_risk_pct": _as_float_or_none(
            values["max_single_trade_risk_pct"]
        ),
        "max_next_trade_risk_pct": _as_float_or_none(
            values["max_next_trade_risk_pct"]
        ),
        "demo_only": policy.get("demo_only") is True,
        "live_trading": policy.get("live_trading") is True,
        "one_order_only": policy.get("one_order_only") is True,
        "require_owner_approval_for_next_trade": policy.get(
            "require_owner_approval_for_next_trade"
        )
        is True,
        "allow_next_trade_while_open_position": policy.get(
            "allow_next_trade_while_open_position"
        )
        is True,
        "compounding_enabled": policy.get("compounding_enabled") is True,
        "no_live_allocation": policy.get("no_live_allocation") is not False,
    }


def _decision_summary(
    *,
    broker_balance: Decimal | None,
    broker_nav: Decimal | None,
    account_equity: Decimal | None,
    unrealized_pl: Decimal | None,
    trade_bucket: Decimal | None,
    open_exposure_present: bool,
    next_trade_allowed: bool,
) -> dict[str, Any]:
    return {
        "broker_balance_is_not_aios_trade_bucket": True,
        "broker_balance_equals_aios_trade_bucket": (
            broker_balance is not None
            and trade_bucket is not None
            and broker_balance == trade_bucket
        ),
        "nav_or_equity_includes_open_unrealized_pl": (
            broker_nav is not None
            and unrealized_pl is not None
            and account_equity is not None
            and account_equity != broker_balance
        ),
        "account_equity_source": (
            "broker_reported_nav"
            if broker_nav is not None
            else "balance_plus_unrealized_pl"
        ),
        "unrealized_pl_is_compoundable_profit": False,
        "unrealized_pl_is_withdrawable_profit": False,
        "risk_uses_configured_aios_bucket_not_full_broker_balance": True,
        "open_exposure_present": open_exposure_present,
        "next_trade_allowed": next_trade_allowed,
        "next_trade_requires_owner_approval": True,
        "live_allocation_allowed": False,
        "live_trading": False,
    }


def _warnings(status: str) -> list[str]:
    warnings = [
        "pure_python_in_memory_evaluator",
        "no_network_or_broker_call_performed",
        "no_order_or_position_mutation_performed",
        "no_credentials_or_account_ids_read",
        "broker_balance_is_not_aios_trade_bucket",
        "nav_equity_may_include_unrealized_pl",
        "unrealized_pl_not_withdrawable_or_compoundable",
        "risk_uses_configured_aios_bucket",
        "bucket_update_deferred_to_result_bucket_step",
        "next_trade_requires_owner_approval",
        "live_allocation_allowed_false",
    ]
    if status == BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY:
        warnings.append("balance_bucket_equity_separation_ready_for_review")
    return warnings


def _next_safe_action(status: str, next_trade_blockers: Sequence[str]) -> str:
    if status == BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY:
        if next_trade_blockers:
            return "hold_next_trade_until_policy_and_owner_approval_clear"
        return "owner_review_required_before_any_next_trade"
    return {
        BLOCKED_INVALID_ACCOUNT_SNAPSHOT: "provide_valid_sanitized_account_snapshot",
        BLOCKED_INVALID_BUCKET_RISK_POLICY: "provide_valid_aios_bucket_risk_policy",
        REJECTED_LIVE_TRADING: "keep_live_trading_false_before_balance_review",
        REJECTED_UNSAFE_AUTHORITY: "remove_unsafe_authority_flags_before_review",
    }.get(status, "stop_and_review_balance_bucket_equity_inputs")


def _risk_amount(
    bucket_balance: Decimal | None,
    risk_pct: Decimal | None,
) -> Decimal | None:
    if bucket_balance is None or risk_pct is None:
        return None
    return bucket_balance * risk_pct / Decimal("100")


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            authority = _mapping(node.get("execution_authority"))
            for field in EXECUTION_AUTHORITY_FIELDS:
                if node.get(field) is True or authority.get(field) is True:
                    blockers.append(f"unsafe_{label}_{field}_true")
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safety_proof() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _first_present(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not decimal_value.is_finite():
        return None
    return decimal_value


def _decimal_or_default(value: Decimal | None) -> Decimal:
    return value if value is not None else Decimal("0")


def _count_or_zero(value: Any) -> int:
    if value is None:
        return 0
    decimal_value = _decimal_or_none(value)
    if decimal_value is None or decimal_value < 0:
        return -1
    if decimal_value != decimal_value.to_integral_value():
        return -1
    return int(decimal_value)


def _as_float_or_none(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return default
    return str(value).strip()


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
