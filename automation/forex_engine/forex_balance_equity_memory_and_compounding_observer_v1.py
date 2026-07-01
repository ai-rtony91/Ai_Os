"""Observe Forex balance/equity movement and governed compounding readiness."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"
MODE = "READ_ONLY_METADATA_ONLY_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER"

BALANCE_EQUITY_MEMORY_READY = "BALANCE_EQUITY_MEMORY_READY"
PROFIT_STACKING_OBSERVATION_READY = "PROFIT_STACKING_OBSERVATION_READY"
GOVERNED_COMPOUNDING_ELIGIBLE = "GOVERNED_COMPOUNDING_ELIGIBLE"
GOVERNED_COMPOUNDING_HOLD = "GOVERNED_COMPOUNDING_HOLD"
TARGET_REACHED_PROTECT_PROFIT = "TARGET_REACHED_PROTECT_PROFIT"
SCALE_DOWN_ON_DRAWDOWN = "SCALE_DOWN_ON_DRAWDOWN"
BLOCKED_BY_RECEIPT_PROOF = "BLOCKED_BY_RECEIPT_PROOF"
BLOCKED_BY_BALANCE_METADATA = "BLOCKED_BY_BALANCE_METADATA"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1"

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
    "live_profit_guaranteed",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

BALANCE_FIELDS = (
    "starting_balance",
    "current_balance",
    "current_equity",
    "realized_net_pnl",
    "unrealized_pnl",
    "trade_open_balance",
    "trade_close_balance",
    "day_start_balance",
    "day_current_balance",
    "week_start_balance",
    "week_current_balance",
    "month_start_balance",
    "month_current_balance",
    "vacation_mode_start_balance",
    "vacation_mode_current_balance",
)

BALANCE_REQUIRED_FIELDS = (
    *BALANCE_FIELDS,
    "snapshot_scope",
    "snapshot_event_id",
    "account_id_absent",
    "credentials_absent",
    "broker_values_absent",
)

RECEIPT_REQUIRED_FIELDS = (
    "receipts_required",
    "receipts_sanitized",
    "realized_pnl_verified",
    "fake_pnl_blocked",
    "balance_snapshot_source",
    "proof_ready_for_learning",
)

POLICY_REQUIRED_FIELDS = (
    "compounding_enabled",
    "compound_mode",
    "target_return_pct",
    "target_balance",
    "profit_lock_pct",
    "reinvest_profit_pct",
    "max_scale_step_pct",
    "stop_compounding_at_target",
    "scale_down_on_drawdown",
    "owner_review_required",
    "withdrawal_allowed",
    "bank_routing_allowed",
)

RISK_REQUIRED_FIELDS = (
    "kill_switch_active",
    "daily_loss_stop_active",
    "drawdown_within_limit",
    "max_drawdown_pct",
    "current_drawdown_pct",
    "max_daily_loss_pct",
    "current_daily_loss_pct",
)

CLAIM_FIELDS = (
    "guaranteed_profit_claimed",
    "fixed_return_promised",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
)

VALID_SNAPSHOT_SCOPES = frozenset({"TRADE", "DAY", "WEEK", "MONTH", "VACATION_MODE", "RUNTIME"})
VALID_COMPOUND_MODES = frozenset(
    {
        "HOLD",
        "COMPOUND_TO_PERCENT_TARGET",
        "COMPOUND_TO_BALANCE_TARGET",
        "COMPOUND_TO_PROFIT_BUCKET_TARGET",
    }
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
    "password",
    "master_password",
    "vault_password",
    "account_number",
    "routing_number",
    "card_number",
    "debit_card_number",
    "cvv",
    "account_id",
    "oanda_account_id",
    "bearer",
    "broker_token",
    "access_token",
    "private_key",
)

SAFE_SENSITIVE_TRUE_FIELDS = frozenset(
    {
        "account_id_absent",
        "credentials_absent",
        "broker_values_absent",
    }
)

SAFE_SENSITIVE_FALSE_FIELDS = frozenset(
    {
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
    }
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer",
    "api key",
    "token value",
    "broker token",
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
    "debit",
    "card",
    "rail",
    "ach",
    "wire",
    "sweep",
    "bucket_purge",
    "money_movement",
    "deposit",
)

BANKING_ALLOWED_FALSE_FIELDS = frozenset(
    {
        "money_moved",
        "money_movement_allowed",
        "bank_access_used",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
        "bank_routing_built",
        "withdrawal_allowed",
        "bank_routing_allowed",
        "withdrawal_allowed_by_this_module",
    }
)

APPROVED_NUMERIC_FIELDS = frozenset(
    {
        *BALANCE_FIELDS,
        "target_return_pct",
        "target_balance",
        "profit_lock_pct",
        "reinvest_profit_pct",
        "max_scale_step_pct",
        "max_drawdown_pct",
        "current_drawdown_pct",
        "max_daily_loss_pct",
        "current_daily_loss_pct",
    }
)


def evaluate_forex_balance_equity_memory_and_compounding_observer_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate balance/equity memory and compounding readiness without side effects."""

    source = _mapping(payload)
    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_SENSITIVE_DATA,
            ready=False,
            blockers=sensitive_blockers,
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_BANKING_FOCUS,
            ready=False,
            blockers=banking_blockers,
        )

    if not source:
        return _build_result(
            source=source,
            status=INCOMPLETE_INPUTS,
            ready=False,
            blockers=("payload_missing",),
        )

    balance = _mapping(source.get("balance_memory"))
    proof = _mapping(source.get("receipt_proof"))
    policy = _mapping(source.get("compounding_policy"))
    risk = _mapping(source.get("risk_state"))
    claims = _mapping(source.get("claims"))

    missing = _missing_inputs(balance, proof, policy, risk, claims)
    if missing:
        return _build_result(
            source=source,
            status=INCOMPLETE_INPUTS,
            ready=False,
            blockers=missing,
        )

    claim_blockers = tuple(f"{field}_true" for field in CLAIM_FIELDS if claims.get(field) is True)
    if claim_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_PROFIT_CLAIM,
            ready=False,
            blockers=claim_blockers,
        )

    balance_blockers = _balance_metadata_blockers(balance)
    if balance_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_BALANCE_METADATA,
            ready=False,
            blockers=balance_blockers,
        )

    proof_blockers = _receipt_proof_blockers(proof)
    if proof_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_RECEIPT_PROOF,
            ready=False,
            blockers=proof_blockers,
        )

    policy_blockers = _policy_blockers(policy)
    if policy_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_RISK_GATES,
            ready=False,
            blockers=policy_blockers,
        )

    metrics = _metrics(balance, policy)
    risk_blockers = _risk_blockers(risk)
    drawdown_breached = bool(risk_blockers)

    if metrics["target_return_reached"] or metrics["target_balance_reached"]:
        status = TARGET_REACHED_PROTECT_PROFIT
    elif drawdown_breached and _bool(policy.get("scale_down_on_drawdown")):
        status = SCALE_DOWN_ON_DRAWDOWN
    elif drawdown_breached or _bool(risk.get("kill_switch_active")) or _bool(risk.get("daily_loss_stop_active")):
        status = GOVERNED_COMPOUNDING_HOLD
    elif not _bool(policy.get("compounding_enabled")):
        status = PROFIT_STACKING_OBSERVATION_READY
    elif metrics["realized_profit_from_baseline"] > 0:
        status = GOVERNED_COMPOUNDING_ELIGIBLE
    else:
        status = GOVERNED_COMPOUNDING_HOLD

    blockers = risk_blockers if status == GOVERNED_COMPOUNDING_HOLD and risk_blockers else ()
    return _build_result(
        source=source,
        status=status,
        ready=True,
        blockers=blockers,
    )


