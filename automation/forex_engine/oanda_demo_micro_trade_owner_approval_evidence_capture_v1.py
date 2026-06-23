"""Owner approval and evidence capture gate for OANDA demo micro-trade review.

This module evaluates sanitized in-memory dictionaries only. It does not read
files, read environment variables, call a broker, persist evidence, or place an
order. The output is a deterministic readiness and evidence classification
record for operator review.
"""

from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-MICRO-TRADE-OWNER-APPROVAL-EVIDENCE-CAPTURE-V1"
EVIDENCE_VERSION = "v1"

BRIDGE_READY_STATUS = "MICRO_TRADE_READY_FOR_OWNER_REVIEW"

EVIDENCE_CAPTURE_BLOCKED_MISSING_BRIDGE_RESULT = "EVIDENCE_CAPTURE_BLOCKED_MISSING_BRIDGE_RESULT"
EVIDENCE_CAPTURE_BLOCKED_BRIDGE_NOT_READY = "EVIDENCE_CAPTURE_BLOCKED_BRIDGE_NOT_READY"
EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION = "EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION"
EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW = "EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW"
EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT = "EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT"
EVIDENCE_CAPTURE_COMPLETE_PROFIT = "EVIDENCE_CAPTURE_COMPLETE_PROFIT"
EVIDENCE_CAPTURE_COMPLETE_LOSS = "EVIDENCE_CAPTURE_COMPLETE_LOSS"
EVIDENCE_CAPTURE_COMPLETE_BREAKEVEN = "EVIDENCE_CAPTURE_COMPLETE_BREAKEVEN"
EVIDENCE_CAPTURE_REJECTED = "EVIDENCE_CAPTURE_REJECTED"

EXECUTION_AUTHORITY_KEYS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

BRIDGE_REQUIRED_FIELDS = (
    "trade_plan_summary",
    "broker_readiness_summary",
    "risk_summary",
    "money_state_summary",
    "evidence_requirements",
)

OWNER_REQUIRED_TRUE_FIELDS = (
    "owner_review_required",
    "owner_approved_runtime_only_demo_review",
    "owner_acknowledged_loss_risk",
    "owner_acknowledged_no_profit_guarantee",
    "owner_acknowledged_stop_loss_required",
    "owner_acknowledged_take_profit_required",
)

OWNER_REQUIRED_FALSE_FIELDS = (
    "owner_approved_live_trading",
    "owner_approved_autonomous_execution",
)

PRE_TRADE_REQUIRED_FIELDS = (
    "candidate_id",
    "instrument",
    "direction",
    "planned_entry",
    "stop_loss",
    "take_profit",
    "position_size_units",
    "risk_amount",
    "reward_risk_ratio",
    "spread_snapshot",
    "balance_snapshot",
    "nav_snapshot",
    "margin_available_snapshot",
    "kill_switch_state",
    "daily_stop_state",
    "max_loss_gate_state",
    "timestamp_utc",
)

POST_TRADE_REQUIRED_FIELDS = (
    "realized_pl",
    "exit_price",
    "close_reason",
    "trade_duration_minutes",
    "post_balance",
    "post_nav",
    "timestamp_utc",
)

RUNTIME_ACTIONS = (
    "inject credentials runtime-only outside repo",
    "confirm OANDA demo account in runtime",
    "confirm no live account",
    "operator manually approves any actual demo order outside this module",
    "capture before/after sanitized evidence",
    "record realized P/L",
)


