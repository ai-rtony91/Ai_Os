"""Packet queue candidate model for Operator Relief."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOKEN_PLACEHOLDER = "[ANTHONY_APPROVAL_REQUIRED]"
DEFAULT_PACKET_QUEUE_PATH = Path("telemetry/operator_relief/packet_queue/current_queue.json")


@dataclass(frozen=True)
class PacketCandidate:
    packet_id: str
    title: str
    purpose: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    validators: list[str]
    stop_point: str
    copy_paste_burden_removed: str
    human_review_required: bool = True
    executable: bool = False
    approval_token: str = TOKEN_PLACEHOLDER

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PacketQueueReport:
    status: str
    queue_path: str | None
    candidate_count: int
    candidates: list[dict[str, Any]]
    reasons: list[str]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _candidate(
    packet_id: str,
    title: str,
    purpose: str,
    allowed_paths: list[str],
    validators: list[str],
    burden: str,
) -> PacketCandidate:
    return PacketCandidate(
        packet_id=packet_id,
        title=title,
        purpose=purpose,
        allowed_paths=allowed_paths,
        forbidden_paths=[
            "AGENTS.md",
            "README.md",
            "docs/governance/**",
            "docs/security/**",
            "automation/forex_engine/**",
            "tests/forex_engine/**",
            "apps/**",
            "services/**",
            "any .env file",
            "any secret file",
            "any live execution path",
        ],
        validators=validators,
        stop_point="Stop after producing evidence and validators. Do not push, merge, notify, schedule, call external services, or execute protected actions.",
        copy_paste_burden_removed=burden,
        executable=False,
    )


def default_packet_candidates() -> list[PacketCandidate]:
    return [
        _candidate(
            "AIOS-PUSH-PR-CURRENT-BRANCH-CANDIDATE",
            "Push and PR current branch candidate",
            "Prepare protected-action evidence for pushing the current branch and opening a PR.",
            ["automation/operator_relief/**", "tests/operator_relief/**", "docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
            ["git diff --check", "python -m pytest tests/operator_relief"],
            "Anthony no longer has to assemble push/PR context manually.",
        ),
        _candidate(
            "AIOS-PACKET-FACTORY-V1-BUILD-CANDIDATE",
            "Packet Factory v1 build candidate",
            "Build readiness gate that emits packet candidates or blocked-readiness reports.",
            ["automation/operator_relief/**", "tests/operator_relief/**"],
            ["python -m pytest tests/operator_relief/test_packet_factory.py"],
            "Anthony no longer repairs malformed packet fields by hand.",
        ),
        _candidate(
            "AIOS-APPROVAL-INBOX-READER-CANDIDATE",
            "Approval Inbox reader candidate",
            "Summarize pending approval cards into one operator-facing approval inbox.",
            ["automation/operator_relief/**", "tests/operator_relief/**", "approval/operator_relief/**"],
            ["python -m pytest tests/operator_relief"],
            "Anthony no longer opens multiple approval files to know what needs action.",
        ),
        _candidate(
            "AIOS-WORKER-LOCK-MANAGER-CANDIDATE",
            "Worker Lock Manager candidate",
            "Prevent lane collisions before workers touch the same file tree.",
            ["automation/operator_relief/**", "tests/operator_relief/**"],
            ["python -m pytest tests/operator_relief"],
            "Anthony no longer manually checks worker collision risk.",
        ),
        _candidate(
            "AIOS-CODEX-CLI-FULL-AUTO-POLICY-CANDIDATE",
            "Codex CLI full-auto policy candidate",
            "Define when CLI handoff remains blocked, review-only, or future executable.",
            ["automation/operator_relief/**", "tests/operator_relief/**", "docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
            ["python -m pytest tests/operator_relief/test_cli_bridge.py"],
            "Anthony no longer translates policy boundaries into every CLI handoff.",
        ),
        _candidate(
            "AIOS-NIGHT-SUPERVISOR-BRIDGE-CANDIDATE",
            "Night Supervisor bridge candidate",
            "Connect night mission evidence to supervisor-loop next-action selection.",
            ["automation/operator_relief/**", "tests/operator_relief/**"],
            ["python -m pytest tests/operator_relief/test_supervisor_loop.py"],
            "Anthony no longer restarts night work by reading reports and choosing manually.",
        ),
        _candidate(
            "AIOS-SOS-HEALTH-CHECK-CANDIDATE",
            "ADB SOS health check candidate",
            "Check ADB wake readiness without sending live notifications.",
            ["automation/operator_relief/**", "tests/operator_relief/**"],
            ["python -m pytest tests/operator_relief"],
            "Anthony no longer guesses whether the wake line is healthy.",
        ),
        _candidate(
            "AIOS-SUPERVISOR-RESUME-HARDENING-CANDIDATE",
            "Supervisor resume loop hardening candidate",
            "Expand stale, consumed, and replay protections around resume telemetry.",
            ["automation/operator_relief/**", "tests/operator_relief/**"],
            ["python -m pytest tests/operator_relief/test_approval_resume_loop.py"],
            "Anthony no longer checks whether a resume decision is safe to reuse.",
        ),
        _candidate(
            "AIOS-ENGINE-ROOM-ADAPTER-CANDIDATE",
            "Engine Room dashboard adapter candidate",
            "Adapt engine-room telemetry for a future read-only dashboard.",
            ["automation/operator_relief/**", "tests/operator_relief/**"],
            ["python -m pytest tests/operator_relief/test_engine_room_telemetry.py"],
            "Anthony no longer has to summarize active worker state manually.",
        ),
        _candidate(
            "AIOS-NON-WOL-MORNING-START-CANDIDATE",
            "Non-WOL morning start candidate",
            "Build a local morning start that does not require Wake-on-LAN.",
            ["automation/operator_relief/**", "tests/operator_relief/**", "docs/workflows/**"],
            ["python -m pytest tests/operator_relief"],
            "Anthony no longer opens each morning command by hand when the machine is already awake.",
        ),
    ]


def validate_packet_candidate(candidate: PacketCandidate) -> list[str]:
    payload = json.dumps(candidate.to_dict(), sort_keys=True)
    reasons: list[str] = []
    if candidate.executable:
        reasons.append("Packet candidate must be executable=false.")
    if not candidate.human_review_required:
        reasons.append("Packet candidate must require human review.")
    if candidate.approval_token != TOKEN_PLACEHOLDER:
        reasons.append("Packet candidate must use approval placeholder.")
    if "AI_OS EXECUTION TOKEN" in payload:
        reasons.append("Packet candidate must not include live execution token text.")
    for field_name in ("allowed_paths", "forbidden_paths", "validators"):
        if not getattr(candidate, field_name):
            reasons.append(f"{field_name} is required.")
    if not candidate.stop_point:
        reasons.append("stop_point is required.")
    return reasons


def write_packet_queue(
    repo_root: Path,
    candidates: list[PacketCandidate] | None = None,
    queue_path: Path | str = DEFAULT_PACKET_QUEUE_PATH,
) -> PacketQueueReport:
    selected = candidates or default_packet_candidates()
    reasons: list[str] = []
    if not (5 <= len(selected) <= 10):
        reasons.append("Packet queue must contain 5-10 candidates.")
    for candidate in selected:
        reasons.extend(validate_packet_candidate(candidate))

    candidate_dicts = [candidate.to_dict() for candidate in selected]
    if reasons:
        return PacketQueueReport(
            status="PACKET_QUEUE_BLOCKED",
            queue_path=None,
            candidate_count=len(selected),
            candidates=candidate_dicts,
            reasons=reasons,
            executable=False,
        )

    path = (repo_root.resolve() / Path(queue_path)).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PACKET_QUEUE_READY",
        "candidate_count": len(selected),
        "candidates": candidate_dicts,
        "executable": False,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return PacketQueueReport(
        status="PACKET_QUEUE_READY",
        queue_path=str(path),
        candidate_count=len(selected),
        candidates=candidate_dicts,
        reasons=[],
        executable=False,
    )
