"""AI_OS Night Supervisor read-only escalation ranking engine.

Schema/contract reference: schemas/aios/orchestration/overnight_supervisor.schema.json
Mode: DRY_RUN
blocked_capabilities: self_repair, approval_mutation, packet_movement,
worker_launch, file_write, telemetry_append, git_stage_commit_push
next_safe_action: Surface ranked escalations to the Human Owner without mutation.
commit_performed: NO / push_performed: NO
"""

from __future__ import annotations

import argparse
import json
from typing import Any


SEVERITY_RANK = {"BLOCKED": 3, "WARNING": 2, "REVIEW": 1}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _add_item(items: list[dict[str, str]], severity: str, trigger: str, evidence: str, next_safe_action: str) -> None:
    items.append(
        {
            "severity": severity if severity in SEVERITY_RANK else "REVIEW",
            "trigger": trigger,
            "evidence": evidence,
            "next_safe_action": next_safe_action,
        }
    )


def build_escalation_items(
    queue_items: list[dict[str, Any]] | None = None,
    *,
    freshness_summary: dict[str, Any] | None = None,
    validator_results: list[dict[str, Any]] | None = None,
    approval_state: dict[str, Any] | None = None,
    commit_package_state: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Build sorted escalation items without changing any source state."""

    items: list[dict[str, str]] = []

    for queue_item in queue_items or []:
        packet_id = str(queue_item.get("packet_id") or "UNKNOWN")
        status = str(queue_item.get("status") or "UNKNOWN").upper()
        if status in {"BLOCKED", "FAILED"}:
            _add_item(
                items,
                "BLOCKED",
                f"packet:{packet_id}",
                str(queue_item.get("status_reason") or f"Packet status is {status}."),
                "Human Owner review required before any mutation.",
            )
        elif status == "STALE":
            _add_item(
                items,
                "WARNING",
                f"packet:{packet_id}",
                "Packet evidence is stale.",
                "Refresh evidence in an approved DRY_RUN collection pass.",
            )
        elif status == "WAITING_APPROVAL":
            _add_item(
                items,
                "REVIEW",
                f"packet:{packet_id}",
                "Packet is waiting for approval.",
                "Surface approval requirement to the Human Owner.",
            )

    if freshness_summary:
        missing = int(freshness_summary.get("missing_count", freshness_summary.get("missing", 0)) or 0)
        stale = int(freshness_summary.get("stale_count", freshness_summary.get("stale", 0)) or 0)
        unknown = int(freshness_summary.get("unknown_count", freshness_summary.get("unknown", 0)) or 0)
        if missing:
            _add_item(items, "WARNING", "freshness:missing", f"{missing} expected evidence source(s) missing.", "Collect or review missing evidence in DRY_RUN mode.")
        if stale:
            _add_item(items, "WARNING", "freshness:stale", f"{stale} evidence source(s) stale.", "Refresh stale evidence before overnight reliance.")
        if unknown:
            _add_item(items, "REVIEW", "freshness:unknown", f"{unknown} evidence source(s) lack timestamps.", "Add timestamped evidence in a follow-on packet.")

    for result in validator_results or []:
        state = str(result.get("state") or result.get("status") or "UNKNOWN").upper()
        validator_id = str(result.get("validator_id") or result.get("id") or "validator")
        if state in {"FAIL", "FAILED", "BLOCKED"}:
            _add_item(items, "BLOCKED", f"validator:{validator_id}", f"Validator state is {state}.", "Resolve validator failure before protected action.")
        elif state in {"WARN", "WARNING"}:
            _add_item(items, "WARNING", f"validator:{validator_id}", "Validator returned warning state.", "Review validator warning before routing work.")
        elif state in {"UNKNOWN", "NOT_RUN"}:
            _add_item(items, "REVIEW", f"validator:{validator_id}", f"Validator state is {state}.", "Run or review validator evidence before relying on result.")

    if approval_state:
        open_count = int(approval_state.get("open_count", approval_state.get("unanswered_count", 0)) or 0)
        if open_count:
            _add_item(items, "REVIEW", "approval:open", f"{open_count} approval item(s) need review.", "Human Owner approval required before mutation.")

    if commit_package_state:
        candidate_count = int(commit_package_state.get("candidate_count", 0) or 0)
        if candidate_count:
            _add_item(items, "REVIEW", "commit_package:candidate", f"{candidate_count} commit package candidate(s) detected.", "Review exact-file package before any staging.")

    return sorted(items, key=lambda item: (-SEVERITY_RANK[item["severity"]], item["trigger"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank AI_OS escalations from supplied DRY_RUN evidence.")
    parser.add_argument("--queue-json", default=None, help="Optional queue item list JSON path.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()
    queue_items = []
    if args.queue_json:
        from pathlib import Path

        queue_items = json.loads(Path(args.queue_json).read_text(encoding="utf-8"))
    print(json.dumps(build_escalation_items(queue_items), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
