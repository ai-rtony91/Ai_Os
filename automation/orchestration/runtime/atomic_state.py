from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MISSING_JSON = "MISSING_JSON"
CORRUPT_JSON = "CORRUPT_JSON"
VALID_JSON = "VALID_JSON"


@dataclass(frozen=True)
class JsonReadResult:
    status: str
    path: str
    data: Any | None
    error: str | None = None


def atomic_write_json(path: Path | str, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(target.parent),
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    finally:
        temp_path = Path(temp_name)
        if temp_path.exists():
            temp_path.unlink()


def read_json_tolerant(path: Path | str) -> JsonReadResult:
    target = Path(path)
    if not target.exists():
        return JsonReadResult(MISSING_JSON, str(target), None)
    try:
        return JsonReadResult(VALID_JSON, str(target), json.loads(target.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        return JsonReadResult(CORRUPT_JSON, str(target), None, f"{exc.__class__.__name__}: {exc}")
