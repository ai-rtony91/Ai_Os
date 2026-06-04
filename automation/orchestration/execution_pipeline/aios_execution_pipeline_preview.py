#!/usr/bin/env python3
"""AI_OS Phase 17 local execution pipeline preview runner."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GOAL = REPO_ROOT / "docs/AI_OS/execution_pipeline/fixtures/GOAL_INPUT_EXAMPLE_001.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/AI_OS/execution_pipeline/preview_outputs"
ALLOWED_WRITE_ROOT = (REPO_ROOT / "docs/AI_OS/execution_pipeline").resolve()

REQUIRED_SAFETY_FIELDS = [
    "mode",
    "local_fixture_only",
    "autonomy_level",
    "human_approval_required",
    "allowed_paths",
    "forbidden_paths",
    "stop_point",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
    "live_openai_api_call",
    "api_key_required",
    "network_required",
    "package_install_required",
    "live_trading_status",
    "broker_execution_status",
    "oanda_status",
    "night_supervisor_interference_check",
]

BLOCKED_PATTERNS = [
    r"\breal api key\b",
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
    r"\bforce push\b",
    r"\brebase\b",
    r"\bnight supervisor runtime write\b",
    r"\btelemetry runtime write\b",
    r"\bapproval inbox runtime write\b",
]

SAFETY_DECLARATION_FIELDS = set(REQUIRED_SAFETY_FIELDS)


class PreviewFailure(RuntimeError):
    pass


def repo_path(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def assert_allowed_write(path: Path) -> None:
    resolved = path.resolve()
    if not (resolved == ALLOWED_WRITE_ROOT or ALLOWED_WRITE_ROOT in resolved.parents):
        raise PreviewFailure(f"Forbidden write path: {path}")


def read_goal(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PreviewFailure("Goal fixture must be a JSON object.")
    missing = [field for field in REQUIRED_SAFETY_FIELDS + ["goal_id", "goal_text"] if field not in data]
    if missing:
        raise PreviewFailure("Missing goal fields: " + ", ".join(missing))
    return data


def iter_request_text(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    if path and path[-1] in SAFETY_DECLARATION_FIELDS:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        found: list[str] = []
        for index, item in enumerate(value):
            found.extend(iter_request_text(item, path + (str(index),)))
        return found
    if isinstance(value, dict):
        found = []
        for key, item in value.items():
            found.extend(iter_request_text(item, path + (str(key),)))
        return found
    return []


def validate_safety(data: dict[str, Any]) -> None:
    expected = {
        "local_fixture_only": True,
        "human_approval_required": True,
        "commit_allowed": False,
        "push_allowed": False,
        "merge_allowed": False,
        "live_openai_api_call": False,
        "api_key_required": False,
        "network_required": False,
        "package_install_required": False,
        "live_trading_status": "BLOCKED",
        "broker_execution_status": "BLOCKED",
        "oanda_status": "BLOCKED",
        "night_supervisor_interference_check": "PASS",
    }
    failures = [
        f"{field} expected {expected_value!r}, got {data.get(field)!r}"
        for field, expected_value in expected.items()
        if data.get(field) != expected_value
    ]
    matches: list[str] = []
    for text in iter_request_text(data):
        lowered = text.lower()
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, lowered):
                matches.append(pattern)
    if failures or matches:
        raise PreviewFailure("; ".join(failures + [f"blocked term {m}" for m in matches]))


def base(goal: dict[str, Any]) -> dict[str, Any]:
    return {field: goal[field] for field in REQUIRED_SAFETY_FIELDS}


def build_outputs(goal: dict[str, Any]) -> dict[str, Any | str]:
    packet_id = "PHASE17_PACKET_DRAFT_PREVIEW_001"
    common = base(goal)
    packet_md = """🧩 CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: DRAFT_ONLY_DO_NOT_EXECUTE

TITLE
Phase 17 Draft Packet - Inspect Repo Status

LANE
DRY_RUN validation lane

WORKTREE
C:\\Dev\\Ai.Os

BRANCH
main

MISSION
Inspect repo status and propose the next validation step without APPLY.

PRECHECK
Run git status --short --branch and confirm clean main.

ALLOWED PATHS
- docs/AI_OS/execution_pipeline/
- automation/orchestration/execution_pipeline/
- schemas/aios/execution_pipeline/

