"""Metadata-only owner runtime credential/session bridge evaluator."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (
    _bool,
    false_blockers,
    find_sensitive_data_blockers,
    hard_false_result,
    safety_false_result,
    safety_summary,
    true_blockers,
    unique,
)


SCHEMA = "AIOS_FOREX_OWNER_RUNTIME_CREDENTIAL_SESSION_BRIDGE_V1"
MODE = "READ_ONLY_METADATA_ONLY_OWNER_RUNTIME_CREDENTIAL_SESSION_BRIDGE"

RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY = (
    "RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY"
)
READY_FOR_OWNER_RUNTIME_CREDENTIAL_ENTRY_REVIEW = (
    "READY_FOR_OWNER_RUNTIME_CREDENTIAL_ENTRY_REVIEW"
)
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_SESSION_EXPIRY = "BLOCKED_BY_SESSION_EXPIRY"
BLOCKED_BY_CREDENTIAL_BOUNDARY = "BLOCKED_BY_CREDENTIAL_BOUNDARY"
BLOCKED_BY_OWNER_APPROVAL_TOKEN = "BLOCKED_BY_OWNER_APPROVAL_TOKEN"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_READY = "AIOS_FOREX_POST_EXECUTION_REVIEW_LOOP_V1"


def evaluate_owner_runtime_credential_session_bridge_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Validate credential/session metadata without asking for or reading secrets."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = find_sensitive_data_blockers(source)
    sensitive_data_detected = bool(sensitive_data_blockers)
    boundary = _credential_boundary_summary(source)
    approval = _approval_summary(source)

    if sensitive_data_detected:
        status = BLOCKED_BY_SENSITIVE_DATA
        blockers = sensitive_data_blockers
    elif not source:
        status = INCOMPLETE_INPUTS
        blockers = ["payload_missing"]
    elif not approval["ready"]:
        status = BLOCKED_BY_OWNER_APPROVAL_TOKEN
        blockers = list(approval["blockers"])
    elif boundary["session_unexpired"] is not True:
        status = BLOCKED_BY_SESSION_EXPIRY
        blockers = ["session_unexpired_false"]
    elif not boundary["ready"]:
        status = BLOCKED_BY_CREDENTIAL_BOUNDARY
        blockers = list(boundary["blockers"])
    elif _bool(source.get("owner_runtime_credential_entry_review_required")) is True:
        status = READY_FOR_OWNER_RUNTIME_CREDENTIAL_ENTRY_REVIEW
        blockers = []
    else:
        status = RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY
        blockers = []

    bridge_ready = status in {
        RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY,
        READY_FOR_OWNER_RUNTIME_CREDENTIAL_ENTRY_REVIEW,
    }
    next_best_packet = NEXT_PACKET_READY if bridge_ready else SCHEMA

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "credential_session_bridge_status": status,
        "credential_session_bridge_ready": bridge_ready,
        "owner_decision_required": True,
        "approval_token_required": True,
        "read_only": True,
        "metadata_only": True,
        "credential_boundary_summary": boundary,
        "owner_approval_summary": approval,
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_data_blockers": list(sensitive_data_blockers),
        "credential_session_bridge_blockers": unique(blockers),
        "owner_action_queue": _owner_action_queue(blockers, next_best_packet),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "input_fields_seen": sorted(str(key) for key in source.keys())
            if not sensitive_data_detected
            else [],
            "credential_session_bridge_status": status,
            "credential_session_bridge_ready": bridge_ready,
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


def _credential_boundary_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    true_checks = {
        "owner_enters_credentials_outside_repo_chat": _bool(
            source.get("owner_enters_credentials_outside_repo_chat")
        ),
        "runtime_only_credential_handoff": _bool(
            source.get("runtime_only_credential_handoff")
        ),
        "no_stored_api_key": _bool(source.get("no_stored_api_key")),
        "no_stored_account_id": _bool(source.get("no_stored_account_id")),
        "no_master_password": _bool(source.get("no_master_password")),
        "no_vault_password": _bool(source.get("no_vault_password")),
        "no_raw_token": _bool(source.get("no_raw_token")),
        "secret_scan_required": _bool(source.get("secret_scan_required")),
        "redaction_required": _bool(source.get("redaction_required")),
        "session_expiry_required": _bool(source.get("session_expiry_required")),
        "session_unexpired": _bool(source.get("session_unexpired")),
        "one_order_session_scope": _bool(source.get("one_order_session_scope")),
    }
    false_checks = {
        "credential_values_provided": _bool(source.get("credential_values_provided")),
        "credential_values_persisted": _bool(
            source.get("credential_values_persisted")
        ),
        "credential_values_logged": _bool(source.get("credential_values_logged")),
        "credential_values_requested_by_aios": _bool(
            source.get("credential_values_requested_by_aios")
        ),
        "repo_secret_storage_allowed": _bool(source.get("repo_secret_storage_allowed")),
        "chat_secret_sharing_allowed": _bool(
            source.get("chat_secret_sharing_allowed")
        ),
        "env_var_read_allowed": _bool(source.get("env_var_read_allowed")),
        "account_id_provided": _bool(source.get("account_id_provided")),
    }
    blockers = [*true_blockers(true_checks), *false_blockers(false_checks)]
    return {
        "ready": bool(source) and not blockers,
        "blockers": unique(blockers),
        **true_checks,
        **false_checks,
    }


def _approval_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    if "approval_token_metadata_present" not in source:
        return {"ready": True, "blockers": [], "approval_token_metadata_present": None}
    true_checks = {
        "approval_token_metadata_present": _bool(
            source.get("approval_token_metadata_present")
        ),
        "approval_token_id_present": _bool(
            source.get("approval_token_id_present"), default=True
        ),
        "approval_token_unexpired": _bool(
            source.get("approval_token_unexpired"), default=True
        ),
        "approval_token_unused": _bool(
            source.get("approval_token_unused"), default=True
        ),
    }
    false_checks = {
        "generic_yes_detected": _bool(source.get("generic_yes_detected"), default=False)
    }
    blockers = [*true_blockers(true_checks), *false_blockers(false_checks)]
    return {"ready": not blockers, "blockers": unique(blockers), **true_checks, **false_checks}


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
            "REVIEW_RUNTIME_ONLY_CREDENTIAL_HANDOFF",
            "REVIEW_SESSION_EXPIRY",
            "REVIEW_SECRET_REDACTION",
            "REVIEW_NEXT_PACKET",
        )
    ]


def _safe_manual_next_action(status: str) -> str:
    if status == RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY:
        return "Proceed to sanitized post-execution review-loop metadata."
    if status == READY_FOR_OWNER_RUNTIME_CREDENTIAL_ENTRY_REVIEW:
        return "Owner may review runtime-only credential entry outside repo and chat."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive values and rerun with metadata only."
    if status == BLOCKED_BY_SESSION_EXPIRY:
        return "Refresh the runtime session metadata before continuing."
    return "Repair credential/session boundary metadata and rerun."
