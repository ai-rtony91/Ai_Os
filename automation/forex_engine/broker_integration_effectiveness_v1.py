"""AIOS Broker Integration Effectiveness V1.

Provides deterministic local validation for paper-demo broker integration
readiness, including:
- broker adapter contract checks,
- dry-run envelope validation,
- paper trade candidate -> broker-safe dry-run intent mapping,
- contract-level latency bucket definitions for benchmarking.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from automation.forex_engine import (
    broker_bridge_runtime_validator_h_v1,
    broker_specific_paper_demo,
    no_order_connector_contracts_g_v1,
    schema_contracts as schemas,
)

BROKER_DEMO_BLOCKED = "BROKER_DEMO_BLOCKED"
BROKER_DEMO_DRYRUN_READY = "BROKER_DEMO_DRYRUN_READY"
BROKER_DEMO_CONNECTOR_REJECTED = "BROKER_DEMO_CONNECTOR_REJECTED"
BROKER_DEMO_CONTRACT_INVALID = "BROKER_DEMO_CONTRACT_INVALID"
BROKER_DEMO_STATUS_READY = "BROKER_DEMO_STATUS_READY"
BROKER_DEMO_STATUS_REVIEW = "BROKER_DEMO_STATUS_REVIEW"
BROKER_DEMO_STATUS_REJECTED = "BROKER_DEMO_STATUS_REJECTED"

FORBIDDEN_ENVELOPE_FIELDS = {
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
    "raw_response",
}


@dataclass(frozen=True)
class BrokerIntegrationEnvelopeEvaluation:
    status: str
    ready: bool
    blocked_reasons: tuple[str, ...]
    sanitized_payload: dict[str, Any]
    runtime_evaluation: dict[str, Any]
    connector_status: str


def build_broker_integration_effectiveness_contract() -> dict[str, Any]:
    """Return the canonical broker-integration effectiveness contract."""
    contract = {
        "schema": "AIOS_BROKER_INTEGRATION_EFFECTIVENESS_V1_CONTRACT.v1",
        "adapter_id": "AIOS_OANDA_PAPER_DEMO_ADAPTER",
        "adapter_mode": "DEMO_DRYRUN",
        "required_approvals": [
            "human_owner_approved",
            "protected_connector_gate_ready",
            "runtime_connector_ready",
            "connector_contract_ready",
            "kill_switch_clear",
            "daily_stop_clear",
            "max_loss_gate_ready",
        ],
        "required_envelope_fields": [
            "instrument",
            "side",
            "units_or_notional",
            "risk_cap_usd",
            "stop_loss",
            "take_profit",
            "kill_switch_active",
            "max_loss_usd",
            "daily_stop_hit",
            "human_approval_required",
            "simulation_only",
            "broker_demo_only",
            "dry_run_connector_id",
        ],
        "forbidden_live_flags": [
            "broker_sdk_allowed",
            "network_api_allowed",
            "credentials_used",
            "broker_request_sent",
            "order_route_requested",
            "account_state_requested",
            "market_data_requested",
            "order_placed",
            "live_execution_allowed",
            "live_ready",
            "live_order",
        ],
        "allowed_endpoint_classification": ["DEMO", "PRACTICE_DEMO"],
        "retry_loops_allowed": False,
        "connector_call_limit": 0,
        "max_attempts": 1,
        "broker_connection_active": False,
        "broker_demo_readiness_status": BROKER_DEMO_DRYRUN_READY,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "live_execution_allowed": False,
        "live_account_access_allowed": False,
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


def check_broker_demo_contract(
    *,
    broker_adapter_contract: Mapping[str, Any] | None = None,
    broker_specific_config: broker_specific_paper_demo.BrokerSpecificPaperDemoConfig
    | Mapping[str, Any]
    | None = None,
) -> BrokerIntegrationEnvelopeEvaluation:
    """Validate adapter and broker-specific paper-demo contracts."""
    blocked: list[str] = []

    adapter_result = broker_specific_paper_demo.validate_broker_specific_paper_demo_config(
        broker_specific_config
    )
    if not adapter_result["config_valid"]:
        blocked.extend(list(adapter_result["blockers"]))

    bridge_contract = build_broker_integration_effectiveness_contract()
    if (broker_adapter_contract or {}).get("adapter_mode") != bridge_contract["adapter_mode"]:
        blocked.append("adapter_mode_invalid")
    if (broker_adapter_contract or {}).get("live_ready") is not False:
        blocked.append("adapter_live_ready_not_false")
    if (broker_adapter_contract or {}).get("broker_sdk_allowed", False) is not False:
        blocked.append("adapter_broker_sdk_allowed_must_be_false")
    if (broker_adapter_contract or {}).get("network_api_allowed", False) is not False:
        blocked.append("adapter_network_api_allowed_must_be_false")

    ready = not blocked
    status = BROKER_DEMO_DRYRUN_READY if ready else BROKER_DEMO_CONTRACT_INVALID
    return BrokerIntegrationEnvelopeEvaluation(
        status=status,
        ready=ready,
        blocked_reasons=tuple(blocked),
        sanitized_payload={
            "adapter_validation_status": adapter_result["status"],
            "adapter_contract_ready": adapter_result["config_valid"],
            "adapter_mode": "DEMO_DRYRUN",
            "live_capability": False,
            "broker_request_allowed": False,
        },
        runtime_evaluation={
            "broker_specific_config": adapter_result,
            "broker_bridge_contract": bridge_contract,
        },
        connector_status="BROKER_INTEGRATION_CONTRACT_CHECK_COMPLETED",
    )


def _forbidden_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = key_text.strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_ENVELOPE_FIELDS:
                paths.append(path)
            paths.extend(_forbidden_field_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_forbidden_field_paths(nested, f"{prefix}[{index}]"))
    return _unique(paths)


def _as_bool(value: Any) -> bool:
    return bool(value)


def _as_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any) -> int:
    try:
        if value is None:
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def _unique(items: Sequence[str]) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen


def validate_broker_demo_envelope(
    *,
    envelope: Mapping[str, Any] | None,
    no_order_connector: no_order_connector_contracts_g_v1.NoOrderConnectorContract | None = None,
) -> BrokerIntegrationEnvelopeEvaluation:
    """Validate a broker-demo request envelope and classify the gate result."""
    payload = dict(envelope or {})
    blocked: list[str] = []

    for key in _forbidden_field_paths(payload):
        blocked.append(f"forbidden_field:{key}")

    if payload.get("human_approval_required") is not True:
        blocked.append("human_owner_approval_required")
    if payload.get("simulation_only") is not True:
        blocked.append("simulation_only_required")
    if payload.get("broker_demo_only") is not True:
        blocked.append("broker_demo_only_required")
    if payload.get("kill_switch_active") is not False:
        blocked.append("kill_switch_active")
    if payload.get("max_loss_usd") in (None, 0, ""):
        blocked.append("risk_cap_missing")
    if payload.get("daily_stop_hit") is not False:
        blocked.append("daily_stop_hit")
    if payload.get("max_attempts") not in (None, 1):
        blocked.append("max_attempts_must_equal_one")
    if payload.get("retry_loop_enabled", False):
        blocked.append("retry_loop_blocked")
    if payload.get("order_route_requested") is True:
        blocked.append("order_route_attempt_blocked")
    if payload.get("account_state_requested") is True:
        blocked.append("account_state_request_blocked")
    if payload.get("market_data_requested") is True:
        blocked.append("market_data_request_blocked")
    if payload.get("endpoint_mode") not in {"DEMO", "PRACTICE_DEMO"}:
        blocked.append("unsupported_endpoint_classification")

    if no_order_connector is None:
        blocked.append("runtime_connector_required")
        connector_state = "MISSING"
    else:
        connector_eval = no_order_connector_contracts_g_v1.evaluate_no_order_connector(no_order_connector)
        blocked.extend(connector_eval.blocked_reasons)
        connector_state = (
            "READY" if connector_eval.ready else "REJECTED"
        )

    for key in (
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_used",
        "broker_request_sent",
        "order_placed",
        "live_execution_allowed",
        "network_used",
    ):
        if payload.get(key) is True:
            blocked.append(f"privileged_flag:{key}")

    blocked_reasons = tuple(_unique(blocked))
    runtime_eval = {
        "connector_status": connector_state,
        "dry_run_only": True,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    broker_bridge = broker_bridge_runtime_validator_h_v1.validate_broker_bridge_runtime(
        endpoint_mode=payload.get("endpoint_mode") or "DEMO",
        credential_metadata=payload.get("credential_metadata"),
        account_metadata=payload.get("account_metadata"),
        governance_approved=_as_bool(payload.get("human_approval_required")),
        kill_switch_active=_as_bool(payload.get("kill_switch_active")),
        no_order_connector=no_order_connector
        or no_order_connector_contracts_g_v1.build_demo_no_order_contract("default-broker-demo-connector"),
    )
    runtime_eval["bridge_ready"] = broker_bridge.ready
    runtime_eval["bridge_blocked_reasons"] = list(broker_bridge.blocked_reasons)

    if blocked_reasons:
        status = (
            BROKER_DEMO_CONNECTOR_REJECTED
            if ("runtime_connector_required" in blocked_reasons or "REJECTED" in blocked_reasons)
            else BROKER_DEMO_BLOCKED
        )
        ready = False
    else:
        status = BROKER_DEMO_DRYRUN_READY
        ready = True

    runtime_eval["status"] = status
    runtime_eval["ready"] = ready

    return BrokerIntegrationEnvelopeEvaluation(
        status=status,
        ready=ready,
        blocked_reasons=blocked_reasons,
        sanitized_payload=_sanitize_envelope(payload),
        runtime_evaluation=runtime_eval,
        connector_status=connector_state,
    )


def map_paper_trade_candidate_to_broker_dryrun_intent(
    candidate: Mapping[str, Any] | None,
    *,
    risk_cap_usd: float,
    max_loss_usd: float,
    kill_switch_active: bool,
    daily_stop_hit: bool,
    human_approval_required: bool,
    dry_run_connector_id: str = "AIOS-DRY-RUN-CONNECTOR",
) -> dict[str, Any]:
    """Convert an internal paper candidate into a broker-safe dry-run envelope."""
    payload = dict(candidate or {})
    raw_symbol = str(payload.get("symbol") or payload.get("instrument") or "")
    instrument = raw_symbol.replace("-", "_").replace("/", "_").upper() if raw_symbol else "EUR_USD"

    stop_loss = _as_float(payload.get("stop_loss") or payload.get("stop_loss_price"))
    take_profit = _as_float(payload.get("take_profit") or payload.get("take_profit_price"))
    side = str(payload.get("side") or payload.get("direction") or "BUY").upper()
    if side not in {"BUY", "SELL"}:
        side = "BUY"
    units_or_notional = _as_int(payload.get("units") or payload.get("qty") or payload.get("volume"))
    if units_or_notional <= 0:
        units_or_notional = 1

    result = {
        "schema": "AIOS_BROKER_DEMO_DRYRUN_INTENT_ENVELOPE.v1",
        "instrument": instrument,
        "side": side,
        "units_or_notional": units_or_notional,
        "risk_cap_usd": _as_float(risk_cap_usd),
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "kill_switch_active": bool(kill_switch_active),
        "max_loss_usd": _as_float(max_loss_usd),
        "daily_stop_hit": bool(daily_stop_hit),
        "human_approval_required": bool(human_approval_required),
        "simulation_only": True,
        "broker_demo_only": True,
        "dry_run_connector_id": str(dry_run_connector_id),
        "endpoint_mode": "PRACTICE_DEMO",
        "max_attempts": 1,
        "retry_loop_enabled": False,
        "order_route_requested": False,
        "account_state_requested": False,
        "market_data_requested": False,
        "credential_metadata": {},
        "account_metadata": {},
        "live_order": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "live_execution_allowed": False,
        "live_ready": False,
        "real_order_ready": False,
    }
    return result


def _sanitize_envelope(payload: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    defaults = {
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_used": False,
        "broker_request_sent": False,
        "order_placed": False,
        "network_used": False,
        "live_execution_allowed": False,
        "live_ready": False,
        "would_place_order": False,
        "live_order": False,
        "simulation_only": False,
        "broker_demo_only": False,
    }
    sanitized.update(defaults)
    for key, value in payload.items():
        if key in FORBIDDEN_ENVELOPE_FIELDS:
            continue
        if key in {"credential_metadata", "account_metadata"}:
            continue
        sanitized[key] = value
    for key, value in defaults.items():
        if key not in sanitized:
            sanitized[key] = value
    return sanitized


def build_broker_integration_latency_budget(
    *,
    target_ms: dict[str, int] | None = None,
) -> dict[str, Any]:
    budgets = {
        "state_snapshot_read_ms": 8,
        "signal_candidate_read_ms": 6,
        "risk_gate_ms": 5,
        "kill_switch_gate_ms": 3,
        "broker_envelope_build_ms": 4,
        "connector_call_placeholder_ms": 0,
        "broker_response_placeholder_ms": 0,
    }
    if target_ms:
        for key, value in target_ms.items():
            if key in budgets and isinstance(value, int) and value > 0:
                budgets[key] = value
    report = {
        "schema": "AIOS_BROKER_INTEGRATION_LATENCY_BUDGET_V1_REPORT.v1",
        "status": BROKER_DEMO_STATUS_READY,
        "dashboards": {
            "dashboard_click_short_circuit": "dashboard click path must not invoke any connector logic",
            "cached_state_read": True,
            "manual_approval_gate_required": True,
        },
        "gates": {
            "state_snapshot_read_ms": {
                "budget": budgets["state_snapshot_read_ms"],
                "target": "contracted",
            },
            "signal_candidate_read_ms": {
                "budget": budgets["signal_candidate_read_ms"],
                "target": "contracted",
            },
            "risk_gate_ms": {
                "budget": budgets["risk_gate_ms"],
                "target": "contracted",
            },
            "kill_switch_gate_ms": {
                "budget": budgets["kill_switch_gate_ms"],
                "target": "contracted",
            },
            "broker_envelope_build_ms": {
                "budget": budgets["broker_envelope_build_ms"],
                "target": "contracted",
            },
            "connector_call_placeholder_ms": {
                "budget": budgets["connector_call_placeholder_ms"],
                "target": "placeholder",
            },
            "broker_response_placeholder_ms": {
                "budget": budgets["broker_response_placeholder_ms"],
                "target": "placeholder",
            },
        },
        "total_budget_ms": sum(budgets.values()),
        "contracted_but_offline_by_default": True,
        "broker_call_by_default": False,
    }
    return report


def summarize_broker_integration_effectiveness(
    *,
    contract_eval: BrokerIntegrationEnvelopeEvaluation | None = None,
    envelope_eval: BrokerIntegrationEnvelopeEvaluation | None = None,
) -> dict[str, Any]:
    contract_status = contract_eval.status if contract_eval else BROKER_DEMO_CONTRACT_INVALID
    envelope_status = envelope_eval.status if envelope_eval else BROKER_DEMO_BLOCKED
    blocked = []
    if not (contract_eval and contract_eval.ready):
        blocked.append("contract_check_required")
    if not (envelope_eval and envelope_eval.ready):
        blocked.append("demo_envelope_blocked")
    ready = not blocked
    status = BROKER_DEMO_DRYRUN_READY if ready else BROKER_DEMO_BLOCKED
    return {
        "schema": "AIOS_BROKER_INTEGRATION_EFFECTIVENESS_SUMMARY_V1.v1",
        "status": status,
        "ready": ready,
        "contract_status": contract_status,
        "envelope_status": envelope_status,
        "blocked_reasons": blocked,
        "blocked_demo_ready": not ready,
        "no_live_or_network_action": True,
        "dry_run_connector_required": True,
    }
