from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_QUEUE_SPECIFIC_APPROVAL_REQUEST.v1"
MODE = "DRY_RUN_FIRST"
TARGET_PACKET_ID = "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1"
EXACT_HUMAN_APPROVAL_PHRASE = (
    "ANTHONY_EXPLICITLY_APPROVES_P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1_FOR_DRY_RUN_QUEUE_REVIEW_ONLY"
)

DEFAULT_P2_REPORT = Path("Reports/p2_enqueue_bridge/p2_enqueue_bridge_preview.json")
DEFAULT_QUEUE_GATE_REPORT = Path("Reports/queue_mutation_gate/queue_mutation_gate_preview.json")
DEFAULT_APPROVAL_GATE = Path("automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json")
DEFAULT_APPROVAL_INBOX = Path("automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json")
DEFAULT_REPORT_DIR = Path("Reports/approval_state_transition")
DEFAULT_REQUEST_JSON_NAME = "p2_queue_approval_request.json"
DEFAULT_REQUEST_MD_NAME = "p2_queue_approval_request.md"
APPROVAL_GATE_OUTPUT_PATH = Path(
    "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1.json"
)
SECRET_MARKERS = (
    "sec" + "ret=",
    "tok" + "en=",
    "pass" + "word=",
    "api" + "_key=",
    "api" + "key=",
    "bear" + "er ",
    "s" + "k-",
)


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: str | Path) -> dict[str, Any] | None:
    source_path = Path(path)
    if not source_path.exists() or not source_path.is_file():
        return None
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _first_non_empty(mapping: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        value = mapping.get(name)
        if value not in (None, "", [], {}):
            return value
    return None


def _string(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def normalize_p2_queue_target(report: dict[str, Any]) -> dict[str, Any]:
    report = _ensure_dict(report)
    proposed = _ensure_dict(report.get("proposed_queue_item_preview"))
    target_packet_id = _string(_first_non_empty(proposed, ("packet_id", "preview_id"))) or TARGET_PACKET_ID
    allowed_paths = _as_list(_first_non_empty(proposed, ("allowed_paths",)))
    forbidden_paths = _as_list(_first_non_empty(proposed, ("forbidden_paths",)))
    return {
        "target_packet_id": target_packet_id,
        "preview_id": _string(_first_non_empty(proposed, ("preview_id",))) or target_packet_id,
        "lane_id": _string(_first_non_empty(proposed, ("lane_id", "lane_name", "lane"))),
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "bridge_status": _string(report.get("bridge_status")),
        "bridge_blockers": list(report.get("bridge_blockers") or []),
        "invalid_reasons": list(report.get("invalid_reasons") or []),
        "queue_validation_status": _string(
            _ensure_dict(_ensure_dict(report.get("human_gate_evidence_summary"))).get("queue_validation_status")
        ),
        "source_reports": list(_as_list(report.get("report_paths"))),
        "approval_evidence": _ensure_dict(proposed.get("approval_evidence")),
    }


def _normalise_gate_target(report: dict[str, Any]) -> dict[str, Any]:
    report = _ensure_dict(report)
    approval_check = _ensure_dict(report.get("approval_check"))
    proposed = _ensure_dict(report.get("proposed_queue_item"))
    return {
        "gate_status": _string(report.get("gate_status")),
        "gate_status_reason": _string(report.get("gate_status_reason")),
        "target_packet_id": _string(_first_non_empty(approval_check, ("target_packet_id",))) or _string(
            _first_non_empty(proposed, ("packet_id",))
        ),
        "approval_gate_packet_id": _string(_first_non_empty(approval_check, ("approval_gate_packet_id",))),
        "approval_gate_packet_mismatch": bool(approval_check.get("approval_gate_packet_mismatch")),
        "approval_evidence_present": bool(approval_check.get("approval_evidence_present")),
        "explicit_approval": bool(approval_check.get("explicit_approval")),
        "blockers": list(_ensure_dict(report.get("validation")).get("blockers") or []),
        "invalid_reasons": list(_ensure_dict(report.get("validation")).get("invalid_reasons") or []),
    }


def _approval_status_fields(
    *,
    approved: bool,
    human_approval_phrase: str | None,
    approved_by: str | None,
    approval_authority: str | None,
) -> tuple[str, bool, str | None, str | None, bool]:
    phrase_matches = human_approval_phrase == EXACT_HUMAN_APPROVAL_PHRASE
    if approved and phrase_matches and approval_authority and approved_by:
        return "approved_for_apply", True, approval_authority, approved_by, True
    return "pending_review", False, approval_authority, approved_by, False


def _approval_evidence(
    *,
    source_files: list[str],
    target_packet_id: str,
    current_gate_packet_id: str,
    current_gate_status: str,
    current_gate_pending: bool,
    approval_authority: str | None,
    approved_by: str | None,
    allowed_paths: list[str],
    blocked_paths: list[str],
    validator_chain_required: bool,
    commit_package_required: bool,
    explicit_approval: bool,
    approved_by_human: bool,
    authority_active: bool,
    approval_completed: bool,
) -> dict[str, Any]:
    packet_mismatch = bool(current_gate_packet_id and current_gate_packet_id != target_packet_id)
    non_authorizing_reason = (
        f"queue-specific approval required; existing apply gate targets {current_gate_packet_id or 'an unknown packet'}"
        if packet_mismatch
        else "queue-specific approval required; human approval is pending"
    )
    status = "APPROVED_FOR_DRY_RUN_QUEUE_REVIEW_ONLY" if explicit_approval else "PENDING_HUMAN_APPROVAL"
    evidence_type = "EXPLICIT_HUMAN_APPROVAL_PHRASE" if explicit_approval else "HUMAN_REVIEW_REQUIRED"
    return {
        "type": evidence_type,
        "status": status,
        "source_files": source_files,
        "target_packet_id": target_packet_id,
        "packet_id": current_gate_packet_id or None,
        "approval_gate_packet_id": current_gate_packet_id or None,
        "approval_gate_packet_mismatch": packet_mismatch,
        "approval_status": "approved_for_apply" if explicit_approval else "pending_review",
        "approved_by_human": approved_by_human,
        "approval_granted": explicit_approval,
        "approval_authority": approval_authority,
        "approved_by": approved_by,
        "allowed_paths": allowed_paths,
        "blocked_paths": blocked_paths,
        "validator_chain_required": validator_chain_required,
        "commit_package_required": commit_package_required,
        "explicit_approval": explicit_approval,
        "non_authorizing_placeholder": not explicit_approval,
        "non_authorizing_reason": non_authorizing_reason,
        "authority_active": authority_active,
        "approval_completed": approval_completed,
        "apply_gate_pending": not explicit_approval and current_gate_pending,
        "missing_authority_fields": not bool(approval_authority and approved_by),
        "approval_gate_output_path": APPROVAL_GATE_OUTPUT_PATH.as_posix(),
        "approval_gate_write_allowed": explicit_approval,
    }


def validate_queue_specific_approval_request(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    checked_fields = [
        "schema",
        "mode",
        "target_packet_id",
        "approval_status",
        "approved_by_human",
        "approval_authority",
        "approved_by",
        "queue_write_allowed",
        "canonical_queue_mutation_allowed",
        "worker_inbox_mutation_allowed",
        "runtime_execution_allowed",
        "scheduler_registration_allowed",
        "sos_notification_allowed",
        "live_trading_allowed",
        "validator_chain_required",
        "commit_package_required",
        "allowed_paths",
        "blocked_paths",
        "source_p2_report",
        "source_queue_gate_report",
        "approval_evidence",
        "safe_next_action",
        "stop_condition",
    ]
    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report must be an object"],
            "checked_fields": checked_fields,
            "unsafe_flags": ["report_not_object"],
        }

    for field in checked_fields:
        if field not in report:
            blockers.append(f"missing required field: {field}")

    if _string(report.get("schema")) != SCHEMA:
        blockers.append("schema must be AIOS_QUEUE_SPECIFIC_APPROVAL_REQUEST.v1")
    if _string(report.get("mode")) != MODE:
        blockers.append("mode must be DRY_RUN_FIRST")
    if _string(report.get("target_packet_id")) != TARGET_PACKET_ID:
        blockers.append("target_packet_id must equal P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1")
    if not _as_list(report.get("allowed_paths")):
        blockers.append("allowed_paths must be a non-empty list")
    if not _as_list(report.get("blocked_paths")):
        blockers.append("blocked_paths must be a non-empty list")
    if report.get("validator_chain_required") is not True:
        blockers.append("validator_chain_required must be true")
    if report.get("commit_package_required") is not True:
        blockers.append("commit_package_required must be true")
    for field in (
        "queue_write_allowed",
        "canonical_queue_mutation_allowed",
        "worker_inbox_mutation_allowed",
        "runtime_execution_allowed",
        "scheduler_registration_allowed",
        "sos_notification_allowed",
        "live_trading_allowed",
    ):
        if report.get(field) is True:
            blockers.append(f"{field} must remain false")

    approval_evidence = _ensure_dict(report.get("approval_evidence"))
    if not approval_evidence:
        blockers.append("approval_evidence must be present")
    else:
        if _string(approval_evidence.get("target_packet_id")) != TARGET_PACKET_ID:
            blockers.append("approval_evidence.target_packet_id must equal P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1")
        if not _as_list(approval_evidence.get("source_files")):
            blockers.append("approval_evidence.source_files must be non-empty")
        if approval_evidence.get("approval_granted") is True and approval_evidence.get("explicit_approval") is not True:
            blockers.append("approval_evidence.explicit_approval must be true when approval_granted is true")
        if _string(approval_evidence.get("status")) == "APPROVED_FOR_DRY_RUN_QUEUE_REVIEW_ONLY":
            if approval_evidence.get("approved_by_human") is not True:
                blockers.append("approved approval_evidence must set approved_by_human true")
            if not _string(approval_evidence.get("approval_authority")):
                blockers.append("approved approval_evidence must include approval_authority")
            if not _string(approval_evidence.get("approved_by")):
                blockers.append("approved approval_evidence must include approved_by")
        if any(
            isinstance(value, str) and any(marker in value.lower() for marker in SECRET_MARKERS)
            for value in approval_evidence.values()
        ):
            blockers.append("approval_evidence contains secret-shaped values")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": list(dict.fromkeys(blockers)),
        "checked_fields": checked_fields,
        "safe_next_action": (
            "P2 queue approval request is ready for human review."
            if status == "PASS"
            else "Repair the request shape before submitting a human approval checkpoint."
        ),
    }


def summarize_queue_specific_approval_request(report: dict[str, Any]) -> dict[str, Any]:
    validation = _ensure_dict(report.get("validation"))
    approval_evidence = _ensure_dict(report.get("approval_evidence"))
    return {
        "schema": report.get("schema"),
        "target_packet_id": report.get("target_packet_id"),
        "approval_status": report.get("approval_status"),
        "approval_gate_packet_id": approval_evidence.get("approval_gate_packet_id"),
        "approval_gate_packet_mismatch": approval_evidence.get("approval_gate_packet_mismatch"),
        "queue_gate_status": report.get("queue_gate_status"),
        "queue_write_allowed": report.get("queue_write_allowed"),
        "approval_granted": approval_evidence.get("approval_granted"),
        "explicit_approval": approval_evidence.get("explicit_approval"),
        "validation_status": validation.get("status"),
        "blocker_count": len(validation.get("blockers") or []),
        "report_paths": list(report.get("report_paths") or []),
        "safe_next_action": report.get("safe_next_action"),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    validation = _ensure_dict(report.get("validation"))
    approval_evidence = _ensure_dict(report.get("approval_evidence"))
    lines = [
        "# AI_OS Queue Specific Approval Request",
        "",
        f"- schema: `{report.get('schema')}`",
        f"- mode: `{report.get('mode')}`",
        f"- target_packet_id: `{report.get('target_packet_id')}`",
        f"- approval_status: `{report.get('approval_status')}`",
        f"- approved_by_human: `{report.get('approved_by_human')}`",
        f"- approval_gate_output_path: `{report.get('approval_gate_output_path')}`",
        f"- queue_gate_status: `{report.get('queue_gate_status')}`",
        f"- approval_gate_packet_mismatch: `{approval_evidence.get('approval_gate_packet_mismatch')}`",
        f"- explicit_approval: `{approval_evidence.get('explicit_approval')}`",
        f"- queue_write_allowed: `{report.get('queue_write_allowed')}`",
        f"- canonical_queue_mutation_allowed: `{report.get('canonical_queue_mutation_allowed')}`",
        f"- worker_inbox_mutation_allowed: `{report.get('worker_inbox_mutation_allowed')}`",
        f"- runtime_execution_allowed: `{report.get('runtime_execution_allowed')}`",
        f"- scheduler_registration_allowed: `{report.get('scheduler_registration_allowed')}`",
        f"- sos_notification_allowed: `{report.get('sos_notification_allowed')}`",
        f"- live_trading_allowed: `{report.get('live_trading_allowed')}`",
        f"- validation_status: `{validation.get('status')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Human Approval Checkpoint",
        f"- Required exact phrase: `{EXACT_HUMAN_APPROVAL_PHRASE}`",
        "- This draft does not mutate approval inbox state.",
        "- This draft does not authorize the canonical active queue.",
        "- A mismatched heartbeat gate must not be repurposed.",
        "",
        "## Source Files",
    ]
    for source in _as_list(approval_evidence.get("source_files")):
        lines.append(f"- {source}")
    lines.extend(
        [
            "",
            "## Blockers",
        ]
    )
    blockers = validation.get("blockers") or []
    lines.extend([f"- {blocker}" for blocker in blockers] or ["- none"])
    lines.extend(
        [
            "",
            "## Safety",
            "- Draft only unless the exact human approval phrase is present and write-gate behavior is explicitly requested.",
            "- No queue write, worker inbox mutation, runtime execution, scheduler registration, SOS send, live trading, commit, or push occurs here.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_queue_specific_approval_request(
    report: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, str]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / DEFAULT_REQUEST_JSON_NAME
    md_path = out_dir / DEFAULT_REQUEST_MD_NAME
    report = dict(report)
    report["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    report["validation"] = validate_queue_specific_approval_request(report)
    report["summary"] = summarize_queue_specific_approval_request(report)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    return {"json_path": json_path.as_posix(), "md_path": md_path.as_posix()}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _queue_specific_gate_payload(report: dict[str, Any]) -> dict[str, Any]:
    approval_evidence = _ensure_dict(report.get("approval_evidence"))
    return {
        "schema": "AIOS_APPLY_APPROVAL_GATE.v1",
        "approval_gate_id": "APPLY_APPROVAL_GATE_P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
        "packet_id": report.get("target_packet_id"),
        "approval_status": report.get("approval_status"),
        "approved_by_human": report.get("approved_by_human"),
        "approval_authority": report.get("approval_authority"),
        "approved_by": report.get("approved_by"),
        "validator_chain_required": report.get("validator_chain_required"),
        "commit_package_required": report.get("commit_package_required"),
        "queue_write_allowed": report.get("queue_write_allowed"),
        "canonical_queue_mutation_allowed": report.get("canonical_queue_mutation_allowed"),
        "worker_inbox_mutation_allowed": report.get("worker_inbox_mutation_allowed"),
        "runtime_execution_allowed": report.get("runtime_execution_allowed"),
        "scheduler_registration_allowed": report.get("scheduler_registration_allowed"),
        "sos_notification_allowed": report.get("sos_notification_allowed"),
        "live_trading_allowed": report.get("live_trading_allowed"),
        "allowed_paths": list(report.get("allowed_paths") or []),
        "blocked_paths": list(report.get("blocked_paths") or []),
        "approval_evidence": {
            "type": approval_evidence.get("type"),
            "phrase_hash_or_label": "ANTHONY_EXPLICIT_P2_QUEUE_REVIEW_APPROVAL",
            "status": approval_evidence.get("status"),
            "scope": "P2 queue mutation gate review only",
            "target_packet_id": report.get("target_packet_id"),
            "approval_gate_packet_id": approval_evidence.get("approval_gate_packet_id"),
            "approval_gate_packet_mismatch": approval_evidence.get("approval_gate_packet_mismatch"),
        },
        "safe_next_action": "Rerun P2 bridge and queue mutation gate; do not mutate active queue.",
    }


def build_queue_specific_approval_request(
    repo_root: str | Path = ".",
    approved: bool = False,
    approved_by: str | None = None,
    approval_authority: str | None = None,
    now: str | None = None,
    human_approval_phrase: str | None = None,
    write_approval_gate: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root)
    p2_report = load_json(root / DEFAULT_P2_REPORT) or {}
    queue_gate_report = load_json(root / DEFAULT_QUEUE_GATE_REPORT) or {}
    approval_gate = load_json(root / DEFAULT_APPROVAL_GATE) or {}
    approval_inbox = load_json(root / DEFAULT_APPROVAL_INBOX) or {}
    p2_target = normalize_p2_queue_target(p2_report)
    gate_target = _normalise_gate_target(queue_gate_report)

    source_files = [
        str((root / DEFAULT_P2_REPORT).as_posix()),
        str((root / DEFAULT_QUEUE_GATE_REPORT).as_posix()),
        str((root / DEFAULT_APPROVAL_GATE).as_posix()),
        str((root / DEFAULT_APPROVAL_INBOX).as_posix()),
    ]

    current_gate_packet_id = _string(
        _first_non_empty(approval_gate, ("packet_id", "approval_gate_id"))
    )
    approval_authority_source = approval_authority or _string(
        _first_non_empty(approval_inbox, ("approval_authority",))
    ) or _string(_first_non_empty(approval_gate, ("approval_authority", "bound_by")))
    approved_by_value = approved_by or approval_authority_source or None
    allowed_paths = list(p2_target["allowed_paths"])
    blocked_paths = list(p2_target["forbidden_paths"])
    validator_chain_required = True
    commit_package_required = True
    authority_active = _string(approval_inbox.get("authority_status")).lower() == "active_authority"
    approval_completed = _string(approval_inbox.get("approval_status")).lower() == "completed"

    approval_status, approved_by_human, approval_authority_value, approved_by_value, explicit_approval = (
        _approval_status_fields(
            approved=approved,
            human_approval_phrase=human_approval_phrase,
            approved_by=approved_by_value,
            approval_authority=approval_authority_source or approved_by_value,
        )
    )

    if not approval_authority_value:
        approval_authority_value = approval_authority_source or None
    if approved and human_approval_phrase != EXACT_HUMAN_APPROVAL_PHRASE:
        approval_status = "pending_review"
        approved_by_human = False
        explicit_approval = False
    if not approved:
        approval_status = "pending_review"
        approved_by_human = False
        explicit_approval = False
        approved_by_value = None

    approval_evidence = _approval_evidence(
        source_files=source_files,
        target_packet_id=p2_target["target_packet_id"],
        current_gate_packet_id=current_gate_packet_id or gate_target["approval_gate_packet_id"],
        current_gate_status=_string(approval_gate.get("approval_status")),
        current_gate_pending=_string(approval_gate.get("approval_status")) == "pending_review",
        approval_authority=approval_authority_value,
        approved_by=approved_by_value,
        allowed_paths=allowed_paths,
        blocked_paths=blocked_paths,
        validator_chain_required=validator_chain_required,
        commit_package_required=commit_package_required,
        explicit_approval=explicit_approval,
        approved_by_human=approved_by_human,
        authority_active=authority_active,
        approval_completed=approval_completed,
    )

    report = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": _now(now),
        "target_packet_id": p2_target["target_packet_id"],
        "approval_status": approval_status,
        "approved_by_human": approved_by_human,
        "approval_authority": approval_authority_value,
        "approved_by": approved_by_value,
        "queue_write_allowed": False,
        "canonical_queue_mutation_allowed": False,
        "worker_inbox_mutation_allowed": False,
        "runtime_execution_allowed": False,
        "scheduler_registration_allowed": False,
        "sos_notification_allowed": False,
        "live_trading_allowed": False,
        "validator_chain_required": validator_chain_required,
        "commit_package_required": commit_package_required,
        "allowed_paths": allowed_paths,
        "blocked_paths": blocked_paths,
        "source_p2_report": str((root / DEFAULT_P2_REPORT).as_posix()),
        "source_queue_gate_report": str((root / DEFAULT_QUEUE_GATE_REPORT).as_posix()),
        "source_approval_gate": str((root / DEFAULT_APPROVAL_GATE).as_posix()),
        "source_approval_inbox": str((root / DEFAULT_APPROVAL_INBOX).as_posix()),
        "queue_gate_status": gate_target["gate_status"],
        "queue_gate_blockers": list(gate_target["blockers"]),
        "queue_gate_invalid_reasons": list(gate_target["invalid_reasons"]),
        "approval_gate_output_path": APPROVAL_GATE_OUTPUT_PATH.as_posix(),
        "approval_gate_write_allowed": bool(
            explicit_approval and write_approval_gate and human_approval_phrase == EXACT_HUMAN_APPROVAL_PHRASE
        ),
        "approval_evidence": approval_evidence,
        "safe_next_action": (
            "Anthony must review the draft request and confirm the exact human approval phrase before any queue-specific gate write."
            if not explicit_approval
            else "Queue-specific approval is explicit in memory only; do not mutate the canonical active queue."
        ),
        "stop_condition": "Stop before mutating approval inbox, active queue, worker inbox, runtime, scheduler, SOS, live trading, commit, or push.",
        "approval_attempt_rejected": bool(approved and human_approval_phrase != EXACT_HUMAN_APPROVAL_PHRASE),
    }
    report["validation"] = validate_queue_specific_approval_request(report)
    report["summary"] = summarize_queue_specific_approval_request(report)
    return report


def _write_queue_specific_approval_gate(report: dict[str, Any], repo_root: Path) -> Path | None:
    if not report.get("approval_gate_write_allowed"):
        return None
    gate_path = repo_root / APPROVAL_GATE_OUTPUT_PATH
    _write_json(gate_path, _queue_specific_gate_payload(report))
    return gate_path


def run_queue_specific_approval_request(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    approved: bool = False,
    approved_by: str | None = None,
    approval_authority: str | None = None,
    now: str | None = None,
    human_approval_phrase: str | None = None,
    write_approval_gate: bool = False,
) -> dict[str, Any]:
    report = build_queue_specific_approval_request(
        repo_root=repo_root,
        approved=approved,
        approved_by=approved_by,
        approval_authority=approval_authority,
        now=now,
        human_approval_phrase=human_approval_phrase,
        write_approval_gate=write_approval_gate,
    )
    output_dir_path = Path(output_dir) if output_dir else Path(repo_root) / DEFAULT_REPORT_DIR
    write_queue_specific_approval_request(report, output_dir_path)
    if write_approval_gate:
        _write_queue_specific_approval_gate(report, Path(repo_root))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the AI_OS queue-specific approval request draft.")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--output-dir", default=None, help="optional output directory")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp")
    parser.add_argument("--approved", action="store_true", help="allow an in-memory approved draft when phrase matches")
    parser.add_argument("--approved-by", default=None, help="name of the approver")
    parser.add_argument("--approval-authority", default=None, help="approval authority source label")
    parser.add_argument("--human-approval-phrase", default=None, help="exact human approval phrase")
    parser.add_argument("--no-write", action="store_true", help="skip writing the draft report")
    parser.add_argument("--write-approval-gate", action="store_true", help="attempt to write the queue-specific approval gate")
    args = parser.parse_args()

    report = build_queue_specific_approval_request(
        repo_root=args.repo_root,
        approved=args.approved,
        approved_by=args.approved_by,
        approval_authority=args.approval_authority,
        now=args.now,
        human_approval_phrase=args.human_approval_phrase,
        write_approval_gate=args.write_approval_gate,
    )
    if not args.no_write:
        output_dir = Path(args.output_dir) if args.output_dir else Path(args.repo_root) / DEFAULT_REPORT_DIR
        write_queue_specific_approval_request(report, output_dir)
        if args.write_approval_gate:
            _write_queue_specific_approval_gate(report, Path(args.repo_root))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
