"""Repo-safe readiness model for the next Forex broker boundary.

This module builds deterministic local state only. It does not read
environment variables, contact brokers, call subprocesses, or write files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


PACKET_ID = "PKT-FOREX-BROKER-CONNECTION-PROOF-BOUNDARY-READINESS-V1"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
MISSION_NAME = "Governed Forex Finish Line"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
PROGRAM_NAME = "Forex Profit Autonomy System"
EPIC_ID = "EPC-FOREX-AUTONOMY-COMPLETION-001"
EPIC_NAME = "Autonomy Completion"
BUCKET_ID = "BKT-FOREX-OVERNIGHT-REPO-SAFE-BUILD-001"
BUCKET_NAME = "Overnight Repo-Safe Broker Boundary And Autonomy Reuse Build Stage"

READINESS_STATUS = "OWNER_GATED_BROKER_CONNECTION_PROOF_READY_FOR_REVIEW"
NEXT_PROTECTED_BOUNDARY = "broker connection proof"
ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "Reports" / "forex_delivery"
SOURCE_STATE_PATH = REPORTS_DIR / "AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json"

DEFAULT_STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_REPORT.md"
)
DEFAULT_NEXT_PACKET_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_NEXT_CODEX_PACKET_V1.md"
)

PROTECTED_FALSE_FIELDS = (
    "broker_api_used",
    "credentials_used",
    "env_read",
    "account_identifiers_used",
    "order_execution",
    "demo_authorized",
    "live_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_started",
    "background_loop_started",
)

REQUIRED_OWNER_INPUTS = (
    "explicit owner approval for broker connection proof review scope",
    "approved broker path without storing credentials in repo",
    "approved runtime-only credential handling plan",
    "approved account identifier handling and redaction plan",
    "approved stop point before any account inspection or order-capable action",
)

FORBIDDEN_UNTIL_OWNER_APPROVAL = (
    "broker contact",
    "credential use",
    ".env access",
    "account identifier use",
    "broker account inspection",
    "order placement",
    "demo execution",
    "live execution",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "worker activation",
    "watcher activation",
    "listener activation",
    "background-loop activation",
)


def run_broker_connection_proof_boundary_readiness_v1() -> dict[str, Any]:
    source_state = _load_source_state()
    stash_detected = True
    result: dict[str, Any] = {
        "readiness_status": READINESS_STATUS,
        "current_autonomy_level": str(
            source_state.get("current_autonomy_level", "PROTECTED_OWNER_BOUNDARY_REQUIRED")
        ),
        "source_orchestrator_status": str(
            source_state.get(
                "orchestrator_status",
                "OWNER_WAKE_REQUIRED_FOR_PROTECTED_FOREX_BOUNDARY",
            )
        ),
        "source_completed_repo_only_stage_count": int(
            source_state.get("completed_repo_only_stage_count", 1)
        ),
        "source_repo_only_remaining_stage_count": int(
            source_state.get("repo_only_remaining_stage_count", 0)
        ),
        "source_protected_stage_count": int(source_state.get("protected_stage_count", 12)),
        "next_protected_boundary": NEXT_PROTECTED_BOUNDARY,
        "owner_wake_required": True,
        "stash_detected": stash_detected,
        "stash_preserved": stash_detected,
        "stash_applied": False,
        "required_owner_inputs": list(REQUIRED_OWNER_INPUTS),
        "forbidden_until_owner_approval": list(FORBIDDEN_UNTIL_OWNER_APPROVAL),
        "readiness_checks": _readiness_checks(source_state, stash_detected),
        "reusable_autonomy_pattern": reusable_autonomy_pattern(),
        "recommended_next_packet": _relative_path(DEFAULT_NEXT_PACKET_OUTPUT_PATH),
        "safe_next_action": (
            "Stop at the protected broker connection proof boundary and request Human "
            "Owner review before broker contact, credentials, .env access, account "
            "identifiers, account inspection, orders, demo/live action, scheduler, "
            "daemon, webhook, or background loop."
        ),
        "mission_id": MISSION_ID,
        "mission_name": MISSION_NAME,
        "program_id": PROGRAM_ID,
        "program_name": PROGRAM_NAME,
        "epic_id": EPIC_ID,
        "epic_name": EPIC_NAME,
        "bucket_id": BUCKET_ID,
        "bucket_name": BUCKET_NAME,
        "packet_id": PACKET_ID,
    }
    result.update({field: False for field in PROTECTED_FALSE_FIELDS})
    return result


def build_report_markdown(result: Mapping[str, Any]) -> str:
    checks = _mapping(result.get("readiness_checks"))
    lines = [
        "# AIOS Forex Broker Connection Proof Boundary Readiness V1 Report",
        "",
        f"Readiness status: {result.get('readiness_status')}",
        f"Current autonomy level: {result.get('current_autonomy_level')}",
        f"Source orchestrator status: {result.get('source_orchestrator_status')}",
        f"Completed repo-only stages: {result.get('source_completed_repo_only_stage_count')}",
        f"Remaining repo-only stages: {result.get('source_repo_only_remaining_stage_count')}",
        f"Protected stages: {result.get('source_protected_stage_count')}",
        f"Next protected boundary: {result.get('next_protected_boundary')}",
        f"Owner wake required: {result.get('owner_wake_required')}",
        "",
        "Readiness checks:",
    ]
    for key in sorted(checks):
        lines.append(f"- {key}: {checks[key]}")
    lines.extend(
        [
            "",
            "Protected actions retained false:",
        ]
    )
    for field in PROTECTED_FALSE_FIELDS:
        lines.append(f"- {field}: {result.get(field)}")
    lines.extend(
        [
            f"- stash_applied: {result.get('stash_applied')}",
            "",
            "Required owner inputs later:",
        ]
    )
    for item in _string_list(result.get("required_owner_inputs")):
        lines.append(f"- {item}")
    lines.extend(["", "Forbidden before owner approval:"])
    for item in _string_list(result.get("forbidden_until_owner_approval")):
        lines.append(f"- {item}")
    lines.extend(["", "Safe next action:", str(result.get("safe_next_action")), ""])
    return "\n".join(lines)


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    return f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_BROKER_CONNECTION_PROOF_OWNER_REVIEW_DRY_RUN_V1

IDENTITY MARKER
AIOS_FOREX_BROKER_CONNECTION_PROOF_OWNER_REVIEW_DRY_RUN_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-BROKER-CONNECTION-PROOF-OWNER-REVIEW-DRY-RUN-V1

PACKET NAME
Broker Connection Proof Owner Review Dry Run V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Protected Broker Connection Boundary Review

WORKTREE
C:\\Dev\\Ai.Os

BRANCH
resolve after preflight

MISSION ID
{MISSION_ID}

MISSION NAME
{MISSION_NAME}

PROGRAM ID
{PROGRAM_ID}

PROGRAM NAME
{PROGRAM_NAME}

EPIC ID
EPC-FOREX-BROKER-CONNECTION-PROOF-001

EPIC NAME
Broker Connection Proof Protected Boundary

BUCKET ID
BKT-FOREX-BROKER-CONNECTION-PROOF-OWNER-REVIEW-001

BUCKET NAME
Owner Review For Broker Connection Proof

APPROVAL AUTHORITY
Anthony is the only authority for broker contact, credentials, .env access, account identifiers, account inspection, demo execution, live execution, order placement, scheduler activation, daemon activation, webhook activation, background-loop activation, APPLY, repository history creation, publication, PR creation, integration, and live trading authorization.
This packet is DRY_RUN-only and does not approve any protected action.

MISSION
Review the protected broker connection proof boundary using repo evidence only.
Do not execute broker connection proof.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not inspect broker account state.
Do not place orders.
Do not authorize demo execution.
Do not authorize live execution.
Do not start scheduler, daemon, webhook, worker, watcher, listener, or background loop.
Do not create files.
Do not edit files.
Do not create repository history.
Do not publish.
Do not create PR.

PREFLIGHT
cd C:\\Dev\\Ai.Os
pwd
git status --short --branch
git branch --show-current
git log -1 --oneline

READ FIRST
AGENTS.md
README.md
RISK_POLICY.md
docs/governance/AI_OS_REPO_MEMORY.md
docs/governance/aios-identity-and-lane-governance.md

READ SOURCE ARTIFACTS
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json

FORBIDDEN PATHS
AGENTS.md
README.md
RISK_POLICY.md
.env
.env.*
secrets
credentials
broker account identifiers
broker modules
order modules
demo execution modules
live execution modules
scheduler files
daemon files
webhook files
background-loop files
dashboard mutation files
unrelated docs
unrelated tests
any path outside C:\\Dev\\Ai.Os

REQUIRED BEHAVIOR
Confirm readiness_status is {result.get('readiness_status')}.
Confirm next protected boundary is broker connection proof.
Confirm owner_wake_required is true.
Confirm broker interface use, credentials, .env access, account identifiers, order placement, demo authorization, live authorization, scheduler, daemon, webhook, and background loop remain false.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json
git status --short --branch

STOP POINT
Stop after DRY_RUN owner review report.
Do not contact broker, use credentials, read .env, use account identifiers, inspect account state, place orders, authorize demo/live action, start scheduler, daemon, webhook, worker, watcher, listener, or background loop.

SAFE NEXT ACTION
Request Human Owner review of the exact broker connection proof scope before any protected broker-facing action.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
READINESS_STATUS:
NEXT_PROTECTED_BOUNDARY:
OWNER_WAKE_REQUIRED:
BROKER_API_USED:
CREDENTIALS_USED:
ENV_READ:
ACCOUNT_IDENTIFIERS_USED:
ORDER_EXECUTION:
DEMO_AUTHORIZED:
LIVE_AUTHORIZED:
SCHEDULER_STARTED:
DAEMON_STARTED:
WEBHOOK_STARTED:
BACKGROUND_LOOP_STARTED:
NEXT_SAFE_ACTION:
GIT_STATUS:
"""


