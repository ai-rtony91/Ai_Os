"""P14 protected demo-order command final rehearsal and owner execution card."""

from __future__ import annotations

from typing import Any, Dict

from automation.forex_engine.c1_owner_run_protected_demo_order_command_release_review_v1 import (
    evaluate_c1_owner_run_protected_demo_order_command_release_review,
)


CAMPAIGN_ID = "AIOS-FOREX-P14-C1-PROTECTED-DEMO-ORDER-COMMAND-FINAL-REHEARSAL-OWNER-EXECUTION-CARD-V1"
CANDIDATE_ID = "c1-eur-buy"
CANDIDATE_NAME = "paper_long_run_supervisor_v2 LONG EURUSD"
REQUIRED_P13_STATUS = (
    "P13_OWNER_RUN_PROTECTED_DEMO_ORDER_COMMAND_RELEASE_REVIEW_PASSED_FOR_P14_FINAL_REHEARSAL"
)

P14_FINAL_REHEARSAL_BLOCKED_OWNER_INPUT_REQUIRED = (
    "P14_FINAL_REHEARSAL_BLOCKED_OWNER_INPUT_REQUIRED"
)
P14_FINAL_REHEARSAL_BLOCKED_P13_REPAIR_REQUIRED = (
    "P14_FINAL_REHEARSAL_BLOCKED_P13_REPAIR_REQUIRED"
)
P14_FINAL_REHEARSAL_FAILED_REPAIR_REQUIRED = (
    "P14_FINAL_REHEARSAL_FAILED_REPAIR_REQUIRED"
)
P14_FINAL_REHEARSAL_READY = (
    "P14_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_PREPARED_FOR_P15_EXECUTION_PACKET_REVIEW"
)

P15_READY = "P15_READY"
NOT_READY = "NOT_READY"

OWNER_EXECUTION_REQUIRED_KEYS = [
    "owner_execution_card_required",
    "owner_execution_card_prepared",
    "explicit_owner_execution_packet_review_required",
    "credential_handling_review",
    "broker_connection_review",
    "final_owner_execution_card_review",
]

FORBIDDEN_FIELDS = [
    "account_identifier",
    "account_id",
    "broker_account_id",
    "account_number",
    "credentials",
    "credential",
    "password",
    "token",
    "secret",
    "api_key",
    "api_keys",
    "api_token",
    "broker_api_key",
    "raw_live_account_data",
    "live_account_data",
    "live_balance",
    "live_position_data",
]

P14_AUTH_TRUE_INVALID = [
    "broker_api_access_authorized",
    "credential_access_authorized",
    "broker_api_connection_authorized_now",
    "credential_access_authorized_now",
    "order_submission_authorized_now",
    "execution_command_authorized_now",
    "execution_command_authorized",
    "demo_order_placement_authorized",
    "live_trading_authorized",
    "money_movement_authorized",
    "autonomy_approval",
]

def _as_bool(value: Any) -> bool:
    return value is True


def _as_false(value: Any) -> bool:
    return value is False


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _has_forbidden_field(owner_input: Dict[str, Any]) -> bool:
    return any(field in owner_input for field in FORBIDDEN_FIELDS)


def _has_invalid_authorization_true(owner_input: Dict[str, Any]) -> bool:
    return any(_as_bool(owner_input.get(field)) for field in P14_AUTH_TRUE_INVALID)


def _missing_required_marker(owner_input: Dict[str, Any]) -> bool:
    for field in OWNER_EXECUTION_REQUIRED_KEYS:
        if not _as_bool(owner_input.get(field)):
            return True
    return False


