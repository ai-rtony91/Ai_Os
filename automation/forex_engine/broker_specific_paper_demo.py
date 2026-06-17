from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


BROKER_ID = "OANDA"
BROKER_REFERENCE = "OANDA_PAPER_DEMO_REFERENCE_ONLY"
PAPER_DEMO_ENVIRONMENT = "PRACTICE_DEMO"
CONFIG_READY = "BROKER_SPECIFIC_PAPER_DEMO_CONFIG_READY"
CONFIG_BLOCKED = "BROKER_SPECIFIC_PAPER_DEMO_CONFIG_BLOCKED"
MAPPING_READY = "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_READY"
MAPPING_BLOCKED = "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_BLOCKED"
LIVE_EXECUTION_BLOCKED = "BROKER_SPECIFIC_LIVE_EXECUTION_BLOCKED"
SUPPORTED_ACCOUNT_MODES = {"PRACTICE_DEMO", "PAPER_DEMO"}
SUPPORTED_ORDER_TYPES = {"MARKET"}
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
    "transaction_id",
    "live_payload",
    "raw_live_payload",
}


@dataclass(frozen=True)
class BrokerSpecificPaperDemoConfig:
    broker_id: str = BROKER_ID
    account_mode: str = PAPER_DEMO_ENVIRONMENT
    environment: str = "PRACTICE_REFERENCE_ONLY"
    external_auth_reference_present: bool = True
    human_approval_reference: str = "AIOS-FOREX-BROKER-SPECIFIC-PAPER-DEMO-INTEGRATION-V1"
    paper_demo_mode_confirmation: bool = True
    broker_sdk_allowed: bool = False
    network_api_allowed: bool = False
    credentials_allowed: bool = False
    env_secret_read_allowed: bool = False
    live_execution_allowed: bool = False
    live_orders_allowed: bool = False
    broker_request_allowed: bool = False


def default_broker_specific_paper_demo_config() -> BrokerSpecificPaperDemoConfig:
    return BrokerSpecificPaperDemoConfig()


def build_broker_specific_paper_demo_interface_requirements() -> dict[str, Any]:
    requirements = {
        "schema": "AIOS_BROKER_SPECIFIC_PAPER_DEMO_INTERFACE_REQUIREMENTS.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "supported_account_modes": sorted(SUPPORTED_ACCOUNT_MODES),
        "supported_order_types": sorted(SUPPORTED_ORDER_TYPES),
        "required_mappings": [
            "account_state",
            "market_data",
            "order_state",
            "fill_state",
            "evidence",
        ],
        "external_auth_reference_required": True,
        "repo_stored_auth_material_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "broker_request_allowed": False,
        "live_execution_allowed": False,
        "live_orders_allowed": False,
        "live_account_access_allowed": False,
        "real_money_routing_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "fail_closed_for_missing_external_auth": True,
        "fail_closed_for_unsupported_account_mode": True,
        "fail_closed_for_live_execution_attempts": True,
    }
    schemas.assert_no_live_permissions(requirements)
    return requirements


