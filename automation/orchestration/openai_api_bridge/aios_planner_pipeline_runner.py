#!/usr/bin/env python3
"""Local-only AI_OS OpenAI planner pipeline simulator.

This runner uses only Python standard library modules. It does not read
secrets, read .env files, install packages, use network access, call OpenAI,
or mutate runtime state.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPO_ROOT / "docs/AI_OS/openai_api_bridge/fixtures/PIPELINE_GOAL_INPUT_001.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/AI_OS/openai_api_bridge/pipeline_outputs"

ALLOWED_WRITE_ROOTS = [
    (REPO_ROOT / "docs/AI_OS/openai_api_bridge").resolve(),
    (REPO_ROOT / "automation/orchestration/openai_api_bridge").resolve(),
]

REQUIRED_INPUT_FIELDS = [
    "goal_id",
    "goal_text",
    "requested_phase",
    "requested_mode",
    "autonomy_level",
    "allowed_paths",
    "forbidden_paths",
    "human_approval_required",
    "live_openai_api_call_allowed",
    "api_key_allowed",
    "network_allowed",
    "package_install_allowed",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
    "live_trading_status",
    "broker_execution_status",
    "oanda_status",
    "stop_point",
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
    r"\bforce push\b",
    r"\brebase\b",
    r"\bnight supervisor runtime write\b",
    r"\btelemetry runtime write\b",
    r"\bapproval inbox runtime write\b",
]

SAFETY_DECLARATION_FIELDS = {
    "allowed_paths",
    "forbidden_paths",
    "human_approval_required",
    "live_openai_api_call_allowed",
    "api_key_allowed",
    "network_allowed",
    "package_install_allowed",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
    "live_trading_status",
    "broker_execution_status",
    "oanda_status",
    "stop_point",
}


class PipelineFailure(RuntimeError):
    """Raised when pipeline validation fails."""


def repo_path(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def assert_allowed_write(path: Path) -> None:
    resolved = path.resolve()
    if not any(resolved == root or root in resolved.parents for root in ALLOWED_WRITE_ROOTS):
        raise PipelineFailure(f"Forbidden write path: {path}")


def load_goal(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise PipelineFailure("Pipeline input must be a JSON object.")
    missing = [field for field in REQUIRED_INPUT_FIELDS if field not in data]
    if missing:
        raise PipelineFailure("Missing required input fields: " + ", ".join(missing))
    return data


def iter_request_strings(value: Any, path: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    if path and path[-1] in SAFETY_DECLARATION_FIELDS:
        return []
    if isinstance(value, str):
        return [(".".join(path) or "$", value)]
    if isinstance(value, list):
        found: list[tuple[str, str]] = []
        for index, item in enumerate(value):
            found.extend(iter_request_strings(item, path + (str(index),)))
        return found
    if isinstance(value, dict):
        found = []
        for key, item in value.items():
            found.extend(iter_request_strings(item, path + (str(key),)))
        return found
    return []


def scan_goal_for_blocked_requests(data: dict[str, Any]) -> None:
    matches: list[str] = []
    for path, text in iter_request_strings(data):
        lowered = text.lower()
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, lowered):
                matches.append(f"{path}: {pattern}")
    if matches:
        raise PipelineFailure("Blocked request text found: " + "; ".join(matches))


def validate_risky_flags(data: dict[str, Any]) -> None:
    expected = {
        "live_openai_api_call_allowed": False,
        "api_key_allowed": False,
        "network_allowed": False,
        "package_install_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "merge_allowed": False,
        "live_trading_status": "BLOCKED",
        "broker_execution_status": "BLOCKED",
        "oanda_status": "BLOCKED",
    }
    failures = [
        f"{field} expected {expected_value!r}, got {data.get(field)!r}"
        for field, expected_value in expected.items()
        if data.get(field) != expected_value
    ]
    if failures:
        raise PipelineFailure("Risky input flags failed: " + "; ".join(failures))


def build_pipeline(data: dict[str, Any]) -> dict[str, Any]:
    packet_id = "AIOS-P16-PIPELINE-CODEX-PACKET-DRAFT-001"
    allowed_paths = data["allowed_paths"]
    forbidden_paths = data["forbidden_paths"]
    planner = {
        "goal_id": data["goal_id"],
        "planner_status": "PASS",
        "interpreted_goal": "Draft a Codex-safe packet that checks repo status, proposes the next validator, and stops before APPLY.",
        "safety_classification": "SAFE_LOCAL_ONLY",
        "autonomy_level": data["autonomy_level"],
        "local_fixture_only": True,
        "live_openai_api_call": False,
        "api_key_required": False,
        "network_required": False,
        "package_install_required": False,
        "recommended_packet_id": packet_id,
        "blocked_actions": [
            "APPLY",
            "commit",
            "push",
            "merge",
            "force push",
            "rebase",
            "live OpenAI API call",
            "API key",
            "network call",
            "package install",
            "broker",
            "OANDA",
            "live trading",
        ],
        "recommended_next_action": "Review the generated Codex packet draft and keep it DRAFT_ONLY until a separate human-approved packet is issued.",
    }
    packet_md = f"""🧩 CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: DRAFT_ONLY_DO_NOT_EXECUTE

