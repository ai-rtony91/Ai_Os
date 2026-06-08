"""One-shot AI_OS operator-relief loop.

This v1 loop collects repo state, classifies blockers, records evidence, writes
approval items only when human action is needed, emits local notifications only
for human-needed events, prints a next safe action, and exits.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .approval_queue import build_approval_item, write_approval_item
from .evidence_ledger import append_evidence
from .notification_gate import emit_notification, should_notify
from .packet_builder import build_packet_draft
from .repo_state import collect_repo_state
from .task_classifier import classify_state


def run_once(repo_root: Path | None = None, send_adb_sos: bool = False) -> dict[str, object]:
    repo_state = collect_repo_state(repo_root)
    classification = classify_state(repo_state)
    packet_draft = build_packet_draft(repo_state)
    evidence = {
        "event": "operator_relief_loop",
        "repo_state": repo_state.to_dict(),
        "classification": classification,
        "packet_draft": packet_draft,
        "copy_paste_reduction": {
            "manual_repo_status_copy_removed": True,
            "manual_next_action_prompt_removed": True,
            "manual_packet_context_copy_removed": True,
        },
    }
    evidence_path = append_evidence(evidence)

    approval_path = None
    if classification["approval_needed"]:
        item = build_approval_item(
            reason="; ".join(classification["reasons"]) or classification["classification"],
            risk_level="medium",
            recommended_action=classification["safe_next_action"],
            source_evidence={"ledger_path": str(evidence_path), "classification": classification},
        )
        approval_path = write_approval_item(item)

    notification_path = None
    if should_notify(classification):
        notification_path = emit_notification(classification, send_adb_sos_enabled=send_adb_sos)

    return {
        "repo_state": repo_state.to_dict(),
        "classification": classification,
        "evidence_path": str(evidence_path),
        "approval_path": str(approval_path) if approval_path else None,
        "notification_path": str(notification_path) if notification_path else None,
        "adb_sos_enabled": send_adb_sos,
        "packet_draft_executable": packet_draft["executable"],
        "executable": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the one-shot AI_OS operator-relief loop.")
    parser.add_argument(
        "--send-adb-sos",
        action="store_true",
        help="Send the existing Android ADB SOS wake notification only when human attention is required.",
    )
    args = parser.parse_args()
    result = run_once(send_adb_sos=args.send_adb_sos)
    print("AI_OS Operator Relief Closed Loop v1")
    print("Mode: LOCAL_REPO_WORKFLOW_ONLY")
    print("Codex call: disabled")
    print("OpenAI API call: disabled")
    print(f"ADB SOS wake: {'enabled' if args.send_adb_sos else 'disabled'}")
    print("Auto-commit: disabled")
    print("Auto-push: disabled")
    print("Next safe action: " + result["classification"]["safe_next_action"])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
