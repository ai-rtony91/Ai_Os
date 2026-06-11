"""Adapter for queue-safe approval evidence projection.

This module reads approval artifacts and produces a structured payload that can be
embedded directly into preview proposal objects. It does not mutate approvals
and never converts authority status to an explicit approval on its own.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_APPROVAL_GATE_PATH = Path("automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json")
DEFAULT_QUEUE_SPECIFIC_APPROVAL_GATE_PATH = Path(
    "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1.json"
)
DEFAULT_APPROVAL_INBOX_PATH = Path("automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json")
DEFAULT_QUEUE_TARGET_PACKET_ID = "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1"
APPROVED_STATUSES = {"approved_for_apply", "approved"}
NON_AUTHORIZED_STATUSES = {
    "pending_review",
    "pending",
    "review",
    "blocked",
    "invalid",
    "rejected",
}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _bool(value: Any) -> bool:
    return value is True


def _list_from(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    return []


def _first_non_empty(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _select_approval_gate_path(root: Path) -> tuple[Path, bool]:
    queue_specific_path = root / DEFAULT_QUEUE_SPECIFIC_APPROVAL_GATE_PATH
    if queue_specific_path.exists():
        return queue_specific_path, True
    return root / DEFAULT_APPROVAL_GATE_PATH, False


def _approval_gate_packet_id(approval_gate: dict[str, Any]) -> str:
    packet_id = _first_non_empty(approval_gate, ("packet_id", "approval_gate_id"))
    return str(packet_id).strip() if packet_id is not None else ""


def _approval_gate_matches_target(approval_gate_packet_id: str, target_packet_id: str) -> bool:
    if not approval_gate_packet_id or not target_packet_id:
        return False
    return approval_gate_packet_id == target_packet_id


def _to_status(value: Any) -> str:
    return str(value or "").strip().lower()


def _build_non_authorizing_reason(
    *,
    approval_status: str,
    approved_by_human: bool,
    has_authority: bool,
    has_approver: bool,
    apply_gate_present: bool,
    apply_gate_pending: bool,
    target_packet_id: str,
    approval_gate_packet_id: str,
    approval_gate_packet_mismatch: bool,
) -> str:
    if not apply_gate_present:
        return "apply approval gate file is missing"
    if approval_gate_packet_mismatch:
        return (
            "approval gate packet_id "
            f"{approval_gate_packet_id or 'missing'} does not match target_packet_id {target_packet_id or 'missing'}"
        )
    if apply_gate_pending:
        return "apply approval gate is pending_review"
    if approval_status and approval_status not in APPROVED_STATUSES:
        return f"apply approval status is {approval_status}"
    if approved_by_human and not has_authority:
        return "approval authority is missing"
    if approved_by_human and not has_approver:
        return "approval approver is missing"
    if not approved_by_human:
        return "human approval has not been granted"
    return "approval evidence is not explicit"


def _projection_has_authority_fields(approval_gate: dict[str, Any]) -> tuple[bool, bool]:
    if not approval_gate:
        return False, False
    approval_authority = _first_non_empty(
        approval_gate,
        ("approval_authority", "bound_by"),
    )
    approved_by = _first_non_empty(approval_gate, ("approved_by",))
    return bool(str(approval_authority).strip()), bool(str(approved_by).strip())


def build_queue_mutation_approval_evidence(
    *,
    repo_root: str | Path = ".",
    approval_gate_path: str | Path = DEFAULT_APPROVAL_GATE_PATH,
    approval_inbox_path: str | Path = DEFAULT_APPROVAL_INBOX_PATH,
    target_packet_id: str = DEFAULT_QUEUE_TARGET_PACKET_ID,
) -> dict[str, Any]:
    root = Path(repo_root)
    approval_gate_path = Path(approval_gate_path)
    approval_inbox_path = Path(approval_inbox_path)
    if not approval_gate_path.is_absolute():
        approval_gate_path = root / approval_gate_path
    if not approval_inbox_path.is_absolute():
        approval_inbox_path = root / approval_inbox_path

    selected_gate_path, selected_from_queue_specific = _select_approval_gate_path(root)
    if selected_from_queue_specific:
        approval_gate_path = selected_gate_path
    elif not approval_gate_path.exists() and selected_gate_path.exists():
        approval_gate_path = selected_gate_path

    approval_gate = _read_json(approval_gate_path) or {}
    approval_inbox = _read_json(approval_inbox_path) or {}

    source_files: list[str] = []
    if approval_gate_path.exists():
        source_files.append(str(approval_gate_path.as_posix()))
    if approval_inbox_path.exists():
        source_files.append(str(approval_inbox_path.as_posix()))

    approval_status = _to_status(_first_non_empty(approval_gate, ("approval_status",)))
    if not approval_status:
        approval_status = "missing_approval_status"

    approved_by_human = _bool(approval_gate.get("approved_by_human"))
    approval_gate_packet_id = _approval_gate_packet_id(approval_gate)
    approval_gate_packet_mismatch = bool(
        approval_gate_packet_id
        and str(target_packet_id).strip()
        and not _approval_gate_matches_target(approval_gate_packet_id, str(target_packet_id).strip())
    )
    approval_granted = False
    approval_authority = _first_non_empty(approval_gate, ("approval_authority", "bound_by"))
    if approval_authority is None:
        approval_authority = _first_non_empty(approval_inbox, ("approval_authority",))
    approved_by = _first_non_empty(approval_gate, ("approved_by",))
    if approved_by is None:
        approved_by = _first_non_empty(approval_inbox, ("approved_by",))
    has_authority, has_approver = _projection_has_authority_fields(approval_gate)
    if not has_authority:
        has_authority = bool(str(approval_authority).strip())
    if not has_approver:
        has_approver = bool(str(approved_by).strip())
    allowed_paths = _list_from(
        _first_non_empty(approval_gate, ("allowed_paths",))
        or _first_non_empty(approval_inbox, ("allowed_paths",))
    )
    blocked_paths = _list_from(
        _first_non_empty(approval_gate, ("blocked_paths", "blocked_path"))
        or _first_non_empty(approval_inbox, ("blocked_paths", "blocked_path"))
    )
    explicit_apply_approved = (
        approval_status in APPROVED_STATUSES
        and approved_by_human is True
        and approval_gate_packet_mismatch is False
        and has_authority is True
        and has_approver is True
        and bool(allowed_paths)
        and bool(blocked_paths)
        and _bool(_first_non_empty(approval_gate, ("validator_chain_required",)))
        and _bool(_first_non_empty(approval_gate, ("commit_package_required",)))
    )
    if explicit_apply_approved:
        approval_granted = True

    non_authorizing_placeholder = not explicit_apply_approved
    apply_gate_present = approval_gate_path.exists() and approval_gate_path.is_file()
    apply_gate_pending = approval_status in NON_AUTHORIZED_STATUSES or approval_status == "pending_review"
    approval_completed = approval_status in APPROVED_STATUSES

    missing_authority_fields = bool(
        approval_status in APPROVED_STATUSES and (not has_authority or not has_approver)
    )
    authority_active = str(_first_non_empty(approval_inbox, ("authority_status",))).strip().lower() == "active_authority"

    non_authorizing_reason = _build_non_authorizing_reason(
        approval_status=approval_status,
        approved_by_human=approved_by_human,
        has_authority=has_authority,
        has_approver=has_approver,
        apply_gate_present=apply_gate_present,
        apply_gate_pending=apply_gate_pending,
        target_packet_id=str(target_packet_id).strip(),
        approval_gate_packet_id=approval_gate_packet_id,
        approval_gate_packet_mismatch=approval_gate_packet_mismatch,
    )

    return {
        "source_files": source_files,
        "target_packet_id": str(target_packet_id).strip(),
        "approval_status": approval_status,
        "approved_by_human": approved_by_human,
        "approval_granted": approval_granted,
        "approval_authority": str(approval_authority) if approval_authority is not None else None,
        "approved_by": str(approved_by) if approved_by is not None else None,
        "packet_id": approval_gate_packet_id,
        "approval_gate_packet_id": approval_gate_packet_id,
        "approval_gate_path_used": approval_gate_path.as_posix(),
        "approval_gate_selected_from_queue_specific": selected_from_queue_specific,
        "approval_gate_packet_mismatch": approval_gate_packet_mismatch,
        "allowed_paths": allowed_paths,
        "blocked_paths": blocked_paths,
        "validator_chain_required": _first_non_empty(
            approval_gate, ("validator_chain_required",)
        )
        if "validator_chain_required" in approval_gate
        else _first_non_empty(approval_inbox, ("validator_chain_required",),),
        "commit_package_required": _first_non_empty(
            approval_gate, ("commit_package_required",)
        )
        if "commit_package_required" in approval_gate
        else _first_non_empty(approval_inbox, ("commit_package_required",),),
        "explicit_approval": explicit_apply_approved,
        "non_authorizing_reason": non_authorizing_reason,
        "file_exists": apply_gate_present and approval_inbox_path.exists(),
        "schema_present": bool("schema" in approval_gate or "schema" in approval_inbox),
        "authority_active": authority_active,
        "approval_completed": approval_completed,
        "apply_gate_pending": apply_gate_pending,
        "explicit_apply_approved": explicit_apply_approved,
        "missing_authority_fields": missing_authority_fields,
        "non_authorizing_placeholder": non_authorizing_placeholder,
    }


__all__ = ["build_queue_mutation_approval_evidence"]
