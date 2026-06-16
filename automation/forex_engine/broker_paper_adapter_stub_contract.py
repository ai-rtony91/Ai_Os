from __future__ import annotations

from typing import Any

from automation.forex_engine import schema_contracts as schemas


STUB_CONTRACT_READY = "STUB_CONTRACT_READY"
STUB_REPAIR_PACKET = "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT-REPAIR-V1"
DRYRUN_INTENT_LEDGER_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1"
ALLOWED_STUB_CLASSIFICATIONS = {"FAIL", "WATCHLIST", STUB_CONTRACT_READY}
FORBIDDEN_STUB_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}
APPROVED_FAKE_SYMBOLS = ["EURUSD_FAKE", "GBPUSD_FAKE", "USDJPY_FAKE"]
APPROVED_SIDES = ["buy", "sell"]
APPROVED_ORDER_TYPES = ["market_stub", "limit_stub"]
MAX_LOSS_USD_CAP = 25.0


def build_broker_paper_adapter_stub_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_BROKER_PAPER_ADAPTER_STUB_CONTRACT.v1",
        "mode": "PAPER_ONLY_STUB_CONTRACT",
        "adapter_mode": "STUB_ONLY",
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "manual_approval_required": True,
        "presecurity_gate_required": True,
        "kill_switch_required": True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "max_loss_usd_cap": MAX_LOSS_USD_CAP,
        "approved_fake_symbols": list(APPROVED_FAKE_SYMBOLS),
        "approved_sides": list(APPROVED_SIDES),
        "approved_order_types": list(APPROVED_ORDER_TYPES),
        "intent_schema": {
            "symbol": "fake/local symbol from approved_fake_symbols",
            "side": "buy or sell",
            "quantity_units": "positive local integer",
            "order_type": "market_stub or limit_stub",
            "stop_loss_pips": "positive local number",
            "take_profit_pips": "optional positive local number",
            "max_loss_usd": f"positive local number <= {MAX_LOSS_USD_CAP}",
            "dry_run": True,
            "approved_by_operator": True,
        },
        "normalized_intent_schema": {
            "symbol": "uppercase fake symbol",
            "side": "lowercase side",
            "quantity_units": "integer units",
            "order_type": "lowercase stub order type",
            "stop_loss_pips": "float",
            "take_profit_pips": "float or none",
            "max_loss_usd": "float capped by contract",
            "dry_run": True,
            "approved_by_operator": True,
        },
        "rejection_reasons": [],
        "safety_invariants": broker_paper_stub_boundary_summary(),
        "next_safe_packet_if_ready": DRYRUN_INTENT_LEDGER_PACKET,
        "next_safe_packet_if_blocked": STUB_REPAIR_PACKET,
        "next_safe_action": (
            "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1; "
            "broker SDK, credentials, network, webhooks, broker-paper orders, and live trading remain blocked."
        ),
    }
    schemas.assert_no_live_permissions(contract)
    return contract


def validate_broker_paper_stub_intent(
    intent: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_adapter_stub_contract())
    payload = dict(intent or {})
    normalized = _normalize_intent(payload)
    rejection_reasons = _intent_rejection_reasons(normalized, active_contract)
    result = {
        "schema": "AIOS_BROKER_PAPER_STUB_INTENT_VALIDATION.v1",
        "mode": "PAPER_ONLY_STUB_CONTRACT",
        "accepted_for_simulation": not rejection_reasons,
        "normalized_intent": normalized,
        "rejection_reasons": rejection_reasons,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "broker_paper_orders_allowed": False,
        "classification": STUB_CONTRACT_READY if not rejection_reasons else "WATCHLIST",
        "next_safe_action": _next_safe_action(STUB_CONTRACT_READY if not rejection_reasons else "WATCHLIST"),
    }
    schemas.assert_no_live_permissions(result)
    return result


def simulate_broker_paper_stub_adapter(
    intent: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_adapter_stub_contract())
    validation = validate_broker_paper_stub_intent(intent, active_contract)
    accepted = bool(validation["accepted_for_simulation"])
    classification = STUB_CONTRACT_READY if accepted else "WATCHLIST"
    result = {
        "schema": "AIOS_BROKER_PAPER_STUB_ADAPTER_SIMULATION.v1",
        "mode": "PAPER_ONLY_STUB_CONTRACT",
        "adapter_mode": "STUB_ONLY",
        "accepted_for_simulation": accepted,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "broker_paper_orders_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "live_orders_allowed": False,
        "audit_record": {
            "audit_mode": "LOCAL_STUB_ONLY",
            "normalized_intent": validation["normalized_intent"],
            "decision": "simulated" if accepted else "rejected",
            "broker_request_sent": False,
            "order_placed": False,
        },
        "rejection_reasons": list(validation["rejection_reasons"]),
        "classification": classification,
        "next_safe_action": _next_safe_action(classification),
        "safety": broker_paper_stub_boundary_summary(),
    }
    result["classification"] = classify_broker_paper_stub_contract(result)
    schemas.assert_no_live_permissions(result)
    return result


