from __future__ import annotations

from typing import Any

from automation.forex_engine import broker_paper_adapter_stub_contract
from automation.forex_engine import broker_paper_dryrun_intent_ledger
from automation.forex_engine import broker_paper_dryrun_risk_governor
from automation.forex_engine import broker_paper_presecurity_gate
from automation.forex_engine import schema_contracts as schemas


DRYRUN_REPLAY_HARNESS_READY = "DRYRUN_REPLAY_HARNESS_READY"
REPLAY_HARNESS_REPAIR_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-REPAIR-V1"
REPLAY_EVIDENCE_GATE_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1"
PACKET_ID = "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1"
ALLOWED_REPLAY_HARNESS_CLASSIFICATIONS = {"FAIL", "WATCHLIST", DRYRUN_REPLAY_HARNESS_READY}
FORBIDDEN_REPLAY_HARNESS_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def build_broker_paper_dryrun_replay_harness_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_HARNESS_CONTRACT.v1",
        "packet_id": PACKET_ID,
        "mode": "PAPER_ONLY_DRYRUN_REPLAY_HARNESS",
        "replay_storage": "IN_MEMORY_ONLY",
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
        "dryrun_ledger_required": True,
        "dryrun_risk_governor_required": True,
        "kill_switch_required": True,
        "kill_switch_armed": True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "deterministic_replay_required": True,
        "source_modules_reused": [
            "automation.forex_engine.broker_paper_presecurity_gate",
            "automation.forex_engine.broker_paper_adapter_stub_contract",
            "automation.forex_engine.broker_paper_dryrun_intent_ledger",
            "automation.forex_engine.broker_paper_dryrun_risk_governor",
        ],
        "replay_batch_schema": {
            "symbol": "fake/local symbol from the stub contract allowlist",
            "side": "buy or sell for accepted examples; invalid local values must be rejected",
            "quantity_units": "local integer",
            "order_type": "market_stub or limit_stub for accepted examples",
            "stop_loss_pips": "positive local number for accepted examples",
            "take_profit_pips": "optional positive local number",
            "max_loss_usd": "positive local number capped by the existing risk governor",
            "dry_run": True,
            "approved_by_operator": True,
        },
        "replay_result_schema": {
            "records_replayed": "int",
            "stub_accepted": "int",
            "stub_rejected": "int",
            "ledger_records": "int",
            "risk_accepted": "int",
            "risk_rejected": "int",
            "aggregate_max_loss_usd": "float",
            "max_daily_loss_usd": "float",
            "kill_switch_armed": True,
            "would_place_order": False,
            "order_placed": False,
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_ready": False,
            "broker_paper_orders_allowed": False,
        },
        "safety_invariants": broker_paper_dryrun_replay_harness_boundary_summary(),
        "next_safe_packet_if_ready": REPLAY_EVIDENCE_GATE_PACKET,
        "next_safe_packet_if_blocked": REPLAY_HARNESS_REPAIR_PACKET,
        "next_safe_action": (
            "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1; "
            "broker SDKs, credentials, network/API, broker-paper orders, and live trading remain blocked."
        ),
    }
    schemas.assert_no_live_permissions(contract)
    return contract


def build_default_replay_batch() -> list[dict[str, Any]]:
    return [
        {
            "symbol": "EURUSD_FAKE",
            "side": "buy",
            "quantity_units": 500,
            "order_type": "market_stub",
            "stop_loss_pips": 8.0,
            "take_profit_pips": 12.0,
            "max_loss_usd": 1.0,
            "dry_run": True,
            "approved_by_operator": True,
        },
        {
            "symbol": "EURUSD_FAKE",
            "side": "hold",
            "quantity_units": 0,
            "order_type": "market",
            "stop_loss_pips": None,
            "take_profit_pips": 12.0,
            "max_loss_usd": 30.0,
            "dry_run": True,
            "approved_by_operator": True,
        },
    ]


