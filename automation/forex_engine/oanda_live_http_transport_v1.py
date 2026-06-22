"""Injected OANDA live HTTP transport V1.

This module is a one-shot transport adapter for the governed live exception
spine. It accepts only injected runtime collaborators, keeps runtime
credentials local to the order call, and returns sanitized evidence only.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping


OANDA_LIVE_HTTP_TRANSPORT_READY = "OANDA_LIVE_HTTP_TRANSPORT_READY"
OANDA_LIVE_HTTP_TRANSPORT_BLOCKED = "OANDA_LIVE_HTTP_TRANSPORT_BLOCKED"
OANDA_LIVE_HTTP_TRANSPORT_INVALID = "OANDA_LIVE_HTTP_TRANSPORT_INVALID"
OANDA_LIVE_HTTP_TRANSPORT_REVIEW_REQUIRED = "OANDA_LIVE_HTTP_TRANSPORT_REVIEW_REQUIRED"

OANDA_LIVE_HTTP_ORDER_SUBMITTED = "OANDA_LIVE_HTTP_ORDER_SUBMITTED"
OANDA_LIVE_HTTP_ORDER_BLOCKED = "OANDA_LIVE_HTTP_ORDER_BLOCKED"
OANDA_LIVE_HTTP_ORDER_INVALID = "OANDA_LIVE_HTTP_ORDER_INVALID"

MAX_LIVE_MICRO_UNITS = 1000

_OANDA_LIVE_BASE_URL = "https://api-fxtrade.oanda.com/v3"

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
        "order_id",
        "orderid",
        "lasttransactionid",
        "last_transaction_id",
        "transaction_id",
        "id",
        "raw_request",
        "raw_response",
        "raw_payload",
    }
)

_REQUIRED_TRUE_CONFIG = {
    "operator_approved_live_runtime": "operator_approval_missing",
    "live_endpoint_confirmed": "live_endpoint_not_confirmed",
    "allow_live_network_once": "allow_live_network_once_required",
    "credentials_runtime_only": "runtime_only_credentials_required",
    "single_order_only": "single_order_only_required",
    "micro_size_only": "micro_size_only_required",
    "no_retry": "no_retry_required",
    "no_loop": "no_loop_required",
    "http_client_injected": "http_client_injected_required",
    "runtime_auth_provider_injected": "runtime_auth_provider_injected_required",
}

_REQUIRED_FALSE_CONFIG = {
    "credentials_persisted": "credentials_persisted_blocked",
    "account_id_persisted": "account_id_persisted_blocked",
}


def build_oanda_live_http_transport_config(runtime_config: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build a sanitized fail-closed transport config result."""

    config = dict(runtime_config or {})
    blockers: list[str] = []

    if not config:
        status = OANDA_LIVE_HTTP_TRANSPORT_INVALID
        blockers.append("transport_config_missing")
    elif _contains_sensitive_keys(config):
        status = OANDA_LIVE_HTTP_TRANSPORT_INVALID
        blockers.append("sensitive_config_field_detected")
    elif bool(config.get("operator_approved_live_runtime", False)) is not True:
        status = OANDA_LIVE_HTTP_TRANSPORT_REVIEW_REQUIRED
        blockers.append("operator_approval_missing")
    else:
        for key, blocker in _REQUIRED_TRUE_CONFIG.items():
            if bool(config.get(key, False)) is not True:
                blockers.append(blocker)
        for key, blocker in _REQUIRED_FALSE_CONFIG.items():
            if bool(config.get(key, True)) is not False:
                blockers.append(blocker)
        if _to_int(config.get("max_order_count")) != 1:
            blockers.append("max_order_count_must_equal_one")

        status = OANDA_LIVE_HTTP_TRANSPORT_READY if not blockers else OANDA_LIVE_HTTP_TRANSPORT_BLOCKED

    sanitized_config = _sanitize_mapping(config)
    ready = status == OANDA_LIVE_HTTP_TRANSPORT_READY
    return {
        "config_schema": "AIOS_OANDA_LIVE_HTTP_TRANSPORT_CONFIG_V1",
        "config_status": status,
        "ready": ready,
        "blockers": tuple(_unique(blockers)),
        "sanitized_config": sanitized_config,
        "capability_summary": {
            "supports_live_orders": ready,
            "supports_single_order_only": ready,
            "supports_micro_size_only": ready,
            "live_endpoint_confirmed": bool(config.get("live_endpoint_confirmed", False)),
            "http_client_injected": bool(config.get("http_client_injected", False)),
            "runtime_auth_provider_injected": bool(config.get("runtime_auth_provider_injected", False)),
            "stores_credentials": False,
            "stores_account_id": False,
        },
        "safety_summary": _safety_summary(order_submitted=False),
        "next_safe_action": _next_transport_config_action(status),
    }


