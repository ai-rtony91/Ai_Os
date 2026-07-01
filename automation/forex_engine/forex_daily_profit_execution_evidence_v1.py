"""Metadata-only Forex daily profit execution evidence evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


SCHEMA = "AIOS_FOREX_DAILY_PROFIT_EXECUTION_EVIDENCE_CAMPAIGN_V1"
MODE = "READ_ONLY_METADATA_ONLY_DAILY_PROFIT_EXECUTION_EVIDENCE"

DAILY_PROFIT_EXECUTION_EVIDENCE_READY = (
    "DAILY_PROFIT_EXECUTION_EVIDENCE_READY"
)
READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT = (
    "READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT"
)
READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW = (
    "READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW"
)
CONTINUE_EVIDENCE_CAPTURE = "CONTINUE_EVIDENCE_CAPTURE"
BLOCKED_BY_REVIEW_REPAIR_REQUIRED = "BLOCKED_BY_REVIEW_REPAIR_REQUIRED"
BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE = "BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE"
BLOCKED_BY_RISK_LIMITS = "BLOCKED_BY_RISK_LIMITS"
BLOCKED_BY_EXECUTION_READINESS = "BLOCKED_BY_EXECUTION_READINESS"
BLOCKED_BY_POST_TRADE_REVIEW = "BLOCKED_BY_POST_TRADE_REVIEW"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

BELOW_PROFIT_THRESHOLD = "BELOW_PROFIT_THRESHOLD"
DAILY_PROFIT_EVIDENCE_PRESENT = "DAILY_PROFIT_EVIDENCE_PRESENT"
TWENTY_PERCENT_REVIEW_BAND = "TWENTY_PERCENT_REVIEW_BAND"
FIFTY_PERCENT_REVIEW_BAND = "FIFTY_PERCENT_REVIEW_BAND"
ONE_HUNDRED_PERCENT_REVIEW_BAND = "ONE_HUNDRED_PERCENT_REVIEW_BAND"
ONE_HUNDRED_TWENTY_PERCENT_STRESS_REVIEW_BAND = (
    "ONE_HUNDRED_TWENTY_PERCENT_STRESS_REVIEW_BAND"
)

NEXT_PACKET_CURRENT = SCHEMA
NEXT_PACKET_PROTECTED_DEMO = (
    "AIOS_FOREX_PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_V1"
)
NEXT_PACKET_LIVE_MICRO_REVIEW = "AIOS_FOREX_LIVE_MICRO_EXCEPTION_REVIEW_V1"
BANKING_DEFERRED_STATEMENT = (
    "Banking deferred until realized profit exists and owner explicitly "
    "approves transfer work."
)

HARD_FALSE_FIELDS = (
    "live_trade_executed",
    "demo_trade_executed",
    "money_moved",
    "bank_access_used",
    "broker_api_called",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
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

SAFE_SENSITIVE_NAMED_METADATA_KEYS = frozenset(
    {
        "broker_api_called",
        "credential_read",
        "credential_stored",
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
        "live_trade_executed",
        "demo_trade_executed",
        "account_id_provided",
        "no_stored_account_id",
        "no_stored_api_key",
        "no_master_password",
        "no_vault_password",
        "no_raw_token",
    }
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
)

PROFIT_REQUIRED_FIELDS = (
    "evidence_sample_count",
    "min_evidence_sample_count",
    "expectancy_positive",
    "profit_factor",
    "min_profit_factor",
    "max_drawdown_pct",
    "max_allowed_drawdown_pct",
    "walk_forward_gate_cleared",
    "out_of_sample_passed",
    "spread_slippage_model_present",
    "daily_profit_target_defined",
    "guaranteed_profit_claimed",
    "fixed_return_target_promised",
)

EXECUTION_REQUIRED_FIELDS = (
    "protected_runtime_gate_ready",
    "credential_session_bridge_ready",
    "post_trade_review_ready",
    "twenty_two_hour_six_day_ready",
    "broker_mode_declared",
    "one_order_gate_ready",
    "owner_approval_required",
    "broker_api_called",
    "credential_read",
    "live_trade_executed",
    "demo_trade_executed",
)

RISK_REQUIRED_FIELDS = (
    "max_risk_per_trade_pct",
    "max_daily_loss_pct",
    "stop_loss_required",
    "take_profit_required",
    "kill_switch_ready",
    "kill_switch_active",
    "daily_loss_stop_ready",
    "daily_loss_stop_active",
    "one_order_only",
    "next_order_blocked_until_review",
)

DAILY_CYCLE_REQUIRED_FIELDS = (
    "pre_trade_check_ready",
    "execution_window_defined",
    "post_trade_review_required",
    "daily_pnl_record_required",
    "no_second_trade_without_review",
    "owner_can_stop",
)

ALLOWED_BROKER_MODE_LABELS = frozenset(
    {"PRACTICE", "DEMO", "OANDA_DEMO", "PROTECTED_DEMO", "LIVE_MICRO_REVIEW_ONLY"}
)


def evaluate_forex_daily_profit_execution_evidence_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate daily profit-readiness evidence without runtime side effects."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = _sensitive_data_blockers(source)
    banking_focus_blockers = _banking_focus_blockers(source)
    missing_inputs = _missing_inputs(source)

    if sensitive_data_blockers:
        profit_evidence_summary = _redacted_profit_evidence_summary()
        execution_readiness_summary = _redacted_execution_readiness_summary()
        risk_control_summary = _redacted_risk_control_summary()
        daily_cycle_summary = _redacted_daily_cycle_summary()
        weekly_monthly_yearly_summary = _cadence_summary()
        banking_freeze_summary = _banking_freeze_summary(
            banking_focus_blockers=(),
            status=BLOCKED_BY_SENSITIVE_DATA,
        )
        return_discovery_band = BELOW_PROFIT_THRESHOLD
        blockers = list(sensitive_data_blockers)
        daily_profit_status = BLOCKED_BY_SENSITIVE_DATA
    elif banking_focus_blockers:
        profit_evidence_summary = _redacted_profit_evidence_summary()
        execution_readiness_summary = _redacted_execution_readiness_summary()
        risk_control_summary = _redacted_risk_control_summary()
        daily_cycle_summary = _redacted_daily_cycle_summary()
        weekly_monthly_yearly_summary = _cadence_summary()
        banking_freeze_summary = _banking_freeze_summary(
            banking_focus_blockers=banking_focus_blockers,
            status=BLOCKED_BY_BANKING_FOCUS,
        )
        return_discovery_band = BELOW_PROFIT_THRESHOLD
        blockers = list(banking_focus_blockers)
        daily_profit_status = BLOCKED_BY_BANKING_FOCUS
    else:
        profit_evidence_summary = _profit_evidence_summary(source)
        execution_readiness_summary = _execution_readiness_summary(source)
        risk_control_summary = _risk_control_summary(source)
        daily_cycle_summary = _daily_cycle_summary(source)
        weekly_monthly_yearly_summary = _cadence_summary()
        banking_freeze_summary = _banking_freeze_summary(
            banking_focus_blockers=(),
            status="BANKING_FOCUS_DEFERRED",
        )
        return_discovery_band = _return_discovery_band(
            source=source,
            profit_evidence_summary=profit_evidence_summary,
        )
        daily_profit_status, blockers = _daily_profit_status(
            source=source,
            missing_inputs=missing_inputs,
            profit_evidence_summary=profit_evidence_summary,
            execution_readiness_summary=execution_readiness_summary,
            risk_control_summary=risk_control_summary,
            daily_cycle_summary=daily_cycle_summary,
            return_discovery_band=return_discovery_band,
        )

    daily_profit_ready = daily_profit_status in {
        DAILY_PROFIT_EXECUTION_EVIDENCE_READY,
        READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT,
        READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW,
    }
    next_best_packet = _next_best_packet(daily_profit_status)
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "daily_profit_status": daily_profit_status,
        "daily_profit_ready": daily_profit_ready,
        "return_discovery_band": return_discovery_band,
        "owner_decision_required": True,
        "read_only": True,
        "metadata_only": True,
        "profit_evidence_summary": profit_evidence_summary,
        "execution_readiness_summary": execution_readiness_summary,
        "risk_control_summary": risk_control_summary,
        "daily_cycle_summary": daily_cycle_summary,
        "weekly_monthly_yearly_summary": weekly_monthly_yearly_summary,
        "banking_freeze_summary": banking_freeze_summary,
        "owner_action_queue": _owner_action_queue(
            daily_profit_status=daily_profit_status,
            blockers=blockers,
            next_best_packet=next_best_packet,
        ),
        "blockers": list(blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(daily_profit_status),
        "audit_record": _audit_record(
            daily_profit_status=daily_profit_status,
            daily_profit_ready=daily_profit_ready,
            blockers=blockers,
            missing_inputs=missing_inputs,
            return_discovery_band=return_discovery_band,
            next_best_packet=next_best_packet,
            sensitive_data_detected=bool(sensitive_data_blockers),
            banking_focus_detected=bool(banking_focus_blockers),
        ),
        "safety": _safety(),
    }
    result.update({field: False for field in HARD_FALSE_FIELDS})
    return result


def _daily_profit_status(
    *,
    source: Mapping[str, Any],
    missing_inputs: tuple[str, ...],
    profit_evidence_summary: dict[str, Any],
    execution_readiness_summary: dict[str, Any],
    risk_control_summary: dict[str, Any],
    daily_cycle_summary: dict[str, Any],
    return_discovery_band: str,
) -> tuple[str, list[str]]:
    blockers: list[str] = []
    if not source or missing_inputs:
        blockers.extend(f"missing_{field}" for field in missing_inputs)
        return INCOMPLETE_INPUTS, _unique(blockers)
    if profit_evidence_summary["guaranteed_profit_claimed"] is True:
        return BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE, [
            "guaranteed_profit_claim_detected"
        ]
    if profit_evidence_summary["fixed_return_target_promised"] is True:
        return BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE, [
            "fixed_return_promise_detected"
        ]
    if risk_control_summary["drawdown_gate_cleared"] is False:
        return BLOCKED_BY_RISK_LIMITS, ["drawdown_limit_exceeded"]
    if profit_evidence_summary["profit_edge_evidence_present"] is False:
        blockers.extend(profit_evidence_summary["profit_evidence_blockers"])
        return BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE, _unique(blockers)
    if risk_control_summary["risk_limits_cleared"] is False:
        blockers.extend(risk_control_summary["risk_blockers"])
        return BLOCKED_BY_RISK_LIMITS, _unique(blockers)
    if execution_readiness_summary["post_trade_review_ready"] is False:
        return BLOCKED_BY_POST_TRADE_REVIEW, ["post_trade_review_not_ready"]
    if daily_cycle_summary["post_trade_review_required"] is False:
        return BLOCKED_BY_POST_TRADE_REVIEW, [
            "daily_cycle_post_trade_review_not_required"
        ]
    if execution_readiness_summary["execution_readiness_cleared"] is False:
        blockers.extend(execution_readiness_summary["execution_blockers"])
        return BLOCKED_BY_EXECUTION_READINESS, _unique(blockers)
    if daily_cycle_summary["daily_cycle_ready"] is False:
        blockers.extend(daily_cycle_summary["daily_cycle_blockers"])
        return BLOCKED_BY_EXECUTION_READINESS, _unique(blockers)
    if _stress_review_required(return_discovery_band) and not (
        _bool(source.get("stress_review_ready"))
        and _bool(source.get("drawdown_review_ready"))
    ):
        return BLOCKED_BY_RISK_LIMITS, [
            "stress_review_required_for_high_return_band",
            "drawdown_review_required_for_high_return_band",
        ]
    if _bool(source.get("live_micro_exception_review_requested")):
        return READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW, []
    if _bool(source.get("protected_demo_profit_attempt_requested")):
        return READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT, []
    return DAILY_PROFIT_EXECUTION_EVIDENCE_READY, []


def _profit_evidence_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    evidence_sample_count = _decimal(source.get("evidence_sample_count"))
    min_evidence_sample_count = _decimal(source.get("min_evidence_sample_count"))
    profit_factor = _decimal(source.get("profit_factor"))
    min_profit_factor = _decimal(source.get("min_profit_factor"))
    max_drawdown_pct = _decimal(source.get("max_drawdown_pct"))
    max_allowed_drawdown_pct = _decimal(source.get("max_allowed_drawdown_pct"))

    sample_gate_cleared = (
        evidence_sample_count is not None
        and min_evidence_sample_count is not None
        and evidence_sample_count >= min_evidence_sample_count
    )
    profit_factor_gate_cleared = (
        profit_factor is not None
        and min_profit_factor is not None
        and profit_factor >= min_profit_factor
    )
    drawdown_gate_cleared = (
        max_drawdown_pct is not None
        and max_allowed_drawdown_pct is not None
        and max_drawdown_pct <= max_allowed_drawdown_pct
    )
    guaranteed_profit_claimed = _bool(source.get("guaranteed_profit_claimed"))
    fixed_return_target_promised = _bool(source.get("fixed_return_target_promised"))
    gates = {
        "sample_gate_cleared": sample_gate_cleared,
        "expectancy_positive": _bool(source.get("expectancy_positive")),
        "profit_factor_gate_cleared": profit_factor_gate_cleared,
        "drawdown_gate_cleared": drawdown_gate_cleared,
        "walk_forward_gate_cleared": _bool(
            source.get("walk_forward_gate_cleared")
        ),
        "out_of_sample_passed": _bool(source.get("out_of_sample_passed")),
        "spread_slippage_model_present": _bool(
            source.get("spread_slippage_model_present")
        ),
        "daily_profit_target_defined": _bool(
            source.get("daily_profit_target_defined")
        ),
        "no_guaranteed_profit_claim": not guaranteed_profit_claimed,
        "no_fixed_return_promise": not fixed_return_target_promised,
    }
    blockers = [
        key
        for key, value in gates.items()
        if key not in {"drawdown_gate_cleared"} and value is False
    ]
    return {
        "evidence_sample_count": _number_or_none(evidence_sample_count),
        "min_evidence_sample_count": _number_or_none(min_evidence_sample_count),
        "sample_gate_cleared": sample_gate_cleared,
        "expectancy_positive": gates["expectancy_positive"],
        "profit_factor": _number_or_none(profit_factor),
        "min_profit_factor": _number_or_none(min_profit_factor),
        "profit_factor_gate_cleared": profit_factor_gate_cleared,
        "max_drawdown_pct": _number_or_none(max_drawdown_pct),
        "max_allowed_drawdown_pct": _number_or_none(max_allowed_drawdown_pct),
        "drawdown_gate_cleared": drawdown_gate_cleared,
        "walk_forward_gate_cleared": gates["walk_forward_gate_cleared"],
        "out_of_sample_passed": gates["out_of_sample_passed"],
        "spread_slippage_model_present": gates[
            "spread_slippage_model_present"
        ],
        "daily_profit_target_defined": gates["daily_profit_target_defined"],
        "guaranteed_profit_claimed": guaranteed_profit_claimed,
        "fixed_return_target_promised": fixed_return_target_promised,
        "band_is_observation_only": True,
        "band_is_financial_advice": False,
        "band_is_live_trading_permission": False,
        "profit_edge_evidence_present": all(gates.values()),
        "profit_evidence_blockers": blockers,
    }


def _execution_readiness_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    broker_mode = source.get("broker_mode_declared")
    broker_mode_ready = _broker_mode_ready(broker_mode)
    hard_false_clear = all(source.get(field) is False for field in (
        "broker_api_called",
        "credential_read",
        "live_trade_executed",
        "demo_trade_executed",
    ))
    gates = {
        "protected_runtime_gate_ready": _bool(
            source.get("protected_runtime_gate_ready")
        ),
        "credential_session_bridge_ready": _bool(
            source.get("credential_session_bridge_ready")
        ),
        "post_trade_review_ready": _bool(source.get("post_trade_review_ready")),
        "twenty_two_hour_six_day_ready": _bool(
            source.get("twenty_two_hour_six_day_ready")
        ),
        "broker_mode_declared": broker_mode_ready,
        "one_order_gate_ready": _bool(source.get("one_order_gate_ready")),
        "owner_approval_required": _bool(source.get("owner_approval_required")),
        "runtime_hard_false_inputs_clear": hard_false_clear,
    }
    blockers = [key for key, value in gates.items() if value is False]
    return {
        **gates,
        "broker_mode_label": _safe_broker_mode_label(broker_mode),
        "broker_api_called": False,
        "credential_read": False,
        "live_trade_executed": False,
        "demo_trade_executed": False,
        "execution_readiness_cleared": all(gates.values()),
        "execution_blockers": blockers,
    }


def _risk_control_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    max_risk_per_trade_pct = _decimal(source.get("max_risk_per_trade_pct"))
    max_daily_loss_pct = _decimal(source.get("max_daily_loss_pct"))
    max_drawdown_pct = _decimal(source.get("max_drawdown_pct"))
    max_allowed_drawdown_pct = _decimal(source.get("max_allowed_drawdown_pct"))
    risk_per_trade_gate = (
        max_risk_per_trade_pct is not None
        and max_risk_per_trade_pct <= Decimal("0.01")
    )
    daily_loss_gate = (
        max_daily_loss_pct is not None
        and max_daily_loss_pct <= Decimal("0.03")
    )
    drawdown_gate = (
        max_drawdown_pct is not None
        and max_allowed_drawdown_pct is not None
        and max_drawdown_pct <= max_allowed_drawdown_pct
    )
    gates = {
        "risk_per_trade_gate": risk_per_trade_gate,
        "daily_loss_gate": daily_loss_gate,
        "drawdown_gate_cleared": drawdown_gate,
        "stop_loss_required": _bool(source.get("stop_loss_required")),
        "take_profit_required": _bool(source.get("take_profit_required")),
        "kill_switch_ready": _bool(source.get("kill_switch_ready")),
        "kill_switch_inactive": source.get("kill_switch_active") is False,
        "daily_loss_stop_ready": _bool(source.get("daily_loss_stop_ready")),
        "daily_loss_stop_inactive": source.get("daily_loss_stop_active")
        is False,
        "one_order_only": _bool(source.get("one_order_only")),
        "next_order_blocked_until_review": _bool(
            source.get("next_order_blocked_until_review")
        ),
    }
    blockers = [key for key, value in gates.items() if value is False]
    return {
        "max_risk_per_trade_pct": _number_or_none(max_risk_per_trade_pct),
        "max_daily_loss_pct": _number_or_none(max_daily_loss_pct),
        "max_drawdown_pct": _number_or_none(max_drawdown_pct),
        "max_allowed_drawdown_pct": _number_or_none(max_allowed_drawdown_pct),
        **gates,
        "risk_limits_cleared": all(gates.values()),
        "risk_blockers": blockers,
    }


def _daily_cycle_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    gates = {
        "pre_trade_check_ready": _bool(source.get("pre_trade_check_ready")),
        "execution_window_defined": _bool(source.get("execution_window_defined")),
        "post_trade_review_required": _bool(
            source.get("post_trade_review_required")
        ),
        "daily_pnl_record_required": _bool(
            source.get("daily_pnl_record_required")
        ),
        "no_second_trade_without_review": _bool(
            source.get("no_second_trade_without_review")
        ),
        "owner_can_stop": _bool(source.get("owner_can_stop")),
    }
    blockers = [key for key, value in gates.items() if value is False]
    return {
        **gates,
        "daily_cycle_ready": all(gates.values()),
        "daily_cycle_blockers": blockers,
    }


def _cadence_summary() -> dict[str, Any]:
    return {
        "daily_review": True,
        "weekly_review": True,
        "monthly_review": True,
        "yearly_review": True,
        "compound_review_only": True,
        "no_money_movement": True,
        "no_banking_transfer": True,
        "applies_to": "FOREX_METADATA_ONLY",
        "reusable_cadence_metadata": True,
    }


def _banking_freeze_summary(
    *, banking_focus_blockers: tuple[str, ...], status: str
) -> dict[str, Any]:
    return {
        "status": status,
        "banking_focus_detected": bool(banking_focus_blockers),
        "banking_work_allowed": False,
        "withdrawal_work_allowed": False,
        "transfer_work_allowed": False,
        "money_movement_allowed": False,
        "next_best_packet_remains_profit_evidence": True,
        "statement": BANKING_DEFERRED_STATEMENT,
        "blockers": list(banking_focus_blockers),
    }


def _return_discovery_band(
    *, source: Mapping[str, Any], profit_evidence_summary: dict[str, Any]
) -> str:
    return_fraction = _return_fraction(source)
    if return_fraction is None:
        if profit_evidence_summary["profit_edge_evidence_present"]:
            return DAILY_PROFIT_EVIDENCE_PRESENT
        return BELOW_PROFIT_THRESHOLD
    if return_fraction >= Decimal("1.20"):
        return ONE_HUNDRED_TWENTY_PERCENT_STRESS_REVIEW_BAND
    if return_fraction >= Decimal("1.00"):
        return ONE_HUNDRED_PERCENT_REVIEW_BAND
    if return_fraction >= Decimal("0.50"):
        return FIFTY_PERCENT_REVIEW_BAND
    if return_fraction >= Decimal("0.20"):
        return TWENTY_PERCENT_REVIEW_BAND
    if return_fraction > Decimal("0"):
        return DAILY_PROFIT_EVIDENCE_PRESENT
    return BELOW_PROFIT_THRESHOLD


def _return_fraction(source: Mapping[str, Any]) -> Decimal | None:
    for key in (
        "observed_return_pct",
        "daily_return_pct",
        "realized_return_pct",
        "profit_return_pct",
        "return_pct",
    ):
        value = _decimal(source.get(key))
        if value is None:
            continue
        if value > Decimal("2"):
            return value / Decimal("100")
        return value
    return None


def _stress_review_required(return_discovery_band: str) -> bool:
    return return_discovery_band in {
        ONE_HUNDRED_PERCENT_REVIEW_BAND,
        ONE_HUNDRED_TWENTY_PERCENT_STRESS_REVIEW_BAND,
    }


def _missing_inputs(source: Mapping[str, Any]) -> tuple[str, ...]:
    if not source:
        return (
            *PROFIT_REQUIRED_FIELDS,
            *EXECUTION_REQUIRED_FIELDS,
            *RISK_REQUIRED_FIELDS,
            *DAILY_CYCLE_REQUIRED_FIELDS,
        )
    required = (
        *PROFIT_REQUIRED_FIELDS,
        *EXECUTION_REQUIRED_FIELDS,
        *RISK_REQUIRED_FIELDS,
        *DAILY_CYCLE_REQUIRED_FIELDS,
    )
    return tuple(field for field in required if field not in source)


def _sensitive_data_blockers(value: Any) -> tuple[str, ...]:
    blockers: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, child in node.items():
                key_text = str(raw_key).lower()
                if _sensitive_key_blocked(key_text, child):
                    blockers.append(f"sensitive_key_at_{path}")
                    continue
                walk(child, f"{path}.field")
            return
        if isinstance(node, Sequence) and not isinstance(node, (str, bytes, bytearray)):
            for child in node:
                walk(child, f"{path}.item")
            return
        if isinstance(node, str) and _secret_like_value(node):
            blockers.append(f"secret_like_value_at_{path}")
            return
        if isinstance(node, int) and not isinstance(node, bool):
            if _has_long_digit_run(str(node)):
                blockers.append(f"long_digit_run_at_{path}")

    walk(value, "payload")
    return tuple(_unique(blockers))


def _sensitive_key_blocked(key_text: str, value: Any) -> bool:
    if key_text in SAFE_SENSITIVE_NAMED_METADATA_KEYS and isinstance(value, bool):
        return False
    return any(part in key_text for part in SENSITIVE_KEY_PARTS)


def _secret_like_value(value: str) -> bool:
    lowered = value.lower()
    markers = (
        "sk-",
        "bearer ",
        "api key",
        "token value",
        "broker token",
        "access token",
        "private key",
        "password",
        "secret",
        "-----begin",
    )
    return any(marker in lowered for marker in markers) or _has_long_digit_run(
        value
    )


def _has_long_digit_run(value: str) -> bool:
    run = 0
    for character in value:
        if character.isdigit():
            run += 1
            if run >= 9:
                return True
        else:
            run = 0
    return False


def _banking_focus_blockers(value: Any) -> tuple[str, ...]:
    blockers: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, child in node.items():
                key_text = str(raw_key).lower()
                if key_text == "banking_focus_requested" and child is True:
                    blockers.append("banking_focus_flag_true")
                    continue
                if any(part in key_text for part in BANKING_KEY_PARTS):
                    blockers.append(f"banking_focus_key_at_{path}")
                    continue
                walk(child, f"{path}.field")
            return
        if isinstance(node, Sequence) and not isinstance(node, (str, bytes, bytearray)):
            for child in node:
                walk(child, f"{path}.item")

    walk(value, "payload")
    return tuple(_unique(blockers))


def _next_best_packet(daily_profit_status: str) -> str:
    if daily_profit_status in {
        DAILY_PROFIT_EXECUTION_EVIDENCE_READY,
        READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT,
    }:
        return NEXT_PACKET_PROTECTED_DEMO
    if daily_profit_status == READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW:
        return NEXT_PACKET_LIVE_MICRO_REVIEW
    return NEXT_PACKET_CURRENT


def _safe_manual_next_action(daily_profit_status: str) -> str:
    if daily_profit_status == BLOCKED_BY_BANKING_FOCUS:
        return BANKING_DEFERRED_STATEMENT
    if daily_profit_status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive fields and rerun metadata-only evaluation."
    if daily_profit_status == INCOMPLETE_INPUTS:
        return "Provide complete sanitized Forex profit-readiness metadata."
    if daily_profit_status == BLOCKED_BY_NO_PROFIT_EDGE_EVIDENCE:
        return "Continue sanitized evidence capture before any execution attempt."
    if daily_profit_status == BLOCKED_BY_RISK_LIMITS:
        return "Reduce risk or add stress/drawdown review evidence before proceeding."
    if daily_profit_status == BLOCKED_BY_EXECUTION_READINESS:
        return "Repair protected runtime readiness metadata before demo review."
    if daily_profit_status == BLOCKED_BY_POST_TRADE_REVIEW:
        return "Complete post-trade review readiness before another order path."
    if daily_profit_status == READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW:
        return "Owner may review a separate live-micro exception packet; no trade is authorized here."
    return "Owner may review the protected demo daily profit attempt packet next."


def _owner_action_queue(
    *, daily_profit_status: str, blockers: Sequence[str], next_best_packet: str
) -> list[dict[str, Any]]:
    if daily_profit_status == BLOCKED_BY_BANKING_FOCUS:
        return [
            {
                "action": "DEFER_BANKING_TRANSFER_WITHDRAWAL_WORK",
                "required": True,
                "summary": BANKING_DEFERRED_STATEMENT,
            },
            {
                "action": "RETURN_TO_PROFIT_EXECUTION_EVIDENCE",
                "required": True,
                "next_best_packet": next_best_packet,
            },
        ]
    if daily_profit_status == BLOCKED_BY_SENSITIVE_DATA:
        return [
            {
                "action": "REMOVE_SENSITIVE_DATA_FROM_METADATA",
                "required": True,
                "raw_values_echoed": False,
            }
        ]
    if daily_profit_status in {
        DAILY_PROFIT_EXECUTION_EVIDENCE_READY,
        READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT,
        READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW,
    }:
        return [
            {
                "action": "OWNER_REVIEW_PROFIT_EVIDENCE",
                "required": True,
                "next_best_packet": next_best_packet,
            },
            {
                "action": "APPROVE_OR_REJECT_SEPARATE_EXECUTION_PACKET",
                "required": True,
                "no_trade_authorized_by_this_result": True,
            },
        ]
    return [
        {
            "action": "REPAIR_BLOCKERS",
            "required": True,
            "blocker_count": len(blockers),
            "next_best_packet": next_best_packet,
        }
    ]


def _audit_record(
    *,
    daily_profit_status: str,
    daily_profit_ready: bool,
    blockers: Sequence[str],
    missing_inputs: Sequence[str],
    return_discovery_band: str,
    next_best_packet: str,
    sensitive_data_detected: bool,
    banking_focus_detected: bool,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "daily_profit_status": daily_profit_status,
        "daily_profit_ready": daily_profit_ready,
        "return_discovery_band": return_discovery_band,
        "blocker_count": len(blockers),
        "missing_input_count": len(missing_inputs),
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_values_echoed": False,
        "banking_focus_detected": banking_focus_detected,
        "read_only": True,
        "metadata_only": True,
        "next_best_packet": next_best_packet,
    }


def _safety() -> dict[str, Any]:
    safety: dict[str, Any] = {field: False for field in HARD_FALSE_FIELDS}
    safety.update(
        {
            "no_guaranteed_profit_claim": True,
            "no_fixed_return_promise": True,
            "return_bands_are_observation_only": True,
            "return_bands_are_financial_advice": False,
            "return_bands_authorize_live_trading": False,
            "broker_execution_authorized": False,
            "live_micro_exception_authorized": False,
            "protected_demo_order_authorized": False,
            "credential_or_account_value_echoed": False,
        }
    )
    return safety


def _redacted_profit_evidence_summary() -> dict[str, Any]:
    return {
        "redacted": True,
        "profit_edge_evidence_present": False,
        "profit_evidence_blockers": ["redacted_until_safe_metadata_provided"],
        "guaranteed_profit_claimed": False,
        "fixed_return_target_promised": False,
        "band_is_observation_only": True,
        "band_is_financial_advice": False,
        "band_is_live_trading_permission": False,
    }


def _redacted_execution_readiness_summary() -> dict[str, Any]:
    return {
        "redacted": True,
        "execution_readiness_cleared": False,
        "post_trade_review_ready": False,
        "execution_blockers": ["redacted_until_safe_metadata_provided"],
        "broker_api_called": False,
        "credential_read": False,
        "live_trade_executed": False,
        "demo_trade_executed": False,
    }


def _redacted_risk_control_summary() -> dict[str, Any]:
    return {
        "redacted": True,
        "risk_limits_cleared": False,
        "drawdown_gate_cleared": False,
        "risk_blockers": ["redacted_until_safe_metadata_provided"],
    }


def _redacted_daily_cycle_summary() -> dict[str, Any]:
    return {
        "redacted": True,
        "daily_cycle_ready": False,
        "post_trade_review_required": False,
        "daily_cycle_blockers": ["redacted_until_safe_metadata_provided"],
    }


def _broker_mode_ready(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.upper() in ALLOWED_BROKER_MODE_LABELS
    return False


def _safe_broker_mode_label(value: Any) -> str:
    if isinstance(value, str) and value.upper() in ALLOWED_BROKER_MODE_LABELS:
        return value.upper()
    if value is True:
        return "DECLARED"
    return "UNDECLARED"


def _bool(value: Any) -> bool:
    return value is True


def _decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _number_or_none(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