def _build_result(
    *,
    source: Mapping[str, Any],
    status: str,
    ready: bool,
    blockers: Sequence[str],
) -> dict[str, Any]:
    balance = _mapping(source.get("balance_memory"))
    proof = _mapping(source.get("receipt_proof"))
    policy = _mapping(source.get("compounding_policy"))
    risk = _mapping(source.get("risk_state"))
    metrics = _metrics(balance, policy)
    blocker_list = _unique(blockers)
    profit_lock = _profit_lock_amount(metrics, policy)
    reinvest = _reinvest_amount(metrics, policy)
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": bool(ready),
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "balance_memory_enabled": bool(ready),
        "profit_stacking_enabled": bool(ready),
        "compounding_observer_enabled": bool(ready),
        "withdrawal_deferred": True,
        "bank_routing_deferred": True,
        "trade_delta": metrics["trade_delta"],
        "day_delta": metrics["day_delta"],
        "week_delta": metrics["week_delta"],
        "month_delta": metrics["month_delta"],
        "vacation_mode_delta": metrics["vacation_mode_delta"],
        "realized_profit_from_baseline": metrics["realized_profit_from_baseline"],
        "equity_drift": metrics["equity_drift"],
        "target_return_reached": metrics["target_return_reached"],
        "target_balance_reached": metrics["target_balance_reached"],
        "recommended_compounding_action": _recommended_action(status),
        "recommended_profit_lock_amount": profit_lock,
        "recommended_reinvest_amount": reinvest,
        "balance_memory_summary": _balance_summary(balance, metrics),
        "learning_signal_summary": _learning_summary(status, balance, proof, risk, metrics),
        "compounding_policy_summary": _policy_summary(policy),
        "blockers": blocker_list,
        "next_best_packet": _next_packet(status),
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "status": status,
            "ready": bool(ready),
            "blockers": blocker_list,
            "next_best_packet": _next_packet(status),
            "read_only": True,
            "metadata_only": True,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
        },
        "safety": _safety_summary(),
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _missing_inputs(
    balance: Mapping[str, Any],
    proof: Mapping[str, Any],
    policy: Mapping[str, Any],
    risk: Mapping[str, Any],
    claims: Mapping[str, Any],
) -> tuple[str, ...]:
    missing: list[str] = []
    if not balance:
        missing.append("balance_memory_missing")
    if not proof:
        missing.append("receipt_proof_missing")
    if not policy:
        missing.append("compounding_policy_missing")
    if not risk:
        missing.append("risk_state_missing")
    if not claims:
        missing.append("claims_missing")
    missing.extend(f"missing_balance_memory_{field}" for field in BALANCE_REQUIRED_FIELDS if field not in balance)
    missing.extend(f"missing_receipt_proof_{field}" for field in RECEIPT_REQUIRED_FIELDS if field not in proof)
    missing.extend(f"missing_compounding_policy_{field}" for field in POLICY_REQUIRED_FIELDS if field not in policy)
    missing.extend(f"missing_risk_state_{field}" for field in RISK_REQUIRED_FIELDS if field not in risk)
    missing.extend(f"missing_claims_{field}" for field in CLAIM_FIELDS if field not in claims)
    return tuple(_unique(missing))


