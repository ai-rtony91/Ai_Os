"""Metadata-only Forex post-execution review loop evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (
    _bool,
    find_sensitive_data_blockers,
    hard_false_result,
    safety_false_result,
    safety_summary,
    unique,
)


SCHEMA = "AIOS_FOREX_POST_EXECUTION_REVIEW_LOOP_V1"
MODE = "READ_ONLY_METADATA_ONLY_POST_EXECUTION_REVIEW_LOOP"

POST_EXECUTION_REVIEW_LOOP_READY = "POST_EXECUTION_REVIEW_LOOP_READY"
POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY = (
    "POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY"
)
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_MISSING_SANITIZED_RECEIPT = "BLOCKED_BY_MISSING_SANITIZED_RECEIPT"
BLOCKED_BY_MISSING_OWNER_REVIEW = "BLOCKED_BY_MISSING_OWNER_REVIEW"
BLOCKED_BY_MISSING_AUDIT_RECORD = "BLOCKED_BY_MISSING_AUDIT_RECORD"
BLOCKED_BY_NEXT_ORDER_UNLOCKED = "BLOCKED_BY_NEXT_ORDER_UNLOCKED"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_READY = "AIOS_FOREX_22H6D_SUPERVISED_OPERATION_READINESS_V1"

POST_REVIEW_SAFE_METADATA_KEYS = frozenset({"secret_scan_completed"})


def evaluate_forex_post_execution_review_loop_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate post-execution review metadata without requiring an order."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = _post_review_sensitive_data_blockers(source)
    sensitive_data_detected = bool(sensitive_data_blockers)
    metadata_only = _bool(source.get("not_applicable_for_metadata_only")) is True
    summary = _post_review_summary(source, metadata_only=metadata_only)

    if sensitive_data_detected:
        status = BLOCKED_BY_SENSITIVE_DATA
        blockers = sensitive_data_blockers
    elif not source:
        status = INCOMPLETE_INPUTS
        blockers = ["payload_missing"]
    elif summary["owner_review_required"] is not True:
        status = BLOCKED_BY_MISSING_OWNER_REVIEW
        blockers = ["owner_review_required_missing_or_false"]
    elif summary["audit_record_present"] is not True:
        status = BLOCKED_BY_MISSING_AUDIT_RECORD
        blockers = ["audit_record_present_missing_or_false"]
    elif summary["next_order_blocked_until_review"] is not True:
        status = BLOCKED_BY_NEXT_ORDER_UNLOCKED
        blockers = ["next_order_blocked_until_review_missing_or_false"]
    elif not metadata_only and summary["sanitized_execution_receipt_present"] is not True:
        status = BLOCKED_BY_MISSING_SANITIZED_RECEIPT
        blockers = ["sanitized_execution_receipt_present_missing_or_false"]
    elif summary["ready"]:
        status = (
            POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY
            if metadata_only
            else POST_EXECUTION_REVIEW_LOOP_READY
        )
        blockers = []
    else:
        status = BLOCKED_BY_MISSING_SANITIZED_RECEIPT
        blockers = list(summary["blockers"])

    ready = status in {
        POST_EXECUTION_REVIEW_LOOP_READY,
        POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY,
    }
    next_best_packet = NEXT_PACKET_READY if ready else SCHEMA

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "post_execution_review_status": status,
        "post_execution_review_ready": ready,
        "owner_decision_required": True,
        "approval_token_required": True,
        "read_only": True,
        "metadata_only": True,
        "post_execution_review_summary": summary,
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_data_blockers": list(sensitive_data_blockers),
        "post_execution_review_blockers": unique(blockers),
        "owner_action_queue": _owner_action_queue(blockers, next_best_packet),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "post_execution_review_status": status,
            "post_execution_review_ready": ready,
            "input_redacted": sensitive_data_detected,
            "read_only": True,
            "metadata_only": True,
            **hard_false_result(),
            **safety_false_result(),
        },
        "safety": safety_summary(),
        **hard_false_result(),
        **safety_false_result(),
    }


def _post_review_summary(
    source: Mapping[str, Any],
    *,
    metadata_only: bool,
) -> dict[str, Any]:
    true_or_not_applicable = (
        "sanitized_execution_receipt_present",
        "pnl_review_recorded",
        "risk_review_recorded",
        "spread_slippage_review_recorded",
        "exception_review_recorded",
    )
    checks = {
        "post_trade_review_required": _bool(source.get("post_trade_review_required")),
        "owner_review_required": _bool(source.get("owner_review_required")),
        "audit_record_present": _bool(source.get("audit_record_present")),
        "secret_scan_completed": _bool(source.get("secret_scan_completed")),
        "no_raw_secret_logging": _bool(source.get("no_raw_secret_logging")),
        "no_raw_account_identifier_logging": _bool(
            source.get("no_raw_account_identifier_logging")
        ),
        "next_order_blocked_until_review": _bool(
            source.get("next_order_blocked_until_review")
        ),
    }
    for key in true_or_not_applicable:
        checks[key] = True if metadata_only else _bool(source.get(key))

    blockers = [
        f"{key}_missing_or_false"
        for key, value in checks.items()
        if value is not True
    ]
    return {
        "ready": bool(source) and not blockers,
        "blockers": unique(blockers),
        "not_applicable_for_metadata_only": metadata_only,
        **checks,
    }


def _post_review_sensitive_data_blockers(
    value: Any, path: str = "payload"
) -> list[str]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in POST_REVIEW_SAFE_METADATA_KEYS:
                blockers.extend(_safe_metadata_value_blockers(child, child_path))
                continue

            key_blockers = find_sensitive_data_blockers({key_text: None}, path)
            if key_blockers:
                blockers.extend(key_blockers)
                continue
            blockers.extend(_post_review_sensitive_data_blockers(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(
                _post_review_sensitive_data_blockers(child, f"{path}[{index}]")
            )
    else:
        blockers.extend(find_sensitive_data_blockers(value, path))
    return unique(blockers)


def _safe_metadata_value_blockers(value: Any, path: str) -> list[str]:
    if _bool(value) is not None:
        return []
    return find_sensitive_data_blockers(value, path)


def _owner_action_queue(
    blockers: list[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "blocked_by": list(blockers),
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
            **hard_false_result(),
            **safety_false_result(),
        }
        for action_id in (
            "REVIEW_SANITIZED_RECEIPT",
            "REVIEW_OWNER_POST_TRADE_DECISION",
            "REVIEW_AUDIT_RECORD",
            "REVIEW_NEXT_ORDER_LOCK",
            "REVIEW_NEXT_PACKET",
        )
    ]


def _safe_manual_next_action(status: str) -> str:
    if status == POST_EXECUTION_REVIEW_LOOP_READY:
        return "Review the sanitized receipt and keep the next order blocked until owner review."
    if status == POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY:
        return "Continue readiness scoring; no execution receipt is required for metadata-only review."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values before review."
    return "Repair post-execution review metadata and rerun."