def _build_owner_execution_card(owner_input: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "final_rehearsal_card_type": "INERT_PROTECTED_DEMO_ORDER_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_ONLY",
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "instrument": "EUR_USD",
        "side": "BUY",
        "demo_environment_only": True,
        "broker_environment_observed": "DEMO_OR_PRACTICE_ONLY",
        "order_type_selection": "MARKET",
        "owner_control_required": True,
        "final_rehearsal_required": True,
        "final_rehearsal_reviewed": True,
        "owner_execution_card_required": True,
        "owner_execution_card_prepared": True,
        "explicit_owner_execution_packet_review_required": True,
        "credential_handling_review_required": True,
        "broker_connection_review_required": True,
        "broker_api_connection_authorized_now": _as_false(owner_input.get("broker_api_connection_authorized_now")),
        "credential_access_authorized_now": _as_false(owner_input.get("credential_access_authorized_now")),
        "order_submission_authorized_now": _as_false(owner_input.get("order_submission_authorized_now")),
        "execution_command_authorized_now": _as_false(owner_input.get("execution_command_authorized_now")),
        "max_orders_per_signal": 1,
        "max_open_positions": _safe_value(owner_input.get("max_open_positions"), 1),
        "current_open_position_count_max": 1,
        "current_same_signal_order_count_max": 1,
        "pending_order_count_max": 1,
        "stop_loss_required": True,
        "take_profit_required": True,
        "minimum_reward_to_risk": 1.20,
        "max_risk_per_trade_percent": 0.25,
        "max_daily_loss_percent": 1.00,
        "max_weekly_loss_percent": 2.00,
        "spread_guard_reviewed": _as_bool(owner_input.get("spread_guard_review")),
        "slippage_guard_reviewed": _as_bool(owner_input.get("slippage_guard_review")),
        "market_open_reviewed": _as_bool(owner_input.get("market_open_review")),
        "idempotency_key_required": _as_bool(owner_input.get("idempotency_key_required")),
        "stale_price_block_required": _as_bool(owner_input.get("stale_price_block_required")),
        "duplicate_order_block_required": _as_bool(owner_input.get("duplicate_order_block_required")),
        "kill_switch_verified": _as_bool(owner_input.get("kill_switch_verification")),
        "audit_record_required": _as_bool(owner_input.get("audit_record_ready")),
        "final_owner_execution_card_review_required": True,
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "execution_command_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
    }


