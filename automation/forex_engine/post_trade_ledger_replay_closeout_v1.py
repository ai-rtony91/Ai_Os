"""Post-trade ledger, replay, and closeout package V1."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from automation.forex_engine import final_live_operator_bridge_v1
from automation.forex_engine import live_preflight_evidence_bundle_v1
from automation.forex_engine import live_runtime_executor_v1
from automation.forex_engine import oanda_live_http_transport_v1
from automation.forex_engine import oanda_live_runtime_connector_v2
from automation.forex_engine import protected_live_execution_command_package_v1
from automation.forex_engine import protected_runtime_credential_injection_v1
from automation.forex_engine import single_protected_live_micro_trade_execution_package_v1


POST_TRADE_LEDGER_READY = "POST_TRADE_LEDGER_READY"
POST_TRADE_LEDGER_BLOCKED = "POST_TRADE_LEDGER_BLOCKED"
POST_TRADE_LEDGER_INVALID = "POST_TRADE_LEDGER_INVALID"
POST_TRADE_REPLAY_READY = "POST_TRADE_REPLAY_READY"
POST_TRADE_REPLAY_BLOCKED = "POST_TRADE_REPLAY_BLOCKED"
POST_TRADE_CLOSEOUT_READY = "POST_TRADE_CLOSEOUT_READY"
POST_TRADE_CLOSEOUT_BLOCKED = "POST_TRADE_CLOSEOUT_BLOCKED"
POST_TRADE_CLOSEOUT_INVALID = "POST_TRADE_CLOSEOUT_INVALID"
POST_TRADE_RESULT_FAKE_ONLY = "fake_only"
POST_TRADE_RESULT_REAL_REVIEW_REQUIRED = "real_review_required"

_POST_TRADE_SCHEMA = "AIOS_POST_TRADE_LEDGER_REPLAY_CLOSEOUT_V1"
_SENSITIVE_KEYS = frozenset(
    {
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "authorization",
        "secret",
        "password",
        "credential",
        "credentials",
        "account_id",
        "account_number",
        "live_account_id",
        "broker_order_id",
        "order_id",
        "orderid",
        "lasttransactionid",
        "last_transaction_id",
        "transaction_id",
        "raw_request",
        "raw_response",
        "raw_payload",
    }
)


def validate_post_trade_result_input(post_trade_result_input: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate injected post-trade evidence without claiming a real trade."""

    analysis = _analyze_post_trade_result_input(post_trade_result_input)
    status = analysis["validation_status"]
    return {
        "validation_schema": "AIOS_POST_TRADE_RESULT_INPUT_VALIDATION_V1",
        "status": status,
        "ready": status == POST_TRADE_LEDGER_READY,
        "blockers": analysis["blockers"],
        "trade_mode": analysis["trade_mode"],
        "execution_summary": analysis["execution_summary"],
        "risk_summary": analysis["risk_summary"],
        "broker_summary": analysis["broker_summary"],
        "result_summary": analysis["result_summary"],
        "safety_summary": analysis["safety_summary"],
        "sanitized_evidence": analysis["sanitized_evidence"],
        "integration_summary": analysis["integration_summary"],
        "pnl_known": analysis["pnl_known"],
        "realized_pnl": analysis["realized_pnl"],
        "operator_review_required": analysis["operator_review_required"],
        "next_safe_action": _next_validation_action(status),
        "protected_action_status": _protected_action_status(status),
    }


