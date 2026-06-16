from __future__ import annotations

from typing import Any

from automation.forex_engine import broker_paper_dryrun_replay_harness
from automation.forex_engine import schema_contracts as schemas


DRYRUN_REPLAY_EVIDENCE_READY = "DRYRUN_REPLAY_EVIDENCE_READY"
REPLAY_EVIDENCE_GATE_REPAIR_PACKET = "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-REPAIR-V1"
ADAPTER_PLAN_APPROVAL_GATE_PACKET = "PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1"
PACKET_ID = "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1"
ALLOWED_REPLAY_EVIDENCE_CLASSIFICATIONS = {"FAIL", "WATCHLIST", DRYRUN_REPLAY_EVIDENCE_READY}
FORBIDDEN_REPLAY_EVIDENCE_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def build_broker_paper_dryrun_replay_evidence_gate_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_EVIDENCE_GATE_CONTRACT.v1",
        "packet_id": PACKET_ID,
        "mode": "PAPER_ONLY_DRYRUN_REPLAY_EVIDENCE_GATE",
        "evidence_storage": "IN_MEMORY_ONLY",
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
        "replay_harness_required": True,
        "kill_switch_armed_required": True,
        "deterministic_evidence_required": True,
        "minimum_records_replayed": 2,
        "minimum_stub_accepted": 1,
        "minimum_stub_rejected": 1,
        "minimum_risk_accepted": 1,
        "minimum_risk_rejected": 1,
        "required_replay_harness_classification": (
            broker_paper_dryrun_replay_harness.DRYRUN_REPLAY_HARNESS_READY
        ),
        "source_modules_reused": [
            "automation.forex_engine.broker_paper_dryrun_replay_harness",
        ],
        "eom_milestone_alignment": {
            "milestone": "deterministic broker-paper dry-run replay evidence before adapter planning",
            "status": "evidence_gate_only",
            "supports_eom": True,
            "broker_integration_active": False,
            "broker_paper_orders_allowed": False,
            "live_ready": False,
        },
        "next_safe_packet_if_ready": ADAPTER_PLAN_APPROVAL_GATE_PACKET,
        "next_safe_packet_if_blocked": REPLAY_EVIDENCE_GATE_REPAIR_PACKET,
        "next_safe_action": (
            "Proceed only to PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1; "
            "broker SDKs, credentials, network/API, broker-paper orders, and live trading remain blocked."
        ),
    }
    schemas.assert_no_live_permissions(contract)
    return contract


def validate_replay_harness_evidence(
    replay_result: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_dryrun_replay_evidence_gate_contract())
    active_replay = dict(
        replay_result
        or broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    )
    replay_summary = broker_paper_dryrun_replay_harness.summarize_dryrun_replay_harness(
        active_replay
    )
    replay_harness_classification = str(
        active_replay.get("broker_paper_dryrun_replay_harness_classification")
        or active_replay.get("classification")
        or replay_summary.get("broker_paper_dryrun_replay_harness_classification")
        or replay_summary.get("classification")
        or "WATCHLIST"
    )
    result = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_EVIDENCE_GATE_RESULT.v1",
        "packet_id": PACKET_ID,
        "mode": active_contract["mode"],
        "evidence_storage": active_contract["evidence_storage"],
        "replay_harness_classification": replay_harness_classification,
        "broker_paper_dryrun_replay_harness_classification": replay_harness_classification,
        "records_replayed": int(replay_summary.get("records_replayed", 0)),
        "stub_accepted": int(replay_summary.get("stub_accepted", 0)),
        "stub_rejected": int(replay_summary.get("stub_rejected", 0)),
        "ledger_records": int(replay_summary.get("ledger_records", 0)),
        "risk_accepted": int(replay_summary.get("risk_accepted", 0)),
        "risk_rejected": int(replay_summary.get("risk_rejected", 0)),
        "aggregate_max_loss_usd": float(replay_summary.get("aggregate_max_loss_usd", 0.0)),
        "max_daily_loss_usd": float(replay_summary.get("max_daily_loss_usd", 5.0)),
        "kill_switch_armed": replay_summary.get("kill_switch_armed") is True,
        "all_unsafe_flags_false": (
            _all_unsafe_flags_false(active_replay) and _all_unsafe_flags_false(replay_summary)
        ),
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
        "replay_harness_summary": replay_summary,
        "source_modules_reused": list(active_contract["source_modules_reused"]),
        "eom_milestone_alignment": dict(active_contract["eom_milestone_alignment"]),
        "eom_milestone_status": "SUPPORTED_BY_DETERMINISTIC_LOCAL_REPLAY_EVIDENCE",
        "blockers": [],
        "contract": active_contract,
    }
    result["blockers"] = _evidence_blockers(result, active_contract)
    result["classification"] = classify_replay_evidence_gate(result)
    result["broker_paper_dryrun_replay_evidence_gate_classification"] = result["classification"]
    result["broker_paper_dryrun_replay_evidence_gate_ready"] = (
        result["classification"] == DRYRUN_REPLAY_EVIDENCE_READY
    )
    result["evidence_ready"] = result["broker_paper_dryrun_replay_evidence_gate_ready"]
    result["next_safe_packet"] = (
        ADAPTER_PLAN_APPROVAL_GATE_PACKET
        if result["broker_paper_dryrun_replay_evidence_gate_ready"]
        else REPLAY_EVIDENCE_GATE_REPAIR_PACKET
    )
    result["next_safe_action"] = _next_safe_action(result["classification"])
    schemas.assert_no_live_permissions(result)
    return result


