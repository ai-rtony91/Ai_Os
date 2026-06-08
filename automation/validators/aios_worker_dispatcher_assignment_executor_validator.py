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
    if not previews:
        failures.append("sample report did not produce a dispatch packet preview")
    for preview in previews:
        if preview.get("contains_execution_token") is not False:
            failures.append("dispatch preview contains execution token")
        if preview.get("apply_execution_approved") is not False:
            failures.append("dispatch preview implies APPLY approval")
        if preview.get("worker_launch_approved") is not False:
            failures.append("dispatch preview implies worker launch approval")
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
