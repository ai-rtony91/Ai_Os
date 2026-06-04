#!/usr/bin/env python3
"""Local-only OpenAI planner fixture runner for AI_OS.

This runner intentionally does not use provider SDKs, read secrets, read .env
files, install packages, or make network calls.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = REPO_ROOT / "docs/AI_OS/openai_api_bridge/fixtures/PLANNER_INPUT_EXAMPLE_001.json"
OUTPUT_DIR = REPO_ROOT / "docs/AI_OS/openai_api_bridge/runner_outputs"
OUTPUT_JSON = OUTPUT_DIR / "PLANNER_RUN_OUTPUT_001.json"
OUTPUT_REPORT = OUTPUT_DIR / "PLANNER_RUN_REPORT_001.md"

ALLOWED_WRITE_ROOTS = [
    (REPO_ROOT / "docs/AI_OS/openai_api_bridge").resolve(),
    (REPO_ROOT / "automation/orchestration/openai_api_bridge").resolve(),
]

REQUIRED_FIELDS = [
    "mode",
    "autonomy_level",
    "allowed_paths",
    "forbidden_paths",
    "requires_human_approval",
    "live_trading_status",
    "broker_execution_status",
    "secret_handling_status",
    "validator_chain",
    "stop_point",
    "recommended_next_action",
]

BLOCKED_PATTERNS = [
    r"\bapi key\b",
    r"\.env",
    r"\blive openai call\b",
    r"\bnetwork call\b",
    r"\bpackage install\b",
    r"\bbroker\b",
    r"\boanda\b",
    r"\blive trading\b",
    r"\breal order\b",
    r"\bwebhook execution\b",
    r"\bcommit\b",
    r"\bpush\b",
    r"\bmerge\b",
    r"\bnight supervisor runtime write\b",
]

# Safety declaration fields are allowed to name blocked concepts so the fixture
# can state what is forbidden without being treated as a request to do it.
SAFETY_DECLARATION_FIELDS = {
    "allowed_paths",
    "forbidden_paths",
    "requires_human_approval",
    "live_trading_status",
    "broker_execution_status",
    "secret_handling_status",
    "validator_chain",
    "stop_point",
    "recommended_next_action",
}


class SafetyFailure(RuntimeError):
    """Raised when the fixture requests blocked behavior."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def assert_allowed_write(path: Path) -> None:
    resolved = path.resolve()
    if not any(resolved == root or root in resolved.parents for root in ALLOWED_WRITE_ROOTS):
        raise SafetyFailure(f"Forbidden write path: {path}")


def load_input() -> dict[str, Any]:
    if not INPUT_PATH.is_file():
        raise SafetyFailure(f"Missing input fixture: {INPUT_PATH}")
    with INPUT_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SafetyFailure("Input fixture must be a JSON object.")
    return data


def validate_required_fields(data: dict[str, Any]) -> list[str]:
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise SafetyFailure(f"Missing required safety fields: {', '.join(missing)}")
    return REQUIRED_FIELDS


def iter_policy_request_strings(value: Any, path: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    if path and path[-1] in SAFETY_DECLARATION_FIELDS:
        return []
    if isinstance(value, str):
        return [(".".join(path) or "$", value)]
    if isinstance(value, list):
        found: list[tuple[str, str]] = []
        for index, item in enumerate(value):
            found.extend(iter_policy_request_strings(item, path + (str(index),)))
        return found
    if isinstance(value, dict):
        found = []
        for key, item in value.items():
            found.extend(iter_policy_request_strings(item, path + (str(key),)))
        return found
    return []


def scan_for_blocked_requests(data: dict[str, Any]) -> None:
    matches: list[str] = []
    for path, text in iter_policy_request_strings(data):
        lowered = text.lower()
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, lowered):
                matches.append(f"{path}: {pattern}")
    if matches:
        raise SafetyFailure("Blocked request text found: " + "; ".join(matches))


