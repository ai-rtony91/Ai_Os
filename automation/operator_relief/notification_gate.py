"""Quiet local notification decision records.

This module does not send live notifications. It only records local evidence
about whether a condition would need operator attention or is SOS-worthy.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_NOTIFICATION_LOG = Path("telemetry/generated/operator_relief/notifications.jsonl")


def notification_decision(classification: dict[str, Any]) -> dict[str, Any]:
    clean_success = classification.get("classification") == "routine_success"
    sos_worthy = bool(classification.get("sos_worthy"))
    needs_operator = bool(classification.get("needs_operator"))
    return {
        "clean_success": clean_success,
        "needs_operator": needs_operator,
        "sos_worthy": sos_worthy,
        "live_delivery_allowed": False,
        "wake_requested": False,
        "local_evidence_only": needs_operator or sos_worthy,
        "reason": classification.get("classification", "unknown"),
        "executable": False,
    }


def record_notification_decision(
    classification: dict[str, Any],
    log_path: Path | str = DEFAULT_NOTIFICATION_LOG,
) -> Path | None:
    decision = notification_decision(classification)
    if decision["clean_success"]:
        return None
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "classification": classification,
        "decision": decision,
        "executable": False,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return path

