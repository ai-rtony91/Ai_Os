"""Long-only autonomous Forex supervisor contract.

This module is a readiness contract around the existing final Forex gate. It
does not place orders, open broker connections, read credentials, read env
files, schedule work, or start background execution.
"""
from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine.consolidated_readiness_blocker_closure_v1 import (
    BLOCKED_BY_BROKER_GATE,
    BLOCKED_BY_POLICY,
    BLOCKED_BY_RISK,
    FINAL_DEFAULT_MAX_EFFECTIVE_LEVERAGE,
    FINAL_DEFAULT_MAX_LIVE_MICRO_UNITS,
    PROFITABLE_LIVE_BOT_READY,
    REQUIRE_MORE_EVIDENCE,
    build_profitable_live_bot_final_status,
)

AUTONOMOUS_DEMO_READY = "AUTONOMOUS_DEMO_READY"
AUTONOMOUS_BLOCKED_BY_BROKER_GATE = "AUTONOMOUS_BLOCKED_BY_BROKER_GATE"
AUTONOMOUS_BLOCKED_BY_POLICY = "AUTONOMOUS_BLOCKED_BY_POLICY"
AUTONOMOUS_BLOCKED_BY_RISK = "AUTONOMOUS_BLOCKED_BY_RISK"
AUTONOMOUS_REQUIRE_MORE_EVIDENCE = "AUTONOMOUS_REQUIRE_MORE_EVIDENCE"

AUTONOMOUS_MODE = "DEMO_SANDBOX_ONLY"
PACKET_ID = "AIOS-FOREX-LONG-ONLY-AUTONOMOUS-SUPERVISOR-V1"


def _to_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y", "on", "pass", "passed", "ready", "enabled"}:
            return True
        if text in {"false", "0", "no", "n", "off", "fail", "failed", "disabled"}:
            return False
    return bool(value)


