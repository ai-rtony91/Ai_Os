"""Deterministic paper-only learning action router for Forex Engine v1."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from automation.forex_engine.paper_study_journal import (
    PAPER_STUDY_JOURNAL_BLOCKED,
    PAPER_STUDY_JOURNAL_READY,
    PAPER_STUDY_JOURNAL_SCHEMA,
)

PAPER_LEARNING_ACTION_ROUTER_SCHEMA = "forex_paper_learning_action_router_v1"
PAPER_LEARNING_ACTION_READY = "PAPER_LEARNING_ACTION_READY"
PAPER_LEARNING_ACTION_REVIEW_REQUIRED = "REVIEW_REQUIRED"
PAPER_LEARNING_ACTION_BLOCKED = "BLOCKED"

REQUIRED_SOURCE_FIELDS = (
    "schema",
    "journal_id",
    "journal_status",
    "accepted_for_study",
    "execution_allowed",
    "mode",
    "source_review_status",
)

REQUIRED_BLOCKED_ACTIONS = (
    "broker_api_call",
    "oanda_api_call",
    "real_order_submission",
    "webhook_execution",
    "secret_or_api_key_load",
    "live_market_data_fetch",
    "scheduler_or_daemon_start",
    "worker_launch",
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
    "Create a supervised learning payload from this journal and queue paper-only learning reviews before continuing."
)
NEXT_SAFE_REVIEW_ACTION = (
    "Fix study-journal blockers (missing required fields, paper safety, or blocked-actions list) and rerun this router."
)
NEXT_SAFE_RETRY_ACTION = (
    "Rebuild or correct the study journal record, then rerun the Sprint 19 router."
)


def route_paper_study_journal_to_learning_action(
    study_journal: Mapping[str, Any],
    *,
    generated_at_utc: str | None = None,
    router_id: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic supervised learning action route from a study journal."""
    if not isinstance(study_journal, Mapping):
        raise TypeError("study_journal must be a mapping.")

    journal = dict(study_journal)
    source_journal_id = str(journal.get("journal_id", "")).strip()
    source_journal_status = str(journal.get("journal_status", "")).strip()
    accepted_for_study = bool(journal.get("accepted_for_study", False))
    execution_allowed = bool(journal.get("execution_allowed", True))

    study_tags = _coerce_list(journal.get("study_artifacts"), fallback=["paper_study_journal"])

    safety = journal.get("safety")
    if isinstance(safety, Mapping):
        safety_map = dict(safety)
    else:
        safety_map = {}

    blocked_actions = _coerce_list(journal.get("blocked_actions"))
    reason_parts: list[str] = []

    missing_fields = [field for field in REQUIRED_SOURCE_FIELDS if field not in journal]
    if missing_fields:
        reason_parts.append("Missing required study journal fields: " + ", ".join(missing_fields) + ".")

    if source_journal_id == "":
        reason_parts.append("Missing source_journal_id.")

    if journal.get("schema") != PAPER_STUDY_JOURNAL_SCHEMA:
        reason_parts.append("source schema is not forex_paper_study_journal_v1.")

    if source_journal_status != PAPER_STUDY_JOURNAL_READY:
        reason_parts.append("source journal status is not PAPER_STUDY_JOURNAL_READY.")

    if accepted_for_study is False:
        reason_parts.append("accepted_for_study is false.")

    if execution_allowed:
        reason_parts.append("execution_allowed must be false.")

    if str(journal.get("mode", "")) != "PAPER_ONLY":
        reason_parts.append("mode must be PAPER_ONLY.")

    missing_safety_flags = [flag for flag in SAFETY_BLOCK_FLAGS if not bool(safety_map.get(flag, False))]
    if missing_safety_flags:
        reason_parts.append(
            "Safety blocks not fully satisfied: " + ", ".join(missing_safety_flags) + "."
        )

    required_blocked_missing = [action for action in REQUIRED_BLOCKED_ACTIONS if action not in blocked_actions]
    if required_blocked_missing:
        reason_parts.append("required blocked actions are not present: " + ", ".join(required_blocked_missing) + ".")

    if source_journal_status == PAPER_STUDY_JOURNAL_BLOCKED:
        route_status = PAPER_LEARNING_ACTION_BLOCKED
    else:
        route_status = (
            PAPER_LEARNING_ACTION_READY
            if not reason_parts and accepted_for_study is True
            else PAPER_LEARNING_ACTION_REVIEW_REQUIRED
        )

    accepted_for_learning = route_status == PAPER_LEARNING_ACTION_READY
    selected_learning_action = ""
    learning_priority = "low"
    next_safe_action = NEXT_SAFE_REVIEW_ACTION

    if accepted_for_learning:
        selected_learning_action = _select_learning_action(source_journal_status, source_journal_id, study_tags)
        learning_priority = _derive_priority(study_tags)
        next_safe_action = NEXT_SAFE_ACCEPT_ACTION
    elif source_journal_status == PAPER_STUDY_JOURNAL_BLOCKED:
        next_safe_action = NEXT_SAFE_RETRY_ACTION

    required_evidence = [
        "forex_paper_study_journal_v1",
        f"source_journal_id:{source_journal_id or 'unknown'}",
        "safety_block_flags",
        "blocked_actions",
        "source_trace",
    ]

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    if router_id is None:
        router_id = _build_router_id(
            generated_at_utc,
            source_journal_id,
            source_journal_status,
            route_status,
            selected_learning_action,
        )

    return {
        "schema": PAPER_LEARNING_ACTION_ROUTER_SCHEMA,
        "router_id": router_id,
        "source_journal_id": source_journal_id,
        "source_journal_status": source_journal_status,
        "route_status": route_status,
        "accepted_for_learning": accepted_for_learning,
        "execution_allowed": False,
        "live_execution_status": "BLOCKED",
        "mode": "PAPER_ONLY",
        "selected_learning_action": selected_learning_action,
        "action_reason": reason_parts[0] if reason_parts else "Source journal is safe for paper learning routing.",
        "learning_priority": learning_priority,
        "study_tags": study_tags,
        "required_evidence": required_evidence,
        "blocked_actions": _merge_blocked_actions(blocked_actions),
        "next_safe_action": next_safe_action,
        "safety": _build_safety_map(safety_map),
        "source_trace": {
            "source_schema": journal.get("schema"),
            "source_review_status": journal.get("source_review_status"),
            "source_decision_id": str(journal.get("source_decision_id", "")).strip(),
            "source_ledger_record_id": str(journal.get("source_ledger_record_id", "")).strip(),
            "signal_id": str(journal.get("signal_id", "")).strip(),
            "generated_at_utc": generated_at_utc,
            "router_build_inputs": [
                "schema",
                "journal_id",
                "journal_status",
                "accepted_for_study",
                "execution_allowed",
                "mode",
                "study_artifacts",
            ],
            "validation": {
                "missing_fields": missing_fields,
                "missing_blocked_actions": required_blocked_missing,
                "missing_safety_flags": required_safety_missing_flags(safety_map),
            },
        },
    }


