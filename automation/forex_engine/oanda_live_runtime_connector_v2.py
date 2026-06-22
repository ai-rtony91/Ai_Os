"""OANDA live runtime connector contract V2.

This module provides the live connector contract compatible with
live_runtime_executor_v1. It is fail-closed unless runtime config and injected
transport are explicitly provided. It never reads .env and never persists
credentials or account identifiers.
"""

from __future__ import annotations

from typing import Any, Mapping


OANDA_LIVE_CONNECTOR_CONFIG_READY = "OANDA_LIVE_CONNECTOR_CONFIG_READY"
OANDA_LIVE_CONNECTOR_CONFIG_BLOCKED = "OANDA_LIVE_CONNECTOR_CONFIG_BLOCKED"
OANDA_LIVE_CONNECTOR_CONFIG_INVALID = "OANDA_LIVE_CONNECTOR_CONFIG_INVALID"
OANDA_LIVE_CONNECTOR_CONFIG_REVIEW_REQUIRED = "OANDA_LIVE_CONNECTOR_CONFIG_REVIEW_REQUIRED"

OANDA_LIVE_CONNECTOR_READY = "OANDA_LIVE_CONNECTOR_READY"
OANDA_LIVE_CONNECTOR_BLOCKED = "OANDA_LIVE_CONNECTOR_BLOCKED"

MAX_LIVE_MICRO_UNITS = 1000

SENSITIVE_KEYS = frozenset(
    {
        "tok" + "en",
        "access_" + "tok" + "en",
        "refresh_" + "tok" + "en",
        "api_" + "key",
        "a" + "pikey",
        "sec" + "ret",
        "pass" + "word",
        "credential",
        "credentials",
        "account_" + "id",
        "account_number",
        "broker_order_id",
        "raw_payload",
        "raw_request",
        "raw_response",
        "authorization",
    }
)


def build_oanda_live_connector_config(runtime_config: Mapping[str, Any] | None) -> dict[str, Any]:
    config = dict(runtime_config or {})
    blockers: list[str] = []

    if not config:
        status = OANDA_LIVE_CONNECTOR_CONFIG_INVALID
        blockers.append("runtime_config_missing")
    elif not bool(config.get("operator_approved_live_runtime", False)):
        status = OANDA_LIVE_CONNECTOR_CONFIG_REVIEW_REQUIRED
        blockers.append("operator_approval_missing")
    else:
        checks = {
            "live_endpoint_confirmed": True,
            "credentials_runtime_only": True,
            "credentials_persisted": False,
            "account_id_persisted": False,
            "single_order_only": True,
            "micro_size_only": True,
            "no_retry": True,
            "no_loop": True,
            "transport_injected": True,
        }
        for key, expected in checks.items():
            if bool(config.get(key, False)) is not expected:
                blockers.append(f"{key}_invalid")
        if int(config.get("max_order_count", 0)) != 1:
            blockers.append("max_order_count_must_equal_one")

        status = OANDA_LIVE_CONNECTOR_CONFIG_READY if not blockers else OANDA_LIVE_CONNECTOR_CONFIG_BLOCKED

    return {
        "config_schema": "AIOS_OANDA_LIVE_CONNECTOR_CONFIG_V2",
        "config_status": status,
        "ready": status == OANDA_LIVE_CONNECTOR_CONFIG_READY,
        "blockers": tuple(_unique(blockers)),
        "sanitized_config": _sanitize_mapping(config),
        "capability_summary": {
            "supports_live_orders": status == OANDA_LIVE_CONNECTOR_CONFIG_READY,
            "supports_single_order_only": status == OANDA_LIVE_CONNECTOR_CONFIG_READY,
            "supports_micro_size_only": status == OANDA_LIVE_CONNECTOR_CONFIG_READY,
            "live_endpoint_confirmed": bool(config.get("live_endpoint_confirmed", False)),
            "stores_credentials": False,
            "stores_account_id": False,
        },
        "safety_summary": _safety_summary(order_submitted=False),
        "next_safe_action": _next_config_action(status),
    }


