"""OANDA demo micro-trade profitability bridge.

This module evaluates sanitized, in-memory readiness evidence for a future
owner-reviewed OANDA demo micro-trade. It never reads files or environment
variables, never calls a broker, and never grants execution authority.
"""

from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-MICRO-TRADE-PROFITABILITY-BRIDGE-V1"
BRIDGE_VERSION = "v1"

MICRO_TRADE_BLOCKED_MISSING_PLAN = "MICRO_TRADE_BLOCKED_MISSING_PLAN"
MICRO_TRADE_BLOCKED_BROKER_READINESS = "MICRO_TRADE_BLOCKED_BROKER_READINESS"
MICRO_TRADE_BLOCKED_RISK = "MICRO_TRADE_BLOCKED_RISK"
MICRO_TRADE_BLOCKED_MONEY_STATE = "MICRO_TRADE_BLOCKED_MONEY_STATE"
MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE = "MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE"
MICRO_TRADE_BLOCKED_OWNER_APPROVAL = "MICRO_TRADE_BLOCKED_OWNER_APPROVAL"
MICRO_TRADE_READY_FOR_OWNER_REVIEW = "MICRO_TRADE_READY_FOR_OWNER_REVIEW"
MICRO_TRADE_REJECTED = "MICRO_TRADE_REJECTED"

REQUIRED_TRADE_PLAN_FIELDS = (
    "candidate_id",
    "strategy_id",
    "instrument",
    "direction",
    "entry_reason",
    "planned_entry",
    "stop_loss",
    "take_profit",
    "position_size_units",
    "risk_amount",
    "expected_reward_amount",
    "reward_risk_ratio",
    "max_spread_allowed",
    "order_type",
    "time_in_force",
    "trade_window",
    "hold_allowed_overnight",
    "overnight_risk_note",
)

ORDER_TYPES = frozenset({"MARKET", "LIMIT", "STOP"})

EXECUTION_FLAG_KEYS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "order_placement_allowed",
)


def evaluate_oanda_demo_micro_trade_profitability_bridge_v1(
    trade_plan: dict | None = None,
    broker_readiness: dict | None = None,
    risk_state: dict | None = None,
    money_state: dict | None = None,
    evidence_state: dict | None = None,
    owner_approval: dict | None = None,
) -> dict:
    """Evaluate a non-executing demo micro-trade readiness bridge."""

    plan = _mapping(trade_plan)
    broker = _mapping(broker_readiness)
    risk = _mapping(risk_state)
    money = _mapping(money_state)
    evidence = _mapping(evidence_state)
    approval = _mapping(owner_approval)

    if not plan:
        return _result(
            MICRO_TRADE_BLOCKED_MISSING_PLAN,
            blockers=["missing_trade_plan"],
            warnings=["profitability_not_proven", "owner_review_required"],
            trade_plan=plan,
            broker=broker,
            risk=risk,
            money=money,
            evidence=evidence,
            approval=approval,
            profitability_blockers=["missing_trade_plan"],
            risk_blockers=[],
            broker_blockers=[],
            money_blockers=[],
            evidence_blockers=[],
            approval_blockers=[],
        )

    unsafe_blockers = _unsafe_execution_blockers(plan, broker, risk, money, evidence, approval)
    profitability_blockers = _profitability_blockers(plan, risk, evidence)
    broker_blockers = _broker_blockers(broker)
    risk_blockers = _risk_blockers(plan, risk)
    money_blockers = _money_blockers(money)
    evidence_blockers = _evidence_blockers(evidence)
    approval_blockers = _approval_blockers(approval)

    blockers = (
        unsafe_blockers
        + profitability_blockers
        + broker_blockers
        + risk_blockers
        + money_blockers
        + evidence_blockers
        + approval_blockers
    )

    if unsafe_blockers:
        status = MICRO_TRADE_REJECTED
    elif profitability_blockers:
        status = MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE
    elif broker_blockers:
        status = MICRO_TRADE_BLOCKED_BROKER_READINESS
    elif risk_blockers:
        status = MICRO_TRADE_BLOCKED_RISK
    elif money_blockers:
        status = MICRO_TRADE_BLOCKED_MONEY_STATE
    elif evidence_blockers:
        status = MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE
    elif approval_blockers:
        status = MICRO_TRADE_BLOCKED_OWNER_APPROVAL
    else:
        status = MICRO_TRADE_READY_FOR_OWNER_REVIEW

    return _result(
        status,
        blockers=blockers,
        warnings=_warnings(status),
        trade_plan=plan,
        broker=broker,
        risk=risk,
        money=money,
        evidence=evidence,
        approval=approval,
        profitability_blockers=profitability_blockers,
        risk_blockers=risk_blockers,
        broker_blockers=broker_blockers,
        money_blockers=money_blockers,
        evidence_blockers=evidence_blockers,
        approval_blockers=approval_blockers,
    )


