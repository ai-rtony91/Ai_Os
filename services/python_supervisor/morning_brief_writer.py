"""Layer 2 morning brief persistence for AI_OS Night Supervisor.

Writes supervisor report JSON to telemetry/supervisor_briefs/YYYY-MM-DD_HHMMZ.json.
Closes the human review gap: Anthony Meza can open a dated file and review
the full overnight report without capturing shell output.

ONLY approved write target: telemetry/supervisor_briefs/
No write to docs/, automation/, services/, or any protected root.

DRY_RUN (default): returns preview of path + content summary — writes nothing.
APPLY: writes file only when apply_enabled=True and output_dir is reachable.

blocked_capabilities (DRY_RUN): file_writes, child_process_launch,
  packet_movement, approval_mutation, worker_launch.
commit_performed: NO / push_performed: NO.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BRIEF_SCHEMA = "AIOS_MORNING_BRIEF_FILE.v1"
RECEIPT_SCHEMA = "AIOS_BRIEF_WRITE_RECEIPT.v1"
ALLOWED_OUTPUT_DIR = Path("telemetry/supervisor_briefs")
_SAFE_CHARS = re.compile(r"[^A-Za-z0-9_\-]")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_brief_filename(generated_at: str) -> str:
    """Convert ISO timestamp to safe filename: YYYY-MM-DD_HHMMZ.json"""
    try:
        text = generated_at.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(text).astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%d_%H%MZ") + ".json"
    except (ValueError, AttributeError):
        return f"brief_{_SAFE_CHARS.sub('_', str(generated_at))}.json"


def _resolve_output_path(report: dict[str, Any], output_dir: Path) -> Path:
    generated_at = str(report.get("generated_at") or _utc_now())
    filename = build_brief_filename(generated_at)
    candidate = output_dir / filename
    if not candidate.exists():
        return candidate
    stem = filename[: -len(".json")]
    for suffix in range(2, 100):
        candidate = output_dir / f"{stem}_{suffix}.json"
        if not candidate.exists():
            return candidate
    return output_dir / f"{stem}_overflow.json"


def _path_allowed(path: Path, directory: bool = False) -> tuple[bool, str]:
    try:
        resolved = path.resolve()
        allowed_root = ALLOWED_OUTPUT_DIR.resolve()
        target = resolved if directory else resolved.parent
        if target == allowed_root or str(target).startswith(str(allowed_root) + "\\"):
            return True, ""
        return False, "output_path_outside_allowlist"
    except OSError as exc:
        return False, str(exc)


def _brief_file_content(report: dict[str, Any]) -> dict[str, Any]:
    escalations = report.get("escalation_items") or []
    packets = report.get("packet_flow") or []
    status = str(report.get("supervisor_status") or "UNKNOWN")
    return {
        "schema": BRIEF_SCHEMA,
        "_executive_summary": {
            "supervisor_status": status,
            "packet_count": len(packets),
            "escalation_count": len(escalations),
            "mode": str(report.get("mode") or "DRY_RUN"),
            "generated_at": str(report.get("generated_at") or _utc_now()),
            "human_review_required": bool(escalations) or status in ("BLOCKED", "WARNING", "REVIEW"),
        },
        "generated_at": str(report.get("generated_at") or _utc_now()),
        "report": report,
    }


def preview_brief(report: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    """Return preview of what would be written. No filesystem access."""
    generated_at = str(report.get("generated_at") or _utc_now())
    filename = build_brief_filename(generated_at)
    content_bytes = len(json.dumps(_brief_file_content(report)).encode("utf-8"))
    allowed, blocked_reason = _path_allowed(output_dir / filename)
    return {
        "schema": RECEIPT_SCHEMA,
        "written": False,
        "mode": "DRY_RUN",
        "would_write_to": str(output_dir / filename),
        "path_allowed": allowed,
        "blocked_reason": blocked_reason,
        "filename": filename,
        "content_size_bytes": content_bytes,
        "supervisor_status": str(report.get("supervisor_status") or "UNKNOWN"),
        "packet_count": len(report.get("packet_flow") or []),
        "escalation_count": len(report.get("escalation_items") or []),
        "generated_at": _utc_now(),
        "next_safe_action": "Pass apply_enabled=True with Human Owner approval to write.",
    }


def write_brief(
    report: dict[str, Any],
    output_dir: Path,
    apply_enabled: bool = False,
) -> dict[str, Any]:
    """Write morning brief JSON.

    Writes only if apply_enabled=True. All other paths return preview.
    The apply_enabled flag is the APPLY gate — never default True.
    """
    if not apply_enabled:
        return preview_brief(report, output_dir)

    try:
        allowed, blocked_reason = _path_allowed(output_dir, directory=True)
        if not allowed:
            return {
                "schema": RECEIPT_SCHEMA,
                "written": False,
                "mode": "BLOCKED_PATH",
                "output_dir": str(output_dir),
                "generated_at": _utc_now(),
                "blocked_reason": blocked_reason,
            }
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = _resolve_output_path(report, output_dir)
        allowed_file, blocked_reason = _path_allowed(output_path)
        if not allowed_file:
            return {
                "schema": RECEIPT_SCHEMA,
                "written": False,
                "mode": "BLOCKED_PATH",
                "output_path": str(output_path),
                "generated_at": _utc_now(),
                "blocked_reason": blocked_reason,
            }
        content = json.dumps(_brief_file_content(report), indent=2)
        output_path.write_text(content, encoding="utf-8")
        return {
            "schema": RECEIPT_SCHEMA,
            "written": True,
            "mode": "APPLY",
            "output_path": str(output_path),
            "filename": output_path.name,
            "file_size_bytes": len(content.encode("utf-8")),
            "supervisor_status": str(report.get("supervisor_status") or "UNKNOWN"),
            "generated_at": _utc_now(),
        }
    except OSError as exc:
        return {
            "schema": RECEIPT_SCHEMA,
            "written": False,
            "mode": "APPLY",
            "output_dir": str(output_dir),
            "generated_at": _utc_now(),
            "error": str(exc),
        }