def _build_checks(owner_input: Dict[str, Any], p13_ready: bool) -> Dict[str, bool]:
    current_open_position_count = _safe_value(owner_input.get("current_open_position_count"), 0)
    current_same_signal_order_count = _safe_value(owner_input.get("current_same_signal_order_count"), 0)
    pending_order_count = _safe_value(owner_input.get("pending_order_count"), 0)
    max_open_positions = _safe_value(owner_input.get("max_open_positions"), 1)
    max_risk_per_trade_percent = _as_float(owner_input.get("max_risk_per_trade_percent"), 0.0)
    daily_realized_loss_percent = _as_float(owner_input.get("daily_realized_loss_percent"), 0.0)
    weekly_realized_loss_percent = _as_float(owner_input.get("weekly_realized_loss_percent"), 0.0)

    checks = {
        "p13_release_review_ready": p13_ready,
        "final_rehearsal_owner_execution_card_created": p13_ready and all([
            _as_bool(owner_input.get("final_rehearsal_reviewed")),
            _as_bool(owner_input.get("owner_execution_card_prepared")),
            _as_bool(owner_input.get("final_owner_execution_card_review")),
            _as_bool(owner_input.get("explicit_owner_execution_packet_review_required")),
        ]),
        "owner_decision_approved": owner_input.get("owner_decision") == "APPROVE_DEMO_INTENT",
        "candidate_id_confirmed": owner_input.get("candidate_id") == CANDIDATE_ID,
        "instrument_is_eur_usd": owner_input.get("intended_instrument_confirmation") == "EUR_USD",
        "side_is_buy": owner_input.get("intended_side_confirmation") == "BUY",
        "demo_environment_only": owner_input.get("demo_account_marker") == "DEMO_ONLY",
        "order_type_selected": owner_input.get("order_type_selection") == "MARKET",
        "owner_control_required": _as_bool(owner_input.get("owner_control_required")),
        "final_rehearsal_required": _as_bool(owner_input.get("protected_final_rehearsal_required")),
        "final_rehearsal_reviewed": _as_bool(owner_input.get("final_rehearsal_reviewed")),
        "owner_execution_card_required": _as_bool(owner_input.get("owner_execution_card_required")),
        "owner_execution_card_prepared": _as_bool(owner_input.get("owner_execution_card_prepared")),
        "explicit_owner_execution_packet_review_required": _as_bool(owner_input.get("explicit_owner_execution_packet_review_required")),
        "credential_handling_review_marked": _as_bool(owner_input.get("credential_handling_review")),
        "broker_connection_review_marked": _as_bool(owner_input.get("broker_connection_review")),
        "broker_api_connection_authorized_now_is_false": _as_false(owner_input.get("broker_api_connection_authorized_now")),
        "credential_access_authorized_now_is_false": _as_false(owner_input.get("credential_access_authorized_now")),
        "order_submission_authorized_now_is_false": _as_false(owner_input.get("order_submission_authorized_now")),
        "execution_command_authorized_now_is_false": _as_false(owner_input.get("execution_command_authorized_now")),
        "execution_command_authorized_is_false": _as_false(owner_input.get("execution_command_authorized")),
        "max_orders_per_signal_one": _safe_value(owner_input.get("max_orders_per_signal"), 1) == 1
        if owner_input.get("max_orders_per_signal") is not None
        else True,
        "max_open_positions_one": max_open_positions == 1,
        "current_position_count_within_limit": current_open_position_count <= max_open_positions,
        "same_signal_order_count_within_limit": current_same_signal_order_count <= _safe_value(owner_input.get("max_orders_per_signal"), 1),
        "pending_order_count_within_limit": pending_order_count <= 1,
        "stop_loss_reviewed": _as_bool(owner_input.get("stop_loss_review")),
        "take_profit_reviewed": _as_bool(owner_input.get("take_profit_review")),
        "reward_to_risk_reviewed": _as_bool(owner_input.get("reward_to_risk_review")),
        "risk_per_trade_within_limit": max_risk_per_trade_percent <= 0.25,
        "daily_loss_within_limit": daily_realized_loss_percent <= 1.00,
        "weekly_loss_within_limit": weekly_realized_loss_percent <= 2.00,
        "spread_guard_reviewed": _as_bool(owner_input.get("spread_guard_review")),
        "slippage_guard_reviewed": _as_bool(owner_input.get("slippage_guard_review")),
        "market_open_reviewed": _as_bool(owner_input.get("market_open_review")),
        "idempotency_key_required": _as_bool(owner_input.get("idempotency_key_required")),
        "stale_price_block_required": _as_bool(owner_input.get("stale_price_block_required")),
        "duplicate_order_block_required": _as_bool(owner_input.get("duplicate_order_block_required")),
        "kill_switch_verified": _as_bool(owner_input.get("kill_switch_verification")),
        "audit_record_required": _as_bool(owner_input.get("audit_record_ready")),
        "final_owner_execution_card_review_marked": _as_bool(owner_input.get("final_owner_execution_card_review")),
        "demo_order_placement_authorized": _as_false(owner_input.get("demo_order_placement_authorized")),
        "broker_api_access_authorized": _as_false(owner_input.get("broker_api_access_authorized")),
        "credential_access_authorized": _as_false(owner_input.get("credential_access_authorized")),
        "live_trading_blocked": _as_bool(owner_input.get("live_trading_blocked"))
        if owner_input.get("live_trading_blocked") is not None
        else True,
        "money_movement_blocked": _as_bool(owner_input.get("money_movement_blocked"))
        if owner_input.get("money_movement_blocked") is not None
        else True,
        "no_autonomy_approval": _as_bool(owner_input.get("no_autonomy_approval"))
        if owner_input.get("no_autonomy_approval") is not None
        else True,
    }

    return checks


