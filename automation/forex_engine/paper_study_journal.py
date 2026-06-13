"""Deterministic paper study journal builder for Forex Engine v1."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from automation.forex_engine.paper_continuity_review import (
    PAPER_REVIEW_BLOCKED,
    PAPER_REVIEW_READY,
    PAPER_REVIEW_REQUIRED,
)

PAPER_STUDY_JOURNAL_SCHEMA = "forex_paper_study_journal_v1"
PAPER_STUDY_JOURNAL_READY = "PAPER_STUDY_JOURNAL_READY"
PAPER_STUDY_JOURNAL_BLOCKED = "PAPER_STUDY_JOURNAL_BLOCKED"

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
    "Create the journal packet artifact, keep paper-only execution controls, and request human approval for the next packet."
)
NEXT_SAFE_REJECT_ACTION = (
    "Rework the continuity record to satisfy required blocked actions, IDs, and paper-only safety checks, then rerun this stage."
)


def build_paper_study_journal(
    continuity_review: Mapping[str, Any],
    *,
    generated_at_utc: str | None = None,
    journal_id: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic study-journal record from continuity review output."""
    if not isinstance(continuity_review, Mapping):
        raise TypeError("continuity_review must be a mapping.")

    review = dict(continuity_review)

    review_status = str(review.get("review_status", "")).strip()
    source_decision_id = str(review.get("source_decision_id", "")).strip()
    source_ledger_record_id = str(review.get("source_ledger_record_id", "")).strip()
    signal_id = str(review.get("signal_id", "")).strip()
    decision = str(review.get("decision", "")).strip()
    execution_allowed = bool(review.get("execution_allowed", True))
    accepted_for_paper = bool(review.get("accepted_for_paper", False))
    risk_flags = list(review.get("risk_flags") if isinstance(review.get("risk_flags"), list) else [])

    safety = review.get("safety")
    if isinstance(safety, Mapping):
        safety_map = dict(safety)
    else:
        safety_map = {}

    blocked_actions = list(review.get("blocked_actions") if isinstance(review.get("blocked_actions"), list) else [])

    reject_reasons: list[str] = []

    if not review_status:
        reject_reasons.append("Missing continuity review_status.")
    elif review_status != PAPER_REVIEW_READY:
        reject_reasons.append("continuity review_status is not PAPER_REVIEW_READY.")

    if decision != PAPER_REVIEW_REQUIRED:
        reject_reasons.append("decision is not PAPER_ACCEPT.")

    if not accepted_for_paper:
        reject_reasons.append("accepted_for_paper is false.")

    if execution_allowed:
        reject_reasons.append("execution_allowed must be false.")

    if risk_flags:
        reject_reasons.append("risk_flags are present and block study journaling.")

    if not source_decision_id:
        reject_reasons.append("Missing source_decision_id.")

    if not source_ledger_record_id:
        reject_reasons.append("Missing source_ledger_record_id.")

    if not signal_id:
        reject_reasons.append("Missing signal_id.")

    if set(REQUIRED_BLOCKED_ACTIONS) - set(blocked_actions):
        reject_reasons.append("required blocked actions are not present.")

    missing_safety_flags = [flag for flag in SAFETY_BLOCK_FLAGS if not bool(safety_map.get(flag))]
    if missing_safety_flags:
        reject_reasons.append(
            "Safety blocks not fully satisfied: " + ", ".join(missing_safety_flags) + "."
        )

    review_ready = (
        not reject_reasons
        and review_status == PAPER_REVIEW_READY
        and decision == PAPER_REVIEW_REQUIRED
        and accepted_for_paper is True
        and execution_allowed is False
        and risk_flags == []
        and source_decision_id != ""
        and source_ledger_record_id != ""
        and signal_id != ""
        and set(REQUIRED_BLOCKED_ACTIONS).issubset(set(blocked_actions))
        and all(bool(safety_map.get(flag, False)) for flag in SAFETY_BLOCK_FLAGS)
    )

    if review_ready:
        journal_status = PAPER_STUDY_JOURNAL_READY
        accepted_for_study = True
        reason = "Continuity review is journal-ready for supervised paper study."
        reasons = [reason]
        next_safe_action = NEXT_SAFE_ACCEPT_ACTION
    else:
        journal_status = PAPER_STUDY_JOURNAL_BLOCKED
        accepted_for_study = False
        reasons = list(reject_reasons) if reject_reasons else ["Deterministic paper study journal rejection."]
        reason = reasons[0]
        next_safe_action = NEXT_SAFE_REJECT_ACTION

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    merged_blocked_actions = _merge_blocked_actions(blocked_actions)
    if journal_id is None:
        journal_id = _build_journal_id(
            generated_at_utc,
            source_decision_id,
            source_ledger_record_id,
            signal_id,
            review_status,
        )

    return {
        "schema": PAPER_STUDY_JOURNAL_SCHEMA,
        "mode": "PAPER_ONLY",
        "journal_id": journal_id,
        "generated_at_utc": generated_at_utc,
        "source_review_status": review_status,
        "source_review_status_from": review.get("schema", ""),
        "source_decision_id": source_decision_id,
        "source_ledger_record_id": source_ledger_record_id,
        "signal_id": signal_id,
        "journal_status": journal_status,
        "accepted_for_study": accepted_for_study,
        "execution_allowed": False,
        "review_summary": reason if review_ready else "",
        "reason": reason,
        "reasons": reasons,
        "risk_flags": risk_flags,
        "blocked_actions": merged_blocked_actions,
        "safety": safety_map,
        "study_artifacts": [
            "continuity_review_record",
            "paper_decision_record",
            "signal_ledger_record",
        ],
        "next_safe_action": next_safe_action,
    }


def _merge_blocked_actions(blocked_actions: list[Any]) -> list[str]:
    merged = [item for item in blocked_actions if isinstance(item, str)]
    merged.extend([item for item in REQUIRED_BLOCKED_ACTIONS if item not in merged])
    return list(dict.fromkeys(merged))


def _build_journal_id(
    generated_at_utc: str,
    source_decision_id: str,
    source_ledger_record_id: str,
    signal_id: str,
    review_status: str,
) -> str:
    payload = {
        "generated_at_utc": generated_at_utc,
        "source_decision_id": source_decision_id,
        "source_ledger_record_id": source_ledger_record_id,
        "signal_id": signal_id,
        "source_review_status": review_status,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    ).hexdigest()
