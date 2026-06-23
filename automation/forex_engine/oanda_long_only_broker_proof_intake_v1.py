"""Sanitized OANDA long-only broker proof intake.

This module accepts an in-memory sanitized proof dictionary only. It never
reads credentials, env files, account identifiers, or broker resources, and it
never places demo or live orders.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import math
import re
from typing import Any, Iterable, Mapping

from automation.forex_engine.consolidated_readiness_blocker_closure_v1 import (
    _default_final_readiness_payload,
    build_profitable_live_bot_final_status,
    evaluate_account_permission_gate,
)
from automation.forex_engine.forex_trust_safety_audit_v1 import build_safety_audit_result
from automation.forex_engine.long_only_autonomous_supervisor_v1 import (
    build_long_only_autonomous_supervisor_contract,
)

OANDA_LONG_ONLY_BROKER_PROOF_READY = "OANDA_LONG_ONLY_BROKER_PROOF_READY"
OANDA_BROKER_PROOF_BLOCKED = "OANDA_BROKER_PROOF_BLOCKED"
PACKET_ID = "AIOS-FOREX-OANDA-LONG-ONLY-BROKER-PROOF-INTAKE-V1"

OANDA_DEMO_ENVIRONMENTS = frozenset({"demo", "sandbox", "practice"})
OANDA_MAX_EFFECTIVE_LEVERAGE = 2.0
OANDA_MAX_DEMO_PREVIEW_UNITS = 1000

SAFE_CURRENCY_PATTERN = re.compile(r"^[A-Za-z]{3}$")
SAFE_FOREX_INSTRUMENT_PATTERN = re.compile(r"^[A-Za-z]{3}([_/-]?[A-Za-z]{3})$")

REQUIRED_SANITIZED_FIELDS = (
    "broker_name",
    "broker_environment",
    "asset_class",
    "account_type",
    "account_currency",
    "margin_available_confirmed",
    "effective_leverage_limit",
    "long_permission",
    "short_permission",
    "fifo_required",
    "hedging_available",
    "instrument_tradable",
    "instrument",
    "max_units",
    "stop_loss_supported",
    "take_profit_supported",
    "order_type_supported",
    "one_order_only_supported",
    "demo_sandbox_order_preview_supported",
    "broker_house_restrictions",
    "proof_timestamp",
    "proof_source",
    "sanitized_evidence_only",
    "no_credentials_in_payload",
    "no_account_id_in_payload",
    "no_env_in_payload",
    "no_network_call",
    "no_broker_mutation",
    "no_order_execution",
)

TRUE_REQUIRED_FIELDS = (
    "margin_available_confirmed",
    "long_permission",
    "instrument_tradable",
    "stop_loss_supported",
    "take_profit_supported",
    "one_order_only_supported",
    "demo_sandbox_order_preview_supported",
    "sanitized_evidence_only",
    "no_credentials_in_payload",
    "no_account_id_in_payload",
    "no_env_in_payload",
    "no_network_call",
    "no_broker_mutation",
    "no_order_execution",
)

SENSITIVE_KEYS = frozenset(
    {
        "account_id",
        "account_number",
        "account_identifier",
        "accountid",
        "credential",
        "credentials",
        "api_key",
        "apikey",
        "token",
        "access_token",
        "password",
        "secret",
        "env",
        ".env",
    }
)

UNSAFE_TRUE_FLAGS = {
    "network_call": "network_call_detected",
    "network_call_performed": "network_call_detected",
    "broker_mutation": "broker_mutation_detected",
    "broker_call_performed": "broker_mutation_detected",
    "order_execution": "order_execution_detected",
    "order_execution_performed": "order_execution_detected",
    "demo_order_placed": "order_execution_detected",
    "live_order_placed": "order_execution_detected",
    "credential_read": "credential_read_detected",
    "credential_write": "credential_write_detected",
    "env_read": "env_read_detected",
    "env_write": "env_write_detected",
    "account_id_read": "account_id_read_detected",
    "account_id_write": "account_id_write_detected",
}


def _to_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if not text:
        return bool(default)
    if text in {"1", "true", "yes", "y", "on", "pass", "passed", "ready"}:
        return True
    if text in {"0", "false", "no", "n", "off", "fail", "failed", "blocked"}:
        return False
    return bool(value)


def _to_float(value: Any, *, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        number = float(value)
        return number if math.isfinite(number) else float(default)
    except (TypeError, ValueError):
        return float(default)


def _to_int(value: Any, *, default: int = 0) -> int:
    try:
        if value is None:
            return int(default)
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _is_unknown(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "unknown", "missing", "none", "null", "n/a", "na", "pending"}
    return False


def _lower_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _iter_keys(payload: Any) -> Iterable[str]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            yield str(key)
            yield from _iter_keys(value)
    elif isinstance(payload, (list, tuple)):
        for item in payload:
            yield from _iter_keys(item)


def _supported_order_type(value: Any, expected: str = "market") -> bool:
    expected = expected.lower()
    if isinstance(value, str):
        return value.strip().lower() == expected
    if isinstance(value, Iterable):
        return expected in {str(item).strip().lower() for item in value}
    return False


def _safe_currency(value: Any) -> bool:
    return isinstance(value, str) and bool(SAFE_CURRENCY_PATTERN.match(value.strip()))


def _safe_forex_instrument(value: Any) -> bool:
    return isinstance(value, str) and bool(SAFE_FOREX_INSTRUMENT_PATTERN.match(value.strip()))


def _valid_timestamp(value: Any) -> bool:
    if _is_unknown(value):
        return False
    text = str(value).strip()
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _restriction_blockers(value: Any) -> list[str]:
    if _is_unknown(value):
        return ["unknown_required_field:broker_house_restrictions"]
    if not isinstance(value, (list, tuple, set)):
        return ["broker_house_restrictions_not_list"]
    restrictions = {str(item).strip().lower() for item in value}
    blocking = {
        "trading_blocked",
        "orders_blocked",
        "forex_blocked",
        "instrument_blocked",
        "long_blocked",
        "stops_blocked",
        "take_profit_blocked",
        "preview_blocked",
    }
    return [f"broker_house_restriction:{item}" for item in sorted(restrictions & blocking)]


def _safe_payload_blockers(proof: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    audit = build_safety_audit_result(
        proof,
        allowed_keys=REQUIRED_SANITIZED_FIELDS,
        required_keys=REQUIRED_SANITIZED_FIELDS,
    )
    if audit["unknown_keys"]:
        blockers.append("unknown_fields_present")
        blockers.extend(f"unknown_field:{key}" for key in audit["unknown_keys"])
    if audit["rejected_keys"]:
        blockers.extend(f"sensitive_payload_key:{key.split('.')[-1].lower()}" for key in audit["rejected_keys"])
    if audit["sensitive_value_locations"]:
        blockers.append("sensitive_payload_value_detected")
    for key in _iter_keys(proof):
        normalized = key.strip().lower()
        if normalized in SENSITIVE_KEYS:
            blockers.append(f"sensitive_payload_key:{normalized}")

    for field, blocker in UNSAFE_TRUE_FLAGS.items():
        if _to_bool(proof.get(field), default=False):
            blockers.append(blocker)

    if not _to_bool(proof.get("no_credentials_in_payload"), default=False):
        blockers.append("credentials_in_payload_detected")
    if not _to_bool(proof.get("no_account_id_in_payload"), default=False):
        blockers.append("account_id_in_payload_detected")
    if not _to_bool(proof.get("no_env_in_payload"), default=False):
        blockers.append("env_in_payload_detected")
    if not _to_bool(proof.get("no_network_call"), default=False):
        blockers.append("network_call_detected")
    if not _to_bool(proof.get("no_broker_mutation"), default=False):
        blockers.append("broker_mutation_detected")
    if not _to_bool(proof.get("no_order_execution"), default=False):
        blockers.append("order_execution_detected")

    return list(dict.fromkeys(blockers))


def _account_permission_gate_from_proof(proof: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker_name": proof.get("broker_name"),
        "broker_environment": _lower_text(proof.get("broker_environment")),
        "asset_class": _lower_text(proof.get("asset_class")),
        "account_type": proof.get("account_type"),
        "account_currency": proof.get("account_currency"),
        "margin_available_confirmed": proof.get("margin_available_confirmed"),
        "effective_leverage_limit": proof.get("effective_leverage_limit"),
        "long_permission": proof.get("long_permission"),
        "short_permission": proof.get("short_permission"),
        "fifo_required": proof.get("fifo_required"),
        "hedging_available": proof.get("hedging_available"),
        "instrument_tradable": proof.get("instrument_tradable"),
        "max_units": proof.get("max_units"),
        "stop_loss_supported": proof.get("stop_loss_supported"),
        "take_profit_supported": proof.get("take_profit_supported"),
        "order_type_supported": proof.get("order_type_supported"),
        "one_order_only_supported": proof.get("one_order_only_supported"),
        "demo_sandbox_order_preview_supported": proof.get("demo_sandbox_order_preview_supported"),
        "broker_house_restrictions": list(proof.get("broker_house_restrictions") or []),
        "proof_timestamp": proof.get("proof_timestamp"),
        "proof_source": proof.get("proof_source"),
        "sanitized_evidence_only": proof.get("sanitized_evidence_only"),
        "activation_side": "long",
    }


def evaluate_oanda_long_only_broker_proof(
    proof_payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate sanitized OANDA long-only demo/sandbox broker proof."""
    proof = proof_payload if isinstance(proof_payload, Mapping) else {}
    blockers: list[str] = []

    if not proof:
        blockers.append("missing_oanda_broker_proof")

    for field in REQUIRED_SANITIZED_FIELDS:
        if field not in proof:
            blockers.append(f"missing_required_field:{field}")
        elif _is_unknown(proof.get(field)):
            blockers.append(f"unknown_required_field:{field}")

    if proof:
        broker_name = _lower_text(proof.get("broker_name"))
        if "oanda" not in broker_name:
            blockers.append("broker_name_not_oanda")

        if _lower_text(proof.get("broker_environment")) not in OANDA_DEMO_ENVIRONMENTS:
            blockers.append("broker_environment_not_demo_sandbox_or_practice")
        if _lower_text(proof.get("asset_class")) != "forex":
            blockers.append("asset_class_not_forex")

        for field in TRUE_REQUIRED_FIELDS:
            if not _to_bool(proof.get(field), default=False):
                blockers.append(f"{field}_not_confirmed")

        if not _to_bool(proof.get("long_permission"), default=False):
            blockers.append("long_permission_not_confirmed")
        if not _to_bool(proof.get("stop_loss_supported"), default=False):
            blockers.append("stop_loss_not_supported")
        if not _to_bool(proof.get("take_profit_supported"), default=False):
            blockers.append("take_profit_not_supported")
        if not _to_bool(proof.get("one_order_only_supported"), default=False):
            blockers.append("one_order_only_not_supported")
        if not _to_bool(proof.get("demo_sandbox_order_preview_supported"), default=False):
            blockers.append("demo_sandbox_order_preview_not_supported")

        leverage_limit = _to_float(proof.get("effective_leverage_limit"), default=0.0)
        if leverage_limit <= 0:
            blockers.append("invalid_effective_leverage_limit")
        elif leverage_limit > OANDA_MAX_EFFECTIVE_LEVERAGE:
            blockers.append("effective_leverage_limit_above_low_guard")

        max_units = _to_int(proof.get("max_units"), default=0)
        if max_units <= 0:
            blockers.append("invalid_max_units")
        elif max_units > OANDA_MAX_DEMO_PREVIEW_UNITS:
            blockers.append("max_units_above_demo_preview_guard")
        if not _safe_currency(proof.get("account_currency")):
            blockers.append("unsafe_account_currency")
        if not _safe_forex_instrument(proof.get("instrument")):
            blockers.append("unsafe_forex_instrument")
        if not _supported_order_type(proof.get("order_type_supported"), expected="market"):
            blockers.append("market_order_type_not_supported")
        if not _valid_timestamp(proof.get("proof_timestamp")):
            blockers.append("invalid_proof_timestamp")
        blockers.extend(_restriction_blockers(proof.get("broker_house_restrictions")))
        blockers.extend(_safe_payload_blockers(proof))

    blockers = list(dict.fromkeys(blockers))
    account_gate_payload = _account_permission_gate_from_proof(proof)
    account_gate = evaluate_account_permission_gate(account_gate_payload, activation_side="long")
    blockers.extend(account_gate.get("blockers", []))
    blockers = list(dict.fromkeys(blockers))

    ready = not blockers
    audit_result = build_safety_audit_result(
        proof,
        allowed_keys=REQUIRED_SANITIZED_FIELDS,
        required_keys=REQUIRED_SANITIZED_FIELDS,
    )
    return {
        "packet_id": PACKET_ID,
        "status": OANDA_LONG_ONLY_BROKER_PROOF_READY if ready else OANDA_BROKER_PROOF_BLOCKED,
        "ready": ready,
        "broker_name": proof.get("broker_name"),
        "broker_environment": proof.get("broker_environment"),
        "asset_class": proof.get("asset_class"),
        "instrument": proof.get("instrument"),
        "blockers": blockers,
        "warnings": [],
        "normalized_proof": audit_result["redacted_payload"],
        "short_side_enabled": False,
        "long_only_ready_for_demo_preparation": ready,
        "broker_gate_clear_for_demo_preparation": ready,
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "no_network_call": True,
        "no_broker_mutation": True,
        "no_order_execution": True,
        "safety_summary": {
            "sanitized_evidence_only": _to_bool(proof.get("sanitized_evidence_only"), default=False),
            "no_credentials_in_payload": _to_bool(proof.get("no_credentials_in_payload"), default=False),
            "no_account_id_in_payload": _to_bool(proof.get("no_account_id_in_payload"), default=False),
            "no_env_in_payload": _to_bool(proof.get("no_env_in_payload"), default=False),
            "no_network_call": _to_bool(proof.get("no_network_call"), default=False),
            "no_broker_mutation": _to_bool(proof.get("no_broker_mutation"), default=False),
            "no_order_execution": _to_bool(proof.get("no_order_execution"), default=False),
            "execution_allowed": False,
            "ready_to_execute": False,
            "demo_order_allowed": False,
            "live_autonomy_allowed": False,
            "short_side_enabled": False,
        },
        "broker_gate": {
            "broker_sandbox_or_demo_proof": ready,
            "broker_mutation": False,
            "credentials_persisted": False,
            "account_id_persisted": False,
        },
        "account_permission_gate": account_gate_payload,
        "account_permission_gate_result": account_gate,
        "short_side_status": "SHORT_SIDE_DISABLED",
        "long_only_status": "LONG_ONLY_BROKER_PROOF_READY" if ready else OANDA_BROKER_PROOF_BLOCKED,
        "demo_sandbox_only": True,
        "safety": {
            "sanitized_evidence_only": _to_bool(proof.get("sanitized_evidence_only"), default=False),
            "credentials_used": False,
            "credential_read": False,
            "credential_write": False,
            "env_read": False,
            "env_write": False,
            "account_id_read": False,
            "account_id_write": False,
            "network_used": False,
            "broker_mutation": False,
            "order_execution": False,
            "demo_order_placed": False,
            "live_order_placed": False,
            "scheduler": False,
            "daemon": False,
            "webhook": False,
            "background_execution": False,
        },
        "summary": {
            "broker_name": proof.get("broker_name"),
            "broker_environment": proof.get("broker_environment"),
            "asset_class": proof.get("asset_class"),
            "instrument": proof.get("instrument"),
            "long_permission": proof.get("long_permission"),
            "short_permission": proof.get("short_permission"),
            "max_units": proof.get("max_units"),
            "effective_leverage_limit": proof.get("effective_leverage_limit"),
            "proof_source": proof.get("proof_source"),
            "proof_timestamp": proof.get("proof_timestamp"),
        },
        "next_safe_action": (
            "pass_sanitized_oanda_broker_proof_to_autonomous_demo_supervisor"
            if ready
            else "provide_complete_sanitized_oanda_demo_practice_broker_proof"
        ),
    }


