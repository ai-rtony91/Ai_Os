"""AI_OS P2 enqueue bridge preview (observe-only).

This module consumes the existing human-gate dogfood and autonomy-gap reports,
then writes a DRY_RUN preview of the queue item that would be considered by a
future enqueue step. It does not write to the canonical runtime queue, worker
inbox, active packets, telemetry, scheduler, SOS, runtime, or approval state.

Pure standard library. JSON-only CLI. Safe default is DRY_RUN.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_P2_ENQUEUE_BRIDGE_PREVIEW.v1"
MODE = "DRY_RUN"
BRIDGE_TYPE = "p2_enqueue_bridge"
REPORT_JSON_NAME = "p2_enqueue_bridge_preview.json"
REPORT_MD_NAME = "p2_enqueue_bridge_summary.md"
DEFAULT_REPORT_SUBDIR = Path("Reports") / "p2_enqueue_bridge"
DEFAULT_HUMAN_GATE_REPORT = Path("Reports") / "human_gate" / "human_gate_packet_dogfood_report.json"
DEFAULT_HUMAN_GATE_SUMMARY = Path("Reports") / "human_gate" / "human_gate_packet_dogfood_summary.md"
DEFAULT_AUTONOMY_GAP_REPORT = Path("Reports") / "autonomy_gap" / "autonomy_gap_reassessment_report.json"
DEFAULT_AUTONOMY_GAP_SUMMARY = Path("Reports") / "autonomy_gap" / "autonomy_gap_reassessment_summary.md"

PROPOSED_QUEUE_ITEM_ALLOWED_PATHS = [
    "automation/orchestration/work_packets/",
]
PROPOSED_QUEUE_ITEM_FORBIDDEN_PATHS = [
    "automation/orchestration/work_packets/active/",
    "automation/orchestration/work_packets/blocked/",
    "automation/orchestration/work_packets/complete/",
    "automation/orchestration/workers/inbox/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/command_queue/",
    "telemetry/",
    "services/",
    "apps/",
    "aios/modules/trader/",
    "aios.ps1",
]

ALLOWED_BRIDGE_STATUSES = {"READY_FOR_DRY_RUN_PREVIEW", "BLOCKED", "INVALID"}
UNSAFE_BOOL_FIELDS = [
    "approval_granted",
    "execution_allowed",
    "dispatch_allowed",
    "apply_allowed",
    "runtime_launch_allowed",
    "runtime_mutation_allowed",
    "queue_mutation_allowed",
    "telemetry_mutation_allowed",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "sos_allowed",
    "live_trading_allowed",
    "credentials_accessed",
    "unsafe_autonomy_claim",
    "vacation_mode_complete",
]
PREVIEW_FALSE_FIELDS = [
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
]


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def _load_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _status(value: Any) -> str:
    return str(value or "").upper()


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
        _source_fingerprint(repo_root, DEFAULT_HUMAN_GATE_SUMMARY),
        _source_fingerprint(repo_root, DEFAULT_AUTONOMY_GAP_REPORT),
        _source_fingerprint(repo_root, DEFAULT_AUTONOMY_GAP_SUMMARY),
    ]


def load_default_evidence(repo_root: str | Path = ".") -> dict[str, Any]:
    repo_root_path = Path(repo_root)
    human_gate_report = repo_root_path / DEFAULT_HUMAN_GATE_REPORT
    human_gate_summary = repo_root_path / DEFAULT_HUMAN_GATE_SUMMARY
    autonomy_gap_report = repo_root_path / DEFAULT_AUTONOMY_GAP_REPORT
    autonomy_gap_summary = repo_root_path / DEFAULT_AUTONOMY_GAP_SUMMARY
    return {
        "human_gate_report": _load_json(human_gate_report),
        "human_gate_summary_text": _load_text(human_gate_summary),
        "autonomy_gap_report": _load_json(autonomy_gap_report),
        "autonomy_gap_summary_text": _load_text(autonomy_gap_summary),
        "evidence_loaded": {
            "human_gate_report": {"loaded": human_gate_report.exists(), "path": str(DEFAULT_HUMAN_GATE_REPORT)},
            "human_gate_summary": {"loaded": human_gate_summary.exists(), "path": str(DEFAULT_HUMAN_GATE_SUMMARY)},
            "autonomy_gap_report": {"loaded": autonomy_gap_report.exists(), "path": str(DEFAULT_AUTONOMY_GAP_REPORT)},
            "autonomy_gap_summary": {"loaded": autonomy_gap_summary.exists(), "path": str(DEFAULT_AUTONOMY_GAP_SUMMARY)},
        },
        "source_fingerprints": _default_source_fingerprints(repo_root_path),
    }


def _queue_validation_status(human_gate_report: dict[str, Any]) -> str:
    queue_validation = _ensure_dict(human_gate_report.get("queue_validation_summary"))
    return _status(queue_validation.get("queue_validation_status") or queue_validation.get("status"))


def _runtime_gate_status(human_gate_report: dict[str, Any]) -> str:
    runtime_gate = _ensure_dict(human_gate_report.get("runtime_proof_gate_summary"))
    return _status(
        runtime_gate.get("final_verdict")
        or runtime_gate.get("runtime_proof_gate_verdict")
        or _ensure_dict(human_gate_report.get("summary")).get("runtime_proof_gate_verdict")
    )


def _human_gate_packet_status(human_gate_report: dict[str, Any]) -> str:
    packet = _ensure_dict(human_gate_report.get("human_gate_packet_summary"))
    return _status(packet.get("packet_status") or _ensure_dict(human_gate_report.get("summary")).get("packet_status"))


def _p2_readiness_status(autonomy_gap_report: dict[str, Any]) -> str:
    direct = _ensure_dict(autonomy_gap_report.get("p2_enqueue_bridge_readiness"))
    scorecard = _ensure_dict(autonomy_gap_report.get("readiness_scorecard"))
    scorecard_p2 = _ensure_dict(scorecard.get("p2_enqueue_bridge_ready"))
    summary = _ensure_dict(autonomy_gap_report.get("summary"))
    return _status(direct.get("status") or scorecard_p2.get("status") or summary.get("p2_enqueue_bridge_ready"))


def _collect_bridge_blockers(
    *,
    evidence_missing: list[str],
    human_gate_report: dict[str, Any],
    autonomy_gap_report: dict[str, Any],
) -> list[str]:
    blockers = list(evidence_missing)
    dogfood_status = _status(human_gate_report.get("dogfood_status"))
    reassessment_status = _status(autonomy_gap_report.get("reassessment_status"))
    queue_status = _queue_validation_status(human_gate_report)
    runtime_gate_status = _runtime_gate_status(human_gate_report)
    packet_status = _human_gate_packet_status(human_gate_report)
    p2_status = _p2_readiness_status(autonomy_gap_report)

    if dogfood_status in {"BLOCKED", "INVALID"}:
        blockers.append(f"human gate dogfood status is {dogfood_status}")
    if reassessment_status in {"BLOCKED", "INVALID"}:
        blockers.append(f"autonomy gap reassessment status is {reassessment_status}")
    if queue_status == "BLOCK":
        blockers.append("queue validation is BLOCK")
    if runtime_gate_status == "BLOCKED":
        blockers.append("runtime proof gate is BLOCKED")
    if packet_status == "BLOCKED":
        blockers.append("human gate packet is BLOCKED")
    if p2_status == "BLOCKED":
        blockers.append("autonomy gap marks P2 enqueue bridge as BLOCKED")
    return list(dict.fromkeys(blockers))


def _collect_invalid_reasons(
    *,
    human_gate_report: dict[str, Any],
    autonomy_gap_report: dict[str, Any],
) -> list[str]:
    invalid_reasons: list[str] = []
    if _status(human_gate_report.get("dogfood_status")) == "INVALID":
        invalid_reasons.append("human gate dogfood report is INVALID")
    if _status(autonomy_gap_report.get("reassessment_status")) == "INVALID":
        invalid_reasons.append("autonomy gap reassessment is INVALID")
    for field in UNSAFE_BOOL_FIELDS:
        if human_gate_report.get(field) is True:
            invalid_reasons.append(f"human gate report has unsafe true field: {field}")
        if autonomy_gap_report.get(field) is True:
            invalid_reasons.append(f"autonomy gap report has unsafe true field: {field}")
    if human_gate_report.get("mutated_sources"):
        invalid_reasons.append("human gate dogfood report recorded mutated sources")
    return list(dict.fromkeys(invalid_reasons))


def _build_proposed_queue_item_preview(
    *,
    generated_at: str,
    bridge_status: str,
    bridge_blockers: list[str],
    invalid_reasons: list[str],
    human_gate_report: dict[str, Any],
    autonomy_gap_report: dict[str, Any],
) -> dict[str, Any]:
    recommended_lanes = autonomy_gap_report.get("recommended_next_lanes") if isinstance(autonomy_gap_report.get("recommended_next_lanes"), list) else []
    next_lane = recommended_lanes[0] if recommended_lanes and isinstance(recommended_lanes[0], dict) else {}
    return {
        "preview_id": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
        "schema_version": "AIOS_RUNTIME_EXECUTION_QUEUE.v1",
        "generated_at_utc": generated_at,
        "mode": "DRY_RUN_PREVIEW_ONLY",
        "preview_state": "PREVIEW_READY" if bridge_status == "READY_FOR_DRY_RUN_PREVIEW" else "PREVIEW_BLOCKED",
        "lane_id": "p2_review_to_queue_enqueue_bridge",
        "title": "P2 review-to-queue enqueue bridge preview",
        "source_reports": [
            str(DEFAULT_HUMAN_GATE_REPORT),
            str(DEFAULT_AUTONOMY_GAP_REPORT),
        ],
        "allowed_paths": list(PROPOSED_QUEUE_ITEM_ALLOWED_PATHS),
        "forbidden_paths": list(PROPOSED_QUEUE_ITEM_FORBIDDEN_PATHS),
        "evidence_status": {
            "dogfood_status": human_gate_report.get("dogfood_status"),
            "reassessment_status": autonomy_gap_report.get("reassessment_status"),
            "queue_validation_status": _queue_validation_status(human_gate_report),
            "runtime_proof_gate_status": _runtime_gate_status(human_gate_report),
            "human_gate_packet_status": _human_gate_packet_status(human_gate_report),
            "p2_enqueue_bridge_readiness": _p2_readiness_status(autonomy_gap_report),
        },
        "recommended_next_lane": next_lane.get("lane_id") or _ensure_dict(autonomy_gap_report.get("summary")).get("recommended_next_lane"),
        "bridge_blockers": list(bridge_blockers),
        "invalid_reasons": list(invalid_reasons),
        "enqueue_allowed": False,
        "canonical_queue_write_allowed": False,
        "worker_inbox_write_allowed": False,
        "active_packet_write_allowed": False,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_execution_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "consumer": "canonical_runtime_execution_queue_preview_only",
        "safe_next_action": "Review this preview; a separate approved packet is required before any real enqueue.",
        "stop_condition": "Stop before writing to queue, worker inbox, active packets, runtime, scheduler, SOS, or approval state.",
    }


def build_p2_enqueue_bridge_report(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    evidence: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    repo_root_path = Path(repo_root)
    output_dir_path = Path(output_dir) if output_dir else repo_root_path / DEFAULT_REPORT_SUBDIR
    generated_at = _now(now)
    loaded = load_default_evidence(repo_root_path)
    source_evidence = _deepcopy(loaded)
    if evidence:
        source_evidence.update({key: _deepcopy(value) for key, value in evidence.items()})

    human_gate_report = _ensure_dict(source_evidence.get("human_gate_report"))
    autonomy_gap_report = _ensure_dict(source_evidence.get("autonomy_gap_report"))
    evidence_missing = []
    if not human_gate_report:
        evidence_missing.append(str(DEFAULT_HUMAN_GATE_REPORT))
    if not autonomy_gap_report:
        evidence_missing.append(str(DEFAULT_AUTONOMY_GAP_REPORT))

    invalid_reasons = _collect_invalid_reasons(
        human_gate_report=human_gate_report,
        autonomy_gap_report=autonomy_gap_report,
    )
    bridge_blockers = _collect_bridge_blockers(
        evidence_missing=evidence_missing,
        human_gate_report=human_gate_report,
        autonomy_gap_report=autonomy_gap_report,
    )

    if evidence_missing or invalid_reasons:
        bridge_status = "INVALID"
    elif bridge_blockers:
        bridge_status = "BLOCKED"
    else:
        bridge_status = "READY_FOR_DRY_RUN_PREVIEW"

    proposed_preview = _build_proposed_queue_item_preview(
        generated_at=generated_at,
        bridge_status=bridge_status,
        bridge_blockers=bridge_blockers,
        invalid_reasons=invalid_reasons,
        human_gate_report=human_gate_report,
        autonomy_gap_report=autonomy_gap_report,
    )
    report_paths = [
        str(output_dir_path / REPORT_JSON_NAME),
        str(output_dir_path / REPORT_MD_NAME),
    ]
    report = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at,
        "mode": MODE,
        "bridge_type": BRIDGE_TYPE,
        "bridge_status": bridge_status,
        "bridge_status_reason": (
            "P2 evidence can be represented as a DRY_RUN queue preview only."
            if bridge_status == "READY_FOR_DRY_RUN_PREVIEW"
            else "P2 enqueue bridge remains blocked by current evidence."
            if bridge_status == "BLOCKED"
            else "P2 enqueue bridge evidence is missing or invalid."
        ),
        "repo_root": str(repo_root_path),
        "report_paths": report_paths,
        "evidence_loaded": source_evidence.get("evidence_loaded", {}),
        "evidence_missing": evidence_missing,
        "source_fingerprints": source_evidence.get("source_fingerprints", []),
        "bridge_blockers": bridge_blockers,
        "invalid_reasons": invalid_reasons,
        "proposed_queue_item_preview": proposed_preview,
        "human_gate_evidence_summary": {
            "dogfood_status": human_gate_report.get("dogfood_status"),
            "queue_validation_status": _queue_validation_status(human_gate_report),
            "runtime_proof_gate_status": _runtime_gate_status(human_gate_report),
            "human_gate_packet_status": _human_gate_packet_status(human_gate_report),
            "mutation_check_status": human_gate_report.get("mutation_check_status"),
            "mutated_source_count": len(human_gate_report.get("mutated_sources") or []),
        },
        "autonomy_gap_evidence_summary": {
            "reassessment_status": autonomy_gap_report.get("reassessment_status"),
            "recommended_next_lane": _ensure_dict(autonomy_gap_report.get("summary")).get("recommended_next_lane"),
            "p2_enqueue_bridge_readiness": _p2_readiness_status(autonomy_gap_report),
            "live_execution_ready": _status(_ensure_dict(autonomy_gap_report.get("live_execution_readiness")).get("status")),
        },
        "approval_granted": False,
        "execution_allowed": False,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_launch_allowed": False,
        "runtime_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "telemetry_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "service_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
        "unsafe_autonomy_claim": False,
        "vacation_mode_complete": False,
        "safe_next_action": "Review the P2 enqueue preview; real enqueue requires a separate approved APPLY packet.",
        "stop_condition": "Stop after writing preview evidence; do not mutate queues, inboxes, runtime, scheduler, SOS, or approval state.",
        "summary": {},
        "validation": {},
    }
    report["validation"] = validate_p2_enqueue_bridge_report(report)
    report["summary"] = summarize_p2_enqueue_bridge_report(report)
    return report


def build_p2_enqueue_bridge_markdown_summary(report: dict[str, Any]) -> str:
    report = report if isinstance(report, dict) else {}
    summary = summarize_p2_enqueue_bridge_report(report)
    preview = _ensure_dict(report.get("proposed_queue_item_preview"))
    lines = [
        "# AI_OS P2 Enqueue Bridge Preview",
        "",
        f"- generated_at_utc: `{report.get('generated_at_utc')}`",
        f"- bridge_status: `{report.get('bridge_status')}`",
        f"- queue_validation_status: `{summary.get('queue_validation_status')}`",
        f"- human_gate_packet_status: `{summary.get('human_gate_packet_status')}`",
        f"- p2_enqueue_bridge_readiness: `{summary.get('p2_enqueue_bridge_readiness')}`",
        f"- proposed_preview_id: `{preview.get('preview_id')}`",
        f"- enqueue_allowed: `{preview.get('enqueue_allowed')}`",
        f"- queue_mutation_allowed: `{report.get('queue_mutation_allowed')}`",
        f"- runtime_execution_allowed: `{preview.get('runtime_execution_allowed')}`",
        f"- scheduler_creation_allowed: `{report.get('scheduler_creation_allowed')}`",
        f"- sos_allowed: `{report.get('sos_allowed')}`",
        f"- blocker_count: `{summary.get('blocker_count')}`",
        f"- invalid_reason_count: `{summary.get('invalid_reason_count')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Preview",
        f"- {preview.get('title')}",
        f"- recommended_next_lane: `{preview.get('recommended_next_lane')}`",
        "",
        "## Blockers",
    ]
    blockers = report.get("bridge_blockers") or []
    lines.extend([f"- {blocker}" for blocker in blockers] if blockers else ["- None"])
    lines.extend(
        [
            "",
            "## Safety",
            "- This preview does not approve execution.",
            "- No real enqueue, dequeue, dispatch, APPLY, runtime execution, queue mutation, worker inbox mutation, scheduler creation, SOS activation, live trading, or credential access occurred.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_p2_enqueue_bridge_reports(
    report: dict[str, Any],
    *,
    output_dir: str | Path | None = None,
) -> dict[str, str]:
    output_dir_path = Path(output_dir) if output_dir else Path(report.get("repo_root") or ".") / DEFAULT_REPORT_SUBDIR
    output_dir_path.mkdir(parents=True, exist_ok=True)
    json_path = output_dir_path / REPORT_JSON_NAME
    md_path = output_dir_path / REPORT_MD_NAME
    report["report_paths"] = [str(json_path), str(md_path)]
    report["validation"] = validate_p2_enqueue_bridge_report(report)
    report["summary"] = summarize_p2_enqueue_bridge_report(report)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_p2_enqueue_bridge_markdown_summary(report), encoding="utf-8")
    return {"json_path": str(json_path), "md_path": str(md_path)}


def validate_p2_enqueue_bridge_report(report: dict[str, Any]) -> dict[str, Any]:
    checked_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "bridge_type",
        "bridge_status",
        "bridge_status_reason",
        "repo_root",
        "report_paths",
        "evidence_loaded",
        "evidence_missing",
        "source_fingerprints",
        "bridge_blockers",
        "invalid_reasons",
        "proposed_queue_item_preview",
        "human_gate_evidence_summary",
        "autonomy_gap_evidence_summary",
        "approval_granted",
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "runtime_mutation_allowed",
        "queue_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
        "safe_next_action",
        "stop_condition",
    ]
    blockers: list[str] = []
    unsafe_flags: list[str] = []

    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report must be an object"],
            "checked_fields": checked_fields,
            "unsafe_flags": ["report_not_object"],
            "bridge_status": None,
        }

    for field in checked_fields:
        if field not in report:
            blockers.append(f"missing required field: {field}")

    bridge_status = _status(report.get("bridge_status"))
    if bridge_status not in ALLOWED_BRIDGE_STATUSES:
        blockers.append("bridge_status must be READY_FOR_DRY_RUN_PREVIEW, BLOCKED, or INVALID")
        unsafe_flags.append("bridge_status_invalid")
    if report.get("mode") != MODE:
        blockers.append("mode must be DRY_RUN")
        unsafe_flags.append("mode_invalid")
    if report.get("bridge_type") != BRIDGE_TYPE:
        blockers.append("bridge_type must be p2_enqueue_bridge")
        unsafe_flags.append("bridge_type_invalid")

    for field in UNSAFE_BOOL_FIELDS:
        if report.get(field) is True:
            blockers.append(f"{field} must remain false")
            unsafe_flags.append(f"{field}_true")

    preview = _ensure_dict(report.get("proposed_queue_item_preview"))
    if not preview:
        blockers.append("proposed_queue_item_preview must be present")
        unsafe_flags.append("preview_missing")
    for field in PREVIEW_FALSE_FIELDS:
        if preview.get(field) is True:
            blockers.append(f"proposed_queue_item_preview.{field} must remain false")
            unsafe_flags.append(f"preview_{field}_true")
    if preview.get("mode") != "DRY_RUN_PREVIEW_ONLY":
        blockers.append("proposed_queue_item_preview.mode must be DRY_RUN_PREVIEW_ONLY")
        unsafe_flags.append("preview_mode_invalid")
    allowed_paths = preview.get("allowed_paths")
    if not isinstance(allowed_paths, list) or not allowed_paths:
        blockers.append("proposed_queue_item_preview.allowed_paths must be a non-empty list")
        unsafe_flags.append("preview_allowed_paths_missing")
    forbidden_paths = preview.get("forbidden_paths")
    if not isinstance(forbidden_paths, list) or not forbidden_paths:
        blockers.append("proposed_queue_item_preview.forbidden_paths must be a non-empty list")
        unsafe_flags.append("preview_forbidden_paths_missing")

    bridge_blockers = report.get("bridge_blockers")
    if not isinstance(bridge_blockers, list):
        blockers.append("bridge_blockers must be a list")
        unsafe_flags.append("bridge_blockers_invalid")
        bridge_blockers = []
    invalid_reasons = report.get("invalid_reasons")
    if not isinstance(invalid_reasons, list):
        blockers.append("invalid_reasons must be a list")
        unsafe_flags.append("invalid_reasons_invalid")
        invalid_reasons = []
    if bridge_status == "READY_FOR_DRY_RUN_PREVIEW" and bridge_blockers:
        blockers.append("READY_FOR_DRY_RUN_PREVIEW cannot have bridge_blockers")
        unsafe_flags.append("ready_with_blockers")
    if bridge_status == "READY_FOR_DRY_RUN_PREVIEW" and invalid_reasons:
        blockers.append("READY_FOR_DRY_RUN_PREVIEW cannot have invalid_reasons")
        unsafe_flags.append("ready_with_invalid_reasons")
    if bridge_status == "INVALID" and not (report.get("evidence_missing") or invalid_reasons):
        blockers.append("INVALID status requires missing or invalid evidence")
        unsafe_flags.append("invalid_without_reason")

    if not report.get("safe_next_action"):
        blockers.append("safe_next_action must be non-empty")
        unsafe_flags.append("safe_next_action_missing")
    if not report.get("stop_condition"):
        blockers.append("stop_condition must be non-empty")
        unsafe_flags.append("stop_condition_missing")
    report_paths = report.get("report_paths")
    if not isinstance(report_paths, list) or len(report_paths) != 2:
        blockers.append("report_paths must contain JSON and Markdown paths")
        unsafe_flags.append("report_paths_invalid")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": list(dict.fromkeys(blockers)),
        "checked_fields": checked_fields,
        "unsafe_flags": list(dict.fromkeys(unsafe_flags)),
        "bridge_status": report.get("bridge_status"),
    }


def summarize_p2_enqueue_bridge_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "bridge_status": None,
            "queue_validation_status": None,
            "human_gate_packet_status": None,
            "p2_enqueue_bridge_readiness": None,
            "blocker_count": 0,
            "invalid_reason_count": 0,
            "enqueue_allowed": None,
            "queue_mutation_allowed": None,
            "runtime_execution_allowed": None,
            "safe_next_action": None,
            "report_paths": [],
        }
    human_gate = _ensure_dict(report.get("human_gate_evidence_summary"))
    autonomy_gap = _ensure_dict(report.get("autonomy_gap_evidence_summary"))
    preview = _ensure_dict(report.get("proposed_queue_item_preview"))
    return {
        "bridge_status": report.get("bridge_status"),
        "queue_validation_status": human_gate.get("queue_validation_status"),
        "human_gate_packet_status": human_gate.get("human_gate_packet_status"),
        "p2_enqueue_bridge_readiness": autonomy_gap.get("p2_enqueue_bridge_readiness"),
        "recommended_next_lane": autonomy_gap.get("recommended_next_lane") or preview.get("recommended_next_lane"),
        "blocker_count": len(report.get("bridge_blockers") or []),
        "invalid_reason_count": len(report.get("invalid_reasons") or []),
        "enqueue_allowed": preview.get("enqueue_allowed"),
        "canonical_queue_write_allowed": preview.get("canonical_queue_write_allowed"),
        "worker_inbox_write_allowed": preview.get("worker_inbox_write_allowed"),
        "active_packet_write_allowed": preview.get("active_packet_write_allowed"),
        "queue_mutation_allowed": report.get("queue_mutation_allowed"),
        "runtime_execution_allowed": preview.get("runtime_execution_allowed"),
        "scheduler_creation_allowed": report.get("scheduler_creation_allowed"),
        "sos_allowed": report.get("sos_allowed"),
        "live_trading_allowed": report.get("live_trading_allowed"),
        "safe_next_action": report.get("safe_next_action"),
        "stop_condition": report.get("stop_condition"),
        "report_paths": list(report.get("report_paths") or []),
        "validation_status": _ensure_dict(report.get("validation")).get("status"),
    }


def run_p2_enqueue_bridge(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    evidence: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    report = build_p2_enqueue_bridge_report(
        repo_root=repo_root,
        output_dir=output_dir,
        evidence=evidence,
        now=now,
    )
    write_p2_enqueue_bridge_reports(report, output_dir=output_dir)
    return report


def _load_json_arg(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    data = json.loads(text)
    return data if isinstance(data, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the AI_OS P2 enqueue bridge DRY_RUN preview.")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--output-dir", default=None, help="optional output directory")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    parser.add_argument("--mode", default=MODE, choices=[MODE], help="safe mode; only DRY_RUN is supported")
    parser.add_argument("--evidence-json", default=None, help="optional JSON object with evidence sections")
    args = parser.parse_args()

    report = run_p2_enqueue_bridge(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        now=args.now,
        evidence=_load_json_arg(args.evidence_json),
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
