"""Forex continuous bridge-to-profit controller for the remaining governed flow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "Reports" / "forex_delivery"
JSON_REPORT_PATH = (
    REPORT_DIR
    / "AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_V1.json"
)
REPORT_PATH = (
    REPORT_DIR / "AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_V1_REPORT.md"
)
QUEUE_PATH = (
    REPORT_DIR
    / "AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_NEXT_ACTION_QUEUE_V1.md"
)

CAMPAIGN_ID = "AIOS-FOREX-CONTINUOUS-BRIDGE-TO-PROFIT-CONTROLLER-V1"
CONTROLLER_ID = "AIOS-FOREX-CONTINUOUS-BRIDGE-TO-PROFIT-CONTROLLER-V1"

FLOW_1 = "FLOW_1_EXECUTION_AUTHORITY_TARGET_COUNTDOWN_RUNTIME_SOS_GATE"
FLOW_2 = "FLOW_2_SUPERVISED_DEMO_EXECUTION_EVIDENCE_AND_COUNTDOWN_CAPTURE"
FLOW_3 = "FLOW_3_PROFIT_LOOP_LIVE_WEEK_VACATION_MODE_ACTIVATION_GATE"

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
}

REQUIRED_CONTINUE_FIELDS = [
    "controller_action",
    "baseline_equity",
    "current_equity",
    "closed_trade_count",
    "open_trade_count",
    "max_open_positions",
    "current_drawdown_percent",
    "daily_realized_loss_percent",
    "weekly_realized_loss_percent",
    "kill_switch_state",
    "owner_attestation",
    "demo_account_marker",
    "broker_environment",
    "runtime_objective_acknowledged",
    "target_return_band_acknowledged",
    "profit_countdown_acknowledged",
    "live_profitable_week_target_acknowledged",
    "vacation_mode_target_acknowledged",
    "sos_alerts_acknowledged",
]


def build_missing_island_bridge_map(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    # result is used for future expansion of gate-specific text.
    _ = result
    return [
        {
            "island_name": "baseline_equity_bridge",
            "missing_capability": "Owner-supplied or broker-snapshot baseline equity is not yet bound.",
            "why_it_blocks_real_money_progress": (
                "Target return countdown cannot compute without a verified baseline."
            ),
            "required_input_or_gate": "Owner input or broker snapshot baseline equity.",
            "safe_next_repo_action": (
                "Collect validated owner baseline equity input and rerun CONTINUE."
            ),
            "owner_action_required_if_any": "Owner must supply a baseline equity value.",
            "validator_to_prove_bridge_closed": (
                "evaluate returns non-null target_100_percent and target_120_percent."
            ),
            "next_flow_that_consumes_bridge": FLOW_1,
            "stop_pause_continue_recommendation": "BRIDGE",
        },
        {
            "island_name": "broker_snapshot_bridge",
            "missing_capability": "No broker snapshot evidence is currently required in this packet.",
            "why_it_blocks_real_money_progress": (
                "No snapshot proof exists for evidence-based promotion checkpoints."
            ),
            "required_input_or_gate": "broker snapshot artifact in later flows.",
            "safe_next_repo_action": (
                "Proceed to FLOW_2 for broker snapshot capture once runtime gates are active."
            ),
            "owner_action_required_if_any": "None in this file.",
            "validator_to_prove_bridge_closed": "FLOW_2 produces snapshot capture outputs.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "CONTINUE",
        },
        {
            "island_name": "credential_gate_bridge",
            "missing_capability": "Credential gate remains blocked for future live operations.",
            "why_it_blocks_real_money_progress": (
                "Live credentials and API access must stay blocked until explicit owner proof gates pass."
            ),
            "required_input_or_gate": "live credential gate remains false.",
            "safe_next_repo_action": "Preserve the false credential gate in evidence artifacts.",
            "owner_action_required_if_any": "No owner action in this stage.",
            "validator_to_prove_bridge_closed": (
                "credential_access_authorized remains false in controller status."
            ),
            "next_flow_that_consumes_bridge": FLOW_3,
            "stop_pause_continue_recommendation": "PAUSE",
        },
        {
            "island_name": "supervised_demo_execution_bridge",
            "missing_capability": "Demonstrated supervised demo execution proof is not complete in this packet.",
            "why_it_blocks_real_money_progress": (
                "Evidence-based promotion requires supervised demo execution before live readiness."
            ),
            "required_input_or_gate": "FLOW_2 evidence from monitored demo operations.",
            "safe_next_repo_action": "Continue to FLOW_2 with flow-specific evidence controls.",
            "owner_action_required_if_any": "Owner supervision and attestation for demo flow.",
            "validator_to_prove_bridge_closed": "FLOW_2 completion artifact.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "CONTINUE",
        },
        {
            "island_name": "post_trade_evidence_bridge",
            "missing_capability": "Trade close event evidence is not yet captured.",
            "why_it_blocks_real_money_progress": "No closed-trade outcome evidence exists to track candidates.",
            "required_input_or_gate": "broker snapshot, P/L, and TP/SL evidence in FLOW_2.",
            "safe_next_repo_action": "Rely on FLOW_2 capture outputs before candidate updates.",
            "owner_action_required_if_any": "No owner action in this stage.",
            "validator_to_prove_bridge_closed": "FLOW_2 post-trade evidence marker present.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "CONTINUE",
        },
        {
            "island_name": "profit_countdown_update_bridge",
            "missing_capability": "Profit-return countdown is not yet updated after each open or closed trade.",
            "why_it_blocks_real_money_progress": "No objective progression evidence is available without periodic updates.",
            "required_input_or_gate": "FLOW_2 trade event callbacks in owner-hosted mode.",
            "safe_next_repo_action": "Apply FLOW_2 and rerun flow updates from new equity inputs.",
            "owner_action_required_if_any": "Owner must validate evidence and confirm no duplicate order.",
            "validator_to_prove_bridge_closed": "cumulative_return_percent updates after next valid input.",
            "next_flow_that_consumes_bridge": FLOW_2,
            "stop_pause_continue_recommendation": "CONTINUE",
        },
        {
            "island_name": "sos_alert_bridge",
            "missing_capability": "SOS alert contract is defined but not yet consumed by all flows.",
            "why_it_blocks_real_money_progress": "Escalation proof is required before runtime targets remain active.",
            "required_input_or_gate": "sos_alerts_acknowledged and SOS alert hook evidence.",
            "safe_next_repo_action": "Keep sos_alerts_acknowledged false until integration is executed in later flows.",
            "owner_action_required_if_any": "Owner approves alert channel behavior and thresholds.",
            "validator_to_prove_bridge_closed": "FLOW_1 tracks milestone and drawdown SOS statuses.",
            "next_flow_that_consumes_bridge": FLOW_1,
            "stop_pause_continue_recommendation": "CONTINUE",
        },
        {
            "island_name": "runtime_supervisor_22h6d_bridge",
            "missing_capability": "22h/6d runtime objective is defined but not yet active.",
            "why_it_blocks_real_money_progress": "Runtime controls and supervisor gating are required before sustained deployment.",
            "required_input_or_gate": "runtime supervisor host validation.",
            "safe_next_repo_action": "Track objective status in FLOW_1 and await supervisor gate.",
            "owner_action_required_if_any": "Owner confirms runtime objective acknowledgement.",
            "validator_to_prove_bridge_closed": "FLOW_1 updates runtime readiness flags.",
            "next_flow_that_consumes_bridge": FLOW_1,
            "stop_pause_continue_recommendation": "PAUSE",
        },
        {
            "island_name": "vacation_mode_activation_bridge",
            "missing_capability": "Vacation mode is a target and not active.",
            "why_it_blocks_real_money_progress": (
                "Vacation mode needs runtime and SOS proof before target status can be set."
            ),
            "required_input_or_gate": "vacation mode target checkpoint after FLOW_1.",
            "safe_next_repo_action": "Keep vacation_mode_status in TARGET_DEFINED_NOT_ACTIVE.",
            "owner_action_required_if_any": "Owner confirms vacation mode target acceptance.",
            "validator_to_prove_bridge_closed": "Flow evidence that runtime and SOS gates are met.",
            "next_flow_that_consumes_bridge": FLOW_3,
            "stop_pause_continue_recommendation": "PAUSE",
        },
        {
            "island_name": "live_profitable_week_bridge",
            "missing_capability": "Live profitable week remains a target and is not yet proven.",
            "why_it_blocks_real_money_progress": "Live profitability evidence is required before any future promotion.",
            "required_input_or_gate": "candidate score and outcome history from FLOW_3.",
            "safe_next_repo_action": "Do not set completion flags before evidence appears.",
            "owner_action_required_if_any": "Owner confirms the target review result when evidence lands.",
            "validator_to_prove_bridge_closed": "FLOW_3 candidate and target status outputs.",
            "next_flow_that_consumes_bridge": FLOW_3,
            "stop_pause_continue_recommendation": "CONTINUE",
        },
        {
            "island_name": "publish_clean_merge_bridge",
            "missing_capability": "Publish handoff has not been executed yet.",
            "why_it_blocks_real_money_progress": "Evidence artifacts must be prepared before any production branch handoff.",
            "required_input_or_gate": "owner-driven host validation and PR merge controls.",
            "safe_next_repo_action": (
                "Use the generated publish script only after local validators pass."
            ),
            "owner_action_required_if_any": "Owner reviews host validation and PR state.",
            "validator_to_prove_bridge_closed": "Validation script returns VALIDATION_PASSED.",
            "next_flow_that_consumes_bridge": "PUBLISH_READY",
            "stop_pause_continue_recommendation": "PAUSE",
        },
    ]


def _compressed_flows() -> List[Dict[str, Any]]:
    return [
        {
            "flow_id": FLOW_1,
            "name": "Execution authority and runtime/SOS gate",
            "purpose": (
                "final owner-approved supervised demo authority review, countdown readiness, "
                "and SOS/risk gate alignment before publication."
            ),
        },
        {
            "flow_id": FLOW_2,
            "name": "Supervised demo evidence capture",
            "purpose": (
                "monitored demo proof, broker snapshot, TP/SL, realized P/L, and countdown updates."
            ),
        },
        {
            "flow_id": FLOW_3,
            "name": "Candidate progression to future controlled readiness",
            "purpose": (
                "evaluate live-ready candidates for future evidence-based promotion with all live gates off."
            ),
        },
    ]


def _default_result() -> Dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "controller_status": "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_OWNER_INPUT_REQUIRED",
        "controller_mode": "PAUSE_READY",
        "program_goal": "GOVERNED_FOREX_PROFIT_EXECUTION_SYSTEM",
        "owner_live_capital_intent_usd": 1000,
        "baseline_equity_source": "OWNER_INPUT_OR_BROKER_DEMO_OR_LIVE_SNAPSHOT",
        "hardcoded_10000_baseline_forbidden": True,
        "target_return_band": "100_TO_120_PERCENT",
        "target_return_claim_status": "TARGET_NOT_YET_VERIFIED",
        "profit_return_countdown_status": "BASELINE_EQUITY_REQUIRED",
        "profit_return_rate_status": "COUNTDOWN_NOT_ACTIVE_BASELINE_REQUIRED",
        "profit_return_countdown_required": True,
        "runtime_objective": "22_HOURS_PER_DAY_6_DAYS_PER_WEEK",
        "runtime_status": "NOT_ACTIVATED_PENDING_SUPERVISOR_GATE",
        "vacation_mode_status": "TARGET_DEFINED_NOT_ACTIVE",
        "sos_alert_integration_status": "REQUIRED_NOT_ACTIVE",
        "live_profitable_week_target_status": "TARGET_DEFINED_NOT_PROVEN",
        "execution_status": "BLOCKED_PENDING_FLOW_1",
        "compressed_flow_count": 3,
        "compressed_flow_map": _compressed_flows(),
        "next_required_flow": FLOW_1,
        "next_controller_action": "CONTINUE_AFTER_OWNER_HOST_VALIDATION",
        "publish_status": "NOT_READY_VALIDATION_REQUIRED",
        "missing_island_bridge_map": [],
        "input_validation_status": "WAITING_FOR_OWNER_INPUT",
        "input_notes": [],
        "baseline_equity": None,
        "current_equity": None,
        "closed_trade_count": None,
        "open_trade_count": None,
        "max_open_positions": None,
        "current_drawdown_percent": None,
        "daily_realized_loss_percent": None,
        "weekly_realized_loss_percent": None,
        "kill_switch_state": None,
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
        "owner_attestation": None,
        "demo_account_marker": None,
        "broker_environment": None,
        "runtime_objective_acknowledged": False,
        "target_return_band_acknowledged": False,
        "profit_countdown_acknowledged": False,
        "live_profitable_week_target_acknowledged": False,
        "vacation_mode_target_acknowledged": False,
        "sos_alerts_acknowledged": False,
        "post_trade_countdown_update_required": False,
    } | {field: False for field in AUTHORIZATION_FIELDS}


def _to_float(value: Any, field_name: str, notes: List[str]) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        notes.append(f"{field_name}_INVALID")
        return 0.0
    return value


def _to_bool(value: Any, field_name: str, notes: List[str]) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(int(value))
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "off", "n"}:
            return False
    notes.append(f"{field_name}_INVALID")
    return False


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


def evaluate_forex_continuous_bridge_to_profit_controller(
    owner_input: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    result = _default_result()
    if owner_input is None:
        return result
    if not isinstance(owner_input, dict):
        result["controller_status"] = "FOREX_CONTINUOUS_CONTROLLER_INVALID_OWNER_INPUT_TYPE"
        result["controller_mode"] = "BLOCKED"
        result["publish_status"] = "NOT_READY_INVALID_INPUT"
        result["input_validation_status"] = "INVALID_INPUT_TYPE"
        return result

    notes: List[str] = []
    result["input_notes"] = notes

    forbidden = FORBIDDEN_FIELDS.intersection(owner_input.keys())
    if forbidden:
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_FORBIDDEN_FIELD_PRESENT"
        )
        result["controller_mode"] = "BLOCKED"
        result["publish_status"] = "NOT_READY_BLOCKED"
        result["next_controller_action"] = "OWNER_RESUME_REQUIRED"
        result["input_validation_status"] = "FORBIDDEN_FIELD_PRESENT"
        result["input_notes"].append("FORBIDDEN_FIELD_PRESENT")
        result["input_notes"].append(
            "FORBIDDEN_FIELDS:" + ",".join(sorted(forbidden))
        )
        return result

    for auth_field in sorted(AUTHORIZATION_FIELDS):
        result[auth_field] = bool(owner_input.get(auth_field, False))

    auth_true = [field for field in AUTHORIZATION_FIELDS if result[field]]
    if auth_true:
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_UNSAFE_AUTHORIZATION_TRUE"
        )
        result["controller_mode"] = "BLOCKED"
        result["publish_status"] = "NOT_READY_BLOCKED"
        result["next_controller_action"] = "OWNER_REVIEW_REQUIRED"
        result["input_validation_status"] = "AUTHORIZATION_TRUE_BLOCKED"
        result["input_notes"].append("AUTHORIZATION_TRUE_BLOCKED")
        result["input_notes"].append("AUTHORIZATION_FIELDS_TRUE:" + ",".join(auth_true))
        return result

    for auth_field in sorted(AUTHORIZATION_FIELDS):
        result[auth_field] = False

    action = str(owner_input.get("controller_action", "PAUSE")).upper().strip()
    if action not in {"CONTINUE", "PAUSE", "STOP", "BRIDGE"}:
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_INVALID_ACTION"
        )
        result["controller_mode"] = "BLOCKED"
        result["publish_status"] = "NOT_READY_BLOCKED"
        result["input_validation_status"] = "INVALID_CONTROLLER_ACTION"
        result["next_controller_action"] = "OWNER_REVIEW_REQUIRED"
        result["input_notes"].append("INVALID_CONTROLLER_ACTION")
        return result

    if action == "PAUSE":
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_PAUSED_BY_OWNER"
        )
        result["controller_mode"] = "PAUSED"
        result["next_controller_action"] = "OWNER_RESUME_REQUIRED"
        result["publish_status"] = "NOT_READY_PAUSED"
        result["execution_status"] = "BLOCKED_BY_OWNER_PAUSE"
        result["next_required_flow"] = FLOW_1
        result["input_validation_status"] = "OWNER_PAUSE_REQUESTED"
        return result

    if action == "STOP":
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_STOPPED_BY_OWNER"
        )
        result["controller_mode"] = "STOPPED"
        result["next_controller_action"] = "OWNER_REVIEW_REQUIRED"
        result["publish_status"] = "NOT_READY_STOPPED"
        result["execution_status"] = "BLOCKED_BY_OWNER_STOP"
        result["next_required_flow"] = FLOW_1
        result["input_validation_status"] = "OWNER_STOP_REQUESTED"
        return result

    if action == "BRIDGE":
        result["controller_status"] = "FOREX_CONTINUOUS_CONTROLLER_BRIDGE_REQUIRED"
        result["controller_mode"] = "BRIDGE_BUILDING"
        result["next_controller_action"] = "CONTINUE_AFTER_BRIDGE_VALIDATION"
        result["publish_status"] = "NOT_READY_BRIDGE"
        result["execution_status"] = "BLOCKED_MISSING_ISLANDS"
        result["input_validation_status"] = "BRIDGE_MODE_ACTIVE"
        result["missing_island_bridge_map"] = build_missing_island_bridge_map(result)
        return result

    # CONTINUE path
    missing = [field for field in REQUIRED_CONTINUE_FIELDS if field not in owner_input]
    if missing:
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_MISSING_REQUIRED_INPUT"
        )
        result["controller_mode"] = "PAUSE_READY"
        result["publish_status"] = "NOT_READY_VALIDATION_REQUIRED"
        result["execution_status"] = "BLOCKED_PENDING_REQUIRED_INPUT"
        result["input_validation_status"] = "CONTINUE_INPUT_INCOMPLETE"
        result["input_notes"].extend(missing)
        return result

    baseline_equity = _to_float(owner_input["baseline_equity"], "baseline_equity", notes)
    current_equity = _to_float(owner_input["current_equity"], "current_equity", notes)
    closed_trade_count = _to_float(owner_input["closed_trade_count"], "closed_trade_count", notes)
    open_trade_count = _to_float(owner_input["open_trade_count"], "open_trade_count", notes)
    max_open_positions = _to_float(
        owner_input["max_open_positions"], "max_open_positions", notes
    )
    current_drawdown_percent = _to_float(
        owner_input["current_drawdown_percent"], "current_drawdown_percent", notes
    )
    daily_realized_loss_percent = _to_float(
        owner_input["daily_realized_loss_percent"], "daily_realized_loss_percent", notes
    )
    weekly_realized_loss_percent = _to_float(
        owner_input["weekly_realized_loss_percent"], "weekly_realized_loss_percent", notes
    )
    kill_switch_state = _to_bool(
        owner_input["kill_switch_state"], "kill_switch_state", notes
    )
    owner_attestation = _to_bool(
        owner_input["owner_attestation"], "owner_attestation", notes
    )
    demo_account_marker = str(owner_input["demo_account_marker"])
    broker_environment = str(owner_input["broker_environment"])
    runtime_objective_acknowledged = _to_bool(
        owner_input["runtime_objective_acknowledged"], "runtime_objective_acknowledged", notes
    )
    target_return_band_acknowledged = _to_bool(
        owner_input["target_return_band_acknowledged"],
        "target_return_band_acknowledged",
        notes,
    )
    profit_countdown_acknowledged = _to_bool(
        owner_input["profit_countdown_acknowledged"],
        "profit_countdown_acknowledged",
        notes,
    )
    live_profitable_week_target_acknowledged = _to_bool(
        owner_input["live_profitable_week_target_acknowledged"],
        "live_profitable_week_target_acknowledged",
        notes,
    )
    vacation_mode_target_acknowledged = _to_bool(
        owner_input["vacation_mode_target_acknowledged"],
        "vacation_mode_target_acknowledged",
        notes,
    )
    sos_alerts_acknowledged = _to_bool(
        owner_input["sos_alerts_acknowledged"], "sos_alerts_acknowledged", notes
    )

    result["input_notes"] = notes
    if baseline_equity <= 0:
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_INVALID_BASELINE"
        )
        result["controller_mode"] = "BLOCKED"
        result["publish_status"] = "NOT_READY_BLOCKED"
        result["input_validation_status"] = "BASELINE_EQUITY_INVALID"
        return result

    target_equity_100_percent = baseline_equity * 2.00
    target_equity_120_percent = baseline_equity * 2.20
    cumulative_profit_amount = current_equity - baseline_equity
    cumulative_return_percent = (cumulative_profit_amount / baseline_equity) * 100
    remaining_to_100_percent = max(0.0, 100 - cumulative_return_percent)
    remaining_to_120_percent = max(0.0, 120 - cumulative_return_percent)

    result.update(
        {
            "controller_status": "FOREX_CONTINUOUS_CONTROLLER_READY_FOR_FLOW_1",
            "controller_mode": "CONTINUE_READY",
            "profit_return_countdown_status": "COUNTDOWN_ACTIVE",
            "profit_return_rate_status": "COUNTDOWN_ACTIVE",
            "execution_status": "FLOW_1_READY",
            "publish_status": "READY_AFTER_HOST_VALIDATION",
            "next_required_flow": FLOW_1,
            "next_controller_action": "RUN_FLOW_1_AFTER_THIS_PACKET_LANDS",
            "input_validation_status": "CONTINUE_INPUT_VALID",
            "baseline_equity": baseline_equity,
            "current_equity": current_equity,
            "closed_trade_count": int(closed_trade_count),
            "open_trade_count": int(open_trade_count),
            "max_open_positions": int(max_open_positions),
            "current_drawdown_percent": current_drawdown_percent,
            "daily_realized_loss_percent": daily_realized_loss_percent,
            "weekly_realized_loss_percent": weekly_realized_loss_percent,
            "kill_switch_state": kill_switch_state,
            "target_equity_100_percent": target_equity_100_percent,
            "target_equity_120_percent": target_equity_120_percent,
            "cumulative_profit_amount": cumulative_profit_amount,
            "cumulative_return_percent": cumulative_return_percent,
            "remaining_to_100_percent": remaining_to_100_percent,
            "remaining_to_120_percent": remaining_to_120_percent,
            "target_100_reached": cumulative_return_percent >= 100,
            "target_120_reached": cumulative_return_percent >= 120,
            "milestone_alert": _milestone_alert(cumulative_return_percent),
            "drawdown_alert": _drawdown_alert(current_drawdown_percent),
            "owner_attestation": owner_attestation,
            "demo_account_marker": demo_account_marker,
            "broker_environment": broker_environment,
            "runtime_objective_acknowledged": runtime_objective_acknowledged,
            "target_return_band_acknowledged": target_return_band_acknowledged,
            "profit_countdown_acknowledged": profit_countdown_acknowledged,
            "live_profitable_week_target_acknowledged": (
                live_profitable_week_target_acknowledged
            ),
            "vacation_mode_target_acknowledged": vacation_mode_target_acknowledged,
            "sos_alerts_acknowledged": sos_alerts_acknowledged,
            "runtime_status": "NOT_ACTIVATED_PENDING_SUPERVISOR_GATE",
            "vacation_mode_status": "TARGET_DEFINED_NOT_ACTIVE",
            "sos_alert_integration_status": (
                "REQUIRED_NOT_ACTIVE"
                if not sos_alerts_acknowledged
                else "ACKNOWLEDGED_NOT_ACTIVE"
            ),
            "post_trade_countdown_update_required": True,
        }
    )

    if kill_switch_state:
        result["controller_status"] = (
            "FOREX_CONTINUOUS_CONTROLLER_KILL_SWITCH_BLOCKED"
        )
        result["controller_mode"] = "PAUSED"
        result["publish_status"] = "NOT_READY_STOP_REVIEW"
        result["next_controller_action"] = "OWNER_REVIEW_REQUIRED"
        result["execution_status"] = "BLOCKED_BY_KILL_SWITCH"
        result["input_notes"].append("KILL_SWITCH_STATE_ACTIVE")

    return result


def render_owner_report(result: Dict[str, Any]) -> str:
    missing_map_lines = [
        f"- {item['island_name']}: {item['why_it_blocks_real_money_progress']}"
        for item in result.get("missing_island_bridge_map", [])
    ]
    flow_lines = [
        f"- {flow['flow_id']}: {flow['name']}" for flow in result["compressed_flow_map"]
    ]
    return (
        "# AIOS Forex Continuous Bridge To Profit Controller V1 Report\n\n"
        "## Real Forex End-State\n"
        "The remaining flows operate under a governed profit-execution system with owner-facing checkpoints.\n\n"
        "## Current Verified Anchor\n"
        "P14 controlled flow is merged on main and is used as the starting verified anchor.\n\n"
        "## Controller Modes\n"
        f"Controller status: {result['controller_status']}\n\n"
        f"Controller mode: {result['controller_mode']}\n"
        f"Next required flow: {result['next_required_flow']}\n\n"
        "## Owner Live-Capital Intent\n"
        f"Owner live-capital intent: {result['owner_live_capital_intent_usd']} USD\n\n"
        "## Baseline Equity Rule\n"
        "Baseline equity is owner-supplied or broker snapshot derived. A fixed 10,000 baseline is not required.\n\n"
        "## Target Return Band: 100–120%\n"
        f"Target return band: {result['target_return_band']}\n"
        f"Target claim status: {result['target_return_claim_status']}\n"
        f"Profit return countdown status: {result['profit_return_countdown_status']}\n"
        f"Profit return rate status: {result['profit_return_rate_status']}\n\n"
        f"Remaining to 100: {result['remaining_to_100_percent']}\n"
        f"Remaining to 120: {result['remaining_to_120_percent']}\n"
        f"Cumulative return percent: {result['cumulative_return_percent']}\n\n"
        "## Milestone Alerts\n"
        f"Milestone alert: {result['milestone_alert']}\n\n"
        "## Drawdown Alerts\n"
        f"Current drawdown status: {result['drawdown_alert']}\n\n"
        "## Live Profitable Week Target\n"
        f"Live profitable week target status: {result['live_profitable_week_target_status']}\n\n"
        "## 22h/6d Runtime Objective\n"
        f"Runtime objective: {result['runtime_objective']}\n"
        f"Runtime status: {result['runtime_status']}\n\n"
        "## Vacation Mode Target\n"
        f"Vacation mode status: {result['vacation_mode_status']}\n\n"
        "## SOS Alert Integration\n"
        f"SOS alert integration status: {result['sos_alert_integration_status']}\n\n"
        "## Missing Island Bridge Map\n"
        + "\n".join(missing_map_lines)
        + "\n\n"
        "## Compressed Remaining Flow Map\n"
        + "\n".join(flow_lines)
        + "\n\n"
        "## Host Validation Script\n"
        "scripts/forex_delivery/validate_forex_continuous_bridge_to_profit_controller_v1.ps1\n\n"
        "## Host Publish Script\n"
        "scripts/forex_delivery/publish_forex_continuous_bridge_to_profit_controller_v1.ps1\n\n"
        "## Blocked Actions\n"
        "- live trading\n"
        "- live API/broker access\n"
        "- demo order placement\n"
        "- money movement\n"
        "- autonomy activation\n\n"
        "## What This Completes\n"
        "Creates a repo-safe continuous controller with continue, pause, stop, and bridge support for remaining flow execution.\n\n"
        "## What This Does Not Approve\n"
        "No live readiness, no live profitable week proved, no activated 22h/6d runtime status.\n\n"
        "## Next Required Flow\n"
        f"{result['next_required_flow']}\n\n"
        "## Final Owner Sentence\n"
        "AIOS Forex continuous bridge-to-profit controller is consolidated locally: Codex now has a repo-safe stop/pause/continue/bridge controller for the remaining compressed Forex flows, "
        "the owner live-capital intent is $1,000, the target return band is 100–120% tracked from a dynamic baseline, "
        "and live trading, broker/API access, credentials, demo-order placement, execution command, 22h/6d runtime, "
        "vacation mode, autonomy, and money movement remain blocked until separately proven and approved.\n"
    )


def render_next_action_queue(result: Dict[str, Any]) -> str:
    bridge_names = [
        item["island_name"] for item in result.get("missing_island_bridge_map", [])
    ]
    return (
        "# AIOS Forex Continuous Bridge To Profit Controller Next Action Queue V1\n\n"
        "## Purpose\n"
        "Keep the controller advancing only in owner-sanctioned flow order.\n\n"
        "## Controller Status\n"
        f"{result['controller_status']}\n\n"
        "## Controller Mode\n"
        f"{result['controller_mode']}\n\n"
        "## Profit-Return Countdown Status\n"
        f"{result['profit_return_countdown_status']}\n\n"
        "## Runtime Status\n"
        f"{result['runtime_status']}\n\n"
        "## Vacation Mode Status\n"
        f"{result['vacation_mode_status']}\n\n"
        "## SOS Alert Status\n"
        f"{result['sos_alert_integration_status']}\n\n"
        "## Missing Islands\n"
        + "\n".join(f"- {name}" for name in bridge_names)
        + "\n\n"
        "## Next Required Flow\n"
        f"{result['next_required_flow']}\n\n"
        "## Required Next Actions\n"
        "- update artifact status with host validation\n"
        "- keep blocked actions disabled\n"
        "- keep owner approval gates explicit\n"
        "- keep no-duplicate-order proof in future evidence flows\n\n"
        "## Remaining Blocks\n"
        "- live and supervised-demo autonomy controls remain off\n"
        "- demo command execution remains blocked\n"
        "- scheduler and webhook activation remain blocked\n\n"
        "## Final Owner Sentence\n"
        "AIOS Forex continuous bridge-to-profit controller is consolidated locally: Codex now has a repo-safe stop/pause/continue/bridge controller for the remaining compressed Forex flows, "
        "the owner live-capital intent is $1,000, the target return band is 100–120% tracked from a dynamic baseline, "
        "and live trading, broker/API access, credentials, demo-order placement, execution command, 22h/6d runtime, "
        "vacation mode, autonomy, and money movement remain blocked until separately proven and approved.\n"
    )


def generate_artifacts(owner_input: Dict[str, Any] | None = None) -> Dict[str, Any]:
    result = evaluate_forex_continuous_bridge_to_profit_controller(owner_input)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    result["missing_island_bridge_map"] = result.get(
        "missing_island_bridge_map"
    ) or build_missing_island_bridge_map(result)
    JSON_REPORT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    return result


if __name__ == "__main__":
    generate_artifacts()