def _demo_policy_placeholder_bundle() -> dict[str, Any]:
    return {
        "evidence_bundle": {
            "evidence_bundle_id": "oanda-long-only-demo-broker-proof-policy-placeholder",
            "packet_id": PACKET_ID,
            "broker_sandbox_or_demo_proof": True,
            "risk_gate_passed": True,
            "kill_switch_active": True,
            "daily_loss_cap_active": True,
            "approval_hash_verified": True,
            "sanitized": True,
            "owner_live_exception_request": False,
            "owner_approval_required": True,
            "owner_approval_present": False,
            "arming_timestamp": None,
            "kill_switch_confirmed": True,
            "max_loss_confirmed": True,
            "daily_stop_confirmed": True,
            "stop_loss_confirmed": True,
            "take_profit_confirmed": True,
            "one_order_only_confirmed": True,
            "micro_size_confirmed": True,
            "low_effective_leverage_confirmed": True,
            "sanitized_evidence_only": True,
            "no_credential_read": True,
            "no_credential_write": True,
            "no_env_read": True,
            "no_env_write": True,
            "no_account_id_read": True,
            "no_account_id_write": True,
            "no_network_call": True,
            "no_broker_mutation": True,
            "no_live_order_execution": True,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "webhook_enabled": False,
            "background_execution": False,
            "credential_read": False,
            "credential_write": False,
            "env_read": False,
            "env_write": False,
            "account_id_read": False,
            "account_id_write": False,
            "network_call": False,
            "broker_mutation": False,
            "live_order_execution": False,
        }
    }


