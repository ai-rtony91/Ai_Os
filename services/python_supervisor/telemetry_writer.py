"""Layer 2 telemetry append for AI_OS Night Supervisor.

Appends JSONL events to telemetry/work_ledger.jsonl.
DRY_RUN (default): preview only — no file written.
APPLY: writes only when apply_enabled=True is passed explicitly by caller.

The apply_enabled flag is the APPLY gate.
Never default to True. Never infer from environment variables.

blocked_capabilities (DRY_RUN): file_writes, child_process_launch,
  network_calls, approval_mutation, packet_movement, worker_launch.
commit_performed: NO / push_performed: NO.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEDGER_SCHEMA = "AIOS_WORK_LEDGER_EVENT.v1"
RECEIPT_SCHEMA = "AIOS_TELEMETRY_WRITE_RECEIPT.v1"
ALLOWED_LEDGER = Path("telemetry/work_ledger.jsonl")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _payload_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def _path_allowed(path: Path) -> tuple[bool, str]:
    try:
        resolved = path.resolve()
        allowed = ALLOWED_LEDGER.resolve()
        if resolved == allowed:
            return True, ""
        return False, "output_path_outside_allowlist"
    except OSError as exc:
        return False, str(exc)


def build_supervisor_event(
    report: dict[str, Any],
    event_type: str = "night_supervisor_run",
) -> dict[str, Any]:
    """Build a compact telemetry event from a supervisor report.

    Extracts key fields only — does not embed the full report in the ledger.
    """
    return {
        "schema": LEDGER_SCHEMA,
        "event_type": event_type,
        "generated_at": report.get("generated_at") or _utc_now(),
        "session_id": f"AIOS-{_utc_now()[:10]}-SUPERVISOR",
        "supervisor_status": str(report.get("supervisor_status") or "UNKNOWN"),
        "packet_count": len(report.get("packet_flow") or []),
        "escalation_count": len(report.get("escalation_items") or []),
        "mode": str(report.get("mode") or "DRY_RUN"),
        "payload_hash": _payload_hash(report),
    }


def preview_event(
    event_type: str,
    payload: dict[str, Any],
    ledger_path: Path,
) -> dict[str, Any]:
    """Return what would be appended without writing. Always safe."""
    allowed, blocked_reason = _path_allowed(ledger_path)
    record = {
        "schema": LEDGER_SCHEMA,
        "event_type": event_type,
        "generated_at": payload.get("generated_at") or _utc_now(),
        **{k: v for k, v in payload.items() if k not in {"schema", "event_type"}},
    }
    return {
        "schema": RECEIPT_SCHEMA,
        "written": False,
        "mode": "DRY_RUN",
        "ledger_path": str(ledger_path),
        "path_allowed": allowed,
        "blocked_reason": blocked_reason,
        "event_type": event_type,
        "generated_at": _utc_now(),
        "record_preview": record,
        "blocked_capabilities": [
            "file_writes",
            "child_process_launch",
            "network_calls",
            "approval_mutation",
            "packet_movement",
            "worker_launch",
        ],
    }


def append_event(
    event_type: str,
    payload: dict[str, Any],
    ledger_path: Path,
    apply_enabled: bool = False,
) -> dict[str, Any]:
    """Append a JSONL event to the ledger.

    Writes only if apply_enabled=True. All other paths return a preview receipt.
    The apply_enabled flag is the APPLY gate — never default True.
    """
    record = {
        "schema": LEDGER_SCHEMA,
        "event_type": event_type,
        "generated_at": payload.get("generated_at") or _utc_now(),
        **{k: v for k, v in payload.items() if k not in {"schema", "event_type"}},
    }

    allowed, blocked_reason = _path_allowed(ledger_path)
    if not allowed:
        return {
            "schema": RECEIPT_SCHEMA,
            "written": False,
            "mode": "BLOCKED_PATH",
            "ledger_path": str(ledger_path),
            "event_type": event_type,
            "generated_at": _utc_now(),
            "blocked_reason": blocked_reason,
        }

    if not apply_enabled:
        return {
            "schema": RECEIPT_SCHEMA,
            "written": False,
            "mode": "DRY_RUN",
            "ledger_path": str(ledger_path),
            "event_type": event_type,
            "generated_at": _utc_now(),
            "record_preview": record,
            "next_safe_action": "Pass apply_enabled=True with Human Owner approval to write.",
        }

    try:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, separators=(",", ":")) + "\n"
        with ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(line)
        return {
            "schema": RECEIPT_SCHEMA,
            "written": True,
            "mode": "APPLY",
            "ledger_path": str(ledger_path),
            "event_type": event_type,
            "generated_at": _utc_now(),
            "bytes_written": len(line.encode("utf-8")),
            "record_hash": _payload_hash(record),
        }
    except OSError as exc:
        return {
            "schema": RECEIPT_SCHEMA,
            "written": False,
            "mode": "APPLY",
            "ledger_path": str(ledger_path),
            "event_type": event_type,
            "generated_at": _utc_now(),
            "error": str(exc),
        }
