"""Preparation-only long-only Forex risk policy contract.

The contract validates risk scaffolding for demo preparation. It does not size
from account balances, read credentials, call a broker, or execute orders.
"""
from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any

from automation.forex_engine.forex_trust_safety_audit_v1 import contains_sensitive_material

RISK_POLICY_CONTRACT_BLOCKED = "RISK_POLICY_CONTRACT_BLOCKED"
RISK_POLICY_CONTRACT_READY = "RISK_POLICY_CONTRACT_READY"

ALLOWED_MODES = frozenset({"DEMO_SANDBOX_ONLY", "PREPARATION_ONLY"})

REQUIRED_POLICY_FIELDS = (
    "policy_name",
    "policy_version",
    "mode",
    "long_only",
    "short_side_disabled",
    "instrument",
    "max_units_policy",
    "broker_max_units",
    "final_max_units",
    "stop_loss_required",
    "take_profit_required",
    "one_order_only",
    "kill_switch_required",
    "daily_loss_limit_required",
    "max_drawdown_limit_required",
    "manual_owner_approval_required_for_demo_order",
    "live_exception_required_for_live_order",
    "broker_proof_ready",
    "evidence_depth_ready",
    "no_credentials_required",
    "no_account_id_required",
    "no_network_required",
    "no_order_execution",
    "sanitized_policy_only",
)

TRUE_REQUIRED_FIELDS = (
    "long_only",
    "short_side_disabled",
    "stop_loss_required",
    "take_profit_required",
    "one_order_only",
    "kill_switch_required",
    "daily_loss_limit_required",
    "max_drawdown_limit_required",
    "manual_owner_approval_required_for_demo_order",
    "live_exception_required_for_live_order",
    "broker_proof_ready",
    "evidence_depth_ready",
    "no_credentials_required",
    "no_account_id_required",
    "no_network_required",
    "no_order_execution",
    "sanitized_policy_only",
)


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y", "on", "pass", "passed", "ready"}:
            return True
        if text in {"false", "0", "no", "n", "off", "fail", "failed", "blocked"}:
            return False
    return bool(value)


def _finite_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _blocked(policy: Mapping[str, Any] | None, blockers: list[str]) -> dict[str, Any]:
    payload = policy if isinstance(policy, Mapping) else {}
    return {
        "status": RISK_POLICY_CONTRACT_BLOCKED,
        "ready": False,
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": [],
        "policy_name": payload.get("policy_name"),
        "mode": payload.get("mode"),
        "final_max_units": payload.get("final_max_units"),
        "long_only": _to_bool(payload.get("long_only")),
        "short_side_disabled": _to_bool(payload.get("short_side_disabled")),
        "risk_policy_ready_for_demo_preparation": False,
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "next_safe_action": "repair_long_only_risk_policy_contract",
    }


def evaluate_long_only_risk_policy_contract(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    """Evaluate a sanitized preparation-only long-only risk policy."""
    blockers: list[str] = []
    if not isinstance(policy, Mapping) or not policy:
        blockers.append("missing_risk_policy_contract")
        return _blocked(None, blockers)

    payload = dict(policy)
    for field in REQUIRED_POLICY_FIELDS:
        if field not in payload:
            blockers.append(f"missing_required_field:{field}")

    if contains_sensitive_material(payload):
        blockers.append("sensitive_material_detected")

    if str(payload.get("mode", "")).strip().upper() not in ALLOWED_MODES:
        blockers.append("mode_not_demo_sandbox_or_preparation_only")

    for field in TRUE_REQUIRED_FIELDS:
        if not _to_bool(payload.get(field)):
            blockers.append(f"{field}_not_confirmed")

    max_units_policy = _finite_number(payload.get("max_units_policy"))
    broker_max_units = _finite_number(payload.get("broker_max_units"))
    final_max_units = _finite_number(payload.get("final_max_units"))

    if max_units_policy is None or max_units_policy <= 0:
        blockers.append("invalid_max_units_policy")
    if broker_max_units is None or broker_max_units <= 0:
        blockers.append("invalid_broker_max_units")
    if final_max_units is None or final_max_units <= 0:
        blockers.append("invalid_final_max_units")
    if (
        final_max_units is not None
        and max_units_policy is not None
        and final_max_units > max_units_policy
    ):
        blockers.append("final_max_units_exceeds_policy")
    if (
        final_max_units is not None
        and broker_max_units is not None
        and final_max_units > broker_max_units
    ):
        blockers.append("final_max_units_exceeds_broker_max")

    blockers = list(dict.fromkeys(blockers))
    if blockers:
        return _blocked(payload, blockers)

    return {
        "status": RISK_POLICY_CONTRACT_READY,
        "ready": True,
        "blockers": [],
        "warnings": [],
        "policy_name": payload.get("policy_name"),
        "mode": str(payload.get("mode")).strip().upper(),
        "final_max_units": int(final_max_units or 0),
        "long_only": True,
        "short_side_disabled": True,
        "risk_policy_ready_for_demo_preparation": True,
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "next_safe_action": "continue_to_non_executable_order_intent_preview",
    }
