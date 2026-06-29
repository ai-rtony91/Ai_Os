"""Finite next-work queue for repo-safe Forex readiness work."""

from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine.evidence_depth_walkforward_sufficiency_v1 import (
    PROTECTED_FALSE_FIELDS,
)


PACKET_ID = "PKT-FOREX-EVIDENCE-CANDIDATE-DEMO-READINESS-CONSOLIDATED-V1"


def run_forex_next_repo_safe_queue_v1() -> dict[str, Any]:
    result: dict[str, Any] = {
        "queue_status": "FINITE_REPO_SAFE_QUEUE_READY",
        "completed_buckets": [
            "evidence_depth_walkforward_sufficiency",
            "candidate_selector_hardening",
            "promotion_rejection_gate_strengthening",
            "demo_readiness_decision",
        ],
        "next_repo_safe_buckets": [
            {
                "bucket_id": "BKT-FOREX-EVIDENCE-DEPTH-EXPANSION-002",
                "name": "additional deterministic walkforward evidence samples",
                "protected": False,
            },
            {
                "bucket_id": "BKT-FOREX-CANDIDATE-REVIEW-PACKET-002",
                "name": "owner-review packet refinement without broker contact",
                "protected": False,
            },
            {
                "bucket_id": "BKT-FOREX-DEMO-READINESS-EVIDENCE-002",
                "name": "demo readiness evidence checklist hardening",
                "protected": False,
            },
        ],
        "protected_boundaries": [
            "broker contact",
            "credentials",
            ".env access",
            "account identifiers",
            "account inspection",
            "demo execution",
            "live execution",
            "orders",
            "scheduler daemon webhook worker watcher listener background loop",
        ],
        "recommended_next_packet": "Reports/forex_delivery/AIOS_FOREX_EVIDENCE_CANDIDATE_DEMO_READINESS_NEXT_CODEX_PACKET_V1.md",
        "safe_next_action": "Run only the next repo-safe evidence packet before any protected broker boundary.",
        "packet_id": PACKET_ID,
    }
    result.update({field: False for field in PROTECTED_FALSE_FIELDS})
    return result


def build_report_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex Next Repo-Safe Queue V1 Report",
        "",
        f"Queue status: {result.get('queue_status')}",
        "",
        "Completed buckets:",
    ]
    lines.extend(f"- {item}" for item in result.get("completed_buckets", []))
    lines.extend(["", "Next repo-safe buckets:"])
    for bucket in result.get("next_repo_safe_buckets", []):
        lines.append(f"- {bucket.get('bucket_id')}: {bucket.get('name')}")
    lines.extend(["", "Protected boundaries:"])
    lines.extend(f"- {item}" for item in result.get("protected_boundaries", []))
    lines.extend(["", "Safe next action:", str(result.get("safe_next_action")), ""])
    return "\n".join(lines)


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    return """CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_REPO_SAFE_EVIDENCE_QUEUE_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_REPO_SAFE_EVIDENCE_QUEUE_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-REPO-SAFE-EVIDENCE-QUEUE-REVIEW-V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Autonomy Completion / Repo-Safe Evidence Queue Review

WORKTREE
C:\\Dev\\Ai.Os

BRANCH
resolve after preflight

MISSION
Review the finite repo-safe evidence queue and select a bounded non-broker packet.

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_REPORT.md

FORBIDDEN PATHS
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
any path outside C:\\Dev\\Ai.Os

APPROVAL AUTHORITY
This packet is DRY_RUN-only. It does not approve APPLY, repository history creation, publication, PR creation, broker contact, credentials, .env access, account identifiers, account inspection, demo/live execution, orders, scheduler, daemon, webhook, worker, watcher, listener, or background loop.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_STATE.json
git status --short --branch

STOP POINT
Stop after read-only queue review.

SAFE NEXT ACTION
Select one bounded repo-safe evidence packet, or stop for Human Owner approval before any protected boundary.

FINAL REPORT FORMAT
STATUS:
QUEUE_STATUS:
RECOMMENDED_NEXT_PACKET:
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


__all__ = [
    "build_next_codex_packet",
    "build_report_markdown",
    "run_forex_next_repo_safe_queue_v1",
]