def evaluate_oanda_demo_micro_trade_owner_approval_evidence_capture_v1(
    bridge_result: dict | None = None,
    owner_decision: dict | None = None,
    pre_trade_evidence: dict | None = None,
    post_trade_evidence: dict | None = None,
) -> dict:
    """Evaluate owner approval and sanitized evidence capture readiness."""

    bridge = _mapping(bridge_result)
    owner = _mapping(owner_decision)
    pre_trade = _mapping(pre_trade_evidence)
    post_trade = _mapping(post_trade_evidence)

    if not bridge:
        return _result(
            status=EVIDENCE_CAPTURE_BLOCKED_MISSING_BRIDGE_RESULT,
            blockers=["missing_bridge_result"],
            warnings=_default_warnings(),
            bridge=bridge,
            owner=owner,
            pre_trade=pre_trade,
            post_trade=post_trade,
        )

    unsafe_blockers = _unsafe_authority_blockers(bridge, owner)
    bridge_blockers = _bridge_blockers(bridge)
    owner_blockers = _owner_decision_blockers(owner)
    pre_trade_blockers = _pre_trade_blockers(pre_trade)
    post_trade_supplied = bool(post_trade)
    post_trade_blockers = _post_trade_blockers(post_trade) if post_trade_supplied else []

    blockers = _unique(
        unsafe_blockers + bridge_blockers + owner_blockers + pre_trade_blockers + post_trade_blockers
    )

    if unsafe_blockers:
        status = EVIDENCE_CAPTURE_REJECTED
    elif bridge_blockers:
        status = EVIDENCE_CAPTURE_BLOCKED_BRIDGE_NOT_READY
    elif owner_blockers or pre_trade_blockers:
        status = EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION
    elif post_trade_supplied and post_trade_blockers:
        status = EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT
    elif post_trade_supplied:
        status = _post_trade_status(post_trade)
    else:
        status = EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status, post_trade_supplied),
        bridge=bridge,
        owner=owner,
        pre_trade=pre_trade,
        post_trade=post_trade,
    )