def build_post_trade_ledger_entry(post_trade_result_input: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build a sanitized post-trade ledger entry."""

    analysis = _analyze_post_trade_result_input(post_trade_result_input)
    status = _stage_status(
        ready_status=POST_TRADE_LEDGER_READY,
        blocked_status=POST_TRADE_LEDGER_BLOCKED,
        invalid_status=POST_TRADE_LEDGER_INVALID,
        analysis=analysis,
    )
    return {
        "ledger_schema": _POST_TRADE_SCHEMA,
        "ledger_status": status,
        "ready": status == POST_TRADE_LEDGER_READY,
        "blockers": analysis["blockers"],
        "trade_mode": analysis["trade_mode"],
        "order_intent_summary": analysis["order_intent_summary"],
        "execution_summary": analysis["execution_summary"],
        "risk_summary": analysis["risk_summary"],
        "broker_summary": analysis["broker_summary"],
        "result_summary": analysis["result_summary"],
        "safety_summary": analysis["safety_summary"],
        "sanitized_evidence": analysis["sanitized_evidence"],
        "next_safe_action": _next_ledger_action(status),
        "real_order_executed": bool(analysis["result_summary"].get("real_order_executed", False)),
        "fake_order_executed": bool(analysis["result_summary"].get("fake_order_executed", False)),
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
        "pnl_known": analysis["pnl_known"],
        "realized_pnl": analysis["realized_pnl"],
    }


def build_post_trade_replay_reconstruction(
    post_trade_result_input: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build a replay reconstruction from sanitized post-trade evidence."""

    analysis = _analyze_post_trade_result_input(post_trade_result_input)
    status = _stage_status(
        ready_status=POST_TRADE_REPLAY_READY,
        blocked_status=POST_TRADE_REPLAY_BLOCKED,
        invalid_status=POST_TRADE_LEDGER_INVALID,
        analysis=analysis,
        ready_override=analysis["trade_mode"] == POST_TRADE_RESULT_FAKE_ONLY
        and not analysis["blockers"],
    )
    observed_inputs = {
        "execution_package_state": analysis["observed_inputs"]["execution_package_state"],
        "execution_result": analysis["observed_inputs"]["execution_result"],
        "command_package_state": analysis["observed_inputs"]["command_package_state"],
        "preflight_bundle_state": analysis["observed_inputs"]["preflight_bundle_state"],
        "runtime_injection_state": analysis["observed_inputs"]["runtime_injection_state"],
        "transport_state": analysis["observed_inputs"]["transport_state"],
        "connector_state": analysis["observed_inputs"]["connector_state"],
        "final_bridge_state": analysis["observed_inputs"]["final_bridge_state"],
        "operator_review_state": analysis["observed_inputs"]["operator_review_state"],
    }
    decision_path = _replay_decision_path(analysis)
    return {
        "replay_schema": _POST_TRADE_SCHEMA,
        "replay_status": status,
        "ready": status == POST_TRADE_REPLAY_READY,
        "blockers": analysis["blockers"],
        "observed_inputs": observed_inputs,
        "decision_path": decision_path,
        "risk_controls": analysis["risk_controls"],
        "execution_controls": analysis["execution_controls"],
        "result_path": analysis["result_path"],
        "blocked_or_allowed_reason": _replay_reason(status, analysis),
        "fake_vs_real_classification": analysis["trade_mode"],
        "next_safe_action": _next_replay_action(status),
        "sanitized_evidence": analysis["sanitized_evidence"],
    }


def build_post_trade_closeout_summary(
    post_trade_result_input: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build the final closeout summary for fake-only Codex use."""

    analysis = _analyze_post_trade_result_input(post_trade_result_input)
    status = _closeout_status(analysis)
    return {
        "closeout_schema": _POST_TRADE_SCHEMA,
        "closeout_status": status,
        "ready": status == POST_TRADE_CLOSEOUT_READY,
        "result_classification": analysis["trade_mode"],
        "pnl_known": analysis["pnl_known"],
        "realized_pnl": analysis["realized_pnl"],
        "unresolved_fields": _closeout_unresolved_fields(analysis, status),
        "operator_review_required": analysis["operator_review_required"],
        "replay_ready": analysis["trade_mode"] == POST_TRADE_RESULT_FAKE_ONLY and not analysis["blockers"],
        "ledger_ready": analysis["trade_mode"] == POST_TRADE_RESULT_FAKE_ONLY and not analysis["blockers"],
        "mobile_summary_ready": True,
        "next_safe_action": _next_closeout_action(status),
        "project_completion_marker": _project_completion_marker(status, analysis),
        "sanitized_evidence": analysis["sanitized_evidence"],
    }


def build_post_trade_mobile_summary(
    post_trade_result_input: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build a compact Samsung/mobile truth summary for post-trade review."""

    analysis = _analyze_post_trade_result_input(post_trade_result_input)
    closeout = build_post_trade_closeout_summary(post_trade_result_input)
    status = closeout["closeout_status"]
    result_summary = analysis["result_summary"]
    return {
        "mode": "GOVERNED_POST_TRADE_LEDGER_REPLAY_CLOSEOUT_V1",
        "post_trade_status": status,
        "trade_mode": analysis["trade_mode"],
        "instrument": analysis["order_intent_summary"].get("instrument", "UNKNOWN"),
        "side": analysis["order_intent_summary"].get("side", "UNKNOWN"),
        "units": analysis["order_intent_summary"].get("units", "UNKNOWN"),
        "stop_loss": analysis["order_intent_summary"].get("stop_loss", "REQUIRED"),
        "take_profit": analysis["order_intent_summary"].get("take_profit", "REQUIRED"),
        "fake_order_executed": bool(result_summary.get("fake_order_executed", False)),
        "real_order_executed": bool(result_summary.get("real_order_executed", False)),
        "fake_broker_call_performed": bool(result_summary.get("fake_broker_call_performed", False)),
        "real_broker_call_performed": bool(result_summary.get("real_broker_call_performed", False)),
        "realized_pnl": closeout["realized_pnl"],
        "pnl_known": closeout["pnl_known"],
        "operator_review_required": closeout["operator_review_required"],
        "replay_ready": closeout["replay_ready"],
        "ledger_ready": closeout["ledger_ready"],
        "closeout_ready": closeout["ready"],
        "next_safe_action": closeout["next_safe_action"],
    }


def build_post_trade_completion_packet(
    post_trade_result_input: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build the final completion packet from sanitized post-trade evidence."""

    analysis = _analyze_post_trade_result_input(post_trade_result_input)
    ledger_entry = build_post_trade_ledger_entry(post_trade_result_input)
    replay_reconstruction = build_post_trade_replay_reconstruction(post_trade_result_input)
    closeout_summary = build_post_trade_closeout_summary(post_trade_result_input)
    mobile_summary = build_post_trade_mobile_summary(post_trade_result_input)
    status = _completion_status(analysis, closeout_summary)
    blockers = _unique(tuple(analysis["blockers"]) + tuple(closeout_summary["unresolved_fields"]))
    build_lane_completion = status == POST_TRADE_CLOSEOUT_READY and analysis["trade_mode"] == POST_TRADE_RESULT_FAKE_ONLY
    real_trade_completion = bool(
        analysis["result_summary"].get("real_order_executed", False)
        and analysis["result_summary"].get("real_broker_call_performed", False)
        and not analysis["blockers"]
        and closeout_summary["ready"]
    )
    return {
        "completion_schema": _POST_TRADE_SCHEMA,
        "status": status,
        "ready": status == POST_TRADE_CLOSEOUT_READY,
        "blockers": blockers,
        "ledger_entry": ledger_entry,
        "replay_reconstruction": replay_reconstruction,
        "closeout_summary": closeout_summary,
        "mobile_summary": mobile_summary,
        "safety_summary": analysis["safety_summary"],
        "protected_action_status": _protected_action_status(status),
        "next_safe_action": _next_completion_action(status, build_lane_completion, real_trade_completion),
        "build_lane_completion": build_lane_completion,
        "real_trade_completion": real_trade_completion,
        "sanitized_evidence": analysis["sanitized_evidence"],
    }


def sanitize_post_trade_evidence(payload: Any) -> dict[str, Any]:
    """Remove sensitive fields and keep fake-only Codex outputs sanitized."""

    return _sanitize_mapping(payload)


def classify_post_trade_blockers(post_trade_result_input: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Collect blockers for a post-trade result input."""

    return _analyze_post_trade_result_input(post_trade_result_input)["blockers"]


def _analyze_post_trade_result_input(post_trade_result_input: Mapping[str, Any] | None) -> dict[str, Any]:
    state = dict(post_trade_result_input or {})
    observed_inputs = {
        "execution_package_state": _mapping(state.get("execution_package_state")),
        "execution_result": _mapping(state.get("execution_result")),
        "command_package_state": _mapping(state.get("command_package_state")),
        "preflight_bundle_state": _mapping(state.get("preflight_bundle_state")),
        "runtime_injection_state": _mapping(state.get("runtime_injection_state")),
        "transport_state": _mapping(state.get("transport_state")),
        "connector_state": _mapping(state.get("connector_state")),
        "final_bridge_state": _mapping(state.get("final_bridge_state")),
        "operator_review_state": _mapping(state.get("operator_review_state")),
    }
    blockers: list[str] = []
    invalid = False

    if not state:
        blockers.append("post_trade_result_input_missing")
        invalid = True
    elif _contains_sensitive_keys(state):
        blockers.append("sensitive_post_trade_result_input_field_detected")
        invalid = True

    package_summary, package_blockers = _validate_execution_package_state(observed_inputs["execution_package_state"])
    command_summary, command_blockers = _validate_command_state(observed_inputs["command_package_state"])
    preflight_summary, preflight_blockers = _validate_preflight_state(observed_inputs["preflight_bundle_state"])
    runtime_summary, runtime_blockers = _validate_runtime_injection_state(observed_inputs["runtime_injection_state"])
    transport_summary, transport_blockers = _validate_transport_state(observed_inputs["transport_state"])
    connector_summary, connector_blockers = _validate_connector_state(observed_inputs["connector_state"])
    bridge_summary, bridge_blockers = _validate_final_bridge_state(observed_inputs["final_bridge_state"])
    execution_result_summary, execution_result_blockers = _validate_execution_result_state(
        observed_inputs["execution_result"]
    )
    operator_review_summary, operator_review_blockers = _validate_operator_review_state(
        observed_inputs["operator_review_state"]
    )

    blockers.extend(package_blockers)
    blockers.extend(command_blockers)
    blockers.extend(preflight_blockers)
    blockers.extend(runtime_blockers)
    blockers.extend(transport_blockers)
    blockers.extend(connector_blockers)
    blockers.extend(bridge_blockers)
    blockers.extend(execution_result_blockers)
    blockers.extend(operator_review_blockers)

    trade_mode = _trade_mode(execution_result_summary)
    if trade_mode == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED:
        blockers.append("real_review_path_required")
    if trade_mode == POST_TRADE_RESULT_FAKE_ONLY and execution_result_summary["real_trade_claimed"]:
        blockers.append("inconsistent_real_trade_claim")

    if package_summary["ready"] is False and "execution_package_state_missing" not in blockers:
        blockers.append("single_live_micro_trade_package_not_ready")
    if command_summary["ready"] is False and "command_package_state_missing" not in blockers:
        blockers.append("protected_command_not_ready")
    if preflight_summary["ready"] is False and "preflight_bundle_state_missing" not in blockers:
        blockers.append("live_preflight_not_ready")
    if runtime_summary["ready"] is False and "runtime_injection_state_missing" not in blockers:
        blockers.append("runtime_injection_not_ready")
    if transport_summary["ready"] is False and "transport_state_missing" not in blockers:
        blockers.append("oanda_transport_not_ready")
    if connector_summary["ready"] is False and "connector_state_missing" not in blockers:
        blockers.append("oanda_connector_not_ready")
    if bridge_summary["ready"] is False and "final_bridge_state_missing" not in blockers:
        blockers.append("final_bridge_not_ready")
    if execution_result_summary["ready"] is False and "execution_result_missing" not in blockers:
        blockers.append("fake_execution_result_not_submitted")
    if operator_review_summary["ready"] is False and "operator_review_state_missing" not in blockers:
        blockers.append("operator_review_required_false")

    if package_summary["real_order_executed"]:
        blockers.append("real_order_executed_true")
    if package_summary["real_broker_call_performed"]:
        blockers.append("real_broker_call_performed_true")
    if package_summary["order_executed"]:
        blockers.append("order_executed_true")
    if execution_result_summary["fake_order_executed"] is False and "execution_result_missing" not in blockers:
        blockers.append("fake_order_executed_required")
    if execution_result_summary["fake_broker_call_performed"] is False and "execution_result_missing" not in blockers:
        blockers.append("fake_broker_call_performed_required")
    if execution_result_summary["real_order_executed"] is True:
        blockers.append("real_order_executed_must_be_false_for_fake_path")
    if execution_result_summary["real_broker_call_performed"] is True:
        blockers.append("real_broker_call_performed_must_be_false_for_fake_path")
    if execution_result_summary["order_executed"] is True:
        blockers.append("order_executed_must_be_false_for_fake_path")
    if package_summary["credential_persisted"] or execution_result_summary["credential_persisted"]:
        blockers.append("credential_persisted_blocked")
    if package_summary["account_id_persisted"] or execution_result_summary["account_id_persisted"]:
        blockers.append("account_id_persisted_blocked")
    if package_summary["raw_broker_payload_persisted"] or execution_result_summary["raw_broker_payload_persisted"]:
        blockers.append("raw_broker_payload_persisted_blocked")

    # Allow a real-review-required path to remain classified while never being ready in Codex.
    if trade_mode == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED:
        blockers = _unique(blockers)
        validation_status = POST_TRADE_LEDGER_BLOCKED
    else:
        blockers = _unique(blockers)
        validation_status = POST_TRADE_LEDGER_READY if not blockers and not invalid else (
            POST_TRADE_LEDGER_INVALID if invalid else POST_TRADE_LEDGER_BLOCKED
        )

    risk_summary = {
        "single_live_micro_trade_package_ready": package_summary["ready"],
        "protected_command_sealed": command_summary["sealed"],
        "live_preflight_ready": preflight_summary["ready"],
        "runtime_injection_ready": runtime_summary["ready"],
        "oanda_transport_ready": transport_summary["ready"],
        "oanda_connector_ready": connector_summary["ready"],
        "final_bridge_ready": bridge_summary["ready"],
        "operator_review_required": operator_review_summary["operator_review_required"],
        "max_loss_gate_clear": preflight_summary["max_loss_gate_clear"],
        "daily_stop_clear": preflight_summary["daily_stop_clear"],
        "kill_switch_enabled": preflight_summary["kill_switch_enabled"],
        "one_trade_only": command_summary["one_trade_only"],
        "micro_size_only": command_summary["micro_size_only"],
    }
    risk_controls = {
        "single_live_micro_trade_package_ready": package_summary["ready"],
        "protected_command_sealed": command_summary["sealed"],
        "live_preflight_ready": preflight_summary["ready"],
        "runtime_injection_ready": runtime_summary["ready"],
        "oanda_transport_ready": transport_summary["ready"],
        "oanda_connector_ready": connector_summary["ready"],
        "final_bridge_ready": bridge_summary["ready"],
        "account_risk_ready": preflight_summary["account_risk_ready"],
        "instrument_ready": preflight_summary["instrument_ready"],
        "quote_spread_ready": preflight_summary["quote_spread_ready"],
        "order_intent_ready": preflight_summary["order_intent_ready"],
        "mobile_operator_ready": preflight_summary["mobile_operator_ready"],
        "max_loss_gate_clear": preflight_summary["max_loss_gate_clear"],
        "daily_stop_clear": preflight_summary["daily_stop_clear"],
        "kill_switch_enabled": preflight_summary["kill_switch_enabled"],
    }
    broker_summary = {
        "transport_ready": transport_summary["ready"],
        "connector_ready": connector_summary["ready"],
        "fake_broker_call_performed": execution_result_summary["fake_broker_call_performed"],
        "real_broker_call_performed": execution_result_summary["real_broker_call_performed"],
        "real_order_executed": execution_result_summary["real_order_executed"],
        "order_executed": execution_result_summary["order_executed"],
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
    }
    realized_pnl = _pnl_from_state(
        observed_inputs["operator_review_state"],
        observed_inputs["execution_result"],
        observed_inputs["execution_package_state"],
    )
    result_summary = {
        "result_classification": trade_mode,
        "fake_order_executed": execution_result_summary["fake_order_executed"],
        "fake_broker_call_performed": execution_result_summary["fake_broker_call_performed"],
        "real_order_executed": execution_result_summary["real_order_executed"],
        "real_broker_call_performed": execution_result_summary["real_broker_call_performed"],
        "order_executed": execution_result_summary["order_executed"],
        "pnl_known": realized_pnl is not None,
        "realized_pnl": realized_pnl,
    }
    result_summary["pnl_known"] = realized_pnl is not None
    result_summary["realized_pnl"] = realized_pnl
    result_path = {
        "trade_mode": trade_mode,
        "result_classification": trade_mode,
        "fake_order_executed": execution_result_summary["fake_order_executed"],
        "fake_broker_call_performed": execution_result_summary["fake_broker_call_performed"],
        "real_order_executed": execution_result_summary["real_order_executed"],
        "real_broker_call_performed": execution_result_summary["real_broker_call_performed"],
        "order_executed": execution_result_summary["order_executed"],
        "pnl_known": realized_pnl is not None,
        "realized_pnl": realized_pnl,
        "operator_review_required": operator_review_summary["operator_review_required"],
    }

    execution_controls = {
        "fake_order_executed": execution_result_summary["fake_order_executed"],
        "fake_broker_call_performed": execution_result_summary["fake_broker_call_performed"],
        "real_order_executed": execution_result_summary["real_order_executed"],
        "real_broker_call_performed": execution_result_summary["real_broker_call_performed"],
        "order_executed": execution_result_summary["order_executed"],
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
    }
    safety_summary = {
        "fake_only_trade_mode": trade_mode == POST_TRADE_RESULT_FAKE_ONLY,
        "real_review_required_trade_mode": trade_mode == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED,
        "ledger_ready": validation_status == POST_TRADE_LEDGER_READY,
        "replay_ready": validation_status == POST_TRADE_LEDGER_READY and trade_mode == POST_TRADE_RESULT_FAKE_ONLY,
        "closeout_ready": validation_status == POST_TRADE_LEDGER_READY and realized_pnl is not None,
        "operator_review_required": operator_review_summary["operator_review_required"],
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
        "real_order_executed": execution_result_summary["real_order_executed"],
        "real_broker_call_performed": execution_result_summary["real_broker_call_performed"],
        "order_executed": execution_result_summary["order_executed"],
    }
    order_intent_summary = _order_intent_summary(
        observed_inputs["execution_package_state"],
        observed_inputs["command_package_state"],
        observed_inputs["preflight_bundle_state"],
        observed_inputs["final_bridge_state"],
    )
    sanitized_evidence = sanitize_post_trade_evidence(
        {
            "execution_package_state": observed_inputs["execution_package_state"],
            "execution_result": observed_inputs["execution_result"],
            "command_package_state": observed_inputs["command_package_state"],
            "preflight_bundle_state": observed_inputs["preflight_bundle_state"],
            "runtime_injection_state": observed_inputs["runtime_injection_state"],
            "transport_state": observed_inputs["transport_state"],
            "connector_state": observed_inputs["connector_state"],
            "final_bridge_state": observed_inputs["final_bridge_state"],
            "operator_review_state": observed_inputs["operator_review_state"],
            "trade_mode": trade_mode,
            "realized_pnl": realized_pnl,
        }
    )

    return {
        "analysis_schema": _POST_TRADE_SCHEMA,
        "validation_status": validation_status,
        "blockers": blockers,
        "trade_mode": trade_mode,
        "execution_package_state": observed_inputs["execution_package_state"],
        "command_package_state": observed_inputs["command_package_state"],
        "preflight_bundle_state": observed_inputs["preflight_bundle_state"],
        "runtime_injection_state": observed_inputs["runtime_injection_state"],
        "transport_state": observed_inputs["transport_state"],
        "connector_state": observed_inputs["connector_state"],
        "final_bridge_state": observed_inputs["final_bridge_state"],
        "execution_result_state": observed_inputs["execution_result"],
        "operator_review_state": observed_inputs["operator_review_state"],
        "execution_package_summary": package_summary,
        "command_summary": command_summary,
        "preflight_summary": preflight_summary,
        "runtime_summary": runtime_summary,
        "transport_summary": transport_summary,
        "connector_summary": connector_summary,
        "bridge_summary": bridge_summary,
        "execution_result_summary": execution_result_summary,
        "operator_review_summary": operator_review_summary,
        "execution_summary": {
            "single_live_micro_trade_package_ready": package_summary["ready"],
            "single_live_micro_trade_package_status": package_summary["status"],
            "fake_execution_available": package_summary["fake_execution_available"],
            "fake_order_executed": execution_result_summary["fake_order_executed"],
            "fake_broker_call_performed": execution_result_summary["fake_broker_call_performed"],
            "real_order_executed": execution_result_summary["real_order_executed"],
            "real_broker_call_performed": execution_result_summary["real_broker_call_performed"],
            "order_executed": execution_result_summary["order_executed"],
            "credential_persisted": False,
            "account_id_persisted": False,
            "raw_broker_payload_persisted": False,
        },
        "risk_summary": risk_summary,
        "risk_controls": risk_controls,
        "broker_summary": broker_summary,
        "result_summary": result_summary,
        "result_path": result_path,
        "execution_controls": execution_controls,
        "order_intent_summary": order_intent_summary,
        "safety_summary": safety_summary,
        "sanitized_evidence": sanitized_evidence,
        "integration_summary": _integration_summary(),
        "pnl_known": realized_pnl is not None,
        "realized_pnl": realized_pnl,
        "operator_review_required": operator_review_summary["operator_review_required"],
        "observed_inputs": observed_inputs,
        "ready": validation_status == POST_TRADE_LEDGER_READY,
    }


def _validate_execution_package_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    package = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(package.get("ready", False)),
        "status": str(package.get("status", "")).strip(),
        "fake_execution_available": bool(package.get("fake_execution_available", False)),
        "real_order_executed": bool(package.get("real_order_executed", False)),
        "real_broker_call_performed": bool(package.get("real_broker_call_performed", False)),
        "order_executed": bool(package.get("order_executed", False)),
        "credential_persisted": bool(package.get("credential_persisted", False)),
        "account_id_persisted": bool(package.get("account_id_persisted", False)),
        "raw_broker_payload_persisted": bool(package.get("raw_broker_payload_persisted", False)),
    }
    if not package:
        blockers.append("execution_package_state_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(package):
        blockers.append("sensitive_execution_package_state_field_detected")
    if summary["ready"] is not True:
        blockers.append("single_live_micro_trade_package_not_ready")
    if summary["status"] != single_protected_live_micro_trade_execution_package_v1.SINGLE_LIVE_MICRO_TRADE_READY:
        blockers.append("single_live_micro_trade_package_status_not_ready")
    if bool(package.get("fake_execution_available", True)) is not True:
        blockers.append("fake_execution_not_available")
    if summary["real_order_executed"] is not False:
        blockers.append("real_order_executed_true")
    if summary["real_broker_call_performed"] is not False:
        blockers.append("real_broker_call_performed_true")
    if summary["order_executed"] is not False:
        blockers.append("order_executed_true")
    if summary["credential_persisted"] is not False:
        blockers.append("credential_persisted_blocked")
    if summary["account_id_persisted"] is not False:
        blockers.append("account_id_persisted_blocked")
    if summary["raw_broker_payload_persisted"] is not False:
        blockers.append("raw_broker_payload_persisted_blocked")

    integration = _mapping(package.get("integration_summary"))
    if integration:
        expected = _integration_summary()
        for key in (
            "protected_command_status",
            "live_preflight_status",
            "runtime_injection_status",
            "oanda_connector_status",
            "oanda_transport_status",
            "final_bridge_status",
            "executor_request_status",
            "uses_sanitized_readiness_shapes_only",
        ):
            if key in integration and integration.get(key) != expected.get(key):
                blockers.append(f"execution_package_{key}_not_ready")

    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _validate_command_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    command = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(command.get("ready", False)),
        "status": str(command.get("command_status", command.get("status", ""))).strip(),
        "sealed": str(command.get("sealed", "")) == protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_SEALED,
        "execution_allowed": bool(command.get("execution_allowed", False)),
        "order_executed": bool(command.get("order_executed", False)),
        "broker_call_performed": bool(command.get("broker_call_performed", False)),
        "credential_persisted": bool(command.get("credential_persisted", False)),
        "account_id_persisted": bool(command.get("account_id_persisted", False)),
        "raw_broker_payload_persisted": bool(command.get("raw_broker_payload_persisted", False)),
        "one_trade_only": bool(_mapping(command.get("sanitized_command")).get("one_trade_only", False)),
        "micro_size_only": bool(_mapping(command.get("sanitized_command")).get("micro_size_only", False)),
    }
    if not command:
        blockers.append("command_package_state_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(command):
        blockers.append("sensitive_command_package_state_field_detected")

    sanitized_command = _mapping(command.get("sanitized_command"))
    preflight_summary = _mapping(command.get("preflight_summary"))
    if summary["ready"] is not True:
        blockers.append("protected_command_not_ready")
    if not summary["sealed"]:
        blockers.append("protected_command_not_sealed")
    if summary["status"] != protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_SEALED:
        blockers.append("protected_command_status_not_sealed")
    if bool(sanitized_command.get("execution_allowed", False)) is not False:
        blockers.append("execution_allowed_must_remain_false")
    if bool(sanitized_command.get("execution_requested", False)) is not False:
        blockers.append("execution_requested_must_remain_false")
    if bool(sanitized_command.get("order_executed", False)) is not False:
        blockers.append("order_executed_must_remain_false")
    if bool(sanitized_command.get("broker_call_performed", False)) is not False:
        blockers.append("broker_call_performed_must_remain_false")
    if bool(sanitized_command.get("credential_persisted", False)) is not False:
        blockers.append("credential_persisted_blocked")
    if bool(sanitized_command.get("account_id_persisted", False)) is not False:
        blockers.append("account_id_persisted_blocked")
    if bool(sanitized_command.get("raw_broker_payload_persisted", False)) is not False:
        blockers.append("raw_broker_payload_persisted_blocked")
    if bool(preflight_summary.get("live_preflight_ready", False)) is not True:
        blockers.append("live_preflight_not_ready")
    if bool(preflight_summary.get("final_bridge_ready", False)) is not True:
        blockers.append("final_bridge_not_ready")
    if bool(preflight_summary.get("runtime_injection_ready", False)) is not True:
        blockers.append("runtime_injection_not_ready")
    if bool(preflight_summary.get("oanda_connector_ready", False)) is not True:
        blockers.append("oanda_connector_not_ready")
    if bool(preflight_summary.get("oanda_transport_ready", False)) is not True:
        blockers.append("oanda_transport_not_ready")
    if bool(preflight_summary.get("account_risk_ready", False)) is not True:
        blockers.append("account_risk_not_ready")
    if bool(preflight_summary.get("instrument_ready", False)) is not True:
        blockers.append("instrument_not_ready")
    if bool(preflight_summary.get("quote_spread_ready", False)) is not True:
        blockers.append("quote_spread_not_ready")
    if bool(preflight_summary.get("order_intent_ready", False)) is not True:
        blockers.append("order_intent_not_ready")
    if bool(preflight_summary.get("mobile_operator_ready", False)) is not True:
        blockers.append("mobile_operator_not_ready")
    if bool(preflight_summary.get("max_loss_gate_clear", False)) is not True:
        blockers.append("max_loss_gate_not_clear")
    if bool(preflight_summary.get("daily_stop_clear", False)) is not True:
        blockers.append("daily_stop_not_clear")
    if bool(preflight_summary.get("kill_switch_enabled", False)) is not False:
        blockers.append("kill_switch_enabled")

    integration = _mapping(command.get("integration_summary"))
    if integration:
        expected = _integration_summary()
        for key in (
            "live_preflight_status",
            "runtime_injection_status",
            "oanda_connector_status",
            "oanda_transport_status",
            "final_bridge_status",
            "executor_request_status",
            "uses_sanitized_readiness_shapes_only",
        ):
            if key in integration and integration.get(key) != expected.get(key):
                blockers.append(f"command_{key}_not_ready")

    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _validate_preflight_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    preflight = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(preflight.get("ready", False)),
        "status": str(preflight.get("status", preflight.get("preflight_status", ""))).strip(),
        "execution_allowed": bool(preflight.get("execution_allowed", False)),
        "order_executed": bool(preflight.get("order_executed", False)),
        "broker_call_performed": bool(preflight.get("broker_call_performed", False)),
    }
    component_status = _mapping(preflight.get("component_status"))
    account = _mapping(component_status.get("account"))
    instrument = _mapping(component_status.get("instrument"))
    quote = _mapping(component_status.get("quote_spread"))
    order = _mapping(component_status.get("order_intent"))
    if not preflight:
        blockers.append("preflight_bundle_state_missing")
        summary["ready"] = False
        summary["max_loss_gate_clear"] = True
        summary["daily_stop_clear"] = True
        summary["kill_switch_enabled"] = False
        summary["account_risk_ready"] = False
        summary["instrument_ready"] = False
        summary["quote_spread_ready"] = False
        summary["order_intent_ready"] = False
        summary["mobile_operator_ready"] = False
        summary["final_bridge_ready"] = False
        summary["runtime_injection_ready"] = False
        summary["oanda_connector_ready"] = False
        summary["oanda_transport_ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(preflight):
        blockers.append("sensitive_preflight_bundle_state_field_detected")
    if summary["ready"] is not True:
        blockers.append("live_preflight_not_ready")
    if summary["status"] != live_preflight_evidence_bundle_v1.LIVE_PREFLIGHT_EVIDENCE_READY:
        blockers.append("live_preflight_status_not_ready")
    if bool(preflight.get("execution_allowed", False)) is not False:
        blockers.append("execution_allowed_must_remain_false")
    if bool(preflight.get("order_executed", False)) is not False:
        blockers.append("order_executed_must_remain_false")
    if bool(preflight.get("broker_call_performed", False)) is not False:
        blockers.append("broker_call_performed_must_remain_false")
    if bool(preflight.get("credential_persisted", False)) is not False:
        blockers.append("credential_persisted_blocked")
    if bool(preflight.get("account_id_persisted", False)) is not False:
        blockers.append("account_id_persisted_blocked")
    if bool(preflight.get("raw_broker_payload_persisted", False)) is not False:
        blockers.append("raw_broker_payload_persisted_blocked")
    if component_status:
        if bool(component_status.get("final_bridge_ready", False)) is not True:
            blockers.append("final_bridge_not_ready")
        if bool(component_status.get("runtime_injection_ready", False)) is not True:
            blockers.append("runtime_injection_not_ready")
        if bool(component_status.get("oanda_connector_ready", False)) is not True:
            blockers.append("oanda_connector_not_ready")
        if bool(component_status.get("oanda_transport_ready", False)) is not True:
            blockers.append("oanda_transport_not_ready")
        if bool(component_status.get("mobile_operator_ready", False)) is not True:
            blockers.append("mobile_operator_not_ready")
        if not account.get("ready", False):
            blockers.extend(tuple(account.get("blockers", ())))
        if not instrument.get("ready", False):
            blockers.extend(tuple(instrument.get("blockers", ())))
        if not quote.get("ready", False):
            blockers.extend(tuple(quote.get("blockers", ())))
        if not order.get("ready", False):
            blockers.extend(tuple(order.get("blockers", ())))

    summary["ready"] = not blockers
    summary["max_loss_gate_clear"] = bool(component_status.get("order_intent", {}).get("sanitized_evidence", {}).get("max_loss_gate_clear", True))
    summary["daily_stop_clear"] = bool(component_status.get("order_intent", {}).get("sanitized_evidence", {}).get("daily_stop_clear", True))
    summary["kill_switch_enabled"] = bool(component_status.get("account", {}).get("sanitized_evidence", {}).get("kill_switch_enabled", False))
    summary["account_risk_ready"] = bool(component_status.get("account", {}).get("ready", False))
    summary["instrument_ready"] = bool(component_status.get("instrument", {}).get("ready", False))
    summary["quote_spread_ready"] = bool(component_status.get("quote_spread", {}).get("ready", False))
    summary["order_intent_ready"] = bool(component_status.get("order_intent", {}).get("ready", False))
    summary["mobile_operator_ready"] = bool(component_status.get("mobile_operator_ready", False))
    summary["final_bridge_ready"] = bool(component_status.get("final_bridge_ready", False))
    summary["runtime_injection_ready"] = bool(component_status.get("runtime_injection_ready", False))
    summary["oanda_connector_ready"] = bool(component_status.get("oanda_connector_ready", False))
    summary["oanda_transport_ready"] = bool(component_status.get("oanda_transport_ready", False))
    return summary, tuple(_unique(blockers))


def _validate_runtime_injection_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    injection = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(injection.get("ready", False)),
        "status": str(injection.get("status", injection.get("validation_status", ""))).strip(),
        "credentials_runtime_only": False,
        "allow_live_network_once": False,
        "one_trade_only": False,
        "micro_size_only": False,
        "no_retry": False,
        "no_loop": False,
        "runtime_auth_provider_injected": False,
        "http_client_injected": False,
        "final_bridge_ready": False,
        "oanda_transport_ready": False,
        "oanda_connector_ready": False,
        "credential_persisted": bool(injection.get("credential_persisted", False)),
        "account_id_persisted": bool(injection.get("account_id_persisted", False)),
        "raw_broker_payload_persisted": bool(injection.get("raw_broker_payload_persisted", False)),
    }
    if not injection:
        blockers.append("runtime_injection_state_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(injection):
        blockers.append("sensitive_runtime_injection_state_field_detected")
    sanitized = _mapping(injection.get("sanitized_summary"))
    if summary["status"] != protected_runtime_credential_injection_v1.PROTECTED_RUNTIME_INJECTION_READY:
        blockers.append("runtime_injection_not_ready")
    if summary["ready"] is not True:
        blockers.append("runtime_injection_not_ready")
    required_true = (
        ("authenticated_operator", "authenticated_operator_required"),
        ("protected_action_authorized", "protected_action_authorization_required"),
        ("live_exception_requested", "live_exception_request_required"),
        ("understands_live_risk_ack", "live_risk_ack_required"),
        ("operator_approved_live_runtime", "operator_live_runtime_approval_required"),
        ("credentials_runtime_only", "credentials_runtime_only_required"),
        ("allow_live_network_once", "allow_live_network_once_required"),
        ("one_trade_only", "one_trade_only_required"),
        ("micro_size_only", "micro_size_only_required"),
        ("no_retry", "no_retry_required"),
        ("no_loop", "no_loop_required"),
        ("runtime_auth_provider_injected", "runtime_auth_provider_injected_required"),
        ("http_client_injected", "http_client_injected_required"),
        ("final_bridge_ready", "final_bridge_ready_required"),
        ("oanda_transport_ready", "oanda_transport_ready_required"),
        ("oanda_connector_ready", "oanda_connector_ready_required"),
    )
    for key, blocker in required_true:
        if bool(sanitized.get(key, False)) is not True:
            blockers.append(blocker)
    for key, blocker in (("credentials_persisted", "credentials_persisted_blocked"), ("account_id_persisted", "account_id_persisted_blocked")):
        if bool(sanitized.get(key, False)) is not False:
            blockers.append(blocker)
    summary["credentials_runtime_only"] = bool(sanitized.get("credentials_runtime_only", False))
    summary["allow_live_network_once"] = bool(sanitized.get("allow_live_network_once", False))
    summary["one_trade_only"] = bool(sanitized.get("one_trade_only", False))
    summary["micro_size_only"] = bool(sanitized.get("micro_size_only", False))
    summary["no_retry"] = bool(sanitized.get("no_retry", False))
    summary["no_loop"] = bool(sanitized.get("no_loop", False))
    summary["runtime_auth_provider_injected"] = bool(sanitized.get("runtime_auth_provider_injected", False))
    summary["http_client_injected"] = bool(sanitized.get("http_client_injected", False))
    summary["final_bridge_ready"] = bool(sanitized.get("final_bridge_ready", False))
    summary["oanda_transport_ready"] = bool(sanitized.get("oanda_transport_ready", False))
    summary["oanda_connector_ready"] = bool(sanitized.get("oanda_connector_ready", False))
    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _validate_transport_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    transport = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(transport.get("ready", False)),
        "status": str(
            transport.get("readiness_status", transport.get("config_status", transport.get("status", "")))
        ).strip(),
        "http_client_injected": False,
        "runtime_auth_provider_injected": False,
        "stores_credentials": False,
        "stores_account_id": False,
    }
    if not transport:
        blockers.append("transport_state_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(transport):
        blockers.append("sensitive_transport_state_field_detected")
    capability = _mapping(transport.get("transport_capability_summary") or transport.get("capability_summary"))
    if summary["status"] not in {
        oanda_live_http_transport_v1.OANDA_LIVE_HTTP_TRANSPORT_READY,
        "",
    }:
        blockers.append("oanda_transport_not_ready")
    if summary["ready"] is not True:
        blockers.append("oanda_transport_not_ready")
    if capability:
        if bool(capability.get("supports_live_orders", False)) is not True:
            blockers.append("oanda_transport_not_ready")
        if bool(capability.get("supports_single_order_only", False)) is not True:
            blockers.append("oanda_transport_not_ready")
        if bool(capability.get("supports_micro_size_only", False)) is not True:
            blockers.append("oanda_transport_not_ready")
        if bool(capability.get("stores_credentials", False)) is not False:
            blockers.append("credential_persisted_blocked")
        if bool(capability.get("stores_account_id", False)) is not False:
            blockers.append("account_id_persisted_blocked")
        summary["http_client_injected"] = bool(capability.get("http_client_injected", False))
        summary["runtime_auth_provider_injected"] = bool(capability.get("runtime_auth_provider_injected", False))
        summary["stores_credentials"] = bool(capability.get("stores_credentials", False))
        summary["stores_account_id"] = bool(capability.get("stores_account_id", False))
    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _validate_connector_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    connector = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(connector.get("ready", False)),
        "status": str(connector.get("config_status", connector.get("status", ""))).strip(),
        "stores_credentials": False,
        "stores_account_id": False,
    }
    if not connector:
        blockers.append("connector_state_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(connector):
        blockers.append("sensitive_connector_state_field_detected")
    capability = _mapping(connector.get("connector_capability_summary") or connector.get("capability_summary"))
    if summary["status"] and summary["status"] != oanda_live_runtime_connector_v2.OANDA_LIVE_CONNECTOR_CONFIG_READY:
        blockers.append("oanda_connector_not_ready")
    if summary["ready"] is not True:
        blockers.append("oanda_connector_not_ready")
    if capability:
        if bool(capability.get("supports_live_orders", False)) is not True:
            blockers.append("oanda_connector_not_ready")
        if bool(capability.get("supports_single_order_only", False)) is not True:
            blockers.append("oanda_connector_not_ready")
        if bool(capability.get("supports_micro_size_only", False)) is not True:
            blockers.append("oanda_connector_not_ready")
        if bool(capability.get("stores_credentials", False)) is not False:
            blockers.append("credential_persisted_blocked")
        if bool(capability.get("stores_account_id", False)) is not False:
            blockers.append("account_id_persisted_blocked")
        summary["stores_credentials"] = bool(capability.get("stores_credentials", False))
        summary["stores_account_id"] = bool(capability.get("stores_account_id", False))
    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _validate_final_bridge_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    bridge = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(bridge.get("ready", False)),
        "status": str(bridge.get("bridge_status", bridge.get("status", ""))).strip(),
        "actual_credentials_supplied": bool(bridge.get("actual_credentials_supplied", False)),
        "actual_transport_injected": bool(bridge.get("actual_transport_injected", False)),
        "order_executed": bool(bridge.get("order_executed", False)),
        "broker_call_performed": bool(bridge.get("broker_call_performed", False)),
    }
    if not bridge:
        blockers.append("final_bridge_state_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(bridge):
        blockers.append("sensitive_final_bridge_state_field_detected")
    mobile = _mapping(bridge.get("mobile_summary"))
    if summary["status"] != final_live_operator_bridge_v1.FINAL_LIVE_OPERATOR_BRIDGE_READY:
        blockers.append("final_bridge_not_ready")
    if summary["ready"] is not True:
        blockers.append("final_bridge_not_ready")
    if bool(bridge.get("actual_credentials_supplied", False)) is not False:
        blockers.append("credentials_supplied_blocked")
    if bool(bridge.get("actual_transport_injected", False)) is not False:
        blockers.append("transport_injected_blocked")
    if bool(bridge.get("order_executed", False)) is not False:
        blockers.append("order_executed_true")
    if bool(bridge.get("broker_call_performed", False)) is not False:
        blockers.append("broker_call_performed_true")
    if mobile:
        if bool(mobile.get("dashboard_places_order", False)) is not False:
            blockers.append("dashboard_places_order_true")
        if bool(mobile.get("final_execution_requires_explicit_protected_live_action_authorization", False)) is not True:
            blockers.append("final_live_action_authorization_required")
    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _validate_execution_result_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    result = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(result.get("ready", False)),
        "status": str(result.get("status", result.get("execution_status", ""))).strip(),
        "fake_order_executed": bool(result.get("fake_order_executed", False)),
        "fake_broker_call_performed": bool(result.get("fake_broker_call_performed", False)),
        "real_order_executed": bool(result.get("real_order_executed", False)),
        "real_broker_call_performed": bool(result.get("real_broker_call_performed", False)),
        "order_executed": bool(result.get("order_executed", False)),
        "credential_persisted": bool(result.get("credential_persisted", False)),
        "account_id_persisted": bool(result.get("account_id_persisted", False)),
        "raw_broker_payload_persisted": bool(result.get("raw_broker_payload_persisted", False)),
        "real_trade_claimed": False,
    }
    if not result:
        blockers.append("execution_result_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(result):
        blockers.append("sensitive_execution_result_field_detected")
    summary["real_trade_claimed"] = bool(summary["real_order_executed"] and summary["real_broker_call_performed"])
    if summary["status"] != single_protected_live_micro_trade_execution_package_v1.SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED:
        blockers.append("fake_execution_result_not_submitted")
    if summary["ready"] is not True:
        blockers.append("fake_execution_result_not_submitted")
    if summary["fake_order_executed"] is not True:
        blockers.append("fake_order_executed_required")
    if summary["fake_broker_call_performed"] is not True:
        blockers.append("fake_broker_call_performed_required")
    if summary["real_order_executed"] is not False and not summary["real_trade_claimed"]:
        blockers.append("real_order_executed_must_be_false_for_fake_path")
    if summary["real_broker_call_performed"] is not False and not summary["real_trade_claimed"]:
        blockers.append("real_broker_call_performed_must_be_false_for_fake_path")
    if summary["order_executed"] is not False:
        blockers.append("order_executed_must_be_false_for_fake_path")
    if summary["credential_persisted"] is not False:
        blockers.append("credential_persisted_blocked")
    if summary["account_id_persisted"] is not False:
        blockers.append("account_id_persisted_blocked")
    if summary["raw_broker_payload_persisted"] is not False:
        blockers.append("raw_broker_payload_persisted_blocked")
    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _validate_operator_review_state(state: Mapping[str, Any] | None) -> tuple[dict[str, Any], tuple[str, ...]]:
    review = _mapping(state)
    blockers: list[str] = []
    summary = {
        "ready": bool(review.get("operator_review_required", False)),
        "operator_review_required": bool(review.get("operator_review_required", False)),
        "realized_pnl": _to_float_or_none(review.get("realized_pnl")),
        "review_status": str(review.get("review_status", review.get("status", ""))).strip(),
    }
    if not review:
        blockers.append("operator_review_state_missing")
        summary["ready"] = False
        return summary, tuple(blockers)
    if _contains_sensitive_keys(review):
        blockers.append("sensitive_operator_review_state_field_detected")
    if summary["operator_review_required"] is not True:
        blockers.append("operator_review_required_false")
    summary["ready"] = not blockers
    return summary, tuple(_unique(blockers))


def _order_intent_summary(
    execution_package_state: Mapping[str, Any],
    command_package_state: Mapping[str, Any],
    preflight_bundle_state: Mapping[str, Any],
    final_bridge_state: Mapping[str, Any],
) -> dict[str, Any]:
    package = _mapping(execution_package_state)
    command = _mapping(command_package_state)
    preflight = _mapping(preflight_bundle_state)
    bridge = _mapping(final_bridge_state)
    order = _mapping(command.get("order_intent_summary"))
    if not order:
        order = _mapping(_mapping(preflight.get("component_status")).get("order_intent"))
        order = _mapping(order.get("sanitized_evidence")) if order else {}
    if not order:
        order = _mapping(_mapping(bridge.get("sanitized_arm_request")))
    if not order:
        order = _mapping(_mapping(package.get("order_intent_summary")))
    if not order:
        order = {}
    return sanitize_post_trade_evidence(
        {
            "instrument": order.get("instrument", "UNKNOWN"),
            "side": order.get("side", "UNKNOWN"),
            "units": order.get("units", "UNKNOWN"),
            "stop_loss": order.get("stop_loss", "REQUIRED"),
            "take_profit": order.get("take_profit", "REQUIRED"),
            "max_loss_gate_clear": bool(order.get("max_loss_gate_clear", True)),
            "daily_stop_clear": bool(order.get("daily_stop_clear", True)),
            "kill_switch_enabled": bool(order.get("kill_switch_enabled", False)),
            "one_trade_only": bool(order.get("one_trade_only", True)),
            "micro_size_only": bool(order.get("micro_size_only", True)),
        }
    )


def _trade_mode(execution_result_summary: Mapping[str, Any]) -> str:
    if bool(execution_result_summary.get("real_order_executed", False)) or bool(
        execution_result_summary.get("real_broker_call_performed", False)
    ):
        return POST_TRADE_RESULT_REAL_REVIEW_REQUIRED
    return POST_TRADE_RESULT_FAKE_ONLY


def _pnl_from_state(
    operator_review_state: Mapping[str, Any],
    execution_result_state: Mapping[str, Any],
    execution_package_state: Mapping[str, Any],
) -> float | None:
    for candidate in (
        operator_review_state.get("realized_pnl"),
        operator_review_state.get("realized_pl"),
        execution_result_state.get("realized_pnl"),
        execution_result_state.get("realized_pl"),
        execution_package_state.get("realized_pnl"),
        execution_package_state.get("realized_pl"),
        _mapping(operator_review_state.get("sanitized_summary")).get("realized_pnl"),
        _mapping(execution_result_state.get("sanitized_result_summary")).get("realized_pnl"),
    ):
        value = _to_float_or_none(candidate)
        if value is not None:
            return value
    return None


def _replay_decision_path(analysis: Mapping[str, Any]) -> tuple[str, ...]:
    if analysis["trade_mode"] == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED:
        return (
            "real_review_path_selected",
            "sanitized_evidence_only",
            "human_review_required_outside_codex",
        )
    return (
        "single_live_micro_trade_package_ready",
        "protected_command_sealed",
        "live_preflight_ready",
        "runtime_injection_ready",
        "oanda_transport_ready",
        "oanda_connector_ready",
        "final_bridge_ready",
        "fake_result_submitted",
        "fake_only_post_trade_path",
    )


def _replay_reason(status: str, analysis: Mapping[str, Any]) -> str:
    if status == POST_TRADE_REPLAY_READY:
        return "fake_only_post_trade_path_allowed"
    if analysis["trade_mode"] == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED:
        return "real_review_path_required_outside_codex"
    if "realized_pnl" in _closeout_unresolved_fields(analysis, POST_TRADE_CLOSEOUT_BLOCKED):
        return "realized_pnl_required_for_closeout"
    return analysis["blockers"][0] if analysis["blockers"] else "post_trade_replay_blocked"


def _closeout_unresolved_fields(analysis: Mapping[str, Any], status: str) -> tuple[str, ...]:
    unresolved: list[str] = []
    if analysis["trade_mode"] == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED:
        unresolved.append("real_review_required")
    if analysis["operator_review_required"] is not True:
        unresolved.append("operator_review_required")
    if analysis["pnl_known"] is not True:
        unresolved.append("realized_pnl")
    if status == POST_TRADE_CLOSEOUT_INVALID:
        unresolved.append("invalid_post_trade_input")
    return tuple(_unique(unresolved))


def _closeout_status(analysis: Mapping[str, Any]) -> str:
    if analysis["validation_status"] == POST_TRADE_LEDGER_INVALID:
        return POST_TRADE_CLOSEOUT_INVALID
    if analysis["trade_mode"] == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED:
        return POST_TRADE_CLOSEOUT_BLOCKED
    if analysis["operator_review_required"] is not True:
        return POST_TRADE_CLOSEOUT_BLOCKED
    if analysis["pnl_known"] is not True:
        return POST_TRADE_CLOSEOUT_BLOCKED
    if analysis["blockers"]:
        return POST_TRADE_CLOSEOUT_BLOCKED
    return POST_TRADE_CLOSEOUT_READY


def _completion_status(analysis: Mapping[str, Any], closeout_summary: Mapping[str, Any]) -> str:
    if analysis["validation_status"] == POST_TRADE_LEDGER_INVALID or closeout_summary["closeout_status"] == POST_TRADE_CLOSEOUT_INVALID:
        return POST_TRADE_CLOSEOUT_INVALID
    if analysis["validation_status"] == POST_TRADE_LEDGER_BLOCKED or closeout_summary["closeout_status"] == POST_TRADE_CLOSEOUT_BLOCKED:
        return POST_TRADE_CLOSEOUT_BLOCKED
    return POST_TRADE_CLOSEOUT_READY


def _project_completion_marker(status: str, analysis: Mapping[str, Any]) -> str:
    if status == POST_TRADE_CLOSEOUT_READY and analysis["trade_mode"] == POST_TRADE_RESULT_FAKE_ONLY:
        return "FAKE_POST_TRADE_BUILD_LANE_COMPLETE"
    if analysis["trade_mode"] == POST_TRADE_RESULT_REAL_REVIEW_REQUIRED:
        return "REAL_REVIEW_REQUIRED_OUTSIDE_CODEX"
    return "POST_TRADE_BUILD_LANE_PENDING"


def _protected_action_status(status: str) -> str:
    return {
        POST_TRADE_LEDGER_READY: "POST_TRADE_READY_FOR_OPERATOR_REVIEW",
        POST_TRADE_LEDGER_BLOCKED: "POST_TRADE_BLOCKED",
        POST_TRADE_LEDGER_INVALID: "POST_TRADE_INVALID",
        POST_TRADE_REPLAY_READY: "POST_TRADE_READY_FOR_REPLAY_REVIEW",
        POST_TRADE_REPLAY_BLOCKED: "POST_TRADE_BLOCKED",
        POST_TRADE_CLOSEOUT_READY: "POST_TRADE_READY_FOR_CLOSEOUT_REVIEW",
        POST_TRADE_CLOSEOUT_BLOCKED: "POST_TRADE_BLOCKED",
        POST_TRADE_CLOSEOUT_INVALID: "POST_TRADE_INVALID",
    }.get(status, "POST_TRADE_BLOCKED")


def _next_validation_action(status: str) -> str:
    return {
        POST_TRADE_LEDGER_READY: "stop_and_wait_for_human_post_trade_review",
        POST_TRADE_LEDGER_BLOCKED: "resolve_post_trade_input_blockers",
        POST_TRADE_LEDGER_INVALID: "provide_complete_sanitized_post_trade_input",
    }.get(status, "provide_complete_sanitized_post_trade_input")


def _next_ledger_action(status: str) -> str:
    return {
        POST_TRADE_LEDGER_READY: "stop_and_wait_for_replay_and_closeout_review",
        POST_TRADE_LEDGER_BLOCKED: "resolve_post_trade_ledger_blockers",
        POST_TRADE_LEDGER_INVALID: "provide_complete_sanitized_post_trade_input",
    }.get(status, "provide_complete_sanitized_post_trade_input")


def _next_replay_action(status: str) -> str:
    return {
        POST_TRADE_REPLAY_READY: "stop_and_wait_for_replay_review",
        POST_TRADE_REPLAY_BLOCKED: "resolve_post_trade_replay_blockers",
        POST_TRADE_LEDGER_INVALID: "provide_complete_sanitized_post_trade_input",
    }.get(status, "provide_complete_sanitized_post_trade_input")


def _next_closeout_action(status: str) -> str:
    return {
        POST_TRADE_CLOSEOUT_READY: "stop_and_wait_for_human_closeout_review",
        POST_TRADE_CLOSEOUT_BLOCKED: "resolve_post_trade_closeout_blockers",
        POST_TRADE_CLOSEOUT_INVALID: "provide_complete_sanitized_post_trade_input",
    }.get(status, "provide_complete_sanitized_post_trade_input")


def _next_completion_action(status: str, build_lane_completion: bool, real_trade_completion: bool) -> str:
    if real_trade_completion:
        return "route_real_trade_evidence_to_human_review_outside_codex"
    if build_lane_completion and status == POST_TRADE_CLOSEOUT_READY:
        return "stop_and_wait_for_human_review_or_archive_later"
    if status == POST_TRADE_CLOSEOUT_BLOCKED:
        return "resolve_post_trade_completion_blockers"
    return "provide_complete_sanitized_post_trade_input"


def _stage_status(
    ready_status: str,
    blocked_status: str,
    invalid_status: str,
    analysis: Mapping[str, Any],
    ready_override: bool | None = None,
) -> str:
    if analysis["validation_status"] == POST_TRADE_LEDGER_INVALID:
        return invalid_status
    if ready_override is True:
        return ready_status
    if analysis["validation_status"] == POST_TRADE_LEDGER_READY and not analysis["blockers"]:
        return ready_status
    return blocked_status


def _mapping(payload: Any) -> dict[str, Any]:
    if isinstance(payload, Mapping):
        return dict(payload)
    return {}


def _unique(values: Sequence[str] | list[str]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)


def _to_int(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        if isinstance(value, bool):
            return int(value)
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _to_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        if isinstance(value, bool):
            return float(int(value))
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, bool):
            return float(int(value))
        return float(value)
    except (TypeError, ValueError):
        return None


def _contains_sensitive_keys(payload: Any) -> bool:
    if not isinstance(payload, Mapping):
        return False
    for key, value in payload.items():
        normalized = str(key).lower().strip()
        if normalized in _SENSITIVE_KEYS:
            return True
        if isinstance(value, Mapping) and _contains_sensitive_keys(value):
            return True
        if isinstance(value, (list, tuple)):
            for item in value:
                if _contains_sensitive_keys(item):
                    return True
    return False


def _sanitize_mapping(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).lower().strip()
        if normalized in _SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[str(key)] = _sanitize_mapping(value)
        elif isinstance(value, (list, tuple)):
            sanitized[str(key)] = tuple(
                _sanitize_mapping(item) if isinstance(item, Mapping) else item for item in value
            )
        else:
            sanitized[str(key)] = value

    real_trade_claimed = bool(payload.get("real_order_executed", False)) and bool(
        payload.get("real_broker_call_performed", False)
    )
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    sanitized["real_order_executed"] = real_trade_claimed
    sanitized["real_broker_call_performed"] = real_trade_claimed
    sanitized["order_executed"] = bool(payload.get("order_executed", False)) if real_trade_claimed else False
    sanitized["broker_call_performed"] = bool(payload.get("broker_call_performed", False)) if real_trade_claimed else False
    sanitized["execution_allowed"] = False
    return sanitized


def _integration_summary() -> dict[str, Any]:
    return {
        "single_live_micro_trade_package_status": single_protected_live_micro_trade_execution_package_v1.SINGLE_LIVE_MICRO_TRADE_READY,
        "protected_command_status": protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_SEALED,
        "live_preflight_status": live_preflight_evidence_bundle_v1.LIVE_PREFLIGHT_EVIDENCE_READY,
        "runtime_injection_status": protected_runtime_credential_injection_v1.PROTECTED_RUNTIME_INJECTION_READY,
        "oanda_transport_status": oanda_live_http_transport_v1.OANDA_LIVE_HTTP_TRANSPORT_READY,
        "oanda_connector_status": oanda_live_runtime_connector_v2.OANDA_LIVE_CONNECTOR_CONFIG_READY,
        "final_bridge_status": final_live_operator_bridge_v1.FINAL_LIVE_OPERATOR_BRIDGE_READY,
        "executor_request_status": live_runtime_executor_v1.LIVE_RUNTIME_REQUEST_READY,
        "executor_execution_status": live_runtime_executor_v1.LIVE_RUNTIME_EXECUTION_READY,
        "executor_ledger_status": live_runtime_executor_v1.LIVE_RUNTIME_LEDGER_READY,
        "uses_sanitized_readiness_shapes_only": True,
    }
