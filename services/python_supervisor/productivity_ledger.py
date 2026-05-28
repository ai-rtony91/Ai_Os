"""Layer 2 productivity timer ledger for AI_OS Night Supervisor.

Schema:  telemetry/productivity/PRODUCTIVITY_TIMER_LEDGER.schema.json
Ledger:  telemetry/productivity/PRODUCTIVITY_TIMER_LEDGER.jsonl

DRY_RUN (default): preview + schema validation, no write.
APPLY: append only when apply_enabled=True and entry validates.

blocked_capabilities (DRY_RUN): file_writes, approval_mutation,
  packet_movement, worker_launch, runtime_mutation.
commit_performed: NO / push_performed: NO.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ENTRY_SCHEMA = "AIOS_PRODUCTIVITY_TIMER_ENTRY.v1"
RECEIPT_SCHEMA = "AIOS_LEDGER_APPEND_RECEIPT.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_utc_str(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    try:
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text).astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, AttributeError):
        return None


def _elapsed_minutes(start: str | None, stop: str | None) -> float | None:
    s = _to_utc_str(start)
    e = _to_utc_str(stop)
    if not s or not e:
        return None
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        delta = datetime.strptime(e, fmt) - datetime.strptime(s, fmt)
        return round(delta.total_seconds() / 60, 2)
    except ValueError:
        return None


def _elapsed_seconds(start: str | None, stop: str | None) -> float | None:
    s = _to_utc_str(start)
    e = _to_utc_str(stop)
    if not s or not e:
        return None
    try:
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        delta = datetime.strptime(e, fmt) - datetime.strptime(s, fmt)
        return round(delta.total_seconds(), 2)
    except ValueError:
        return None


def build_entry(
    session_id: str,
    active_packet_id: str,
    worker_lane: str,
    task_label: str,
    operator_start_time: str,
    operator_stop_time: str | None = None,
    validator_started_at: str | None = None,
    validator_finished_at: str | None = None,
    output_summary: str = "",
    blocked_reason: str | None = None,
    evidence_ready_for_collect: bool = False,
) -> dict[str, Any]:
    """Build a typed ledger entry dict. Does not write anything."""
    now = _utc_now()
    if not session_id:
        session_id = f"AIOS-{now[:10]}-LEDGER"
    return {
        "session_id": session_id,
        "date_key": now[:10],
        "operator_start_time": _to_utc_str(operator_start_time) or now,
        "operator_stop_time": _to_utc_str(operator_stop_time),
        "elapsed_minutes": _elapsed_minutes(operator_start_time, operator_stop_time),
        "active_packet_id": active_packet_id or "UNKNOWN",
        "worker_lane": worker_lane or "UNKNOWN",
        "task_label": task_label or "UNKNOWN",
        "validator_started_at": _to_utc_str(validator_started_at),
        "validator_finished_at": _to_utc_str(validator_finished_at),
        "validator_elapsed_seconds": _elapsed_seconds(validator_started_at, validator_finished_at),
        "output_summary": output_summary or "DRY_RUN ledger entry.",
        "blocked_reason": blocked_reason if blocked_reason and blocked_reason.strip() else None,
        "evidence_ready_for_collect": bool(evidence_ready_for_collect),
    }


def validate_entry(
    entry: dict[str, Any],
    schema_path: Path | None = None,
) -> tuple[bool, list[str]]:
    """Validate entry against required fields and basic types."""
    required = [
        "session_id", "date_key", "operator_start_time", "operator_stop_time",
        "elapsed_minutes", "active_packet_id", "worker_lane", "task_label",
        "validator_started_at", "validator_finished_at", "validator_elapsed_seconds",
        "output_summary", "blocked_reason", "evidence_ready_for_collect",
    ]
    errors: list[str] = []

    for field in required:
        if field not in entry:
            errors.append(f"Missing required field: {field}")

    if schema_path is not None and schema_path.exists():
        try:
            import jsonschema  # type: ignore[import]
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            try:
                jsonschema.validate(instance=entry, schema=schema)
            except jsonschema.ValidationError as exc:
                errors.append(f"Schema validation: {exc.message}")
        except ImportError:
            pass

    return (len(errors) == 0, errors)


def preview_append(
    entry: dict[str, Any],
    ledger_path: Path,
    schema_path: Path | None = None,
) -> dict[str, Any]:
    """Return preview of what would be appended. No write."""
    valid, errors = validate_entry(entry, schema_path)
    return {
        "schema": RECEIPT_SCHEMA,
        "written": False,
        "mode": "DRY_RUN",
        "valid": valid,
        "errors": errors,
        "would_append_to": str(ledger_path),
        "jsonl_preview": json.dumps(entry, separators=(",", ":")),
        "generated_at": _utc_now(),
        "next_safe_action": "Pass apply_enabled=True with Human Owner approval to append.",
    }


def append_entry(
    entry: dict[str, Any],
    ledger_path: Path,
    schema_path: Path | None = None,
    apply_enabled: bool = False,
) -> dict[str, Any]:
    """Append a validated JSONL entry to the ledger.

    Validates first — invalid entries are blocked regardless of apply_enabled.
    Writes only if apply_enabled=True and entry is valid.
    The apply_enabled flag is the APPLY gate — never default True.
    """
    valid, errors = validate_entry(entry, schema_path)

    if not valid:
        return {
            "schema": RECEIPT_SCHEMA,
            "written": False,
            "mode": "BLOCKED_INVALID_ENTRY",
            "valid": False,
            "errors": errors,
            "ledger_path": str(ledger_path),
            "generated_at": _utc_now(),
            "next_safe_action": "Fix validation errors before appending.",
        }

    if not apply_enabled:
        return preview_append(entry, ledger_path, schema_path)

    try:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, separators=(",", ":")) + "\n"
        with ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(line)
        return {
            "schema": RECEIPT_SCHEMA,
            "written": True,
            "mode": "APPLY",
            "valid": True,
            "errors": [],
            "ledger_path": str(ledger_path),
            "bytes_written": len(line.encode("utf-8")),
            "generated_at": _utc_now(),
        }
    except OSError as exc:
        return {
            "schema": RECEIPT_SCHEMA,
            "written": False,
            "mode": "APPLY",
            "valid": True,
            "errors": [str(exc)],
            "ledger_path": str(ledger_path),
            "generated_at": _utc_now(),
        }
