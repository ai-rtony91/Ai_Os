from __future__ import annotations

from typing import Any, Protocol

from automation.forex_engine import schema_contracts as schemas


PAPER_DEMO_MODE = "PAPER_DEMO"
PAPER_DEMO_CONNECTED = "PAPER_DEMO_CONNECTED"
PAPER_DEMO_AUTHENTICATED = "PAPER_DEMO_AUTHENTICATED"
PAPER_ORDER_ACCEPTED = "PAPER_ORDER_ACCEPTED"
PAPER_ORDER_REJECTED = "PAPER_ORDER_REJECTED"
PAPER_FILL_SIMULATED = "PAPER_FILL_SIMULATED"
PAPER_POSITION_OPEN = "PAPER_POSITION_OPEN"
PAPER_POSITION_CLOSED = "PAPER_POSITION_CLOSED"
UNSUPPORTED_ACTION_BLOCKED = "UNSUPPORTED_ACTION_BLOCKED"
LIVE_EXECUTION_BLOCKED = "LIVE_EXECUTION_BLOCKED"

ALLOWED_INSTRUMENTS = ("EUR_USD", "GBP_USD", "USD_JPY")
LOCAL_MARKET = {
    "EUR_USD": {"bid": 1.07995, "ask": 1.08005, "spread_pips": 1.0},
    "GBP_USD": {"bid": 1.26993, "ask": 1.27007, "spread_pips": 1.4},
    "USD_JPY": {"bid": 154.995, "ask": 155.005, "spread_pips": 1.0},
}
FORBIDDEN_FIELD_NAMES = {
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "token",
    "password",
    "secret",
    "private_key",
    "credential",
    "credentials",
    "broker_credentials",
    "account_id",
    "account_number",
    "live_account_id",
    "broker_order_id",
    "live_payload",
    "raw_live_payload",
}


class BrokerPaperAdapter(Protocol):
    def connect(self, request: dict[str, Any] | None = None) -> dict[str, Any]:
        ...

    def authenticate(self, request: dict[str, Any] | None = None) -> dict[str, Any]:
        ...

    def get_market_data(self, instrument: str) -> dict[str, Any]:
        ...

    def get_account_state(self) -> dict[str, Any]:
        ...

    def create_order(self, order: dict[str, Any]) -> dict[str, Any]:
        ...

    def get_position_state(self) -> dict[str, Any]:
        ...

    def close_position(self, position_id: str, close_price: float | None = None) -> dict[str, Any]:
        ...

    def build_evidence_bundle(self) -> dict[str, Any]:
        ...


def build_paper_demo_broker_adapter_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_PAPER_DEMO_BROKER_ADAPTER_CONTRACT.v1",
        "mode": PAPER_DEMO_MODE,
        "adapter_name": "AIOS_PAPER_DEMO_BROKER_ADAPTER",
        "supported_capabilities": [
            "connect",
            "authenticate",
            "market_data",
            "account_state",
            "order_simulation",
            "fill_simulation",
            "position_state",
            "position_close",
            "evidence_generation",
        ],
        "unsupported_actions_fail_closed": True,
        "allowed_instruments": list(ALLOWED_INSTRUMENTS),
        "market_data_source": "LOCAL_DETERMINISTIC_FIXTURE",
        "account_state_source": "SANITIZED_IN_MEMORY_PAPER_STATE",
        "evidence_storage": "IN_MEMORY_ONLY",
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "live_execution_allowed": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
    }
    schemas.assert_no_live_permissions(contract)
    return contract


