"""Run the local safe Forex Completion Campaign Part 3 manifest check."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_completion_campaign_part3_owner_validation_and_pr_landing_v1 import (  # noqa: E402
    HARD_FALSE_FIELDS,
    PART1_FILES,
    PART2_FILES,
    PART3_FILES,
    evaluate_forex_completion_campaign_part3_owner_validation_and_pr_landing_v1,
)


VALIDATOR_NAMES = (
    "part3_module_py_compile",
    "part3_runner_py_compile",
    "part3_focused_tests",
    "part1_focused_tests",
    "part2_protected_runtime_tests",
    "part2_credential_bridge_tests",
    "part2_post_execution_review_tests",
    "part2_22h6d_readiness_tests",
    "part2_completion_tests",
    "part2_runner",
    "part3_runner",
    "existing_runtime_dry_run_regression",
    "existing_owner_runtime_transport_regression",
    "existing_broker_adapter_binding_regression",
    "existing_capital_program_regression",
    "forbidden_marker_scan",
    "diff_whitespace_validation",
)


def _path_manifest(paths: tuple[str, ...]) -> dict[str, bool]:
    return {path: (ROOT / path).exists() for path in paths}


def build_payload() -> dict:
    return {
        "part1_files": _path_manifest(PART1_FILES),
        "part2_files": _path_manifest(PART2_FILES),
        "part3_files": _path_manifest(PART3_FILES),
        "validation_results": {
            name: "UNKNOWN_NOT_RUN_BY_SCRIPT" for name in VALIDATOR_NAMES
        },
        "dirty_state": {
            "branch": "main",
            "same_mission_untracked_only": True,
            "unrelated_dirty_files_present": False,
            "staged_files_present": False,
        },
        "safety_boundary": {field: False for field in HARD_FALSE_FIELDS},
        "owner_validation": {
            "owner_review_required": True,
            "commit_approval_required": True,
            "push_approval_required": True,
            "pr_approval_required": True,
            "merge_approval_required": True,
            "owner_has_not_approved_commit_yet": True,
        },
    }


def main() -> int:
    result = (
        evaluate_forex_completion_campaign_part3_owner_validation_and_pr_landing_v1(
            build_payload()
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("schema") and result.get("landing_status") else 1


if __name__ == "__main__":
    raise SystemExit(main())
