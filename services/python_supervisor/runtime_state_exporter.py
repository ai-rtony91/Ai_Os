"""Export AI_OS Python supervisor state into telemetry/runtime JSON files.

DRY_RUN by default. Use --apply to write runtime state files.
Evidence only; this module never writes telemetry/work_ledger.jsonl.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RECEIPT_SCHEMA = "AIOS_RUNTIME_EXPORT_RECEIPT.v1"
RUNTIME_SCHEMA = "aios.runtime_visibility_api.v1"
HEARTBEAT_SCHEMA = "AIOS_RUNTIME_HEARTBEAT.v1"
PROCESS_SCHEMA = "AIOS_RUNTIME_PROCESS.v1"
READ_ONLY_MODE = "READ_ONLY"

RUNTIME_FILES = {
    "runtime_state": Path("telemetry/runtime/runtime_state.json"),
    "runtime_heartbeat": Path("telemetry/runtime/runtime_heartbeat.json"),
    "runtime_process": Path("telemetry/runtime/runtime_process.json"),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _ensure_runtime_path(path: Path, repo_root: Path) -> None:
    resolved = path.resolve()
    runtime_root = (repo_root / "telemetry" / "runtime").resolve()
    if runtime_root not in (resolved, *resolved.parents):
        raise ValueError(f"Refusing to write outside telemetry/runtime: {resolved}")
    if resolved.name == "work_ledger.jsonl" or "work_ledger.jsonl" in resolved.parts:
        raise ValueError("Refusing to write telemetry/work_ledger.jsonl")


def _count_by_packet_state(packet_flow: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for packet in packet_flow:
        state = str(packet.get("packet_state") or packet.get("status") or "UNKNOWN")
        counts[state] = counts.get(state, 0) + 1
    return counts


def _runtime_status(supervisor_status: str) -> str:
    status = supervisor_status.upper()
    if status in {"READY", "SAFE", "OK"}:
        return "ready"
    if status in {"BLOCKED", "ACTION_NEEDED"}:
        return "blocked"
    if status in {"REVIEW", "WARNING", "WARN"}:
        return "degraded"
    return "unknown"


def _packet_to_active_packet(packet: dict[str, Any], generated_at: str) -> dict[str, Any]:
    packet_id = str(packet.get("packet_id") or "UNKNOWN")
    return {
        "packetId": packet_id,
        "status": str(packet.get("packet_state") or "UNKNOWN"),
        "action": str(packet.get("next_safe_action") or "review"),
        "risk": "MEDIUM" if packet.get("approval_required") else "LOW",
        "reason": str(packet.get("escalation_reason") or "Supervisor packet flow evidence."),
        "lastEventType": "supervisor_packet_flow",
        "lastUpdatedAt": generated_at,
    }


def build_runtime_state(supervisor_report: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    generated_at = _utc_now()
    supervisor_status = str(supervisor_report.get("supervisor_status") or "UNKNOWN")
    packet_flow = list(supervisor_report.get("packet_flow") or [])
    escalations = list(supervisor_report.get("escalation_items") or [])
    repo_health = dict(supervisor_report.get("repo_health") or {})
    counts = _count_by_packet_state(packet_flow)
    waiting_for_approval = len(supervisor_report.get("approval_required") or [])
    recent_events = [
        {
            "eventId": f"supervisor_{index + 1}",
            "eventType": "supervisor_escalation",
            "source": "python_supervisor",
            "summary": str(item.get("evidence") or item.get("message") or "Supervisor escalation."),
            "status": str(item.get("severity") or "REVIEW"),
            "risk": str(item.get("severity") or "REVIEW"),
            "ts": generated_at,
        }
        for index, item in enumerate(escalations[:20])
    ]
    problems = [str(item.get("evidence") or item.get("message") or item) for item in escalations]

    return {
        "schema": RUNTIME_SCHEMA,
        "generatedAt": generated_at,
        "generated_at": generated_at,
        "mode": READ_ONLY_MODE,
        "status": _runtime_status(supervisor_status),
        "supervisor_status": supervisor_status,
        "packet_flow": packet_flow,
        "repo_health": repo_health,
        "escalation_items": escalations,
        "runtime": {
            "runtimeId": "python-supervisor-export",
            "status": _runtime_status(supervisor_status),
            "lastTickAt": generated_at,
            "freshness": "fresh",
            "queueSource": "python_supervisor",
        },
        "health": {
            "health": "ACTION_NEEDED" if problems else "OK",
            "healthy": not problems,
            "problems": problems,
            "generatedAt": generated_at,
            "schedulerActions": len(packet_flow),
            "staleWorkers": 0,
            "expiredWorkers": 0,
            "reclaimablePackets": 0,
            "retryablePackets": counts.get("STALE", 0),
            "poisonPackets": counts.get("BLOCKED", 0),
        },
        "queue": {
            "itemCount": len(packet_flow),
            "scheduled": len(packet_flow),
            "dispatchable": counts.get("READY_FOR_REVIEW", 0),
            "waitingForApproval": waiting_for_approval,
            "retryable": counts.get("STALE", 0),
            "manualReview": len(escalations),
            "reclaimable": 0,
            "poison": counts.get("BLOCKED", 0),
            "countsByStatus": counts,
            "status": "supervisor_projection",
        },
        "audit": {
            "ledgerPath": "telemetry/work_ledger.jsonl",
            "sourceEventCount": len(recent_events),
            "invalidLineCount": 0,
            "recentTimeline": recent_events,
        },
        "activePackets": [_packet_to_active_packet(packet, generated_at) for packet in packet_flow],
        "failedPackets": {"retryable": [], "poison": [], "all": []},
        "workers": [],
        "backpressure": {
            "throttled": bool(escalations),
            "level": "review" if escalations else "none",
            "reason": "Supervisor escalations require review." if escalations else "No supervisor escalations.",
            "allowedConcurrentPackets": 0 if escalations else 1,
            "checkedAt": generated_at,
            "pressureInputs": {
                "packetFlowCount": len(packet_flow),
                "escalationCount": len(escalations),
            },
        },
        "alerts": [
            {
                "severity": "critical" if str(item.get("severity")) == "BLOCKED" else "warning",
                "category": "supervisor",
                "message": str(item.get("evidence") or item.get("message") or "Supervisor escalation."),
                "generatedAt": generated_at,
            }
            for item in escalations
        ],
        "telemetry": {
            "eventCount": len(recent_events),
            "invalidLineCount": 0,
            "lastEventAt": recent_events[-1]["ts"] if recent_events else None,
            "recentEvents": recent_events,
            "ledger": {"path": "telemetry/work_ledger.jsonl", "exists": True},
        },
        "executionLedger": {
            "packetCount": len(packet_flow),
            "approvalCount": waiting_for_approval,
            "blockedPacketCount": counts.get("BLOCKED", 0),
            "appliedPacketCount": 0,
            "lastUpdatedAt": generated_at,
        },
        "provenance": {
            "runtime": "python_supervisor",
            "queue": "python_supervisor",
            "telemetry": "runtime_state_exporter.py",
            "fixture": False,
        },
        "warnings": problems,
        "controls": {
            "startRuntime": "BLOCKED_BY_EXPORTER_DEFAULT",
            "stopRuntime": "BLOCKED_BY_EXPORTER_DEFAULT",
            "assignQueueItem": "BLOCKED_BY_EXPORTER_DEFAULT",
            "advancePacket": "BLOCKED_BY_EXPORTER_DEFAULT",
        },
        "nextSafeAction": str(
            (supervisor_report.get("next_safe_actions") or [{}])[0].get("action")
            if supervisor_report.get("next_safe_actions")
            else "Review runtime visibility export before any protected action."
        ),
        "next_safe_action": str(
            (supervisor_report.get("next_safe_actions") or [{}])[0].get("action")
            if supervisor_report.get("next_safe_actions")
            else "Review runtime visibility export before any protected action."
        ),
    }


def build_heartbeat(supervisor_report: dict[str, Any]) -> dict[str, Any]:
    now = _utc_now()
    return {
        "schema": HEARTBEAT_SCHEMA,
        "last_beat": now,
        "heartbeatAt": now,
        "supervisor_status": str(supervisor_report.get("supervisor_status") or "UNKNOWN"),
        "status": _runtime_status(str(supervisor_report.get("supervisor_status") or "UNKNOWN")),
        "mode": READ_ONLY_MODE,
    }


def build_process_stub() -> dict[str, Any]:
    return {
        "schema": PROCESS_SCHEMA,
        "process_status": "EXPORTER_DRIVEN",
        "status": "EXPORTER_DRIVEN",
        "started_by": "runtime_state_exporter.py",
        "generated_at": _utc_now(),
        "mode": READ_ONLY_MODE,
    }


def _write_json(path: Path, payload: dict[str, Any], repo_root: Path) -> None:
    _ensure_runtime_path(path, repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def export_runtime_state(repo_root: Path, apply_enabled: bool = False) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    supervisor_dir = repo_root / "services" / "python_supervisor"
    if str(supervisor_dir) not in sys.path:
        sys.path.insert(0, str(supervisor_dir))

    from supervisor_engine import build_supervisor_report  # pylint: disable=import-outside-toplevel

    supervisor_report = build_supervisor_report(repo_root)
    runtime_state = build_runtime_state(supervisor_report, repo_root)
    heartbeat = build_heartbeat(supervisor_report)
    process_stub = build_process_stub()
    payloads = {
        "runtime_state": runtime_state,
        "runtime_heartbeat": heartbeat,
        "runtime_process": process_stub,
    }
    write_paths = [RUNTIME_FILES[key].as_posix() for key in payloads]

    if apply_enabled:
        for key, payload in payloads.items():
            _write_json(repo_root / RUNTIME_FILES[key], payload, repo_root)

    return {
        "schema": RECEIPT_SCHEMA,
        "generated_at": _utc_now(),
        "mode": "APPLY" if apply_enabled else "DRY_RUN",
        "apply_enabled": apply_enabled,
        "written": apply_enabled,
        "write_paths": write_paths if apply_enabled else [],
        "runtime_state_preview": runtime_state,
        "heartbeat_preview": heartbeat,
        "process_preview": process_stub,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export AI_OS runtime state from Python supervisor output.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--apply", action="store_true", help="Write telemetry/runtime files.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON receipt.")
    args = parser.parse_args()

    receipt = export_runtime_state(Path(args.repo_root), apply_enabled=args.apply)
    print(json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
