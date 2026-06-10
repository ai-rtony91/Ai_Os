"""AI_OS Runtime APPLY lane preview (observe-only).

This module builds a non-mutating projection for the Runtime APPLY lane.
It never writes canonical queue state, worker inbox state, runtime state, or
approval/scheduler/SOS/trading state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_RUNTIME_APPLY_LANE_PREVIEW.v1"
MODE = "DRY_RUN_PREVIEW_ONLY"
REPORT_DIR = Path("Reports") / "runtime_apply_lane"
REPORT_JSON_NAME = "runtime_apply_lane_preview.json"
REPORT_MD_NAME = "runtime_apply_lane_summary.md"

STATUS_READY = "READY_FOR_RUNTIME_PREVIEW"
STATUS_BLOCKED = "BLOCKED"
STATUS_INVALID = "INVALID"
ALLOWED_STATUSES = {STATUS_READY, STATUS_BLOCKED, STATUS_INVALID}

DEFAULT_P2_PREVIEW = Path("Reports") / "p2_enqueue_bridge" / "p2_enqueue_bridge_preview.json"
DEFAULT_QUEUE_GATE_PREVIEW = Path("Reports") / "queue_mutation_gate" / "queue_mutation_gate_preview.json"
DEFAULT_RUNTIME_PROOF_REPORT = Path("Reports") / "runtime_proof_gate" / "runtime_proof_gate_preview.json"

PROHIBITED_PREFIXES = (
    ".github/",
    "AGENTS.md",
    "README.md",
    "docs/",
    "automation/orchestration/work_packets/active/",
    "automation/orchestration/work_packets/blocked/",
    "automation/orchestration/work_packets/complete/",
    "automation/orchestration/workers/inbox/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/command_queue/",
    "telemetry/",
    "services/",
    "apps/",
    "aios.ps1",
)

PROTECTED_FALSE_FIELDS = (
    "approval_granted",
    "execution_allowed",
    "dispatch_allowed",
    "apply_allowed",
    "runtime_launch_allowed",
    "runtime_mutation_allowed",
    "queue_mutation_allowed",
    "worker_inbox_mutation_allowed",
    "approval_inbox_mutation_allowed",
    "command_queue_mutation_allowed",
    "telemetry_mutation_allowed",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "sos_allowed",
    "live_trading_allowed",
    "credentials_accessed",
    "unsafe_autonomy_claim",
    "vacation_mode_complete",
)


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _hash_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path) -> dict[str, Any]:
    if path.is_dir():
        files = []
        for file in sorted(path.rglob("*")):
            if file.is_file():
                files.append(
                    {
                        "path": file.relative_to(path).as_posix(),
                        "size": file.stat().st_size,
                        "sha256": _hash_file(file),
                    }
                )
        return {
            "exists": path.exists(),
            "is_dir": True,
            "path": path.as_posix(),
            "files": files,
        }
    return {
        "exists": path.exists(),
        "is_file": path.is_file(),
        "path": path.as_posix(),
        "size": path.stat().st_size if path.exists() else None,
        "sha256": _hash_file(path),
    }


def _list_from(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_path(value: str) -> str:
    norm = value.replace("\\", "/").strip()
    while norm.startswith("./"):
        norm = norm[2:]
    return norm.lower().rstrip("/")


def _path_targets_protected(paths: list[str]) -> list[str]:
    blocked = []
    for path_text in paths:
        normalized = _normalize_path(path_text)
        for prefix in PROHIBITED_PREFIXES:
            p = _normalize_path(prefix)
            if normalized == p or normalized.startswith(p + "/"):
                blocked.append(path_text)
                break
    return sorted(set(blocked))


def _extract_p2_preview(payload: dict[str, Any]) -> dict[str, Any]:
    item = _ensure_dict(payload.get("proposed_queue_item_preview"))
    validation = _ensure_dict(payload.get("validation"))
    summary = _ensure_dict(payload.get("summary"))
    return {
        "bridge_status": _norm(payload.get("bridge_status")),
        "bridge_validation_status": validation.get("status"),
        "bridge_blockers": payload.get("bridge_blockers") or [],
        "invalid_reasons": payload.get("invalid_reasons") or [],
        "packet_id": item.get("preview_id"),
        "lane_id": item.get("lane_id"),
        "allowed_paths": _list_from(item.get("allowed_paths")),
        "forbidden_paths": _list_from(item.get("forbidden_paths")),
        "recommended_next_lane": summary.get("recommended_next_lane") or item.get("recommended_next_lane"),
        "runtime_execution_allowed": item.get("runtime_execution_allowed"),
        "scheduler_creation_allowed": item.get("scheduler_creation_allowed"),
        "sos_allowed": item.get("sos_allowed"),
        "live_trading_allowed": item.get("live_trading_allowed"),
        "queue_mutation_allowed": item.get("queue_mutation_allowed"),
        "runtime_launch_allowed": item.get("runtime_launch_allowed"),
        "worker_inbox_write_allowed": item.get("worker_inbox_write_allowed"),
    }


def _extract_queue_preview(payload: dict[str, Any]) -> dict[str, Any]:
    item = _ensure_dict(payload.get("proposed_queue_item"))
    approval = _ensure_dict(payload.get("approval_check"))
    validation = _ensure_dict(payload.get("validation"))
    duplicate = _ensure_dict(payload.get("duplicate_check"))
    protected = _ensure_dict(payload.get("protected_path_check"))
    return {
        "gate_status": _norm(payload.get("gate_status")),
        "validation_status": validation.get("status"),
        "validation_blockers": validation.get("blockers") or [],
        "validation_invalid_reasons": validation.get("invalid_reasons") or [],
        "packet_id": item.get("packet_id"),
        "mode": item.get("mode"),
        "lane": item.get("lane"),
        "allowed_paths": _list_from(item.get("allowed_paths")),
        "forbidden_paths": _list_from(item.get("forbidden_paths")),
        "target_paths": _list_from(item.get("target_paths")),
        "explicit_approval": bool(approval.get("explicit_approval")),
        "approval_evidence_present": bool(approval.get("approval_evidence_present")),
        "duplicate_packet_id": bool(duplicate.get("duplicate_packet_id")),
        "protected_path_targeted": bool(protected.get("protected_path_targeted")),
        "runtime_execution_allowed": payload.get("runtime_execution_allowed"),
        "queue_mutation_allowed": payload.get("queue_mutation_allowed"),
        "runtime_launch_allowed": payload.get("runtime_launch_allowed"),
        "scheduler_creation_allowed": payload.get("scheduler_creation_allowed"),
        "sos_allowed": payload.get("sos_allowed"),
        "live_trading_allowed": payload.get("live_trading_allowed"),
        "worker_inbox_mutation_allowed": payload.get("worker_inbox_mutation_allowed"),
    }


def _extract_runtime_preview(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "final_verdict": _norm(payload.get("final_verdict")),
        "human_gate_ready": bool(payload.get("human_gate_ready")),
        "runtime_launch_allowed": payload.get("runtime_launch_allowed"),
        "runtime_execution_allowed": payload.get("execution_allowed"),
        "runtime_mutation_allowed": payload.get("runtime_mutation_allowed"),
        "scheduler_creation_allowed": payload.get("scheduler_creation_allowed"),
        "sos_allowed": payload.get("sos_allowed"),
        "live_trading_allowed": payload.get("live_trading_allowed"),
        "approval_granted": payload.get("approval_granted"),
        "vacation_mode_complete": payload.get("vacation_mode_complete"),
    }


def _default_evidence(repo_root: Path) -> dict[str, Any]:
    return {
        "p2_preview": _read_json(repo_root / DEFAULT_P2_PREVIEW),
        "queue_mutation_gate_preview": _read_json(repo_root / DEFAULT_QUEUE_GATE_PREVIEW),
        "runtime_proof_gate": _read_json(repo_root / DEFAULT_RUNTIME_PROOF_REPORT),
        "source_fingerprints": [
            _fingerprint(repo_root / "Reports" / "p2_enqueue_bridge" / "p2_enqueue_bridge_preview.json"),
            _fingerprint(repo_root / "Reports" / "queue_mutation_gate" / "queue_mutation_gate_preview.json"),
            _fingerprint(repo_root / "Reports" / "runtime_proof_gate" / "runtime_proof_gate_preview.json"),
            _fingerprint(repo_root / "automation/orchestration/work_packets/active"),
            _fingerprint(repo_root / "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"),
            _fingerprint(repo_root / "automation/orchestration/approval_inbox"),
            _fingerprint(repo_root / "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"),
            _fingerprint(repo_root / "services/runtime"),
            _fingerprint(repo_root / "telemetry/runtime"),
            _fingerprint(repo_root / "automation/orchestration/work_packets/active"),
        ],
        "evidence_loaded": {
            "p2_preview": {
                "loaded": (repo_root / DEFAULT_P2_PREVIEW).exists(),
                "path": str(DEFAULT_P2_PREVIEW),
            },
            "queue_mutation_gate_preview": {
                "loaded": (repo_root / DEFAULT_QUEUE_GATE_PREVIEW).exists(),
                "path": str(DEFAULT_QUEUE_GATE_PREVIEW),
            },
            "runtime_proof_gate": {
                "loaded": (repo_root / DEFAULT_RUNTIME_PROOF_REPORT).exists(),
                "path": str(DEFAULT_RUNTIME_PROOF_REPORT),
            },
        },
    }


def build_runtime_apply_lane_report(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    p2_preview: dict[str, Any] | None = None,
    queue_mutation_gate_preview: dict[str, Any] | None = None,
    runtime_proof_gate: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    output_dir_path = Path(output_dir) if output_dir else root / REPORT_DIR

    evidence = _default_evidence(root)
    if p2_preview is not None:
        evidence["p2_preview"] = p2_preview
    if queue_mutation_gate_preview is not None:
        evidence["queue_mutation_gate_preview"] = queue_mutation_gate_preview
    if runtime_proof_gate is not None:
        evidence["runtime_proof_gate"] = runtime_proof_gate

    p2 = _ensure_dict(evidence.get("p2_preview"))
    queue_gate = _ensure_dict(evidence.get("queue_mutation_gate_preview"))
    runtime = _ensure_dict(evidence.get("runtime_proof_gate"))

    p2_meta = _extract_p2_preview(p2)
    queue_meta = _extract_queue_preview(queue_gate)
    runtime_meta = _extract_runtime_preview(runtime)

    blockers: list[str] = []
    invalid_reasons: list[str] = []

    if not p2:
        invalid_reasons.append("missing required evidence: p2_preview")
    if not queue_gate:
        invalid_reasons.append("missing required evidence: queue_mutation_gate_preview")
    if not runtime:
        invalid_reasons.append("missing required evidence: runtime_proof_gate")

    # Packet integrity checks from queue gate and P2 preview.
    if p2_meta["bridge_status"] != "READY_FOR_DRY_RUN_PREVIEW":
        blockers.append("P2 bridge is not READY_FOR_DRY_RUN_PREVIEW")
    if not queue_meta["packet_id"]:
        blockers.append("queue mutation preview packet_id is missing")
    if not queue_meta["mode"]:
        blockers.append("queue mutation preview mode is missing")
    if not queue_meta["lane"]:
        blockers.append("queue mutation preview lane is missing")
    if not queue_meta["allowed_paths"]:
        blockers.append("queue mutation preview allowed_paths is missing")
    if not queue_meta["forbidden_paths"]:
        blockers.append("queue mutation preview forbidden_paths is missing")
    if not queue_meta["explicit_approval"]:
        blockers.append("queue mutation approval is not explicit")
    if not queue_meta["approval_evidence_present"]:
        blockers.append("queue mutation approval evidence is missing")
    if queue_meta["duplicate_packet_id"]:
        blockers.append("queue mutation gate would duplicate active packet ID")
    if queue_meta["protected_path_targeted"]:
        blockers.append("queue mutation proposal targets protected paths")

    queue_gate_blockers = queue_meta["validation_blockers"]
    for blocker in queue_gate_blockers:
        if blocker and blocker not in blockers:
            blockers.append(f"queue gate validation: {blocker}")
    if queue_meta["validation_invalid_reasons"]:
        # Known queue contract gaps (such as stale allowed/forbidden) should not
        # crash runtime preview readiness; they block safely.
        blockers.append("queue gate evidence still carries invalid reasons")

    # Runtime proof safety checks.
    if not runtime_meta["final_verdict"]:
        blockers.append("runtime proof final_verdict is missing")
    elif runtime_meta["final_verdict"] != "READY_FOR_HUMAN_GATE":
        blockers.append("runtime proof final_verdict is not READY_FOR_HUMAN_GATE")
    if runtime_meta["runtime_launch_allowed"] is True:
        blockers.append("runtime proof indicates runtime_launch_allowed true")
    if runtime_meta["runtime_execution_allowed"] is True:
        blockers.append("runtime proof indicates execution_allowed true")
    if runtime_meta["runtime_mutation_allowed"] is True:
        blockers.append("runtime proof indicates runtime_mutation_allowed true")
    if runtime_meta["scheduler_creation_allowed"] is True:
        blockers.append("runtime proof indicates scheduler_creation_allowed true")
    if runtime_meta["sos_allowed"] is True:
        blockers.append("runtime proof indicates sos_allowed true")
    if runtime_meta["live_trading_allowed"] is True:
        blockers.append("runtime proof indicates live_trading_allowed true")
    if runtime_meta["approval_granted"] is True:
        blockers.append("runtime proof indicates approval_granted true")
    if runtime_meta["vacation_mode_complete"] is True:
        blockers.append("runtime proof indicates vacation_mode_complete true")

    if queue_meta["runtime_execution_allowed"] is True:
        blockers.append("queue gate evidence indicates runtime_execution_allowed true")
    if queue_meta["runtime_launch_allowed"] is True:
        blockers.append("queue gate evidence indicates runtime_launch_allowed true")
    if queue_meta["scheduler_creation_allowed"] is True:
        blockers.append("queue gate evidence indicates scheduler_creation_allowed true")
    if queue_meta["sos_allowed"] is True:
        blockers.append("queue gate evidence indicates sos_allowed true")
    if queue_meta["live_trading_allowed"] is True:
        blockers.append("queue gate evidence indicates live_trading_allowed true")

    p2_safe_fields = (
        p2_meta["runtime_execution_allowed"],
        p2_meta["scheduler_creation_allowed"],
        p2_meta["sos_allowed"],
        p2_meta["live_trading_allowed"],
        p2_meta["queue_mutation_allowed"],
        p2_meta["runtime_launch_allowed"],
        p2_meta["worker_inbox_write_allowed"],
    )
    if any(value is True for value in p2_safe_fields):
        blockers.append("P2 preview requires unsafe execution/route flags")

    worker_availability_preview = {
        "previewed": True,
        "path_targets": queue_meta["target_paths"] or queue_meta["allowed_paths"],
        "protected_targets": _path_targets_protected(
            queue_meta["target_paths"] + queue_meta["allowed_paths"]
        ),
    }
    if worker_availability_preview["protected_targets"]:
        blockers.append("queue gate targets protected paths")

    apply_status = STATUS_INVALID if invalid_reasons else STATUS_READY
    if blockers or not (p2 and queue_gate and runtime):
        apply_status = STATUS_BLOCKED if apply_status != STATUS_INVALID else STATUS_INVALID

    route_targets = {
        "source": queue_meta["allowed_paths"] or p2_meta["allowed_paths"],
        "protected": queue_meta["forbidden_paths"] or p2_meta["forbidden_paths"],
    }

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": _now(now),
        "repo_root": root.as_posix(),
        "apply_status": apply_status,
        "apply_status_reason": (
            "Runtime APPLY lane can proceed to preview-only routing."
            if apply_status == STATUS_READY
            else "Runtime APPLY lane is blocked by evidence blockers."
            if apply_status == STATUS_BLOCKED
            else "Runtime APPLY lane preview is invalid due missing required evidence."
        ),
        "evidence_missing": [item for item in ["p2_preview", "queue_mutation_gate_preview", "runtime_proof_gate"] if not evidence[item]],
        "evidence_loaded": evidence.get("evidence_loaded", {}),
        "source_fingerprints": evidence.get("source_fingerprints", []),
        "p2_preview": {
            "bridge_status": p2_meta["bridge_status"],
            "bridge_validation_status": p2_meta["bridge_validation_status"],
            "packet_id": p2_meta["packet_id"],
            "lane_id": p2_meta["lane_id"],
            "allowed_paths": p2_meta["allowed_paths"],
            "forbidden_paths": p2_meta["forbidden_paths"],
            "recommended_next_lane": p2_meta["recommended_next_lane"],
        },
        "queue_mutation_gate_preview": {
            "gate_status": queue_meta["gate_status"],
            "validation_status": queue_meta["validation_status"],
            "packet_id": queue_meta["packet_id"],
            "lane": queue_meta["lane"],
            "mode": queue_meta["mode"],
            "allowed_paths": queue_meta["allowed_paths"],
            "forbidden_paths": queue_meta["forbidden_paths"],
            "target_paths": queue_meta["target_paths"],
            "explicit_approval": queue_meta["explicit_approval"],
            "approval_evidence_present": queue_meta["approval_evidence_present"],
        },
        "runtime_proof_gate": {
            "final_verdict": runtime_meta["final_verdict"],
            "human_gate_ready": runtime_meta["human_gate_ready"],
            "runtime_launch_allowed": runtime_meta["runtime_launch_allowed"],
            "execution_allowed": runtime_meta["runtime_execution_allowed"],
            "runtime_mutation_allowed": runtime_meta["runtime_mutation_allowed"],
            "scheduler_creation_allowed": runtime_meta["scheduler_creation_allowed"],
            "sos_allowed": runtime_meta["sos_allowed"],
            "live_trading_allowed": runtime_meta["live_trading_allowed"],
            "approval_granted": runtime_meta["approval_granted"],
            "vacation_mode_complete": runtime_meta["vacation_mode_complete"],
        },
        "worker_availability_preview": worker_availability_preview,
        "route_targets": route_targets,
        "blockers": list(dict.fromkeys(blockers)),
        "invalid_reasons": invalid_reasons,
        "would_apply": False,
        "would_route": False,
        "would_execute": False,
        "runtime_launch": False,
        "runtime_execution": False,
        "queue_mutation": False,
        "worker_inbox_mutation": False,
        "approval_inbox_mutation": False,
        "command_queue_mutation": False,
        "scheduler_registration": False,
        "sos_notification": False,
        "trading_execution": False,
        "execution_projection": {
            "would_apply": False,
            "would_route": False,
            "would_execute": False,
            "runtime_launch": False,
            "runtime_execution": False,
            "queue_mutation": False,
            "worker_inbox_mutation": False,
            "approval_inbox_mutation": False,
            "command_queue_mutation": False,
            "scheduler_registration": False,
            "sos_notification": False,
            "trading_execution": False,
        },
        "report_paths": [str((output_dir_path / REPORT_JSON_NAME)), str((output_dir_path / REPORT_MD_NAME))],
        "safe_next_action": (
            "No mutable action taken. Explicit approval and remaining blockers resolved allow moving toward runtime apply execution lane preview."
            if apply_status == STATUS_READY
            else (
                "Resolve blockers and explicit approvals before any runtime apply lane mutation."
                if apply_status == STATUS_BLOCKED
                else "Repair evidence and rerun preview."
            )
        ),
        "stop_condition": "Stop before writing to active queue, worker inbox, approval inbox, command queue, telemetry, scheduler, SOS, services, or runtime.",
    }

    # Explicitly expose canonical false-allow flags expected by operators and tests.
    report.update(
        {
            "queue_mutation_allowed": False,
            "worker_inbox_mutation_allowed": False,
            "approval_inbox_mutation_allowed": False,
            "command_queue_mutation_allowed": False,
            "runtime_launch_allowed": False,
            "runtime_execution_allowed": False,
            "scheduler_creation_allowed": False,
            "sos_allowed": False,
            "live_trading_allowed": False,
            "runtime_mutation_allowed": False,
            "credentials_accessed": False,
            "telemetry_mutation_allowed": False,
        }
    )

    validation = validate_runtime_apply_lane_preview(report)
    report["validation"] = validation
    report["summary"] = summarize_runtime_apply_lane_preview(report)
    return report


def validate_runtime_apply_lane_preview(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["report_not_object"],
            "apply_status": None,
        }

    checked_fields = [
        "schema",
        "mode",
        "generated_at_utc",
        "repo_root",
        "apply_status",
        "evidence_missing",
        "p2_preview",
        "queue_mutation_gate_preview",
        "runtime_proof_gate",
        "worker_availability_preview",
        "route_targets",
        "blockers",
        "invalid_reasons",
        "would_apply",
        "would_route",
        "would_execute",
        "runtime_launch",
        "runtime_execution",
        "queue_mutation",
        "worker_inbox_mutation",
        "approval_inbox_mutation",
        "command_queue_mutation",
        "scheduler_registration",
        "sos_notification",
        "trading_execution",
        "safe_next_action",
        "stop_condition",
        "report_paths",
    ]

    blockers: list[str] = []
    hard_blockers: list[str] = []
    unsafe_flags: list[str] = []

    for field in checked_fields:
        if field not in report:
            hard_blockers.append(f"missing required field: {field}")

    if report.get("schema") != SCHEMA:
        hard_blockers.append("schema mismatch")
        unsafe_flags.append("schema_invalid")
    if report.get("mode") != MODE:
        hard_blockers.append("mode mismatch")
        unsafe_flags.append("mode_invalid")
    if report.get("generated_at_utc") is None:
        hard_blockers.append("generated_at_utc missing")
        unsafe_flags.append("generated_at_utc_missing")

    apply_status = _norm(report.get("apply_status"))
    if apply_status not in ALLOWED_STATUSES:
        hard_blockers.append("apply_status must be READY_FOR_RUNTIME_PREVIEW, BLOCKED, or INVALID")
        unsafe_flags.append("apply_status_invalid")

    for field in (
        "would_apply",
        "would_route",
        "would_execute",
        "runtime_launch",
        "runtime_execution",
        "queue_mutation",
        "worker_inbox_mutation",
        "approval_inbox_mutation",
        "command_queue_mutation",
        "scheduler_registration",
        "sos_notification",
        "trading_execution",
        "queue_mutation_allowed",
        "worker_inbox_mutation_allowed",
        "approval_inbox_mutation_allowed",
        "command_queue_mutation_allowed",
        "runtime_launch_allowed",
        "runtime_execution_allowed",
        "scheduler_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "runtime_mutation_allowed",
        "credentials_accessed",
        "telemetry_mutation_allowed",
    ):
        if report.get(field) is not False:
            hard_blockers.append(f"{field} must remain false")
            unsafe_flags.append(f"{field}_true")

    execution_projection = _ensure_dict(report.get("execution_projection"))
    for field in (
        "would_apply",
        "would_route",
        "would_execute",
        "runtime_launch",
        "runtime_execution",
        "queue_mutation",
        "worker_inbox_mutation",
        "approval_inbox_mutation",
        "command_queue_mutation",
        "scheduler_registration",
        "sos_notification",
        "trading_execution",
    ):
        if execution_projection.get(field) is not False:
            hard_blockers.append(f"execution_projection.{field} must remain false")

    if apply_status == STATUS_READY and (report.get("blockers") or report.get("invalid_reasons")):
        hard_blockers.append("READY state cannot include blockers or invalid reasons")
        unsafe_flags.append("ready_with_issues")
    if apply_status == STATUS_INVALID and not report.get("invalid_reasons"):
        hard_blockers.append("INVALID state requires invalid_reasons")
        unsafe_flags.append("invalid_without_invalid_reasons")
    if not report.get("safe_next_action") or not isinstance(report.get("safe_next_action"), str):
        hard_blockers.append("safe_next_action required")
        unsafe_flags.append("safe_next_action_missing")
    if not report.get("stop_condition") or not isinstance(report.get("stop_condition"), str):
        hard_blockers.append("stop_condition required")
        unsafe_flags.append("stop_condition_missing")

    report_paths = report.get("report_paths")
    if not isinstance(report_paths, list) or len(report_paths) != 2:
        hard_blockers.append("report_paths must list JSON and markdown paths")
        unsafe_flags.append("report_paths_invalid")

    projected = " ".join(json.dumps(report.get("protection", {})).lower().split())
    secret_patterns = ("secret=", "token=", "password=", "api_key=", "apikey=", "bearer ", "sk-")
    for pattern in secret_patterns:
        if pattern in projected:
            hard_blockers.append("obvious secret assignment pattern detected in output")
            unsafe_flags.append("secret_pattern_detected")
            break

    status = "PASS" if not hard_blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers + hard_blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": list(dict.fromkeys(unsafe_flags)),
        "apply_status": apply_status,
    }


def summarize_runtime_apply_lane_preview(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "apply_status": None,
            "p2_bridge_status": None,
            "queue_gate_status": None,
            "runtime_proof_verdict": None,
            "blocked_count": 0,
            "invalid_reason_count": 0,
            "would_apply": None,
            "would_route": None,
            "would_execute": None,
            "runtime_launch": None,
            "runtime_execution": None,
            "safe_next_action": None,
        }
    return {
        "apply_status": report.get("apply_status"),
        "p2_bridge_status": _ensure_dict(report.get("p2_preview")).get("bridge_status"),
        "queue_gate_status": _ensure_dict(report.get("queue_mutation_gate_preview")).get("gate_status"),
        "runtime_proof_verdict": _ensure_dict(report.get("runtime_proof_gate")).get("final_verdict"),
        "blocked_count": len(report.get("blockers") or []),
        "invalid_reason_count": len(report.get("invalid_reasons") or []),
        "would_apply": report.get("would_apply"),
        "would_route": report.get("would_route"),
        "would_execute": report.get("would_execute"),
        "runtime_launch": report.get("runtime_launch"),
        "runtime_execution": report.get("runtime_execution"),
        "safe_next_action": report.get("safe_next_action"),
    }


def build_runtime_apply_lane_markdown_summary(report: dict[str, Any]) -> str:
    summary = summarize_runtime_apply_lane_preview(report)
    lines = [
        "# AI_OS Runtime APPLY Lane Preview",
        "",
        f"- apply_status: `{summary.get('apply_status')}`",
        f"- p2_bridge_status: `{summary.get('p2_bridge_status')}`",
        f"- queue_gate_status: `{summary.get('queue_gate_status')}`",
        f"- runtime_proof_verdict: `{summary.get('runtime_proof_verdict')}`",
        f"- would_apply: `{summary.get('would_apply')}`",
        f"- would_route: `{summary.get('would_route')}`",
        f"- would_execute: `{summary.get('would_execute')}`",
        f"- runtime_launch: `{summary.get('runtime_launch')}`",
        f"- runtime_execution: `{summary.get('runtime_execution')}`",
        f"- queue_mutation: `{report.get('queue_mutation')}`",
        f"- worker_inbox_mutation: `{report.get('worker_inbox_mutation')}`",
        f"- approval_inbox_mutation: `{report.get('approval_inbox_mutation')}`",
        f"- scheduler_registration: `{report.get('scheduler_registration')}`",
        f"- sos_notification: `{report.get('sos_notification')}`",
        f"- trading_execution: `{report.get('trading_execution')}`",
        f"- safe_next_action: {summary.get('safe_next_action')}",
        f"- blocked_count: {summary.get('blocked_count')}",
        "",
        "## Safety",
        "- This preview does not execute runtime, mutate worker inbox, mutate queue, launch services, arm SOS, or perform trading.",
        "",
        "## Blockers",
    ]
    if report.get("blockers"):
        lines.extend(f"- {item}" for item in report.get("blockers", []))
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_runtime_apply_lane_reports(
    report: dict[str, Any], *, output_dir: str | Path | None = None
) -> dict[str, str]:
    out_dir = Path(output_dir) if output_dir is not None else Path(report.get("repo_root", ".")) / REPORT_DIR
    if not out_dir.is_absolute():
        out_dir = Path(report.get("repo_root", ".")).resolve() / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / REPORT_JSON_NAME
    md_path = out_dir / REPORT_MD_NAME
    report["report_paths"] = [str(json_path), str(md_path)]
    report["validation"] = validate_runtime_apply_lane_preview(report)
    report["summary"] = summarize_runtime_apply_lane_preview(report)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_runtime_apply_lane_markdown_summary(report), encoding="utf-8")
    return {"json_path": str(json_path), "md_path": str(md_path)}


def run_runtime_apply_lane_preview(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    report = build_runtime_apply_lane_report(repo_root=repo_root, output_dir=output_dir, now=now)
    write_runtime_apply_lane_reports(report, output_dir=output_dir)
    return report


def _load_json_arg(raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    parsed = json.loads(raw)
    return parsed if isinstance(parsed, dict) else None


def _load_path_arg(path_text: str | None, repo_root: Path) -> dict[str, Any] | None:
    if path_text is None:
        return None
    path = Path(path_text)
    if not path.is_absolute():
        path = repo_root / path
    return _read_json(path)


def _cli():
    parser = argparse.ArgumentParser(description="Build runtime APPLY lane preview evidence.")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--output-dir", default=None, help="output report directory")
    parser.add_argument("--now", default=None, help="override UTC timestamp")
    parser.add_argument(
        "--p2-preview-json",
        default=None,
        help="optional inline P2 preview JSON override",
    )
    parser.add_argument(
        "--queue-mutation-gate-json",
        default=None,
        help="optional inline queue mutation gate JSON override",
    )
    parser.add_argument(
        "--runtime-proof-gate-json",
        default=None,
        help="optional inline runtime proof JSON override",
    )
    parser.add_argument("--p2-preview-path", default=None, help="optional path to P2 preview JSON")
    parser.add_argument("--queue-mutation-gate-path", default=None, help="optional path to queue mutation gate JSON")
    parser.add_argument("--runtime-proof-gate-path", default=None, help="optional path to runtime proof gate JSON")
    parser.add_argument("--no-write", action="store_true", help="build in-memory report only")
    return parser.parse_args()


def main() -> int:
    args = _cli()
    root = Path(args.repo_root)
    p2_preview = _load_json_arg(args.p2_preview_json)
    queue_gate = _load_json_arg(args.queue_mutation_gate_json)
    runtime_proof = _load_json_arg(args.runtime_proof_gate_json)
    if args.p2_preview_path:
        p2_preview = _load_path_arg(args.p2_preview_path, root)
    if args.queue_mutation_gate_path:
        queue_gate = _load_path_arg(args.queue_mutation_gate_path, root)
    if args.runtime_proof_gate_path:
        runtime_proof = _load_path_arg(args.runtime_proof_gate_path, root)

    report = build_runtime_apply_lane_report(
        repo_root=root,
        output_dir=args.output_dir,
        p2_preview=p2_preview,
        queue_mutation_gate_preview=queue_gate,
        runtime_proof_gate=runtime_proof,
        now=args.now,
    )
    if not args.no_write:
        write_runtime_apply_lane_reports(report, output_dir=args.output_dir)
    print(json.dumps(report["summary"], sort_keys=True, indent=2))
    return 0 if report["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
