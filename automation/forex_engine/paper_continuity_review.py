"""Deterministic paper continuity/review step for Forex Engine v1."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

PAPER_CONTINUITY_REVIEW_SCHEMA = "forex_paper_continuity_review_v1"

PAPER_REVIEW_READY = "PAPER_REVIEW_READY"
PAPER_REVIEW_BLOCKED = "PAPER_REVIEW_BLOCKED"

PAPER_REVIEW_REQUIRED = "PAPER_ACCEPT"

REQUIRED_BLOCKED_ACTIONS = (
    "broker_api_call",
    "oanda_api_call",
    "real_order_submission",
    "webhook_execution",
    "secret_or_api_key_load",
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

NEXT_SAFE_ACCEPT_ACTION = (
    "Continue with supervised paper continuity study and document the supervised follow-up action."
)
NEXT_SAFE_REJECT_ACTION = (
    "Rework the decision record to remove unsafe decision paths and blockers, then rerun review."
)


def evaluate_decision_for_continuity_review(
    decision_record: Mapping[str, Any],
    *,
    generated_at_utc: str | None = None,
    review_id: str | None = None,
) -> dict[str, Any]:
    """Evaluate a paper risk decision and return a deterministic review record."""
    if not isinstance(decision_record, Mapping):
        raise TypeError("decision_record must be a mapping.")

    source = dict(decision_record)

    source_decision_id = str(source.get("source_decision_id", "")).strip()
    source_ledger_record_id = str(
        source.get("source_ledger_record_id", "").strip() or source.get("ledger_record_id", "").strip()
    )
    signal_id = str(source.get("signal_id", "")).strip()
    decision = str(source.get("decision", "")).strip()
    accepted_for_paper = bool(source.get("accepted_for_paper", False))
    execution_allowed = bool(source.get("execution_allowed", True))
    risk_flags = list(source.get("risk_flags", []) if isinstance(source.get("risk_flags"), list) else [])

    safety = source.get("safety")
    if isinstance(safety, Mapping):
        safety_map = dict(safety)
    else:
        safety_map = {}

    blocked_actions = list(source.get("blocked_actions", [])) if isinstance(source.get("blocked_actions"), list) else []

    reject_reasons: list[str] = []

    if not source_decision_id:
        reject_reasons.append("Missing source_decision_id.")
    if not source_ledger_record_id:
        reject_reasons.append("Missing source_ledger_record_id.")
    if not signal_id:
        reject_reasons.append("Missing signal_id.")

    if decision != PAPER_REVIEW_REQUIRED:
        reject_reasons.append("decision is not PAPER_ACCEPT.")

    if not accepted_for_paper:
        reject_reasons.append("accepted_for_paper is false.")

    if execution_allowed:
        reject_reasons.append("execution_allowed must be false.")

    if risk_flags:
        reject_reasons.append("risk_flags are present and block review.")

    missing_safety_flags = [flag for flag in SAFETY_BLOCK_FLAGS if not bool(safety_map.get(flag))]
    if missing_safety_flags:
        reject_reasons.append(
            "Safety blocks not fully satisfied: " + ", ".join(missing_safety_flags) + "."
        )

    required_blocks_present = set(REQUIRED_BLOCKED_ACTIONS).issubset(set(blocked_actions))
    if not required_blocks_present:
        reject_reasons.append("required blocked actions are not present.")

    can_review = (
        not reject_reasons
        and decision == PAPER_REVIEW_REQUIRED
        and accepted_for_paper is True
        and execution_allowed is False
        and len(risk_flags) == 0
        and source_decision_id != ""
        and source_ledger_record_id != ""
        and signal_id != ""
        and required_blocks_present
        and all(bool(safety_map.get(flag, False)) for flag in SAFETY_BLOCK_FLAGS)
    )

    if can_review:
        review_status = PAPER_REVIEW_READY
        review_summary = "Paper risk decision is reviewable and safe for supervised continuation."
        reasons = [review_summary]
        next_safe_action = NEXT_SAFE_ACCEPT_ACTION
        accepted_for_output = True
    else:
        review_status = PAPER_REVIEW_BLOCKED
        reasons = list(reject_reasons) if reject_reasons else ["Deterministic continuity review rejection."]
        next_safe_action = NEXT_SAFE_REJECT_ACTION
        accepted_for_output = False

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    if review_id is None:
        review_id = _build_review_id(
            generated_at_utc,
            source_decision_id,
            source_ledger_record_id,
            signal_id,
            decision,
            review_status,
        )

    return {
        "schema": PAPER_CONTINUITY_REVIEW_SCHEMA,
        "mode": "PAPER_ONLY",
        "review_id": review_id,
        "source_decision_id": source_decision_id,
        "source_ledger_record_id": source_ledger_record_id,
        "signal_id": signal_id,
        "generated_at_utc": generated_at_utc,
        "decision": decision,
        "review_status": review_status,
        "accepted_for_paper": accepted_for_output,
        "execution_allowed": False,
        "review_summary": review_summary if can_review else "",
        "reason": reasons[0] if reasons else "",
        "reasons": reasons,
        "risk_flags": risk_flags,
        "blocked_actions": list(dict.fromkeys(blocked_actions)),
        "safety": safety_map,
        "next_safe_action": next_safe_action,
    }


def _build_review_id(
    generated_at_utc: str,
    source_decision_id: str,
    source_ledger_record_id: str,
    signal_id: str,
    decision: str,
    review_status: str,
) -> str:
    payload = {
        "generated_at_utc": generated_at_utc,
        "source_decision_id": source_decision_id,
        "source_ledger_record_id": source_ledger_record_id,
        "signal_id": signal_id,
        "decision": decision,
        "review_status": review_status,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    ).hexdigest()
