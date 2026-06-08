"""One-shot AI_OS operator relief core loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from automation.operator_relief.evidence_ledger import append_evidence
    from automation.operator_relief.notification_gate import record_notification_decision
    from automation.operator_relief.packet_builder import build_packet_draft
    from automation.operator_relief.repo_state import collect_repo_state
    from automation.operator_relief.task_classifier import classify_state
else:
    from .evidence_ledger import append_evidence
    from .notification_gate import record_notification_decision
    from .packet_builder import build_packet_draft
    from .repo_state import collect_repo_state
    from .task_classifier import classify_state


def run_once(
    repo_root: Path | None = None,
    evidence_path: Path | str | None = None,
    notification_log_path: Path | str | None = None,
    expected_branch: str | None = None,
    requested_action: str | None = None,
    touched_paths: list[str] | None = None,
    sos_triggers: list[str] | None = None,
) -> dict[str, object]:
    repo_state = collect_repo_state(repo_root)
    classification = classify_state(
        repo_state,
        expected_branch=expected_branch,
        requested_action=requested_action,
        touched_paths=touched_paths,
        sos_triggers=sos_triggers,
    )
    packet_draft = build_packet_draft(repo_state)
    evidence = {
        "event": "operator_relief_one_shot_core",
        "repo_state": repo_state.to_dict(),
        "classification": classification,
        "packet_draft": packet_draft,
        "safety_boundaries": {
            "one_shot_only": True,
            "scheduler_started": False,
            "night_supervisor_started": False,
            "live_sos_sent": False,
            "adb_wake_attempted": False,
            "auto_commit_attempted": False,
            "auto_push_attempted": False,
            "broker_or_live_trading_touched": False,
        },
        "copy_paste_reduction": {
            "repo_status_captured": True,
            "next_safe_action_captured": True,
            "packet_draft_captured": True,
        },
        "executable": False,
    }
    ledger_path = append_evidence(evidence, evidence_path) if evidence_path else append_evidence(evidence)
    notification_path = record_notification_decision(classification, notification_log_path) if notification_log_path else record_notification_decision(classification)

    return {
        "repo_state": repo_state.to_dict(),
        "classification": classification,
        "evidence_path": str(ledger_path),
        "notification_path": str(notification_path) if notification_path else None,
        "packet_draft_executable": packet_draft["executable"],
        "executable": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local one-shot AI_OS operator relief core loop.")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--expected-branch", default=None)
    args = parser.parse_args()

    result = run_once(repo_root=args.repo_root, expected_branch=args.expected_branch)
    print("AI_OS Operator Relief One-Shot Core v1")
    print("Mode: LOCAL_EVIDENCE_ONLY")
    print("Scheduler: disabled")
    print("Night Supervisor: disabled")
    print("Live SOS: disabled")
    print("ADB wake: disabled")
    print("Auto-commit: disabled")
    print("Auto-push: disabled")
    print("Next safe action: " + str(result["classification"]["safe_next_action"]))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
