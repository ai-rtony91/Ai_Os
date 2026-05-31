"""AI_OS unified approval projection.

Reads Relay approvals, Operation Glue approvals, and the Python approval queue
projection as source evidence. This module is projection-only: it does not
mutate source stores, approve actions, migrate records, call the network, run
shell commands, stage files, commit, push, or enable trading.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_UNIFIED_APPROVALS.v1"
OUTPUT_PATH = Path("telemetry/approvals/UNIFIED_APPROVALS.json")
STATUS_VALUES = ("WAITING_APPROVAL", "APPROVED", "REJECTED", "BLOCKED")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def read_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError:
        return None


def compact(value: Any, limit: int = 220) -> str:
    return " ".join(str(value or "").split())[:limit]


def normalize_status(value: Any, source_path: str = "", text: str = "") -> str:
    source = f"{value or ''} {source_path} {text}".lower()
    if "/approved/" in source_path.replace("\\", "/").lower():
        return "APPROVED"
    if "/rejected/" in source_path.replace("\\", "/").lower():
        return "REJECTED"
    if any(term in source for term in ("unsafe", "blocked", "blocker", "live order", "buy order", "sell order")):
        return "BLOCKED"
    if any(term in source for term in ("approved", "already_handled")):
        return "APPROVED"
    if "rejected" in source:
        return "REJECTED"
    return "WAITING_APPROVAL"


def extract_markdown_field(text: str, label: str) -> str | None:
    pattern = re.compile(rf"\*\*{re.escape(label)}\s*:\*\*\s*(.+)", re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def stable_key(item: dict[str, Any]) -> str:
    origin = str(item.get("origin_ref") or "").strip().lower().replace("\\", "/")
    source_path = str(item.get("source_path") or "").strip().lower().replace("\\", "/")
    item_id = str(item.get("id") or "").strip().lower()
    if origin:
        return f"origin:{origin}"
    if source_path:
        return f"path:{source_path}"
    return f"id:{item_id}"


def make_item(
    *,
    source_store: str,
    item_id: str,
    title: str,
    status: str,
    risk_level: str | None,
    gate_flags: list[str] | None,
    origin_ref: str | None,
    created_at: str | None,
    decided_at: str | None,
    decided_by: str | None,
    source_path: str,
    summary: str,
) -> dict[str, Any]:
    item = {
        "id": item_id or source_path or "UNKNOWN",
        "source_store": source_store,
        "title": title or item_id or source_path or "Approval Item",
        "status": status if status in STATUS_VALUES else "WAITING_APPROVAL",
        "risk_level": risk_level,
        "gate_flags": gate_flags or [],
        "origin_ref": origin_ref,
        "created_at": created_at,
        "decided_at": decided_at,
        "decided_by": decided_by,
        "source_path": source_path,
        "stable_key": "",
        "summary": summary or "Approval item requires review.",
    }
    item["stable_key"] = stable_key(item)
    return item


def relay_items(repo_root: Path) -> list[dict[str, Any]]:
    approvals_root = repo_root / "relay" / "approvals"
    if not approvals_root.exists():
        return []
    files = sorted(
        path for path in approvals_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}
    )
    items: list[dict[str, Any]] = []
    for path in files:
        rel = repo_relative(path, repo_root)
        text = read_text(path)
        payload = read_json(path) if path.suffix.lower() == ".json" else None
        data = payload if isinstance(payload, dict) else {}
        title = data.get("title") or extract_markdown_field(text, "Title")
        if not title and data.get("id"):
            title = str(data["id"]).replace("_", " ").replace("-", " ").title()
        if not title:
            title = next((line.strip("# ").strip() for line in text.splitlines() if line.strip()), path.stem)
        status = normalize_status(data.get("status"), rel, text)
        risk = data.get("risk") or data.get("risk_level") or extract_markdown_field(text, "Risk level")
        created = data.get("created_at") or extract_markdown_field(text, "Created (UTC)")
        origin = data.get("origin_id") or data.get("source_packet") or data.get("source_handoff") or data.get("packet_id")
        gate_flags = []
        if "approval required" in text.lower() or data.get("packet") == "approval":
            gate_flags.append("HUMAN_APPROVAL_REQUIRED")
        if any(term in f"{json.dumps(data, sort_keys=True)} {text}".lower() for term in ("git ", "commit", "push", "merge")):
            gate_flags.append("PROTECTED_ACTION_GATE_REQUIRED")
        items.append(make_item(
            source_store="relay",
            item_id=str(data.get("id") or path.stem),
            title=str(title),
            status=status,
            risk_level=str(risk) if risk else None,
            gate_flags=gate_flags,
            origin_ref=str(origin) if origin else rel,
            created_at=str(created) if created else None,
            decided_at=str(data.get("decided_at")) if data.get("decided_at") else None,
            decided_by=str(data.get("decided_by")) if data.get("decided_by") else None,
            source_path=rel,
            summary=compact(data.get("reason") or data.get("needs") or data.get("proposed") or text),
        ))
    return items


def glue_items(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / "control" / "operation_glue" / "APPROVAL_INBOX.json"
    payload = read_json(path)
    if not isinstance(payload, dict):
        return []
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    items: list[dict[str, Any]] = []
    rel = repo_relative(path, repo_root)
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        gate_flags = []
        if entry.get("approval_required"):
            gate_flags.append("HUMAN_APPROVAL_REQUIRED")
        if entry.get("protected_action_gate_required"):
            gate_flags.append("PROTECTED_ACTION_GATE_REQUIRED")
        if entry.get("approval_marker_required"):
            gate_flags.append(str(entry["approval_marker_required"]))
        items.append(make_item(
            source_store="glue",
            item_id=str(entry.get("item_id") or entry.get("id") or rel),
            title=str(entry.get("action_type") or entry.get("item_id") or "Operation Glue Approval"),
            status=normalize_status(entry.get("status"), rel, json.dumps(entry, sort_keys=True)),
            risk_level=str(entry.get("risk_level")) if entry.get("risk_level") else None,
            gate_flags=gate_flags,
            origin_ref=str(entry.get("source_packet") or entry.get("source_result") or rel),
            created_at=str(entry.get("created_at") or payload.get("generated_at")) if (entry.get("created_at") or payload.get("generated_at")) else None,
            decided_at=str(entry.get("decided_at")) if entry.get("decided_at") else None,
            decided_by=str(entry.get("decided_by")) if entry.get("decided_by") else None,
            source_path=rel,
            summary=compact(entry.get("reason") or entry.get("next_safe_action") or entry),
        ))
    return items


def python_queue_items(repo_root: Path) -> list[dict[str, Any]]:
    sys.path.insert(0, str((repo_root / "services" / "python_supervisor").resolve()))
    try:
        from approval_queue import build_approval_queue  # type: ignore
    except Exception:
        return []
    state = build_approval_queue(repo_root)
    raw_items = state.get("approval_items") if isinstance(state, dict) else []
    if not isinstance(raw_items, list):
        return []
    items: list[dict[str, Any]] = []
    for entry in raw_items:
        if not isinstance(entry, dict):
            continue
        source_path = str(entry.get("source_path") or "services/python_supervisor/approval_queue.py")
        status = normalize_status(entry.get("status"), source_path, json.dumps(entry, sort_keys=True))
        gate_flags = ["PYTHON_QUEUE_PROJECTION"]
        if entry.get("status") in {"WAITING_REVIEW", "UNSAFE_BLOCKED"}:
            gate_flags.append("HUMAN_APPROVAL_REQUIRED")
        items.append(make_item(
            source_store="python_queue",
            item_id=str(entry.get("id") or source_path),
            title=str(entry.get("title") or entry.get("id") or "Python Queue Approval"),
            status=status,
            risk_level=str(entry.get("risk_level")) if entry.get("risk_level") else None,
            gate_flags=gate_flags,
            origin_ref=source_path,
            created_at=None,
            decided_at=None,
            decided_by=None,
            source_path=source_path,
            summary=compact(entry.get("reason") or entry.get("requested_action") or entry),
        ))
    return items


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = {"relay": 0, "glue": 1, "python_queue": 2}
    status_rank = {"BLOCKED": 0, "WAITING_APPROVAL": 1, "APPROVED": 2, "REJECTED": 3}
    selected: dict[str, dict[str, Any]] = {}
    for item in items:
        key = item["stable_key"]
        current = selected.get(key)
        if current is None:
            selected[key] = item
            continue
        current_score = (status_rank.get(current["status"], 9), priority.get(current["source_store"], 9))
        item_score = (status_rank.get(item["status"], 9), priority.get(item["source_store"], 9))
        if item_score < current_score:
            item = {**item, "related_sources": [current["source_store"], *current.get("related_sources", [])]}
            selected[key] = item
        else:
            current.setdefault("related_sources", []).append(item["source_store"])
    return sorted(selected.values(), key=lambda item: (item["status"], item["stable_key"]))


def counts(items: list[dict[str, Any]]) -> dict[str, int]:
    result = {"waiting": 0, "approved": 0, "rejected": 0, "blocked": 0, "total": len(items)}
    for item in items:
        status = item["status"]
        if status == "WAITING_APPROVAL":
            result["waiting"] += 1
        elif status == "APPROVED":
            result["approved"] += 1
        elif status == "REJECTED":
            result["rejected"] += 1
        elif status == "BLOCKED":
            result["blocked"] += 1
    return result


def build_projection(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    per_store_items = {
        "relay": relay_items(root),
        "glue": glue_items(root),
        "python_queue": python_queue_items(root),
    }
    raw_items = [item for group in per_store_items.values() for item in group]
    unified = dedupe(raw_items)
    return {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "mode": "READ_ONLY_PROJECTION",
        "dedup_key": "origin_ref when present, else source_path, else id; status priority BLOCKED > WAITING_APPROVAL > APPROVED > REJECTED; source priority relay > glue > python_queue.",
        "source_record_counts": {key: len(value) for key, value in per_store_items.items()},
        "per_store_counts": {key: counts(value) for key, value in per_store_items.items()},
        "unified_counts": counts(unified),
        "raw_record_count": len(raw_items),
        "deduped_record_count": len(unified),
        "items": unified,
        "safety_flags": {
            "read_only_source_stores": True,
            "no_migration": True,
            "no_source_store_mutation": True,
            "no_network": True,
            "no_commit": True,
            "no_push": True,
            "no_live_trading": True
        }
    }


def write_projection(repo_root: Path, projection: dict[str, Any], apply: bool) -> dict[str, Any]:
    target = repo_root / OUTPUT_PATH
    if not apply:
        return {"planned_output_paths": [repo_relative(target, repo_root)], "written_output_paths": []}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(projection, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"planned_output_paths": [repo_relative(target, repo_root)], "written_output_paths": [repo_relative(target, repo_root)]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Project unified AI_OS approvals read-only.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Write telemetry/approvals/UNIFIED_APPROVALS.json.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve()
    projection = build_projection(root)
    receipt = write_projection(root, projection, args.apply)
    result = {
        "schema": "AIOS_UNIFIED_APPROVALS_RUN_RECEIPT.v1",
        "mode": "APPLY" if args.apply else "DRY_RUN",
        "status": "PASS",
        **receipt,
        "projection": projection,
    }
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
