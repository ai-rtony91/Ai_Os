"""Flow 1 active execution authority module for runtime and SOS contract handoff."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "Reports" / "forex_delivery"
JSON_REPORT_PATH = (
    REPORT_DIR / "AIOS_FOREX_FLOW1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN_V2.json"
)
REPORT_PATH = (
    REPORT_DIR
    / "AIOS_FOREX_FLOW1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN_V2_REPORT.md"
)
QUEUE_PATH = (
    REPORT_DIR
    / "AIOS_FOREX_FLOW1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN_NEXT_ACTION_QUEUE_V2.md"
)
HANDOFF_PATH = (
    REPORT_DIR / "AIOS_FOREX_FLOW1_TO_FLOW2_ACTIVE_SUPERVISED_DEMO_EVIDENCE_HANDOFF_V2.md"
)

FLOW_2 = "FLOW_2_SUPERVISED_DEMO_EXECUTION_EVIDENCE_AND_COUNTDOWN_CAPTURE"
OWNER_LIVE_CAPITAL_INTENT_USD = 1000
TARGET_RETURN_BAND = "100_TO_120_PERCENT"
RUNTIME_OBJECTIVE = "22_HOURS_PER_DAY_6_DAYS_PER_WEEK"

DEFAULT_REQUESTED_MAX_OPEN_POSITIONS = 4
DEFAULT_REQUESTED_QUANTITY_SCALE = 4.0
RISK_PER_TRADE_PERCENT_DEFAULT = 0.25
MAX_AGGREGATE_OPEN_RISK_PERCENT_DEFAULT = 1.00
MAX_DAILY_LOSS_PERCENT_DEFAULT = 1.00
MAX_WEEKLY_LOSS_PERCENT_DEFAULT = 2.00
MAX_DRAWDOWN_STOP_PERCENT_DEFAULT = 10.00
MAX_MARGIN_UTILIZATION_PERCENT_DEFAULT = 25.00

FORBIDDEN_FIELDS = {
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
}

AUTHORIZATION_FIELDS = {
    "broker_api_access_authorized",
    "credential_access_authorized",
    "demo_order_placement_authorized",
    "live_trading_authorized",
    "execution_command_authorized",
    "runtime_22h6d_activated",
    "vacation_mode_activated",
    "autonomous_trading_authorized",
    "money_movement_authorized",
    "broker_connection_authorized",
    "order_submission_authorized",
}

BANNED_OUTPUT_TOKENS = [
    "TODO",
    "TBD",
    "@filename",
    "probably",
    "roughly",
    "approximately",
    "I estimate",
    "guaranteed profit",
    "guaranteed returns",
    "100-120 percent verified",
    "100–120% verified",
    "target achieved without evidence",
    "live ready",
    "autonomous trading ready",
    "vacation mode active",
    "22h6d active",
    "22h/6d active",
    "live profitable week proven",
    "broker connected",
    "credentials loaded",
    "order placed",
    "trade executed",
    "demo trade executed",
    "live trade executed",
    "real order",
    "real trade",
    "approval granted",
    "API key accepted",
    "credentials accepted",
    "account id accepted",
    "broker connected successfully",
    "money machine",
    "mean machine",
]


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _safe_str(value: Any, default: str) -> str:
    if value is None:
        return default
    return str(value).strip().upper()


def _milestone_alert(cumulative_return_percent: float) -> str:
    if cumulative_return_percent >= 120:
        return "TARGET_120_REACHED_HIGH_PRIORITY_SOS_ALERT"
    if cumulative_return_percent >= 100:
        return "TARGET_100_REACHED_HIGH_PRIORITY_SOS_ALERT"
    if cumulative_return_percent >= 75:
        return "TARGET_75_PROGRESS_ALERT"
    if cumulative_return_percent >= 50:
        return "TARGET_50_PROGRESS_ALERT"
    if cumulative_return_percent >= 25:
        return "TARGET_25_PROGRESS_ALERT"
    return "TARGET_IN_PROGRESS_NO_MILESTONE_ALERT"


def _drawdown_alert(current_drawdown_percent: float) -> str:
    if current_drawdown_percent >= 10:
        return "DRAWDOWN_CRITICAL_SOS_STOP_REVIEW"
    if current_drawdown_percent >= 5:
        return "DRAWDOWN_WARNING_OWNER_REVIEW"
    return "DRAWDOWN_WITHIN_CONTROL"


def _base_result() -> Dict[str, Any]:
    return {
        "flow1_status": "FLOW1_BLOCKED_OWNER_INPUT_REQUIRED",
        "flow1_mode": "PAUSE_READY",
        "flow1_repo_gate_active": True,
        "owner_live_capital_intent_usd": OWNER_LIVE_CAPITAL_INTENT_USD,
        "requested_max_open_positions": DEFAULT_REQUESTED_MAX_OPEN_POSITIONS,
        "requested_quantity_scale": DEFAULT_REQUESTED_QUANTITY_SCALE,
        "configured_max_open_positions": DEFAULT_REQUESTED_MAX_OPEN_POSITIONS,
        "calculated_max_open_positions": 0,
        "available_equity": 0.0,
        "baseline_equity": 0.0,
        "current_equity": 0.0,
        "risk_per_trade_percent": RISK_PER_TRADE_PERCENT_DEFAULT,
        "max_aggregate_open_risk_percent": MAX_AGGREGATE_OPEN_RISK_PERCENT_DEFAULT,
        "max_margin_utilization_percent": MAX_MARGIN_UTILIZATION_PERCENT_DEFAULT,
        "margin_capacity_status": "MARGIN_CAPACITY_BLOCKED",
        "exposure_capacity_status": "EXPOSURE_CAPACITY_BLOCKED",
        "position_capacity_status": "WAITING_FOR_BASELINE_EQUITY",
        "position_capacity_reason": "waiting_for_baseline_equity",
        "final_position_capacity": 0,
        "risk_limited_capacity": 0,
        "margin_limited_capacity": 0,
        "remaining_position_slots": 0,
        "aggregate_risk_budget_amount": 0.0,
        "margin_budget_amount": 0.0,
        "baseline_equity_source": "OWNER_INPUT_OR_BROKER_DEMO_OR_LIVE_SNAPSHOT",
        "hardcoded_10000_baseline_forbidden": True,
        "target_return_band": TARGET_RETURN_BAND,
        "target_return_claim_status": "TARGET_NOT_YET_VERIFIED",
        "target_equity_100_percent": None,
        "target_equity_120_percent": None,
        "cumulative_profit_amount": None,
        "cumulative_return_percent": None,
        "remaining_to_100_percent": None,
        "remaining_to_120_percent": None,
        "target_100_reached": False,
        "target_120_reached": False,
        "milestone_alert": "TARGET_IN_PROGRESS_NO_MILESTONE_ALERT",
        "drawdown_alert": "DRAWDOWN_WITHIN_CONTROL",
        "profit_return_countdown_status": "BASELINE_EQUITY_REQUIRED",
        "profit_return_rate_status": "COUNTDOWN_NOT_ACTIVE_BASELINE_REQUIRED",
        "runtime_objective": RUNTIME_OBJECTIVE,
        "runtime_status": "GATED_PENDING_SUPERVISED_EVIDENCE",
        "vacation_mode_status": "TARGET_DEFINED_GATE_PENDING",
        "sos_alert_integration_status": "REQUIRED_GATE_PENDING",
        "execution_authority_status": "BLOCKED_PENDING_OWNER_INPUT",
        "flow2_handoff_status": "NOT_READY",
        "next_required_flow": "FLOW_1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN",
        "next_required_action": "OWNER_SUPPLY_SANITIZED_FLOW1_INPUT",
        "publish_status": "NOT_READY_VALIDATION_REQUIRED",
        "flow1_bridge_map": [],
        "flow1_action": "CONTINUE",
        "current_drawdown_percent": 0.0,
        "daily_realized_loss_percent": 0.0,
        "weekly_realized_loss_percent": 0.0,
        "open_trade_count": 0,
        "closed_trade_count": 0,
        "max_open_positions": DEFAULT_REQUESTED_MAX_OPEN_POSITIONS,
        "target_return_band_acknowledged": False,
        "profit_countdown_acknowledged": False,
        "runtime_objective_acknowledged": False,
        "vacation_mode_target_acknowledged": False,
        "sos_alerts_acknowledged": False,
        "risk_controls_acknowledged": False,
        "idempotency_acknowledged": False,
        "no_duplicate_order_acknowledged": False,
        "stale_price_guard_acknowledged": False,
        "kill_switch_acknowledged": False,
        "owner_supervised_demo_execution_acknowledged": False,
        "flow2_evidence_capture_acknowledged": False,
        "demo_account_marker": "UNKNOWN",
        "broker_environment": "UNKNOWN",
        "kill_switch_state": False,
        "owner_attestation": False,
    }


def _default_authorization_flags() -> Dict[str, bool]:
    return {field: False for field in AUTHORIZATION_FIELDS}


def _positive_or_default(value: Any, default: float) -> float:
    parsed = _safe_float(value, default)
    return parsed if parsed > 0 else default


def calculate_position_capacity(owner_input: Dict[str, Any]) -> Dict[str, Any]:
    requested_max_open_positions = _safe_int(
        owner_input.get("requested_max_open_positions"),
        DEFAULT_REQUESTED_MAX_OPEN_POSITIONS,
    )
    if requested_max_open_positions < 1:
        requested_max_open_positions = DEFAULT_REQUESTED_MAX_OPEN_POSITIONS

    configured_max_open_positions = _safe_int(
        owner_input.get("configured_max_open_positions"),
        requested_max_open_positions,
    )
    if configured_max_open_positions < 1:
        configured_max_open_positions = requested_max_open_positions

    max_open_positions = _safe_int(owner_input.get("max_open_positions"), configured_max_open_positions)
    if max_open_positions < 0:
        max_open_positions = 0

    open_trade_count = _safe_int(owner_input.get("open_trade_count"), 0)
    if open_trade_count < 0:
        open_trade_count = 0

    risk_per_trade_percent = _safe_float(
        owner_input.get("risk_per_trade_percent"),
        RISK_PER_TRADE_PERCENT_DEFAULT,
    )
    if risk_per_trade_percent < 0:
        risk_per_trade_percent = RISK_PER_TRADE_PERCENT_DEFAULT

    max_aggregate_open_risk_percent = _safe_float(
        owner_input.get("max_aggregate_open_risk_percent"),
        MAX_AGGREGATE_OPEN_RISK_PERCENT_DEFAULT,
    )
    if max_aggregate_open_risk_percent < 0:
        max_aggregate_open_risk_percent = MAX_AGGREGATE_OPEN_RISK_PERCENT_DEFAULT

    max_margin_utilization_percent = _safe_float(
        owner_input.get("max_margin_utilization_percent"),
        MAX_MARGIN_UTILIZATION_PERCENT_DEFAULT,
    )
    if max_margin_utilization_percent < 0:
        max_margin_utilization_percent = MAX_MARGIN_UTILIZATION_PERCENT_DEFAULT

    available_equity = _positive_or_default(owner_input.get("available_equity"), 0.0)
    if available_equity <= 0:
        available_equity = _positive_or_default(owner_input.get("current_equity"), 0.0)
    if available_equity <= 0:
        available_equity = _positive_or_default(owner_input.get("baseline_equity"), 0.0)

    estimated_margin_per_position = _positive_or_default(
        owner_input.get("estimated_margin_per_position"),
        available_equity * 0.05,
    )
    estimated_risk_amount_per_position = _positive_or_default(
        owner_input.get("estimated_risk_amount_per_position"),
        available_equity * (risk_per_trade_percent / 100.0),
    )

    current_drawdown_percent = _safe_float(owner_input.get("current_drawdown_percent"), 0.0)
    kill_switch_state = _safe_bool(owner_input.get("kill_switch_state"))

    remaining_position_slots = max(0, max_open_positions - open_trade_count)

    aggregate_risk_budget_amount = available_equity * (max_aggregate_open_risk_percent / 100.0)
    margin_budget_amount = available_equity * (max_margin_utilization_percent / 100.0)

    risk_limited_capacity = (
        math.floor(aggregate_risk_budget_amount / estimated_risk_amount_per_position)
        if estimated_risk_amount_per_position > 0
        else 0
    )
    margin_limited_capacity = (
        math.floor(margin_budget_amount / estimated_margin_per_position)
        if estimated_margin_per_position > 0
        else 0
    )

    if risk_limited_capacity < 0:
        risk_limited_capacity = 0
    if margin_limited_capacity < 0:
        margin_limited_capacity = 0

    final_position_capacity = min(
        remaining_position_slots,
        risk_limited_capacity,
        margin_limited_capacity,
        requested_max_open_positions,
        configured_max_open_positions,
    )

    blockers = []
    if kill_switch_state:
        blockers.append("kill_switch_active")
    if current_drawdown_percent >= MAX_DRAWDOWN_STOP_PERCENT_DEFAULT:
        blockers.append("drawdown_limit_reached")
    if available_equity <= 0:
        blockers.append("available_equity_insufficient")
    if estimated_risk_amount_per_position <= 0:
        blockers.append("risk_amount_invalid")
    if estimated_margin_per_position <= 0:
        blockers.append("margin_amount_invalid")

    if blockers:
        final_position_capacity = 0

    if final_position_capacity < 0:
        final_position_capacity = 0

    if final_position_capacity == 4:
        position_capacity_status = "POSITION_CAPACITY_READY_UP_TO_4"
    elif final_position_capacity > 0:
        position_capacity_status = "POSITION_CAPACITY_READY_PARTIAL"
    else:
        position_capacity_status = "POSITION_CAPACITY_BLOCKED"

    if blockers:
        reason = "blocked_by_" + "_".join(blockers)
    elif position_capacity_status == "POSITION_CAPACITY_READY_UP_TO_4":
        reason = "capacity_allows_up_to_4_positions"
    elif position_capacity_status == "POSITION_CAPACITY_READY_PARTIAL":
        reason = "capacity_limited_by_risk_margin_position_slots"
    else:
        reason = "position_capacity_blocked_by_runtime_controls"

    margin_capacity_status = (
        "MARGIN_CAPACITY_READY" if margin_limited_capacity > 0 else "MARGIN_CAPACITY_BLOCKED"
    )
    exposure_capacity_status = (
        "EXPOSURE_CAPACITY_READY" if risk_limited_capacity > 0 else "EXPOSURE_CAPACITY_BLOCKED"
    )

    return {
        "requested_max_open_positions": requested_max_open_positions,
        "configured_max_open_positions": configured_max_open_positions,
        "max_open_positions": max_open_positions,
        "final_position_capacity": final_position_capacity,
        "position_capacity_status": position_capacity_status,
        "position_capacity_reason": reason,
        "risk_limited_capacity": risk_limited_capacity,
        "margin_limited_capacity": margin_limited_capacity,
        "remaining_position_slots": remaining_position_slots,
        "aggregate_risk_budget_amount": aggregate_risk_budget_amount,
        "margin_budget_amount": margin_budget_amount,
        "risk_per_trade_percent": risk_per_trade_percent,
        "max_aggregate_open_risk_percent": max_aggregate_open_risk_percent,
        "max_margin_utilization_percent": max_margin_utilization_percent,
        "calculated_max_open_positions": final_position_capacity,
        "available_equity": available_equity,
        "estimated_margin_per_position": estimated_margin_per_position,
        "estimated_risk_amount_per_position": estimated_risk_amount_per_position,
        "margin_capacity_status": margin_capacity_status,
        "exposure_capacity_status": exposure_capacity_status,
    }


def build_flow1_bridge_map(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "island_name": "flow1_position_capacity_bridge",
            "missing_capability": "Position capacity is not fully validated against risk, margin, and open-slot limits.",
            "why_it_blocks_profit_execution_progress": "4X scaling requires a bounded final_position_capacity to prevent over-allocation.",
            "required_input_or_gate": "position capacity fields and budget calculations are valid.",
            "safe_next_repo_action": "Provide equity and risk values, then rerun evaluate in CONTINUE mode.",
            "owner_action_required_if_any": "Owner should confirm requested max open positions and risk caps.",
            "validator_to_prove_bridge_closed": "final_position_capacity is computed by policy and >= 1.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_BLOCKED",
        },
        {
            "island_name": "flow1_target_countdown_bridge",
            "missing_capability": "Target return countdown is not active from normalized baseline equity.",
            "why_it_blocks_profit_execution_progress": "Flow 2 start conditions require live return progress state.",
            "required_input_or_gate": "baseline_equity and current_equity are validated.",
            "safe_next_repo_action": "Provide baseline and current equity, then rerun evaluate.",
            "owner_action_required_if_any": "Owner should confirm baseline source and input consistency.",
            "validator_to_prove_bridge_closed": "cumulative_return_percent and remaining targets are computed.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_BASELINE_MISSING",
        },
        {
            "island_name": "flow1_sos_alert_bridge",
            "missing_capability": "SOS alert integration has not been accepted.",
            "why_it_blocks_profit_execution_progress": "Flow handoff requires mandatory SOS escalation readiness.",
            "required_input_or_gate": "sos_alerts_acknowledged is true and milestone contract exists.",
            "safe_next_repo_action": "Confirm sos_alerts_acknowledged and rerun evaluate.",
            "owner_action_required_if_any": "Owner should review the escalation requirement list.",
            "validator_to_prove_bridge_closed": "sos_alert_integration_status is SOS_CONTRACT_READY_FOR_FLOW2.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_MISSING_ALERTS",
        },
        {
            "island_name": "flow1_risk_control_bridge",
            "missing_capability": "Risk control gate acknowledgment is incomplete.",
            "why_it_blocks_profit_execution_progress": "Risk and loss limits are mandatory before gated continue.",
            "required_input_or_gate": "risk_controls_acknowledged and loss thresholds are within policy.",
            "safe_next_repo_action": "Collect risk_controls_acknowledged and rerun evaluate.",
            "owner_action_required_if_any": "Owner should confirm risk-control and loss policy acknowledgements.",
            "validator_to_prove_bridge_closed": "risk_controls_acknowledged is true and loss limits pass.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_RISK_CONTROL_MISSING",
        },
        {
            "island_name": "flow1_idempotency_bridge",
            "missing_capability": "Idempotency key guard is not confirmed.",
            "why_it_blocks_profit_execution_progress": "Duplicate execution must be prevented before handoff.",
            "required_input_or_gate": "idempotency_acknowledged is true.",
            "safe_next_repo_action": "Confirm idempotency acknowledgement and rerun evaluate.",
            "owner_action_required_if_any": "Owner should confirm idempotency governance.",
            "validator_to_prove_bridge_closed": "idempotency_acknowledged is true.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_IDEMPOTENCY_MISSING",
        },
        {
            "island_name": "flow1_no_duplicate_order_bridge",
            "missing_capability": "No-duplicate-order control is not yet acknowledged.",
            "why_it_blocks_profit_execution_progress": "Duplicate order prevention is mandatory for Flow 2 evidence quality.",
            "required_input_or_gate": "no_duplicate_order_acknowledged is true.",
            "safe_next_repo_action": "Confirm no-duplicate-order acknowledgement and rerun evaluate.",
            "owner_action_required_if_any": "Owner should confirm no-duplicate-order controls.",
            "validator_to_prove_bridge_closed": "no_duplicate_order_acknowledged is true.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_DUPLICATE_GUARD_MISSING",
        },
        {
            "island_name": "flow1_stale_price_guard_bridge",
            "missing_capability": "Stale-price guard is not acknowledged.",
            "why_it_blocks_profit_execution_progress": "Stale-price protection is required for evidence integrity.",
            "required_input_or_gate": "stale_price_guard_acknowledged is true.",
            "safe_next_repo_action": "Confirm stale-price guard state and rerun evaluate.",
            "owner_action_required_if_any": "Owner should confirm stale-price guard behavior.",
            "validator_to_prove_bridge_closed": "stale_price_guard_acknowledged is true.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_STALE_GUARD_MISSING",
        },
        {
            "island_name": "flow1_kill_switch_bridge",
            "missing_capability": "Kill switch state is active or not acknowledged.",
            "why_it_blocks_profit_execution_progress": "Execution authority is blocked until kill switch is off and acknowledged.",
            "required_input_or_gate": "kill_switch_state is false and kill_switch_acknowledged is true.",
            "safe_next_repo_action": "Resolve kill-switch state in owner input and rerun evaluate.",
            "owner_action_required_if_any": "Owner should acknowledge kill switch status and controls.",
            "validator_to_prove_bridge_closed": "kill_switch_state is false.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_KILL_SWITCH_ACTIVE",
        },
        {
            "island_name": "flow1_flow2_evidence_handoff_bridge",
            "missing_capability": "Flow 2 evidence handoff package is incomplete.",
            "why_it_blocks_profit_execution_progress": "Flow 2 requires stable gate state and evidence definitions before entry.",
            "required_input_or_gate": "flow2_evidence_capture_acknowledged and handoff file content exists.",
            "safe_next_repo_action": "Confirm handoff requirements and keep gates stable.",
            "owner_action_required_if_any": "Owner should confirm broker snapshot and evidence cadence.",
            "validator_to_prove_bridge_closed": "flow2_handoff_status is READY.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_IF_HANDOFF_NOT_READY",
        },
        {
            "island_name": "flow1_publish_clean_merge_bridge",
            "missing_capability": "Validation and publish gates are not yet clean.",
            "why_it_blocks_profit_execution_progress": "Flow handoff cannot complete without validated artifacts.",
            "required_input_or_gate": "validator and publish flow complete without failure.",
            "safe_next_repo_action": "Run host validator and publish flow as required.",
            "owner_action_required_if_any": "Owner should authorize repository publish sequence.",
            "validator_to_prove_bridge_closed": "HOST_VALIDATION_REQUIRED transitions to approved handoff state.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "PAUSE_UNTIL_PUBLISH_CHECKS",
        },
    ]


def _validate_forbidden_fields(owner_input: Dict[str, Any]) -> List[str]:
    return [field for field in FORBIDDEN_FIELDS if field in owner_input]


def _validate_authorization_true(owner_input: Dict[str, Any]) -> List[str]:
    return [field for field in AUTHORIZATION_FIELDS if _safe_bool(owner_input.get(field))]


def _required_json_fields(result: Dict[str, Any]) -> bool:
    required = [
        "flow1_status",
        "flow1_mode",
        "owner_live_capital_intent_usd",
        "requested_max_open_positions",
        "requested_quantity_scale",
        "final_position_capacity",
        "position_capacity_status",
        "target_return_band",
        "target_return_claim_status",
        "profit_return_countdown_status",
        "runtime_objective",
        "runtime_status",
        "vacation_mode_status",
        "sos_alert_integration_status",
        "flow2_handoff_status",
        "next_required_flow",
        "flow1_repo_gate_active",
    ]
    return all(key in result for key in required)


def evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(
    owner_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    result = _base_result()
    result.update(_default_authorization_flags())

    if owner_input is None:
        return result

    owner_input = dict(owner_input)
    result["flow1_action"] = _safe_str(owner_input.get("flow1_action"), "CONTINUE")
    result["owner_attestation"] = _safe_bool(owner_input.get("owner_attestation"))

    result["baseline_equity"] = _safe_float(owner_input.get("baseline_equity"), 0.0)
    result["current_equity"] = _safe_float(owner_input.get("current_equity"), result["baseline_equity"])

    if result["baseline_equity"] == 0.0 and "baseline_equity" in owner_input:
        result["baseline_equity"] = 0.0

    result["available_equity"] = _positive_or_default(owner_input.get("available_equity"), 0.0)
    if result["available_equity"] == 0.0:
        result["available_equity"] = _positive_or_default(owner_input.get("current_equity"), 0.0)
    if result["available_equity"] == 0.0:
        result["available_equity"] = _positive_or_default(owner_input.get("baseline_equity"), 0.0)

    result["open_trade_count"] = _safe_int(owner_input.get("open_trade_count"), 0)
    result["closed_trade_count"] = _safe_int(owner_input.get("closed_trade_count"), 0)
    result["current_drawdown_percent"] = _safe_float(owner_input.get("current_drawdown_percent"), 0.0)
    result["daily_realized_loss_percent"] = _safe_float(owner_input.get("daily_realized_loss_percent"), 0.0)
    result["weekly_realized_loss_percent"] = _safe_float(owner_input.get("weekly_realized_loss_percent"), 0.0)
    result["kill_switch_state"] = _safe_bool(owner_input.get("kill_switch_state"))

    if "demo_account_marker" in owner_input:
        result["demo_account_marker"] = _safe_str(owner_input.get("demo_account_marker"), "UNKNOWN")
    if "broker_environment" in owner_input:
        result["broker_environment"] = _safe_str(owner_input.get("broker_environment"), "UNKNOWN")

    for field in (
        "target_return_band_acknowledged",
        "profit_countdown_acknowledged",
        "runtime_objective_acknowledged",
        "vacation_mode_target_acknowledged",
        "sos_alerts_acknowledged",
        "risk_controls_acknowledged",
        "idempotency_acknowledged",
        "no_duplicate_order_acknowledged",
        "stale_price_guard_acknowledged",
        "kill_switch_acknowledged",
        "owner_supervised_demo_execution_acknowledged",
        "flow2_evidence_capture_acknowledged",
    ):
        result[field] = _safe_bool(owner_input.get(field))

    # Keep authorization defaults but surface explicit true values as hard fails.
    for field in AUTHORIZATION_FIELDS:
        result[field] = _safe_bool(owner_input.get(field))

    capacity = calculate_position_capacity(owner_input)
    result.update(capacity)
    result["requested_max_open_positions"] = capacity["requested_max_open_positions"]

    if result["baseline_equity"] > 0:
        result["target_equity_100_percent"] = result["baseline_equity"] * 2.00
        result["target_equity_120_percent"] = result["baseline_equity"] * 2.20
        result["cumulative_profit_amount"] = result["current_equity"] - result["baseline_equity"]
        cumulative_return_percent = (
            (result["current_equity"] - result["baseline_equity"]) / result["baseline_equity"]
        ) * 100.0
        result["cumulative_return_percent"] = float(cumulative_return_percent)
        result["remaining_to_100_percent"] = max(0.0, 100.0 - cumulative_return_percent)
        result["remaining_to_120_percent"] = max(0.0, 120.0 - cumulative_return_percent)
        result["target_100_reached"] = cumulative_return_percent >= 100.0
        result["target_120_reached"] = cumulative_return_percent >= 120.0
        result["milestone_alert"] = _milestone_alert(cumulative_return_percent)
    else:
        result["target_equity_100_percent"] = None
        result["target_equity_120_percent"] = None
        result["cumulative_profit_amount"] = None
        result["cumulative_return_percent"] = None
        result["remaining_to_100_percent"] = None
        result["remaining_to_120_percent"] = None
        result["target_100_reached"] = False
        result["target_120_reached"] = False
        result["milestone_alert"] = "TARGET_IN_PROGRESS_NO_MILESTONE_ALERT"

    result["drawdown_alert"] = _drawdown_alert(result["current_drawdown_percent"])

    if not _required_json_fields(result):
        raise RuntimeError("MODULE_OUTPUT_MISSING_REQUIRED_FIELDS")

    forbidden_fields = _validate_forbidden_fields(owner_input)
    authorization_true_fields = _validate_authorization_true(owner_input)
    if forbidden_fields:
        result["forbidden_fields_found"] = forbidden_fields
    if authorization_true_fields:
        result["authorization_flags_true"] = authorization_true_fields

    action = result["flow1_action"]
    if action == "PAUSE":
        result["flow1_status"] = "FLOW1_PAUSED_BY_OWNER"
        result["flow1_mode"] = "PAUSED"
        result["next_required_action"] = "OWNER_RESUME_REQUIRED"
        result["publish_status"] = "NOT_READY_PAUSED"
        return result

    if action == "STOP":
        result["flow1_status"] = "FLOW1_STOPPED_BY_OWNER"
        result["flow1_mode"] = "STOPPED"
        result["next_required_action"] = "OWNER_REVIEW_REQUIRED"
        result["publish_status"] = "NOT_READY_STOPPED"
        return result

    if action == "BRIDGE":
        result["flow1_status"] = "FLOW1_BRIDGE_BUILDING"
        result["flow1_mode"] = "BRIDGE_BUILDING"
        result["flow1_bridge_map"] = build_flow1_bridge_map(result)
        result["next_required_action"] = "CONTINUE_AFTER_BRIDGE_VALIDATION"
        return result

    gate_requirements = [
        _required_json_fields(result),
        result["target_return_band_acknowledged"],
        result["profit_countdown_acknowledged"],
        result["runtime_objective_acknowledged"],
        result["vacation_mode_target_acknowledged"],
        result["sos_alerts_acknowledged"],
        result["risk_controls_acknowledged"],
        result["idempotency_acknowledged"],
        result["no_duplicate_order_acknowledged"],
        result["stale_price_guard_acknowledged"],
        result["kill_switch_acknowledged"],
        result["owner_supervised_demo_execution_acknowledged"],
        result["flow2_evidence_capture_acknowledged"],
        not result["kill_switch_state"],
        result["open_trade_count"] <= result["max_open_positions"],
        result["daily_realized_loss_percent"] <= MAX_DAILY_LOSS_PERCENT_DEFAULT,
        result["weekly_realized_loss_percent"] <= MAX_WEEKLY_LOSS_PERCENT_DEFAULT,
        result["current_drawdown_percent"] < MAX_DRAWDOWN_STOP_PERCENT_DEFAULT,
        result["final_position_capacity"] >= 1,
        result["demo_account_marker"] in {"DEMO_ONLY", "DEMO_OR_PRACTICE_ONLY"},
        result["broker_environment"] in {"DEMO_ONLY", "DEMO_OR_PRACTICE_ONLY"},
    ]

    if forbidden_fields:
        result["flow1_status"] = "FLOW1_BLOCKED_FORBIDDEN_FIELD_PRESENT"
        result["flow1_mode"] = "PAUSE_READY"
        result["execution_authority_status"] = "BLOCKED_PENDING_OWNER_INPUT"
        result["next_required_action"] = "OWNER_SUPPLY_SANITIZED_FLOW1_INPUT"
        result["publish_status"] = "NOT_READY_VALIDATION_REQUIRED"
        return result

    if authorization_true_fields:
        result["flow1_status"] = "FLOW1_BLOCKED_AUTHORIZATION_ENABLED"
        result["flow1_mode"] = "PAUSE_READY"
        result["execution_authority_status"] = "BLOCKED_PENDING_OWNER_INPUT"
        result["next_required_action"] = "OWNER_SUPPLY_SANITIZED_FLOW1_INPUT"
        result["publish_status"] = "NOT_READY_VALIDATION_REQUIRED"
        return result

    if not all(gate_requirements):
        result["flow1_status"] = "FLOW1_BLOCKED_CONTINUE_GATES_MISSING"
        result["flow1_mode"] = "PAUSE_READY"
        result["profit_return_countdown_status"] = (
            "COUNTDOWN_ACTIVE" if result["baseline_equity"] > 0 else "BASELINE_EQUITY_REQUIRED"
        )
        result["profit_return_rate_status"] = (
            "COUNTDOWN_NOT_ACTIVE_BASELINE_REQUIRED"
            if result["baseline_equity"] <= 0
            else "COUNTDOWN_NOT_ACTIVE_GATES_PENDING"
        )
        result["execution_authority_status"] = "BLOCKED_PENDING_GATES"
        result["flow2_handoff_status"] = "NOT_READY"
        result["runtime_status"] = "GATED_PENDING_SUPERVISED_EVIDENCE"
        result["vacation_mode_status"] = "TARGET_DEFINED_GATE_PENDING"
        result["sos_alert_integration_status"] = "REQUIRED_GATE_PENDING"
        result["next_required_action"] = "OWNER_SUPPLY_SANITIZED_FLOW1_INPUT"
        return result

    result["flow1_status"] = (
        "FLOW1_ACTIVE_GATE_READY_FOR_FLOW2_SUPERVISED_DEMO_EVIDENCE_CAPTURE"
    )
    result["flow1_mode"] = "CONTINUE_READY"
    result["profit_return_countdown_status"] = "COUNTDOWN_ACTIVE"
    result["profit_return_rate_status"] = "COUNTDOWN_ACTIVE"
    result["runtime_status"] = "GATED_READY_FOR_SUPERVISED_DEMO_EVIDENCE"
    result["vacation_mode_status"] = "TARGET_DEFINED_GATE_READY_FOR_EVIDENCE"
    result["sos_alert_integration_status"] = "SOS_CONTRACT_READY_FOR_FLOW2"
    result["execution_authority_status"] = "READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION_HANDOFF"
    result["flow2_handoff_status"] = "READY"
    result["next_required_flow"] = FLOW_2
    result["next_required_action"] = (
        "RUN_FLOW2_SUPERVISED_DEMO_EXECUTION_EVIDENCE_CAPTURE_AFTER_THIS_PACKET_LANDS"
    )
    result["publish_status"] = "READY_AFTER_HOST_VALIDATION"
    return result


def render_owner_report(result: Dict[str, Any]) -> str:
    return (
        "# AIOS Forex Flow 1 Active Execution Authority Runtime SOS Profit Countdown V2 Report\n\n"
        "## Real Forex End-State\n"
        "Flow 1 evaluates dynamic capacity, countdown, SOS gates, and controlled readiness for Flow 2 handoff.\n\n"
        "## Current Verified Anchor\n"
        "continuous bridge controller is merged on main and anchors this packet.\n\n"
        "## Owner Live-Capital Intent\n"
        f"- owner_live_capital_intent_usd: {result['owner_live_capital_intent_usd']}\n"
        f"- requested_max_open_positions: {result['requested_max_open_positions']}\n"
        f"- requested_quantity_scale: {result['requested_quantity_scale']}\n"
        "## Baseline Equity Rule\n"
        f"- baseline_equity: {result['baseline_equity']}\n"
        f"- baseline_equity_source: {result['baseline_equity_source']}\n"
        f"- hardcoded_10000_baseline_forbidden: {str(result['hardcoded_10000_baseline_forbidden']).lower()}\n\n"
        "## Target Return Band\n"
        f"- target_return_band: {result['target_return_band']}\n"
        f"- target_return_claim_status: {result['target_return_claim_status']}\n"
        f"- profit_return_countdown_status: {result['profit_return_countdown_status']}\n"
        f"- profit_return_rate_status: {result['profit_return_rate_status']}\n\n"
        "## Position Capacity Engine\n"
        f"- requested_max_open_positions: {result['requested_max_open_positions']}\n"
        f"- configured_max_open_positions: {result['configured_max_open_positions']}\n"
        f"- calculated_max_open_positions: {result['calculated_max_open_positions']}\n"
        f"- final_position_capacity: {result['final_position_capacity']}\n"
        f"- position_capacity_status: {result['position_capacity_status']}\n"
        f"- position_capacity_reason: {result['position_capacity_reason']}\n"
        f"- available_equity: {result['available_equity']}\n"
        f"- baseline_equity: {result['baseline_equity']}\n"
        f"- risk_per_trade_percent: {result['risk_per_trade_percent']}\n"
        f"- max_aggregate_open_risk_percent: {result['max_aggregate_open_risk_percent']}\n"
        f"- max_margin_utilization_percent: {result['max_margin_utilization_percent']}\n"
        f"- margin_capacity_status: {result['margin_capacity_status']}\n"
        f"- exposure_capacity_status: {result['exposure_capacity_status']}\n"
        f"- risk_limited_capacity: {result['risk_limited_capacity']}\n"
        f"- margin_limited_capacity: {result['margin_limited_capacity']}\n"
        f"- remaining_position_slots: {result['remaining_position_slots']}\n"
        f"- aggregate_risk_budget_amount: {result['aggregate_risk_budget_amount']}\n"
        f"- margin_budget_amount: {result['margin_budget_amount']}\n\n"
        "## Requested 4X Quantity Scale\n"
        f"- requested_quantity_scale: {result['requested_quantity_scale']}\n\n"
        "## Profit-Return Countdown\n"
        f"- target_equity_100_percent: {result['target_equity_100_percent']}\n"
        f"- target_equity_120_percent: {result['target_equity_120_percent']}\n"
        f"- cumulative_profit_amount: {result['cumulative_profit_amount']}\n"
        f"- cumulative_return_percent: {result['cumulative_return_percent']}\n"
        f"- remaining_to_100_percent: {result['remaining_to_100_percent']}\n"
        f"- remaining_to_120_percent: {result['remaining_to_120_percent']}\n"
        f"- target_100_reached: {str(result['target_100_reached']).lower()}\n"
        f"- target_120_reached: {str(result['target_120_reached']).lower()}\n"
        f"- milestone_alert: {result['milestone_alert']}\n"
        f"- drawdown_alert: {result['drawdown_alert']}\n\n"
        "## Runtime Objective\n"
        f"- runtime_objective: {result['runtime_objective']}\n"
        f"- runtime_status: {result['runtime_status']}\n\n"
        "## Vacation Mode Target\n"
        f"- vacation_mode_status: {result['vacation_mode_status']}\n\n"
        "## SOS Alert Contract\n"
        f"- sos_alert_integration_status: {result['sos_alert_integration_status']}\n"
        f"- flow2_handoff_status: {result['flow2_handoff_status']}\n\n"
        "## Risk Control Gate\n"
        f"- risk_controls_acknowledged: {str(result['risk_controls_acknowledged']).lower()}\n\n"
        "## Idempotency And No-Duplicate-Order Gate\n"
        f"- idempotency_acknowledged: {str(result['idempotency_acknowledged']).lower()}\n"
        f"- no_duplicate_order_acknowledged: {str(result['no_duplicate_order_acknowledged']).lower()}\n\n"
        "## Stale-Price Guard\n"
        f"- stale_price_guard_acknowledged: {str(result['stale_price_guard_acknowledged']).lower()}\n\n"
        "## Kill-Switch Gate\n"
        f"- kill_switch_state: {str(result['kill_switch_state']).lower()}\n"
        f"- kill_switch_acknowledged: {str(result['kill_switch_acknowledged']).lower()}\n\n"
        "## Flow 2 Handoff\n"
        f"- next_required_flow: {result['next_required_flow']}\n"
        f"- flow1_status: {result['flow1_status']}\n\n"
        "## Bridge Map\n"
        f"- required_islands: {len(result['flow1_bridge_map']) if isinstance(result['flow1_bridge_map'], list) else 0}\n\n"
        "## Host Validation Script\n"
        "scripts/forex_delivery/validate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.ps1\n\n"
        "## Host Publish Script\n"
        "scripts/forex_delivery/publish_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.ps1\n\n"
        "## Blocked External Actions\n"
        "- broker_api_access_authorized\n"
        "- credential_access_authorized\n"
        "- demo_order_placement_authorized\n"
        "- live_trading_authorized\n"
        "- execution_command_authorized\n"
        "- runtime_22h6d_activated\n"
        "- vacation_mode_activated\n"
        "- autonomous_trading_authorized\n"
        "- money_movement_authorized\n"
        "- broker_connection_authorized\n"
        "- order_submission_authorized\n\n"
        "## What This Completes\n"
        "Flow 1 now provides dynamic capacity and return countdown logic and handoff checks for Flow 2 evidence capture.\n\n"
        "## What This Does Not Approve\n"
        "No live trading, broker/API access, credentials, order submission, execution command, autonomous operation, or money movement is approved.\n\n"
        "## Next Required Flow\n"
        "FLOW_2_SUPERVISED_DEMO_EXECUTION_EVIDENCE_AND_COUNTDOWN_CAPTURE\n\n"
        "## Final Owner Sentence\n"
        "AIOS Forex Flow 1 active execution authority runtime SOS profit countdown gate is prepared locally: the owner live-capital intent remains $1,000, requested max open positions is 4 with 4X target scaling bounded by risk and margin capacity, the target return band remains 100–120% tracked from dynamic baseline equity, Flow 2 supervised demo evidence capture is the next governed flow when validated owner input passes, and live trading, broker/API access, credentials, order submission, execution command, 22h6d runtime, vacation mode, autonomy, and money movement remain blocked until separately proven and approved.\n"
    )


def render_next_action_queue(result: Dict[str, Any]) -> str:
    bridge_names = [entry["island_name"] for entry in result.get("flow1_bridge_map", [])]
    if bridge_names:
        bridge_lines = "\n".join(f"- {entry}" for entry in bridge_names)
    else:
        bridge_lines = "- no active bridge entries"

    return (
        "# AIOS Forex Flow 1 Active Execution Authority Runtime SOS Profit Countdown Next Action Queue V2\n\n"
        "## Purpose\n"
        "Advance Flow 1 to a controlled supervised evidence handoff only after required gates and capacity checks pass.\n\n"
        "## Flow 1 Status\n"
        f"{result['flow1_status']}\n\n"
        "## Flow 1 Mode\n"
        f"{result['flow1_mode']}\n\n"
        "## Position Capacity Status\n"
        f"{result['position_capacity_status']}\n\n"
        "## Profit-Return Countdown Status\n"
        f"{result['profit_return_countdown_status']}\n\n"
        "## Runtime Status\n"
        f"{result['runtime_status']}\n\n"
        "## Vacation Mode Status\n"
        f"{result['vacation_mode_status']}\n\n"
        "## SOS Alert Status\n"
        f"{result['sos_alert_integration_status']}\n\n"
        "## Bridge Map\n"
        f"{bridge_lines}\n\n"
        "## Next Required Flow\n"
        f"{result['next_required_flow']}\n\n"
        "## Required Next Actions\n"
        "- confirm all required input and gate acknowledgements for CONTINUE path.\n"
        "- keep all execution authority flags false.\n"
        "- keep broker/demo-only behavior in local scope.\n\n"
        "## Remaining Blocks\n"
        "- broker_API_access_authorized remains false.\n"
        "- credential_access_authorized remains false.\n"
        "- demo_order_placement_authorized remains false.\n"
        "- live_trading_authorized remains false.\n"
        "- execution_command_authorized remains false.\n"
        "- money_movement_authorized remains false.\n\n"
        "## Final Owner Sentence\n"
        "AIOS Forex Flow 1 active execution authority runtime SOS profit countdown gate is prepared locally: the owner live-capital intent remains $1,000, requested max open positions is 4 with 4X target scaling bounded by risk and margin capacity, the target return band remains 100–120% tracked from dynamic baseline equity, Flow 2 supervised demo evidence capture is the next governed flow when validated owner input passes, and live trading, broker/API access, credentials, order submission, execution command, 22h6d runtime, vacation mode, autonomy, and money movement remain blocked until separately proven and approved.\n"
    )


def render_flow2_handoff(result: Dict[str, Any]) -> str:
    return (
        "# AIOS Forex Flow 1 to Flow 2 Active Supervised Demo Evidence Handoff V2\n\n"
        "## Flow 1 Status\n"
        f"{result['flow1_status']}\n\n"
        "## Next Required Flow\n"
        f"{result['next_required_flow']}\n\n"
        "## Owner Live-Capital Intent\n"
        f"{result['owner_live_capital_intent_usd']}\n\n"
        "## Baseline Equity Rule\n"
        f"baseline_equity_source: {result['baseline_equity_source']}\n"
        f"baseline_equity: {result['baseline_equity']}\n"
        f"hardcoded_10000_baseline_forbidden: {str(result['hardcoded_10000_baseline_forbidden']).lower()}\n\n"
        "## Requested Max Open Positions\n"
        f"{result['requested_max_open_positions']}\n\n"
        "## Final Position Capacity\n"
        f"{result['final_position_capacity']}\n\n"
        "## 4X Target Scale Status\n"
        f"{result['requested_quantity_scale']}\n\n"
        "## Target Return Countdown Status\n"
        f"{result['profit_return_countdown_status']}\n\n"
        "## SOS Alert Requirement\n"
        f"{result['sos_alert_integration_status']}\n\n"
        "## Runtime Objective Status\n"
        f"{result['runtime_status']}\n\n"
        "## Evidence Capture Requirements for Flow 2\n"
        "- broker snapshot capture\n"
        "- TP/SL capture\n"
        "- realized P/L capture\n"
        "- no duplicate order requirement\n"
        "- no runaway exposure requirement\n"
        "- post-trade countdown update\n\n"
        "## Broker Snapshot Requirement\n"
        "Capture broker/demo-only snapshot before entry.\n\n"
        "## TP/SL Capture Requirement\n"
        "Capture TP/SL data for each managed position.\n\n"
        "## Realized P/L Capture Requirement\n"
        "Capture realized P/L for close events.\n\n"
        "## No Duplicate Order Requirement\n"
        "Maintain no-duplicate-order control while Flow 2 captures evidence.\n\n"
        "## No Runaway Exposure Requirement\n"
        "Maintain capped aggregate open risk and notional exposure while evidence is collected.\n\n"
        "## Post-Trade Countdown Update Requirement\n"
        "Update return countdown after each close-trade input.\n\n"
        "## Blocked Actions\n"
        "- order_submission_authorized\n"
        "- broker_connection_authorized\n"
        "- money_movement_authorized\n"
        "- autonomous_trading_authorized\n"
        "- runtime_22h6d_activated\n"
        "- vacation_mode_activated\n\n"
        "## Final Owner Sentence\n"
        "AIOS Forex Flow 1 active execution authority runtime SOS profit countdown gate is prepared locally: the owner live-capital intent remains $1,000, requested max open positions is 4 with 4X target scaling bounded by risk and margin capacity, the target return band remains 100–120% tracked from dynamic baseline equity, Flow 2 supervised demo evidence capture is the next governed flow when validated owner input passes, and live trading, broker/API access, credentials, order submission, execution command, 22h6d runtime, vacation mode, autonomy, and money movement remain blocked until separately proven and approved.\n"
    )


def generate_artifacts(owner_input: Dict[str, Any] | None = None) -> Dict[str, Any]:
    result = evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_REPORT_PATH.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    HANDOFF_PATH.write_text(render_flow2_handoff(result), encoding="utf-8")
    return result


def contains_banned_output_tokens(payload: str) -> bool:
    lowered = payload.lower()
    return any(token.lower() in lowered for token in BANNED_OUTPUT_TOKENS)


if __name__ == "__main__":
    generate_artifacts()