def summarize_broker_paper_stub_contract(result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    classification = classify_broker_paper_stub_contract(payload)
    summary = {
        "schema": "AIOS_BROKER_PAPER_STUB_CONTRACT_SUMMARY.v1",
        "mode": str(payload.get("mode") or "PAPER_ONLY_STUB_CONTRACT"),
        "classification": classification,
        "broker_paper_stub_contract_classification": classification,
        "broker_paper_stub_contract_ready": classification == STUB_CONTRACT_READY,
        "adapter_mode": str(payload.get("adapter_mode") or "STUB_ONLY"),
        "accepted_for_simulation": bool(payload.get("accepted_for_simulation", False)),
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "live_ready": False,
        "rejection_reasons": list(payload.get("rejection_reasons") or []),
        "next_safe_packet": DRYRUN_INTENT_LEDGER_PACKET if classification == STUB_CONTRACT_READY else STUB_REPAIR_PACKET,
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action(classification)),
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_broker_paper_stub_contract(result: dict[str, Any]) -> str:
    payload = dict(result)
    candidate = str(payload.get("classification") or "WATCHLIST")
    if candidate in FORBIDDEN_STUB_CLASSIFICATIONS or candidate not in ALLOWED_STUB_CLASSIFICATIONS:
        return "FAIL"
    forbidden_false_fields = (
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
    )
    if any(payload.get(field) is not False for field in forbidden_false_fields if field in payload):
        return "FAIL"
    if list(payload.get("rejection_reasons") or []):
        return "WATCHLIST"
    return STUB_CONTRACT_READY


def broker_paper_stub_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_STUB_BOUNDARY.v1",
        "stub_contract_only": True,
        "local_simulation_only": True,
        "broker_integration_active": False,
        "broker_sdk_allowed": False,
        "network_allowed": False,
        "network_api_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "credentials_used": False,
        "credentials_required_now": False,
        "secrets_allowed": False,
        "env_reads_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "paper_order_execution": False,
        "live_orders_allowed": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "account_mutation": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "reports_written": False,
        "files_written": [],
        "next_safe_packet_if_ready": DRYRUN_INTENT_LEDGER_PACKET,
    }


def _normalize_intent(intent: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": str(intent.get("symbol") or "").strip().upper(),
        "side": str(intent.get("side") or "").strip().lower(),
        "quantity_units": _int_or_none(intent.get("quantity_units")),
        "order_type": str(intent.get("order_type") or "").strip().lower(),
        "stop_loss_pips": _float_or_none(intent.get("stop_loss_pips")),
        "take_profit_pips": _float_or_none(intent.get("take_profit_pips")),
        "max_loss_usd": _float_or_none(intent.get("max_loss_usd")),
        "dry_run": bool(intent.get("dry_run", False)),
        "approved_by_operator": bool(intent.get("approved_by_operator", False)),
    }


def _intent_rejection_reasons(intent: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if intent.get("dry_run") is not True:
        reasons.append("dry_run_required")
    if intent.get("approved_by_operator") is not True:
        reasons.append("operator_approval_required_for_future_execution")
    if intent.get("symbol") not in set(contract.get("approved_fake_symbols") or APPROVED_FAKE_SYMBOLS):
        reasons.append("symbol_not_in_fake_allowlist")
    if intent.get("side") not in set(contract.get("approved_sides") or APPROVED_SIDES):
        reasons.append("side_must_be_buy_or_sell")
    if intent.get("order_type") not in set(contract.get("approved_order_types") or APPROVED_ORDER_TYPES):
        reasons.append("order_type_must_be_stub_only")
    if not isinstance(intent.get("quantity_units"), int) or int(intent.get("quantity_units") or 0) <= 0:
        reasons.append("quantity_units_must_be_positive")
    if not _positive_number(intent.get("stop_loss_pips")):
        reasons.append("stop_loss_pips_required")
    if not _positive_number(intent.get("max_loss_usd")):
        reasons.append("max_loss_usd_required")
    elif float(intent["max_loss_usd"]) > float(contract.get("max_loss_usd_cap", MAX_LOSS_USD_CAP)):
        reasons.append("max_loss_usd_exceeds_contract_cap")
    return _unique(reasons)


def _next_safe_action(classification: str) -> str:
    if classification == STUB_CONTRACT_READY:
        return (
            "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1; "
            "broker SDK, credentials, network, webhooks, paper orders, and live trading remain blocked."
        )
    if classification == "FAIL":
        return "Repair stub contract safety invariants before dry-run intent ledger work."
    return "Fix rejected local stub intent fields; no broker request or order placement is allowed."


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and float(value) > 0.0


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
