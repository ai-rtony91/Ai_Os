"""AI_OS Operator Control Switch v1 (observe-only).

This module reads the merged runtime proof spine evidence, human-gate dogfood
evidence, autonomy-gap reassessment, and P2 enqueue bridge preview, then writes
a DRY_RUN operator control report. It does not mutate queues, worker inboxes,
active packets, telemetry, runtime, scheduler, SOS, trading, or approval state.

Pure standard library. JSON-only CLI. Safe default is DRY_RUN status.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_OPERATOR_CONTROL_SWITCH_REPORT.v1"
MODE = "DRY_RUN"
CONTROL_SURFACE = "operator_control_switch"
REPORT_JSON_NAME = "operator_control_switch_report.json"
REPORT_MD_NAME = "operator_control_switch_summary.md"
DEFAULT_REPORT_SUBDIR = Path("Reports") / "operator_control"
DEFAULT_HUMAN_GATE_REPORT = Path("Reports") / "human_gate" / "human_gate_packet_dogfood_report.json"
DEFAULT_AUTONOMY_GAP_REPORT = Path("Reports") / "autonomy_gap" / "autonomy_gap_reassessment_report.json"
DEFAULT_P2_BRIDGE_REPORT = Path("Reports") / "p2_enqueue_bridge" / "p2_enqueue_bridge_preview.json"

SAFE_ACTIONS = ("status", "inspect", "report", "preview")
UNSAFE_ACTIONS = ("enqueue", "dequeue", "dispatch", "execute", "approve", "mutate", "schedule", "sos", "live")
ALLOWED_CONTROL_STATUSES = {"READY_FOR_OPERATOR_REVIEW", "BLOCKED", "INVALID"}
PROTECTED_FALSE_FIELDS = [
    "approval_granted",
    "action_mutates_state",
    "execution_allowed",
    "dispatch_allowed",
    "apply_allowed",
    "runtime_launch_allowed",
    "runtime_mutation_allowed",
    "queue_mutation_allowed",
    "worker_inbox_mutation_allowed",
    "active_packet_mutation_allowed",
    "command_queue_mutation_allowed",
    "telemetry_mutation_allowed",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "sos_allowed",
    "live_trading_allowed",
    "credentials_accessed",
]


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _status(value: Any) -> str:
    return str(value or "").upper()


def _normalize_action(action: str | None) -> str:
    return str(action or "status").strip().lower() or "status"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def _path_hash(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_fingerprint(repo_root: Path, relative_path: Path) -> dict[str, Any]:
    path = repo_root / relative_path
    return {
        "path": str(relative_path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "size": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": _path_hash(path),
    }


def _default_source_fingerprints(repo_root: Path) -> list[dict[str, Any]]:
    return [
        _source_fingerprint(repo_root, DEFAULT_HUMAN_GATE_REPORT),
        _source_fingerprint(repo_root, DEFAULT_AUTONOMY_GAP_REPORT),
        _source_fingerprint(repo_root, DEFAULT_P2_BRIDGE_REPORT),
    ]


def load_default_evidence(repo_root: str | Path = ".") -> dict[str, Any]:
    repo_root_path = Path(repo_root)
    human_gate_report = repo_root_path / DEFAULT_HUMAN_GATE_REPORT
    autonomy_gap_report = repo_root_path / DEFAULT_AUTONOMY_GAP_REPORT
    p2_bridge_report = repo_root_path / DEFAULT_P2_BRIDGE_REPORT
    return {
        "human_gate_report": _load_json(human_gate_report),
        "autonomy_gap_report": _load_json(autonomy_gap_report),
        "p2_bridge_report": _load_json(p2_bridge_report),
        "evidence_loaded": {
            "human_gate_report": {"loaded": human_gate_report.exists(), "path": str(DEFAULT_HUMAN_GATE_REPORT)},
            "autonomy_gap_report": {"loaded": autonomy_gap_report.exists(), "path": str(DEFAULT_AUTONOMY_GAP_REPORT)},
            "p2_bridge_report": {"loaded": p2_bridge_report.exists(), "path": str(DEFAULT_P2_BRIDGE_REPORT)},
        },
        "source_fingerprints": _default_source_fingerprints(repo_root_path),
    }


def _queue_validation_status(human_gate_report: dict[str, Any]) -> str:
    queue_validation = _ensure_dict(human_gate_report.get("queue_validation_summary"))
    return _status(queue_validation.get("queue_validation_status") or queue_validation.get("status"))


def _runtime_gate_status(human_gate_report: dict[str, Any]) -> str:
    runtime_gate = _ensure_dict(human_gate_report.get("runtime_proof_gate_summary"))
    summary = _ensure_dict(human_gate_report.get("summary"))
    return _status(
        runtime_gate.get("final_verdict")
        or runtime_gate.get("runtime_proof_gate_verdict")
        or summary.get("runtime_proof_gate_verdict")
    )


def _human_gate_packet_status(human_gate_report: dict[str, Any]) -> str:
    packet = _ensure_dict(human_gate_report.get("human_gate_packet_summary"))
    summary = _ensure_dict(human_gate_report.get("summary"))
    return _status(packet.get("packet_status") or summary.get("packet_status"))


def _p2_readiness_status(autonomy_gap_report: dict[str, Any]) -> str:
    p2_readiness = _ensure_dict(autonomy_gap_report.get("p2_enqueue_bridge_readiness"))
    scorecard = _ensure_dict(autonomy_gap_report.get("readiness_scorecard"))
    p2_scorecard = _ensure_dict(scorecard.get("p2_enqueue_bridge_ready"))
    summary = _ensure_dict(autonomy_gap_report.get("summary"))
    return _status(p2_readiness.get("status") or p2_scorecard.get("status") or summary.get("p2_enqueue_bridge_ready"))


def _live_execution_status(autonomy_gap_report: dict[str, Any]) -> str:
    live_execution = _ensure_dict(autonomy_gap_report.get("live_execution_readiness"))
    summary = _ensure_dict(autonomy_gap_report.get("summary"))
    return _status(live_execution.get("status") or summary.get("live_execution_ready"))


def _recommended_next_lane(autonomy_gap_report: dict[str, Any]) -> str | None:
    summary_lane = _ensure_dict(autonomy_gap_report.get("summary")).get("recommended_next_lane")
    if summary_lane:
        return str(summary_lane)
    lanes = autonomy_gap_report.get("recommended_next_lanes") or []
    if lanes and isinstance(lanes[0], dict) and lanes[0].get("lane_id"):
        return str(lanes[0]["lane_id"])
    return None


def _human_gate_evidence_summary(human_gate_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "dogfood_status": _status(human_gate_report.get("dogfood_status")),
        "queue_validation_status": _queue_validation_status(human_gate_report),
        "runtime_proof_gate_status": _runtime_gate_status(human_gate_report),
        "human_gate_packet_status": _human_gate_packet_status(human_gate_report),
        "mutation_check_status": _status(human_gate_report.get("mutation_check_status")),
        "execution_allowed": human_gate_report.get("execution_allowed"),
        "queue_mutation_allowed": human_gate_report.get("queue_mutation_allowed"),
        "safe_next_action": human_gate_report.get("safe_next_action"),
        "stop_condition": human_gate_report.get("stop_condition"),
    }


def _autonomy_gap_evidence_summary(autonomy_gap_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "reassessment_status": _status(autonomy_gap_report.get("reassessment_status")),
        "p2_enqueue_bridge_readiness": _p2_readiness_status(autonomy_gap_report),
        "live_execution_readiness": _live_execution_status(autonomy_gap_report),
        "recommended_next_lane": _recommended_next_lane(autonomy_gap_report),
        "execution_allowed": autonomy_gap_report.get("execution_allowed"),
        "queue_mutation_allowed": autonomy_gap_report.get("queue_mutation_allowed"),
        "safe_next_action": autonomy_gap_report.get("safe_next_action"),
    }


def _p2_bridge_evidence_summary(p2_bridge_report: dict[str, Any]) -> dict[str, Any]:
    preview = _ensure_dict(p2_bridge_report.get("proposed_queue_item_preview"))
    summary = _ensure_dict(p2_bridge_report.get("summary"))
    return {
        "bridge_status": _status(p2_bridge_report.get("bridge_status")),
        "validation_status": _status(_ensure_dict(p2_bridge_report.get("validation")).get("status")),
        "recommended_next_lane": summary.get("recommended_next_lane") or preview.get("recommended_next_lane"),
        "enqueue_allowed": preview.get("enqueue_allowed"),
        "canonical_queue_write_allowed": preview.get("canonical_queue_write_allowed"),
        "worker_inbox_write_allowed": preview.get("worker_inbox_write_allowed"),
        "active_packet_write_allowed": preview.get("active_packet_write_allowed"),
        "runtime_execution_allowed": preview.get("runtime_execution_allowed"),
        "queue_mutation_allowed": p2_bridge_report.get("queue_mutation_allowed"),
        "safe_next_action": p2_bridge_report.get("safe_next_action"),
        "stop_condition": p2_bridge_report.get("stop_condition"),
    }


def _is_ready_status(value: Any) -> bool:
    return _status(value) in {"PASS", "READY", "READY_FOR_HUMAN_GATE", "READY_FOR_HUMAN_REVIEW", "READY_FOR_DRY_RUN_PREVIEW"}


def _collect_evidence_blockers(
    *,
    human_gate_summary: dict[str, Any],
    autonomy_gap_summary: dict[str, Any],
    p2_bridge_summary: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if not _is_ready_status(human_gate_summary.get("dogfood_status")):
        blockers.append(f"human gate dogfood status is {human_gate_summary.get('dogfood_status') or 'MISSING'}")
    if not _is_ready_status(human_gate_summary.get("queue_validation_status")):
        blockers.append(f"runtime queue validation status is {human_gate_summary.get('queue_validation_status') or 'MISSING'}")
    if not _is_ready_status(human_gate_summary.get("runtime_proof_gate_status")):
        blockers.append(f"runtime proof gate status is {human_gate_summary.get('runtime_proof_gate_status') or 'MISSING'}")
    if not _is_ready_status(human_gate_summary.get("human_gate_packet_status")):
        blockers.append(f"human gate packet status is {human_gate_summary.get('human_gate_packet_status') or 'MISSING'}")
    if not _is_ready_status(autonomy_gap_summary.get("reassessment_status")):
        blockers.append(f"autonomy gap reassessment status is {autonomy_gap_summary.get('reassessment_status') or 'MISSING'}")
    if not _is_ready_status(autonomy_gap_summary.get("p2_enqueue_bridge_readiness")):
        blockers.append(
            f"autonomy gap P2 enqueue bridge readiness is {autonomy_gap_summary.get('p2_enqueue_bridge_readiness') or 'MISSING'}"
        )
    if not _is_ready_status(p2_bridge_summary.get("bridge_status")):
        blockers.append(f"P2 enqueue bridge status is {p2_bridge_summary.get('bridge_status') or 'MISSING'}")
    if p2_bridge_summary.get("validation_status") and p2_bridge_summary.get("validation_status") != "PASS":
        blockers.append(f"P2 enqueue bridge validation is {p2_bridge_summary.get('validation_status')}")
    return blockers


def _collect_invalid_reasons(
    *,
    action: str,
    evidence_missing: list[str],
    human_gate_report: dict[str, Any],
    autonomy_gap_report: dict[str, Any],
    p2_bridge_report: dict[str, Any],
) -> list[str]:
    invalid: list[str] = []
    if action not in SAFE_ACTIONS:
        if action in UNSAFE_ACTIONS:
            invalid.append(f"unsafe action rejected: {action}")
        else:
            invalid.append(f"unsupported action rejected: {action}")
    for missing in evidence_missing:
        invalid.append(f"{missing} evidence missing")
    for field in PROTECTED_FALSE_FIELDS:
        if human_gate_report.get(field) is True:
            invalid.append(f"human gate evidence has unsafe true field: {field}")
        if autonomy_gap_report.get(field) is True:
            invalid.append(f"autonomy gap evidence has unsafe true field: {field}")
        if p2_bridge_report.get(field) is True:
            invalid.append(f"P2 bridge evidence has unsafe true field: {field}")
    p2_preview = _ensure_dict(p2_bridge_report.get("proposed_queue_item_preview"))
    for field in [
        "enqueue_allowed",
        "canonical_queue_write_allowed",
        "worker_inbox_write_allowed",
        "active_packet_write_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_execution_allowed",
        "scheduler_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
    ]:
        if p2_preview.get(field) is True:
            invalid.append(f"P2 bridge preview has unsafe true field: {field}")
    return invalid


def _next_blocked_lane(
    *,
    control_status: str,
    invalid_reasons: list[str],
    human_gate_summary: dict[str, Any],
    autonomy_gap_summary: dict[str, Any],
    p2_bridge_summary: dict[str, Any],
) -> str | None:
    if control_status == "INVALID":
        if invalid_reasons and "action rejected" in invalid_reasons[0]:
            return "OPERATOR_CONTROL_ACTION"
        return "OPERATOR_CONTROL_EVIDENCE"
    if control_status != "BLOCKED":
        return None
    if not _is_ready_status(p2_bridge_summary.get("bridge_status")):
        return "P2_ENQUEUE_BRIDGE"
    if not _is_ready_status(autonomy_gap_summary.get("p2_enqueue_bridge_readiness")):
        return autonomy_gap_summary.get("recommended_next_lane") or "AUTONOMY_GAP_REASSESSMENT"
    if not _is_ready_status(human_gate_summary.get("runtime_proof_gate_status")):
        return "RUNTIME_PROOF_GATE"
    if not _is_ready_status(human_gate_summary.get("human_gate_packet_status")):
        return "HUMAN_GATE_DOGFOOD"
    return autonomy_gap_summary.get("recommended_next_lane") or "QUEUE_BLOCKER_TRIAGE"


def _safe_next_action(
    *,
    control_status: str,
    action: str,
    next_blocked_lane: str | None,
) -> str:
    if control_status == "INVALID":
        if action in UNSAFE_ACTIONS:
            return "Use only status, inspect, report, or preview; unsafe operator actions require a separate approved APPLY packet."
        return "Restore required evidence files or use a supported safe action before relying on the operator control report."
    if control_status == "BLOCKED":
        return f"Review {next_blocked_lane or 'the blocked evidence lane'} and keep queue, runtime, scheduler, SOS, and trading mutation blocked."
    return "Operator reviews the consolidated readiness report; any real queue action requires a separate approved APPLY packet."


def _protected_boundary_report() -> dict[str, Any]:
    return {
        "canonical_queue_write_allowed": False,
        "worker_inbox_write_allowed": False,
        "active_packet_write_allowed": False,
        "command_queue_write_allowed": False,
        "approval_inbox_write_allowed": False,
        "telemetry_write_allowed": False,
        "runtime_launch_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "protected_paths": [
            "automation/orchestration/work_packets/active/",
            "automation/orchestration/workers/inbox/",
            "automation/orchestration/approval_inbox/",
            "automation/orchestration/command_queue/",
            "telemetry/",
            "services/",
            "apps/",
            "aios/modules/trader/",
        ],
    }


def build_operator_control_report(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    action: str = "status",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root_path = Path(repo_root)
    output_dir_path = Path(output_dir) if output_dir else repo_root_path / DEFAULT_REPORT_SUBDIR
    generated_at = _now(now)
    requested_action = _normalize_action(action)
    source_evidence = _deepcopy(evidence) if evidence is not None else load_default_evidence(repo_root_path)

    human_gate_report = _ensure_dict(source_evidence.get("human_gate_report"))
    autonomy_gap_report = _ensure_dict(source_evidence.get("autonomy_gap_report"))
    p2_bridge_report = _ensure_dict(source_evidence.get("p2_bridge_report"))
    evidence_missing: list[str] = []
    if not human_gate_report:
        evidence_missing.append("human_gate_report")
    if not autonomy_gap_report:
        evidence_missing.append("autonomy_gap_report")
    if not p2_bridge_report:
        evidence_missing.append("p2_bridge_report")

    human_gate_summary = _human_gate_evidence_summary(human_gate_report)
    autonomy_gap_summary = _autonomy_gap_evidence_summary(autonomy_gap_report)
    p2_bridge_summary = _p2_bridge_evidence_summary(p2_bridge_report)
    blockers = _collect_evidence_blockers(
        human_gate_summary=human_gate_summary,
        autonomy_gap_summary=autonomy_gap_summary,
        p2_bridge_summary=p2_bridge_summary,
    )
    invalid_reasons = _collect_invalid_reasons(
        action=requested_action,
        evidence_missing=evidence_missing,
        human_gate_report=human_gate_report,
        autonomy_gap_report=autonomy_gap_report,
        p2_bridge_report=p2_bridge_report,
    )

    if invalid_reasons:
        control_status = "INVALID"
    elif blockers:
        control_status = "BLOCKED"
    else:
        control_status = "READY_FOR_OPERATOR_REVIEW"

    next_blocked_lane = _next_blocked_lane(
        control_status=control_status,
        invalid_reasons=invalid_reasons,
        human_gate_summary=human_gate_summary,
        autonomy_gap_summary=autonomy_gap_summary,
        p2_bridge_summary=p2_bridge_summary,
    )
    report_paths = [
        str(output_dir_path / REPORT_JSON_NAME),
        str(output_dir_path / REPORT_MD_NAME),
    ]
    report = {
        "schema": SCHEMA,
        "mode": MODE,
        "control_surface": CONTROL_SURFACE,
        "generated_at_utc": generated_at,
        "repo_root": str(repo_root_path),
        "requested_action": requested_action,
        "action_allowed": requested_action in SAFE_ACTIONS,
        "action_mutates_state": False,
        "unsafe_action_rejected": requested_action in UNSAFE_ACTIONS,
        "safe_actions": list(SAFE_ACTIONS),
        "rejected_unsafe_actions": list(UNSAFE_ACTIONS),
        "control_status": control_status,
        "control_status_reason": (
            "Operator review can proceed from observe-only evidence."
            if control_status == "READY_FOR_OPERATOR_REVIEW"
            else "Operator review is blocked by unresolved evidence."
            if control_status == "BLOCKED"
            else "Operator control input or evidence is invalid for review."
        ),
        "evidence_loaded": source_evidence.get("evidence_loaded", {}),
        "evidence_missing": evidence_missing,
        "source_fingerprints": source_evidence.get("source_fingerprints", []),
        "report_paths": report_paths,
        "human_gate_evidence_summary": human_gate_summary,
        "autonomy_gap_evidence_summary": autonomy_gap_summary,
        "p2_bridge_evidence_summary": p2_bridge_summary,
        "operator_blockers": blockers,
        "invalid_reasons": invalid_reasons,
        "next_blocked_lane": next_blocked_lane,
        "safe_next_action": _safe_next_action(
            control_status=control_status,
            action=requested_action,
            next_blocked_lane=next_blocked_lane,
        ),
        "stop_condition": "Stop after writing operator control evidence; do not mutate queues, packets, inboxes, runtime, scheduler, SOS, trading, telemetry, or approvals.",
        "protected_boundaries": _protected_boundary_report(),
    }
    for field in PROTECTED_FALSE_FIELDS:
        report[field] = False
    report["validation"] = validate_operator_control_report(report)
    report["summary"] = summarize_operator_control_report(report)
    return report


def build_operator_control_markdown_summary(report: dict[str, Any]) -> str:
    report = report if isinstance(report, dict) else {}
    summary = summarize_operator_control_report(report)
    lines = [
        "# AI_OS Operator Control Switch Summary",
        "",
        f"- generated_at_utc: `{report.get('generated_at_utc')}`",
        f"- requested_action: `{report.get('requested_action')}`",
        f"- action_allowed: `{report.get('action_allowed')}`",
        f"- control_status: `{report.get('control_status')}`",
        f"- next_blocked_lane: `{report.get('next_blocked_lane')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Evidence",
        f"- human_gate_dogfood_status: `{summary.get('human_gate_dogfood_status')}`",
        f"- runtime_proof_gate_status: `{summary.get('runtime_proof_gate_status')}`",
        f"- autonomy_gap_status: `{summary.get('autonomy_gap_status')}`",
        f"- p2_enqueue_bridge_status: `{summary.get('p2_enqueue_bridge_status')}`",
        f"- p2_enqueue_allowed: `{summary.get('p2_enqueue_allowed')}`",
        "",
        "## Blockers",
    ]
    blockers = report.get("operator_blockers") or []
    invalid = report.get("invalid_reasons") or []
    if not blockers and not invalid:
        lines.append("- none")
    else:
        lines.extend(f"- {item}" for item in blockers)
        lines.extend(f"- {item}" for item in invalid)
    lines.extend(
        [
            "",
            "## Safety",
            "- This switch exposes status, inspect, report, and preview only.",
            "- Unsafe actions are rejected in code and represented as INVALID operator input.",
            "- This report does not enqueue, dequeue, dispatch, execute, approve, schedule, arm SOS, or touch live trading.",
            f"- stop_condition: {report.get('stop_condition')}",
            "",
        ]
    )
    return "\n".join(lines)


def write_operator_control_reports(
    report: dict[str, Any],
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    output_dir_path = Path(output_dir) if output_dir else Path(report.get("repo_root") or ".") / DEFAULT_REPORT_SUBDIR
    output_dir_path.mkdir(parents=True, exist_ok=True)
    json_path = output_dir_path / REPORT_JSON_NAME
    md_path = output_dir_path / REPORT_MD_NAME
    report["report_paths"] = [str(json_path), str(md_path)]
    report["validation"] = validate_operator_control_report(report)
    report["summary"] = summarize_operator_control_report(report)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_operator_control_markdown_summary(report), encoding="utf-8")
    return report


def validate_operator_control_report(report: dict[str, Any]) -> dict[str, Any]:
    required = [
        "schema",
        "mode",
        "control_surface",
        "requested_action",
        "action_allowed",
        "safe_actions",
        "rejected_unsafe_actions",
        "control_status",
        "report_paths",
        "human_gate_evidence_summary",
        "autonomy_gap_evidence_summary",
        "p2_bridge_evidence_summary",
        "operator_blockers",
        "invalid_reasons",
        "safe_next_action",
        "stop_condition",
        "protected_boundaries",
    ]
    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report must be an object"],
            "unsafe_flags": ["report_not_object"],
            "control_status": None,
        }

    blockers: list[str] = []
    unsafe_flags: list[str] = []
    for field in required:
        if field not in report:
            blockers.append(f"missing required field: {field}")
            unsafe_flags.append(f"missing_{field}")

    if report.get("schema") != SCHEMA:
        blockers.append(f"schema must be {SCHEMA}")
        unsafe_flags.append("schema_invalid")
    if report.get("mode") != MODE:
        blockers.append("mode must be DRY_RUN")
        unsafe_flags.append("mode_invalid")
    if report.get("control_surface") != CONTROL_SURFACE:
        blockers.append(f"control_surface must be {CONTROL_SURFACE}")
        unsafe_flags.append("control_surface_invalid")

    requested_action = _normalize_action(report.get("requested_action"))
    if requested_action in UNSAFE_ACTIONS:
        if report.get("action_allowed") is not False:
            blockers.append("unsafe requested_action must not be allowed")
            unsafe_flags.append("unsafe_action_allowed")
        if report.get("unsafe_action_rejected") is not True:
            blockers.append("unsafe requested_action must be explicitly rejected")
            unsafe_flags.append("unsafe_action_not_rejected")
    elif requested_action in SAFE_ACTIONS:
        if report.get("action_allowed") is not True:
            blockers.append("safe requested_action must be allowed")
            unsafe_flags.append("safe_action_not_allowed")
    else:
        if report.get("action_allowed") is not False:
            blockers.append("unsupported requested_action must not be allowed")
            unsafe_flags.append("unsupported_action_allowed")

    control_status = _status(report.get("control_status"))
    if control_status not in ALLOWED_CONTROL_STATUSES:
        blockers.append("control_status must be READY_FOR_OPERATOR_REVIEW, BLOCKED, or INVALID")
        unsafe_flags.append("control_status_invalid")
    if control_status == "READY_FOR_OPERATOR_REVIEW" and (report.get("operator_blockers") or report.get("invalid_reasons")):
        blockers.append("READY_FOR_OPERATOR_REVIEW cannot have blockers or invalid reasons")
        unsafe_flags.append("ready_with_blockers")
    if control_status == "BLOCKED" and not report.get("operator_blockers"):
        blockers.append("BLOCKED status requires operator_blockers")
        unsafe_flags.append("blocked_without_blockers")
    if control_status == "INVALID" and not report.get("invalid_reasons"):
        blockers.append("INVALID status requires invalid_reasons")
        unsafe_flags.append("invalid_without_reasons")

    for field in PROTECTED_FALSE_FIELDS:
        if report.get(field) is True:
            blockers.append(f"{field} must remain false")
            unsafe_flags.append(f"{field}_true")

    protected = _ensure_dict(report.get("protected_boundaries"))
    for field in [
        "canonical_queue_write_allowed",
        "worker_inbox_write_allowed",
        "active_packet_write_allowed",
        "command_queue_write_allowed",
        "approval_inbox_write_allowed",
        "telemetry_write_allowed",
        "runtime_launch_allowed",
        "scheduler_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
    ]:
        if protected.get(field) is True:
            blockers.append(f"protected_boundaries.{field} must remain false")
            unsafe_flags.append(f"protected_{field}_true")

    if not report.get("safe_next_action"):
        blockers.append("safe_next_action is required")
        unsafe_flags.append("safe_next_action_missing")
    if not report.get("stop_condition"):
        blockers.append("stop_condition is required")
        unsafe_flags.append("stop_condition_missing")
    report_paths = report.get("report_paths")
    if not isinstance(report_paths, list) or len(report_paths) != 2:
        blockers.append("report_paths must contain JSON and Markdown paths")
        unsafe_flags.append("report_paths_invalid")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "unsafe_flags": unsafe_flags,
        "control_status": report.get("control_status"),
    }


def summarize_operator_control_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "control_status": None,
            "requested_action": None,
            "action_allowed": None,
            "next_blocked_lane": None,
            "safe_next_action": None,
            "validation_status": None,
        }
    human_gate = _ensure_dict(report.get("human_gate_evidence_summary"))
    autonomy_gap = _ensure_dict(report.get("autonomy_gap_evidence_summary"))
    p2_bridge = _ensure_dict(report.get("p2_bridge_evidence_summary"))
    protected = _ensure_dict(report.get("protected_boundaries"))
    return {
        "control_status": report.get("control_status"),
        "requested_action": report.get("requested_action"),
        "action_allowed": report.get("action_allowed"),
        "unsafe_action_rejected": report.get("unsafe_action_rejected"),
        "next_blocked_lane": report.get("next_blocked_lane"),
        "human_gate_dogfood_status": human_gate.get("dogfood_status"),
        "runtime_proof_gate_status": human_gate.get("runtime_proof_gate_status"),
        "autonomy_gap_status": autonomy_gap.get("reassessment_status"),
        "autonomy_recommended_next_lane": autonomy_gap.get("recommended_next_lane"),
        "p2_enqueue_bridge_status": p2_bridge.get("bridge_status"),
        "p2_enqueue_allowed": p2_bridge.get("enqueue_allowed"),
        "queue_mutation_allowed": report.get("queue_mutation_allowed"),
        "runtime_launch_allowed": report.get("runtime_launch_allowed"),
        "scheduler_creation_allowed": report.get("scheduler_creation_allowed"),
        "sos_allowed": report.get("sos_allowed"),
        "live_trading_allowed": report.get("live_trading_allowed"),
        "canonical_queue_write_allowed": protected.get("canonical_queue_write_allowed"),
        "worker_inbox_write_allowed": protected.get("worker_inbox_write_allowed"),
        "active_packet_write_allowed": protected.get("active_packet_write_allowed"),
        "safe_next_action": report.get("safe_next_action"),
        "stop_condition": report.get("stop_condition"),
        "validation_status": _ensure_dict(report.get("validation")).get("status"),
        "report_paths": list(report.get("report_paths") or []),
    }


def run_operator_control_switch(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    action: str = "status",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = build_operator_control_report(
        repo_root=repo_root,
        output_dir=output_dir,
        now=now,
        action=action,
        evidence=evidence,
    )
    write_operator_control_reports(report, output_dir=output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the AI_OS operator control switch DRY_RUN report.")
    parser.add_argument("action", nargs="?", default="status", help="safe action: status, inspect, report, or preview")
    parser.add_argument("--action", dest="action_option", help="safe action override")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--output-dir", default=None, help="report output directory")
    parser.add_argument("--now", default=None, help="override generated_at_utc")
    parser.add_argument("--mode", default=MODE, choices=[MODE], help="safe mode; only DRY_RUN is supported")
    args = parser.parse_args()
    action = args.action_option or args.action
    report = run_operator_control_switch(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        now=args.now,
        action=action,
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    if report["validation"]["status"] != "PASS":
        return 3
    return 0 if report["action_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