def _to_int(value: Any, *, default: int = 0) -> int:
    try:
        if value is None:
            return int(default)
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _to_float(value: Any, *, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _normalise_side(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"buy", "long"}:
        return "LONG"
    if text in {"sell", "short"}:
        return "SHORT"
    return "UNKNOWN"


def _default_supervisor_contract(final_status: Mapping[str, Any]) -> dict[str, Any]:
    thresholds = final_status.get("thresholds") if isinstance(final_status.get("thresholds"), Mapping) else {}
    return {
        "trading_window_intent": {
            "hours_per_day": 22,
            "days_per_week": 6,
            "execution_enabled": False,
        },
        "mode": AUTONOMOUS_MODE,
        "demo_sandbox_only": True,
        "long_only_activation": True,
        "activation_side": "LONG",
        "short_side_enabled": False,
        "one_active_order_max": 1,
        "max_live_micro_units": _to_int(
            thresholds.get("max_live_micro_units"),
            default=FINAL_DEFAULT_MAX_LIVE_MICRO_UNITS,
        ),
        "effective_leverage_cap": _to_float(
            thresholds.get("max_effective_leverage"),
            default=FINAL_DEFAULT_MAX_EFFECTIVE_LEVERAGE,
        ),
        "stop_loss_required": True,
        "take_profit_required": True,
        "max_loss_cap_required": True,
        "daily_stop_cap_required": True,
        "kill_switch_required": True,
        "broker_gate_required": True,
        "policy_live_exception_gate_required": True,
        "audit_log_required": True,
        "operator_review_required_before_live": True,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "webhook_enabled": False,
        "background_execution": False,
    }


def _merge_contract(
    final_status: Mapping[str, Any],
    supervisor_contract: Mapping[str, Any] | None,
) -> dict[str, Any]:
    contract = _default_supervisor_contract(final_status)
    if not isinstance(supervisor_contract, Mapping):
        return contract

    overrides = dict(supervisor_contract)
    window = overrides.pop("trading_window_intent", None)
    if isinstance(window, Mapping):
        contract["trading_window_intent"].update(dict(window))
    contract.update(overrides)
    return contract


def _contract_blockers(contract: Mapping[str, Any], final_status: Mapping[str, Any]) -> dict[str, list[str]]:
    thresholds = final_status.get("thresholds") if isinstance(final_status.get("thresholds"), Mapping) else {}
    risk_blockers: list[str] = []
    broker_blockers: list[str] = []
    policy_blockers: list[str] = []

    window = contract.get("trading_window_intent") if isinstance(contract.get("trading_window_intent"), Mapping) else {}
    if _to_int(window.get("hours_per_day"), default=0) != 22:
        policy_blockers.append("autonomous_trading_window_hours_not_22")
    if _to_int(window.get("days_per_week"), default=0) != 6:
        policy_blockers.append("autonomous_trading_window_days_not_6")
    if _to_bool(window.get("execution_enabled"), default=False):
        policy_blockers.append("autonomous_window_execution_not_allowed")

    if str(contract.get("mode", "")).upper() != AUTONOMOUS_MODE:
        policy_blockers.append("demo_sandbox_mode_required")
    if not _to_bool(contract.get("demo_sandbox_only"), default=False):
        policy_blockers.append("demo_sandbox_only_required")
    if not _to_bool(contract.get("long_only_activation"), default=False):
        policy_blockers.append("long_only_activation_required")
    if _normalise_side(contract.get("activation_side")) != "LONG":
        policy_blockers.append("short_side_disabled")
    if _to_bool(contract.get("short_side_enabled"), default=False):
        policy_blockers.append("short_side_disabled")

    if _to_int(contract.get("one_active_order_max"), default=0) != 1:
        risk_blockers.append("one_active_order_max_not_one")

    inherited_max_units = _to_int(
        thresholds.get("max_live_micro_units"),
        default=FINAL_DEFAULT_MAX_LIVE_MICRO_UNITS,
    )
    max_live_micro_units = _to_int(contract.get("max_live_micro_units"), default=0)
    if max_live_micro_units <= 0 or max_live_micro_units > inherited_max_units:
        risk_blockers.append("max_live_micro_units_not_within_threshold")

    inherited_leverage_cap = _to_float(
        thresholds.get("max_effective_leverage"),
        default=FINAL_DEFAULT_MAX_EFFECTIVE_LEVERAGE,
    )
    effective_leverage_cap = _to_float(contract.get("effective_leverage_cap"), default=0.0)
    if effective_leverage_cap <= 0 or effective_leverage_cap > inherited_leverage_cap:
        risk_blockers.append("effective_leverage_cap_not_within_threshold")

    required_risk_fields = (
        ("stop_loss_required", "stop_loss_required"),
        ("take_profit_required", "take_profit_required"),
        ("max_loss_cap_required", "max_loss_cap_required"),
        ("daily_stop_cap_required", "daily_stop_cap_required"),
        ("kill_switch_required", "kill_switch_required"),
    )
    for field, blocker in required_risk_fields:
        if not _to_bool(contract.get(field), default=False):
            risk_blockers.append(blocker)

    if not _to_bool(contract.get("broker_gate_required"), default=False):
        broker_blockers.append("broker_gate_required")
    if not _to_bool(contract.get("policy_live_exception_gate_required"), default=False):
        policy_blockers.append("policy_live_exception_gate_required")
    if not _to_bool(contract.get("audit_log_required"), default=False):
        policy_blockers.append("audit_log_required")
    if not _to_bool(contract.get("operator_review_required_before_live"), default=False):
        policy_blockers.append("operator_review_required_before_live")

    for field in ("scheduler_enabled", "daemon_enabled", "webhook_enabled", "background_execution"):
        if _to_bool(contract.get(field), default=False):
            policy_blockers.append(f"{field}_not_allowed")

    return {
        "risk": list(dict.fromkeys(risk_blockers)),
        "broker": list(dict.fromkeys(broker_blockers)),
        "policy": list(dict.fromkeys(policy_blockers)),
    }


def _autonomous_status(blockers: Mapping[str, list[str]]) -> str:
    if blockers.get("evidence"):
        return AUTONOMOUS_REQUIRE_MORE_EVIDENCE
    if blockers.get("risk"):
        return AUTONOMOUS_BLOCKED_BY_RISK
    if blockers.get("broker"):
        return AUTONOMOUS_BLOCKED_BY_BROKER_GATE
    if blockers.get("policy"):
        return AUTONOMOUS_BLOCKED_BY_POLICY
    return AUTONOMOUS_DEMO_READY


def _next_safe_action(status: str) -> str:
    if status == AUTONOMOUS_DEMO_READY:
        return "prepare_operator_reviewed_demo_plan_only_no_execution"
    if status == AUTONOMOUS_REQUIRE_MORE_EVIDENCE:
        return "restore_profitable_evidence_and_walk_forward_gate"
    if status == AUTONOMOUS_BLOCKED_BY_RISK:
        return "resolve_risk_contract_before_any_demo_autonomy"
    if status == AUTONOMOUS_BLOCKED_BY_BROKER_GATE:
        return "provide_sanitized_demo_sandbox_broker_and_account_permission_proof"
    if status == AUTONOMOUS_BLOCKED_BY_POLICY:
        return "provide_owner_review_and_live_exception_policy_contracts"
    return "stop_before_autonomous_execution"


def _safe_runtime_flags(contract: Mapping[str, Any], final_status: Mapping[str, Any]) -> dict[str, bool]:
    base = final_status.get("safety") if isinstance(final_status.get("safety"), Mapping) else {}
    safety = {key: _to_bool(value, default=False) for key, value in base.items()}
    safety.update(
        {
            "paper_only": True,
            "demo_sandbox_only": True,
            "prepare_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "account_id_present": False,
            "network_used": False,
            "order_execution": False,
            "broker_mutation": False,
            "credential_read": False,
            "credential_write": False,
            "env_read": False,
            "account_id_read": False,
            "account_id_write": False,
            "demo_trading": False,
            "live_trading": False,
            "live_trading_authorized": False,
            "scheduler": False,
            "daemon": False,
            "webhook": False,
            "background_execution": False,
            "requested_scheduler_enabled": _to_bool(contract.get("scheduler_enabled"), default=False),
            "requested_daemon_enabled": _to_bool(contract.get("daemon_enabled"), default=False),
            "requested_webhook_enabled": _to_bool(contract.get("webhook_enabled"), default=False),
            "requested_background_execution": _to_bool(contract.get("background_execution"), default=False),
        }
    )
    return safety


def build_long_only_autonomous_supervisor_contract(
    *,
    final_status_payload: dict[str, Any] | None = None,
    final_status_result: dict[str, Any] | None = None,
    supervisor_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-executing long-only autonomous supervisor readiness contract."""
    final_status = dict(
        final_status_result
        if isinstance(final_status_result, Mapping)
        else build_profitable_live_bot_final_status(evidence_payload=final_status_payload)
    )
    contract = _merge_contract(final_status, supervisor_contract)
    local_blockers = _contract_blockers(contract, final_status)
    final_blockers = final_status.get("blockers") if isinstance(final_status.get("blockers"), Mapping) else {}

    blockers = {
        "evidence": list(final_blockers.get("evidence", [])),
        "risk": list(final_blockers.get("risk", [])) + local_blockers["risk"],
        "broker": list(final_blockers.get("broker", [])) + local_blockers["broker"],
        "policy": list(final_blockers.get("policy", [])) + local_blockers["policy"],
    }
    blockers = {key: list(dict.fromkeys(value)) for key, value in blockers.items()}
    status = _autonomous_status(blockers)
    safety = _safe_runtime_flags(contract, final_status)

    evidence_ready = not blockers["evidence"]
    risk_ready = not blockers["risk"]
    local_contract_safe_to_prepare = (
        _to_bool(contract.get("demo_sandbox_only"), default=False)
        and _to_bool(contract.get("long_only_activation"), default=False)
        and _normalise_side(contract.get("activation_side")) == "LONG"
        and not _to_bool(contract.get("short_side_enabled"), default=False)
        and _to_bool(contract.get("audit_log_required"), default=False)
        and _to_bool(contract.get("operator_review_required_before_live"), default=False)
        and _to_int(contract.get("one_active_order_max"), default=0) == 1
        and not safety["requested_scheduler_enabled"]
        and not safety["requested_daemon_enabled"]
        and not safety["requested_webhook_enabled"]
        and not safety["requested_background_execution"]
    )
    can_prepare_demo_plan = bool(evidence_ready and risk_ready and local_contract_safe_to_prepare)

    return {
        "packet_id": PACKET_ID,
        "status": status,
        "final_status": final_status.get("status"),
        "candidate_id": final_status.get("candidate_id"),
        "mode": AUTONOMOUS_MODE,
        "trading_window_intent": dict(contract["trading_window_intent"]),
        "contract": dict(contract),
        "readiness_gates": {
            "evidence_gate_cleared": bool(final_status.get("evidence_gate_cleared")),
            "risk_gate_cleared": not blockers["risk"],
            "broker_gate_cleared": not blockers["broker"],
            "policy_gate_cleared": not blockers["policy"],
            "final_live_for_keeps_ready": final_status.get("status") == PROFITABLE_LIVE_BOT_READY,
        },
        "long_only_status": "LONG_ONLY_ACTIVE",
        "activation_side": _normalise_side(contract.get("activation_side")),
        "short_side_enabled": False,
        "short_side_status": "SHORT_SIDE_DISABLED",
        "demo_sandbox_only": True,
        "can_prepare_demo_plan": can_prepare_demo_plan,
        "execution_allowed": False,
        "ready_to_execute": False,
        "live_autonomy_allowed": False,
        "live_autonomy_blocked": True,
        "demo_plan": {
            "candidate_id": final_status.get("candidate_id"),
            "side": "LONG",
            "mode": AUTONOMOUS_MODE,
            "prepare_only": True,
            "order_execution": False,
            "one_active_order_max": contract.get("one_active_order_max"),
            "max_live_micro_units": contract.get("max_live_micro_units"),
            "effective_leverage_cap": contract.get("effective_leverage_cap"),
        },
        "blockers": blockers,
        "safety": safety,
        "next_safe_action": _next_safe_action(status),
        "source_final_status_mode": final_status.get("mode"),
    }


def main() -> dict[str, Any]:  # pragma: no cover
    return build_long_only_autonomous_supervisor_contract()


if __name__ == "__main__":  # pragma: no cover
    print(main())