def validate_broker_specific_paper_demo_config(
    config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _config_payload(config)
    blockers: list[str] = []
    forbidden_fields = _forbidden_field_paths(payload)
    blockers.extend([f"forbidden_field:{field}" for field in forbidden_fields])

    broker_id = str(payload.get("broker_id") or "").upper()
    account_mode = str(payload.get("account_mode") or "").upper()
    if broker_id != BROKER_ID:
        blockers.append("unsupported_broker_target")
    if account_mode not in SUPPORTED_ACCOUNT_MODES:
        blockers.append("unsupported_account_mode")
    if "LIVE" in account_mode:
        blockers.append("live_account_mode_blocked")
    if payload.get("external_auth_reference_present") is not True:
        blockers.append("missing_external_auth_reference")
    if payload.get("paper_demo_mode_confirmation") is not True:
        blockers.append("paper_demo_mode_confirmation_required")

    for field in (
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "live_execution_allowed",
        "live_orders_allowed",
        "broker_request_allowed",
    ):
        if payload.get(field) is True:
            blockers.append(f"forbidden_capability_enabled:{field}")

    result = {
        "schema": "AIOS_BROKER_SPECIFIC_PAPER_DEMO_CONFIG_VALIDATION.v1",
        "broker_id": broker_id or BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "account_mode": account_mode,
        "environment": str(payload.get("environment") or "PRACTICE_REFERENCE_ONLY"),
        "status": CONFIG_BLOCKED if blockers else CONFIG_READY,
        "config_valid": not blockers,
        "blockers": _unique(blockers),
        "external_auth_reference_present": payload.get("external_auth_reference_present") is True,
        "repo_stored_auth_material_present": False,
        "repo_stored_auth_material_allowed": False,
        "credential_material_present": False,
        "credential_material_required_external": True,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "broker_request_allowed": False,
        "live_execution_allowed": False,
        "live_orders_allowed": False,
        "live_account_access_allowed": False,
        "real_money_routing_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
    }
    schemas.assert_no_live_permissions(result)
    return result


def map_broker_specific_account_state(
    account_state: dict[str, Any],
    config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None = None,
) -> dict[str, Any]:
    validation = validate_broker_specific_paper_demo_config(config)
    if not validation["config_valid"]:
        return _blocked_mapping("account_state", validation)
    result = {
        "schema": "AIOS_OANDA_PAPER_DEMO_ACCOUNT_STATE_MAPPING.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": MAPPING_READY,
        "account_mode": "PRACTICE_DEMO",
        "currency": "USD",
        "balance_usd": float(account_state.get("current_balance_usd", 0.0)),
        "nav_usd": float(account_state.get("current_balance_usd", 0.0)),
        "margin_available_usd": float(account_state.get("available_margin_usd", 0.0)),
        "open_trade_count": int(account_state.get("open_position_count", account_state.get("open_positions", 0))),
        "account_identifier_present": False,
        "live_account_data": False,
        "sanitized": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def map_broker_specific_market_data(
    market_data: dict[str, Any],
    config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None = None,
) -> dict[str, Any]:
    validation = validate_broker_specific_paper_demo_config(config)
    if not validation["config_valid"]:
        return _blocked_mapping("market_data", validation)
    instrument = _normalize_instrument(market_data.get("instrument"))
    bid = _float_or_zero(market_data.get("bid"))
    ask = _float_or_zero(market_data.get("ask"))
    if bid <= 0 and ask <= 0:
        mid = _float_or_zero(market_data.get("price") or market_data.get("mid_price"))
        bid = mid
        ask = mid
    result = {
        "schema": "AIOS_OANDA_PAPER_DEMO_MARKET_DATA_MAPPING.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": MAPPING_READY,
        "instrument": instrument,
        "oanda_instrument": instrument,
        "quote_type": "PRICE_REFERENCE_ONLY",
        "bid": bid,
        "ask": ask,
        "mid_price": round((bid + ask) / 2, 5) if bid and ask else _float_or_zero(market_data.get("price")),
        "spread_pips": _float_or_zero(market_data.get("spread_pips")),
        "source": "LOCAL_DETERMINISTIC_FIXTURE_MAPPED_TO_OANDA_SHAPE",
        "live_market_data": False,
        "sanitized": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def map_broker_specific_order_state(
    order_state: dict[str, Any],
    config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None = None,
) -> dict[str, Any]:
    validation = validate_broker_specific_paper_demo_config(config)
    if not validation["config_valid"]:
        return _blocked_mapping("order_state", validation)
    side = str(order_state.get("side") or "").upper()
    units = int(order_state.get("filled_units") or order_state.get("requested_units") or 0)
    signed_units = units if side == "BUY" else -units
    result = {
        "schema": "AIOS_OANDA_PAPER_DEMO_ORDER_STATE_MAPPING.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": MAPPING_READY,
        "paper_order_id": str(order_state.get("paper_order_id") or ""),
        "client_order_id": str(order_state.get("client_order_id") or ""),
        "oanda_instrument": _normalize_instrument(order_state.get("instrument")),
        "oanda_order_type": str(order_state.get("order_type") or "MARKET").upper(),
        "oanda_units_preview": signed_units,
        "time_in_force_preview": "FOK",
        "position_fill_preview": "DEFAULT",
        "stop_loss_preview": order_state.get("stop_loss"),
        "take_profit_preview": order_state.get("take_profit"),
        "order_status": str(order_state.get("order_status") or order_state.get("status") or ""),
        "route_allowed": False,
        "paper_only": True,
        "sanitized": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def map_broker_specific_fill_state(
    fill_state: dict[str, Any],
    config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None = None,
) -> dict[str, Any]:
    validation = validate_broker_specific_paper_demo_config(config)
    if not validation["config_valid"]:
        return _blocked_mapping("fill_state", validation)
    result = {
        "schema": "AIOS_OANDA_PAPER_DEMO_FILL_STATE_MAPPING.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": MAPPING_READY,
        "fill_id": str(fill_state.get("fill_id") or ""),
        "paper_order_id": str(fill_state.get("paper_order_id") or ""),
        "oanda_transaction_type_preview": "ORDER_FILL_REFERENCE_ONLY",
        "oanda_transaction_identifier_present": False,
        "oanda_instrument": _normalize_instrument(fill_state.get("instrument")),
        "filled_units": int(fill_state.get("filled_units") or 0),
        "fill_price": _float_or_zero(fill_state.get("fill_price")),
        "fill_verified": fill_state.get("fill_verified") is True,
        "paper_only": True,
        "sanitized": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def build_broker_specific_evidence_mapping(
    *,
    config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None = None,
    account_mapping: dict[str, Any] | None = None,
    market_mapping: dict[str, Any] | None = None,
    order_mapping: dict[str, Any] | None = None,
    fill_mapping: dict[str, Any] | None = None,
    source_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validation = validate_broker_specific_paper_demo_config(config)
    mappings = [
        dict(account_mapping or {}),
        dict(market_mapping or {}),
        dict(order_mapping or {}),
        dict(fill_mapping or {}),
    ]
    mapping_blockers = [
        blocker
        for mapping in mappings
        for blocker in list(mapping.get("blockers") or [])
    ]
    blockers = _unique([*validation["blockers"], *mapping_blockers])
    result = {
        "schema": "AIOS_OANDA_PAPER_DEMO_EVIDENCE_MAPPING.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": MAPPING_BLOCKED if blockers else MAPPING_READY,
        "evidence_ready": not blockers,
        "blockers": blockers,
        "source_evidence_status": str((source_evidence or {}).get("status") or "UNKNOWN"),
        "mapped_artifacts": [
            "account_state",
            "market_data",
            "order_state",
            "fill_state",
        ],
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "repo_stored_auth_material_present": False,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def build_broker_specific_paper_demo_mapping_set(
    *,
    config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None = None,
    account_state: dict[str, Any],
    market_data: dict[str, Any],
    order_state: dict[str, Any],
    fill_state: dict[str, Any],
    source_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_config = config or default_broker_specific_paper_demo_config()
    validation = validate_broker_specific_paper_demo_config(active_config)
    account_mapping = map_broker_specific_account_state(account_state, active_config)
    market_mapping = map_broker_specific_market_data(market_data, active_config)
    order_mapping = map_broker_specific_order_state(order_state, active_config)
    fill_mapping = map_broker_specific_fill_state(fill_state, active_config)
    evidence_mapping = build_broker_specific_evidence_mapping(
        config=active_config,
        account_mapping=account_mapping,
        market_mapping=market_mapping,
        order_mapping=order_mapping,
        fill_mapping=fill_mapping,
        source_evidence=source_evidence,
    )
    result = {
        "schema": "AIOS_BROKER_SPECIFIC_PAPER_DEMO_MAPPING_SET.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": MAPPING_READY if evidence_mapping["evidence_ready"] else MAPPING_BLOCKED,
        "config_validation": validation,
        "interface_requirements": build_broker_specific_paper_demo_interface_requirements(),
        "account_mapping": account_mapping,
        "market_data_mapping": market_mapping,
        "order_state_mapping": order_mapping,
        "fill_state_mapping": fill_mapping,
        "evidence_mapping": evidence_mapping,
        "paper_demo_only": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def reject_broker_specific_live_execution_attempt(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers = ["live_execution_blocked"]
    blockers.extend([f"forbidden_field:{field}" for field in _forbidden_field_paths(payload or {})])
    mode = str((payload or {}).get("mode") or (payload or {}).get("account_mode") or "").upper()
    if "LIVE" in mode:
        blockers.append("live_account_mode_blocked")
    result = {
        "schema": "AIOS_BROKER_SPECIFIC_LIVE_EXECUTION_REJECTION.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": LIVE_EXECUTION_BLOCKED,
        "blocked": True,
        "blockers": _unique(blockers),
        "paper_demo_only": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def fail_closed_broker_specific_action(
    action: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blockers = ["unsupported_broker_specific_action"]
    blockers.extend([f"forbidden_field:{field}" for field in _forbidden_field_paths(payload or {})])
    result = {
        "schema": "AIOS_BROKER_SPECIFIC_FAIL_CLOSED_ACTION.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": MAPPING_BLOCKED,
        "action": str(action or "unknown"),
        "blocked": True,
        "blockers": _unique(blockers),
        "paper_demo_only": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def _blocked_mapping(operation: str, validation: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema": "AIOS_BROKER_SPECIFIC_PAPER_DEMO_BLOCKED_MAPPING.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "operation": operation,
        "status": MAPPING_BLOCKED,
        "blocked": True,
        "blockers": list(validation.get("blockers") or []),
        "paper_demo_only": True,
        **_blocked_capabilities(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def _blocked_capabilities() -> dict[str, Any]:
    return {
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "broker_request_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "live_execution_allowed": False,
        "live_account_access_allowed": False,
        "real_money_routing_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "live_order": False,
    }


def _config_payload(config: BrokerSpecificPaperDemoConfig | dict[str, Any] | None) -> dict[str, Any]:
    if config is None:
        return asdict(default_broker_specific_paper_demo_config())
    if isinstance(config, BrokerSpecificPaperDemoConfig):
        return asdict(config)
    return dict(config)


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


def _float_or_zero(value: Any) -> float:
    try:
        if value in (None, ""):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
