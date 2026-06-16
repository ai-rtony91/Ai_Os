from __future__ import annotations

from typing import Any

from automation.forex_engine import broker_paper_adapter_stub_contract
from automation.forex_engine import schema_contracts as schemas


DRYRUN_LEDGER_READY = "DRYRUN_LEDGER_READY"
DRYRUN_LEDGER_REPAIR_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-REPAIR-V1"
DRYRUN_RISK_GOVERNOR_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1"
PACKET_ID = "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1"
ALLOWED_LEDGER_CLASSIFICATIONS = {"FAIL", "WATCHLIST", DRYRUN_LEDGER_READY}
FORBIDDEN_LEDGER_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def build_broker_paper_dryrun_intent_ledger_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_INTENT_LEDGER_CONTRACT.v1",
        "packet_id": PACKET_ID,
        "mode": "PAPER_ONLY_DRYRUN_INTENT_LEDGER",
        "ledger_storage": "IN_MEMORY_ONLY",
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
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
        "stub_contract_required": True,
        "kill_switch_required": True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "deterministic_record_required": True,
        "intent_schema": {
            "symbol": "fake/local symbol from the stub contract allowlist",
            "side": "buy or sell",
            "quantity_units": "positive local integer",
            "order_type": "market_stub or limit_stub",
            "max_loss_usd": "positive local number capped by the stub contract",
            "stop_loss_pips": "positive local number",
            "take_profit_pips": "optional positive local number",
            "dry_run": True,
            "approved_by_operator": True,
        },
        "stub_result_schema": {
            "adapter_mode": "STUB_ONLY",
            "accepted_for_simulation": "bool",
            "would_place_order": False,
            "order_placed": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "broker_paper_orders_allowed": False,
            "classification": "STUB_CONTRACT_READY or WATCHLIST",
        },
        "ledger_record_schema": {
            "record_id": "deterministic local id",
            "packet_id": PACKET_ID,
            "mode": "PAPER_ONLY_DRYRUN_INTENT_LEDGER",
            "symbol": "fake/local symbol",
            "side": "buy or sell",
            "quantity_units": "integer",
            "order_type": "market_stub or limit_stub",
            "max_loss_usd": "float",
            "stop_loss_pips": "float",
            "take_profit_pips": "float or none",
            "dry_run": True,
            "approved_by_operator": True,
            "accepted_for_simulation": "bool",
            "would_place_order": False,
            "order_placed": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "broker_paper_orders_allowed": False,
            "rejection_reasons": "list[str]",
            "audit_notes": "list[str]",
            "safety_flags": "dict[str, bool]",
        },
        "ledger_summary_schema": {
            "records_count": "int",
            "accepted_count": "int",
            "rejected_count": "int",
            "classification": "FAIL, WATCHLIST, or DRYRUN_LEDGER_READY",
            "next_safe_packet": DRYRUN_RISK_GOVERNOR_PACKET,
        },
        "rejection_reasons": [],
        "safety_invariants": broker_paper_dryrun_intent_ledger_boundary_summary(),
        "next_safe_packet_if_ready": DRYRUN_RISK_GOVERNOR_PACKET,
        "next_safe_packet_if_blocked": DRYRUN_LEDGER_REPAIR_PACKET,
        "next_safe_action": (
            "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1 after the "
            "in-memory dry-run ledger is ready; broker SDK, credentials, network, "
            "webhooks, paper orders, and live trading remain blocked."
        ),
    }
    schemas.assert_no_live_permissions(contract)
    return contract


def build_empty_dryrun_intent_ledger(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_dryrun_intent_ledger_contract())
    ledger = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_INTENT_LEDGER.v1",
        "packet_id": PACKET_ID,
        "mode": active_contract["mode"],
        "ledger_storage": active_contract["ledger_storage"],
        "contract": active_contract,
        "records": [],
        "records_count": 0,
        "accepted_count": 0,
        "rejected_count": 0,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "rejection_reasons": [],
        "blockers": ["no_dryrun_intent_records"] ,
        "classification": "WATCHLIST",
        "next_safe_packet": DRYRUN_LEDGER_REPAIR_PACKET,
        "next_safe_action": "Add local fake dry-run intent records; no disk writes, broker requests, or orders are allowed.",
    }
    schemas.assert_no_live_permissions(ledger)
    return ledger