class PaperDemoBrokerAdapter:
    def __init__(
        self,
        *,
        starting_balance_usd: float = 500.0,
        available_margin_usd: float = 500.0,
        max_units: int = 1,
    ) -> None:
        self.starting_balance_usd = float(starting_balance_usd)
        self.current_balance_usd = float(starting_balance_usd)
        self.available_margin_usd = float(available_margin_usd)
        self.max_units = int(max_units)
        self.connected = False
        self.authenticated = False
        self._sequence = 0
        self._orders: dict[str, dict[str, Any]] = {}
        self._fills: dict[str, dict[str, Any]] = {}
        self._positions: dict[str, dict[str, Any]] = {}
        self._events: list[dict[str, Any]] = []

    def connect(self, request: dict[str, Any] | None = None) -> dict[str, Any]:
        blocked = _blocked_request_reasons(request or {})
        if blocked:
            result = self._blocked_state("connect", blocked)
        else:
            self.connected = True
            result = {
                "schema": "AIOS_PAPER_DEMO_BROKER_CONNECT.v1",
                "adapter_name": "AIOS_PAPER_DEMO_BROKER_ADAPTER",
                "mode": PAPER_DEMO_MODE,
                "status": PAPER_DEMO_CONNECTED,
                "connected": True,
                "paper_demo": True,
                "broker_connection_allowed": False,
                "live_execution_allowed": False,
                "broker_sdk_allowed": False,
                "network_api_allowed": False,
                "credentials_allowed": False,
                "credential_material_present": False,
                "broker_request_sent": False,
                "network_used": False,
                "credentials_used": False,
                "live_ready": False,
                "live_trade_ready": False,
            }
        self._record_event("connect", result)
        return result

    def authenticate(self, request: dict[str, Any] | None = None) -> dict[str, Any]:
        blocked = _blocked_request_reasons(request or {})
        if not self.connected:
            blocked.append("connect_required_before_authenticate")
        if blocked:
            result = self._blocked_state("authenticate", blocked)
        else:
            self.authenticated = True
            result = {
                "schema": "AIOS_PAPER_DEMO_BROKER_AUTH.v1",
                "mode": PAPER_DEMO_MODE,
                "status": PAPER_DEMO_AUTHENTICATED,
                "authenticated": True,
                "auth_model": "LOCAL_PAPER_DEMO_SESSION",
                "credential_material_required": False,
                "credential_material_present": False,
                "credentials_allowed": False,
                "credentials_used": False,
                "env_secret_read_allowed": False,
                "network_api_allowed": False,
                "broker_request_sent": False,
                "network_used": False,
                "live_execution_allowed": False,
                "live_ready": False,
                "live_trade_ready": False,
            }
        self._record_event("authenticate", result)
        return result

    def get_market_data(self, instrument: str) -> dict[str, Any]:
        normalized = _normalize_instrument(instrument)
        blockers = self._session_blockers()
        if normalized not in ALLOWED_INSTRUMENTS:
            blockers.append("instrument_not_allowlisted")
        if blockers:
            result = self._blocked_state("market_data", blockers, instrument=normalized)
        else:
            quote = LOCAL_MARKET[normalized]
            bid = float(quote["bid"])
            ask = float(quote["ask"])
            result = {
                "schema": "AIOS_PAPER_DEMO_MARKET_DATA.v1",
                "mode": PAPER_DEMO_MODE,
                "status": "LOCAL_MARKET_DATA_READY",
                "instrument": normalized,
                "bid": bid,
                "ask": ask,
                "mid_price": round((bid + ask) / 2, 5),
                "price": round((bid + ask) / 2, 5),
                "spread_pips": float(quote["spread_pips"]),
                "source": "LOCAL_DETERMINISTIC_FIXTURE",
                "live_market_data": False,
                "broker_request_sent": False,
                "network_used": False,
                "live_ready": False,
            }
        self._record_event("market_data", result)
        return result

    def get_account_state(self) -> dict[str, Any]:
        blockers = self._session_blockers()
        if blockers:
            result = self._blocked_state("account_state", blockers)
        else:
            result = {
                "schema": "AIOS_PAPER_DEMO_ACCOUNT_STATE.v1",
                "mode": PAPER_DEMO_MODE,
                "status": "SANITIZED_PAPER_ACCOUNT_STATE",
                "account_mode": "PAPER_DEMO",
                "starting_balance_usd": self.starting_balance_usd,
                "current_balance_usd": self.current_balance_usd,
                "available_margin_usd": self.available_margin_usd,
                "open_positions": len(self._positions),
                "open_position_count": len(self._positions),
                "live_account_data": False,
                "broker_request_sent": False,
                "network_used": False,
                "credentials_used": False,
                "live_ready": False,
                "live_trade_ready": False,
            }
        self._record_event("account_state", result)
        return result

    def create_order(self, order: dict[str, Any]) -> dict[str, Any]:
        blockers = self._session_blockers()
        blockers.extend(_blocked_request_reasons(order))
        order_contract = _normalize_order(order)
        blockers.extend(_order_blockers(order_contract, self.max_units))
        if blockers:
            result = {
                **self._blocked_state("order_create", blockers),
                "schema": "AIOS_PAPER_DEMO_ORDER_STATE.v1",
                "status": PAPER_ORDER_REJECTED,
                "order_status": PAPER_ORDER_REJECTED,
                "order_accepted": False,
                "fill": None,
                "position": None,
            }
            self._record_event("order_reject", result)
            return result

        self._sequence += 1
        paper_order_id = f"AIOS-PAPER-ORDER-{self._sequence:06d}"
        fill_id = f"AIOS-PAPER-FILL-{self._sequence:06d}"
        position_id = f"AIOS-PAPER-POSITION-{self._sequence:06d}"
        market = LOCAL_MARKET[order_contract["instrument"]]
        fill_price = round((float(market["bid"]) + float(market["ask"])) / 2, 5)
        order_state = {
            "schema": "AIOS_PAPER_DEMO_ORDER_STATE.v1",
            "mode": PAPER_DEMO_MODE,
            "status": PAPER_ORDER_ACCEPTED,
            "order_status": PAPER_FILL_SIMULATED,
            "order_accepted": True,
            "paper_order_id": paper_order_id,
            "client_order_id": order_contract["client_order_id"],
            "instrument": order_contract["instrument"],
            "side": order_contract["side"],
            "order_type": order_contract["order_type"],
            "requested_units": order_contract["units"],
            "filled_units": order_contract["units"],
            "requested_price": order_contract["requested_price"],
            "fill_price": fill_price,
            "stop_loss": order_contract["stop_loss"],
            "take_profit": order_contract["take_profit"],
            "paper_only": True,
            "execution_allowed": False,
            "live_order": False,
            "would_place_order": False,
            "order_placed": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "live_trade_ready": False,
        }
        fill = _build_fill(order_state, fill_id)
        position = _build_open_position(order_state, fill, position_id)
        order_state["fill"] = fill
        order_state["position"] = position
        self._orders[paper_order_id] = order_state
        self._fills[fill_id] = fill
        self._positions[position_id] = position
        self._record_event("order_create", order_state)
        self._record_event("fill", fill)
        self._record_event("position_open", position)
        schemas.assert_no_live_permissions(order_state)
        return order_state

    def get_position_state(self) -> dict[str, Any]:
        result = {
            "schema": "AIOS_PAPER_DEMO_POSITION_STATE.v1",
            "mode": PAPER_DEMO_MODE,
            "status": "PAPER_POSITION_STATE_READY",
            "open_position_count": len(self._positions),
            "positions": [dict(position) for position in self._positions.values()],
            "paper_only": True,
            "live_order": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "live_trade_ready": False,
        }
        self._record_event("position_state", result)
        schemas.assert_no_live_permissions(result)
        return result

    def close_position(self, position_id: str, close_price: float | None = None) -> dict[str, Any]:
        position = self._positions.pop(position_id, None)
        if position is None:
            result = {
                **self._blocked_state("position_close", ["position_not_found"]),
                "schema": "AIOS_PAPER_DEMO_POSITION_CLOSE.v1",
                "status": PAPER_ORDER_REJECTED,
                "position_closed": False,
                "realized_pl_usd": None,
            }
            self._record_event("position_close_reject", result)
            return result

        close_value = float(close_price if close_price is not None else position["entry_price"])
        side = str(position["side"])
        units = float(position["units"])
        entry = float(position["entry_price"])
        if side == "BUY":
            realized_pl_usd = round((close_value - entry) * units, 2)
        else:
            realized_pl_usd = round((entry - close_value) * units, 2)
        self.current_balance_usd = round(self.current_balance_usd + realized_pl_usd, 2)
        self.available_margin_usd = round(self.available_margin_usd + float(position["margin_reserved_usd"]), 2)
        result = {
            "schema": "AIOS_PAPER_DEMO_POSITION_CLOSE.v1",
            "mode": PAPER_DEMO_MODE,
            "status": PAPER_POSITION_CLOSED,
            "position_id": position_id,
            "position_closed": True,
            "instrument": position["instrument"],
            "side": side,
            "units": units,
            "entry_price": entry,
            "close_price": close_value,
            "realized_pl_usd": realized_pl_usd,
            "pl_capture_status": "RECORDED",
            "paper_only": True,
            "live_order": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "live_trade_ready": False,
        }
        self._record_event("position_close", result)
        schemas.assert_no_live_permissions(result)
        return result

    def build_evidence_bundle(self) -> dict[str, Any]:
        result = {
            "schema": "AIOS_PAPER_DEMO_ADAPTER_EVIDENCE.v1",
            "mode": PAPER_DEMO_MODE,
            "status": "PAPER_DEMO_EVIDENCE_READY",
            "archive_status": "IN_MEMORY_ONLY",
            "event_count": len(self._events),
            "events": [dict(event) for event in self._events],
            "sanitized": True,
            "contains_private_data": False,
            "contains_real_credentials": False,
            "broker_sdk_allowed": False,
            "network_api_allowed": False,
            "credentials_allowed": False,
            "broker_paper_orders_allowed": False,
            "live_orders_allowed": False,
            "live_order": False,
            "would_place_order": False,
            "order_placed": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "live_trade_ready": False,
        }
        schemas.assert_no_live_permissions(result)
        return result

    def perform_unsupported_action(self, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        blockers = ["unsupported_broker_action", *_blocked_request_reasons(payload or {})]
        result = {
            **self._blocked_state("unsupported_action", blockers),
            "schema": "AIOS_PAPER_DEMO_UNSUPPORTED_ACTION.v1",
            "status": UNSUPPORTED_ACTION_BLOCKED,
            "action": str(action or "unknown"),
        }
        self._record_event("unsupported_action", result)
        return result

    def submit_live_order(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        result = {
            **self._blocked_state("live_order", ["live_execution_blocked", *_blocked_request_reasons(payload or {})]),
            "schema": "AIOS_PAPER_DEMO_LIVE_EXECUTION_BLOCK.v1",
            "status": LIVE_EXECUTION_BLOCKED,
            "live_execution_allowed": False,
            "live_orders_allowed": False,
        }
        self._record_event("live_order_block", result)
        return result

    def _session_blockers(self) -> list[str]:
        blockers: list[str] = []
        if not self.connected:
            blockers.append("connect_required")
        if not self.authenticated:
            blockers.append("authenticate_required")
        return blockers

    def _blocked_state(
        self,
        operation: str,
        blockers: list[str],
        **extra: Any,
    ) -> dict[str, Any]:
        result = {
            "schema": "AIOS_PAPER_DEMO_BLOCKED_ACTION.v1",
            "mode": PAPER_DEMO_MODE,
            "operation": operation,
            "status": PAPER_ORDER_REJECTED,
            "blocked": True,
            "blockers": _unique(blockers),
            "paper_only": True,
            "execution_allowed": False,
            "live_order": False,
            "live_execution_allowed": False,
            "broker_sdk_allowed": False,
            "network_api_allowed": False,
            "credentials_allowed": False,
            "env_secret_read_allowed": False,
            "broker_paper_orders_allowed": False,
            "live_orders_allowed": False,
            "would_place_order": False,
            "order_placed": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "live_trade_ready": False,
            "real_order_ready": False,
            **extra,
        }
        schemas.assert_no_live_permissions(result)
        return result

    def _record_event(self, event: str, payload: dict[str, Any]) -> None:
        self._events.append(
            {
                "event": event,
                "recorded": True,
                "sanitized": True,
                "paper_only": True,
                "status": payload.get("status"),
                "schema": payload.get("schema"),
                "contains_private_data": False,
                "contains_real_credentials": False,
            }
        )


def _normalize_order(order: dict[str, Any]) -> dict[str, Any]:
    instrument = _normalize_instrument(order.get("instrument") or order.get("symbol"))
    return {
        "client_order_id": str(order.get("client_order_id") or "AIOS-PAPER-DEMO-ORDER"),
        "instrument": instrument,
        "side": str(order.get("side") or "").upper(),
        "order_type": str(order.get("order_type") or "").upper(),
        "units": _int_or_zero(order.get("units") or order.get("requested_units")),
        "requested_price": _float_or_none(
            order.get("requested_price") or order.get("entry_reference_price")
        ),
        "stop_loss": _float_or_none(order.get("stop_loss")),
        "take_profit": _float_or_none(order.get("take_profit")),
        "max_loss_usd": _float_or_none(order.get("max_loss_usd")),
    }


def _order_blockers(order: dict[str, Any], max_units: int) -> list[str]:
    blockers: list[str] = []
    if order["instrument"] not in ALLOWED_INSTRUMENTS:
        blockers.append("instrument_not_allowlisted")
    if order["side"] not in {"BUY", "SELL"}:
        blockers.append("side_must_be_buy_or_sell")
    if order["order_type"] != "MARKET":
        blockers.append("only_market_orders_supported_in_paper_demo_adapter")
    if order["units"] <= 0:
        blockers.append("units_must_be_positive")
    if order["units"] > max_units:
        blockers.append("units_exceed_paper_demo_limit")
    if order["stop_loss"] is None or order["stop_loss"] <= 0:
        blockers.append("stop_loss_required")
    if order["max_loss_usd"] is None or order["max_loss_usd"] <= 0:
        blockers.append("max_loss_required")
    return blockers


def _build_fill(order_state: dict[str, Any], fill_id: str) -> dict[str, Any]:
    return {
        "schema": "AIOS_PAPER_DEMO_FILL.v1",
        "mode": PAPER_DEMO_MODE,
        "status": PAPER_FILL_SIMULATED,
        "fill_id": fill_id,
        "paper_order_id": order_state["paper_order_id"],
        "instrument": order_state["instrument"],
        "side": order_state["side"],
        "filled_units": order_state["filled_units"],
        "fill_price": order_state["fill_price"],
        "fill_verified": True,
        "paper_only": True,
        "live_order": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
    }


def _build_open_position(
    order_state: dict[str, Any],
    fill: dict[str, Any],
    position_id: str,
) -> dict[str, Any]:
    units = float(fill["filled_units"])
    return {
        "schema": "AIOS_PAPER_DEMO_POSITION.v1",
        "mode": PAPER_DEMO_MODE,
        "status": PAPER_POSITION_OPEN,
        "position_id": position_id,
        "paper_order_id": order_state["paper_order_id"],
        "fill_id": fill["fill_id"],
        "instrument": order_state["instrument"],
        "side": order_state["side"],
        "units": units,
        "entry_price": fill["fill_price"],
        "stop_loss": order_state["stop_loss"],
        "take_profit": order_state["take_profit"],
        "margin_reserved_usd": round(units * 0.02, 2),
        "paper_only": True,
        "live_order": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
    }


def _blocked_request_reasons(value: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in _forbidden_field_paths(value):
        blockers.append(f"forbidden_field:{field}")
    mode = str(value.get("mode") or value.get("account_mode") or "").upper()
    if "LIVE" in mode:
        blockers.append("live_mode_blocked")
    for key, nested in value.items():
        normalized = _normalize_key(str(key))
        if normalized in {"live_order", "live_ready", "live_trade_ready", "live_execution_allowed"} and nested is True:
            blockers.append(f"live_permission_attempt:{normalized}")
        if normalized in {"broker_request_sent", "network_used", "credentials_used", "order_placed"} and nested is True:
            blockers.append(f"execution_side_effect_attempt:{normalized}")
    return _unique(blockers)


def _forbidden_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in FORBIDDEN_FIELD_NAMES:
                paths.append(path)
            paths.extend(_forbidden_field_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_forbidden_field_paths(nested, f"{prefix}[{index}]"))
    return _unique(paths)


def _normalize_instrument(value: Any) -> str:
    text = str(value or "").strip().upper().replace("/", "_").replace("-", "_")
    if len(text) == 6 and "_" not in text:
        return f"{text[:3]}_{text[3:]}"
    return text


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