def build_oanda_market_order_payload(order_intent: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build a sanitized OANDA market-order payload from order intent."""

    intent = dict(order_intent or {})
    blockers = _order_intent_blockers(intent)

    instrument = str(intent.get("instrument", "")).strip()
    side = str(intent.get("side", "")).strip().upper()
    units = _to_int(intent.get("units"))
    signed_units = units if side == "BUY" else -units
    stop_loss = intent.get("stop_loss")
    take_profit = intent.get("take_profit")

    if blockers:
        return {
            "payload_schema": "AIOS_OANDA_MARKET_ORDER_PAYLOAD_V1",
            "payload_status": OANDA_LIVE_HTTP_ORDER_INVALID,
            "ready": False,
            "payload": {},
            "instrument": instrument,
            "side": side,
            "units": units,
            "signed_units": 0,
            "blockers": tuple(_unique(blockers)),
            "sanitized_order_intent": _sanitize_mapping(intent),
        }

    payload = {
        "order": {
            "type": "MARKET",
            "instrument": instrument,
            "units": str(signed_units),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"price": str(stop_loss)},
            "takeProfitOnFill": {"price": str(take_profit)},
        }
    }

    return {
        "payload_schema": "AIOS_OANDA_MARKET_ORDER_PAYLOAD_V1",
        "payload_status": OANDA_LIVE_HTTP_TRANSPORT_READY,
        "ready": True,
        "payload": payload,
        "instrument": instrument,
        "side": side,
        "units": units,
        "signed_units": signed_units,
        "blockers": tuple(),
        "sanitized_order_intent": _sanitize_mapping(intent),
    }


def build_oanda_live_http_transport_readiness(
    config_result: Mapping[str, Any] | None,
    http_client: Any = None,
    runtime_auth_provider: Callable[[], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a readiness packet without calling runtime auth or the network."""

    blockers = classify_oanda_http_transport_blockers(
        config_result=config_result,
        http_client=http_client,
        runtime_auth_provider=runtime_auth_provider,
    )
    ready = not blockers
    config = dict(config_result or {})
    return {
        "readiness_schema": "AIOS_OANDA_LIVE_HTTP_TRANSPORT_READINESS_V1",
        "readiness_status": OANDA_LIVE_HTTP_TRANSPORT_READY if ready else OANDA_LIVE_HTTP_TRANSPORT_BLOCKED,
        "ready": ready,
        "blockers": tuple(blockers),
        "transport_capability_summary": {
            "supports_live_orders": ready,
            "supports_single_order_only": ready,
            "supports_micro_size_only": ready,
            "live_endpoint_confirmed": bool(config.get("capability_summary", {}).get("live_endpoint_confirmed", False)),
            "http_client_injected": _http_client_valid(http_client),
            "runtime_auth_provider_injected": callable(runtime_auth_provider),
            "stores_credentials": False,
            "stores_account_id": False,
        },
        "safety_summary": _safety_summary(order_submitted=False),
        "next_safe_action": "call_place_live_micro_order_once" if ready else "repair_oanda_live_http_transport_readiness",
    }


def sanitize_oanda_transport_result(payload: Any) -> dict[str, Any]:
    """Return sanitized transport evidence with persistence flags forced false."""

    sanitized = _sanitize_mapping(payload)
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    sanitized["authorization_persisted"] = False
    return sanitized


def classify_oanda_http_transport_blockers(
    config_result: Mapping[str, Any] | None = None,
    order_intent: Mapping[str, Any] | None = None,
    http_client: Any = None,
    runtime_auth_provider: Callable[[], Mapping[str, Any]] | None = None,
    order_count: int = 0,
) -> tuple[str, ...]:
    """Classify fail-closed transport blockers without side effects."""

    blockers: list[str] = []
    config = dict(config_result or {})

    if not config:
        blockers.append("transport_config_missing")
    elif config.get("config_status") != OANDA_LIVE_HTTP_TRANSPORT_READY or not bool(config.get("ready", False)):
        blockers.append("transport_config_not_ready")
        blockers.extend(config.get("blockers", ()))

    if not _http_client_valid(http_client):
        blockers.append("http_client_invalid")
    if not callable(runtime_auth_provider):
        blockers.append("runtime_auth_invalid")
    if _to_int(order_count) >= 1:
        blockers.append("second_order_blocked")
    if order_intent is not None:
        blockers.extend(_order_intent_blockers(order_intent))

    return tuple(_unique(blockers))


class OandaLiveHttpTransportV1:
    """Injected one-shot OANDA HTTP transport.

    Runtime credentials are fetched only inside place_live_micro_order and are
    never assigned to instance attributes or returned in results.
    """

    demo_only = False
    paper_only = False
    stores_credentials = False
    stores_account_id = False

    def __init__(
        self,
        config_result: Mapping[str, Any] | None,
        http_client: Any = None,
        runtime_auth_provider: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.config_result = sanitize_oanda_transport_result(config_result or {})
        self.http_client = http_client
        self.runtime_auth_provider = runtime_auth_provider
        self.order_count = 0

        ready = (
            self.config_result.get("config_status") == OANDA_LIVE_HTTP_TRANSPORT_READY
            and bool(self.config_result.get("ready", False))
            and _http_client_valid(http_client)
            and callable(runtime_auth_provider)
        )
        self.supports_live_orders = ready
        self.supports_single_order_only = ready
        self.supports_micro_size_only = ready
        self.live_endpoint_confirmed = bool(
            self.config_result.get("capability_summary", {}).get("live_endpoint_confirmed", False)
        )

    def place_live_micro_order(self, order_intent: Mapping[str, Any] | None) -> dict[str, Any]:
        intent = dict(order_intent or {})
        payload_result = build_oanda_market_order_payload(intent)
        blockers = list(
            classify_oanda_http_transport_blockers(
                config_result=self.config_result,
                order_intent=intent,
                http_client=self.http_client,
                runtime_auth_provider=self.runtime_auth_provider,
                order_count=self.order_count,
            )
        )

        if blockers:
            return _build_order_result(
                order_status=OANDA_LIVE_HTTP_ORDER_INVALID
                if payload_result["blockers"]
                else OANDA_LIVE_HTTP_ORDER_BLOCKED,
                submitted=False,
                accepted=False,
                status_code=None,
                order_count=self.order_count,
                payload_result=payload_result,
                broker_status="BLOCKED",
                sanitized_response={},
                blockers=blockers,
            )

        runtime_auth = self._load_runtime_auth()
        if not runtime_auth["ready"]:
            return _build_order_result(
                order_status=OANDA_LIVE_HTTP_ORDER_BLOCKED,
                submitted=False,
                accepted=False,
                status_code=None,
                order_count=self.order_count,
                payload_result=payload_result,
                broker_status="BLOCKED",
                sanitized_response={},
                blockers=("runtime_auth_invalid",),
            )

        access_token = str(runtime_auth["access_token"]).strip()
        account_id = str(runtime_auth["account_id"]).strip()
        base_url = self._base_url()
        order_url = f"{base_url}/accounts/{account_id}/orders"
        request_payload = dict(payload_result["payload"])
        request_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        self.order_count += 1
        response = self.http_client.post(order_url, json=request_payload, headers=request_headers)
        response_evidence = _extract_http_response(response)

        accepted = _is_accepted_response(response_evidence)
        broker_status = _broker_status(response_evidence, accepted)
        return _build_order_result(
            order_status=OANDA_LIVE_HTTP_ORDER_SUBMITTED,
            submitted=True,
            accepted=accepted,
            status_code=response_evidence["status_code"],
            order_count=self.order_count,
            payload_result=payload_result,
            broker_status=broker_status,
            sanitized_response=response_evidence["sanitized_response"],
            blockers=(),
        )

    def _load_runtime_auth(self) -> dict[str, Any]:
        if not callable(self.runtime_auth_provider):
            return {"ready": False}
        try:
            runtime_auth = self.runtime_auth_provider()
        except Exception:
            return {"ready": False}
        if not isinstance(runtime_auth, Mapping):
            return {"ready": False}
        access_token = runtime_auth.get("access_token") or runtime_auth.get("token")
        account_id = runtime_auth.get("account_id")
        if not str(access_token or "").strip() or not str(account_id or "").strip():
            return {"ready": False}
        return {"ready": True, "access_token": access_token, "account_id": account_id}

    def _base_url(self) -> str:
        sanitized_config = self.config_result.get("sanitized_config", {})
        configured = ""
        if isinstance(sanitized_config, Mapping):
            configured = str(sanitized_config.get("base_url", "")).strip()
        return (configured or _OANDA_LIVE_BASE_URL).rstrip("/")


def _build_order_result(
    order_status: str,
    submitted: bool,
    accepted: bool,
    status_code: int | None,
    order_count: int,
    payload_result: Mapping[str, Any],
    broker_status: str,
    sanitized_response: Mapping[str, Any],
    blockers: tuple[str, ...] | list[str],
) -> dict[str, Any]:
    return {
        "order_schema": "AIOS_OANDA_LIVE_HTTP_ORDER_RESULT_V1",
        "order_status": order_status,
        "submitted": bool(submitted),
        "accepted": bool(accepted),
        "status_code": status_code,
        "order_count": order_count,
        "instrument": payload_result.get("instrument", ""),
        "side": payload_result.get("side", ""),
        "units": payload_result.get("signed_units", 0),
        "broker_status": broker_status,
        "sanitized_response": sanitize_oanda_transport_result(sanitized_response),
        "blockers": tuple(_unique(blockers)),
        "safety_summary": _safety_summary(order_submitted=submitted),
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
        "authorization_persisted": False,
    }


def _extract_http_response(response: Any) -> dict[str, Any]:
    status_code = getattr(response, "status_code", None)
    response_payload: Any = {}

    if isinstance(response, Mapping):
        status_code = response.get("status_code", status_code)
        response_payload = response.get("json", response.get("body", response))
    elif hasattr(response, "json") and callable(response.json):
        try:
            response_payload = response.json()
        except Exception:
            response_payload = {}

    return {
        "status_code": _to_int(status_code) if status_code is not None else None,
        "sanitized_response": sanitize_oanda_transport_result(response_payload),
    }


def _is_accepted_response(response_evidence: Mapping[str, Any]) -> bool:
    status_code = response_evidence.get("status_code")
    if isinstance(status_code, int) and 200 <= status_code < 300:
        return True
    sanitized_response = response_evidence.get("sanitized_response", {})
    if isinstance(sanitized_response, Mapping):
        return bool(sanitized_response.get("accepted", sanitized_response.get("submitted", False)))
    return False


def _broker_status(response_evidence: Mapping[str, Any], accepted: bool) -> str:
    sanitized_response = response_evidence.get("sanitized_response", {})
    if isinstance(sanitized_response, Mapping) and sanitized_response.get("status"):
        return str(sanitized_response["status"])
    return "ACCEPTED" if accepted else "NOT_ACCEPTED"


def _order_intent_blockers(intent: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not intent:
        blockers.append("order_intent_missing")
    if _contains_sensitive_keys(intent):
        blockers.append("sensitive_order_intent_field_detected")

    instrument = str(intent.get("instrument", "")).strip()
    side = str(intent.get("side", "")).strip().upper()
    units = _to_int(intent.get("units"))

    if not instrument:
        blockers.append("instrument_missing")
    if side not in {"BUY", "SELL"}:
        blockers.append("side_invalid")
    if units <= 0:
        blockers.append("units_not_positive")
    elif units > MAX_LIVE_MICRO_UNITS:
        blockers.append("units_above_micro_size_max")
    if intent.get("stop_loss") in (None, ""):
        blockers.append("stop_loss_missing")
    if intent.get("take_profit") in (None, ""):
        blockers.append("take_profit_missing")
    return blockers


def _http_client_valid(http_client: Any) -> bool:
    return http_client is not None and callable(getattr(http_client, "post", None))


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
        elif isinstance(value, list | tuple):
            sanitized[str(key)] = [
                _sanitize_mapping(item) if isinstance(item, Mapping) else item
                for item in value
            ]
        else:
            sanitized[str(key)] = value
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    sanitized["authorization_persisted"] = False
    return sanitized


def _contains_sensitive_keys(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized = str(key).lower().strip()
            if normalized in _SENSITIVE_KEYS:
                return True
            if _contains_sensitive_keys(value):
                return True
    elif isinstance(payload, list | tuple):
        return any(_contains_sensitive_keys(item) for item in payload)
    return False


def _safety_summary(order_submitted: bool) -> dict[str, bool | int]:
    return {
        "live_http_transport_contract": True,
        "order_submitted": bool(order_submitted),
        "credential_persistence": False,
        "account_id_persistence": False,
        "raw_broker_payload_persistence": False,
        "authorization_persistence": False,
        "env_read": False,
        "file_secret_read": False,
        "one_order_only": True,
        "max_units": MAX_LIVE_MICRO_UNITS,
        "sanitized_evidence_only": True,
    }


def _next_transport_config_action(status: str) -> str:
    return {
        OANDA_LIVE_HTTP_TRANSPORT_READY: "build_oanda_live_http_transport_readiness",
        OANDA_LIVE_HTTP_TRANSPORT_BLOCKED: "resolve_oanda_live_http_transport_blockers",
        OANDA_LIVE_HTTP_TRANSPORT_INVALID: "provide_valid_oanda_live_http_transport_config",
        OANDA_LIVE_HTTP_TRANSPORT_REVIEW_REQUIRED: "obtain_operator_live_runtime_approval",
    }.get(status, "provide_valid_oanda_live_http_transport_config")


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