FORBIDDEN PATHS
- telemetry/
- control/
- automation/orchestration/locks/
- automation/orchestration/approval_inbox/
- automation/orchestration/memory/
- automation/orchestration/night_supervisor/
- broker/OANDA/live trading files
- secret files
- .env files

HARD BLOCKS
No APPLY, commit, push, merge, API keys, network, package install, broker, OANDA, or live trading.

VALIDATION CHAIN
git_clean_state -> forbidden_path_check -> no_secret_check -> no_network_check -> trading_safety_check -> final_git_status

STOP POINT
Stop after validator recommendation.

FINAL REPORT
Report precheck, validator recommendation, protected actions, and final git status.
"""
    return {
        "PACKET_DRAFT_PREVIEW_001.md": packet_md,
        "WORKER_ASSIGNMENT_PREVIEW_001.json": common | {"packet_id": packet_id, "worker_lane": "DRY_RUN validation lane", "worker_type": "Codex"},
        "VALIDATOR_CHAIN_PREVIEW_001.json": common | {"validator_chain": ["git_clean_state", "forbidden_path_check", "no_secret_check", "no_network_check", "trading_safety_check", "final_git_status"]},
        "APPROVAL_PREVIEW_001.json": common | {"approval_id": "PHASE17_APPROVAL_PREVIEW_001", "approval_status": "PREVIEW_ONLY", "runtime_write_status": "BLOCKED"},
        "COMMIT_PACKAGE_PREVIEW_001.json": common | {"commit_package_id": "PHASE17_COMMIT_PACKAGE_PREVIEW_001", "suggested_commit_message": "feat(aios): add execution pipeline preview"},
        "CLEAN_STATE_VERIFIER_PREVIEW_001.json": common | {"verifier_id": "PHASE17_CLEAN_STATE_VERIFIER_001", "required_git_status": "git status --short --branch"},
        "EXECUTION_SUPERVISOR_STATE_PREVIEW_001.json": common | {"supervisor_state_id": "PHASE17_SUPERVISOR_STATE_001", "packet_state": "draft_preview", "validation_state": "preview_passed", "approval_state": "preview_only", "blocked_state": "none"},
        "FULL_EXECUTION_PIPELINE_PREVIEW_REPORT_001.md": "# Full Execution Pipeline Preview Report 001\n\nStatus: PASS\n\nPhase 17 simulated goal intake, packet generation, worker routing, validator dispatch, approval preview, commit package preview, clean-state verification, and supervisor state.\n\nReal OpenAI API, API keys, package installs, network, runtime autonomy, approval inbox writes, telemetry writes, broker/OANDA/live trading, commit, push, merge, rebase, and force push remain blocked.\n",
    }


def validate_outputs(outputs: dict[str, Any | str]) -> None:
    for name, value in outputs.items():
        if name.endswith(".json"):
            if not isinstance(value, dict):
                raise PreviewFailure(f"{name} must be a JSON object.")
            for field in REQUIRED_SAFETY_FIELDS:
                if field not in value:
                    raise PreviewFailure(f"{name} missing {field}")
            validate_safety(value)


def write_outputs(output_dir: Path, outputs: dict[str, Any | str]) -> None:
    assert_allowed_write(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in outputs.items():
        path = output_dir / name
        assert_allowed_write(path)
        if name.endswith(".json"):
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(str(value), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", default=str(DEFAULT_GOAL))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        goal = read_goal(repo_path(args.goal))
        validate_safety(goal)
        outputs = build_outputs(goal)
        validate_outputs(outputs)
        if args.validate_only:
            print("AIOS_EXECUTION_PIPELINE_VALIDATE_ONLY: PASS")
            print("NO_OUTPUT_FILES_WRITTEN")
            return 0
        write_outputs(repo_path(args.output_dir), outputs)
        print("AIOS_EXECUTION_PIPELINE_PREVIEW: PASS")
        print(f"OUTPUT_DIR: {repo_path(args.output_dir).relative_to(REPO_ROOT).as_posix()}")
        return 0
    except (OSError, json.JSONDecodeError, PreviewFailure) as exc:
        print("AIOS_EXECUTION_PIPELINE_PREVIEW: FAIL", file=sys.stderr)
        print(f"Reason: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