def _coerce_list(value: Any, fallback: Sequence[str] | None = None) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item).strip() for item in list(value)]

    if fallback is None:
        return []
    return [str(item).strip() for item in list(fallback)]


def _select_learning_action(
    source_journal_status: str,
    source_journal_id: str,
    study_tags: list[str],
) -> str:
    if source_journal_status != PAPER_STUDY_JOURNAL_READY:
        return ""

    if "anomaly" in study_tags:
        return "run_anomaly_learning_investigation"
    if source_journal_id.startswith("sprint_18_"):
        return "review_sprint_18_learning_evidence_and_update_strategy_notes"
    return "run_paper_learning_summary_and_plan_follow_up"


def _derive_priority(study_tags: list[str]) -> str:
    priority_order = ("high", "medium", "low")
    if "high_confidence" in study_tags:
        return priority_order[0]
    if "risk" in study_tags or "continuity" in study_tags:
        return priority_order[1]
    return priority_order[2]


def required_blocked_missing(blocked_actions: Sequence[str]) -> list[str]:
    blocked = set(str(item) for item in _coerce_list(blocked_actions))
    return [action for action in REQUIRED_BLOCKED_ACTIONS if action not in blocked]


def _build_safety_map(source_safety: Mapping[str, Any] | None) -> dict[str, bool]:
    if not isinstance(source_safety, Mapping):
        source_safety = {}

    safety_map: dict[str, bool] = {}
    for flag in SAFETY_BLOCK_FLAGS:
        safety_map[flag] = bool(source_safety.get(flag, False))
    safety_map["paper_learning_router_execution_disabled"] = True
    safety_map["network_calls_disabled"] = True
    return safety_map


def _merge_blocked_actions(blocked_actions: Sequence[str]) -> list[str]:
    merged = _coerce_list(blocked_actions)
    merged.extend(REQUIRED_BLOCKED_ACTIONS)
    # Keep deterministic ordering while deduplicating.
    return list(dict.fromkeys(merged))


def required_safety_missing_flags(safety_map: Mapping[str, Any] | None) -> list[str]:
    if not isinstance(safety_map, Mapping):
        return list(SAFETY_BLOCK_FLAGS)
    return [flag for flag in SAFETY_BLOCK_FLAGS if not bool(safety_map.get(flag, False))]


def _build_router_id(
    generated_at_utc: str,
    source_journal_id: str,
    source_journal_status: str,
    route_status: str,
    selected_learning_action: str,
) -> str:
    payload = {
        "generated_at_utc": generated_at_utc,
        "source_journal_id": source_journal_id,
        "source_journal_status": source_journal_status,
        "route_status": route_status,
        "selected_learning_action": selected_learning_action,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    ).hexdigest()