def _profitability_blockers(
    plan: Mapping[str, Any],
    risk: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for field in REQUIRED_TRADE_PLAN_FIELDS:
        if not _present(plan.get(field)):
            blockers.append(f"missing_{field}")

    planned_entry = _number(plan.get("planned_entry"))
    stop_loss = _number(plan.get("stop_loss"))
    take_profit = _number(plan.get("take_profit"))
    risk_amount = _number(plan.get("risk_amount"))
    expected_reward = _number(plan.get("expected_reward_amount"))
    reward_risk = _number(plan.get("reward_risk_ratio"))
    position_size = _number(plan.get("position_size_units"))
    max_spread = _number(plan.get("max_spread_allowed"))
    min_reward_risk = _positive_number(
        plan.get("min_reward_risk_ratio"),
        evidence.get("min_reward_risk_ratio"),
        default=1.5,
    )
    max_position_size = _positive_number(
        plan.get("max_position_size_units"),
        risk.get("max_position_size_units"),
        default=1000.0,
    )
    max_allowed_trade_loss = _number(risk.get("max_allowed_trade_loss"))
    direction = _upper(plan.get("direction"))
    order_type = _upper(plan.get("order_type"))

    if planned_entry is None:
        blockers.append("planned_entry_not_numeric")
    if stop_loss is None:
        blockers.append("stop_loss_not_numeric")
    if take_profit is None:
        blockers.append("take_profit_not_numeric")
    if risk_amount is None or risk_amount <= 0:
        blockers.append("risk_amount_not_positive")
    if expected_reward is None or expected_reward <= 0:
        blockers.append("expected_reward_not_positive")
    if reward_risk is None or reward_risk < min_reward_risk:
        blockers.append("reward_risk_below_threshold")
    if position_size is None or position_size <= 0:
        blockers.append("position_size_not_positive")
    elif position_size > max_position_size:
        blockers.append("position_size_above_micro_cap")
    if max_spread is None:
        blockers.append("max_spread_allowed_not_numeric")
    if direction not in {"BUY", "SELL"}:
        blockers.append("direction_not_buy_or_sell")
    if order_type not in ORDER_TYPES:
        blockers.append("order_type_not_supported")
    if not _text(plan.get("entry_reason")):
        blockers.append("entry_reason_blank")

    if planned_entry is not None and stop_loss is not None and take_profit is not None:
        if direction == "BUY" and not (stop_loss < planned_entry < take_profit):
            blockers.append("buy_stop_take_profit_geometry_invalid")
        if direction == "SELL" and not (take_profit < planned_entry < stop_loss):
            blockers.append("sell_stop_take_profit_geometry_invalid")

    if _bool(plan.get("hold_allowed_overnight")):
        if not _text(plan.get("overnight_risk_note")):
            blockers.append("overnight_risk_note_missing")
        if not _bool(risk.get("daily_stop_ready")):
            blockers.append("overnight_daily_stop_not_ready")
        if not _bool(risk.get("max_loss_gate_ready")):
            blockers.append("overnight_max_loss_gate_not_ready")
        if not _bool(risk.get("kill_switch_ready")):
            blockers.append("overnight_kill_switch_not_ready")
        if (
            risk_amount is None
            or max_allowed_trade_loss is None
            or max_allowed_trade_loss <= 0
            or risk_amount > max_allowed_trade_loss
        ):
            blockers.append("overnight_risk_amount_not_bounded")

    return _unique(blockers)


def _broker_blockers(broker: Mapping[str, Any]) -> list[str]:
    required = {
        "broker_readiness_passed": True,
        "read_only_money_visibility_ready": True,
        "demo_environment": True,
        "live_environment": False,
        "account_id_present_runtime_only": True,
        "credential_present_runtime_only": True,
        "no_credential_persistence": True,
        "no_account_id_persistence": True,
    }
    blockers: list[str] = []
    if _upper(broker.get("broker")) != "OANDA_DEMO":
        blockers.append("broker_not_oanda_demo")
    for field, expected in required.items():
        value = _bool(broker.get(field))
        if value is not expected:
            blockers.append(f"{field}_not_{str(expected).lower()}")
    return blockers


def _risk_blockers(plan: Mapping[str, Any], risk: Mapping[str, Any]) -> list[str]:
    true_fields = (
        "risk_gate_passed",
        "kill_switch_ready",
        "daily_stop_ready",
        "max_loss_gate_ready",
        "stop_loss_required",
        "take_profit_required",
        "no_averaging_down",
        "one_order_only",
    )
    blockers = [f"{field}_not_ready" for field in true_fields if not _bool(risk.get(field))]
    max_daily_loss_remaining = _number(risk.get("max_daily_loss_remaining"))
    max_allowed_trade_loss = _number(risk.get("max_allowed_trade_loss"))
    risk_amount = _number(plan.get("risk_amount"))

    if max_daily_loss_remaining is None or max_daily_loss_remaining <= 0:
        blockers.append("max_daily_loss_remaining_not_positive")
    if max_allowed_trade_loss is None or max_allowed_trade_loss <= 0:
        blockers.append("max_allowed_trade_loss_not_positive")
    if risk_amount is None or max_allowed_trade_loss is None or risk_amount > max_allowed_trade_loss:
        blockers.append("risk_amount_exceeds_allowed_trade_loss")
    return blockers


def _money_blockers(money: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in ("balance", "nav", "margin_available", "margin_used_percent"):
        if not _present(money.get(field)):
            blockers.append(f"missing_{field}")

    margin_used_percent = _number(money.get("margin_used_percent"))
    max_margin = _positive_number(money.get("max_margin_used_percent"), default=20.0)
    if margin_used_percent is None:
        blockers.append("margin_used_percent_not_numeric")
    elif margin_used_percent > max_margin:
        blockers.append("margin_used_percent_above_limit")

    open_count = _integer(money.get("open_trade_count"))
    pending_count = _integer(money.get("pending_order_count"))
    max_open = _integer(money.get("max_open_trade_count_allowed"), default=0)
    max_pending = _integer(money.get("max_pending_order_count_allowed"), default=0)
    if open_count is None:
        blockers.append("open_trade_count_missing")
    elif open_count > max_open:
        blockers.append("open_trade_count_above_allowed")
    if pending_count is None:
        blockers.append("pending_order_count_missing")
    elif pending_count > max_pending:
        blockers.append("pending_order_count_above_allowed")
    return blockers


def _evidence_blockers(evidence: Mapping[str, Any]) -> list[str]:
    required = (
        "evidence_capture_ready",
        "pre_trade_snapshot_required",
        "post_trade_snapshot_required",
        "pnl_capture_required",
        "broker_readiness_capture_required",
        "risk_capture_required",
        "screenshot_or_report_required",
        "trade_outcome_schema_ready",
    )
    return [f"{field}_not_ready" for field in required if not _bool(evidence.get(field))]


def _approval_blockers(approval: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not _bool(approval.get("owner_review_required")):
        blockers.append("owner_review_required_not_set")
    if not _bool(approval.get("owner_approved_for_demo_micro_trade_review")):
        blockers.append("owner_demo_micro_trade_review_not_approved")
    if _bool(approval.get("owner_approved_for_order_placement")):
        blockers.append("owner_order_placement_authority_must_remain_false")
    return blockers


def _unsafe_execution_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for payload in payloads:
        for key in EXECUTION_FLAG_KEYS:
            if _bool(payload.get(key)):
                blockers.append(f"unsafe_{key}_true")
    return _unique(blockers)


def _result(
    status: str,
    *,
    blockers: list[str],
    warnings: list[str],
    trade_plan: Mapping[str, Any],
    broker: Mapping[str, Any],
    risk: Mapping[str, Any],
    money: Mapping[str, Any],
    evidence: Mapping[str, Any],
    approval: Mapping[str, Any],
    profitability_blockers: list[str],
    risk_blockers: list[str],
    broker_blockers: list[str],
    money_blockers: list[str],
    evidence_blockers: list[str],
    approval_blockers: list[str],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "bridge_version": BRIDGE_VERSION,
        "status": status,
        "blockers": _unique(blockers),
        "warnings": _unique(warnings),
        "trade_plan_summary": _trade_plan_summary(trade_plan),
        "profitability_plan": _profitability_plan(trade_plan, risk, evidence, profitability_blockers),
        "risk_summary": _risk_summary(trade_plan, risk, risk_blockers),
        "broker_readiness_summary": _broker_summary(broker, broker_blockers),
        "money_state_summary": _money_summary(money, money_blockers),
        "evidence_requirements": _evidence_summary(evidence, evidence_blockers),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
        "owner_approval_summary": {
            "owner_review_required": _bool(approval.get("owner_review_required")),
            "owner_approved_for_demo_micro_trade_review": _bool(
                approval.get("owner_approved_for_demo_micro_trade_review")
            ),
            "owner_approved_for_order_placement": _bool(approval.get("owner_approved_for_order_placement")),
            "blockers": approval_blockers,
        },
    }


def _trade_plan_summary(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": _text(plan.get("candidate_id"), "MISSING"),
        "strategy_id": _text(plan.get("strategy_id"), "MISSING"),
        "instrument": _text(plan.get("instrument"), "MISSING"),
        "direction": _upper(plan.get("direction")) or "MISSING",
        "order_type": _upper(plan.get("order_type")) or "MISSING",
        "time_in_force": _text(plan.get("time_in_force"), "MISSING"),
        "trade_window": _text(plan.get("trade_window"), "MISSING"),
        "position_size_units": _number(plan.get("position_size_units")),
        "planned_entry": _number(plan.get("planned_entry")),
        "stop_loss": _number(plan.get("stop_loss")),
        "take_profit": _number(plan.get("take_profit")),
        "hold_allowed_overnight": _bool(plan.get("hold_allowed_overnight")),
    }


def _profitability_plan(
    plan: Mapping[str, Any],
    risk: Mapping[str, Any],
    evidence: Mapping[str, Any],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "profitability_proven": False,
        "profitability_claim_allowed": False,
        "profit_seeking_structure_ready": not blockers,
        "min_reward_risk_ratio": _positive_number(
            plan.get("min_reward_risk_ratio"),
            evidence.get("min_reward_risk_ratio"),
            default=1.5,
        ),
        "reward_risk_ratio": _number(plan.get("reward_risk_ratio")),
        "risk_amount": _number(plan.get("risk_amount")),
        "expected_reward_amount": _number(plan.get("expected_reward_amount")),
        "max_position_size_units": _positive_number(
            plan.get("max_position_size_units"),
            risk.get("max_position_size_units"),
            default=1000.0,
        ),
        "geometry_valid": not any("geometry_invalid" in blocker for blocker in blockers),
        "evidence_capture_required_after_outcome": True,
        "blockers": blockers,
    }


def _risk_summary(plan: Mapping[str, Any], risk: Mapping[str, Any], blockers: list[str]) -> dict[str, Any]:
    return {
        "risk_gate_passed": _bool(risk.get("risk_gate_passed")),
        "kill_switch_ready": _bool(risk.get("kill_switch_ready")),
        "daily_stop_ready": _bool(risk.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(risk.get("max_loss_gate_ready")),
        "risk_amount": _number(plan.get("risk_amount")),
        "max_allowed_trade_loss": _number(risk.get("max_allowed_trade_loss")),
        "max_daily_loss_remaining": _number(risk.get("max_daily_loss_remaining")),
        "one_order_only": _bool(risk.get("one_order_only")),
        "blockers": blockers,
    }


def _broker_summary(broker: Mapping[str, Any], blockers: list[str]) -> dict[str, Any]:
    return {
        "broker": _upper(broker.get("broker")) or "MISSING",
        "broker_readiness_passed": _bool(broker.get("broker_readiness_passed")),
        "read_only_money_visibility_ready": _bool(broker.get("read_only_money_visibility_ready")),
        "demo_environment": _bool(broker.get("demo_environment")),
        "live_environment": _bool(broker.get("live_environment")),
        "runtime_only_access_model": _bool(broker.get("account_id_present_runtime_only"))
        and _bool(broker.get("credential_present_runtime_only")),
        "persistence_blocked": _bool(broker.get("no_credential_persistence"))
        and _bool(broker.get("no_account_id_persistence")),
        "blockers": blockers,
    }


def _money_summary(money: Mapping[str, Any], blockers: list[str]) -> dict[str, Any]:
    return {
        "balance_present": _present(money.get("balance")),
        "nav_present": _present(money.get("nav")),
        "margin_available_present": _present(money.get("margin_available")),
        "margin_used_percent": _number(money.get("margin_used_percent")),
        "max_margin_used_percent": _positive_number(money.get("max_margin_used_percent"), default=20.0),
        "open_trade_count": _integer(money.get("open_trade_count")),
        "pending_order_count": _integer(money.get("pending_order_count")),
        "max_open_trade_count_allowed": _integer(money.get("max_open_trade_count_allowed"), default=0),
        "max_pending_order_count_allowed": _integer(money.get("max_pending_order_count_allowed"), default=0),
        "blockers": blockers,
    }


def _evidence_summary(evidence: Mapping[str, Any], blockers: list[str]) -> dict[str, Any]:
    required = (
        "evidence_capture_ready",
        "pre_trade_snapshot_required",
        "post_trade_snapshot_required",
        "pnl_capture_required",
        "broker_readiness_capture_required",
        "risk_capture_required",
        "screenshot_or_report_required",
        "trade_outcome_schema_ready",
    )
    return {field: _bool(evidence.get(field)) for field in required} | {"blockers": blockers}


def _execution_authority() -> dict[str, bool]:
    return {
        "execution_allowed": False,
        "demo_order_allowed": False,
        "live_order_allowed": False,
        "broker_write_allowed": False,
        "autonomous_order_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }


def _warnings(status: str) -> list[str]:
    warnings = ["profitability_not_proven", "owner_review_required", "execution_authority_false"]
    if status == MICRO_TRADE_READY_FOR_OWNER_REVIEW:
        warnings.append("ready_for_review_not_ready_for_order_placement")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        MICRO_TRADE_BLOCKED_MISSING_PLAN: "provide_complete_sanitized_demo_micro_trade_plan",
        MICRO_TRADE_BLOCKED_BROKER_READINESS: "provide_sanitized_oanda_demo_broker_readiness_and_money_visibility",
        MICRO_TRADE_BLOCKED_RISK: "resolve_kill_switch_daily_stop_max_loss_and_trade_risk_gates",
        MICRO_TRADE_BLOCKED_MONEY_STATE: "provide_read_only_money_state_with_margin_and_order_counts",
        MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE: "repair_trade_plan_profitability_structure_and_evidence_capture",
        MICRO_TRADE_BLOCKED_OWNER_APPROVAL: "obtain_owner_review_approval_without_order_placement_authority",
        MICRO_TRADE_READY_FOR_OWNER_REVIEW: "owner_review_demo_micro_trade_candidate_then_run_separate_approved_execution_packet",
        MICRO_TRADE_REJECTED: "remove_unsafe_execution_authority_request_before_review",
    }.get(status, "stop_and_review_bridge_state")


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "ready", "passed", "pass"}
    return bool(value)


def _number(value: Any) -> float | None:
    if isinstance(value, str):
        value = value.strip().removesuffix("%")
    try:
        if value in (None, ""):
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def _positive_number(*values: Any, default: float) -> float:
    for value in values:
        number = _number(value)
        if number is not None and number > 0:
            return number
    return default


def _integer(value: Any, default: int | None = None) -> int | None:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value).strip()


def _upper(value: Any) -> str:
    return _text(value).upper()


def _present(value: Any) -> bool:
    if value in (None, "", [], {}):
        return False
    if isinstance(value, str) and value.strip().upper() in {"UNAVAILABLE", "UNKNOWN", "MISSING"}:
        return False
    return True


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