def _bridge_blockers(bridge: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if bridge.get("status") != BRIDGE_READY_STATUS:
        blockers.append("bridge_status_not_ready_for_owner_review")

    authority = _mapping(bridge.get("execution_authority"))
    for key in EXECUTION_AUTHORITY_KEYS:
        if _bool(authority.get(key)):
            blockers.append(f"bridge_{key}_must_remain_false")
        if key not in authority:
            blockers.append(f"bridge_missing_{key}")

    for field in BRIDGE_REQUIRED_FIELDS:
        if not isinstance(bridge.get(field), Mapping):
            blockers.append(f"missing_{field}")
    return blockers


def _owner_decision_blockers(owner: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not owner:
        return ["missing_owner_decision"]

    for field in OWNER_REQUIRED_TRUE_FIELDS:
        if not _bool(owner.get(field)):
            blockers.append(f"{field}_not_confirmed")

    for field in OWNER_REQUIRED_FALSE_FIELDS:
        if _bool(owner.get(field)):
            blockers.append(f"{field}_must_remain_false")
    return blockers


def _pre_trade_blockers(pre_trade: Mapping[str, Any]) -> list[str]:
    if not pre_trade:
        return ["missing_pre_trade_evidence"]

    blockers = [f"missing_pre_trade_{field}" for field in PRE_TRADE_REQUIRED_FIELDS if not _present(pre_trade.get(field))]
    if pre_trade.get("evidence_source") != "sanitized_runtime_input":
        blockers.append("pre_trade_evidence_source_not_sanitized_runtime_input")
    return blockers


def _post_trade_blockers(post_trade: Mapping[str, Any]) -> list[str]:
    blockers = [
        f"missing_post_trade_{field}" for field in POST_TRADE_REQUIRED_FIELDS if not _present(post_trade.get(field))
    ]
    if post_trade.get("evidence_source") != "sanitized_runtime_input":
        blockers.append("post_trade_evidence_source_not_sanitized_runtime_input")
    if _number(post_trade.get("realized_pl")) is None:
        blockers.append("post_trade_realized_pl_not_numeric")
    return _unique(blockers)


def _unsafe_authority_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for payload in payloads:
        for key in EXECUTION_AUTHORITY_KEYS:
            if _bool(payload.get(key)):
                blockers.append(f"unsafe_{key}_true")
    return _unique(blockers)


def _post_trade_status(post_trade: Mapping[str, Any]) -> str:
    realized_pl = _number(post_trade.get("realized_pl"))
    if realized_pl is None:
        return EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT
    if realized_pl > 0:
        return EVIDENCE_CAPTURE_COMPLETE_PROFIT
    if realized_pl < 0:
        return EVIDENCE_CAPTURE_COMPLETE_LOSS
    return EVIDENCE_CAPTURE_COMPLETE_BREAKEVEN


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    bridge: Mapping[str, Any],
    owner: Mapping[str, Any],
    pre_trade: Mapping[str, Any],
    post_trade: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "evidence_version": EVIDENCE_VERSION,
        "status": status,
        "blockers": _unique(blockers),
        "warnings": _unique(warnings),
        "owner_decision_summary": _owner_summary(owner),
        "pre_trade_evidence_summary": _pre_trade_summary(pre_trade),
        "post_trade_evidence_summary": _post_trade_summary(post_trade),
        "required_runtime_actions": list(RUNTIME_ACTIONS),
        "required_human_actions": _required_human_actions(status),
        "execution_authority": _execution_authority(),
        "evidence_record": _evidence_record(bridge, owner, pre_trade, post_trade),
        "next_safe_action": _next_safe_action(status),
    }


def _owner_summary(owner: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "owner_review_required": _bool(owner.get("owner_review_required")),
        "owner_approved_runtime_only_demo_review": _bool(owner.get("owner_approved_runtime_only_demo_review")),
        "owner_approved_live_trading": _bool(owner.get("owner_approved_live_trading")),
        "owner_approved_autonomous_execution": _bool(owner.get("owner_approved_autonomous_execution")),
        "owner_acknowledged_loss_risk": _bool(owner.get("owner_acknowledged_loss_risk")),
        "owner_acknowledged_no_profit_guarantee": _bool(owner.get("owner_acknowledged_no_profit_guarantee")),
        "owner_acknowledged_stop_loss_required": _bool(owner.get("owner_acknowledged_stop_loss_required")),
        "owner_acknowledged_take_profit_required": _bool(owner.get("owner_acknowledged_take_profit_required")),
    }


def _pre_trade_summary(pre_trade: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": _text(pre_trade.get("candidate_id"), "MISSING"),
        "instrument": _text(pre_trade.get("instrument"), "MISSING"),
        "direction": _text(pre_trade.get("direction"), "MISSING"),
        "planned_entry": _number(pre_trade.get("planned_entry")),
        "stop_loss": _number(pre_trade.get("stop_loss")),
        "take_profit": _number(pre_trade.get("take_profit")),
        "position_size_units": _number(pre_trade.get("position_size_units")),
        "risk_amount": _number(pre_trade.get("risk_amount")),
        "reward_risk_ratio": _number(pre_trade.get("reward_risk_ratio")),
        "evidence_source": _text(pre_trade.get("evidence_source"), "MISSING"),
        "timestamp_utc": _text(pre_trade.get("timestamp_utc"), "MISSING"),
    }


def _post_trade_summary(post_trade: Mapping[str, Any]) -> dict[str, Any]:
    realized_pl = _number(post_trade.get("realized_pl"))
    return {
        "realized_pl": realized_pl,
        "outcome": _outcome_label(realized_pl),
        "exit_price": _number(post_trade.get("exit_price")),
        "close_reason": _text(post_trade.get("close_reason"), "MISSING"),
        "trade_duration_minutes": _number(post_trade.get("trade_duration_minutes")),
        "post_balance": _number(post_trade.get("post_balance")),
        "post_nav": _number(post_trade.get("post_nav")),
        "evidence_source": _text(post_trade.get("evidence_source"), "MISSING"),
        "timestamp_utc": _text(post_trade.get("timestamp_utc"), "MISSING"),
    }


def _evidence_record(
    bridge: Mapping[str, Any],
    owner: Mapping[str, Any],
    pre_trade: Mapping[str, Any],
    post_trade: Mapping[str, Any],
) -> dict[str, Any]:
    trade_plan = _mapping(bridge.get("trade_plan_summary"))
    return {
        "bridge_status": _text(bridge.get("status"), "MISSING"),
        "candidate_id": _text(pre_trade.get("candidate_id"), _text(trade_plan.get("candidate_id"), "MISSING")),
        "instrument": _text(pre_trade.get("instrument"), _text(trade_plan.get("instrument"), "MISSING")),
        "direction": _text(pre_trade.get("direction"), _text(trade_plan.get("direction"), "MISSING")),
        "owner_runtime_only_demo_review_approved": _bool(owner.get("owner_approved_runtime_only_demo_review")),
        "pre_trade_evidence_source": _text(pre_trade.get("evidence_source"), "MISSING"),
        "post_trade_evidence_source": _text(post_trade.get("evidence_source"), "MISSING"),
        "realized_pl": _number(post_trade.get("realized_pl")),
        "profitability_proven": False,
        "profitability_evidence_recorded": bool(post_trade),
        "execution_authority": _execution_authority(),
    }


def _required_human_actions(status: str) -> list[str]:
    if status == EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW:
        return [
            "review the runtime-only demo package",
            "keep order placement outside this module",
            "capture post-trade evidence after any separately approved runtime action",
        ]
    if status.startswith("EVIDENCE_CAPTURE_COMPLETE"):
        return ["review realized P/L evidence", "decide whether another governed demo review is justified"]
    return ["resolve listed blockers", "do not place a trade from this module"]


def _execution_authority() -> dict[str, bool]:
    return {key: False for key in EXECUTION_AUTHORITY_KEYS}


def _warnings(status: str, post_trade_supplied: bool) -> list[str]:
    warnings = [
        "no_profit_guarantee",
        "runtime_only_credentials_outside_repo_required",
        "order_placement_outside_this_module",
        "execution_authority_false",
    ]
    if status == EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW and not post_trade_supplied:
        warnings.append("post_trade_evidence_not_recorded_yet")
    if status.startswith("EVIDENCE_CAPTURE_COMPLETE"):
        warnings.append("single_trade_outcome_is_evidence_not_profitability_proof")
    return warnings


def _default_warnings() -> list[str]:
    return [
        "missing_bridge_result",
        "no_profit_guarantee",
        "execution_authority_false",
    ]


def _next_safe_action(status: str) -> str:
    return {
        EVIDENCE_CAPTURE_BLOCKED_MISSING_BRIDGE_RESULT: "provide_bridge_ready_result_from_profitability_bridge",
        EVIDENCE_CAPTURE_BLOCKED_BRIDGE_NOT_READY: "repair_bridge_package_before_owner_evidence_review",
        EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION: "provide_owner_decision_and_sanitized_pre_trade_evidence",
        EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW: "owner_review_runtime_only_demo_package_outside_repo",
        EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT: "capture_complete_sanitized_post_trade_result",
        EVIDENCE_CAPTURE_COMPLETE_PROFIT: "review_profit_evidence_without_claiming_persistent_profitability",
        EVIDENCE_CAPTURE_COMPLETE_LOSS: "review_loss_evidence_and_risk_controls_before_any_next_trade",
        EVIDENCE_CAPTURE_COMPLETE_BREAKEVEN: "review_breakeven_evidence_before_any_next_trade",
        EVIDENCE_CAPTURE_REJECTED: "remove_unsafe_execution_authority_request_before_review",
    }.get(status, "stop_and_review_evidence_capture_state")


def _outcome_label(realized_pl: float | None) -> str:
    if realized_pl is None:
        return "MISSING"
    if realized_pl > 0:
        return "PROFIT"
    if realized_pl < 0:
        return "LOSS"
    return "BREAKEVEN"


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


def _text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value).strip()


def _present(value: Any) -> bool:
    if value in (None, "", [], {}):
        return False
    if isinstance(value, str) and value.strip().upper() in {"UNAVAILABLE", "UNKNOWN", "MISSING"}:
        return False
    return True


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
