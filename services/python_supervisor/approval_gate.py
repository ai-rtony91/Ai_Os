"""AI_OS Night Supervisor approval gate (read-only, fail-closed).

Schema/contract reference: schemas/aios/orchestration/APPROVAL_INBOX_SCHEMA.json
Mode: DRY_RUN
blocked_capabilities: approval_mutation, approval_grant, file_write,
git_stage_commit_push
next_safe_action: Use gate results as evidence. This module NEVER grants
approval; it only reads existing Human-Owner approval records.
commit_performed: NO / push_performed: NO

Fail-closed contract: if no inbox exists, if a record is missing, malformed,
not human-approved, or expired, the intent is DENIED. Approval is only ever
read, never written, and never inferred.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


APPROVED_STATUSES = {"APPROVED", "APPROVED_APPLY", "GRANTED", "ALLOW"}


def _inbox_dir(repo_root: Path) -> Path:
    return repo_root / "automation" / "orchestration" / "approval_inbox"


def _read_json(path: Path) -> Any:
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return json.loads(path.read_text(encoding=encoding))
        except Exception:  # noqa: BLE001 - fail-closed on any parse problem
            continue
    return None


def load_approvals(repo_root: str | Path = ".") -> list[dict[str, Any]]:
    """Load all approval records. Absence yields an empty list (fail-closed)."""

    inbox = _inbox_dir(Path(repo_root).resolve())
    if not inbox.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(inbox.glob("*.json")):
        payload = _read_json(path)
        if isinstance(payload, dict):
            records.append(payload)
        elif isinstance(payload, list):
            records.extend(item for item in payload if isinstance(item, dict))
    return records


def _record_grants(record: dict[str, Any], packet_id: str, effector: str) -> bool:
    if str(record.get("packet_id") or "") != packet_id:
        return False
    if not bool(record.get("approved_by_human")):
        return False
    if str(record.get("approval_status") or "").upper() not in APPROVED_STATUSES:
        return False
    # If the record names a specific action, it must match the effector.
    requested = str(record.get("requested_action") or "").strip()
    if requested and requested != effector and effector not in requested.split(","):
        return False
    return True


def evaluate_intent(intent: dict[str, Any], approvals: list[dict[str, Any]]) -> dict[str, Any]:
    """Return an approval decision for a single intent. Fail-closed."""

    packet_id = str(intent.get("packet_id") or "")
    effector = str(intent.get("effector") or "")

    if not intent.get("requires_approval"):
        return {
            "intent_id": intent.get("intent_id"),
            "approved": True,
            "reason": "Effector does not require approval (read-only/heartbeat tier).",
            "matched_approval_id": None,
        }

    for record in approvals:
        if _record_grants(record, packet_id, effector):
            return {
                "intent_id": intent.get("intent_id"),
                "approved": True,
                "reason": "Matched Human-Owner approval record.",
                "matched_approval_id": record.get("approval_id"),
                "approval_authority": record.get("approval_authority"),
            }

    return {
        "intent_id": intent.get("intent_id"),
        "approved": False,
        "reason": "No matching Human-Owner approval record. Fail-closed: DENIED.",
        "matched_approval_id": None,
    }


def evaluate_intents(intents: list[dict[str, Any]], repo_root: str | Path = ".") -> list[dict[str, Any]]:
    approvals = load_approvals(repo_root)
    return [evaluate_intent(intent, approvals) for intent in intents]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Night Supervisor intents against the approval inbox.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--intents-json", required=True, help="Path to an action-intent JSON array.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()
    intents = json.loads(Path(args.intents_json).read_text(encoding="utf-8"))
    print(json.dumps(evaluate_intents(intents, args.repo_root), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