def build_output(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": "PLANNER_RUN_OUTPUT_001",
        "generated_at_utc": utc_now(),
        "mode": "DRY_RUN",
        "local_fixture_only": True,
        "live_openai_api_call": False,
        "api_key_required": False,
        "package_install_required": False,
        "network_required": False,
        "autonomy_level": data["autonomy_level"],
        "allowed_paths": data["allowed_paths"],
        "forbidden_paths": data["forbidden_paths"],
        "human_approval_required": True,
        "commit_allowed": False,
        "push_allowed": False,
        "live_trading_status": "BLOCKED",
        "broker_execution_status": "BLOCKED",
        "oanda_status": "BLOCKED",
        "night_supervisor_interference_check": "PASS",
        "planner_summary": {
            "input_fixture": str(INPUT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "validated_required_fields": REQUIRED_FIELDS,
            "blocked_request_scan": "PASS",
            "deterministic_output": True,
        },
        "recommended_next_action": (
            "Review the local fixture runner output. A future packet may propose "
            "a non-network adapter preview, but live API calls and secrets remain blocked."
        ),
    }


def validate_output_safety(output: dict[str, Any]) -> None:
    expected = {
        "mode": "DRY_RUN",
        "local_fixture_only": True,
        "live_openai_api_call": False,
        "api_key_required": False,
        "package_install_required": False,
        "network_required": False,
        "human_approval_required": True,
        "commit_allowed": False,
        "push_allowed": False,
        "live_trading_status": "BLOCKED",
        "broker_execution_status": "BLOCKED",
        "oanda_status": "BLOCKED",
        "night_supervisor_interference_check": "PASS",
    }
    failures = [
        f"{field} expected {expected_value!r}, got {output.get(field)!r}"
        for field, expected_value in expected.items()
        if output.get(field) != expected_value
    ]
    if failures:
        raise SafetyFailure("Output safety validation failed: " + "; ".join(failures))


def write_outputs(output: dict[str, Any]) -> None:
    assert_allowed_write(OUTPUT_JSON)
    assert_allowed_write(OUTPUT_REPORT)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")
    report = [
        "# Planner Run Report 001",
        "",
        "Status: PASS",
        "Mode: DRY_RUN",
        "Local fixture only: YES",
        "Live OpenAI API call: NO",
        "API key required: NO",
        "Package install required: NO",
        "Network required: NO",
        "Commit allowed: NO",
        "Push allowed: NO",
        "Live trading status: BLOCKED",
        "Broker execution status: BLOCKED",
        "OANDA status: BLOCKED",
        "Night Supervisor interference check: PASS",
        "",
        "## Output",
        "",
        f"- JSON output: `{OUTPUT_JSON.relative_to(REPO_ROOT).as_posix()}`",
        "",
        "## Recommended Next Action",
        "",
        output["recommended_next_action"],
        "",
    ]
    with OUTPUT_REPORT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(report))


def main() -> int:
    validate_only = "--validate-only" in sys.argv[1:]
    try:
        data = load_input()
        validate_required_fields(data)
        scan_for_blocked_requests(data)
        output = build_output(data)
        validate_output_safety(output)
        if validate_only:
            print("PLANNER_FIXTURE_RUNNER_VALIDATE_ONLY: PASS")
            print("NO_OUTPUT_FILES_WRITTEN")
            return 0
        write_outputs(output)
        print("PLANNER_FIXTURE_RUNNER_RESULT: PASS")
        print(f"OUTPUT_JSON: {OUTPUT_JSON.relative_to(REPO_ROOT).as_posix()}")
        print(f"OUTPUT_REPORT: {OUTPUT_REPORT.relative_to(REPO_ROOT).as_posix()}")
        return 0
    except (OSError, json.JSONDecodeError, SafetyFailure) as exc:
        print("PLANNER_FIXTURE_RUNNER_RESULT: FAIL", file=sys.stderr)
        print(f"Reason: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
