"""Metadata-only profit protection and future withdrawal-review evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1"
MODE = "READ_ONLY_METADATA_ONLY_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE"

PROFIT_PROTECTION_READY = "PROFIT_PROTECTION_READY"
PROFIT_LOCK_READY = "PROFIT_LOCK_READY"
WITHDRAWAL_REVIEW_FUTURE_READY = "WITHDRAWAL_REVIEW_FUTURE_READY"
REINVESTMENT_BUCKET_READY = "REINVESTMENT_BUCKET_READY"
OWNER_REVIEW_REQUIRED = "OWNER_REVIEW_REQUIRED"
BLOCKED_BY_UNREALIZED_PROFIT = "BLOCKED_BY_UNREALIZED_PROFIT"
BLOCKED_BY_MISSING_RECEIPTS = "BLOCKED_BY_MISSING_RECEIPTS"
BLOCKED_BY_COMPOUNDING_RESULT = "BLOCKED_BY_COMPOUNDING_RESULT"
BLOCKED_BY_PROFIT_POLICY = "BLOCKED_BY_PROFIT_POLICY"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

TARGET_TYPES = frozenset(
    {
        "RETURN_TARGET",
        "BALANCE_TARGET",
        "PROFIT_BUCKET_TARGET",
        "OWNER_REVIEW_TARGET",
    }
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "compounding_result",
    "profit_protection_policy",
    "profit_state",
    "claims",
)

REQUIRED_COMPOUNDING_FIELDS = (
    "status",
    "ready",
    "scale_decision",
    "protected_profit_amount",
    "reinvest_amount",
    "profit_lock_amount",
    "money_moved",
    "withdrawal_allowed_by_this_module",
    "bank_routing_allowed_by_this_module",
    "live_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

REQUIRED_POLICY_FIELDS = (
    "realized_profit_only",
    "receipts_required",
    "receipts_sanitized",
    "owner_review_required",
    "protect_profit_at_target",
    "profit_lock_pct",
    "reinvest_profit_pct",
    "minimum_profit_to_protect",
    "withdrawal_review_future_allowed",
    "withdrawal_execution_allowed",
    "bank_routing_allowed",
    "money_movement_allowed",
    "transfer_allowed",
    "ach_allowed",
    "wire_allowed",
    "card_allowed",
    "deposit_allowed",
)

REQUIRED_PROFIT_FIELDS = (
    "realized_net_profit",
    "unrealized_profit",
    "target_reached",
    "target_type",
    "receipts_ready",
    "pnl_reconciled",
    "fake_pnl_blocked",
    "balance_snapshot_ready",
)

REQUIRED_CLAIM_FIELDS = (
    "guaranteed_profit_claimed",
    "fixed_return_promised",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed_by_this_module",
    "demo_trade_executed_by_this_module",
    "broker_api_called_by_this_module",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "money_moved",
    "bank_access_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
    "bank_routing_built",
    "withdrawal_execution_built",
    "ach_built",
    "wire_built",
    "card_built",
    "deposit_built",
    "withdrawal_allowed_by_this_module",
    "bank_routing_allowed_by_this_module",
    "live_profit_guaranteed",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token",
    "password",
    "secret",
    "bearer",
    "account_id",
    "accountnumber",
    "routing_number",
    "card_number",
    "cvv",
    "master_password",
    "vault_password",
    "private_key",
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer ",
    "api key",
    "token value",
    "access token",
    "private key",
    "password",
    "secret",
    "-----begin",
)

BANKING_KEY_PARTS = (
    "bank",
    "banking",
    "withdraw",
    "withdrawal",
    "transfer",
    "ach",
    "wire",
    "card",
    "deposit",
    "money_movement",
    "money movement",
    "fund",
    "funding",
)

BANKING_KEY_TOKENS = frozenset(
    {
        "bank",
        "banking",
        "withdraw",
        "withdrawal",
        "transfer",
        "ach",
        "wire",
        "card",
        "deposit",
        "routing",
        "fund",
        "funding",
        "money",
        "movement",
    }
)

BANKING_ALLOWED_FALSE_FIELDS = frozenset(
    {
        "money_moved",
        "withdrawal_allowed_by_this_module",
        "bank_routing_allowed_by_this_module",
        "withdrawal_execution_allowed",
        "bank_routing_allowed",
        "money_movement_allowed",
        "transfer_allowed",
        "ach_allowed",
        "wire_allowed",
        "card_allowed",
        "deposit_allowed",
        "bank_access_used",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
        "bank_routing_built",
        "withdrawal_execution_built",
        "ach_built",
        "wire_built",
        "card_built",
        "deposit_built",
    }
)

BANKING_ALLOWED_TRUE_FIELDS = frozenset(
    {
        "withdrawal_review_future_allowed",
        "money_moved",
        "realized_profit_only",
        "receipts_required",
        "receipts_sanitized",
        "owner_review_required",
        "protect_profit_at_target",
        "fake_pnl_blocked",
        "balance_snapshot_ready",
    }
)


def evaluate_forex_profit_protection_and_withdrawal_review_future_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate profit protection and future withdrawal-review metadata only."""

    source = _mapping(payload)
    if not source:
        return _build_result(
            status=INCOMPLETE_INPUTS,
            ready=False,
            blockers=("payload_missing",),
            next_best_packet="AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
            safe_manual_next_action=(
                "Provide compounding_result, profit_protection_policy, profit_state, and claims."
            ),
            compounding_result={},
            policy={},
            profit_state={},
            claims={},
        )

    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _blocked_result(
            status=BLOCKED_BY_SENSITIVE_DATA,
            blockers=sensitive_blockers,
            next_best_packet="AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
            safe_manual_next_action="Remove sensitive keys or secret-like values before reevaluating.",
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _blocked_result(
            status=BLOCKED_BY_BANKING_FOCUS,
            blockers=banking_blockers,
            next_best_packet="AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
            safe_manual_next_action=(
                "Remove active withdrawal, routing, transfer, ACH, wire, card, deposit, "
                "or money-movement focus."
            ),
        )

    missing = tuple(
        f"{field}_missing" for field in REQUIRED_TOP_LEVEL_FIELDS if field not in source
    )
    if missing:
        return _blocked_result(
            status=INCOMPLETE_INPUTS,
            blockers=missing,
            next_best_packet="AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
            safe_manual_next_action="Provide all top-level sections required by this evaluator.",
        )

    compounding_result = _mapping(source.get("compounding_result"))
    policy = _mapping(source.get("profit_protection_policy"))
    profit_state = _mapping(source.get("profit_state"))
    claims = _mapping(source.get("claims"))

    compounding_blockers = _compounding_result_blockers(compounding_result)
    if compounding_blockers:
        return _blocked_result(
            status=BLOCKED_BY_COMPOUNDING_RESULT,
            blockers=compounding_blockers,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action="Repair compounding result metadata before future-review evaluation.",
            compounding_result=compounding_result,
            policy=policy,
            profit_state=profit_state,
            claims=claims,
        )

    policy_blockers = _profit_policy_blockers(policy)
    if policy_blockers:
        return _blocked_result(
            status=BLOCKED_BY_PROFIT_POLICY,
            blockers=policy_blockers,
            next_best_packet="AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
            safe_manual_next_action="Repair profit protection policy metadata and safety flags.",
            compounding_result=compounding_result,
            policy=policy,
            profit_state=profit_state,
            claims=claims,
        )

    profit_blockers = _profit_state_blockers(profit_state)
    if profit_blockers:
        if "realized_only_unrealized_profit_present" in profit_blockers:
            return _blocked_result(
                status=BLOCKED_BY_UNREALIZED_PROFIT,
                blockers=profit_blockers,
                next_best_packet="AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1",
                safe_manual_next_action="Verify realized profit before considering unrealized profit.",
                compounding_result=compounding_result,
                policy=policy,
                profit_state=profit_state,
                claims=claims,
            )
        return _blocked_result(
            status=BLOCKED_BY_MISSING_RECEIPTS,
            blockers=profit_blockers,
            next_best_packet="AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1",
            safe_manual_next_action="Repair receipts, reconciliation, and balance snapshot metadata.",
            compounding_result=compounding_result,
            policy=policy,
            profit_state=profit_state,
            claims=claims,
        )

    claim_blockers = _claim_blockers(claims)
    if claim_blockers:
        return _blocked_result(
            status=BLOCKED_BY_PROFIT_CLAIM,
            blockers=claim_blockers,
            next_best_packet="AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
            safe_manual_next_action="Remove all profit guarantee and fixed-return claims.",
            compounding_result=compounding_result,
            policy=policy,
            profit_state=profit_state,
            claims=claims,
        )

    status = _decision_status(compounding_result, policy, profit_state)
    return _decision_result(
        status=status,
        compounding_result=compounding_result,
        policy=policy,
        profit_state=profit_state,
        claims=claims,
    )


def _decision_status(
    compounding_result: Mapping[str, Any],
    policy: Mapping[str, Any],
    profit_state: Mapping[str, Any],
) -> str:
    realized_net_profit = _number(profit_state.get("realized_net_profit"))
    minimum_profit_to_protect = _number(policy.get("minimum_profit_to_protect"))
    reinvest_amount = _number(compounding_result.get("reinvest_amount"))
    target_reached = _bool(profit_state.get("target_reached"))
    target_type = str(profit_state.get("target_type", ""))
    receipts_ready = _bool(profit_state.get("receipts_ready"))
    pnl_reconciled = _bool(profit_state.get("pnl_reconciled"))
    fake_pnl_blocked = _bool(profit_state.get("fake_pnl_blocked"))
    balance_snapshot_ready = _bool(profit_state.get("balance_snapshot_ready"))

    if target_reached and realized_net_profit > 0:
        return WITHDRAWAL_REVIEW_FUTURE_READY
    if target_type == "OWNER_REVIEW_TARGET":
        return OWNER_REVIEW_REQUIRED
    if (
        realized_net_profit >= minimum_profit_to_protect
        and receipts_ready
        and pnl_reconciled
        and fake_pnl_blocked
        and balance_snapshot_ready
    ):
        return PROFIT_LOCK_READY
    if reinvest_amount > 0 and not target_reached:
        return REINVESTMENT_BUCKET_READY
    if realized_net_profit > 0:
        return PROFIT_PROTECTION_READY
    return OWNER_REVIEW_REQUIRED


def _decision_result(
    *,
    status: str,
    compounding_result: Mapping[str, Any],
    policy: Mapping[str, Any],
    profit_state: Mapping[str, Any],
    claims: Mapping[str, Any],
) -> dict[str, Any]:
    realized_net_profit = _number(profit_state.get("realized_net_profit"))
    profit_lock_pct = _bounded_percent(_number(policy.get("profit_lock_pct")))
    reinvest_profit_pct = _bounded_percent(_number(policy.get("reinvest_profit_pct")))
    protected_profit_amount = _round(realized_net_profit * profit_lock_pct)
    reinvest_amount = _round(realized_net_profit * reinvest_profit_pct)
    deferred_withdrawal_review_amount = _round(
        max(realized_net_profit - protected_profit_amount - reinvest_amount, 0.0)
    )
    profit_lock_amount = _round(
        _number(compounding_result.get("profit_lock_amount"))
        if "profit_lock_amount" in compounding_result
        else protected_profit_amount
    )
    if profit_lock_amount == 0.0 and protected_profit_amount > 0.0:
        profit_lock_amount = protected_profit_amount

    ready = status in {
        PROFIT_LOCK_READY,
        WITHDRAWAL_REVIEW_FUTURE_READY,
        REINVESTMENT_BUCKET_READY,
        OWNER_REVIEW_REQUIRED,
    }
    result = _build_result(
        status=status,
        ready=ready,
        compounding_result=compounding_result,
        policy=policy,
        profit_state=profit_state,
        claims=claims,
        blockers=(),
        next_best_packet=_next_packet(status),
        safe_manual_next_action=_safe_manual_next_action(status),
        protected_profit_amount=protected_profit_amount,
        reinvest_amount=reinvest_amount,
        deferred_withdrawal_review_amount=deferred_withdrawal_review_amount,
        profit_lock_amount=profit_lock_amount,
        withdrawal_review_future_enabled=status == WITHDRAWAL_REVIEW_FUTURE_READY,
        compounding_status=str(compounding_result.get("status", "")),
        compounding_ready=_bool(compounding_result.get("ready")),
        compounding_scale_decision=str(compounding_result.get("scale_decision", "")),
    )
    return result


def _blocked_result(
    *,
    status: str,
    blockers: Sequence[str],
    next_best_packet: str,
    safe_manual_next_action: str,
    compounding_result: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
    profit_state: Mapping[str, Any] | None = None,
    claims: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_result(
        status=status,
        ready=False,
        compounding_result=_mapping(compounding_result),
        policy=_mapping(policy),
        profit_state=_mapping(profit_state),
        claims=_mapping(claims),
        blockers=blockers,
        next_best_packet=next_best_packet,
        safe_manual_next_action=safe_manual_next_action,
        protected_profit_amount=0.0,
        reinvest_amount=0.0,
        deferred_withdrawal_review_amount=0.0,
        profit_lock_amount=0.0,
        withdrawal_review_future_enabled=False,
        compounding_status=str(_mapping(compounding_result).get("status", "")),
        compounding_ready=_bool(_mapping(compounding_result).get("ready")),
        compounding_scale_decision=str(_mapping(compounding_result).get("scale_decision", "")),
    )


def _build_result(
    *,
    status: str,
    ready: bool,
    compounding_result: Mapping[str, Any],
    policy: Mapping[str, Any],
    profit_state: Mapping[str, Any],
    claims: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
    safe_manual_next_action: str,
    protected_profit_amount: float,
    reinvest_amount: float,
    deferred_withdrawal_review_amount: float,
    profit_lock_amount: float,
    withdrawal_review_future_enabled: bool,
    compounding_status: str,
    compounding_ready: bool,
    compounding_scale_decision: str,
) -> dict[str, Any]:
    result = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": bool(ready),
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "profit_protection_enabled": status
        in {
            PROFIT_LOCK_READY,
            WITHDRAWAL_REVIEW_FUTURE_READY,
            REINVESTMENT_BUCKET_READY,
            OWNER_REVIEW_REQUIRED,
        },
        "realized_profit_only": _bool(policy.get("realized_profit_only")),
        "protected_profit_amount": _round(protected_profit_amount),
        "reinvest_amount": _round(reinvest_amount),
        "deferred_withdrawal_review_amount": _round(deferred_withdrawal_review_amount),
        "profit_lock_amount": _round(profit_lock_amount),
        "withdrawal_review_future_enabled": bool(withdrawal_review_future_enabled),
        "withdrawal_execution_allowed": False,
        "bank_routing_allowed": False,
        "money_moved": False,
        "profit_bucket_summary": _profit_bucket_summary(
            protected_profit_amount=protected_profit_amount,
            reinvest_amount=reinvest_amount,
            deferred_withdrawal_review_amount=deferred_withdrawal_review_amount,
            profit_lock_amount=profit_lock_amount,
            policy=policy,
            profit_state=profit_state,
        ),
        "future_review_summary": _future_review_summary(
            status=status,
            withdrawal_review_future_enabled=withdrawal_review_future_enabled,
            policy=policy,
            profit_state=profit_state,
            deferred_withdrawal_review_amount=deferred_withdrawal_review_amount,
        ),
        "compounding_summary": _compounding_summary(
            compounding_result=compounding_result,
            compounding_status=compounding_status,
            compounding_ready=compounding_ready,
            compounding_scale_decision=compounding_scale_decision,
            protected_profit_amount=protected_profit_amount,
            reinvest_amount=reinvest_amount,
            profit_lock_amount=profit_lock_amount,
        ),
        "blockers": list(_unique(blockers)),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": safe_manual_next_action,
        "audit_record": _audit_record(
            status=status,
            ready=ready,
            compounding_result=compounding_result,
            policy=policy,
            profit_state=profit_state,
            claims=claims,
            blockers=blockers,
            next_best_packet=next_best_packet,
            protected_profit_amount=protected_profit_amount,
            reinvest_amount=reinvest_amount,
            deferred_withdrawal_review_amount=deferred_withdrawal_review_amount,
            profit_lock_amount=profit_lock_amount,
            withdrawal_review_future_enabled=withdrawal_review_future_enabled,
            compounding_status=compounding_status,
            compounding_ready=compounding_ready,
            compounding_scale_decision=compounding_scale_decision,
        ),
        "safety": _safety_profile(),
    }
    result.update({field: False for field in HARD_FALSE_FIELDS})
    return result


def _audit_record(
    *,
    status: str,
    ready: bool,
    compounding_result: Mapping[str, Any],
    policy: Mapping[str, Any],
    profit_state: Mapping[str, Any],
    claims: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
    protected_profit_amount: float,
    reinvest_amount: float,
    deferred_withdrawal_review_amount: float,
    profit_lock_amount: float,
    withdrawal_review_future_enabled: bool,
    compounding_status: str,
    compounding_ready: bool,
    compounding_scale_decision: str,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": bool(ready),
        "owner_decision_required": True,
        "read_only": True,
        "metadata_only": True,
        "withdrawal_review_future_enabled": bool(withdrawal_review_future_enabled),
        "withdrawal_execution_allowed": False,
        "bank_routing_allowed": False,
        "money_moved": False,
        "compounding_status": compounding_status,
        "compounding_ready": bool(compounding_ready),
        "compounding_scale_decision": compounding_scale_decision,
        "protected_profit_amount": _round(protected_profit_amount),
        "reinvest_amount": _round(reinvest_amount),
        "deferred_withdrawal_review_amount": _round(deferred_withdrawal_review_amount),
        "profit_lock_amount": _round(profit_lock_amount),
        "blockers": list(_unique(blockers)),
        "next_best_packet": next_best_packet,
        "realized_net_profit": _number(profit_state.get("realized_net_profit")),
        "unrealized_profit": _number(profit_state.get("unrealized_profit")),
        "profit_guarantee_free": not any(
            _bool(claims.get(field)) for field in REQUIRED_CLAIM_FIELDS
        ),
        "compounding_ready": _bool(compounding_result.get("ready")),
        "policy_realized_profit_only": _bool(policy.get("realized_profit_only")),
    }


def _safety_profile() -> dict[str, bool]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "no_broker_trade": True,
        "no_broker_api_called": True,
        "no_live_trading": True,
        "no_demo_trading": True,
        "no_credential_read": True,
        "no_money_movement": True,
        "no_banking": True,
        "no_withdrawal_execution": True,
        "no_bank_routing": True,
        "no_transfer": True,
        "no_ach": True,
        "no_wire": True,
        "no_card": True,
        "no_deposit": True,
        "no_scheduler": True,
        "no_daemon": True,
        "no_webhook": True,
        "no_dashboard_runtime": True,
        "no_profit_guarantee": True,
        "no_fixed_return_promise": True,
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _profit_bucket_summary(
    *,
    protected_profit_amount: float,
    reinvest_amount: float,
    deferred_withdrawal_review_amount: float,
    profit_lock_amount: float,
    policy: Mapping[str, Any],
    profit_state: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "realized_profit_only": _bool(policy.get("realized_profit_only")),
        "target_reached": _bool(profit_state.get("target_reached")),
        "minimum_profit_to_protect": _number(policy.get("minimum_profit_to_protect")),
        "profit_lock_pct": _bounded_percent(_number(policy.get("profit_lock_pct"))),
        "reinvest_profit_pct": _bounded_percent(_number(policy.get("reinvest_profit_pct"))),
        "protected_profit_amount": _round(protected_profit_amount),
        "profit_lock_amount": _round(profit_lock_amount),
        "reinvest_amount": _round(reinvest_amount),
        "deferred_withdrawal_review_amount": _round(deferred_withdrawal_review_amount),
    }


def _future_review_summary(
    *,
    status: str,
    withdrawal_review_future_enabled: bool,
    policy: Mapping[str, Any],
    profit_state: Mapping[str, Any],
    deferred_withdrawal_review_amount: float,
) -> dict[str, Any]:
    return {
        "status": status,
        "withdrawal_review_future_enabled": bool(withdrawal_review_future_enabled),
        "owner_review_required": _bool(policy.get("owner_review_required")),
        "withdrawal_review_future_allowed": _bool(
            policy.get("withdrawal_review_future_allowed")
        ),
        "target_reached": _bool(profit_state.get("target_reached")),
        "target_type": str(profit_state.get("target_type", "")),
        "deferred_withdrawal_review_amount": _round(deferred_withdrawal_review_amount),
    }


def _compounding_summary(
    *,
    compounding_result: Mapping[str, Any],
    compounding_status: str,
    compounding_ready: bool,
    compounding_scale_decision: str,
    protected_profit_amount: float,
    reinvest_amount: float,
    profit_lock_amount: float,
) -> dict[str, Any]:
    return {
        "status": compounding_status,
        "ready": bool(compounding_ready),
        "scale_decision": compounding_scale_decision,
        "protected_profit_amount": _round(
            _number(compounding_result.get("protected_profit_amount"))
            if "protected_profit_amount" in compounding_result
            else protected_profit_amount
        ),
        "reinvest_amount": _round(
            _number(compounding_result.get("reinvest_amount"))
            if "reinvest_amount" in compounding_result
            else reinvest_amount
        ),
        "profit_lock_amount": _round(
            _number(compounding_result.get("profit_lock_amount"))
            if "profit_lock_amount" in compounding_result
            else profit_lock_amount
        ),
        "money_moved": _bool(compounding_result.get("money_moved")),
        "withdrawal_allowed_by_this_module": _bool(
            compounding_result.get("withdrawal_allowed_by_this_module")
        ),
        "bank_routing_allowed_by_this_module": _bool(
            compounding_result.get("bank_routing_allowed_by_this_module")
        ),
        "live_profit_guaranteed": _bool(compounding_result.get("live_profit_guaranteed")),
        "fixed_return_promised_by_aios": _bool(
            compounding_result.get("fixed_return_promised_by_aios")
        ),
    }


def _compounding_result_blockers(compounding_result: Mapping[str, Any]) -> tuple[str, ...]:
    if not compounding_result:
        return ("compounding_result_missing",)
    missing = tuple(
        f"missing_compounding_result_{field}"
        for field in REQUIRED_COMPOUNDING_FIELDS
        if field not in compounding_result
    )
    if missing:
        return missing
    blockers: list[str] = []
    if _bool(compounding_result.get("ready")) is False:
        blockers.append("compounding_result_ready_false")
    if not isinstance(compounding_result.get("scale_decision"), str):
        blockers.append("scale_decision_not_string")
    if _bool(compounding_result.get("money_moved")) is True:
        blockers.append("money_moved_true")
    if compounding_result.get("withdrawal_allowed_by_this_module") is not False:
        blockers.append("withdrawal_allowed_by_this_module_not_false")
    if compounding_result.get("bank_routing_allowed_by_this_module") is not False:
        blockers.append("bank_routing_allowed_by_this_module_not_false")
    if compounding_result.get("live_profit_guaranteed") is not False:
        blockers.append("live_profit_guaranteed_not_false")
    if compounding_result.get("fixed_return_promised_by_aios") is not False:
        blockers.append("fixed_return_promised_by_aios_not_false")
    if not _is_number(compounding_result.get("protected_profit_amount")):
        blockers.append("protected_profit_amount_not_number")
    if not _is_number(compounding_result.get("reinvest_amount")):
        blockers.append("reinvest_amount_not_number")
    if not _is_number(compounding_result.get("profit_lock_amount")):
        blockers.append("profit_lock_amount_not_number")
    return tuple(_unique(blockers))


def _profit_policy_blockers(policy: Mapping[str, Any]) -> tuple[str, ...]:
    if not policy:
        return ("profit_protection_policy_missing",)
    missing = tuple(
        f"missing_profit_policy_{field}"
        for field in REQUIRED_POLICY_FIELDS
        if field not in policy
    )
    if missing:
        return missing
    blockers: list[str] = []
    for field in (
        "realized_profit_only",
        "receipts_required",
        "receipts_sanitized",
        "owner_review_required",
        "protect_profit_at_target",
        "withdrawal_review_future_allowed",
    ):
        if policy.get(field) is not True:
            blockers.append(f"{field}_must_be_true")

    for field in (
        "withdrawal_execution_allowed",
        "bank_routing_allowed",
        "money_movement_allowed",
        "transfer_allowed",
        "ach_allowed",
        "wire_allowed",
        "card_allowed",
        "deposit_allowed",
    ):
        if policy.get(field) is not False:
            blockers.append(f"{field}_must_be_false")

    for field in ("profit_lock_pct", "reinvest_profit_pct"):
        value = _number(policy.get(field))
        if not _is_number(policy.get(field)):
            blockers.append(f"{field}_not_number")
        elif not 0 <= value <= 1:
            blockers.append(f"{field}_out_of_range")

    if not _is_number(policy.get("minimum_profit_to_protect")):
        blockers.append("minimum_profit_to_protect_not_number")
    elif _number(policy.get("minimum_profit_to_protect")) < 0:
        blockers.append("minimum_profit_to_protect_negative")

    return tuple(_unique(blockers))


def _profit_state_blockers(profit_state: Mapping[str, Any]) -> tuple[str, ...]:
    if not profit_state:
        return ("profit_state_missing",)
    missing = tuple(
        f"missing_profit_state_{field}"
        for field in REQUIRED_PROFIT_FIELDS
        if field not in profit_state
    )
    if missing:
        return missing
    blockers: list[str] = []
    if not _is_number(profit_state.get("realized_net_profit")):
        blockers.append("realized_net_profit_not_number")
    if not _is_number(profit_state.get("unrealized_profit")):
        blockers.append("unrealized_profit_not_number")
    if not isinstance(profit_state.get("target_reached"), bool):
        blockers.append("target_reached_not_bool")
    if str(profit_state.get("target_type", "")) not in TARGET_TYPES:
        blockers.append("target_type_invalid")
    for field in ("receipts_ready", "pnl_reconciled", "fake_pnl_blocked", "balance_snapshot_ready"):
        if profit_state.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    realized_net_profit = _number(profit_state.get("realized_net_profit"))
    unrealized_profit = _number(profit_state.get("unrealized_profit"))
    if realized_net_profit <= 0 and unrealized_profit > 0:
        blockers.append("realized_only_unrealized_profit_present")
    return tuple(_unique(blockers))


def _claim_blockers(claims: Mapping[str, Any]) -> tuple[str, ...]:
    if not claims:
        return ("claims_missing",)
    missing = tuple(
        f"missing_claim_{field}" for field in REQUIRED_CLAIM_FIELDS if field not in claims
    )
    if missing:
        return missing
    if any(_bool(claims.get(field)) for field in REQUIRED_CLAIM_FIELDS):
        return ("profit_claim_block_detected",)
    return ()


def _next_packet(status: str) -> str:
    if status == WITHDRAWAL_REVIEW_FUTURE_READY:
        return "AIOS_FOREX_PROFIT_WITHDRAWAL_OWNER_REVIEW_FUTURE_V1"
    if status == PROFIT_LOCK_READY:
        return "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"
    if status == REINVESTMENT_BUCKET_READY:
        return "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
    if status == PROFIT_PROTECTION_READY:
        return "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1"
    if status == OWNER_REVIEW_REQUIRED:
        return "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"
    if status == BLOCKED_BY_UNREALIZED_PROFIT:
        return "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"
    if status == BLOCKED_BY_MISSING_RECEIPTS:
        return "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
    if status == BLOCKED_BY_COMPOUNDING_RESULT:
        return "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"
    return "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1"


def _safe_manual_next_action(status: str) -> str:
    if status == WITHDRAWAL_REVIEW_FUTURE_READY:
        return "Route to future owner review; do not build withdrawal execution."
    if status == PROFIT_LOCK_READY:
        return "Lock realized profit and keep withdrawal deferred."
    if status == REINVESTMENT_BUCKET_READY:
        return "Keep reinvestment in metadata-only active supervision."
    if status == PROFIT_PROTECTION_READY:
        return "Profit protection metadata is ready; keep the review lane open."
    if status == OWNER_REVIEW_REQUIRED:
        return "Owner review required before any future banking lane."
    if status == BLOCKED_BY_UNREALIZED_PROFIT:
        return "Verify realized profit before any protection review."
    if status == BLOCKED_BY_MISSING_RECEIPTS:
        return "Repair receipts and reconciliation metadata."
    if status == BLOCKED_BY_COMPOUNDING_RESULT:
        return "Repair compounding result metadata first."
    if status == BLOCKED_BY_PROFIT_POLICY:
        return "Repair profit protection policy metadata and safety flags."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove active banking and money-movement focus keys."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive data from the payload."
    if status == BLOCKED_BY_PROFIT_CLAIM:
        return "Remove profit guarantee and fixed-return claims."
    return "Repair blocked inputs and rerun this metadata packet."


def _banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{raw_key}"
            if key in BANKING_ALLOWED_FALSE_FIELDS and child is False:
                continue
            if key in BANKING_ALLOWED_TRUE_FIELDS and child is True:
                continue
            if _banking_focus_key_active(key) and _is_active_focus(child):
                blockers.append(f"{child_path}:banking_focus")
                continue
            blockers.extend(_banking_focus_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_banking_focus_blockers(child, f"{path}[{index}]"))
    return tuple(_unique(blockers))


def _banking_focus_key_active(key: str) -> bool:
    if "money_movement" in key:
        return True
    tokens = set(key.split("_"))
    return any(token in BANKING_KEY_TOKENS for token in tokens)


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{raw_key}"
            if any(part in key for part in SENSITIVE_KEY_PARTS) and not _safe_sensitive_value(child):
                blockers.append(f"{child_path}:sensitive_key")
            blockers.extend(_sensitive_data_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    if isinstance(value, str) and not _safe_sensitive_value(value) and _looks_secret_string(value):
        blockers.append(f"{path}:secret_like_value")
    return tuple(_unique(blockers))


def _looks_secret_string(value: str) -> bool:
    lowered = value.lower()
    if any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS):
        return True
    return len(value) >= 16 and _has_long_digit_run(value, minimum=12)


def _has_long_digit_run(value: str, minimum: int = 12) -> bool:
    run = 0
    for char in value:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _safe_sensitive_value(value: Any) -> bool:
    if isinstance(value, str):
        try:
            float(value)
        except ValueError:
            return False
        return True
    return False


def _is_active_focus(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        return lowered not in {"", "false", "0", "none", "off", "disabled"}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _bounded_percent(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def _round(value: float) -> float:
    return round(float(value), 6)


def _bool(value: Any) -> bool:
    return value is True


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result