def create_dryrun_intent_record(
    intent: dict[str, Any] | None = None,
    stub_result: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_dryrun_intent_ledger_contract())
    payload = dict(intent or {})
    normalized = _normalize_intent(payload)
    active_stub_result = dict(stub_result or broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(payload))
    rejection_reasons = _unique(
        [
            *_intent_rejection_reasons(normalized),
            *_stub_result_rejection_reasons(active_stub_result),
            *[str(reason) for reason in list(active_stub_result.get("rejection_reasons") or [])],
        ]
    )
    accepted = bool(active_stub_result.get("accepted_for_simulation", False)) and not rejection_reasons
    audit_notes = (
        [
            "local_stub_simulation_ingested",
            "dry_run_record_only",
            "no_order_placement",
            "no_broker_request",
            "in_memory_only",
        ]
        if accepted
        else ["rejected_before_any_broker_request", "in_memory_rejection_audit_only"]
    )
    record = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_INTENT_LEDGER_RECORD.v1",
        "record_id": _deterministic_record_id(normalized, accepted),
        "packet_id": PACKET_ID,
        "mode": active_contract["mode"],
        "symbol": normalized["symbol"],
        "side": normalized["side"],
        "quantity_units": normalized["quantity_units"],
        "order_type": normalized["order_type"],
        "max_loss_usd": normalized["max_loss_usd"],
        "stop_loss_pips": normalized["stop_loss_pips"],
        "take_profit_pips": normalized["take_profit_pips"],
        "dry_run": normalized["dry_run"],
        "approved_by_operator": normalized["approved_by_operator"],
        "accepted_for_simulation": accepted,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "broker_paper_orders_allowed": False,
        "rejection_reasons": rejection_reasons,
        "audit_notes": audit_notes,
        "safety_flags": _safety_flags(),
        "classification": DRYRUN_LEDGER_READY if accepted else "WATCHLIST",
        "next_safe_action": _record_next_safe_action(accepted),
    }
    record["classification"] = classify_dryrun_intent_ledger(record)
    schemas.assert_no_live_permissions(record)
    return record


def append_dryrun_intent_record(
    ledger: dict[str, Any] | None = None,
    record: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_dryrun_intent_ledger_contract())
    base_ledger = dict(ledger or build_empty_dryrun_intent_ledger(active_contract))
    records = [dict(item) for item in list(base_ledger.get("records") or []) if isinstance(item, dict)]
    active_record = dict(record or create_dryrun_intent_record(contract=active_contract))
    records.append(active_record)
    next_ledger = {
        **base_ledger,
        "schema": "AIOS_BROKER_PAPER_DRYRUN_INTENT_LEDGER.v1",
        "packet_id": PACKET_ID,
        "mode": active_contract["mode"],
        "ledger_storage": active_contract["ledger_storage"],
        "contract": active_contract,
        "records": records,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
    }
    summary = summarize_dryrun_intent_ledger(next_ledger)
    next_ledger.update(
        {
            "records_count": summary["records_count"],
            "accepted_count": summary["accepted_count"],
            "rejected_count": summary["rejected_count"],
            "rejection_reasons": summary["rejection_reasons"],
            "blockers": summary["blockers"],
            "classification": summary["classification"],
            "next_safe_packet": summary["next_safe_packet"],
            "next_safe_action": summary["next_safe_action"],
        }
    )
    schemas.assert_no_live_permissions(next_ledger)
    return next_ledger


def replay_dryrun_intent_batch(
    intents: list[dict[str, Any]] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_dryrun_intent_ledger_contract())
    batch = list(intents or _demo_intents())
    ledger = build_empty_dryrun_intent_ledger(active_contract)
    for intent in batch:
        record = create_dryrun_intent_record(intent, contract=active_contract)
        ledger = append_dryrun_intent_record(ledger, record, active_contract)
    schemas.assert_no_live_permissions(ledger)
    return ledger


