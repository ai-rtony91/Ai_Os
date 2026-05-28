"""Night Supervisor V2 orchestration shell.

Default mode is DRY_RUN. This module coordinates queue, routing, lock,
approval, dispatch preview, and telemetry preview stages without mutating
packet, lock, approval, worker, Git, broker, webhook, or trading state.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parents[1]
PY_SUPERVISOR_DIR = REPO_ROOT / "services" / "python_supervisor"
if str(PY_SUPERVISOR_DIR) not in sys.path:
    sys.path.insert(0, str(PY_SUPERVISOR_DIR))

from approval_officer import (  # noqa: E402
    apply_approval_status,
    approval_required_for_packet,
    check_packet_approval,
    read_approval_inbox,
)
from lock_manager import apply_lock_status, check_packet_lock, scan_locks  # noqa: E402
from packet_dispatcher import dispatch_packets  # noqa: E402
from queue_scanner import scan_queue  # noqa: E402
from telemetry_writer import build_supervisor_event, preview_event  # noqa: E402
from worker_assignment import assign_workers  # noqa: E402
from worker_route_recommender import recommend_routes_for_packets  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _risk_level(value: Any) -> str:
    token = str(value or "UNKNOWN").upper()
    if token in {"LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"}:
        return token
    if token in {"BLOCKED", "REVIEW_REQUIRED"}:
        return "HIGH"
    return "UNKNOWN"


def run_queue_stage(repo_root: Path) -> list[dict[str, Any]]:
    """Return active packets from queue scanner."""
    return scan_queue(repo_root)


def _contract_from_packet(packet: dict[str, Any]) -> dict[str, Any]:
    timestamp = _utc_now()
    packet_path = str(packet.get("source_path") or packet.get("packet_path") or "")
    return {
        "schema": "AIOS_PACKET_ROUTING_CONTRACT_V1",
        "schema_version": "1.0",
        "packet_id": str(packet.get("packet_id") or "UNKNOWN"),
        "packet_path": packet_path,
        "packet_title": str(packet.get("title") or packet.get("packet_title") or packet.get("packet_id") or "UNKNOWN"),
        "packet_state": str(packet.get("status") or packet.get("packet_state") or "UNKNOWN"),
        "source": "queue_scanner",
        "risk_level": _risk_level(packet.get("risk_level") or packet.get("risk_class")),
        "risk_reasons": [str(item) for item in _as_list(packet.get("risk_reasons") or packet.get("risk_signals"))],
        "recommended_worker": "",
        "assigned_worker": str(packet.get("assigned_worker") or packet.get("worker_id") or ""),
        "routing_source": "unknown",
        "routing_confidence": "UNKNOWN",
        "lock_status": "UNKNOWN",
        "lock_owner": "",
        "lock_id": str(packet.get("lock_id") or ""),
        "approval_required": bool(packet.get("approval_required")),
        "approval_status": "UNKNOWN",
        "approval_id": "",
        "dispatch_status": "NOT_READY",
        "dispatch_mode": "DRY_RUN",
        "dispatch_receipt_id": "",
        "telemetry_status": "NOT_WRITTEN",
        "blocked_reason": "",
        "timestamp": timestamp,
    }


def run_routing_stage(packets: list[dict[str, Any]], repo_root: Path) -> list[dict[str, Any]]:
    """Return routing contracts with worker recommendations."""
    contracts = [_contract_from_packet(packet) for packet in packets]
    route_by_packet = {item["packet_id"]: item for item in recommend_routes_for_packets(packets, repo_root)}
    assignments = {item.get("packet_id"): item for item in assign_workers(packets, repo_root)}

    for contract in contracts:
        packet_id = contract["packet_id"]
        route = route_by_packet.get(packet_id, {})
        assignment = assignments.get(packet_id, {})
        if route:
            contract["recommended_worker"] = str(route.get("recommended_worker") or "")
            contract["risk_level"] = _risk_level(route.get("risk_level") or contract.get("risk_level"))
            contract["risk_reasons"] = [str(route.get("reason") or "")]
            contract["routing_source"] = "worker_route_recommender"
            contract["routing_confidence"] = "MEDIUM"
            if route.get("needs_human_approval"):
                contract["approval_required"] = True
        if assignment:
            contract["assigned_worker"] = str(assignment.get("worker_id") or contract.get("assigned_worker") or "")
            contract["routing_source"] = "combined" if route else "worker_assignment"
    return contracts


def run_lock_stage(contracts: list[dict[str, Any]], repo_root: Path) -> list[dict[str, Any]]:
    """Return contracts with lock_status applied."""
    locks = scan_locks(repo_root)
    return [
        apply_lock_status(
            contract,
            check_packet_lock(str(contract.get("packet_id") or ""), str(contract.get("packet_path") or ""), locks),
        )
        for contract in contracts
    ]


def run_approval_stage(contracts: list[dict[str, Any]], repo_root: Path) -> list[dict[str, Any]]:
    """Return contracts with approval_status applied."""
    approvals = read_approval_inbox(repo_root)
    updated = []
    for contract in contracts:
        required = approval_required_for_packet(contract)
        result = check_packet_approval(
            str(contract.get("packet_id") or ""),
            str(contract.get("packet_path") or ""),
            approvals,
            required,
        )
        updated.append(apply_approval_status(contract, result))
    return updated


def run_dispatch_stage(
    contracts: list[dict[str, Any]],
    repo_root: Path,
    apply_enabled: bool = False,
) -> list[dict[str, Any]]:
    """Return dispatch previews or receipts."""
    return dispatch_packets(contracts, repo_root, apply_enabled=apply_enabled)


def run_telemetry_stage(report: dict[str, Any], repo_root: Path, apply_enabled: bool = False) -> dict[str, Any]:
    """Return telemetry preview unless apply_enabled is true and separately approved."""
    event = build_supervisor_event(
        report,
        event_type="night_supervisor_v2_preview",
    )
    preview = preview_event(
        "night_supervisor_v2_preview",
        event,
        Path(repo_root).resolve() / "telemetry" / "work_ledger.jsonl",
    )
    preview["apply_enabled"] = bool(apply_enabled)
    preview["write_performed"] = False
    return preview


def build_supervisor_v2_report(repo_root: Path, apply_enabled: bool = False) -> dict[str, Any]:
    """Build full Night Supervisor V2 report without mutating by default."""
    root = Path(repo_root).resolve()
    packets = run_queue_stage(root)
    routed = run_routing_stage(packets, root)
    locked = run_lock_stage(routed, root)
    approved = run_approval_stage(locked, root)
    dispatch_receipts = run_dispatch_stage(approved, root, apply_enabled=apply_enabled)

    for contract, receipt in zip(approved, dispatch_receipts, strict=False):
        contract["dispatch_status"] = str(receipt.get("dispatch_status") or "FAILED")
        contract["dispatch_receipt_id"] = str(receipt.get("dispatch_receipt_id") or "")
        contract["telemetry_status"] = "DRY_RUN_PREVIEW"
        blocker = str(receipt.get("blocked_reason") or "")
        if blocker:
            current = str(contract.get("blocked_reason") or "")
            contract["blocked_reason"] = "; ".join(item for item in [current, blocker] if item)

    report = {
        "schema": "AIOS_NIGHT_SUPERVISOR_V2_REPORT.v1",
        "mode": "DRY_RUN" if not apply_enabled else "APPLY_PREVIEW",
        "apply_enabled": bool(apply_enabled),
        "generated_at": _utc_now(),
        "repo_root": str(root),
        "stage_order": [
            "queue_scanner",
            "worker_route_recommender",
            "worker_assignment",
            "lock_manager",
            "approval_officer",
            "packet_dispatcher",
            "telemetry_preview",
        ],
        "queue_packets": packets,
        "routing_contracts": approved,
        "dispatch_receipts": dispatch_receipts,
        "blocked_count": sum(1 for item in approved if item.get("blocked_reason")),
        "write_performed": False,
        "worker_launch_enabled": False,
        "queue_mutation_enabled": False,
        "approval_mutation_enabled": False,
        "lock_mutation_enabled": False,
    }
    report["telemetry_preview"] = run_telemetry_stage(report, root, apply_enabled=apply_enabled)
    return report