def replay_dryrun_batch_through_safety_stack(
    intents: list[dict[str, Any]] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_dryrun_replay_harness_contract())
    batch = [dict(item) for item in list(intents or build_default_replay_batch())]
    presecurity = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate()
    stub_contract = broker_paper_adapter_stub_contract.build_broker_paper_adapter_stub_contract()
    ledger_contract = broker_paper_dryrun_intent_ledger.build_broker_paper_dryrun_intent_ledger_contract()
    ledger = broker_paper_dryrun_intent_ledger.build_empty_dryrun_intent_ledger(ledger_contract)
    stub_results: list[dict[str, Any]] = []

    for intent in batch:
        stub_result = broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(
            intent,
            stub_contract,
        )
        record = broker_paper_dryrun_intent_ledger.create_dryrun_intent_record(
            intent,
            stub_result,
            ledger_contract,
        )
        ledger = broker_paper_dryrun_intent_ledger.append_dryrun_intent_record(
            ledger,
            record,
            ledger_contract,
        )
        stub_results.append(stub_result)

    ledger_summary = broker_paper_dryrun_intent_ledger.summarize_dryrun_intent_ledger(ledger)
    risk_result = broker_paper_dryrun_risk_governor.evaluate_dryrun_ledger_risk(ledger)
    risk_summary = broker_paper_dryrun_risk_governor.summarize_dryrun_risk_governor(risk_result)
    stub_accepted = sum(1 for item in stub_results if item.get("accepted_for_simulation") is True)
    stub_rejected = len(stub_results) - stub_accepted
    result = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_HARNESS_RESULT.v1",
        "packet_id": PACKET_ID,
        "mode": active_contract["mode"],
        "replay_storage": active_contract["replay_storage"],
        "presecurity_gate_classification": presecurity.get("classification", "WATCHLIST"),
        "source_modules_reused": list(active_contract["source_modules_reused"]),
        "records_replayed": len(batch),
        "stub_accepted": stub_accepted,
        "stub_rejected": stub_rejected,
        "stub_results": stub_results,
        "ledger_records": int(ledger_summary["records_count"]),
        "ledger": ledger,
        "risk_accepted": int(risk_summary["risk_accepted"]),
        "risk_rejected": int(risk_summary["risk_rejected"]),
        "risk_result": risk_result,
        "aggregate_max_loss_usd": float(risk_summary["aggregate_max_loss_usd"]),
        "max_daily_loss_usd": float(risk_summary["max_daily_loss_usd"]),
        "kill_switch_armed": risk_summary.get("kill_switch_armed") is True,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
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
        "live_ready": False,
        "live_trade_ready": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "safety_flags": _safety_flags(),
        "rejection_reasons": _unique(
            [
                *[
                    str(reason)
                    for item in stub_results
                    for reason in list(item.get("rejection_reasons") or [])
                ],
                *[str(reason) for reason in list(ledger_summary.get("rejection_reasons") or [])],
                *[str(reason) for reason in list(risk_summary.get("rejection_reasons") or [])],
            ]
        ),
        "blockers": [],
        "contract": active_contract,
    }
    result["blockers"] = _replay_blockers(result)
    result["classification"] = classify_dryrun_replay_harness(result)
    result["broker_paper_dryrun_replay_harness_classification"] = result["classification"]
    result["broker_paper_dryrun_replay_harness_ready"] = (
        result["classification"] == DRYRUN_REPLAY_HARNESS_READY
    )
    result["next_safe_packet"] = (
        REPLAY_EVIDENCE_GATE_PACKET
        if result["classification"] == DRYRUN_REPLAY_HARNESS_READY
        else REPLAY_HARNESS_REPAIR_PACKET
    )
    result["next_safe_action"] = _next_safe_action(result["classification"])
    schemas.assert_no_live_permissions(result)
    return result


def summarize_dryrun_replay_harness(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(result or replay_dryrun_batch_through_safety_stack())
    summary = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_HARNESS_SUMMARY.v1",
        "packet_id": PACKET_ID,
        "mode": str(payload.get("mode") or "PAPER_ONLY_DRYRUN_REPLAY_HARNESS"),
        "classification": str(payload.get("classification") or "WATCHLIST"),
        "broker_paper_dryrun_replay_harness_classification": str(
            payload.get("broker_paper_dryrun_replay_harness_classification")
            or payload.get("classification")
            or "WATCHLIST"
        ),
        "broker_paper_dryrun_replay_harness_ready": bool(
            payload.get("broker_paper_dryrun_replay_harness_ready", False)
        ),
        "replay_storage": str(payload.get("replay_storage") or "IN_MEMORY_ONLY"),
        "records_replayed": int(payload.get("records_replayed", 0)),
        "stub_accepted": int(payload.get("stub_accepted", 0)),
        "stub_rejected": int(payload.get("stub_rejected", 0)),
        "ledger_records": int(payload.get("ledger_records", 0)),
        "risk_accepted": int(payload.get("risk_accepted", 0)),
        "risk_rejected": int(payload.get("risk_rejected", 0)),
        "aggregate_max_loss_usd": float(payload.get("aggregate_max_loss_usd", 0.0)),
        "max_daily_loss_usd": float(payload.get("max_daily_loss_usd", 5.0)),
        "kill_switch_armed": payload.get("kill_switch_armed") is True,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
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
        "live_ready": False,
        "live_trade_ready": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "safety_flags": dict(payload.get("safety_flags") or _safety_flags()),
        "rejection_reasons": list(payload.get("rejection_reasons") or []),
        "blockers": list(payload.get("blockers") or []),
        "next_safe_packet": str(payload.get("next_safe_packet") or REPLAY_HARNESS_REPAIR_PACKET),
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action("WATCHLIST")),
    }
    summary["classification"] = classify_dryrun_replay_harness(summary)
    summary["broker_paper_dryrun_replay_harness_classification"] = summary["classification"]
    summary["broker_paper_dryrun_replay_harness_ready"] = (
        summary["classification"] == DRYRUN_REPLAY_HARNESS_READY
    )
    summary["next_safe_packet"] = (
        REPLAY_EVIDENCE_GATE_PACKET
        if summary["classification"] == DRYRUN_REPLAY_HARNESS_READY
        else REPLAY_HARNESS_REPAIR_PACKET
    )
    summary["next_safe_action"] = _next_safe_action(summary["classification"])
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_dryrun_replay_harness(summary: dict[str, Any] | None = None) -> str:
    payload = dict(summary or {})
    candidate = str(
        payload.get("classification")
        or payload.get("broker_paper_dryrun_replay_harness_classification")
        or "WATCHLIST"
    )
    if candidate in FORBIDDEN_REPLAY_HARNESS_CLASSIFICATIONS:
        return "FAIL"
    if candidate not in ALLOWED_REPLAY_HARNESS_CLASSIFICATIONS:
        return "FAIL"
    if _has_forbidden_effect(payload):
        return "FAIL"
    if list(payload.get("blockers") or _replay_blockers(payload)):
        return "WATCHLIST"
    if (
        int(payload.get("records_replayed", 0)) >= 2
        and int(payload.get("stub_accepted", 0)) >= 1
        and int(payload.get("stub_rejected", 0)) >= 1
        and int(payload.get("ledger_records", 0)) >= 2
        and int(payload.get("risk_accepted", 0)) >= 1
        and int(payload.get("risk_rejected", 0)) >= 1
    ):
        return DRYRUN_REPLAY_HARNESS_READY
    return "WATCHLIST"


