"""Deterministic paper risk decision router for Forex Engine v1."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from automation.forex_engine.readiness import PAPER_READY

PAPER_DECISION_SCHEMA = "forex_paper_risk_decision_v1"
PAPER_ACCEPT = "PAPER_ACCEPT"
PAPER_REJECT = "PAPER_REJECT"

REQUIRED_LEDGERS_FOR_PAPER_DECISION = (
    "readiness_status",
    "accepted_for_paper",
    "execution_allowed",
    "safety",
)

SAFETY_BLOCK_FLAGS = (
    "no_live_trading",
    "no_broker_apis",
    "no_oanda",
    "no_webhooks",
    "no_real_market_data",
    "no_real_orders",
    "no_api_keys_or_secrets",
    "no_network",
    "no_scheduler_or_daemon",
    "no_worker_launch",
)

REQUIRED_BLOCKED_ACTIONS = (
    "broker_api_call",
    "oanda_api_call",
    "real_order_submission",
    "webhook_execution",
    "secret_or_api_key_load",
)

NEXT_SAFE_ACCEPT_ACTION = (
    "Route to the paper continuity/review step and proceed with supervised next-stage build."
)
NEXT_SAFE_REJECT_ACTION = (
    "Rework the ledger record to remove unsafe fields and blockers, then rerun intake + router."
)


def evaluate_ledger_for_paper_risk_decision(
    ledger_record: Mapping[str, Any],
    *,
    generated_at_utc: str | None = None,
    decision_id: str | None = None,
) -> dict[str, Any]:
    """Evaluate a paper intake ledger record and return a formal paper risk decision."""
    if not isinstance(ledger_record, Mapping):
        raise TypeError("ledger_record must be a mapping.")

    record = dict(ledger_record)

    source_record_id = str(
        record.get("source_ledger_record_id") or record.get("ledger_record_id", "")
    ).strip()
    signal_id = str(record.get("signal_id", "")).strip()

    readiness_status = str(record.get("readiness_status", "")).strip()
    accepted_for_paper = bool(record.get("accepted_for_paper", False))
    execution_allowed = bool(record.get("execution_allowed", True))
    risk_flags = list(_ensure_list(record.get("risk_flags"), "risk_flags", []))
    blocked_actions = list(_ensure_list(record.get("blocked_actions"), "blocked_actions", []))

    reject_reasons: list[str] = []

    safety = record.get("safety")
    if isinstance(safety, Mapping):
        safety_map = dict(safety)
    else:
        safety_map = {}
        reject_reasons.append("Missing or invalid safety map.")

    for required_key in REQUIRED_LEDGERS_FOR_PAPER_DECISION:
        if required_key not in record:
            reject_reasons.append(f"Missing required ledger field: {required_key}.")

    safety_failures = [key for key in SAFETY_BLOCK_FLAGS if not bool(safety_map.get(key))]
    if safety_failures:
        reject_reasons.append(
            f"Safety blocks not fully satisfied: {', '.join(safety_failures)}."
        )

    if readiness_status != PAPER_READY:
        reject_reasons.append("readiness_status is not PAPER_READY.")

    if not accepted_for_paper:
        reject_reasons.append("accepted_for_paper is false.")

    if execution_allowed:
        reject_reasons.append("execution_allowed must be false for paper-only routing.")

    if risk_flags:
        reject_reasons.append("Risk flags are present and block paper routing.")

    output_blocked_actions = _merge_blocked_actions(blocked_actions)
    required_blocks_present = set(REQUIRED_BLOCKED_ACTIONS).issubset(
        set(output_blocked_actions)
    )
    if not required_blocks_present:
        reject_reasons.append("required blocked actions are not present.")

    if not source_record_id:
        reject_reasons.append("Missing source_ledger_record_id.")

    if not signal_id:
        reject_reasons.append("Missing signal_id.")

    can_accept = (
        len(reject_reasons) == 0
        and readiness_status == PAPER_READY
        and accepted_for_paper is True
        and execution_allowed is False
        and risk_flags == []
        and source_record_id != ""
        and signal_id != ""
        and required_blocks_present
        and all(bool(safety_map.get(flag, False)) for flag in SAFETY_BLOCK_FLAGS)
    )

    if can_accept:
        decision = PAPER_ACCEPT
        accept_for_output = True
        reasons = ["Ledger is safe and ready for paper risk acceptance."]
        next_safe_action = NEXT_SAFE_ACCEPT_ACTION
    else:
        decision = PAPER_REJECT
        accept_for_output = False
        reasons = list(reject_reasons) if reject_reasons else ["Deterministic paper router rejection."]
        next_safe_action = NEXT_SAFE_REJECT_ACTION

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    if decision_id is None:
        decision_id = _build_decision_id(
            generated_at_utc,
            source_record_id,
            signal_id,
            readiness_status,
            decision,
        )

    return {
        "schema": PAPER_DECISION_SCHEMA,
        "mode": "PAPER_ONLY",
        "decision_id": decision_id,
        "source_ledger_record_id": source_record_id,
        "signal_id": signal_id,
        "generated_at_utc": generated_at_utc,
        "readiness_status": readiness_status,
        "decision": decision,
        "accepted_for_paper": accept_for_output,
        "execution_allowed": False,
        "reason": reasons[0],
        "reasons": reasons,
        "risk_flags": risk_flags,
        "blocked_actions": output_blocked_actions,
        "safety": safety_map,
        "next_safe_action": next_safe_action,
    }


def _ensure_list(value: Any, field_name: str, reasons: list[str]) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        if isinstance(reasons, list):
            reasons.append(f"{field_name} must be a list.")
        return []
    return list(value)


def _merge_blocked_actions(blocked_actions: list[Any]) -> list[str]:
    merged = [
        item for item in list(blocked_actions) + list(REQUIRED_BLOCKED_ACTIONS) if isinstance(item, str)
    ]
    return list(dict.fromkeys(merged))


def _build_decision_id(
    generated_at_utc: str,
    source_record_id: str,
    signal_id: str,
    readiness_status: str,
    decision: str,
) -> str:
    payload = {
        "generated_at_utc": generated_at_utc,
        "source_ledger_record_id": source_record_id,
        "signal_id": signal_id,
        "readiness_status": readiness_status,
        "decision": decision,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    ).hexdigest()