def _build_result(
    owner_input: Dict[str, Any] | None,
    p13_status: str,
    p13_observed: str,
    protected_command_status: str,
    checks: Dict[str, bool],
    status: str,
    owner_status: str,
    next_lane: str,
    post_score: int,
    final_card: Dict[str, Any],
) -> Dict[str, Any]:
    passed_requirements = [k for k, v in checks.items() if v]
    failed_requirements = [k for k, v in checks.items() if not v]

    result: Dict[str, Any] = {
        "campaign_id": CAMPAIGN_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_name": CANDIDATE_NAME,
        "input_score": 100 if owner_input else 100,
        "post_p14_score": post_score,
        "p13_release_review_status": p13_status,
        "p13_release_review_status_observed": p13_observed,
        "protected_command_release_status": protected_command_status,
        "protected_command_release_status_observed": protected_command_status,
        "p14_final_rehearsal_status": status,
        "owner_execution_card_status": owner_status,
        "next_required_lane": next_lane,
        "final_rehearsal_owner_execution_card_created": bool(final_card),
        "final_rehearsal_owner_execution_card": final_card,
        "final_rehearsal_checks": checks,
        "passed_requirements": passed_requirements,
        "failed_requirements": failed_requirements,
        "blocked_actions": [
            "demo-order placement",
            "demo-order placement authorization",
            "live trading",
            "broker/API access",
            "credential access",
            "execution command execution",
            "execution command authorization",
            "money movement",
            "autonomy approval",
        ],
        "forbidden_actions": [
            "demo-order placement",
            "live trading",
            "broker/API access",
            "credential access",
            "execution command execution",
            "money movement",
            "autonomy approval",
        ],
        "demo_order_placement_authorized": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "execution_command_authorized": False,
        "live_trading_blocked": True,
        "money_movement_blocked": True,
        "no_autonomy_approval": True,
        "trader_meaning": (
            "AIOS is creating a protected demo-order command final rehearsal and owner execution card "
            "artifact for the EUR/USD buy setup so it can verify final owner-card readiness before "
            "explicit protected demo-order execution packet review is considered."
        ),
        "final_owner_sentence": _final_owner_sentence(
            owner_input=owner_input,
            status=status,
            next_lane=next_lane,
        ),
    }

    if owner_input is None:
        result["input_score"] = 100

    return result


def _final_owner_sentence(
    *,
    owner_input: Dict[str, Any] | None,
    status: str,
    next_lane: str,
) -> str:
    if owner_input is None:
        return (
            "P14 is waiting for validated owner input and no broker/API, credential, "
            "demo-order, or execution-command authority is authorized."
        )
    if status == P14_FINAL_REHEARSAL_READY:
        return (
            "Protected demo-order final rehearsal and owner execution card is prepared in inert "
            "form for explicit P15 owner review. Broker/API access, credentials, demo-order "
            "placement, execution command, live trading, money movement, and autonomy remain "
            "blocked."
        )
    if status == P14_FINAL_REHEARSAL_FAILED_REPAIR_REQUIRED:
        return (
            "P14 final rehearsal failed repair checks and remains blocked from P15 route. "
            "No broker/API, credential, demo-order, or execution-command authority is authorized."
        )
    if status == P14_FINAL_REHEARSAL_BLOCKED_P13_REPAIR_REQUIRED:
        return (
            f"P14 is blocked waiting for prior P13 release review repair. Next required lane is {next_lane}. "
            "No broker/API, credential, demo-order, or execution-command authority is authorized."
        )
    return (
        "P14 is waiting for validated owner input and no broker/API, credential, demo-order, "
        "or execution-command authority is authorized."
    )


def evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(
    owner_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if owner_input is None:
        checks = {
            "p13_release_review_ready": False,
            "final_rehearsal_owner_execution_card_created": False,
            "owner_decision_approved": False,
            "candidate_id_confirmed": False,
            "instrument_is_eur_usd": False,
            "side_is_buy": False,
            "demo_environment_only": False,
            "order_type_selected": False,
            "owner_control_required": False,
            "final_rehearsal_required": False,
            "final_rehearsal_reviewed": False,
            "owner_execution_card_required": False,
            "owner_execution_card_prepared": False,
            "explicit_owner_execution_packet_review_required": False,
            "credential_handling_review_marked": False,
            "broker_connection_review_marked": False,
            "broker_api_connection_authorized_now_is_false": True,
            "credential_access_authorized_now_is_false": True,
            "order_submission_authorized_now_is_false": True,
            "execution_command_authorized_now_is_false": True,
            "execution_command_authorized_is_false": True,
            "max_orders_per_signal_one": True,
            "max_open_positions_one": True,
            "current_position_count_within_limit": True,
            "same_signal_order_count_within_limit": True,
            "pending_order_count_within_limit": True,
            "stop_loss_reviewed": False,
            "take_profit_reviewed": False,
            "reward_to_risk_reviewed": False,
            "risk_per_trade_within_limit": False,
            "daily_loss_within_limit": False,
            "weekly_loss_within_limit": False,
            "spread_guard_reviewed": False,
            "slippage_guard_reviewed": False,
            "market_open_reviewed": False,
            "idempotency_key_required": False,
            "stale_price_block_required": False,
            "duplicate_order_block_required": False,
            "kill_switch_verified": False,
            "audit_record_required": False,
            "final_owner_execution_card_review_marked": False,
            "demo_order_placement_authorized": False,
            "broker_api_access_authorized": False,
            "credential_access_authorized": False,
            "live_trading_blocked": True,
            "money_movement_blocked": True,
            "no_autonomy_approval": True,
        }
        return _build_result(
            owner_input=None,
            p13_status="P13_RELEASE_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED",
            p13_observed="P13_RELEASE_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED",
            protected_command_status="NOT_READY",
            checks=checks,
            status=P14_FINAL_REHEARSAL_BLOCKED_OWNER_INPUT_REQUIRED,
            owner_status=NOT_READY,
            next_lane="P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT",
            post_score=100,
            final_card={},
        )

    safe_input = dict(owner_input)

    p13_result = evaluate_c1_owner_run_protected_demo_order_command_release_review(safe_input)
    p13_status_observed = str(p13_result.get("p13_release_review_status", ""))
    protected_command_status_observed = str(
        p13_result.get("protected_command_release_status", "NOT_READY")
    )

    p13_ready = (
        p13_status_observed == REQUIRED_P13_STATUS
        and protected_command_status_observed == "P14_READY"
    )

    if _has_forbidden_field(safe_input) or _has_invalid_authorization_true(safe_input):
        checks = _build_checks(safe_input, p13_ready=False)
        checks["p13_release_review_ready"] = p13_ready
        return _build_result(
            owner_input=safe_input,
            p13_status=p13_status_observed or "P13_RELEASE_REVIEW_BLOCKED_P13_REPAIR_REQUIRED",
            p13_observed=p13_status_observed or "P13_RELEASE_REVIEW_BLOCKED_P13_REPAIR_REQUIRED",
            protected_command_status=protected_command_status_observed,
            checks=checks,
            status=P14_FINAL_REHEARSAL_FAILED_REPAIR_REQUIRED,
            owner_status=NOT_READY,
            next_lane="P14_FINAL_REHEARSAL_REPAIR_REVIEW",
            post_score=80,
            final_card={},
        )

    if _missing_required_marker(safe_input):
        checks = _build_checks(safe_input, p13_ready)
        checks["p13_release_review_ready"] = p13_ready
        return _build_result(
            owner_input=safe_input,
            p13_status=p13_status_observed or "P13_RELEASE_REVIEW_FAILED_REPAIR_REQUIRED",
            p13_observed=p13_status_observed or "P13_RELEASE_REVIEW_FAILED_REPAIR_REQUIRED",
            protected_command_status=protected_command_status_observed,
            checks=checks,
            status=P14_FINAL_REHEARSAL_FAILED_REPAIR_REQUIRED,
            owner_status=NOT_READY,
            next_lane="P14_FINAL_REHEARSAL_REPAIR_REVIEW",
            post_score=80,
            final_card={},
        )

    checks = _build_checks(safe_input, p13_ready)

    if not p13_ready:
        return _build_result(
            owner_input=safe_input,
            p13_status=p13_status_observed or "P13_RELEASE_REVIEW_BLOCKED_P13_REPAIR_REQUIRED",
            p13_observed=p13_status_observed or "P13_RELEASE_REVIEW_BLOCKED_P13_REPAIR_REQUIRED",
            protected_command_status=protected_command_status_observed,
            checks=checks,
            status=P14_FINAL_REHEARSAL_BLOCKED_P13_REPAIR_REQUIRED,
            owner_status=NOT_READY,
            next_lane="P13_COMMAND_RELEASE_REVIEW_REPAIR",
            post_score=80,
            final_card={},
        )

    if not all(checks.values()):
        return _build_result(
            owner_input=safe_input,
            p13_status=p13_status_observed,
            p13_observed=p13_status_observed,
            protected_command_status=protected_command_status_observed,
            checks=checks,
            status=P14_FINAL_REHEARSAL_FAILED_REPAIR_REQUIRED,
            owner_status=NOT_READY,
            next_lane="P14_FINAL_REHEARSAL_REPAIR_REVIEW",
            post_score=80,
            final_card={},
        )

    final_card = _build_owner_execution_card(safe_input)
    return _build_result(
        owner_input=safe_input,
        p13_status=REQUIRED_P13_STATUS,
        p13_observed=p13_status_observed,
        protected_command_status="P14_READY",
        checks=checks,
        status=P14_FINAL_REHEARSAL_READY,
        owner_status=P15_READY,
        next_lane="P15_EXPLICIT_OWNER_APPROVED_PROTECTED_DEMO_ORDER_EXECUTION_PACKET_REVIEW",
        post_score=100,
        final_card=final_card,
    )


def render_owner_report(result: Dict[str, Any]) -> str:
    checks = result["final_rehearsal_checks"]
    pass_list = result["passed_requirements"]
    fail_list = result["failed_requirements"]
    blocked = result["blocked_actions"]

    lines = [
        "# AIOS Forex C1 Protected Demo Order Command Final Rehearsal Owner Execution Card V1 Report",
        "",
        "## Campaign Scope",
        "",
        f"Campaign ID: `{result['campaign_id']}`",
        f"Candidate: `{result['candidate_id']}` / `{result['candidate_name']}`",
        "",
        "## Trader Meaning",
        "",
        result["trader_meaning"],
        "",
        "## P13 Entry Condition",
        "",
        f"- p13_release_review_status: `{result['p13_release_review_status']}`",
        f"- p13_release_review_status_observed: `{result['p13_release_review_status_observed']}`",
        f"- protected_command_release_status_observed: `{result['protected_command_release_status_observed']}`",
        "",
        "## Final Rehearsal Owner Execution Card",
        "",
    ]

    final_card = result["final_rehearsal_owner_execution_card"]
    if final_card:
        for key, value in final_card.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- not prepared yet")

    lines.extend(
        [
            "",
            "## Final Rehearsal Checks",
            "",
            "| field | value |",
            "|---|---|",
        ]
    )
    for key, value in checks.items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Passed Requirements",
            "",
        ]
    )
    lines.extend([f"- {key}" for key in pass_list] or ["- none"])

    lines.extend(
        [
            "",
            "## Failed Requirements",
            "",
        ]
    )
    lines.extend([f"- {key}" for key in fail_list] or ["- none"])

    lines.extend(
        [
            "",
            "## Blocked Actions",
            "",
        ]
    )
    lines.extend([f"- {action}" for action in blocked])

    lines.extend(
        [
            "",
            "## P15 Readiness Decision",
            "",
            f"- p14_final_rehearsal_status: `{result['p14_final_rehearsal_status']}`",
            f"- owner_execution_card_status: `{result['owner_execution_card_status']}`",
            f"- post_p14_score: `{result['post_p14_score']}`",
            f"- next_required_lane: `{result['next_required_lane']}`",
            f"- demo_order_placement_authorized: `{result['demo_order_placement_authorized']}`",
            f"- broker_api_access_authorized: `{result['broker_api_access_authorized']}`",
            f"- credential_access_authorized: `{result['credential_access_authorized']}`",
            f"- execution_command_authorized: `{result['execution_command_authorized']}`",
            f"- live_trading_blocked: `{result['live_trading_blocked']}`",
            f"- money_movement_blocked: `{result['money_movement_blocked']}`",
            f"- no_autonomy_approval: `{result['no_autonomy_approval']}`",
            "",
            "## Next Required Lane",
            "",
            f"{result['next_required_lane']}",
            "",
            "## What This Completes",
            "",
            "- creates an inert P14 final rehearsal and owner execution card layer",
            "- verifies final rehearsal controls for EUR/USD BUY under demo-only conditions",
            "- routes a passing result to P15 explicit owner-approved protected demo-order execution packet review",
            "- keeps demo-order placement, broker/API, credentials, execution command, live trading, money movement, and autonomy blocked",
            "",
            "## What This Does Not Approve",
            "",
            "- demo-order placement",
            "- live trading",
            "- broker/API connection authority",
            "- credential access",
            "- execution command",
            "- money movement",
            "- 22/6 autonomy approval",
            "",
            "## Final Owner Sentence",
            "",
            result["final_owner_sentence"],
            "",
        ]
    )
    return "\n".join(lines)