def build_final_status_payload_with_oanda_broker_proof(
    proof_payload: Mapping[str, Any] | None,
    *,
    base_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Attach valid sanitized OANDA proof to the final readiness payload shape."""
    intake = evaluate_oanda_long_only_broker_proof(proof_payload)
    payload = deepcopy(dict(base_payload or _default_final_readiness_payload()))
    if not intake["ready"]:
        payload["oanda_broker_proof_intake"] = intake
        return payload

    payload["broker_gate"] = dict(intake["broker_gate"])
    payload["account_permission_gate"] = dict(intake["account_permission_gate"])
    contracts = payload.get("live_exception_contracts") if isinstance(payload.get("live_exception_contracts"), Mapping) else {}
    contracts = deepcopy(dict(contracts))
    contracts.setdefault("evidence_bundle", _demo_policy_placeholder_bundle()["evidence_bundle"])
    payload["live_exception_contracts"] = contracts
    payload["oanda_broker_proof_intake"] = intake
    return payload


def build_oanda_long_only_autonomous_supervisor_contract(
    proof_payload: Mapping[str, Any] | None,
    *,
    final_status_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build autonomous supervisor readiness from sanitized OANDA proof."""
    intake = evaluate_oanda_long_only_broker_proof(proof_payload)
    if intake["ready"]:
        payload = build_final_status_payload_with_oanda_broker_proof(
            proof_payload,
            base_payload=final_status_payload,
        )
        final_status = build_profitable_live_bot_final_status(evidence_payload=payload)
        autonomous = build_long_only_autonomous_supervisor_contract(final_status_result=final_status)
    else:
        autonomous = build_long_only_autonomous_supervisor_contract(final_status_payload=dict(final_status_payload or {}))
        autonomous["status"] = "AUTONOMOUS_BLOCKED_BY_BROKER_GATE"
        autonomous["readiness_gates"]["broker_gate_cleared"] = False
        autonomous["blockers"]["broker"] = list(
            dict.fromkeys(list(autonomous["blockers"].get("broker", [])) + intake["blockers"])
        )

    autonomous["oanda_broker_proof_status"] = intake["status"]
    autonomous["oanda_broker_proof_intake"] = intake
    autonomous["execution_allowed"] = False
    autonomous["ready_to_execute"] = False
    autonomous["live_autonomy_allowed"] = False
    autonomous["live_autonomy_blocked"] = True
    autonomous["safety"]["order_execution"] = False
    autonomous["safety"]["network_used"] = False
    autonomous["safety"]["broker_mutation"] = False
    autonomous["safety"]["credential_read"] = False
    autonomous["safety"]["env_read"] = False
    autonomous["safety"]["account_id_read"] = False
    return autonomous


def main() -> dict[str, Any]:  # pragma: no cover
    return evaluate_oanda_long_only_broker_proof({})


if __name__ == "__main__":  # pragma: no cover
    print(main())
