"""Metadata-only governed compounding capital scaling evaluator for Forex."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"
MODE = "READ_ONLY_METADATA_ONLY_GOVERNED_COMPOUNDING_CAPITAL_SCALING"

GOVERNED_COMPOUNDING_SCALE_READY = "GOVERNED_COMPOUNDING_SCALE_READY"
GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED = "GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED"
GOVERNED_COMPOUNDING_HOLD_REQUIRED = "GOVERNED_COMPOUNDING_HOLD_REQUIRED"
GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED = "GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED"
GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT = (
    "GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT"
)
GOVERNED_COMPOUNDING_STOP_REQUIRED = "GOVERNED_COMPOUNDING_STOP_REQUIRED"
GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED = (
    "GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED"
)
BLOCKED_BY_BALANCE_OBSERVER = "BLOCKED_BY_BALANCE_OBSERVER"
BLOCKED_BY_RECEIPT_PROOF = "BLOCKED_BY_RECEIPT_PROOF"
BLOCKED_BY_RISK_STATE = "BLOCKED_BY_RISK_STATE"
BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

REQUIRED_TOP_LEVEL_FIELDS = (
    "balance_observer_result",
    "compounding_scale_policy",
    "proof_state",
    "risk_state",
    "claims",
)

REQUIRED_BALANCE_FIELDS = (
    "status",
    "ready",
    "realized_profit_from_baseline",
    "equity_drift",
    "target_return_reached",
    "target_balance_reached",
    "withdrawal_deferred",
    "bank_routing_deferred",
    "money_moved",
)

REQUIRED_POLICY_FIELDS = (
    "compounding_enabled",
    "owner_review_required",
    "scale_up_allowed",
    "scale_down_on_drawdown",
    "stop_at_target",
    "current_risk_budget_pct",
    "max_scale_step_pct",
    "max_risk_per_trade_pct",
    "max_total_burst_risk_pct",
    "profit_lock_pct",
    "reinvest_profit_pct",
    "minimum_verified_profit_to_scale",
    "consecutive_scale_ups_since_review",
    "max_consecutive_scale_ups_before_review",
    "withdrawal_allowed",
    "bank_routing_allowed",
    "money_movement_allowed",
)

REQUIRED_PROOF_FIELDS = (
    "receipts_sanitized",
    "realized_pnl_verified",
    "repeatability_score",
    "proof_ready_for_scaling",
    "fake_pnl_blocked",
)

REQUIRED_RISK_FIELDS = (
    "kill_switch_active",
    "daily_loss_stop_active",
    "drawdown_within_limit",
    "current_drawdown_pct",
    "max_drawdown_pct",
    "current_daily_loss_pct",
    "max_daily_loss_pct",
)

REQUIRED_CLAIM_FIELDS = (
    "guaranteed_profit_claimed",
    "fixed_return_promised",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
)

SCALE_DECISION_SCALE_UP = "SCALE_UP"
SCALE_DECISION_HOLD = "HOLD"
SCALE_DECISION_SCALE_DOWN = "SCALE_DOWN"
SCALE_DECISION_PROTECT_PROFIT = "PROTECT_PROFIT"
SCALE_DECISION_STOP = "STOP_COMPOUNDING"
SCALE_DECISION_OWNER_REVIEW = "OWNER_REVIEW_REQUIRED"
SCALE_DECISION_BLOCKED = "BLOCKED"

SCALE_DIRECTION_UP = "UP"
SCALE_DIRECTION_DOWN = "DOWN"
SCALE_DIRECTION_HOLD = "HOLD"
SCALE_DIRECTION_REVIEW = "REVIEW"
SCALE_DIRECTION_STOP = "STOP"
SCALE_DIRECTION_NONE = "NONE"

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
    "routing",
    "money_movement",
    "money movement",
    "transfer",
    "fund",
    "funding",
    "acount",
)

BANKING_ALLOWED_FALSE_FIELDS = frozenset(
    {
        "withdrawal_allowed",
        "bank_routing_allowed",
        "money_movement_allowed",
        "money_moved",
        "withdrawal_work_built",
        "bank_routing_built",
        "banking_work_built",
        "transfer_work_built",
        "bank_access_used",
    }
)
BANKING_ALLOWED_TRUE_FIELDS = frozenset(
    {
        "withdrawal_deferred",
        "bank_routing_deferred",
    }
)


def evaluate_forex_governed_compounding_capital_scaling_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate governed compounding decisions from metadata only."""

    source = _mapping(payload)
    if not source:
        return _build_result(
            status=INCOMPLETE_INPUTS,
            ready=False,
            blockers=("payload_missing",),
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action="Provide complete payload sections for balance, policy, proof, risk, and claims.",
            balance={},
            policy={},
            proof={},
            risk={},
            claims={},
        )

    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _blocked_result(
            status=BLOCKED_BY_SENSITIVE_DATA,
            blockers=sensitive_blockers,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action="Remove sensitive keys or values from payload before reevaluating.",
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _blocked_result(
            status=BLOCKED_BY_BANKING_FOCUS,
            blockers=banking_blockers,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action=(
                "Remove active withdrawal/banking/routing/money-movement focus fields. "
                "Keep explicit false or deferred safety fields."
            ),
        )

    missing = tuple(
        f"{field}_missing" for field in REQUIRED_TOP_LEVEL_FIELDS if field not in source
    )
    if missing:
        return _blocked_result(
            status=INCOMPLETE_INPUTS,
            blockers=missing,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action="Provide all five top-level sections required by this evaluator.",
        )

    balance = _mapping(source.get("balance_observer_result"))
    policy = _mapping(source.get("compounding_scale_policy"))
    proof = _mapping(source.get("proof_state"))
    risk = _mapping(source.get("risk_state"))
    claims = _mapping(source.get("claims"))

    balance_blockers = _balance_blockers(balance)
    if balance_blockers:
        return _blocked_result(
            status=BLOCKED_BY_BALANCE_OBSERVER,
            blockers=balance_blockers,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action="Repair balance observer metadata and provide sanitized balance fields.",
            balance=balance,
            policy=policy,
            proof=proof,
            risk=risk,
            claims=claims,
        )

    proof_blockers = _proof_blockers(proof)
    if proof_blockers:
        return _blocked_result(
            status=BLOCKED_BY_RECEIPT_PROOF,
            blockers=proof_blockers,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action=(
                "Provide receipts_sanitized=True, realized_pnl_verified=True, "
                "proof_ready_for_scaling=True, and fake_pnl_blocked=True."
            ),
            balance=balance,
            policy=policy,
            proof=proof,
            risk=risk,
            claims=claims,
        )

    policy_blockers = _policy_blockers(policy)
    if policy_blockers:
        return _blocked_result(
            status=BLOCKED_BY_POLICY,
            blockers=policy_blockers,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action=(
                "Repair compounding policy metadata and enforce explicit false safety flags."
            ),
            balance=balance,
            policy=policy,
            proof=proof,
            risk=risk,
            claims=claims,
        )

    risk_blockers, risk_state_ready = _risk_blockers(risk)
    if risk_blockers:
        return _blocked_result(
            status=BLOCKED_BY_RISK_STATE,
            blockers=risk_blockers,
            next_best_packet=(
                "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"
            ),
            safe_manual_next_action=(
                "Resolve active kill-switch or daily-loss-stop state and retry."
            ),
            balance=balance,
            policy=policy,
            proof=proof,
            risk=risk,
            claims=claims,
        )
    if not risk_state_ready:
        status = GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED
        return _decision_result(
            status=status,
            balance=balance,
            policy=policy,
            proof=proof,
            risk=risk,
            claims=claims,
        )

    claim_blockers = _claim_blockers(claims)
    if claim_blockers:
        return _blocked_result(
            status=BLOCKED_BY_PROFIT_CLAIM,
            blockers=claim_blockers,
            next_best_packet="AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
            safe_manual_next_action="Remove profit guarantee and fixed-return claim metadata.",
            balance=balance,
            policy=policy,
            proof=proof,
            risk=risk,
            claims=claims,
        )

    return _decision_result(
        status=_decision_status(
            balance=balance,
            policy=policy,
            proof=proof,
        ),
        balance=balance,
        policy=policy,
        proof=proof,
        risk=risk,
        claims=claims,
    )


def _decision_result(
    *,
    status: str,
    balance: Mapping[str, Any],
    policy: Mapping[str, Any],
    proof: Mapping[str, Any],
    risk: Mapping[str, Any],
    claims: Mapping[str, Any],
) -> dict[str, Any]:
    ready = status in {
        GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED,
        GOVERNED_COMPOUNDING_HOLD_REQUIRED,
        GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED,
        GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT,
        GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED,
    }
    scale_decision = _scale_decision(status)
    scale_direction = _scale_direction(status)
    return _build_result(
        status=status,
        ready=ready,
        balance=balance,
        policy=policy,
        proof=proof,
        risk=risk,
        claims=claims,
        blockers=(),
        next_best_packet=_next_packet(status),
        safe_manual_next_action=_safe_manual_next_action(status),
        scale_decision=scale_decision,
        scale_direction=scale_direction,
    )


def _blocked_result(
    *,
    status: str,
    blockers: Sequence[str],
    next_best_packet: str,
    safe_manual_next_action: str,
    balance: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
    proof: Mapping[str, Any] | None = None,
    risk: Mapping[str, Any] | None = None,
    claims: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_result(
        status=status,
        ready=False,
        balance=_mapping(balance),
        policy=_mapping(policy),
        proof=_mapping(proof),
        risk=_mapping(risk),
        claims=_mapping(claims),
        blockers=tuple(blockers),
        next_best_packet=next_best_packet,
        safe_manual_next_action=safe_manual_next_action,
        scale_decision=SCALE_DECISION_BLOCKED,
        scale_direction=SCALE_DIRECTION_NONE,
    )


def _decision_status(
    *,
    balance: Mapping[str, Any],
    policy: Mapping[str, Any],
    proof: Mapping[str, Any],
) -> str:
    if _bool(balance.get("target_return_reached")) or _bool(
        balance.get("target_balance_reached")
    ):
        return GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT
    if _bool(policy.get("compounding_enabled")) is False:
        return GOVERNED_COMPOUNDING_HOLD_REQUIRED
    if _number(balance.get("realized_profit_from_baseline")) < _number(
        policy.get("minimum_verified_profit_to_scale")
    ):
        return GOVERNED_COMPOUNDING_HOLD_REQUIRED
    if _number(proof.get("repeatability_score")) < 70:
        return GOVERNED_COMPOUNDING_HOLD_REQUIRED
    if _bool(policy.get("scale_up_allowed")) is False:
        return GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED
    if _integer(policy.get("consecutive_scale_ups_since_review")) >= _integer(
        policy.get("max_consecutive_scale_ups_before_review")
    ):
        return GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED
    return GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED


def _scale_decision(status: str) -> str:
    if status == GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED:
        return SCALE_DECISION_SCALE_UP
    if status == GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED:
        return SCALE_DECISION_SCALE_DOWN
    if status == GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT:
        return SCALE_DECISION_PROTECT_PROFIT
    if status == GOVERNED_COMPOUNDING_STOP_REQUIRED:
        return SCALE_DECISION_STOP
    if status == GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED:
        return SCALE_DECISION_OWNER_REVIEW
    if status == GOVERNED_COMPOUNDING_HOLD_REQUIRED:
        return SCALE_DECISION_HOLD
    return SCALE_DECISION_BLOCKED


def _scale_direction(status: str) -> str:
    if status == GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED:
        return SCALE_DIRECTION_UP
    if status == GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED:
        return SCALE_DIRECTION_DOWN
    if status == GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT:
        return SCALE_DIRECTION_NONE
    if status == GOVERNED_COMPOUNDING_STOP_REQUIRED:
        return SCALE_DIRECTION_STOP
    if status == GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED:
        return SCALE_DIRECTION_REVIEW
    if status == GOVERNED_COMPOUNDING_HOLD_REQUIRED:
        return SCALE_DIRECTION_HOLD
    return SCALE_DIRECTION_NONE


def _build_result(
    *,
    status: str,
    ready: bool,
    balance: Mapping[str, Any],
    policy: Mapping[str, Any],
    proof: Mapping[str, Any],
    risk: Mapping[str, Any],
    claims: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
    safe_manual_next_action: str,
    scale_decision: str = SCALE_DECISION_HOLD,
    scale_direction: str = SCALE_DIRECTION_HOLD,
) -> dict[str, Any]:
    current_risk_budget_pct = _number(policy.get("current_risk_budget_pct"))
    max_scale_step_pct = _number(policy.get("max_scale_step_pct"))
    max_risk_per_trade_pct = _number(policy.get("max_risk_per_trade_pct"))
    profit_lock_pct = _bounded_percent(_number(policy.get("profit_lock_pct")))
    reinvest_profit_pct = _bounded_percent(_number(policy.get("reinvest_profit_pct")))
    realized_profit_from_baseline = _number(balance.get("realized_profit_from_baseline"))
    proposed_next_risk_budget_pct = min(
        current_risk_budget_pct + max_scale_step_pct,
        max_risk_per_trade_pct,
    )
    profit_lock_amount = _round(realized_profit_from_baseline * profit_lock_pct)
    reinvest_amount = _round(realized_profit_from_baseline * reinvest_profit_pct)

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": bool(ready),
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "compounding_scale_enabled": _bool(policy.get("compounding_enabled")),
        "scale_decision": scale_decision,
        "scale_direction": scale_direction,
        "current_risk_budget_pct": _round(current_risk_budget_pct),
        "proposed_next_risk_budget_pct": _round(proposed_next_risk_budget_pct),
        "max_scale_step_pct": _round(max_scale_step_pct),
        "profit_lock_amount": profit_lock_amount,
        "reinvest_amount": reinvest_amount,
        "protected_profit_amount": profit_lock_amount,
        "risk_policy_summary": _risk_policy_summary(policy),
        "proof_summary": _proof_summary(proof),
        "balance_summary": _balance_summary(balance),
        "blockers": list(_unique(blockers)),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": safe_manual_next_action,
        "audit_record": _audit_record(
            status=status,
            ready=ready,
            balance=balance,
            policy=policy,
            proof=proof,
            risk=risk,
            claims=claims,
            blockers=blockers,
            next_best_packet=next_best_packet,
            scale_decision=scale_decision,
            scale_direction=scale_direction,
            current_risk_budget_pct=current_risk_budget_pct,
            proposed_next_risk_budget_pct=proposed_next_risk_budget_pct,
            profit_lock_amount=profit_lock_amount,
            reinvest_amount=reinvest_amount,
            protected_profit_amount=profit_lock_amount,
        ),
        "safety": _safety_profile(),
    }

    result.update({field: False for field in HARD_FALSE_FIELDS})
    if status == GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED and _number(realized_profit_from_baseline) <= 0:
        result["proposed_next_risk_budget_pct"] = _round(current_risk_budget_pct)
    return result


def _risk_policy_summary(policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "compounding_enabled": _bool(policy.get("compounding_enabled")),
        "owner_review_required": _bool(policy.get("owner_review_required")),
        "scale_up_allowed": _bool(policy.get("scale_up_allowed")),
        "scale_down_on_drawdown": _bool(policy.get("scale_down_on_drawdown")),
        "stop_at_target": _bool(policy.get("stop_at_target")),
        "current_risk_budget_pct": _number(policy.get("current_risk_budget_pct")),
        "max_scale_step_pct": _number(policy.get("max_scale_step_pct")),
        "max_risk_per_trade_pct": _number(policy.get("max_risk_per_trade_pct")),
        "max_total_burst_risk_pct": _number(policy.get("max_total_burst_risk_pct")),
        "profit_lock_pct": _bounded_percent(_number(policy.get("profit_lock_pct"))),
        "reinvest_profit_pct": _bounded_percent(_number(policy.get("reinvest_profit_pct"))),
        "minimum_verified_profit_to_scale": _number(
            policy.get("minimum_verified_profit_to_scale")
        ),
        "consecutive_scale_ups_since_review": _integer(
            policy.get("consecutive_scale_ups_since_review")
        ),
        "max_consecutive_scale_ups_before_review": _integer(
            policy.get("max_consecutive_scale_ups_before_review")
        ),
        "withdrawal_allowed": _bool(policy.get("withdrawal_allowed")),
        "bank_routing_allowed": _bool(policy.get("bank_routing_allowed")),
        "money_movement_allowed": _bool(policy.get("money_movement_allowed")),
        "withdrawal_deferred": True,
        "bank_routing_deferred": True,
        "money_movement_deferred": not _bool(policy.get("money_movement_allowed")),
    }

def _proof_summary(proof: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "receipts_sanitized": _bool(proof.get("receipts_sanitized")),
        "realized_pnl_verified": _bool(proof.get("realized_pnl_verified")),
        "repeatability_score": _number(proof.get("repeatability_score")),
        "proof_ready_for_scaling": _bool(proof.get("proof_ready_for_scaling")),
        "fake_pnl_blocked": _bool(proof.get("fake_pnl_blocked")),
    }


def _balance_summary(balance: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": str(balance.get("status", "")),
        "ready": _bool(balance.get("ready")),
        "realized_profit_from_baseline": _number(
            balance.get("realized_profit_from_baseline")
        ),
        "equity_drift": _number(balance.get("equity_drift")),
        "target_return_reached": _bool(balance.get("target_return_reached")),
        "target_balance_reached": _bool(balance.get("target_balance_reached")),
        "withdrawal_deferred": _bool(balance.get("withdrawal_deferred")),
        "bank_routing_deferred": _bool(balance.get("bank_routing_deferred")),
        "money_moved": _bool(balance.get("money_moved")),
    }


def _audit_record(
    *,
    status: str,
    ready: bool,
    balance: Mapping[str, Any],
    policy: Mapping[str, Any],
    proof: Mapping[str, Any],
    risk: Mapping[str, Any],
    claims: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
    scale_decision: str,
    scale_direction: str,
    current_risk_budget_pct: float,
    proposed_next_risk_budget_pct: float,
    profit_lock_amount: float,
    reinvest_amount: float,
    protected_profit_amount: float,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": bool(ready),
        "owner_decision_required": True,
        "read_only": True,
        "metadata_only": True,
        "withdrawal_deferred": True,
        "bank_routing_deferred": True,
        "money_movement_blocked": not bool(policy.get("money_movement_allowed")),
        "claims_no_profit_guarantee": not (
            _bool(claims.get("guaranteed_profit_claimed"))
            or _bool(claims.get("fixed_return_promised"))
            or _bool(claims.get("daily_profit_guaranteed"))
            or _bool(claims.get("weekly_profit_guaranteed"))
            or _bool(claims.get("monthly_profit_guaranteed"))
            or _bool(claims.get("yearly_profit_guaranteed"))
        ),
        "scale_decision": scale_decision,
        "scale_direction": scale_direction,
        "current_risk_budget_pct": _round(current_risk_budget_pct),
        "proposed_next_risk_budget_pct": _round(proposed_next_risk_budget_pct),
        "profit_lock_amount": profit_lock_amount,
        "reinvest_amount": reinvest_amount,
        "protected_profit_amount": protected_profit_amount,
        "blockers": list(_unique(blockers)),
        "next_best_packet": next_best_packet,
        "risk_within_limits": all(
            risk.get(key) is False for key in ("kill_switch_active", "daily_loss_stop_active")
        )
        and _bool(risk.get("drawdown_within_limit")),
        "balance_money_moved": _bool(balance.get("money_moved")),
        "compliant_with_banking_freeze": not bool(policy.get("withdrawal_allowed"))
        and not bool(policy.get("bank_routing_allowed"))
        and not bool(policy.get("money_movement_allowed")),
        "receipt_proof_ready": _bool(proof.get("proof_ready_for_scaling")),
    }


def _safety_profile() -> dict[str, bool]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "withdrawal_deferred": True,
        "bank_routing_deferred": True,
        "no_broker_trade": True,
        "no_broker_api_called": True,
        "no_live_trading": True,
        "no_demo_trading": True,
        "no_credential_read": True,
        "no_money_movement": True,
        "no_banking": True,
        "no_withdrawal_build": True,
        "no_transfer_build": True,
        "no_router_change": True,
        "no_demo_broker_runtime": True,
        "no_live_broker_runtime": True,
        "no_scheduler": True,
        "no_daemon": True,
        "no_webhook": True,
        "no_dashboard_runtime": True,
        "no_profit_guarantee": True,
        "no_fixed_return_promise": True,
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _balance_blockers(balance: Mapping[str, Any]) -> tuple[str, ...]:
    if not balance:
        return ("balance_observer_result_missing",)
    missing = tuple(
        f"missing_balance_observer_{field}" for field in REQUIRED_BALANCE_FIELDS if field not in balance
    )
    if missing:
        return missing
    blockers: list[str] = []
    if not _bool(balance.get("ready")):
        blockers.append("balance_ready_false")
    if not _bool(balance.get("withdrawal_deferred")):
        blockers.append("withdrawal_deferred_not_true")
    if not _bool(balance.get("bank_routing_deferred")):
        blockers.append("bank_routing_deferred_not_true")
    if _bool(balance.get("money_moved")):
        blockers.append("money_moved_true")
    if not _is_number(balance.get("realized_profit_from_baseline")):
        blockers.append("realized_profit_from_baseline_not_number")
    if not _is_number(balance.get("equity_drift")):
        blockers.append("equity_drift_not_number")
    if not isinstance(balance.get("target_return_reached"), bool):
        blockers.append("target_return_reached_not_bool")
    if not isinstance(balance.get("target_balance_reached"), bool):
        blockers.append("target_balance_reached_not_bool")
    if not isinstance(balance.get("status"), str) or not str(balance.get("status")).strip():
        blockers.append("balance_status_missing")
    return tuple(_unique(blockers))


def _proof_blockers(proof: Mapping[str, Any]) -> tuple[str, ...]:
    if not proof:
        return ("proof_state_missing",)
    missing = tuple(
        f"missing_proof_state_{field}" for field in REQUIRED_PROOF_FIELDS if field not in proof
    )
    if missing:
        return missing
    blockers: list[str] = []
    for field in (
        "receipts_sanitized",
        "realized_pnl_verified",
        "proof_ready_for_scaling",
        "fake_pnl_blocked",
    ):
        if proof.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    if not _is_number(proof.get("repeatability_score")):
        blockers.append("repeatability_score_not_number")
    return tuple(_unique(blockers))


def _policy_blockers(policy: Mapping[str, Any]) -> tuple[str, ...]:
    if not policy:
        return ("compounding_scale_policy_missing",)
    missing = tuple(
        f"missing_compounding_policy_{field}" for field in REQUIRED_POLICY_FIELDS if field not in policy
    )
    if missing:
        return missing
    blockers: list[str] = []

    for field in (
        "compounding_enabled",
        "owner_review_required",
        "scale_up_allowed",
        "scale_down_on_drawdown",
        "stop_at_target",
    ):
        if not isinstance(policy.get(field), bool):
            blockers.append(f"{field}_not_bool")

    for field in (
        "current_risk_budget_pct",
        "max_scale_step_pct",
        "max_risk_per_trade_pct",
        "max_total_burst_risk_pct",
        "minimum_verified_profit_to_scale",
    ):
        if not _is_number(policy.get(field)):
            blockers.append(f"{field}_not_number")
        elif _number(policy.get(field)) < 0:
            blockers.append(f"{field}_negative")

    if _number(policy.get("max_scale_step_pct")) > 0.25:
        blockers.append("max_scale_step_pct_above_limit")
    if _number(policy.get("max_risk_per_trade_pct")) > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if _number(policy.get("max_total_burst_risk_pct")) > 0.03:
        blockers.append("max_total_burst_risk_pct_above_limit")

    for field in ("profit_lock_pct", "reinvest_profit_pct"):
        value = _number(policy.get(field))
        if not _is_number(policy.get(field)):
            blockers.append(f"{field}_not_number")
        elif not 0 <= value <= 1:
            blockers.append(f"{field}_out_of_range")

    for field in ("consecutive_scale_ups_since_review", "max_consecutive_scale_ups_before_review"):
        if not _is_int(policy.get(field)):
            blockers.append(f"{field}_not_int")
        elif _integer(policy.get(field)) < 0:
            blockers.append(f"{field}_negative")

    if policy.get("withdrawal_allowed") is not False:
        blockers.append("withdrawal_allowed_not_false")
    if policy.get("bank_routing_allowed") is not False:
        blockers.append("bank_routing_allowed_not_false")
    if policy.get("money_movement_allowed") is not False:
        blockers.append("money_movement_allowed_not_false")

    return tuple(_unique(blockers))


def _risk_blockers(
    risk: Mapping[str, Any],
) -> tuple[tuple[str, ...], bool]:
    if not risk:
        return (("risk_state_missing",), True)
    missing = tuple(
        f"missing_risk_state_{field}" for field in REQUIRED_RISK_FIELDS if field not in risk
    )
    if missing:
        return (missing, True)
    blockers: list[str] = []
    for field in ("kill_switch_active", "daily_loss_stop_active", "drawdown_within_limit"):
        if not isinstance(risk.get(field), bool):
            blockers.append(f"{field}_not_bool")
    if risk.get("kill_switch_active") is True:
        blockers.append("kill_switch_active_true")
    if risk.get("daily_loss_stop_active") is True:
        blockers.append("daily_loss_stop_active_true")
    if not _is_number(risk.get("current_drawdown_pct")):
        blockers.append("current_drawdown_pct_not_number")
    if not _is_number(risk.get("max_drawdown_pct")):
        blockers.append("max_drawdown_pct_not_number")
    if not _is_number(risk.get("current_daily_loss_pct")):
        blockers.append("current_daily_loss_pct_not_number")
    if not _is_number(risk.get("max_daily_loss_pct")):
        blockers.append("max_daily_loss_pct_not_number")

    # drawdown breach is handled as a directional scaling decision and is not a hard block.
    risk_state_ready = (
        risk.get("kill_switch_active") is False
        and risk.get("daily_loss_stop_active") is False
        and _bool(risk.get("drawdown_within_limit"))
    )
    return (tuple(_unique(blockers)), risk_state_ready)


def _claim_blockers(claims: Mapping[str, Any]) -> tuple[str, ...]:
    if not claims:
        return ("claims_missing",)
    missing = tuple(
        f"missing_claim_{field}" for field in REQUIRED_CLAIM_FIELDS if field not in claims
    )
    if missing:
        return missing
    for field in REQUIRED_CLAIM_FIELDS:
        if not isinstance(claims.get(field), bool):
            return tuple(_unique((f"{field}_not_bool",)))
    if any(
        _bool(claims.get(field))
        for field in REQUIRED_CLAIM_FIELDS
    ):
        return ("profit_claim_block_detected",)
    return ()


def _next_packet(status: str) -> str:
    if status == GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED:
        return "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
    if status == GOVERNED_COMPOUNDING_HOLD_REQUIRED:
        return "AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1"
    if status == GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED:
        return "AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1"
    if status == GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT:
        return "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1"
    if status in {
        GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED,
        GOVERNED_COMPOUNDING_STOP_REQUIRED,
    }:
        return "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"
    if status in {
        BLOCKED_BY_RISK_STATE,
        BLOCKED_BY_BALANCE_OBSERVER,
        BLOCKED_BY_RECEIPT_PROOF,
        BLOCKED_BY_POLICY,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_SENSITIVE_DATA,
        BLOCKED_BY_BANKING_FOCUS,
        INCOMPLETE_INPUTS,
    }:
        return "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"
    return "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1"


def _safe_manual_next_action(status: str) -> str:
    if status == GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED:
        return "Owner may review controlled metadata and route to active supervision."
    if status == GOVERNED_COMPOUNDING_SCALE_DOWN_REQUIRED:
        return "Scale down required by risk posture; route to risk-scale-down review."
    if status == GOVERNED_COMPOUNDING_TARGET_REACHED_PROTECT_PROFIT:
        return "Scale decision must pause for profit-protection and future withdrawal review."
    if status == GOVERNED_COMPOUNDING_HOLD_REQUIRED:
        return "Hold and keep proof capture active for repeatable, verified scaling evidence."
    if status == GOVERNED_COMPOUNDING_OWNER_REVIEW_REQUIRED:
        return "Owner review required before the next compounding scale action."
    if status == GOVERNED_COMPOUNDING_STOP_REQUIRED:
        return "Stop scaling and route to vacation owner-toggle operation state."
    if status == BLOCKED_BY_RISK_STATE:
        return "Resolve kill-switch or daily-loss-stop blockers, then rerun evaluator."
    if status == BLOCKED_BY_RECEIPT_PROOF:
        return "Repair proof/receipt readiness."
    if status == BLOCKED_BY_POLICY:
        return "Repair compounding policy fields and constraints."
    if status == BLOCKED_BY_BALANCE_OBSERVER:
        return "Repair balance observer payload."
    if status == BLOCKED_BY_PROFIT_CLAIM:
        return "Remove all profit guarantee and fixed-return claims."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive data from payload."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove active banking and money movement focus keys."
    return "Repair blocked inputs and rerun this metadata packet."


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []

    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{raw_key}"
            if _sensitive_key_blocked(key, child) and not _safe_sensitive_value(child):
                blockers.append(f"{child_path}:sensitive_key")
            blockers.extend(_sensitive_data_blockers(child, child_path))
        return tuple(_unique(blockers))

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))

    if (
        isinstance(value, str)
        and not _safe_sensitive_value(value)
        and _looks_secret_string(value)
    ):
        blockers.append(f"{path}:secret_like_value")
    return tuple(_unique(blockers))


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
            if any(part in key for part in BANKING_KEY_PARTS) and _is_active_bank_focus(child):
                blockers.append(f"{child_path}:banking_focus")
                continue
            blockers.extend(_banking_focus_blockers(child, child_path))
        return tuple(_unique(blockers))

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_banking_focus_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))

    return tuple(_unique(blockers))


def _sensitive_key_blocked(normalized_key: str, value: Any) -> bool:
    if _sensitive_key_is_safe_false_metadata(normalized_key, value):
        return False
    return any(part in normalized_key for part in SENSITIVE_KEY_PARTS)


def _sensitive_key_is_safe_false_metadata(normalized_key: str, value: Any) -> bool:
    if normalized_key in BANKING_ALLOWED_FALSE_FIELDS:
        return True if value is False else False
    if normalized_key.startswith("account_id") and value is False:
        return True
    return False


def _is_active_bank_focus(value: Any) -> bool:
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


def _looks_secret_string(value: str) -> bool:
    lowered = value.lower()
    if any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS):
        return True
    if len(value) >= 16 and _has_long_digit_run(value, minimum=12):
        return True
    return False


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
    # Numeric strings are explicitly allowed as quantitative metrics and are not treated as sensitive.
    if isinstance(value, str):
        try:
            float(value)
        except ValueError:
            return False
        return True
    return False


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


def _integer(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


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
