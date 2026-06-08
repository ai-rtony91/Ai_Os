"""Write human-approval queue items for operator-relief blockers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PENDING_DIR = Path("approval/operator_relief/pending")


def build_approval_item(
    reason: str,
    risk_level: str,
    recommended_action: str,
    source_evidence: dict[str, Any],
) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat()
    item_id = "operator_relief_" + created_at.replace(":", "").replace(".", "").replace("+", "Z")
    return {
        "id": item_id,
        "created_at": created_at,
        "reason": reason,
        "risk_level": risk_level,
        "human_required": True,
        "recommended_action": recommended_action,
        "executable": False,
        "source_evidence": source_evidence,
    }


def write_approval_item(item: dict[str, Any], pending_dir: Path | str = DEFAULT_PENDING_DIR) -> Path:
    directory = Path(pending_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{item['id']}.json"
    path.write_text(json.dumps(item, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
