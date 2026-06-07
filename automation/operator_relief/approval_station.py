"""Bounded local approval decision reader for Operator Relief v1."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


APPROVAL_INPUT_ROOT = Path("automation/operator_relief/approval_input")
SUPPORTED_DECISIONS = {"APPROVE", "REJECT", "CONTINUE_MISSION", "HOLD"}


@dataclass(frozen=True)
class ApprovalStationReport:
    status: str
    decision: str | None
    approval_path: str
    task_id: str | None
    reasons: list[str]
    network_listener_started: bool
    port_opened: bool
    credential_material_stored: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _resolve_inside(repo_root: Path, root_path: Path, candidate_path: str | Path) -> Path:
    root = repo_root.resolve()
    allowed_root = (root / root_path).resolve()
    raw_candidate = Path(candidate_path)
    candidate = raw_candidate if raw_candidate.is_absolute() else root / raw_candidate
    resolved = candidate.resolve()
    if not (resolved == allowed_root or allowed_root in resolved.parents):
        raise ValueError(f"Approval decision path must stay inside {root_path.as_posix()}/.")
    return resolved


def read_approval_decision(
    repo_root: Path,
    decision_path: str | Path,
    input_root: Path = APPROVAL_INPUT_ROOT,
) -> ApprovalStationReport:
    try:
        path = _resolve_inside(repo_root, input_root, decision_path)
    except ValueError as exc:
        return ApprovalStationReport(
            status="APPROVAL_BLOCKED",
            decision=None,
            approval_path=str(decision_path),
            task_id=None,
            reasons=[str(exc)],
            network_listener_started=False,
            port_opened=False,
            credential_material_stored=False,
            executable=False,
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ApprovalStationReport(
            status="APPROVAL_BLOCKED",
            decision=None,
            approval_path=str(path),
            task_id=None,
            reasons=[f"Malformed approval JSON: {exc}"],
            network_listener_started=False,
            port_opened=False,
            credential_material_stored=False,
            executable=False,
        )
    except OSError as exc:
        return ApprovalStationReport(
            status="APPROVAL_BLOCKED",
            decision=None,
            approval_path=str(path),
            task_id=None,
            reasons=[str(exc)],
            network_listener_started=False,
            port_opened=False,
            credential_material_stored=False,
            executable=False,
        )

    decision = payload.get("decision") if isinstance(payload, dict) else None
    task_id = payload.get("task_id") if isinstance(payload, dict) else None
    if decision not in SUPPORTED_DECISIONS:
        return ApprovalStationReport(
            status="APPROVAL_BLOCKED",
            decision=str(decision) if decision is not None else None,
            approval_path=str(path),
            task_id=str(task_id) if task_id is not None else None,
            reasons=["Unknown approval decision."],
            network_listener_started=False,
            port_opened=False,
            credential_material_stored=False,
            executable=False,
        )

    return ApprovalStationReport(
        status="APPROVAL_DECISION_ACCEPTED",
        decision=decision,
        approval_path=str(path),
        task_id=str(task_id) if task_id is not None else None,
        reasons=[],
        network_listener_started=False,
        port_opened=False,
        credential_material_stored=False,
        executable=False,
    )