def broker_paper_dryrun_replay_harness_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_HARNESS_BOUNDARY.v1",
        "mode": "PAPER_ONLY_DRYRUN_REPLAY_HARNESS",
        "replay_harness_only": True,
        "local_simulation_only": True,
        "in_memory_only": True,
        "replay_storage": "IN_MEMORY_ONLY",
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
        "manual_approval_required": True,
        "presecurity_gate_required": True,
        "stub_contract_required": True,
        "dryrun_ledger_required": True,
        "dryrun_risk_governor_required": True,
        "kill_switch_required": True,
        "kill_switch_armed": True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "deterministic_replay_required": True,
        "next_safe_packet_if_ready": REPLAY_EVIDENCE_GATE_PACKET,
    }


def _safety_flags() -> dict[str, Any]:
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
        "live_trade_ready": False,
        "kill_switch_armed": True,
    }


def _blocked_capability_fields() -> tuple[str, ...]:
    return (
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
        "live_trade_ready",
    )


def _has_forbidden_effect(payload: dict[str, Any]) -> bool:
    if any(payload.get(field) is True for field in _blocked_capability_fields()):
        return True
    for flags in (payload.get("safety_flags"), payload.get("safety")):
        if isinstance(flags, dict) and any(flags.get(field) is True for field in _blocked_capability_fields()):
            return True
    return False


def _replay_blockers(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if str(payload.get("replay_storage") or "IN_MEMORY_ONLY") != "IN_MEMORY_ONLY":
        blockers.append("replay_storage_must_be_in_memory_only")
    if int(payload.get("records_replayed", 0)) <= 0:
        blockers.append("no_replay_records")
    if int(payload.get("stub_accepted", 0)) <= 0:
        blockers.append("no_stub_accepted_fake_intent")
    if int(payload.get("stub_rejected", 0)) <= 0:
        blockers.append("no_stub_rejected_fake_intent")
    if int(payload.get("ledger_records", 0)) <= 0:
        blockers.append("no_ledger_records")
    if int(payload.get("risk_accepted", 0)) <= 0:
        blockers.append("no_risk_accepted_record")
    if int(payload.get("risk_rejected", 0)) <= 0:
        blockers.append("no_risk_rejected_record")
    if float(payload.get("aggregate_max_loss_usd", 0.0)) > float(payload.get("max_daily_loss_usd", 5.0)):
        blockers.append("aggregate_max_loss_exceeds_daily_cap")
    if payload.get("kill_switch_armed") is not True:
        blockers.append("kill_switch_must_remain_armed")
    if _has_forbidden_effect(payload):
        blockers.append("forbidden_effect_detected")
    return _unique(blockers)


def _next_safe_action(classification: str) -> str:
    if classification == DRYRUN_REPLAY_HARNESS_READY:
        return (
            "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1; "
            "broker-paper orders, broker SDKs, credentials, network/API, and live trading remain blocked."
        )
    if classification == "FAIL":
        return "Repair replay harness safety invariants before any evidence-gate work."
    return "Repair replay harness accepted/rejected dry-run coverage before evidence-gate work."


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