TITLE
AI_OS Phase 16 Pipeline Draft - Repo Status Validator Packet

LANE
DRY_RUN validation lane

WORKTREE
C:\\Dev\\Ai.Os

BRANCH
main

MISSION
Check repo status, propose the next validator, and stop before APPLY.

DRAFT_ONLY
NO_APPLY_AUTHORITY
NO_COMMIT
NO_PUSH
NO_MERGE
NO_LIVE_API_CALL

PRECHECK
1. Run git status --short --branch.
2. Confirm branch is main.
3. Confirm working tree is clean.

ALLOWED PATHS
- docs/AI_OS/openai_api_bridge/
- automation/orchestration/openai_api_bridge/

FORBIDDEN PATHS
- telemetry/
- control/
- automation/orchestration/locks/
- automation/orchestration/approval_inbox/
- automation/orchestration/memory/
- automation/orchestration/night_supervisor/
- broker files
- OANDA files
- live trading files
- secret files
- .env files

HARD BLOCKS
- Do not use API keys.
- Do not call OpenAI.
- Do not install packages.
- Do not make network calls.
- Do not APPLY.
- Do not commit.
- Do not push.
- Do not merge.

VALIDATION CHAIN
- git_clean_state
- allowed_paths
- blocked_paths
- validate_only_runner
- json_integrity
- no_secrets
- no_network
- no_live_trading_enablement
- final_git_status

STOP POINT
Stop after reporting validator recommendation. Do not APPLY.

FINAL REPORT FORMAT
AI_OS DRAFT PACKET RESULT
1. Precheck: PASS/FAIL
2. Validator recommendation: [text]
3. Forbidden paths touched: YES/NO
4. Commit/push/merge performed: YES/NO
5. Final git status: [exact output]
"""
    worker = {
        "packet_id": packet_id,
        "recommended_worker_lane": "DRY_RUN validation lane",
        "worker_type": "Codex",
        "branch_strategy": "Use current clean main for read-only validation; use PR lane only after approved changes.",
        "worktree_strategy": "Use C:\\Dev\\Ai.Os only; no temporary worktree required for read-only preview.",
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "collision_risk": "LOW",
        "night_supervisor_interference_check": "PASS",
        "requires_human_start": True,
        "requires_human_approval": True,
    }
    validator = {
        "packet_id": packet_id,
        "validator_chain": [
            "git_clean_state",
            "allowed_paths",
            "blocked_paths",
            "validate_only_runner",
            "json_integrity",
            "no_secrets",
            "no_network",
            "no_live_trading_enablement",
            "final_git_status",
        ],
        "required_checks": [
            "git status --short --branch",
            "PowerShell wrapper -ValidateOnly",
            "JSON parse validation",
            "forbidden path scan",
            "secret scan",
            "network/OpenAI call scan",
            "trading safety scan",
        ],
        "json_validation_required": True,
        "validate_only_required": True,
        "dirty_tree_check_required": True,
        "forbidden_path_check_required": True,
        "secret_check_required": True,
        "network_check_required": True,
        "trading_safety_check_required": True,
        "expected_pass_condition": "Validate-only runner passes, JSON parses, tree remains clean, and no forbidden scope is touched.",
    }
    approval = {
        "approval_id": "APPROVAL_PREVIEW_P16_PIPELINE_001",
        "packet_id": packet_id,
        "approval_status": "PREVIEW_ONLY",
        "human_approval_required": True,
        "allowed_decisions": ["approve future DRY_RUN", "request changes", "reject"],
        "blocked_decisions": ["auto APPLY", "auto commit", "auto push", "auto merge", "runtime approval mutation"],
        "required_evidence": ["clean git status", "validated JSON", "forbidden path scan", "no-secret scan", "no-network scan"],
        "expiration_policy": "Preview expires when branch, file scope, or validation evidence changes.",
        "runtime_write_status": "BLOCKED",
    }
    commit = {
        "commit_package_id": "COMMIT_PACKAGE_PREVIEW_P16_PIPELINE_001",
        "packet_id": packet_id,
        "commit_allowed": False,
        "suggested_commit_message": "docs(aios): add OpenAI planner pipeline preview",
        "allowed_files_preview": allowed_paths,
        "forbidden_files_preview": forbidden_paths,
        "git_add_dot_allowed": False,
        "requires_human_commit_approval": True,
        "push_allowed": False,
    }
    clean = {
        "verifier_id": "CLEAN_STATE_VERIFIER_PREVIEW_P16_PIPELINE_001",
        "packet_id": packet_id,
        "required_git_status": "git status --short --branch",
        "expected_clean_status": "No modified, staged, or untracked files outside the approved packet scope.",
        "dirty_file_policy": "Block if unexpected dirty files exist.",
        "untracked_file_policy": "Allow only explicitly approved new files in allowed paths.",
        "forbidden_path_policy": "Block any touched forbidden path.",
        "final_sync_policy": "After approved PR merge only, sync local main to origin/main.",
        "pass_fail_logic": "PASS only when branch, status, path scope, JSON, secret, network, and trading checks pass.",
    }
    return {
        "planner": planner,
        "packet_md": packet_md,
        "worker": worker,
        "validator": validator,
        "approval": approval,
        "commit": commit,
        "clean": clean,
    }


def validate_pipeline_outputs(outputs: dict[str, Any]) -> None:
    planner = outputs["planner"]
    expected = {
        "local_fixture_only": True,
        "live_openai_api_call": False,
        "api_key_required": False,
        "network_required": False,
        "package_install_required": False,
    }
    failures = [
        f"planner.{field} expected {expected_value!r}, got {planner.get(field)!r}"
        for field, expected_value in expected.items()
        if planner.get(field) != expected_value
    ]
    if outputs["commit"].get("commit_allowed") is not False:
        failures.append("commit.commit_allowed must be false")
    if outputs["commit"].get("push_allowed") is not False:
        failures.append("commit.push_allowed must be false")
    if outputs["approval"].get("runtime_write_status") != "BLOCKED":
        failures.append("approval.runtime_write_status must be BLOCKED")
    if outputs["worker"].get("night_supervisor_interference_check") != "PASS":
        failures.append("worker.night_supervisor_interference_check must be PASS")
    if failures:
        raise PipelineFailure("Pipeline output validation failed: " + "; ".join(failures))


def write_json(path: Path, data: dict[str, Any]) -> None:
    assert_allowed_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    assert_allowed_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_outputs(output_dir: Path, outputs: dict[str, Any]) -> None:
    assert_allowed_write(output_dir)
    files = {
        "PIPELINE_PLANNER_RESULT_001.json": outputs["planner"],
        "WORKER_ASSIGNMENT_PREVIEW_001.json": outputs["worker"],
        "VALIDATOR_CHAIN_PREVIEW_001.json": outputs["validator"],
        "APPROVAL_INBOX_PREVIEW_001.json": outputs["approval"],
        "COMMIT_PACKAGE_PREVIEW_001.json": outputs["commit"],
        "CLEAN_STATE_VERIFIER_PREVIEW_001.json": outputs["clean"],
    }
    for name, data in files.items():
        write_json(output_dir / name, data)
    write_text(output_dir / "CODEX_PACKET_DRAFT_001.md", outputs["packet_md"])
    report = """# Full Pipeline Lifecycle Report 001

