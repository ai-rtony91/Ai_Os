"""Broker demo connector readiness probe V2.

Provides an offline-default, deterministic readiness evaluation for whether a
connector is safe to advance toward protected OANDA demo connection review.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, Sequence

from automation.forex_engine import no_order_connector_contracts_g_v1

BROKER_DEMO_PROBE_BLOCKED = "BROKER_DEMO_PROBE_BLOCKED"
BROKER_DEMO_PROBE_READY = "BROKER_DEMO_PROBE_READY"
BROKER_DEMO_PROBE_CONNECTOR_REJECTED = "BROKER_DEMO_PROBE_CONNECTOR_REJECTED"
BROKER_DEMO_PROBE_CONTRACT_INVALID = "BROKER_DEMO_PROBE_CONTRACT_INVALID"

PROBE_SCHEMA = "AIOS_BROKER_DEMO_CONNECTOR_READINESS_PROBE_V2_SCHEMA.v1"
PROBE_CONNECTOR_MODE = "DEMO_DRYRUN"
ALLOWED_ENDPOINT_CLASSIFICATIONS = frozenset({"PRACTICE_DEMO", "PRACTICE_REFERENCE_ONLY", "OANDA_PRACTICE_DEMO"})
STALE_QUOTE_WINDOW_SECONDS = 300
SENSITIVE_KEYS = frozenset(
    {
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "password",
        "private_key",
        "credential",
        "credentials",
        "broker_credentials",
        "account_id",
        "account_number",
        "live_account_id",
        "account_identifier",
        "broker_order_id",
        "raw_request",
        "raw_response",
    }
)


@dataclass(frozen=True)
class BrokerDemoConnectorProbeResult:
    status: str
    ready: bool
    blocked_reasons: tuple[str, ...]
    sanitized_output: dict[str, Any]
    readiness_contract: dict[str, Any]
    connector_status: str
    connector_result: dict[str, Any]


def build_broker_demo_probe_contract() -> dict[str, Any]:
    contract: dict[str, Any] = {
        "schema": "AIOS_BROKER_DEMO_CONNECTOR_READINESS_PROBE_CONTRACT_V2.v1",
        "mode": PROBE_CONNECTOR_MODE,
        "required_gate_fields": (
            "connector_mode",
            "approved_by_human",
            "simulation_only",
            "broker_demo_only",
            "network_allowed",
            "credentials_present",
            "account_id_present",
            "endpoint_classification",
            "kill_switch_enabled",
            "max_loss_gate_clear",
            "daily_stop_clear",
        ),
        "required_approvals": ("approved_by_human", "simulation_only", "broker_demo_only"),
        "forbidden_live_indicators": (
            "live_endpoint_requested",
            "broker_request_requested",
            "order_route_requested",
            "account_state_requested",
            "market_data_requested",
            "order_placed",
            "live_execution_allowed",
            "network_api_allowed",
            "broker_request_sent",
            "connection_attempt_performed",
        ),
        "allowed_endpoint_classifications": sorted(ALLOWED_ENDPOINT_CLASSIFICATIONS),
        "connector_mode_required": PROBE_CONNECTOR_MODE,
        "approved_connector_required": True,
        "max_retry_attempts": 1,
        "retry_loop_allowed": False,
        "safe_gate_benchmarks": {
            "config_validation_ms": 4,
            "connector_readiness_ms": 6,
            "account_envelope_ms": 5,
            "instrument_envelope_ms": 5,
            "quote_envelope_ms": 6,
            "broker_response_placeholder_ms": 0,
            "network_placeholder_ms": 0,
        },
    }
    return contract


def build_connector_readiness_evidence_schema() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_DEMO_CONNECTOR_READINESS_EVIDENCE_V2.v1",
        "probe_ready": False,
        "connector_ready": False,
        "network_call_performed": False,
        "connection_attempt_performed": False,
        "account_response_persisted": False,
        "quote_response_persisted": False,
        "contains_private_data": False,
        "contains_token": False,
        "contains_secret": False,
        "contains_account_identifier": False,
        "raw_endpoint_present": False,
        "broker_paper_only": True,
        "contract": build_broker_demo_probe_contract()["schema"],
    }


def build_broker_demo_probe_latency_buckets() -> dict[str, Any]:
    contract = build_broker_demo_probe_contract()
    budgets = contract["safe_gate_benchmarks"]
    return {
        "schema": "AIOS_BROKER_DEMO_CONNECTOR_READINESS_LATENCY_BUDGET_V2.v1",
        "config_validation_ms": budgets["config_validation_ms"],
        "connector_readiness_ms": budgets["connector_readiness_ms"],
        "account_envelope_ms": budgets["account_envelope_ms"],
        "instrument_envelope_ms": budgets["instrument_envelope_ms"],
        "quote_envelope_ms": budgets["quote_envelope_ms"],
        "broker_response_placeholder_ms": budgets["broker_response_placeholder_ms"],
        "network_latency_explicitly_disabled_ms": budgets["network_placeholder_ms"],
        "default_network_disabled": True,
        "network_latency_separated_by_design": True,
        "total_budget_ms": sum(budgets.values()),
        "buckets": budgets,
    }


def evaluate_demo_connector_readiness(
    *,
    connector_contract: Mapping[str, Any] | None = None,
    connector: Mapping[str, Any] | Callable[..., Any] | object | None = None,
    account_envelope: Mapping[str, Any] | None = None,
    instrument_envelope: Mapping[str, Any] | None = None,
    quote_envelope: Mapping[str, Any] | None = None,
) -> BrokerDemoConnectorProbeResult:
    payload = dict(connector_contract or {})
    blocked: list[str] = []

    contract = build_broker_demo_probe_contract()

    for field in contract["required_gate_fields"]:
        if field not in payload:
            blocked.append(f"missing_field:{field}")

    if _normalize(payload.get("connector_mode")) != PROBE_CONNECTOR_MODE:
        blocked.append("connector_mode_invalid")

    if payload.get("approved_by_human") is not True:
        blocked.append("approved_by_human_required")
    if payload.get("simulation_only") is not True:
        blocked.append("simulation_only_required")
    if payload.get("broker_demo_only") is not True:
        blocked.append("broker_demo_only_required")
    if payload.get("network_allowed") is not False:
        blocked.append("network_allowed_must_be_false")
    if payload.get("credentials_present") is not False:
        blocked.append("credentials_present_must_be_false")
    if payload.get("account_id_present") is not False:
        blocked.append("account_id_present_must_be_false")
    if payload.get("kill_switch_enabled") is not True:
        blocked.append("kill_switch_enabled_required")
    if payload.get("max_loss_gate_clear") is not True:
        blocked.append("max_loss_gate_clear_required")
    if payload.get("daily_stop_clear") is not True:
        blocked.append("daily_stop_clear_required")

    endpoint_classification = _normalize(payload.get("endpoint_classification"))
    if not endpoint_classification:
        blocked.append("endpoint_classification_missing")
    elif endpoint_classification not in ALLOWED_ENDPOINT_CLASSIFICATIONS:
        blocked.append("endpoint_classification_invalid")
    elif endpoint_classification in {"LIVE", "PRODUCTION"}:
        blocked.append("endpoint_classification_rejects_live")

    if payload.get("connector_retry_loop", False):
        blocked.append("retry_loop_blocked")
    if payload.get("max_retry_attempts", 1) != 1:
        blocked.append("retry_attempt_limit_required")

    forbidden_fields = _forbidden_field_paths(payload)
    if forbidden_fields:
        blocked.append("forbidden_field_detected")
        blocked.extend(f"forbidden_field:{path}" for path in forbidden_fields)

    forbidden_values = _forbidden_value_paths(payload)
    if forbidden_values:
        blocked.append("forbidden_value_detected")
        blocked.extend(f"forbidden_value:{path}" for path in forbidden_values if path)

    connector_status = "MISSING"
    connector_result: dict[str, Any] = {
        "schema": "AIOS_BROKER_DEMO_CONNECTOR_REVIEW_V2.v1",
        "approved_connector_present": False,
        "approved_for_demo": False,
        "blockers": ["connector_required_for_review"],
    }

    if connector is None:
        blocked.append("connector_required_for_review")
    else:
        connector_result = evaluate_connector_object_for_demo(connector)
        if not connector_result["ready"]:
            blocked.extend([f"connector_{reason}" for reason in connector_result["blocked_reasons"]])
            connector_status = "REJECTED"
        else:
            connector_status = "READY"

    account_eval = validate_account_envelope(account_envelope)
    instrument_eval = validate_instrument_envelope(instrument_envelope)
    quote_eval = validate_quote_envelope(quote_envelope)
    if not account_eval.ready:
        blocked.extend(f"account_{reason}" for reason in account_eval.blocked_reasons)
    if not instrument_eval.ready:
        blocked.extend(f"instrument_{reason}" for reason in instrument_eval.blocked_reasons)
    if not quote_eval.ready:
        blocked.extend(f"quote_{reason}" for reason in quote_eval.blocked_reasons)

    blocked = tuple(_unique(blocked))
    ready = not blocked and connector_status == "READY"

    if blocked:
        if connector_status == "REJECTED" or "connector_required_for_review" in blocked:
            status = BROKER_DEMO_PROBE_CONNECTOR_REJECTED
        elif any(reason.startswith("connector_") for reason in blocked):
            status = BROKER_DEMO_PROBE_CONNECTOR_REJECTED
        else:
            status = BROKER_DEMO_PROBE_BLOCKED
    else:
        status = BROKER_DEMO_PROBE_READY

    sanitized_output = _sanitize_output(
        {
            "probe_status": status,
            "connector_mode": _normalize(payload.get("connector_mode")),
            "approved_by_human": _as_bool(payload.get("approved_by_human")),
            "simulation_only": _as_bool(payload.get("simulation_only")),
            "broker_demo_only": _as_bool(payload.get("broker_demo_only")),
            "network_allowed": False,
            "network_call_performed": False,
            "network_api_allowed": False,
            "credentials_present": False,
            "account_id_present": False,
            "endpoint_classification": endpoint_classification,
            "kill_switch_enabled": _as_bool(payload.get("kill_switch_enabled")),
            "max_loss_gate_clear": _as_bool(payload.get("max_loss_gate_clear")),
            "daily_stop_clear": _as_bool(payload.get("daily_stop_clear")),
            "live_execution_allowed": False,
            "order_placed": False,
            "broker_request_sent": False,
            "connection_attempt_performed": False,
            "account_envelope_ready": account_eval.ready,
            "instrument_envelope_ready": instrument_eval.ready,
            "quote_envelope_ready": quote_eval.ready,
            "connector_status": connector_status,
            "blocked_reasons": list(blocked),
            "connector_evaluation": connector_result,
            "account_evaluation": account_eval.sanitized_output,
            "instrument_evaluation": instrument_eval.sanitized_output,
            "quote_evaluation": quote_eval.sanitized_output,
            "latency_buckets": build_broker_demo_probe_latency_buckets(),
            "readiness_contract": contract["schema"],
            "evidence": build_connector_readiness_evidence_schema(),
        }
    )
    sanitized_output["evidence"]["probe_ready"] = ready
    sanitized_output["evidence"]["connector_ready"] = connector_status == "READY"

    return BrokerDemoConnectorProbeResult(
        status=status,
        ready=ready,
        blocked_reasons=blocked,
        sanitized_output=sanitized_output,
        readiness_contract=contract,
        connector_status=connector_status,
        connector_result=connector_result,
    )


def evaluate_connector_object_for_demo(
    connector: Mapping[str, Any] | Callable[..., Any] | object,
) -> dict[str, Any]:
    metadata = _extract_connector_metadata(connector)
    blockers: list[str] = []

    if metadata.get("approved_for_demo") is not True:
        blockers.append("connector_not_approved_for_demo")

    metadata_mode = _normalize(metadata.get("connector_mode"))
    if metadata_mode and metadata_mode != _normalize(PROBE_CONNECTOR_MODE):
        blockers.append("connector_mode_invalid")

    if metadata.get("network_allowed") is not False:
        blockers.append("connector_network_not_disabled")

    if metadata.get("requires_order_route") is True:
        blockers.append("connector_order_route_capable")
    if metadata.get("account_state_requested") is True:
        blockers.append("connector_account_state_requested")
    if metadata.get("market_data_requested") is True:
        blockers.append("connector_market_data_requested")

    if _normalize(metadata.get("endpoint_url")).startswith("LIVE"):
        blockers.append("connector_endpoint_url_live")
    if _normalize(metadata.get("endpoint_mode")) not in {"DEMO", "PRACTICE_DEMO"}:
        if _normalize(metadata.get("endpoint_mode")):
            blockers.append("connector_endpoint_mode_invalid")

    if metadata.get("endpoint_classification") and _normalize(metadata.get("endpoint_classification")) not in ALLOWED_ENDPOINT_CLASSIFICATIONS:
        blockers.append("connector_endpoint_classification_invalid")

    connector_forbidden = _forbidden_field_paths(metadata)
    if connector_forbidden:
        blockers.append("connector_forbidden_field_detected")
        blockers.extend(f"connector_forbidden_field:{path}" for path in connector_forbidden)

    connector_forbidden_values = _forbidden_value_paths(metadata)
    if connector_forbidden_values:
        blockers.append("connector_forbidden_value_detected")
        blockers.extend(f"connector_forbidden_value:{path}" for path in connector_forbidden_values if path)

    if _is_no_order_contract(metadata):
        no_order_result = no_order_connector_contracts_g_v1.evaluate_no_order_connector(
            _build_no_order_contract_from_metadata(metadata)
        )
        if not no_order_result.ready:
            blockers.extend([f"no_order:{reason}" for reason in no_order_result.blocked_reasons])

    return {
        "schema": "AIOS_BROKER_DEMO_CONNECTOR_REVIEW_V2.v1",
        "approved_connector_present": True,
        "approved_for_demo": metadata.get("approved_for_demo", False) is True,
        "connector_mode": metadata.get("connector_mode"),
        "endpoint_mode": metadata.get("endpoint_mode"),
        "endpoint_classification": metadata.get("endpoint_classification"),
        "blocked_reason_count": len(blockers),
        "blockers": blockers,
        "blocked_reasons": blockers,
        "ready": not blockers,
        "network_allowed": bool(metadata.get("network_allowed", False)),
    }


def validate_account_envelope(
    account: Mapping[str, Any] | None = None,
) -> BrokerDemoConnectorProbeResult:
    account_payload = dict(account or {})
    blocked: list[str] = []
    if not account_payload:
        blocked.append("account_envelope_missing")

    if account_payload.get("account_id_present") is not False:
        if account_payload.get("account_id_present") is not None:
            blocked.append("account_id_present_forbidden")

    if account_payload.get("balance_placeholder") is None:
        blocked.append("balance_placeholder_required")
    if account_payload.get("equity_placeholder") is None:
        blocked.append("equity_placeholder_required")

    if _as_float(account_payload.get("balance_placeholder")) < 0:
        blocked.append("balance_placeholder_negative")
    if _as_float(account_payload.get("equity_placeholder")) < 0:
        blocked.append("equity_placeholder_negative")

    sanitized = _sanitize_output(account_payload)
    sanitized.pop("account_id", None)
    sanitized.pop("account_id_hash", None)

    blocked_reasons = tuple(_unique(blocked))
    status = BROKER_DEMO_PROBE_READY if not blocked_reasons else BROKER_DEMO_PROBE_BLOCKED
    return BrokerDemoConnectorProbeResult(
        status=status,
        ready=not blocked_reasons,
        blocked_reasons=blocked_reasons,
        sanitized_output=sanitized,
        readiness_contract=build_broker_demo_probe_contract(),
        connector_status="NO_CONNECTOR_CHECK",
        connector_result={},
    )


def validate_instrument_envelope(
    instrument: Mapping[str, Any] | None = None,
) -> BrokerDemoConnectorProbeResult:
    payload = dict(instrument or {})
    blocked: list[str] = []
    raw_symbol = str(payload.get("symbol", "")).strip()
    symbol = _normalize_symbol(raw_symbol)
    if not raw_symbol:
        blocked.append("instrument_symbol_required")
    elif symbol == "":
        blocked.append("instrument_symbol_invalid")
    elif symbol.endswith("_LIVE") or _normalize(raw_symbol).startswith("OANDA-LIVE"):
        blocked.append("instrument_live_symbol_forbidden")

    sanitized = dict(payload)
    if symbol:
        sanitized["symbol"] = symbol

    blocked_reasons = tuple(_unique(blocked))
    status = BROKER_DEMO_PROBE_READY if not blocked_reasons else BROKER_DEMO_PROBE_BLOCKED
    return BrokerDemoConnectorProbeResult(
        status=status,
        ready=not blocked_reasons,
        blocked_reasons=blocked_reasons,
        sanitized_output=sanitized,
        readiness_contract=build_broker_demo_probe_contract(),
        connector_status="NO_CONNECTOR_CHECK",
        connector_result={},
    )


def validate_quote_envelope(
    quote: Mapping[str, Any] | None = None,
) -> BrokerDemoConnectorProbeResult:
    payload = dict(quote or {})
    blocked: list[str] = []
    bid = _as_float(payload.get("bid"))
    ask = _as_float(payload.get("ask"))
    spread = _as_float(payload.get("spread"))
    endpoint = _normalize(payload.get("endpoint_classification"))

    if bid <= 0 or ask <= 0:
        blocked.append("quote_price_positive_required")
    if ask <= bid:
        blocked.append("quote_ask_must_exceed_bid")
    if spread <= 0:
        blocked.append("quote_spread_positive_required")
    if payload.get("timestamp_utc") is None:
        blocked.append("quote_timestamp_required")
    else:
        parsed = _parse_utc(payload["timestamp_utc"])
        if parsed is None:
            blocked.append("quote_timestamp_invalid")
        elif (datetime.now(timezone.utc) - parsed) > timedelta(seconds=STALE_QUOTE_WINDOW_SECONDS):
            blocked.append("quote_stale")

    if endpoint in {"LIVE", "PRODUCTION"}:
        blocked.append("quote_live_endpoint_forbidden")
    if endpoint and endpoint.startswith("LIVE"):
        blocked.append("quote_live_endpoint_forbidden")

    sanitized = _sanitize_output(payload)
    sanitized.pop("quote_id", None)
    sanitized.pop("raw_quote", None)
    sanitized.pop("raw_payload", None)

    blocked_reasons = tuple(_unique(blocked))
    status = BROKER_DEMO_PROBE_READY if not blocked_reasons else BROKER_DEMO_PROBE_BLOCKED
    return BrokerDemoConnectorProbeResult(
        status=status,
        ready=not blocked_reasons,
        blocked_reasons=blocked_reasons,
        sanitized_output=sanitized,
        readiness_contract=build_broker_demo_probe_contract(),
        connector_status="NO_CONNECTOR_CHECK",
        connector_result={},
    )


def summarize_broker_demo_probe_readiness(result: BrokerDemoConnectorProbeResult) -> dict[str, Any]:
    if result.status == BROKER_DEMO_PROBE_READY:
        ready = True
        status = BROKER_DEMO_PROBE_READY
    elif result.status == BROKER_DEMO_PROBE_CONNECTOR_REJECTED:
        ready = False
        status = BROKER_DEMO_PROBE_CONNECTOR_REJECTED
    else:
        ready = False
        status = BROKER_DEMO_PROBE_BLOCKED

    return {
        "schema": "AIOS_BROKER_DEMO_CONNECTOR_READINESS_SUMMARY_V2.v1",
        "status": status,
        "ready": ready,
        "blocked": not ready,
        "contract_ready": result.connector_status == "READY",
        "blocked_reasons": list(result.blocked_reasons),
        "no_live_trading": True,
        "network_calls_performed": result.sanitized_output.get("network_call_performed", False),
        "connection_attempt_performed": result.sanitized_output.get("connection_attempt_performed", False),
        "contains_private_data": bool(result.sanitized_output.get("contains_private_data", False)),
    }


def _as_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_bool(value: Any) -> bool:
    return bool(value)


def _normalize(value: Any) -> str:
    return str(value).strip().replace(" ", "_").upper() if value is not None else ""


def _normalize_symbol(value: Any) -> str:
    symbol = _normalize(value).replace("-", "_")
    return symbol.replace("/", "_")


def _parse_utc(raw: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _extract_connector_metadata(connector: Mapping[str, Any] | Callable[..., Any] | object) -> dict[str, Any]:
    if isinstance(connector, dict):
        return dict(connector)
    if hasattr(connector, "__dict__"):
        return {str(key): value for key, value in vars(connector).items()}
    return {"connector_object_type": type(connector).__name__}


def _is_no_order_contract(metadata: dict[str, Any]) -> bool:
    return metadata.get("connector_mode") == "NO_ORDER_CONNECTOR_CONTRACT"


def _build_no_order_contract_from_metadata(metadata: dict[str, Any]) -> no_order_connector_contracts_g_v1.NoOrderConnectorContract:
    return no_order_connector_contracts_g_v1.NoOrderConnectorContract(
        connector_id=str(metadata.get("connector_id", "UNKNOWN")),
        connector_mode=str(metadata.get("connector_mode", "")),
        endpoint_mode=str(metadata.get("endpoint_mode", no_order_connector_contracts_g_v1.EndpointMode.DEMO.value)),
        capabilities=tuple(metadata.get("capabilities", ())),
        kill_switch_state=str(metadata.get("kill_switch_state", no_order_connector_contracts_g_v1.KillSwitchState.CLEAR.value)),
        credential_boundary_clear=bool(metadata.get("credential_boundary_clear", True)),
        account_boundary_clear=bool(metadata.get("account_boundary_clear", True)),
        governance_status=str(metadata.get("governance_status", no_order_connector_contracts_g_v1.GovernanceStatus.APPROVED.value)),
        blocked_reasons=tuple(metadata.get("blocked_reasons", ())),
    )


def _forbidden_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if _normalize(key) in SENSITIVE_KEYS:
                paths.append(path)
            paths.extend(_forbidden_field_paths(nested, path))
    elif isinstance(value, list | tuple):
        for index, nested in enumerate(value):
            paths.extend(_forbidden_field_paths(nested, f"{prefix}[{index}]"))
    return _unique(paths)


def _forbidden_value_paths(value: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            hits.extend(_forbidden_value_paths(nested, path))
    elif isinstance(value, list | tuple):
        for index, nested in enumerate(value):
            hits.extend(_forbidden_value_paths(nested, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        sensitive_markers = (
            "bearer ",
            "basic ",
            "sec" + "ret",
            "tok" + "en=",
            "refresh_" + "tok" + "en",
            "pass" + "word",
            "api_" + "key",
            "-----" + "begin",
            "oan" + "da-",
        )
        if any(marker in lowered for marker in sensitive_markers):
            hits.append(prefix)
    return _unique(hits)


def _sanitize_output(payload: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = dict(payload)
    for sensitive in SENSITIVE_KEYS:
        sanitized.pop(sensitive, None)
    sanitized.pop("raw_endpoint", None)
    sanitized.pop("raw_endpoint_url", None)
    sanitized.pop("raw_account_response", None)
    sanitized.pop("raw_quote_response", None)
    sanitized["contains_private_data"] = False
    sanitized["contains_token"] = False
    sanitized["contains_secret"] = False
    sanitized["contains_account_identifier"] = False
    sanitized["network_call_performed"] = False
    sanitized["connection_attempt_performed"] = False
    if isinstance(payload, Mapping):
        if "raw_endpoint" in payload or "raw_account_response" in payload or "raw_quote_response" in payload:
            sanitized["contains_private_data"] = True
    return sanitized


def _unique(items: Sequence[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result


