"""DRY_RUN-first packet dispatch preview layer for Night Supervisor V2."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


SAFE_LOCK_STATUSES = {"FREE"}
SAFE_APPROVAL_STATUSES = {"APPROVED", "NOT_REQUIRED"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _receipt_id(contract: dict[str, Any]) -> str:
    seed = "|".join(
        [
            str(contract.get("packet_id") or ""),
            str(contract.get("assigned_worker") or contract.get("recommended_worker") or ""),
            str(contract.get("dispatch_mode") or "DRY_RUN"),
        ]
    )
    return f"dispatch_{sha256(seed.encode('utf-8')).hexdigest()[:16]}"


def can_dispatch(contract: dict[str, Any]) -> tuple[bool, str]:
    """Return whether dispatch is permitted and blocked reason if not."""
    lock_status = str(contract.get("lock_status") or "UNKNOWN").upper()
    approval_status = str(contract.get("approval_status") or "UNKNOWN").upper()
    risk_level = str(contract.get("risk_level") or "UNKNOWN").upper()

    if lock_status not in SAFE_LOCK_STATUSES:
        return False, f"Blocked by lock status: {lock_status}."
    if approval_status not in SAFE_APPROVAL_STATUSES:
        return False, f"Blocked by approval status: {approval_status}."
    if risk_level == "CRITICAL" and approval_status != "APPROVED":
        return False, "Blocked by critical risk without explicit approval."
    if str(contract.get("dispatch_mode") or "DRY_RUN").upper() != "DRY_RUN":
        return False, "APPLY dispatch is not approved in this dispatcher layer."
    return True, ""


def build_dispatch_preview(contract: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Return what would be dispatched, to whom, and why."""
    allowed, blocked_reason = can_dispatch(contract)
    status = "DRY_RUN_PREVIEW" if allowed else "NOT_READY"
    if not allowed:
        reason_lower = blocked_reason.lower()
        if "lock status" in reason_lower:
            status = "BLOCKED_BY_LOCK"
        elif "approval status" in reason_lower:
            status = "BLOCKED_BY_APPROVAL"
        elif "risk" in reason_lower:
            status = "BLOCKED_BY_RISK"
        else:
            status = "BLOCKED_BY_CONFIG"

    worker_id = str(contract.get("assigned_worker") or contract.get("recommended_worker") or "UNASSIGNED")
    return {
        "dispatch_receipt_id": _receipt_id(contract),
        "packet_id": str(contract.get("packet_id") or ""),
        "packet_path": str(contract.get("packet_path") or ""),
        "worker_id": worker_id,
        "dispatch_mode": "DRY_RUN",
        "dispatch_status": status,
        "blocked_reason": blocked_reason,
        "route_evidence": {
            "recommended_worker": str(contract.get("recommended_worker") or ""),
            "assigned_worker": str(contract.get("assigned_worker") or ""),
            "routing_source": str(contract.get("routing_source") or ""),
            "routing_confidence": str(contract.get("routing_confidence") or ""),
        },
        "lock_evidence": {
            "lock_status": str(contract.get("lock_status") or ""),
            "lock_owner": str(contract.get("lock_owner") or ""),
            "lock_id": str(contract.get("lock_id") or ""),
        },
        "approval_evidence": {
            "approval_required": bool(contract.get("approval_required")),
            "approval_status": str(contract.get("approval_status") or ""),
            "approval_id": str(contract.get("approval_id") or ""),
        },
        "created_at": _utc_now(),
        "repo_root": str(Path(repo_root).resolve()),
        "write_performed": False,
    }


def write_dispatch_receipt(receipt: dict[str, Any], repo_root: Path, apply_enabled: bool = False) -> dict[str, Any]:
    """Write receipt only when apply_enabled is true; otherwise return dry-run preview."""
    if not apply_enabled:
        return {**receipt, "write_performed": False, "write_path": ""}

    output_dir = Path(repo_root).resolve() / "automation" / "orchestration" / "dispatch_receipts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{receipt['dispatch_receipt_id']}.json"
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {**receipt, "write_performed": True, "write_path": str(output_path)}


def write_worker_inbox_entry(
    contract: dict[str, Any],
    receipt: dict[str, Any],
    repo_root: Path,
    apply_enabled: bool = False,
) -> dict[str, Any]:
    """Write worker inbox entry only when apply_enabled is true."""
    worker_id = str(receipt.get("worker_id") or "UNASSIGNED")
    entry = {
        "schema": "AIOS_WORKER_INBOX_ENTRY.v1",
        "packet_id": str(contract.get("packet_id") or ""),
        "packet_path": str(contract.get("packet_path") or ""),
        "worker_id": worker_id,
        "dispatch_receipt_id": str(receipt.get("dispatch_receipt_id") or ""),
        "dispatch_mode": "DRY_RUN",
        "created_at": _utc_now(),
        "write_performed": False,
    }
    if not apply_enabled:
        return {**entry, "write_path": ""}

    output_dir = Path(repo_root).resolve() / "automation" / "orchestration" / "worker_inboxes" / worker_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{entry['dispatch_receipt_id']}.json"
    output_path.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {**entry, "write_performed": True, "write_path": str(output_path)}


def dispatch_packets(contracts: list[dict[str, Any]], repo_root: Path, apply_enabled: bool = False) -> list[dict[str, Any]]:
    """Return dispatch receipts or previews."""
    receipts = []
    for contract in contracts:
        preview = build_dispatch_preview(contract, repo_root)
        receipt = write_dispatch_receipt(preview, repo_root, apply_enabled=apply_enabled)
        inbox_entry = write_worker_inbox_entry(contract, receipt, repo_root, apply_enabled=apply_enabled)
        receipts.append({**receipt, "worker_inbox_entry": inbox_entry})
    return receipts