Status: PASS
Mode: DRY_RUN
Local fixture only: YES

## Stages Simulated

- 16.4 Planner -> Packet Generator
- 16.5 Packet Generator -> Worker Assignment
- 16.6 Worker Assignment -> Validator Chain
- 16.7 Validator Chain -> Approval Inbox preview
- 16.8 Approval Inbox -> Commit Package preview
- 16.9 Commit Package -> Clean-State Verifier preview
- 16.10 Real OpenAI API Adapter boundary

## What Was Simulated

A fake local goal was converted into a planner result, Codex packet draft, worker assignment preview, validator chain preview, approval preview, commit package preview, and clean-state verifier preview.

## What Remains Blocked

Real OpenAI API calls, API keys, package installs, network access, runtime autonomy, approval inbox writes, telemetry writes, commits, pushes, merges, broker execution, OANDA, live trading, real orders, and webhook execution remain blocked.

## Why Real OpenAI API Is Not Enabled Yet

The current layer proves the AI_OS packet lifecycle with deterministic local fixtures. A real adapter still needs separate human approval, environment-variable-only configuration, redaction, timeout, retry, audit, no-write validation, and fail-closed behavior.

## Copy-Paste Reduction

The pipeline turns one goal into the complete packet lifecycle preview. Later, this reduces manual relay work by producing the packet, worker, validator, approval, commit, and clean-state artifacts together.

## Next Safe Stage

Review these outputs. The next safe stage is a commit packet for this DRY_RUN Big Pack, or a fix packet if validation finds gaps.
"""
    write_text(output_dir / "FULL_PIPELINE_LIFECYCLE_REPORT_001.md", report)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local AI_OS planner pipeline preview.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input goal fixture path.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory.")
    parser.add_argument("--validate-only", action="store_true", help="Validate without writing files.")
    parser.add_argument("--dry-run", action="store_true", help="Explicit DRY_RUN mode.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        input_path = repo_path(args.input)
        output_dir = repo_path(args.output_dir)
        data = load_goal(input_path)
        validate_risky_flags(data)
        scan_goal_for_blocked_requests(data)
        outputs = build_pipeline(data)
        validate_pipeline_outputs(outputs)
        if args.validate_only:
            print("AIOS_PLANNER_PIPELINE_VALIDATE_ONLY: PASS")
            print("NO_OUTPUT_FILES_WRITTEN")
            return 0
        write_outputs(output_dir, outputs)
        print("AIOS_PLANNER_PIPELINE_RESULT: PASS")
        print(f"OUTPUT_DIR: {output_dir.relative_to(REPO_ROOT).as_posix()}")
        return 0
    except (OSError, json.JSONDecodeError, PipelineFailure) as exc:
        print("AIOS_PLANNER_PIPELINE_RESULT: FAIL", file=sys.stderr)
        print(f"Reason: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
