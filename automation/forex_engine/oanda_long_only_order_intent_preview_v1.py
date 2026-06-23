"""Build a broker-safe, non-executable OANDA long-only order intent preview."""
from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any

from automation.forex_engine.forex_trust_safety_audit_v1 import contains_sensitive_material

ORDER_INTENT_PREVIEW_BLOCKED = "ORDER_INTENT_PREVIEW_BLOCKED"
ORDER_INTENT_PREVIEW_READY = "ORDER_INTENT_PREVIEW_READY"

OANDA_DEMO_ENVIRONMENTS = frozenset({"demo", "sandbox", "practice"})
ALLOWED_MODES = frozenset({"DEMO_SANDBOX_ONLY", "PREPARATION_ONLY"})

REQUIRED_INTENT_FIELDS = (
    "candidate_id",
    "strategy_id",
    "broker_name",
    "broker_environment",
    "mode",
    "instrument",
    "direction",
    "units",
    "max_units",
    "order_side",
    "order_type",
    "stop_loss_required",
    "stop_loss_defined",
    "take_profit_required",
    "take_profit_defined",
    "one_order_only",
    "broker_proof_ready",
    "evidence_depth_ready",
    "risk_policy_ready",
    "owner_demo_order_approval_present",
    "owner_live_exception_present",
    "no_credentials_in_payload",
    "no_account_id_in_payload",
    "no_env_in_payload",
    "no_network_call",
    "no_broker_mutation",
    "no_order_execution",
    "sanitized_intent_only",
)

TRUE_REQUIRED_FIELDS = (
    "stop_loss_required",
    "stop_loss_defined",
    "take_profit_required",
    "take_profit_defined",
    "one_order_only",
    "broker_proof_ready",
    "evidence_depth_ready",
    "risk_policy_ready",
    "no_credentials_in_payload",
    "no_account_id_in_payload",
    "no_env_in_payload",
    "no_network_call",
    "no_broker_mutation",
    "no_order_execution",
    "sanitized_intent_only",
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


def _blocked(intent: Mapping[str, Any] | None, blockers: list[str]) -> dict[str, Any]:
    payload = intent if isinstance(intent, Mapping) else {}
    return {
        "status": ORDER_INTENT_PREVIEW_BLOCKED,
        "preview_ready": False,
        "candidate_id": payload.get("candidate_id"),
        "strategy_id": payload.get("strategy_id"),
        "instrument": payload.get("instrument"),
        "direction": payload.get("direction"),
        "order_side": payload.get("order_side"),
        "units": payload.get("units"),
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": [],
        "non_executable_preview": {},
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "broker_mutation_allowed": False,
        "order_execution_allowed": False,
        "next_safe_action": "repair_non_executable_order_intent_preview",
    }


def build_oanda_long_only_order_intent_preview(intent: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build a sanitized preview that is intentionally not sendable to a broker."""
    blockers: list[str] = []
    if not isinstance(intent, Mapping) or not intent:
        blockers.append("missing_order_intent")
        return _blocked(None, blockers)

    payload = dict(intent)
    for field in REQUIRED_INTENT_FIELDS:
        if field not in payload:
            blockers.append(f"missing_required_field:{field}")

    if contains_sensitive_material(payload):
        blockers.append("sensitive_material_detected")

    if "oanda" not in str(payload.get("broker_name", "")).strip().lower():
        blockers.append("broker_name_not_oanda")
    if str(payload.get("broker_environment", "")).strip().lower() not in OANDA_DEMO_ENVIRONMENTS:
        blockers.append("broker_environment_not_demo_sandbox_or_practice")
    if str(payload.get("mode", "")).strip().upper() not in ALLOWED_MODES:
        blockers.append("mode_not_demo_sandbox_or_preparation_only")
    if str(payload.get("direction", "")).strip().upper() != "LONG":
        blockers.append("direction_not_long")
    if str(payload.get("order_side", "")).strip().upper() != "BUY":
        blockers.append("order_side_not_buy")

    units = _finite_number(payload.get("units"))
    max_units = _finite_number(payload.get("max_units"))
    if units is None or units <= 0:
        blockers.append("invalid_units")
    if max_units is None or max_units <= 0:
        blockers.append("invalid_max_units")
    if units is not None and max_units is not None and units > max_units:
        blockers.append("units_exceed_max_units")

    for field in TRUE_REQUIRED_FIELDS:
        if not _to_bool(payload.get(field)):
            blockers.append(f"{field}_not_confirmed")
    if _to_bool(payload.get("owner_live_exception_present")):
        blockers.append("owner_live_exception_not_allowed_in_preview_packet")

    blockers = list(dict.fromkeys(blockers))
    if blockers:
        return _blocked(payload, blockers)

    non_executable_preview = {
        "preview_candidate_id": payload.get("candidate_id"),
        "preview_strategy_id": payload.get("strategy_id"),
        "preview_broker": "OANDA",
        "preview_environment": str(payload.get("broker_environment")).strip().lower(),
        "preview_mode": str(payload.get("mode")).strip().upper(),
        "preview_instrument": payload.get("instrument"),
        "preview_direction": "LONG",
        "preview_side": "BUY",
        "preview_units": int(units or 0),
        "preview_max_units": int(max_units or 0),
        "preview_order_style": str(payload.get("order_type", "")).strip().lower(),
        "preview_stop_loss_required": True,
        "preview_take_profit_required": True,
        "preview_one_order_only": True,
        "preview_owner_demo_approval_present": _to_bool(payload.get("owner_demo_order_approval_present")),
        "preview_non_executable": True,
    }
    return {
        "status": ORDER_INTENT_PREVIEW_READY,
        "preview_ready": True,
        "candidate_id": payload.get("candidate_id"),
        "strategy_id": payload.get("strategy_id"),
        "instrument": payload.get("instrument"),
        "direction": "LONG",
        "order_side": "BUY",
        "units": int(units or 0),
        "blockers": [],
        "warnings": [],
        "non_executable_preview": non_executable_preview,
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "broker_mutation_allowed": False,
        "order_execution_allowed": False,
        "next_safe_action": "review_demo_preview_only_no_order_authorization",
    }
