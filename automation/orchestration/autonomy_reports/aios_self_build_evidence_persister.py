"""AI_OS self-build cycle evidence persister (observe-only).

Persists the output of decide_self_build_cycle(...) to an atomic JSON evidence
file (and an optional Markdown summary) so every self-build decision leaves a
durable, redacted audit trail.

Safety posture:
  * Observe-only. Writes evidence/report files ONLY. Executes nothing, runs no
    worker, emits no command.
  * Atomic writes: temp file in the target dir, then rename. Temp is cleaned up
    on failure; none remains on success.
  * Redacts secret-shaped values (by key name and by value pattern) before
    writing, and records a redaction_summary.
  * Never overwrites existing evidence unless overwrite=True.
  * Fails closed on malformed cycle output: writes nothing, returns BLOCKED_MALFORMED.

Pure standard library. No network.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SCHEMA = "AIOS_SELF_BUILD_CYCLE_EVIDENCE.v1"
DEFAULT_SUBDIR = Path("Reports") / "self_build_cycle"
REDACTED = "[REDACTED]"

# Redact when a dict KEY looks secret-bearing.
SECRET_KEY = re.compile(
    r"(?i)(token|secret|password|passwd|api[_-]?key|private[_-]?key|credential|"
    r"bearer|access[_-]?key|client[_-]?secret|auth)"
)

# Redact when a string VALUE matches a high-confidence secret shape.
SECRET_VALUE_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private_key_block"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "aws_access_key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"), "github_token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "slack_token"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}\b"), "bearer_token"),
    (re.compile(r"\b[0-9a-fA-F]{40,}\b"), "long_hex_token"),
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _redact(obj: Any, path: str, events: list) -> Any:
    if isinstance(obj, dict):
        out: dict = {}
        for k, v in obj.items():
            kpath = f"{path}.{k}" if path else str(k)
            if isinstance(k, str) and SECRET_KEY.search(k):
                out[k] = REDACTED
                events.append({"path": kpath, "reason": "secret_key_name"})
            else:
                out[k] = _redact(v, kpath, events)
        return out
    if isinstance(obj, list):
        return [_redact(v, f"{path}[{i}]", events) for i, v in enumerate(obj)]
    if isinstance(obj, str):
        for pat, reason in SECRET_VALUE_PATTERNS:
            if pat.search(obj):
                events.append({"path": path, "reason": reason})
                return REDACTED
        return obj
    return obj


def redact(obj: Any) -> tuple[Any, dict]:
    events: list = []
    redacted = _redact(obj, "", events)
    summary = {
        "count": len(events),
        "by_reason": dict(Counter(e["reason"] for e in events)),
        "events": events,
    }
    return redacted, summary


def _is_valid_cycle(cycle_output: Any) -> bool:
    return (
        isinstance(cycle_output, dict)
        and isinstance(cycle_output.get("cycle_id"), str)
        and bool(cycle_output.get("cycle_id"))
        and isinstance(cycle_output.get("decision"), dict)
    )


def build_evidence_record(cycle_output: dict, now: Optional[str] = None) -> dict[str, object]:
    """Build the redacted evidence record. Raises ValueError on malformed input."""
    if not _is_valid_cycle(cycle_output):
        raise ValueError("malformed cycle output: requires cycle_id (str) and decision (dict)")
    now = now or _now()
    redacted, summary = redact({
        "decision": cycle_output.get("decision"),
        "evidence_bundle": cycle_output.get("evidence_bundle", {}),
        "source_modules": cycle_output.get("source_modules", []),
    })
    return {
        "schema": SCHEMA,
        "cycle_id": cycle_output["cycle_id"],
        "timestamp_utc": now,
        "mode": cycle_output.get("mode", "DRY_RUN"),
        "decision": redacted["decision"],
        "safety_status": cycle_output.get("safety_status", "BLOCKED"),
        "requires_human": bool(cycle_output.get("requires_human", True)),
        "evidence_bundle": redacted["evidence_bundle"],
        "source_modules": redacted["source_modules"],
        "redaction_summary": summary,
    }


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def _markdown(record: dict) -> str:
    d = record.get("decision", {}) or {}
    eb = record.get("evidence_bundle", {}) or {}
    lines = [
        "# AI_OS Self-Build Cycle Evidence",
        "",
        f"- cycle_id: `{record['cycle_id']}`",
        f"- timestamp_utc: `{record['timestamp_utc']}`",
        f"- mode: `{record['mode']}`",
        f"- safety_status: `{record['safety_status']}`",
        f"- requires_human: `{record['requires_human']}`",
        "",
        "## Decision",
        f"- action: `{d.get('action')}`",
        f"- reason: {d.get('reason', '')}",
        f"- blocked_reason: `{d.get('blocked_reason', '')}`",
        "",
        "## Evidence summary",
        f"- completion verdict: `{(eb.get('completion') or {}).get('verdict')}`",
        f"- runtime gate: `{(eb.get('runtime') or {}).get('runtime_gate')}`",
        f"- gap candidates: `{(eb.get('gap_candidates') or {}).get('candidate_count')}`",
        f"- redactions: `{record['redaction_summary']['count']}`",
        "",
        "_Observe-only evidence. No action was taken. No command emitted._",
    ]
    return "\n".join(lines) + "\n"


def persist_cycle_evidence(
    cycle_output: Any,
    *,
    output_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
    write_markdown: bool = True,
    overwrite: bool = False,
    now: Optional[str] = None,
) -> dict[str, object]:
    # Fail closed on malformed cycle output: write nothing.
    try:
        record = build_evidence_record(cycle_output, now=now)
    except ValueError as exc:
        return {
            "written": False,
            "status": "BLOCKED_MALFORMED",
            "reason": str(exc),
            "json_path": None,
            "md_path": None,
            "redaction_summary": {"count": 0, "by_reason": {}, "events": []},
        }

    if output_dir is not None:
        target_dir = Path(output_dir)
    else:
        base = Path(repo_root) if repo_root else Path.cwd()
        target_dir = base / DEFAULT_SUBDIR

    json_path = target_dir / f"{record['cycle_id']}.json"
    md_path = target_dir / f"{record['cycle_id']}.md"

    if json_path.exists() and not overwrite:
        return {
            "written": False,
            "status": "SKIPPED_EXISTS",
            "reason": "evidence already exists; pass overwrite=True to replace",
            "json_path": str(json_path),
            "md_path": str(md_path) if md_path.exists() else None,
            "redaction_summary": record["redaction_summary"],
        }

    _atomic_write_text(json_path, json.dumps(record, indent=2, sort_keys=True))
    if write_markdown:
        _atomic_write_text(md_path, _markdown(record))

    return {
        "written": True,
        "status": "WRITTEN",
        "json_path": str(json_path),
        "md_path": str(md_path) if write_markdown else None,
        "redaction_summary": record["redaction_summary"],
    }
