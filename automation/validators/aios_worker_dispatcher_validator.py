from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.orchestration.dispatcher.control_plane import (
    build_dispatch_preview,
    sample_assignments,
    sample_registry,
    sample_task,
    validate_control_plane,
)


def sample_check(repo_root: Path) -> dict[str, object]:
    registry = sample_registry()
    assignments = sample_assignments()
    validation = validate_control_plane(registry, assignments, repo_root)
    preview = build_dispatch_preview(registry, assignments, sample_task())
    failures: list[str] = []
    if validation["status"] != "PASS":
        failures.append("valid dispatcher sample did not pass")
    if preview["dispatch_packet"]["contains_execution_token"] is not False:
        failures.append("dispatch packet sample is executable")
    if preview["dispatch_packet"]["apply_execution_approved"] is not False:
        failures.append("dispatch packet sample implies APPLY approval")
    return {
        "validator": "aios_worker_dispatcher_validator",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "sample_validation": validation,
        "sample_preview": preview,
        "safe_next_action": "Use dispatcher output as read-only preview only." if not failures else "Repair dispatcher samples.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI_OS worker dispatcher control-plane safety.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.sample_check:
        payload = {"status": "BLOCKED", "reason": "--sample-check required"}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    payload = sample_check(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['validator']}: {payload['status']}")
        for failure in payload["failures"]:
            print(f"FAIL: {failure}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