def _balance_metadata_blockers(balance: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in BALANCE_FIELDS:
        if not _is_number(balance.get(field)):
            blockers.append(f"{field}_not_number")
    for field in ("starting_balance", "current_balance", "current_equity"):
        if _number(balance.get(field)) <= 0:
            blockers.append(f"{field}_not_positive")
    if str(balance.get("snapshot_scope", "")).upper() not in VALID_SNAPSHOT_SCOPES:
        blockers.append("snapshot_scope_invalid")
    if not _present(balance.get("snapshot_event_id")):
        blockers.append("snapshot_event_id_missing")
    for field in ("account_id_absent", "credentials_absent", "broker_values_absent"):
        if balance.get(field) is not True:
            blockers.append(f"{field}_not_true")
    return tuple(_unique(blockers))


def _receipt_proof_blockers(proof: Mapping[str, Any]) -> tuple[str, ...]:
    checks = {
        "receipts_required": proof.get("receipts_required") is True,
        "receipts_sanitized": proof.get("receipts_sanitized") is True,
        "realized_pnl_verified": proof.get("realized_pnl_verified") is True,
        "fake_pnl_blocked": proof.get("fake_pnl_blocked") is True,
        "balance_snapshot_source_present": _present(proof.get("balance_snapshot_source")),
        "proof_ready_for_learning": proof.get("proof_ready_for_learning") is True,
    }
    return tuple(key for key, passed in checks.items() if not passed)


def _policy_blockers(policy: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    mode = str(policy.get("compound_mode", "")).upper()
    if mode not in VALID_COMPOUND_MODES:
        blockers.append("compound_mode_invalid")
    for field in ("target_return_pct", "target_balance", "profit_lock_pct", "reinvest_profit_pct", "max_scale_step_pct"):
        if not _is_number(policy.get(field)):
            blockers.append(f"{field}_not_number")
    if not 0 <= _number(policy.get("profit_lock_pct")) <= 1:
        blockers.append("profit_lock_pct_outside_range")
    if not 0 <= _number(policy.get("reinvest_profit_pct")) <= 1:
        blockers.append("reinvest_profit_pct_outside_range")
    if _number(policy.get("max_scale_step_pct")) > 0.25:
        blockers.append("max_scale_step_pct_above_limit")
    for field in ("stop_compounding_at_target", "scale_down_on_drawdown", "owner_review_required"):
        if policy.get(field) is not True:
            blockers.append(f"{field}_not_true")
    for field in ("withdrawal_allowed", "bank_routing_allowed"):
        if policy.get(field) is not False:
            blockers.append(f"{field}_not_false")
    return tuple(_unique(blockers))


def _risk_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if risk.get("kill_switch_active") is not False:
        blockers.append("kill_switch_active_not_false")
    if risk.get("daily_loss_stop_active") is not False:
        blockers.append("daily_loss_stop_active_not_false")
    if risk.get("drawdown_within_limit") is not True:
        blockers.append("drawdown_within_limit_not_true")
    for field in ("max_drawdown_pct", "current_drawdown_pct", "max_daily_loss_pct", "current_daily_loss_pct"):
        if not _is_number(risk.get(field)):
            blockers.append(f"{field}_not_number")
    if _number(risk.get("current_drawdown_pct")) > _number(risk.get("max_drawdown_pct")):
        blockers.append("current_drawdown_pct_above_limit")
    if _number(risk.get("current_daily_loss_pct")) > _number(risk.get("max_daily_loss_pct")):
        blockers.append("current_daily_loss_pct_above_limit")
    return tuple(_unique(blockers))


def _metrics(balance: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    starting = _number(balance.get("starting_balance"))
    current_balance = _number(balance.get("current_balance"))
    current_equity = _number(balance.get("current_equity"))
    realized_profit = _round(current_balance - starting)
    target_return_pct = _number(policy.get("target_return_pct"))
    target_balance = _number(policy.get("target_balance"))
    actual_return_pct = _round(realized_profit / starting) if starting > 0 else 0.0
    return {
        "trade_delta": _round(_number(balance.get("trade_close_balance")) - _number(balance.get("trade_open_balance"))),
        "day_delta": _round(_number(balance.get("day_current_balance")) - _number(balance.get("day_start_balance"))),
        "week_delta": _round(_number(balance.get("week_current_balance")) - _number(balance.get("week_start_balance"))),
        "month_delta": _round(_number(balance.get("month_current_balance")) - _number(balance.get("month_start_balance"))),
        "vacation_mode_delta": _round(
            _number(balance.get("vacation_mode_current_balance"))
            - _number(balance.get("vacation_mode_start_balance"))
        ),
        "realized_profit_from_baseline": _round(realized_profit),
        "equity_drift": _round(current_equity - current_balance),
        "actual_return_pct": actual_return_pct,
        "target_return_reached": target_return_pct > 0 and actual_return_pct >= target_return_pct,
        "target_balance_reached": target_balance > 0 and current_balance >= target_balance,
    }


def _balance_summary(balance: Mapping[str, Any], metrics: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "snapshot_scope": str(balance.get("snapshot_scope", "")).upper(),
        "snapshot_event_id_present": _present(balance.get("snapshot_event_id")),
        "current_balance": _number(balance.get("current_balance")),
        "current_equity": _number(balance.get("current_equity")),
        "realized_net_pnl": _number(balance.get("realized_net_pnl")),
        "unrealized_pnl": _number(balance.get("unrealized_pnl")),
        "realized_profit_from_baseline": metrics["realized_profit_from_baseline"],
        "equity_drift": metrics["equity_drift"],
        "account_id_absent": _bool(balance.get("account_id_absent")),
        "credentials_absent": _bool(balance.get("credentials_absent")),
        "broker_values_absent": _bool(balance.get("broker_values_absent")),
    }


def _learning_summary(
    status: str,
    balance: Mapping[str, Any],
    proof: Mapping[str, Any],
    risk: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "learning_means_metadata_signals_not_strategy_mutation": True,
        "event_based_or_controlled_cadence_recommended": True,
        "proof_ready_for_learning": _bool(proof.get("proof_ready_for_learning")),
        "realized_pnl_verified": _bool(proof.get("realized_pnl_verified")),
        "drawdown_within_limit": _bool(risk.get("drawdown_within_limit")),
        "snapshot_scope": str(balance.get("snapshot_scope", "")).upper(),
        "profit_stacking_positive": metrics["realized_profit_from_baseline"] > 0,
        "status": status,
    }


def _policy_summary(policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "compounding_enabled": _bool(policy.get("compounding_enabled")),
        "compound_mode": str(policy.get("compound_mode", "")).upper(),
        "target_return_pct": _number(policy.get("target_return_pct")),
        "target_balance": _number(policy.get("target_balance")),
        "profit_lock_pct": _number(policy.get("profit_lock_pct")),
        "reinvest_profit_pct": _number(policy.get("reinvest_profit_pct")),
        "max_scale_step_pct": _number(policy.get("max_scale_step_pct")),
        "owner_review_required": _bool(policy.get("owner_review_required")),
        "withdrawal_allowed": False,
        "bank_routing_allowed": False,
    }


def _profit_lock_amount(metrics: Mapping[str, Any], policy: Mapping[str, Any]) -> float:
    profit = max(_number(metrics.get("realized_profit_from_baseline")), 0.0)
    return _round(profit * _number(policy.get("profit_lock_pct")))


def _reinvest_amount(metrics: Mapping[str, Any], policy: Mapping[str, Any]) -> float:
    profit = max(_number(metrics.get("realized_profit_from_baseline")), 0.0)
    return _round(profit * _number(policy.get("reinvest_profit_pct")))


def _recommended_action(status: str) -> str:
    if status == GOVERNED_COMPOUNDING_ELIGIBLE:
        return "OWNER_REVIEW_GOVERNED_COMPOUNDING_SCALE_STEP"
    if status == TARGET_REACHED_PROTECT_PROFIT:
        return "PROTECT_PROFIT_AND_DEFER_WITHDRAWAL_REVIEW"
    if status == SCALE_DOWN_ON_DRAWDOWN:
        return "ROUTE_TO_RISK_SCALE_DOWN_REVIEW"
    if status == PROFIT_STACKING_OBSERVATION_READY:
        return "CONTINUE_BALANCE_EQUITY_OBSERVATION"
    if status == GOVERNED_COMPOUNDING_HOLD:
        return "HOLD_COMPOUNDING_AND_UPDATE_REPEATABILITY_EVIDENCE"
    return "REPAIR_BLOCKERS_BEFORE_BALANCE_MEMORY_USE"


def _next_packet(status: str) -> str:
    routes = {
        GOVERNED_COMPOUNDING_ELIGIBLE: "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
        PROFIT_STACKING_OBSERVATION_READY: NEXT_BEST_PACKET,
        GOVERNED_COMPOUNDING_HOLD: "AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1",
        TARGET_REACHED_PROTECT_PROFIT: "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
        SCALE_DOWN_ON_DRAWDOWN: "AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1",
    }
    return routes.get(status, NEXT_BEST_PACKET)


def _safe_manual_next_action(status: str) -> str:
    if status == GOVERNED_COMPOUNDING_ELIGIBLE:
        return "Owner may review governed compounding capital scaling; no scaling occurs here."
    if status == PROFIT_STACKING_OBSERVATION_READY:
        return "Continue event-based balance/equity observation and proof capture."
    if status == GOVERNED_COMPOUNDING_HOLD:
        return "Hold compounding and route evidence to repeatability review."
    if status == TARGET_REACHED_PROTECT_PROFIT:
        return "Protect profit metadata and defer withdrawal review to a future owner-approved packet."
    if status == SCALE_DOWN_ON_DRAWDOWN:
        return "Route to risk scale-down review before any next exposure decision."
    if status == BLOCKED_BY_RECEIPT_PROOF:
        return "Provide sanitized receipts and verified realized PnL evidence."
    if status == BLOCKED_BY_BALANCE_METADATA:
        return "Repair balance/equity snapshot metadata."
    if status == BLOCKED_BY_RISK_GATES:
        return "Repair risk or compounding policy gates."
    if status == BLOCKED_BY_PROFIT_CLAIM:
        return "Remove guaranteed or fixed-return profit claims."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or secret-looking values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, bank-routing, or money-movement focus."
    return "Provide complete balance memory, proof, policy, risk, and claims metadata."


def _safety_summary() -> dict[str, Any]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "withdrawal_deferred": True,
        "bank_routing_deferred": True,
        "no_broker_access": True,
        "no_credential_access": True,
        "no_money_movement": True,
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in SAFE_SENSITIVE_TRUE_FIELDS and child is True:
                continue
            if normalized in SAFE_SENSITIVE_FALSE_FIELDS and child is False:
                continue
            if _sensitive_key_blocked(normalized):
                blockers.append(f"{child_path}:sensitive_key")
                continue
            blockers.extend(_sensitive_data_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    field_name = path.rsplit(".", 1)[-1].lower().replace("-", "_")
    if isinstance(value, str) and _has_secret_value(value):
        blockers.append(f"{path}:secret_like_value")
    elif isinstance(value, int) and not isinstance(value, bool) and field_name not in APPROVED_NUMERIC_FIELDS:
        if _has_long_digit_run(str(value)):
            blockers.append(f"{path}:long_digit_run")
    return tuple(_unique(blockers))


def _banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in BANKING_ALLOWED_FALSE_FIELDS and child is False:
                continue
            if any(part in normalized for part in BANKING_KEY_PARTS):
                blockers.append(f"{child_path}:banking_focus")
                continue
            blockers.extend(_banking_focus_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_banking_focus_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    return tuple(_unique(blockers))


def _sensitive_key_blocked(normalized_key: str) -> bool:
    return any(part in normalized_key for part in SENSITIVE_KEY_PARTS)


def _has_secret_value(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS) or _has_long_digit_run(lowered)


def _has_long_digit_run(text: str, minimum: int = 8) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number(value: Any) -> float:
    return float(value) if _is_number(value) else 0.0


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _round(value: float) -> float:
    return round(float(value), 6)


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result
