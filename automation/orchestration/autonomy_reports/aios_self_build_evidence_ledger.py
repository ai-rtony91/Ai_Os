"""AI_OS self-build evidence ledger (observe-only reader/aggregator).

The evidence persister (aios_self_build_evidence_persister.py) writes one redacted
JSON record per self-build cycle to Reports/self_build_cycle/<cycle_id>.json. Nothing
on main reads those records back. This ledger closes that arrow: it reads the whole
evidence directory and produces a single, human-reviewable digest of what the
self-build loop has been deciding over time.

Safety posture:
  * Observe-only. Reads evidence JSON files. Optionally writes ONE digest file when
    an explicit output path is given. Executes nothing, runs no worker, emits no
    command, makes no decision the loop will act on.
  * Aggregate-only projection. The digest extracts scalar facts (cycle ids, decision
    action labels, safety statuses, human-required flags, counts, timestamps). It
    NEVER copies evidence_bundle contents forward, so no source value (already
    redacted upstream) can leak through this layer either.
  * Fail-soft on read. A malformed or off-schema file is skipped and recorded as a
    read error; it never crashes the ledger.
  * Atomic digest write, and never overwrites an existing digest unless overwrite=True.

Pure standard library. No network, no mutation of source evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


LEDGER_SCHEMA = "AIOS_SELF_BUILD_EVIDENCE_LEDGER.v1"
EVIDENCE_SCHEMA = "AIOS_SELF_BUILD_CYCLE_EVIDENCE.v1"
DEFAULT_SUBDIR = Path("Reports") / "self_build_cycle"
DEFAULT_DIGEST_NAME = "evidence_ledger_digest.json"

# A self-build cycle is safe-shaped when it is an observed DRY_RUN that took no action.
SAFE_MODE = "DRY_RUN"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_evidence_record(obj: Any) -> bool:
    return (
        isinstance(obj, dict)
        and obj.get("schema") == EVIDENCE_SCHEMA
        and isinstance(obj.get("cycle_id"), str)
        and bool(obj.get("cycle_id"))
    )


def load_evidence_records(evidence_dir: Path) -> tuple[list[dict], list[dict]]:
    """Read every *.json evidence record in evidence_dir.

    Returns (records, errors). Fail-soft: unreadable, non-JSON, or off-schema files
    are skipped and reported in errors; this never raises on bad input files.
    """
    evidence_dir = Path(evidence_dir)
    records: list[dict] = []
    errors: list[dict] = []
    if not evidence_dir.exists() or not evidence_dir.is_dir():
        return records, errors

    for path in sorted(evidence_dir.glob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append({"file": path.name, "reason": "unreadable_or_invalid_json", "detail": str(exc)})
            continue
        if not _is_evidence_record(obj):
            errors.append({"file": path.name, "reason": "off_schema_or_missing_cycle_id"})
            continue
        records.append(obj)
    return records, errors


def _safe_str(value: Any) -> str:
    return value if isinstance(value, str) and value else ""


def summarize_records(records: list[dict], errors: Optional[list[dict]] = None, now: Optional[str] = None) -> dict[str, object]:
    """Project a list of evidence records into one aggregate digest (scalars only)."""
    errors = errors or []
    now = now or _now()

    decision_actions: Counter = Counter()
    safety_status: Counter = Counter()
    modes: Counter = Counter()
    requires_human = 0
    redactions_total = 0
    non_dry_run = 0
    timestamps: list[str] = []
    latest: Optional[dict] = None

    for rec in records:
        decision = rec.get("decision") or {}
        action = _safe_str(decision.get("action")) or "UNKNOWN"
        decision_actions[action] += 1

        status = _safe_str(rec.get("safety_status")) or "UNKNOWN"
        safety_status[status] += 1

        mode = _safe_str(rec.get("mode")) or "UNKNOWN"
        modes[mode] += 1
        if mode != SAFE_MODE:
            non_dry_run += 1

        if bool(rec.get("requires_human", True)):
            requires_human += 1

        red = rec.get("redaction_summary") or {}
        count = red.get("count")
        if isinstance(count, int) and count > 0:
            redactions_total += count

        ts = _safe_str(rec.get("timestamp_utc"))
        if ts:
            timestamps.append(ts)

        # latest = highest timestamp_utc (ISO 8601 sorts lexicographically)
        if latest is None or ts > _safe_str(latest.get("timestamp_utc")):
            latest = {
                "cycle_id": _safe_str(rec.get("cycle_id")),
                "timestamp_utc": ts,
                "decision_action": action,
                "safety_status": status,
                "requires_human": bool(rec.get("requires_human", True)),
            }

    total = len(records)
    blocked_cycles = safety_status.get("BLOCKED", 0)

    if total == 0:
        posture = "NO_EVIDENCE"
    elif non_dry_run == 0 and blocked_cycles == 0:
        posture = "OBSERVE_ONLY_CLEAN"
    else:
        posture = "NEEDS_REVIEW"

    timestamps.sort()
    return {
        "schema": LEDGER_SCHEMA,
        "generated_at_utc": now,
        "evidence_schema": EVIDENCE_SCHEMA,
        "total_cycles": total,
        "first_cycle_utc": timestamps[0] if timestamps else None,
        "last_cycle_utc": timestamps[-1] if timestamps else None,
        "decision_actions": dict(decision_actions),
        "safety_status_counts": dict(safety_status),
        "mode_counts": dict(modes),
        "requires_human_count": requires_human,
        "non_dry_run_count": non_dry_run,
        "blocked_cycle_count": blocked_cycles,
        "redactions_total": redactions_total,
        "latest_cycle": latest,
        "read_errors": list(errors),
        "read_error_count": len(errors),
        "posture": posture,
        "read_only": True,
        "safe_next_action": (
            "Observe-only digest. Human reviews the trend; the ledger advances nothing."
            if posture != "NEEDS_REVIEW"
            else "Review: a cycle was non-DRY_RUN or BLOCKED. Inspect before any protected action."
        ),
    }


def build_ledger(evidence_dir: Optional[Path] = None, *, repo_root: Optional[Path] = None, now: Optional[str] = None) -> dict[str, object]:
    """Load + summarize the evidence directory into a digest. Never mutates source."""
    if evidence_dir is not None:
        target = Path(evidence_dir)
    else:
        base = Path(repo_root) if repo_root else Path.cwd()
        target = base / DEFAULT_SUBDIR
    records, errors = load_evidence_records(target)
    digest = summarize_records(records, errors=errors, now=now)
    digest["evidence_dir"] = str(target)
    return digest


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


def render_markdown(digest: dict) -> str:
    latest = digest.get("latest_cycle") or {}
    lines = [
        "# AI_OS Self-Build Evidence Ledger",
        "",
        f"- generated_at_utc: `{digest.get('generated_at_utc')}`",
        f"- posture: `{digest.get('posture')}`",
        f"- total_cycles: `{digest.get('total_cycles')}`",
        f"- requires_human_count: `{digest.get('requires_human_count')}`",
        f"- non_dry_run_count: `{digest.get('non_dry_run_count')}`",
        f"- blocked_cycle_count: `{digest.get('blocked_cycle_count')}`",
        f"- redactions_total: `{digest.get('redactions_total')}`",
        f"- read_error_count: `{digest.get('read_error_count')}`",
        f"- window: `{digest.get('first_cycle_utc')}` -> `{digest.get('last_cycle_utc')}`",
        "",
        "## Decision actions",
    ]
    for action, count in sorted((digest.get("decision_actions") or {}).items()):
        lines.append(f"- `{action}`: {count}")
    lines.append("")
    lines.append("## Safety status")
    for status, count in sorted((digest.get("safety_status_counts") or {}).items()):
        lines.append(f"- `{status}`: {count}")
    lines.append("")
    lines.append("## Latest cycle")
    lines.append(f"- cycle_id: `{latest.get('cycle_id')}`")
    lines.append(f"- timestamp_utc: `{latest.get('timestamp_utc')}`")
    lines.append(f"- decision_action: `{latest.get('decision_action')}`")
    lines.append(f"- safety_status: `{latest.get('safety_status')}`")
    lines.append("")
    lines.append("_Observe-only digest. No action was taken. No command emitted._")
    return "\n".join(lines) + "\n"


def write_digest(
    digest: dict,
    out_path: Path,
    *,
    write_markdown: bool = True,
    overwrite: bool = False,
) -> dict[str, object]:
    """Atomically write the digest JSON (and optional Markdown). Never overwrites by default."""
    out_path = Path(out_path)
    md_path = out_path.with_suffix(".md")

    if out_path.exists() and not overwrite:
        return {
            "written": False,
            "status": "SKIPPED_EXISTS",
            "json_path": str(out_path),
            "md_path": str(md_path) if md_path.exists() else None,
        }

    _atomic_write_text(out_path, json.dumps(digest, indent=2, sort_keys=True))
    if write_markdown:
        _atomic_write_text(md_path, render_markdown(digest))

    return {
        "written": True,
        "status": "WRITTEN",
        "json_path": str(out_path),
        "md_path": str(md_path) if write_markdown else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate AI_OS self-build cycle evidence into one read-only digest.")
    parser.add_argument("--evidence-dir", default=None, help="directory of <cycle_id>.json evidence records")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", default=None, help="optional digest output path; if omitted, digest is printed only")
    parser.add_argument("--no-markdown", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    digest = build_ledger(
        Path(args.evidence_dir) if args.evidence_dir else None,
        repo_root=Path(args.repo_root),
    )
    if args.out:
        result = write_digest(
            digest,
            Path(args.out),
            write_markdown=not args.no_markdown,
            overwrite=args.overwrite,
        )
        digest["_write_result"] = result
    print(json.dumps(digest, indent=2, sort_keys=True))
    # Exit non-zero only if a cycle needs human review, so a scheduler can surface it.
    return 0 if digest["posture"] != "NEEDS_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