def build_default_replay_evidence_gate_result() -> dict[str, Any]:
    return validate_replay_harness_evidence()


def summarize_replay_evidence_gate(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(result or build_default_replay_evidence_gate_result())
    summary = {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_EVIDENCE_GATE_SUMMARY.v1",
        "packet_id": PACKET_ID,
        "mode": str(payload.get("mode") or "PAPER_ONLY_DRYRUN_REPLAY_EVIDENCE_GATE"),
        "classification": str(payload.get("classification") or "WATCHLIST"),
        "broker_paper_dryrun_replay_evidence_gate_classification": str(
            payload.get("broker_paper_dryrun_replay_evidence_gate_classification")
            or payload.get("classification")
            or "WATCHLIST"
        ),
        "broker_paper_dryrun_replay_evidence_gate_ready": bool(
            payload.get("broker_paper_dryrun_replay_evidence_gate_ready", False)
        ),
        "evidence_ready": bool(payload.get("evidence_ready", False)),
        "evidence_storage": str(payload.get("evidence_storage") or "IN_MEMORY_ONLY"),
        "replay_harness_classification": str(
            payload.get("replay_harness_classification")
            or payload.get("broker_paper_dryrun_replay_harness_classification")
            or "WATCHLIST"
        ),
        "records_replayed": int(payload.get("records_replayed", 0)),
        "stub_accepted": int(payload.get("stub_accepted", 0)),
        "stub_rejected": int(payload.get("stub_rejected", 0)),
        "ledger_records": int(payload.get("ledger_records", 0)),
        "risk_accepted": int(payload.get("risk_accepted", 0)),
        "risk_rejected": int(payload.get("risk_rejected", 0)),
        "aggregate_max_loss_usd": float(payload.get("aggregate_max_loss_usd", 0.0)),
        "max_daily_loss_usd": float(payload.get("max_daily_loss_usd", 5.0)),
        "kill_switch_armed": payload.get("kill_switch_armed") is True,
        "all_unsafe_flags_false": payload.get("all_unsafe_flags_false") is True,
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
        "blockers": list(payload.get("blockers") or []),
        "eom_milestone_alignment": dict(payload.get("eom_milestone_alignment") or {}),
        "eom_milestone_status": str(
            payload.get("eom_milestone_status")
            or "SUPPORTED_BY_DETERMINISTIC_LOCAL_REPLAY_EVIDENCE"
        ),
        "next_safe_packet": str(payload.get("next_safe_packet") or REPLAY_EVIDENCE_GATE_REPAIR_PACKET),
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action("WATCHLIST")),
    }
    summary["classification"] = classify_replay_evidence_gate(summary)
    summary["broker_paper_dryrun_replay_evidence_gate_classification"] = summary["classification"]
    summary["broker_paper_dryrun_replay_evidence_gate_ready"] = (
        summary["classification"] == DRYRUN_REPLAY_EVIDENCE_READY
    )
    summary["evidence_ready"] = summary["broker_paper_dryrun_replay_evidence_gate_ready"]
    summary["next_safe_packet"] = (
        ADAPTER_PLAN_APPROVAL_GATE_PACKET
        if summary["broker_paper_dryrun_replay_evidence_gate_ready"]
        else REPLAY_EVIDENCE_GATE_REPAIR_PACKET
    )
    summary["next_safe_action"] = _next_safe_action(summary["classification"])
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_replay_evidence_gate(summary: dict[str, Any] | None = None) -> str:
    if summary is None:
        return classify_replay_evidence_gate(summarize_replay_evidence_gate())
    payload = dict(summary)
    candidate = str(
        payload.get("classification")
        or payload.get("broker_paper_dryrun_replay_evidence_gate_classification")
        or "WATCHLIST"
    )
    if candidate in FORBIDDEN_REPLAY_EVIDENCE_CLASSIFICATIONS:
        return "FAIL"
    if candidate not in ALLOWED_REPLAY_EVIDENCE_CLASSIFICATIONS:
        return "FAIL"
    if _has_forbidden_effect(payload) or payload.get("all_unsafe_flags_false") is False:
        return "FAIL"
    if list(payload.get("blockers") or _evidence_blockers(payload, {})):
        return "WATCHLIST"
    if _meets_ready_thresholds(payload):
        return DRYRUN_REPLAY_EVIDENCE_READY
    return "WATCHLIST"


