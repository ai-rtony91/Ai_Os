"""Finite repo-safe overnight campaign planner for the Forex lane."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.broker_connection_proof_boundary_readiness_v1 import (
    PROTECTED_FALSE_FIELDS,
    reusable_autonomy_pattern,
)


PACKET_ID = "PKT-FOREX-OVERNIGHT-REPO-SAFE-CAMPAIGN-PLANNER-V1"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
MISSION_NAME = "Governed Forex Finish Line"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
PROGRAM_NAME = "Forex Profit Autonomy System"
EPIC_ID = "EPC-FOREX-AUTONOMY-COMPLETION-001"
EPIC_NAME = "Autonomy Completion"
BUCKET_ID = "BKT-FOREX-OVERNIGHT-REPO-SAFE-BUILD-001"
BUCKET_NAME = "Overnight Repo-Safe Broker Boundary And Autonomy Reuse Build Stage"

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "Reports" / "forex_delivery"
DEFAULT_STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_REPORT.md"
)
DEFAULT_NEXT_PACKET_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_NEXT_CODEX_PACKET_V1.md"
)


def run_forex_overnight_repo_safe_campaign_planner_v1() -> dict[str, Any]:
    work_units = _repo_safe_work_units()
    completed = [
        "broker boundary readiness state/report/packet",
        "reusable autonomy pattern documentation",
        "overnight repo-safe campaign planner state/report/packet",
    ]
    result: dict[str, Any] = {
        "campaign_status": "REPO_SAFE_OVERNIGHT_BUILD_STAGE_READY",
        "current_branch_expected": "forex-broker-boundary-readiness-v1",
        "current_head_expected": "ecec9b60 or newer from PR #1221",
        "repo_safe_work_units": work_units,
        "completed_work_units": completed,
        "remaining_repo_safe_work_units": [
            unit["name"] for unit in work_units if unit["name"] not in completed
        ],
        "protected_boundaries": [
            {
                "name": "broker connection proof",
                "reason": "requires owner approval, broker contact, credentials, .env access, and account identifiers",
            }
        ],
        "next_repo_safe_stage": "owner-review packet refinement and evidence packaging",
        "next_protected_boundary": "broker connection proof",
        "owner_wake_required": True,
        "stash_policy": {
            "stash_detected": True,
            "stash_preserved": True,
            "stash_applied": False,
            "stash_pop_used": False,
            "stash_drop_used": False,
        },
        "failure_reduction_rules": [
            "use current clean branch only",
            "use finite work queue only",
            "write state/report/next-packet artifacts only",
            "stop before broker/API/credential/account/order/runtime boundaries",
            "stage exact allowed paths only",
        ],
        "overnight_run_limits": {
            "finite_queue": True,
            "infinite_loop": False,
            "scheduler_started": False,
            "daemon_started": False,
            "webhook_started": False,
            "background_loop_started": False,
            "requires_new_human_approval_for_protected_boundary": True,
        },
        "reusable_autonomy_pattern": reusable_autonomy_pattern(),
        "recommended_next_packet": _relative_path(DEFAULT_NEXT_PACKET_OUTPUT_PATH),
        "safe_next_action": (
            "Use the generated repo-safe next packet only for bounded local artifact work. "
            "Stop before broker connection proof or any scheduler, daemon, webhook, worker, "
            "watcher, listener, or background loop."
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
    lines = [
        "# AIOS Forex Overnight Repo-Safe Campaign Planner V1 Report",
        "",
        f"Campaign status: {result.get('campaign_status')}",
        f"Expected branch: {result.get('current_branch_expected')}",
        f"Expected head: {result.get('current_head_expected')}",
        f"Next repo-safe stage: {result.get('next_repo_safe_stage')}",
        f"Next protected boundary: {result.get('next_protected_boundary')}",
        f"Owner wake required: {result.get('owner_wake_required')}",
        "",
        "Finite repo-safe work units:",
    ]
    for unit in result.get("repo_safe_work_units", []):
        if isinstance(unit, Mapping):
            lines.append(f"- {unit.get('name')}: {unit.get('output')}")
    lines.extend(["", "Protected boundaries:"])
    for boundary in result.get("protected_boundaries", []):
        if isinstance(boundary, Mapping):
            lines.append(f"- {boundary.get('name')}: {boundary.get('reason')}")
    lines.extend(["", "Runtime actions retained false:"])
    for field in PROTECTED_FALSE_FIELDS:
        lines.append(f"- {field}: {result.get(field)}")
    lines.extend(["", "Safe next action:", str(result.get("safe_next_action")), ""])
    return "\n".join(lines)


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    return f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_NEXT_REPO_SAFE_BUILD_PACKET_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_NEXT_REPO_SAFE_BUILD_PACKET_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-NEXT-REPO-SAFE-BUILD-PACKET-REVIEW-V1

PACKET NAME
Forex Next Repo-Safe Build Packet Review V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Autonomy Completion / Repo-Safe Build Review

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
{EPIC_ID}

EPIC NAME
{EPIC_NAME}

BUCKET ID
BKT-FOREX-NEXT-REPO-SAFE-BUILD-REVIEW-001

BUCKET NAME
Next Repo-Safe Build Review

APPROVAL AUTHORITY
Anthony remains the only authority for APPLY, repository history creation, publication, PR creation, integration, broker contact, credentials, .env access, account identifiers, account inspection, order placement, demo execution, live execution, scheduler activation, daemon activation, webhook activation, worker activation, watcher activation, listener activation, and background-loop activation.
This packet is DRY_RUN-only and does not authorize protected actions.

MISSION
Review the finite repo-safe Forex build queue and select the next bounded local artifact packet.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not inspect broker account state.
Do not place orders.
Do not authorize demo or live execution.
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

READ SOURCE ARTIFACTS
Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json

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
Confirm campaign_status is {result.get('campaign_status')}.
Confirm the queue is finite and repo-safe only.
Confirm broker connection proof remains protected.
Confirm all broker/action/runtime booleans remain false.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json
git status --short --branch

STOP POINT
Stop after DRY_RUN review. Do not execute broker connection proof or any protected runtime action.

SAFE NEXT ACTION
Select only the next bounded repo-safe packet, or stop for Human Owner approval before broker connection proof.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
CAMPAIGN_STATUS:
NEXT_REPO_SAFE_STAGE:
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


def _repo_safe_work_units() -> list[dict[str, str]]:
    return [
        {
            "name": "broker boundary readiness state/report/packet",
            "output": "deterministic local readiness evidence",
        },
        {
            "name": "reusable autonomy pattern documentation",
            "output": "cross-lane autonomy skeleton documentation",
        },
        {
            "name": "overnight repo-safe campaign planner state/report/packet",
            "output": "finite future repo-safe work queue",
        },
        {
            "name": "owner-review packet refinement and evidence packaging",
            "output": "DRY_RUN packet for human review only",
        },
        {
            "name": "repo-safe validator hardening packet",
            "output": "tests for boundary booleans and next-packet safety",
        },
    ]


def _relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


__all__ = [
    "DEFAULT_NEXT_PACKET_OUTPUT_PATH",
    "DEFAULT_REPORT_OUTPUT_PATH",
    "DEFAULT_STATE_OUTPUT_PATH",
    "build_next_codex_packet",
    "build_report_markdown",
    "run_forex_overnight_repo_safe_campaign_planner_v1",
]
