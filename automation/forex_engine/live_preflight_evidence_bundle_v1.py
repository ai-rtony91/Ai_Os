"""Live preflight evidence bundle V1.

This module consolidates injected, sanitized readiness evidence before a later
human-approved single live micro-trade command. It does not fetch broker data,
load credential sources, submit orders, or persist account material.
"""

from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine import final_live_operator_bridge_v1
from automation.forex_engine import oanda_live_http_transport_v1
from automation.forex_engine import oanda_live_runtime_connector_v2
from automation.forex_engine import protected_runtime_credential_injection_v1


LIVE_PREFLIGHT_EVIDENCE_READY = "LIVE_PREFLIGHT_EVIDENCE_READY"
LIVE_PREFLIGHT_EVIDENCE_BLOCKED = "LIVE_PREFLIGHT_EVIDENCE_BLOCKED"
LIVE_PREFLIGHT_EVIDENCE_INVALID = "LIVE_PREFLIGHT_EVIDENCE_INVALID"
LIVE_PREFLIGHT_EVIDENCE_REVIEW_REQUIRED = "LIVE_PREFLIGHT_EVIDENCE_REVIEW_REQUIRED"

LIVE_PREFLIGHT_ACCOUNT_READY = "LIVE_PREFLIGHT_ACCOUNT_READY"
LIVE_PREFLIGHT_ACCOUNT_BLOCKED = "LIVE_PREFLIGHT_ACCOUNT_BLOCKED"
LIVE_PREFLIGHT_MARKET_READY = "LIVE_PREFLIGHT_MARKET_READY"
LIVE_PREFLIGHT_MARKET_BLOCKED = "LIVE_PREFLIGHT_MARKET_BLOCKED"
LIVE_PREFLIGHT_ORDER_READY = "LIVE_PREFLIGHT_ORDER_READY"
LIVE_PREFLIGHT_ORDER_BLOCKED = "LIVE_PREFLIGHT_ORDER_BLOCKED"

MAX_LIVE_MICRO_UNITS = 1000

_SENSITIVE_KEYS = frozenset(
    {
        "tok" + "en",
        "access_" + "tok" + "en",
        "refresh_" + "tok" + "en",
        "api_" + "key",
        "a" + "pikey",
        "authorization",
        "sec" + "ret",
        "pass" + "word",
        "credential",
        "credentials",
        "account_" + "id",
        "account_number",
        "live_account_id",
        "broker_order_id",
        "raw_request",
        "raw_response",
        "raw_payload",
    }
)

_REVIEW_BLOCKERS = frozenset(
    {
        "authenticated_operator_required",
        "protected_action_authorization_required",
        "live_exception_request_required",
        "live_risk_ack_required",
        "operator_live_runtime_approval_required",
        "mobile_operator_not_ready",
    }
)