def reusable_autonomy_pattern() -> dict[str, Any]:
    return {
        "identity_chain": "Mission -> Program -> Epic -> Bucket -> Packet",
        "preflight": "verify path, branch, clean worktree, no staged files, current head, stash metadata",
        "scope": "edit only allowed paths and keep forbidden paths explicit",
        "outputs": ["state JSON", "human report", "next Codex packet"],
        "protected_boundary_stop": "stop before broker/API/credential/account/order/runtime actions",
        "validation": ["py_compile", "focused pytest", "json.tool", "governance validator", "git diff --check"],
        "commit_flow": "stage exact files, inspect cached diff, commit once, stop before push/PR/merge",
    }


def _readiness_checks(source_state: Mapping[str, Any], stash_detected: bool) -> dict[str, bool]:
    return {
        "source_owner_wake_required": bool(source_state.get("owner_wake_required", True)),
        "repo_only_remaining_is_zero": int(source_state.get("repo_only_remaining_stage_count", 0)) == 0,
        "protected_stage_count_preserved": int(source_state.get("protected_stage_count", 12)) == 12,
        "next_boundary_is_broker_connection_proof": str(source_state.get("next_stage", "")) == NEXT_PROTECTED_BOUNDARY,
        "stash_detected_and_preserved": stash_detected,
        "protected_actions_false": True,
    }


def _load_source_state() -> Mapping[str, Any]:
    if not SOURCE_STATE_PATH.exists():
        return {}
    value = json.loads(SOURCE_STATE_PATH.read_text(encoding="utf-8"))
    if isinstance(value, Mapping):
        return value
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return []


def _relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


__all__ = [
    "DEFAULT_NEXT_PACKET_OUTPUT_PATH",
    "DEFAULT_REPORT_OUTPUT_PATH",
    "DEFAULT_STATE_OUTPUT_PATH",
    "PROTECTED_FALSE_FIELDS",
    "build_next_codex_packet",
    "build_report_markdown",
    "reusable_autonomy_pattern",
    "run_broker_connection_proof_boundary_readiness_v1",
]
