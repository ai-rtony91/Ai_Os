"""Append local operator-relief evidence under ignored generated telemetry."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_LEDGER_PATH = Path("telemetry/generated/operator_relief/evidence.jsonl")


def append_evidence(evidence: dict[str, Any], ledger_path: Path | str = DEFAULT_LEDGER_PATH) -> Path:
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executable": False,
        **evidence,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return path