def summarize_dryrun_intent_ledger(ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(ledger or {})
    records = [dict(item) for item in list(payload.get("records") or []) if isinstance(item, dict)]
    records_count = len(records) if records else int(payload.get("records_count", 0))
    accepted_count = (
        sum(1 for item in records if item.get("accepted_for_simulation") is True)
        if records
        else int(payload.get("accepted_count", payload.get("dryrun_ledger_accepted", 0)))
    )
    rejected_count = (
        records_count - accepted_count
        if records
        else int(payload.get("rejected_count", payload.get("dryrun_ledger_rejected", 0)))
    )
    rejection_reasons = _unique(
        [
            *[str(reason) for reason in list(payload.get("rejection_reasons") or [])],
            *[
                str(reason)
                for item in records
                for reason in list(dict(item).get("rejection_reasons") or [])
            ],
        ]
    )
    summary = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_INTENT_LEDGER_SUMMARY.v1",
        "packet_id": PACKET_ID,
        "mode": str(payload.get("mode") or "PAPER_ONLY_DRYRUN_INTENT_LEDGER"),
        "ledger_storage": str(payload.get("ledger_storage") or "IN_MEMORY_ONLY"),
        "records_count": records_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "dryrun_ledger_records": records_count,
        "dryrun_ledger_accepted": accepted_count,
        "dryrun_ledger_rejected": rejected_count,
        "broker_paper_dryrun_ledger_classification": "WATCHLIST",
        "broker_paper_dryrun_ledger_ready": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "rejection_reasons": rejection_reasons,
        "blockers": _ledger_blockers(records_count, accepted_count, records),
        "next_safe_packet": DRYRUN_LEDGER_REPAIR_PACKET,
        "next_safe_action": "Repair dry-run ledger records before risk-governor work; no broker request or order is allowed.",
    }
    summary["classification"] = classify_dryrun_intent_ledger(summary)
    summary["broker_paper_dryrun_ledger_classification"] = summary["classification"]
    summary["broker_paper_dryrun_ledger_ready"] = summary["classification"] == DRYRUN_LEDGER_READY
    summary["next_safe_packet"] = (
        DRYRUN_RISK_GOVERNOR_PACKET
        if summary["classification"] == DRYRUN_LEDGER_READY
        else DRYRUN_LEDGER_REPAIR_PACKET
    )
    summary["next_safe_action"] = _summary_next_safe_action(summary["classification"])
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_dryrun_intent_ledger(summary: dict[str, Any] | None = None) -> str:
    payload = dict(summary or {})
    candidate = str(payload.get("classification") or payload.get("broker_paper_dryrun_ledger_classification") or "WATCHLIST")
    if candidate in FORBIDDEN_LEDGER_CLASSIFICATIONS or candidate not in ALLOWED_LEDGER_CLASSIFICATIONS:
        return "FAIL"
    if candidate == "FAIL":
        return "FAIL"
    forbidden_false_fields = (
        "file_writes_allowed",
        "reports_writes_allowed",
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
    records = [dict(item) for item in list(payload.get("records") or []) if isinstance(item, dict)]
    if any(_record_has_forbidden_effect(item) for item in records):
        return "FAIL"
    if payload.get("accepted_for_simulation") is True and not list(payload.get("rejection_reasons") or []):
        return DRYRUN_LEDGER_READY
    accepted_count = int(payload.get("accepted_count", payload.get("dryrun_ledger_accepted", 0)))
    records_count = int(payload.get("records_count", payload.get("dryrun_ledger_records", 0)))
    if accepted_count > 0 and records_count >= accepted_count:
        return DRYRUN_LEDGER_READY
    return "WATCHLIST"


def broker_paper_dryrun_intent_ledger_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_INTENT_LEDGER_BOUNDARY.v1",
        "ledger_only": True,
        "local_simulation_only": True,
        "in_memory_only": True,
        "ledger_storage": "IN_MEMORY_ONLY",
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
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
        "next_safe_packet_if_ready": DRYRUN_RISK_GOVERNOR_PACKET,
    }