def render_next_action_queue(result: Dict[str, Any]) -> str:
    checks = result["final_rehearsal_checks"]
    pass_list = result["passed_requirements"]
    fail_list = result["failed_requirements"]

    lines = [
        "# AIOS Forex C1 Protected Demo Order Command Final Rehearsal Owner Execution Card Next Action Queue V1",
        "",
        "## Purpose",
        "",
        "This queue records the next action after the P14 protected demo-order command final rehearsal and owner execution card step.",
        "",
        "## P14 Final Rehearsal Status",
        "",
        f"{result['p14_final_rehearsal_status']}",
        "",
        "## Owner Execution Card Status",
        "",
        f"{result['owner_execution_card_status']}",
        "",
        "## Passed Requirements",
        "",
    ]
    lines.extend([f"- {item}" for item in pass_list] or ["- none"])

    lines.extend(
        [
            "",
            "## Failed Requirements",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in fail_list] or ["- none"])

    lines.extend(
        [
            "",
            "## Next Required Lane",
            "",
            result["next_required_lane"],
            "",
            "## Required Next Actions",
            "",
        ]
    )

    default_actions = [
        "supply sanitized owner input through P6B",
        "validate owner input through P6C",
        "build final review card through P6D",
        "rerun P7 dry-run/mock rehearsal",
        "rerun P8 broker/account readiness bridge",
        "rerun P9 protected execution gate review",
        "rerun P10 owner-run handoff preparation",
        "rerun P11 protected owner-run packet review",
        "rerun P12 protected command packet preparation",
        "rerun P13 protected command release review",
        "rerun P14 protected final rehearsal and owner execution card",
        "keep broker/API access blocked",
        "keep credentials blocked",
        "keep demo-order placement blocked",
        "keep execution command blocked",
    ]

    ready_actions = [
        "start P15 explicit owner-approved protected demo-order execution packet review",
        "keep broker/API access blocked until P15 explicitly reviews final connection requirements",
        "keep credentials blocked until P15 explicitly reviews credential-handling requirements",
        "keep demo-order placement blocked until a later separately approved owner-run execution packet",
        "keep execution command blocked until a later separately approved owner-run execution packet",
        "keep live trading blocked",
        "keep money movement blocked",
    ]

    if result["p14_final_rehearsal_status"] == P14_FINAL_REHEARSAL_READY:
        lines.extend([f"- {item}" for item in ready_actions])
    else:
        lines.extend([f"- {item}" for item in default_actions])

    remaining_blocks = [
        "demo-order placement remains blocked",
        "execution command remains blocked",
        "live trading remains blocked",
        "broker/API access remains blocked",
        "credentials remain blocked",
        "money movement remains blocked",
    ]
    if result["p14_final_rehearsal_status"] == P14_FINAL_REHEARSAL_READY:
        remaining_blocks.append("owner execution remains blocked until explicit P15 review completion")

    lines.extend(
        [
            "",
            "## Remaining Blocks",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in remaining_blocks])
    lines.extend(
        [
            "",
            "## Final Owner Sentence",
            "",
            result["final_owner_sentence"],
            "",
            "",
            "Final check values:",
        ]
    )
    lines.extend([f"- {k}: `{v}`" for k, v in checks.items()])
    return "\n".join(lines)
