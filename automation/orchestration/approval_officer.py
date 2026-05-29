"""Read-only AI_OS approval officer for Night Supervisor V2."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_STATES = {"NOT_REQUIRED", "APPROVED", "PENDING", "BLOCKED", "EXPIRED", "UNKNOWN"}
APPROVAL_ROOTS = (Path("automation/orchestration/approval_inbox"),)


def _norm_path(value: Any) -> str:
    return str(value or "").replace("\\", "/").strip()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_status(value: Any) -> str:
    token = str(value or "").strip().lower()
    if token in {"approved", "approved_for_apply", "accepted", "granted"}:
        return "APPROVED"
    if token in {"pending", "pending_review", "waiting", "waiting_approval", "review_required", "needs_review"}:
        return "PENDING"
    if token in {"blocked", "rejected", "denied", "failed"}:
        return "BLOCKED"
    if token == "expired":
        return "EXPIRED"
    if token in {"not_required", "not required", "none"}:
        return "NOT_REQUIRED"
    return "UNKNOWN"


def is_approval_expired(approval: dict[str, Any], now_utc: datetime) -> bool:
    """Return true if approval is stale or past expires_at."""
    expires_at = _parse_time(approval.get("expires_at"))
    if expires_at and expires_at <= now_utc.astimezone(timezone.utc):
        return True
    return str(approval.get("approval_status") or "").upper() == "EXPIRED"


def normalize_approval(raw_approval: dict[str, Any], path: Path) -> dict[str, Any]:
    """Normalize approval data into a consistent record."""
    status = _normalize_status(raw_approval.get("approval_status") or raw_approval.get("status") or raw_approval.get("state"))
    if bool(raw_approval.get("approved_by_human")) and status == "UNKNOWN":
        status = "APPROVED"
    return {
        "approval_id": str(raw_approval.get("approval_id") or raw_approval.get("approval_gate_id") or path.stem),
        "packet_id": str(raw_approval.get("packet_id") or ""),
        "packet_path": _norm_path(raw_approval.get("packet_path") or raw_approval.get("target_path") or ""),
        "requested_by": str(raw_approval.get("requested_by") or ""),
        "approved_by": str(raw_approval.get("approved_by") or raw_approval.get("approved_by_human") or ""),
        "approval_status": status,
        "requested_action": str(raw_approval.get("requested_action") or raw_approval.get("requested_mode") or raw_approval.get("command") or ""),
        "reason": str(raw_approval.get("reason") or raw_approval.get("blocked_reason") or ""),
        "risk_level": str(raw_approval.get("risk_level") or ""),
        "tier": str(raw_approval.get("tier") or ""),
        "created_at": str(raw_approval.get("created_at") or raw_approval.get("requested_at") or ""),
        "updated_at": str(raw_approval.get("updated_at") or raw_approval.get("approved_at") or ""),
        "expires_at": str(raw_approval.get("expires_at") or ""),
        "source_path": _norm_path(path),
    }


def _approval_payloads(payload: Any, path: Path) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return [{"approval_id": path.stem, "approval_status": "UNKNOWN", "reason": "Approval JSON root was not an object."}]

    items: list[dict[str, Any]] = []
    for key in ("pending_approvals", "approved_actions", "blocked_actions", "approvals", "items"):
        for item in _as_list(payload.get(key)):
            if isinstance(item, dict):
                items.append(item)
    if items:
        return items
    return [payload]


def read_approval_inbox(repo_root: Path) -> list[dict[str, Any]]:
    """Read approval inbox JSON records from canonical approval locations."""
    root = Path(repo_root).resolve()
    records: list[dict[str, Any]] = []
    for relative_root in APPROVAL_ROOTS:
        folder = root / relative_root
        if not folder.exists() or not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:  # noqa: BLE001 - fail soft as evidence
                records.append(
                    {
                        "approval_id": path.stem,
                        "packet_id": "",
                        "packet_path": "",
                        "approval_status": "UNKNOWN",
                        "reason": f"Malformed or unreadable approval file: {exc}",
                        "source_path": _norm_path(path.relative_to(root)),
                    }
                )
                continue
            for item in _approval_payloads(payload, path):
                records.append(normalize_approval(item, path.relative_to(root)))
    return records


def approval_required_for_packet(packet: dict[str, Any]) -> bool:
    """Return true if packet metadata, risk, or policy requires approval."""
    if bool(packet.get("approval_required") or packet.get("user_approval_required")):
        return True
    if str(packet.get("approval_status") or "").upper() in {"PENDING", "BLOCKED", "EXPIRED", "UNKNOWN"}:
        return True
    if str(packet.get("risk_level") or "").upper() in {"HIGH", "CRITICAL"}:
        return True
    return False


def _approval_matches(approval: dict[str, Any], packet_id: str, packet_path: str) -> bool:
    approval_packet = str(approval.get("packet_id") or "")
    approval_path = _norm_path(approval.get("packet_path"))
    return bool(
        (approval_packet and packet_id and approval_packet == packet_id)
        or (approval_path and packet_path and approval_path == _norm_path(packet_path))
    )


def check_packet_approval(
    packet_id: str,
    packet_path: str,
    approvals: list[dict[str, Any]],
    approval_required: bool,
) -> dict[str, Any]:
    """Return approval_status, approval_id, blocked_reason."""
    if not approval_required:
        return {
            "approval_status": "NOT_REQUIRED",
            "approval_id": "",
            "blocked_reason": "",
            "approval_evidence": [],
        }

    now = datetime.now(timezone.utc)
    matches = [approval for approval in approvals if _approval_matches(approval, packet_id, packet_path)]
    if not matches:
        return {
            "approval_status": "UNKNOWN",
            "approval_id": "",
            "blocked_reason": "Approval is required but no matching approval record was found.",
            "approval_evidence": [],
        }

    normalized = []
    for approval in matches:
        item = dict(approval)
        if is_approval_expired(item, now):
            item["approval_status"] = "EXPIRED"
        normalized.append(item)

    for state in ("APPROVED", "PENDING", "BLOCKED", "EXPIRED", "UNKNOWN"):
        selected = next((approval for approval in normalized if approval.get("approval_status") == state), None)
        if selected:
            blocker = "" if state == "APPROVED" else f"Approval status blocks dispatch: {state}."
            return {
                "approval_status": state,
                "approval_id": str(selected.get("approval_id") or ""),
                "blocked_reason": blocker,
                "approval_evidence": normalized,
            }

    return {
        "approval_status": "UNKNOWN",
        "approval_id": "",
        "blocked_reason": "Matching approval record did not contain a recognized approval state.",
        "approval_evidence": normalized,
    }


def apply_approval_status(contract: dict[str, Any], approval_result: dict[str, Any]) -> dict[str, Any]:
    """Return updated AIOS_PACKET_ROUTING_CONTRACT_V1 object."""
    updated = dict(contract)
    status = str(approval_result.get("approval_status") or "UNKNOWN")
    if status not in APPROVAL_STATES:
        status = "UNKNOWN"
    updated["approval_status"] = status
    updated["approval_id"] = str(approval_result.get("approval_id") or "")
    updated["approval_required"] = status != "NOT_REQUIRED"
    blocker = str(approval_result.get("blocked_reason") or "")
    if blocker:
        current = str(updated.get("blocked_reason") or "")
        updated["blocked_reason"] = "; ".join(item for item in [current, blocker] if item)
    return updated

