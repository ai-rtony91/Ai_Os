"""Queue read preview for the AI_OS Python supervisor skeleton."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_queue_preview(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "queue_path": str(path),
            "status": "MISSING",
            "items": [],
            "mutation_performed": False,
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return {
            "queue_path": str(path),
            "status": "INVALID_JSON",
            "items": [],
            "error": str(exc),
            "mutation_performed": False,
        }

    return {
        "queue_path": str(path),
        "status": "READ_ONLY",
        "items": payload.get("items", []),
        "mutation_performed": False,
    }