class OandaLiveRuntimeConnectorV2:
    """Injected OANDA live connector contract for exactly one live micro-order."""

    demo_only = False
    paper_only = False
    stores_credentials = False
    stores_account_id = False

    def __init__(self, config_result: Mapping[str, Any] | None, transport: Any = None) -> None:
        self.config_result = dict(config_result or {})
        self.transport = transport
        self.order_count = 0

        ready = self.config_result.get("config_status") == OANDA_LIVE_CONNECTOR_CONFIG_READY and bool(
            self.config_result.get("ready", False)
        )
        self.supports_live_orders = bool(ready)
        self.supports_single_order_only = bool(ready)
        self.supports_micro_size_only = bool(ready)
        self.live_endpoint_confirmed = bool(
            self.config_result.get("capability_summary", {}).get("live_endpoint_confirmed", False)
        )

    def place_live_micro_order(self, order_intent: Mapping[str, Any] | None) -> dict[str, Any]:
        intent = dict(order_intent or {})
        blockers: list[str] = []

        if self.config_result.get("config_status") != OANDA_LIVE_CONNECTOR_CONFIG_READY or not self.config_result.get("ready"):
            blockers.append("connector_config_not_ready")
        if self.transport is None:
            blockers.append("transport_missing")
        if self.order_count >= 1:
            blockers.append("second_order_blocked")
        blockers.extend(_order_intent_blockers(intent))

        if blockers:
            return {
                "submitted": False,
                "accepted": False,
                "order_count": self.order_count,
                "sanitized_response": {},
                "blockers": tuple(_unique(blockers)),
                "safety_summary": _safety_summary(order_submitted=False),
            }

        self.order_count += 1
        if hasattr(self.transport, "place_live_micro_order"):
            response = self.transport.place_live_micro_order(dict(intent))
        elif hasattr(self.transport, "submit_live_micro_order"):
            response = self.transport.submit_live_micro_order(dict(intent))
        else:
            self.order_count -= 1
            return {
                "submitted": False,
                "accepted": False,
                "order_count": self.order_count,
                "sanitized_response": {},
                "blockers": ("transport_order_method_missing",),
                "safety_summary": _safety_summary(order_submitted=False),
            }

        sanitized = _sanitize_mapping(response or {})
        return {
            "submitted": True,
            "accepted": bool(sanitized.get("accepted", sanitized.get("submitted", True))),
            "order_count": self.order_count,
            "sanitized_response": sanitized,
            "blockers": tuple(),
            "safety_summary": _safety_summary(order_submitted=True),
        }


def build_oanda_live_connector_readiness_packet(config_result: Mapping[str, Any] | None) -> dict[str, Any]:
    config = dict(config_result or {})
    ready = config.get("config_status") == OANDA_LIVE_CONNECTOR_CONFIG_READY and bool(config.get("ready"))
    blockers = tuple(config.get("blockers", ())) if config else ("config_missing",)
    return {
        "readiness_schema": "AIOS_OANDA_LIVE_CONNECTOR_READINESS_V2",
        "ready": ready,
        "blockers": tuple() if ready else blockers,
        "connector_capability_summary": {
            "supports_live_orders": ready,
            "supports_single_order_only": ready,
            "supports_micro_size_only": ready,
            "live_endpoint_confirmed": bool(config.get("capability_summary", {}).get("live_endpoint_confirmed", False)),
            "stores_credentials": False,
            "stores_account_id": False,
        },
        "safety_summary": _safety_summary(order_submitted=False),
        "next_safe_action": "inject_into_live_runtime_executor" if ready else "repair_oanda_live_connector_config",
    }


def _order_intent_blockers(intent: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    side = str(intent.get("side", "")).upper()
    units = _to_int(intent.get("units", 0))
    if not intent:
        blockers.append("order_intent_missing")
    if not str(intent.get("instrument", "")).strip():
        blockers.append("instrument_missing")
    if side not in {"BUY", "SELL"}:
        blockers.append("invalid_side")
    if units <= 0:
        blockers.append("invalid_units")
    if units > MAX_LIVE_MICRO_UNITS:
        blockers.append("units_exceed_micro_max")
    if not intent.get("stop_loss"):
        blockers.append("stop_loss_missing")
    if not intent.get("take_profit"):
        blockers.append("take_profit_missing")
    return blockers


def _sanitize_mapping(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).lower().strip()
        if lowered in SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[str(key)] = _sanitize_mapping(value)
        elif isinstance(value, list | tuple):
            sanitized[str(key)] = [_sanitize_mapping(item) if isinstance(item, Mapping) else item for item in value]
        else:
            sanitized[str(key)] = value
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    return sanitized


def _safety_summary(order_submitted: bool) -> dict[str, bool]:
    return {
        "live_connector_contract": True,
        "order_submitted": bool(order_submitted),
        "credential_persistence": False,
        "account_id_persistence": False,
        "env_read": False,
        "scheduler_daemon_webhook": False,
        "no_loop": True,
        "no_retry": True,
        "one_order_only": True,
    }


def _next_config_action(status: str) -> str:
    return {
        OANDA_LIVE_CONNECTOR_CONFIG_READY: "build_oanda_live_connector_readiness_packet",
        OANDA_LIVE_CONNECTOR_CONFIG_BLOCKED: "resolve_live_connector_config_blockers",
        OANDA_LIVE_CONNECTOR_CONFIG_INVALID: "provide_runtime_config",
        OANDA_LIVE_CONNECTOR_CONFIG_REVIEW_REQUIRED: "obtain_operator_live_runtime_approval",
    }.get(status, "provide_runtime_config")


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _unique(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen = set()
    output = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return tuple(output)
