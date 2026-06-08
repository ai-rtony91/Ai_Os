from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.orchestration.dispatcher.assignment_executor import sample_report


def sample_check() -> dict[str, object]:
    report = sample_report()
    failures: list[str] = []
    zero_launch = report.get("zero_launch_confirmation")
    if not isinstance(zero_launch, dict) or zero_launch.get("zero_workers_launched") is not True:
        failures.append("sample report does not confirm zero worker launch")
    previews = report.get("dispatch_packet_previews", [])
    packet_drafts = report.get("packet_drafts", [])
    walkie_events = report.get("internal_walkie_events", [])
    active_state_contracts = report.get("active_state_contracts", {})
    pr_backlog_state = report.get("pr_backlog_state", {})
    queue_contract = active_state_contracts.get("queue", {})
    lock_contract = active_state_contracts.get("locks", {})
    approval_contract = active_state_contracts.get("approval", {})
    worker_inbox_contract = active_state_contracts.get("worker_inbox", {})
    work_packet_contract = active_state_contracts.get("work_packets", {})
    if not active_state_contracts:
        failures.append("sample report did not include active-state contract fields")
    if queue_contract.get("historical_queue_treatment") != "HISTORICAL_REFERENCE":
        failures.append("historical queue contract was not HISTORICAL_REFERENCE")
    if work_packet_contract.get("proposed_backlog_contract") != "PROPOSED_BACKLOG":
        failures.append("proposed backlog contract was not PROPOSED_BACKLOG")
    if lock_contract.get("contract_status") != "EMPTY_ACTIVE_REGISTRY":
        failures.append("empty lock registry was not EMPTY_ACTIVE_REGISTRY")
    if approval_contract.get("approval_contract") != "EVIDENCE_ONLY":
        failures.append("approval inbox contract was not EVIDENCE_ONLY")
    if worker_inbox_contract.get("completed_items_are_active") is not False:
        failures.append("completed worker inbox items were treated as active")
    if active_state_contracts.get("validator_pass_is_approval") is not False:
        failures.append("validator PASS was treated as approval")
    if active_state_contracts.get("github_check_pass_is_approval") is not False:
        failures.append("GitHub check PASS was treated as approval")
    if active_state_contracts.get("dispatcher_preview_is_approval") is not False:
        failures.append("dispatcher preview was treated as approval")
    if not pr_backlog_state:
        failures.append("sample report did not include PR backlog section")
    if pr_backlog_state.get("status") != "UNKNOWN":
        failures.append("missing sample PR backlog should be PR_UNKNOWN/UNKNOWN")
    if pr_backlog_state.get("fixture_mode_deterministic") is not True:
        failures.append("PR backlog fixture mode was not deterministic")
    if pr_backlog_state.get("merge_approved") is not False:
        failures.append("PR backlog state inferred merge approval")
    if pr_backlog_state.get("apply_approved") is not False:
        failures.append("PR backlog state inferred APPLY approval")
    if pr_backlog_state.get("worker_launch_approved") is not False:
        failures.append("PR backlog state inferred worker launch approval")
    if not previews:
        failures.append("sample report did not produce a dispatch packet preview")
    if not packet_drafts:
        failures.append("sample report did not produce packet drafts")
    for preview in previews:
        if preview.get("contains_execution_token") is not False:
            failures.append("dispatch preview contains execution token")
        if preview.get("apply_execution_approved") is not False:
            failures.append("dispatch preview implies APPLY approval")
        if preview.get("worker_launch_approved") is not False:
            failures.append("dispatch preview implies worker launch approval")
    for draft in packet_drafts:
        if not draft.get("status"):
            failures.append("packet draft missing status")
        if draft.get("not_executable_until_operator_approval") is not True:
            failures.append("packet draft is executable without operator approval")
        if draft.get("zero_launch_confirmation", {}).get("zero_workers_launched") is not True:
            failures.append("packet draft does not confirm zero worker launch")
        if draft.get("apply_approved") is not False:
            failures.append("packet draft approves APPLY")
        if draft.get("merge_approved") is not False:
            failures.append("packet draft approves merge")
        if draft.get("push_approved") is not False:
            failures.append("packet draft approves push")
        if draft.get("direct_anthony_wake_approved") is not False:
            failures.append("packet draft directly wakes Anthony")
        if draft.get("worker_launch_approved") is not False:
            failures.append("packet draft approves worker launch")
        if not draft.get("source_dispatch_decision_id") or not draft.get("source_candidate_id"):
            failures.append("packet draft does not reference source decision/candidate")
        draft_text = str(draft.get("draft_text") or "")
        if "CODEX-ONLY PROMPT" not in draft_text:
            failures.append("packet draft text missing CODEX marker")
        if "DRAFT_ONLY_NOT_OPERATOR_APPROVAL" not in draft_text:
            failures.append("packet draft text missing draft-only token")
        if "This draft is not executable until Anthony approves it." not in draft_text:
            failures.append("packet draft text missing operator approval notice")
    if not walkie_events:
        failures.append("sample report did not produce internal walkie events")
    for event in walkie_events:
        if event.get("zero_external_wake_confirmation") is not True:
            failures.append("walkie event does not confirm zero external wake")
        if event.get("zero_worker_launch_confirmation") is not True:
            failures.append("walkie event does not confirm zero worker launch")
        if "direct_anthony_wake" not in event.get("blocked_actions", []):
            failures.append("walkie event does not block direct Anthony wake")
        if event.get("severity") == "SOS_CANDIDATE" and event.get("route_to") != ["watchdog_pi5_review"]:
            failures.append("SOS candidate event must route only to Watchdog/Pi5 review")
        if event.get("candidate_id") == "dry-run-next" and event.get("event_type") != "DRY_RUN_ONLY":
            failures.append("DRY_RUN_ONLY candidate did not emit DRY_RUN_ONLY walkie event")
        if event.get("event_type") == "PR_DEPENDENCY_CHANGED" and event.get("zero_external_wake_confirmation") is not True:
            failures.append("PR dependency walkie event was not preview-only")
    approval_state = report.get("approval_state", {})
    if approval_state.get("future_apply_approved") is not False:
        failures.append("completed/pending approval state was treated as future APPLY approval")
    if report.get("lock_state", {}).get("classification") != "NO_ACTIVE_LOCKS":
        failures.append("empty lock registry was not classified as NO_ACTIVE_LOCKS")
    if report.get("queue_state", {}).get("historical_queue_treatment") != "HISTORICAL_REFERENCE":
        failures.append("historical dispatcher queue was not treated as reference")
    return {
        "validator": "aios_worker_dispatcher_assignment_executor_validator",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "safe_next_action": "Use assignment executor output as DRY_RUN preview only." if not failures else "Repair assignment executor sample behavior.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI_OS worker dispatcher assignment executor sample behavior.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.sample_check:
        payload = {"status": "BLOCKED", "reason": "--sample-check required"}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    payload = sample_check()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['validator']}: {payload['status']}")
        for failure in payload["failures"]:
            print(f"FAIL: {failure}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