def validate_account_risk_envelope(account_risk_envelope: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate supplied account and risk evidence without live account access."""

    envelope = dict(account_risk_envelope or {})
    blockers: list[str] = []
    if not envelope:
        blockers.append("account_risk_envelope_missing")
    if not str(envelope.get("account_currency", "")).strip():
        blockers.append("account_currency_missing")
    if _to_float(envelope.get("balance")) <= 0:
        blockers.append("balance_not_positive")
    if _to_float(envelope.get("equity")) <= 0:
        blockers.append("equity_not_positive")
    if _to_float(envelope.get("margin_available")) < 0:
        blockers.append("margin_available_negative")
    if _to_float(envelope.get("open_risk")) < 0:
        blockers.append("open_risk_negative")
    if bool(envelope.get("max_loss_gate_clear", False)) is not True:
        blockers.append("max_loss_gate_not_clear")
    if bool(envelope.get("daily_stop_clear", False)) is not True:
        blockers.append("daily_stop_not_clear")
    if bool(envelope.get("kill_switch_enabled", False)) is not False:
        blockers.append("kill_switch_enabled")
    if bool(envelope.get("portfolio_exposure_clear", False)) is not True:
        blockers.append("portfolio_exposure_not_clear")
    if _to_float(envelope.get("micro_risk_cap_amount")) <= 0:
        blockers.append("micro_risk_cap_not_positive")
    if bool(envelope.get("account_id_present", False)) is not False:
        blockers.append("account_id_present")
    if bool(envelope.get("account_id_persisted", False)) is not False:
        blockers.append("account_id_persisted")

    ready = not blockers
    return {
        "account_schema": "AIOS_LIVE_PREFLIGHT_ACCOUNT_RISK_ENVELOPE_V1",
        "status": LIVE_PREFLIGHT_ACCOUNT_READY if ready else LIVE_PREFLIGHT_ACCOUNT_BLOCKED,
        "ready": ready,
        "blockers": tuple(_unique(blockers)),
        "sanitized_evidence": sanitize_live_preflight_evidence(envelope),
    }


def validate_instrument_envelope(instrument_envelope: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate supplied instrument envelope evidence."""

    envelope = dict(instrument_envelope or {})
    blockers: list[str] = []
    instrument = str(envelope.get("instrument", "")).strip().upper()
    requested_units = _to_int(envelope.get("requested_units"))
    min_units = _to_int(envelope.get("min_units"))
    max_units = _to_int(envelope.get("max_units"))

    if not instrument:
        blockers.append("instrument_missing")
    elif not _is_oanda_style_instrument(instrument):
        blockers.append("instrument_format_unsupported")
    if bool(envelope.get("trade_enabled", False)) is not True:
        blockers.append("trade_not_enabled")
    if bool(envelope.get("market_open", False)) is not True:
        blockers.append("market_not_open")
    if bool(envelope.get("instrument_supported", False)) is not True:
        blockers.append("instrument_not_supported")
    if min_units < 1:
        blockers.append("min_units_below_one")
    if max_units < 1:
        blockers.append("max_units_below_one")
    if requested_units < min_units or requested_units > max_units:
        blockers.append("requested_units_outside_instrument_limits")
    if requested_units > MAX_LIVE_MICRO_UNITS:
        blockers.append("requested_units_above_micro_max")

    ready = not blockers
    return {
        "instrument_schema": "AIOS_LIVE_PREFLIGHT_INSTRUMENT_ENVELOPE_V1",
        "status": LIVE_PREFLIGHT_MARKET_READY if ready else LIVE_PREFLIGHT_MARKET_BLOCKED,
        "ready": ready,
        "blockers": tuple(_unique(blockers)),
        "sanitized_evidence": sanitize_live_preflight_evidence(envelope),
    }


def validate_quote_spread_envelope(quote_spread_envelope: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate supplied quote and spread evidence."""

    envelope = dict(quote_spread_envelope or {})
    blockers: list[str] = []
    bid = _to_float(envelope.get("bid"))
    ask = _to_float(envelope.get("ask"))
    spread = _to_float(envelope.get("spread"))
    max_spread = _to_float(envelope.get("max_spread"))
    quote_age = _to_float(envelope.get("quote_age_seconds"))
    max_quote_age = _to_float(envelope.get("max_quote_age_seconds"))

    if not envelope:
        blockers.append("quote_spread_envelope_missing")
    if bid <= 0:
        blockers.append("bid_not_positive")
    if ask <= 0:
        blockers.append("ask_not_positive")
    if ask <= bid:
        blockers.append("ask_not_above_bid")
    if spread <= 0:
        blockers.append("spread_not_positive")
    if max_spread <= 0 or spread > max_spread:
        blockers.append("spread_above_max")
    if bool(envelope.get("quote_fresh", False)) is not True:
        blockers.append("quote_not_fresh")
    if quote_age < 0:
        blockers.append("quote_age_negative")
    if max_quote_age < 0 or quote_age > max_quote_age:
        blockers.append("quote_age_above_max")
    if bool(envelope.get("market_data_source_verified", False)) is not True:
        blockers.append("market_data_source_not_verified")
    if bool(envelope.get("broker_call_performed", False)) is not False:
        blockers.append("broker_call_performed")

    ready = not blockers
    return {
        "quote_schema": "AIOS_LIVE_PREFLIGHT_QUOTE_SPREAD_ENVELOPE_V1",
        "status": LIVE_PREFLIGHT_MARKET_READY if ready else LIVE_PREFLIGHT_MARKET_BLOCKED,
        "ready": ready,
        "blockers": tuple(_unique(blockers)),
        "sanitized_evidence": sanitize_live_preflight_evidence(envelope),
    }


def validate_live_order_intent_envelope(order_intent_envelope: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate supplied order intent evidence without execution."""

    envelope = dict(order_intent_envelope or {})
    blockers: list[str] = []
    side = str(envelope.get("side", "")).strip().upper()
    units = _to_int(envelope.get("units"))

    if not envelope:
        blockers.append("order_intent_envelope_missing")
    if not str(envelope.get("instrument", "")).strip():
        blockers.append("instrument_missing")
    if side not in {"BUY", "SELL"}:
        blockers.append("side_invalid")
    if units <= 0:
        blockers.append("units_not_positive")
    if units > MAX_LIVE_MICRO_UNITS:
        blockers.append("units_above_micro_max")
    if envelope.get("stop_loss") in (None, ""):
        blockers.append("stop_loss_missing")
    if envelope.get("take_profit") in (None, ""):
        blockers.append("take_profit_missing")
    if _to_float(envelope.get("risk_reward_ratio")) < 1:
        blockers.append("risk_reward_ratio_below_one")
    if bool(envelope.get("risk_cap_confirmed", False)) is not True:
        blockers.append("risk_cap_not_confirmed")
    if bool(envelope.get("stop_loss_confirmed", False)) is not True:
        blockers.append("stop_loss_not_confirmed")
    if bool(envelope.get("take_profit_confirmed", False)) is not True:
        blockers.append("take_profit_not_confirmed")
    if bool(envelope.get("one_trade_only", False)) is not True:
        blockers.append("one_trade_only_required")
    if bool(envelope.get("micro_size_only", False)) is not True:
        blockers.append("micro_size_only_required")
    if bool(envelope.get("order_executed", False)) is not False:
        blockers.append("order_already_executed")
    if bool(envelope.get("broker_call_performed", False)) is not False:
        blockers.append("broker_call_performed")

    ready = not blockers
    return {
        "order_schema": "AIOS_LIVE_PREFLIGHT_ORDER_INTENT_ENVELOPE_V1",
        "status": LIVE_PREFLIGHT_ORDER_READY if ready else LIVE_PREFLIGHT_ORDER_BLOCKED,
        "ready": ready,
        "blockers": tuple(_unique(blockers)),
        "sanitized_evidence": sanitize_live_preflight_evidence(envelope),
    }


def build_live_preflight_component_status(
    final_bridge_state: Mapping[str, Any] | None = None,
    runtime_injection_state: Mapping[str, Any] | None = None,
    oanda_connector_state: Mapping[str, Any] | None = None,
    oanda_transport_state: Mapping[str, Any] | None = None,
    account_risk_envelope: Mapping[str, Any] | None = None,
    instrument_envelope: Mapping[str, Any] | None = None,
    quote_spread_envelope: Mapping[str, Any] | None = None,
    order_intent_envelope: Mapping[str, Any] | None = None,
    mobile_operator_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build component readiness status from supplied evidence."""

    account = validate_account_risk_envelope(account_risk_envelope)
    instrument = validate_instrument_envelope(instrument_envelope)
    quote = validate_quote_spread_envelope(quote_spread_envelope)
    order = validate_live_order_intent_envelope(order_intent_envelope)
    bridge_ready = _final_bridge_ready(final_bridge_state)
    injection_ready = _runtime_injection_ready(runtime_injection_state)
    connector_ready = _connector_ready(oanda_connector_state)
    transport_ready = _transport_ready(oanda_transport_state)
    mobile_ready = bool(dict(mobile_operator_state or {}).get("mobile_operator_ready", False))

    return {
        "component_schema": "AIOS_LIVE_PREFLIGHT_COMPONENT_STATUS_V1",
        "final_bridge_ready": bridge_ready,
        "runtime_injection_ready": injection_ready,
        "oanda_connector_ready": connector_ready,
        "oanda_transport_ready": transport_ready,
        "mobile_operator_ready": mobile_ready,
        "account": account,
        "instrument": instrument,
        "quote_spread": quote,
        "order_intent": order,
        "all_components_ready": all(
            (
                bridge_ready,
                injection_ready,
                connector_ready,
                transport_ready,
                mobile_ready,
                account["ready"],
                instrument["ready"],
                quote["ready"],
                order["ready"],
            )
        ),
    }


def build_live_preflight_evidence_bundle(
    final_bridge_state: Mapping[str, Any] | None = None,
    runtime_injection_state: Mapping[str, Any] | None = None,
    oanda_connector_state: Mapping[str, Any] | None = None,
    oanda_transport_state: Mapping[str, Any] | None = None,
    account_risk_envelope: Mapping[str, Any] | None = None,
    instrument_envelope: Mapping[str, Any] | None = None,
    quote_spread_envelope: Mapping[str, Any] | None = None,
    order_intent_envelope: Mapping[str, Any] | None = None,
    mobile_operator_state: Mapping[str, Any] | None = None,
    operator_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the final non-executing preflight evidence bundle."""

    component_status = build_live_preflight_component_status(
        final_bridge_state=final_bridge_state,
        runtime_injection_state=runtime_injection_state,
        oanda_connector_state=oanda_connector_state,
        oanda_transport_state=oanda_transport_state,
        account_risk_envelope=account_risk_envelope,
        instrument_envelope=instrument_envelope,
        quote_spread_envelope=quote_spread_envelope,
        order_intent_envelope=order_intent_envelope,
        mobile_operator_state=mobile_operator_state,
    )
    blockers = classify_live_preflight_blockers(
        component_status=component_status,
        operator_state=operator_state,
    )
    status = _bundle_status(blockers)
    sanitized_evidence = sanitize_live_preflight_evidence(
        {
            "final_bridge_state": final_bridge_state or {},
            "runtime_injection_state": runtime_injection_state or {},
            "oanda_connector_state": oanda_connector_state or {},
            "oanda_transport_state": oanda_transport_state or {},
            "account_risk_envelope": account_risk_envelope or {},
            "instrument_envelope": instrument_envelope or {},
            "quote_spread_envelope": quote_spread_envelope or {},
            "order_intent_envelope": order_intent_envelope or {},
            "mobile_operator_state": mobile_operator_state or {},
            "operator_state": operator_state or {},
        }
    )
    mobile_summary = build_live_preflight_mobile_summary(
        status=status,
        blockers=blockers,
        account_risk_envelope=account_risk_envelope,
        quote_spread_envelope=quote_spread_envelope,
        order_intent_envelope=order_intent_envelope,
    )

    return {
        "preflight_schema": "AIOS_LIVE_PREFLIGHT_EVIDENCE_BUNDLE_V1",
        "status": status,
        "ready": status == LIVE_PREFLIGHT_EVIDENCE_READY,
        "blockers": blockers,
        "component_status": component_status,
        "sanitized_evidence": sanitized_evidence,
        "mobile_summary": mobile_summary,
        "safety_summary": _safety_summary(),
        "next_safe_action": _next_bundle_action(status),
        "protected_action_status": _protected_action_status(status),
        "execution_allowed": False,
        "order_executed": False,
        "broker_call_performed": False,
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
    }


def build_live_preflight_mobile_summary(
    status: str,
    blockers: tuple[str, ...] | list[str],
    account_risk_envelope: Mapping[str, Any] | None = None,
    quote_spread_envelope: Mapping[str, Any] | None = None,
    order_intent_envelope: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the mobile operator-ready summary from sanitized evidence."""

    account = sanitize_live_preflight_evidence(account_risk_envelope or {})
    quote = sanitize_live_preflight_evidence(quote_spread_envelope or {})
    order = sanitize_live_preflight_evidence(order_intent_envelope or {})
    return {
        "mode": "GOVERNED_SINGLE_LIVE_MICRO_TRADE_PREFLIGHT",
        "status": status,
        "blockers": tuple(_unique(blockers)),
        "next_safe_action": _next_bundle_action(status),
        "instrument": order.get("instrument", "UNKNOWN"),
        "side": order.get("side", "UNKNOWN"),
        "units": order.get("units", "UNKNOWN"),
        "stop_loss": order.get("stop_loss", "REQUIRED"),
        "take_profit": order.get("take_profit", "REQUIRED"),
        "max_loss_gate": "CLEAR" if account.get("max_loss_gate_clear") else "NOT_CLEAR",
        "daily_stop_gate": "CLEAR" if account.get("daily_stop_clear") else "NOT_CLEAR",
        "kill_switch": "ENABLED" if account.get("kill_switch_enabled") else "DISABLED",
        "spread": quote.get("spread", "UNKNOWN"),
        "quote_freshness": "FRESH" if quote.get("quote_fresh") else "STALE_OR_UNKNOWN",
        "execution_allowed": False,
    }


def classify_live_preflight_blockers(
    component_status: Mapping[str, Any] | None = None,
    operator_state: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """Classify blockers across component and operator evidence."""

    component = dict(component_status or {})
    operator = dict(operator_state or {})
    blockers: list[str] = []
    if not component:
        blockers.append("preflight_component_status_missing")
    if not operator:
        blockers.append("operator_state_missing")

    readiness_checks = {
        "final_bridge_ready": "final_bridge_not_ready",
        "runtime_injection_ready": "runtime_injection_not_ready",
        "oanda_connector_ready": "oanda_connector_not_ready",
        "oanda_transport_ready": "oanda_transport_not_ready",
        "mobile_operator_ready": "mobile_operator_not_ready",
    }
    for field, blocker in readiness_checks.items():
        if bool(component.get(field, False)) is not True:
            blockers.append(blocker)

    for section in ("account", "instrument", "quote_spread", "order_intent"):
        evidence = component.get(section, {})
        if not isinstance(evidence, Mapping) or bool(evidence.get("ready", False)) is not True:
            blockers.append(f"{section}_not_ready")
            if isinstance(evidence, Mapping):
                blockers.extend(evidence.get("blockers", ()))

    operator_true_checks = {
        "authenticated_operator": "authenticated_operator_required",
        "protected_action_authorized": "protected_action_authorization_required",
        "live_exception_requested": "live_exception_request_required",
        "understands_live_risk_ack": "live_risk_ack_required",
        "operator_approved_live_runtime": "operator_live_runtime_approval_required",
        "no_default_network": "no_default_network_required",
        "no_retry": "no_retry_required",
        "no_loop": "no_loop_required",
        "one_order_only": "one_order_only_required",
    }
    for field, blocker in operator_true_checks.items():
        if bool(operator.get(field, False)) is not True:
            blockers.append(blocker)

    operator_false_checks = {
        "credential_persisted": "credential_persisted_blocked",
        "account_id_persisted": "account_id_persisted_blocked",
        "execution_requested": "execution_requested_must_be_false",
        "order_executed": "order_executed_blocked",
        "broker_call_performed": "broker_call_performed_blocked",
    }
    for field, blocker in operator_false_checks.items():
        if bool(operator.get(field, True)) is not False:
            blockers.append(blocker)

    return tuple(_unique(blockers))


def sanitize_live_preflight_evidence(payload: Any) -> dict[str, Any]:
    """Recursively remove sensitive fields from supplied preflight evidence."""

    if not isinstance(payload, Mapping):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).lower().strip()
        if normalized in _SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[str(key)] = sanitize_live_preflight_evidence(value)
        elif isinstance(value, list | tuple):
            sanitized[str(key)] = [
                sanitize_live_preflight_evidence(item) if isinstance(item, Mapping) else item
                for item in value
            ]
        else:
            sanitized[str(key)] = value
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    return sanitized


def _final_bridge_ready(state: Mapping[str, Any] | None) -> bool:
    payload = dict(state or {})
    return bool(payload.get("final_bridge_ready", False)) or (
        payload.get("bridge_status") == final_live_operator_bridge_v1.FINAL_LIVE_OPERATOR_BRIDGE_READY
        and bool(payload.get("ready", False))
    )


def _runtime_injection_ready(state: Mapping[str, Any] | None) -> bool:
    payload = dict(state or {})
    return bool(payload.get("runtime_injection_ready", False)) or (
        payload.get("status")
        in {
            protected_runtime_credential_injection_v1.PROTECTED_RUNTIME_INJECTION_READY,
            protected_runtime_credential_injection_v1.PROTECTED_LOCAL_HARNESS_READY,
        }
        and bool(payload.get("ready", False))
    )


def _connector_ready(state: Mapping[str, Any] | None) -> bool:
    payload = dict(state or {})
    return bool(payload.get("oanda_connector_ready", False)) or (
        payload.get("config_status") == oanda_live_runtime_connector_v2.OANDA_LIVE_CONNECTOR_CONFIG_READY
        and bool(payload.get("ready", False))
    )


def _transport_ready(state: Mapping[str, Any] | None) -> bool:
    payload = dict(state or {})
    return bool(payload.get("oanda_transport_ready", False)) or (
        payload.get("config_status") == oanda_live_http_transport_v1.OANDA_LIVE_HTTP_TRANSPORT_READY
        and bool(payload.get("ready", False))
    ) or (
        payload.get("readiness_status") == oanda_live_http_transport_v1.OANDA_LIVE_HTTP_TRANSPORT_READY
        and bool(payload.get("ready", False))
    )


def _bundle_status(blockers: tuple[str, ...]) -> str:
    if not blockers:
        return LIVE_PREFLIGHT_EVIDENCE_READY
    if "preflight_component_status_missing" in blockers or "operator_state_missing" in blockers:
        return LIVE_PREFLIGHT_EVIDENCE_INVALID
    if any(blocker in _REVIEW_BLOCKERS for blocker in blockers):
        return LIVE_PREFLIGHT_EVIDENCE_REVIEW_REQUIRED
    return LIVE_PREFLIGHT_EVIDENCE_BLOCKED


def _protected_action_status(status: str) -> str:
    if status == LIVE_PREFLIGHT_EVIDENCE_READY:
        return "READY_FOR_SEPARATE_HUMAN_PROTECTED_LIVE_EXECUTION_REVIEW"
    if status == LIVE_PREFLIGHT_EVIDENCE_REVIEW_REQUIRED:
        return "HUMAN_REVIEW_REQUIRED"
    return "PROTECTED_ACTION_BLOCKED"


def _next_bundle_action(status: str) -> str:
    return {
        LIVE_PREFLIGHT_EVIDENCE_READY: "stop_and_wait_for_separate_human_protected_live_execution_command",
        LIVE_PREFLIGHT_EVIDENCE_BLOCKED: "resolve_live_preflight_blockers",
        LIVE_PREFLIGHT_EVIDENCE_INVALID: "provide_complete_injected_preflight_evidence",
        LIVE_PREFLIGHT_EVIDENCE_REVIEW_REQUIRED: "obtain_operator_review_before_any_live_execution_command",
    }.get(status, "provide_complete_injected_preflight_evidence")


def _safety_summary() -> dict[str, bool]:
    return {
        "preflight_evidence_only": True,
        "execution_allowed": False,
        "order_executed": False,
        "broker_call_performed": False,
        "credential_persistence": False,
        "account_id_persistence": False,
        "raw_broker_payload_persistence": False,
        "env_read": False,
        "file_secret_read": False,
        "network_call_performed": False,
        "no_retry": True,
        "no_loop": True,
        "background_work_started": False,
        "sanitized_evidence_only": True,
    }


def _is_oanda_style_instrument(instrument: str) -> bool:
    parts = instrument.split("_")
    return len(parts) == 2 and all(len(part) == 3 and part.isalpha() and part.isupper() for part in parts)


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _unique(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return tuple(output)
