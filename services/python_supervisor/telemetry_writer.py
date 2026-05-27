"""Telemetry preview helper for the AI_OS Python supervisor skeleton."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_preview_event(event_type: str, source: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AIOS_PYTHON_SUPERVISOR_TELEMETRY_PREVIEW.v1",
        "event_type": event_type,
        "source": source,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload,
        "append_performed": False,
        "authority_note": "Telemetry preview is evidence only and does not authorize execution.",
    }