def broker_paper_dryrun_replay_evidence_gate_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_DRYRUN_REPLAY_EVIDENCE_GATE_BOUNDARY.v1",
        "mode": "PAPER_ONLY_DRYRUN_REPLAY_EVIDENCE_GATE",
        "evidence_gate_only": True,
        "replay_harness_required": True,
        "local_simulation_only": True,
        "in_memory_only": True,
        "evidence_storage": "IN_MEMORY_ONLY",
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
        "kill_switch_armed_required": True,
        "deterministic_evidence_required": True,
        "next_safe_packet_if_ready": ADAPTER_PLAN_APPROVAL_GATE_PACKET,
        "next_safe_packet_if_blocked": REPLAY_EVIDENCE_GATE_REPAIR_PACKET,
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


def _all_unsafe_flags_false(replay_summary: dict[str, Any]) -> bool:
    if _has_forbidden_effect(replay_summary):
        return False
    return all(replay_summary.get(field, False) is False for field in _blocked_capability_fields())


def _evidence_blockers(
    payload: dict[str, Any],
    contract: dict[str, Any] | None,
) -> list[str]:
    active_contract = contract or {}
    blockers: list[str] = []
    if str(payload.get("evidence_storage") or "IN_MEMORY_ONLY") != "IN_MEMORY_ONLY":
        blockers.append("evidence_storage_must_be_in_memory_only")
    if (
        str(payload.get("replay_harness_classification") or "")
        != str(
            active_contract.get("required_replay_harness_classification")
            or broker_paper_dryrun_replay_harness.DRYRUN_REPLAY_HARNESS_READY
        )
    ):
        blockers.append("replay_harness_must_be_ready")
    if int(payload.get("records_replayed", 0)) < int(active_contract.get("minimum_records_replayed", 2)):
        blockers.append("minimum_replay_records_not_met")
    if int(payload.get("stub_accepted", 0)) < int(active_contract.get("minimum_stub_accepted", 1)):
        blockers.append("minimum_stub_accepted_not_met")
    if int(payload.get("stub_rejected", 0)) < int(active_contract.get("minimum_stub_rejected", 1)):
        blockers.append("minimum_stub_rejected_not_met")
    if int(payload.get("risk_accepted", 0)) < int(active_contract.get("minimum_risk_accepted", 1)):
        blockers.append("minimum_risk_accepted_not_met")
    if int(payload.get("risk_rejected", 0)) < int(active_contract.get("minimum_risk_rejected", 1)):
        blockers.append("minimum_risk_rejected_not_met")
    if float(payload.get("aggregate_max_loss_usd", 0.0)) > float(payload.get("max_daily_loss_usd", 5.0)):
        blockers.append("aggregate_max_loss_exceeds_daily_cap")
    if payload.get("kill_switch_armed") is not True:
        blockers.append("kill_switch_must_remain_armed")
    if _has_forbidden_effect(payload) or payload.get("all_unsafe_flags_false", True) is not True:
        blockers.append("unsafe_flag_detected")
    return _unique(blockers)


def _meets_ready_thresholds(payload: dict[str, Any]) -> bool:
    return (
        str(payload.get("replay_harness_classification") or "")
        == broker_paper_dryrun_replay_harness.DRYRUN_REPLAY_HARNESS_READY
        and int(payload.get("records_replayed", 0)) >= 2
        and int(payload.get("stub_accepted", 0)) >= 1
        and int(payload.get("stub_rejected", 0)) >= 1
        and int(payload.get("risk_accepted", 0)) >= 1
        and int(payload.get("risk_rejected", 0)) >= 1
        and float(payload.get("aggregate_max_loss_usd", 0.0)) <= float(payload.get("max_daily_loss_usd", 5.0))
        and payload.get("kill_switch_armed") is True
        and payload.get("all_unsafe_flags_false") is True
    )


def _next_safe_action(classification: str) -> str:
    if classification == DRYRUN_REPLAY_EVIDENCE_READY:
        return (
            "Proceed only to PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1; "
            "broker SDKs, credentials, network/API, broker-paper orders, and live trading remain blocked."
        )
    if classification == "FAIL":
        return "Repair replay evidence gate safety invariants before any adapter planning approval work."
    return "Repair replay evidence gate thresholds before any adapter planning approval work."


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