def _demo_intents() -> list[dict[str, Any]]:
    return [
        {
            "symbol": "EURUSD_FAKE",
            "side": "buy",
            "quantity_units": 1000,
            "order_type": "market_stub",
            "stop_loss_pips": 8.0,
            "take_profit_pips": 12.0,
            "max_loss_usd": 10.0,
            "dry_run": True,
            "approved_by_operator": True,
        },
        {
            "symbol": "EURUSD",
            "side": "hold",
            "quantity_units": 0,
            "order_type": "market",
            "max_loss_usd": 1000.0,
            "dry_run": False,
            "approved_by_operator": False,
        },
    ]


def _normalize_intent(intent: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": str(intent.get("symbol") or "").strip().upper(),
        "side": str(intent.get("side") or "").strip().lower(),
        "quantity_units": _int_or_none(intent.get("quantity_units")),
        "order_type": str(intent.get("order_type") or "").strip().lower(),
        "max_loss_usd": _float_or_none(intent.get("max_loss_usd")),
        "stop_loss_pips": _float_or_none(intent.get("stop_loss_pips")),
        "take_profit_pips": _float_or_none(intent.get("take_profit_pips")),
        "dry_run": bool(intent.get("dry_run", False)),
        "approved_by_operator": bool(intent.get("approved_by_operator", False)),
    }


def _intent_rejection_reasons(intent: dict[str, Any]) -> list[str]:
    stub_contract = broker_paper_adapter_stub_contract.build_broker_paper_adapter_stub_contract()
    return broker_paper_adapter_stub_contract.validate_broker_paper_stub_intent(intent, stub_contract)[
        "rejection_reasons"
    ]


def _stub_result_rejection_reasons(stub_result: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if stub_result.get("adapter_mode") != "STUB_ONLY":
        reasons.append("stub_result_must_be_local_stub_only")
    for field in (
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "broker_paper_orders_allowed",
    ):
        if stub_result.get(field) is not False:
            reasons.append(f"unsafe_stub_result:{field}")
    if str(stub_result.get("classification") or "") in FORBIDDEN_LEDGER_CLASSIFICATIONS:
        reasons.append("forbidden_stub_classification")
    return _unique(reasons)


def _ledger_blockers(records_count: int, accepted_count: int, records: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    if records_count <= 0:
        blockers.append("no_dryrun_intent_records")
    if accepted_count <= 0:
        blockers.append("no_accepted_fake_dryrun_intent")
    if any(_record_has_forbidden_effect(item) for item in records):
        blockers.append("forbidden_effect_detected")
    return _unique(blockers)


def _record_has_forbidden_effect(record: dict[str, Any]) -> bool:
    for field in (
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "broker_paper_orders_allowed",
    ):
        if record.get(field) is True:
            return True
    return False


def _safety_flags() -> dict[str, bool]:
    return {
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
    }


def _deterministic_record_id(intent: dict[str, Any], accepted: bool) -> str:
    quantity = str(intent.get("quantity_units") if intent.get("quantity_units") is not None else "none")
    max_loss = intent.get("max_loss_usd")
    max_loss_code = "none" if max_loss is None else str(int(round(float(max_loss) * 100)))
    verdict = "accepted" if accepted else "rejected"
    raw = f"DRYRUN-{intent.get('symbol')}-{intent.get('side')}-{intent.get('order_type')}-{quantity}-{max_loss_code}-{verdict}"
    return "".join(character if character.isalnum() or character in "-_" else "_" for character in raw)


def _record_next_safe_action(accepted: bool) -> str:
    if accepted:
        return "Retain the local dry-run audit record; no broker request or order placement is allowed."
    return "Keep the rejection audit and repair fake local intent fields before any future simulation."


def _summary_next_safe_action(classification: str) -> str:
    if classification == DRYRUN_LEDGER_READY:
        return (
            "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1; broker SDK, "
            "credentials, network, paper orders, and live trading remain blocked."
        )
    if classification == "FAIL":
        return "Repair dry-run ledger safety invariants before any risk-governor work."
    return "Add at least one accepted fake dry-run intent record while preserving rejection audits."


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


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
