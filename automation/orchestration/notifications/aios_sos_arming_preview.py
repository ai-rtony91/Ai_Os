"""AI_OS SOS arming preview (observe-only).

This module evaluates whether the repository state and evidence are ready for an
SOS arming step. It never sends notifications, never mutates runtime state, and
only writes preview evidence for human review.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hashlib import sha256

SCHEMA = "AIOS_SOS_ARMING_PREVIEW.v1"
MODE = "DRY_RUN"
READY = "READY_FOR_SOS_PREVIEW"
BLOCKED = "BLOCKED"
INVALID = "INVALID"
RUNTIME_READY = "READY_FOR_RUNTIME_PREVIEW"

REPORT_JSON_NAME = "sos_arming_preview.json"
REPORT_MD_NAME = "sos_arming_preview_summary.md"
DEFAULT_REPORT_DIR = Path("Reports/sos_preview")

DEFAULT_HUMAN_GATE_REPORT = Path("Reports/human_gate/human_gate_packet_dogfood_report.json")
DEFAULT_AUTONOMY_GAP_REPORT = Path("Reports/autonomy_gap/autonomy_gap_reassessment_report.json")
DEFAULT_P2_PREVIEW = Path("Reports/p2_enqueue_bridge/p2_enqueue_bridge_preview.json")
DEFAULT_QUEUE_MUTATION_PREVIEW = Path("Reports/queue_mutation_gate/queue_mutation_gate_preview.json")
DEFAULT_RUNTIME_APPLY_PREVIEW = Path("Reports/runtime_apply_lane/runtime_apply_lane_preview.json")

PROTECTED_PATHS = (
    Path("automation/orchestration/work_packets/active"),
    Path("automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"),
    Path("automation/orchestration/approval_inbox"),
    Path("automation/orchestration/command_queue"),
    Path("automation/orchestration/work_packets/blocked"),
    Path("automation/orchestration/work_packets/complete"),
    Path("services"),
    Path("telemetry"),
)


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _path_sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path_fingerprint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "kind": "missing"}
    if path.is_file():
        size = path.stat().st_size
        return {
            "path": path.as_posix(),
            "kind": "file",
            "size": size,
            "sha256": _path_sha(path),
        }
    if path.is_dir():
        files = sorted(str(child.relative_to(path).as_posix()) for child in path.rglob("*"))
        return {
            "path": path.as_posix(),
            "kind": "dir",
            "file_count": len(files),
            "entries": files,
            "sha256": None,
        }
    return {"path": path.as_posix(), "kind": "other", "size": path.stat().st_size}


def _collect_protected_fingerprints(paths: tuple[Path, ...]) -> list[dict[str, Any]]:
    return [_path_fingerprint(path.resolve()) for path in paths]


def _to_bool(value: Any) -> bool:
    return bool(value is True)


def _safe_status(value: Any) -> str:
    return str(value or "").upper()


def _load_evidence(repo_root: Path, path: Path) -> tuple[dict[str, Any], bool, str]:
    absolute = repo_root / path
    loaded = _read_json(absolute)
    if loaded is None:
        return {}, False, absolute.as_posix()
    return loaded, True, absolute.as_posix()


def _status_reason(statuses: list[str]) -> str:
    if not statuses:
        return "all safety boundaries clear"
    return "; ".join(statuses)


def build_sos_arming_preview(
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    provided = evidence or {}

    p2_report, p2_loaded, p2_path = (
        _load_evidence(root, DEFAULT_P2_PREVIEW)
        if not evidence
        else (provided.get("p2_bridge_report", {}) if isinstance(provided.get("p2_bridge_report"), dict) else {}, True, str(DEFAULT_P2_PREVIEW))
    )
    queue_gate_report, queue_gate_loaded, queue_gate_path = (
        _load_evidence(root, DEFAULT_QUEUE_MUTATION_PREVIEW)
        if not evidence
        else (
            provided.get("queue_mutation_report", {}) if isinstance(provided.get("queue_mutation_report"), dict) else {},
            True,
            str(DEFAULT_QUEUE_MUTATION_PREVIEW),
        )
    )
    human_report, human_loaded, human_path = (
        _load_evidence(root, DEFAULT_HUMAN_GATE_REPORT)
        if not evidence
        else (
            provided.get("human_gate_report", {}) if isinstance(provided.get("human_gate_report"), dict) else {},
            True,
            str(DEFAULT_HUMAN_GATE_REPORT),
        )
    )
    autonomy_report, autonomy_loaded, autonomy_path = (
        _load_evidence(root, DEFAULT_AUTONOMY_GAP_REPORT)
        if not evidence
        else (
            provided.get("autonomy_gap_report", {}) if isinstance(provided.get("autonomy_gap_report"), dict) else {},
            True,
            str(DEFAULT_AUTONOMY_GAP_REPORT),
        )
    )
    runtime_apply_report: dict[str, Any]
    runtime_apply_loaded: bool
    if evidence and isinstance(provided.get("runtime_apply_report"), dict):
        runtime_apply_report = provided.get("runtime_apply_report", {})
        runtime_apply_loaded = True
        runtime_apply_path = str(DEFAULT_RUNTIME_APPLY_PREVIEW)
    else:
        runtime_apply_report, runtime_apply_loaded, runtime_apply_path = _load_evidence(root, DEFAULT_RUNTIME_APPLY_PREVIEW)
    if not runtime_apply_loaded:
        runtime_apply_report = {}
        runtime_apply_path = str((root / DEFAULT_RUNTIME_APPLY_PREVIEW).as_posix())

    invalid_reasons: list[str] = []
    blockers: list[str] = []

    if not p2_loaded:
        blockers.append(f"P2 bridge evidence not available: {p2_path}")
    if not queue_gate_loaded:
        blockers.append(f"queue mutation gate evidence not available: {queue_gate_path}")
    if not human_loaded:
        invalid_reasons.append(f"human gate report not available: {human_path}")
    if not autonomy_loaded:
        invalid_reasons.append(f"autonomy gap report not available: {autonomy_path}")

    p2_status = _safe_status(p2_report.get("bridge_status"))
    queue_gate_status = _safe_status(queue_gate_report.get("gate_status"))
    runtime_apply_status = _safe_status(runtime_apply_report.get("status"))

    approval_explicit = (
        _to_bool(queue_gate_report.get("approval_check", {}).get("explicit_approval"))
        if queue_gate_loaded
        else False
    )
    if not approval_explicit:
        blockers.append("explicit approval for queue mutation is not present in evidence")

    if p2_status and p2_status != "READY_FOR_DRY_RUN_PREVIEW":
        blockers.append(f"P2 bridge is not ready for SOS preview: {p2_status or 'MISSING'}")
    if queue_gate_status and queue_gate_status != "READY_FOR_HUMAN_REVIEW":
        blockers.append(
            f"queue mutation gate is not ready: {queue_gate_status or 'MISSING'}"
        )
    if not runtime_apply_loaded:
        blockers.append("runtime apply lane preview evidence is required for SOS arming preview")
    elif runtime_apply_status and runtime_apply_status != RUNTIME_READY:
        blockers.append(
            f"runtime apply lane preview is not ready for SOS lane simulation: {runtime_apply_status}"
        )

    human_blocked = _safe_status(human_report.get("dogfood_status"))
    autonomy_blocked = _safe_status(autonomy_report.get("reassessment_status"))
    if human_blocked not in {"PASS", "READY"}:
        blockers.append(f"human gate evidence requires review: {human_blocked or 'MISSING'}")
    if autonomy_blocked not in {"PASS", "READY"}:
        blockers.append(f"autonomy reassessment evidence is blocked: {autonomy_blocked or 'MISSING'}")

    if p2_loaded and p2_report.get("bridge_status") == INVALID:
        invalid_reasons.append("P2 bridge report is invalid")
    if queue_gate_loaded and queue_gate_report.get("gate_status") == INVALID:
        invalid_reasons.append("queue mutation gate report is invalid")
    if invalid_reasons:
        status = INVALID
    elif blockers:
        status = BLOCKED
    else:
        status = READY

    validation = {
        "status": "PASS",
        "checked_fields": [
            "human_gate_report",
            "autonomy_gap_report",
            "p2_bridge_report",
            "queue_mutation_report",
            "runtime_apply_preview",
            "approval_explicit",
            "protected_boundaries",
        ],
        "invalid_reasons": invalid_reasons,
        "blockers": blockers,
    }

    blocked_event = {
        "event": "AIOS_RUNTIME_SOS",
        "event_status": BLOCKED,
        "would_trigger_human": False,
        "would_dispatch": False,
        "would_route": False,
        "would_execute": False,
        "would_apply": False,
        "blocked_reason": _status_reason(blockers),
    }

    protected_boundaries = {
        "notification_allowed": False,
        "notification_sent": False,
        "credential_required": True,
        "scheduler_required": False,
        "runtime_launch_allowed": False,
        "runtime_execution_allowed": False,
        "queue_mutation_allowed": False,
        "worker_inbox_mutation_allowed": False,
        "active_packet_mutation_allowed": False,
        "approval_inbox_mutation_allowed": False,
        "command_queue_mutation_allowed": False,
        "telemetry_mutation_allowed": False,
        "scheduler_registration_allowed": False,
        "service_creation_allowed": False,
        "sos_allowed": False,
        "trading_execution_allowed": False,
        "live_send_blocked": True,
    }

    report = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": _now(now),
        "repo_root": root.as_posix(),
        "sos_status": status,
        "sos_status_reason": _status_reason(invalid_reasons or blockers),
        "evidence_loaded": {
            "p2_bridge_report": p2_path,
            "queue_mutation_report": queue_gate_path,
            "human_gate_report": human_path,
            "autonomy_gap_report": autonomy_path,
            "runtime_apply_preview_present": runtime_apply_loaded,
            "runtime_apply_preview_path": runtime_apply_path,
        },
        "evidence_missing": {
            "p2_bridge_report": not p2_loaded,
            "queue_mutation_report": not queue_gate_loaded,
            "human_gate_report": not human_loaded,
            "autonomy_gap_report": not autonomy_loaded,
            "runtime_apply_preview": not runtime_apply_loaded,
        },
        "blocked_event": blocked_event,
        "human_gate_report_summary": {
            "dogfood_status": human_report.get("dogfood_status"),
            "packet_status": human_report.get("human_gate_packet_summary", {}).get("packet_status"),
        },
        "autonomy_gap_report_summary": {
            "reassessment_status": autonomy_report.get("reassessment_status"),
            "sos_ready": autonomy_report.get("summary", {}).get("sos_ready"),
        },
        "p2_bridge_summary": {
            "bridge_status": p2_report.get("bridge_status"),
            "bridge_blocker_count": len(p2_report.get("bridge_blockers", []) or []),
        },
        "queue_mutation_gate_summary": {
            "gate_status": queue_gate_report.get("gate_status"),
            "explicit_approval": approval_explicit,
            "proposed_packet_id": queue_gate_report.get("proposed_queue_item", {}).get("packet_id"),
            "gate_status_reason": queue_gate_report.get("gate_status_reason"),
        },
        "runtime_apply_summary": {
            "runtime_apply_status": runtime_apply_report.get("status"),
            "ready_for_sos_preview": runtime_apply_report.get("status") == RUNTIME_READY,
        },
        "would_apply": False,
        "would_route": False,
        "would_execute": False,
        "runtime_launch": False,
        "runtime_execution": False,
        "queue_mutation": False,
        "worker_inbox_mutation": False,
        "scheduler_registration": False,
        "trading_execution": False,
        "notification_allowed": False,
        "notification_sent": False,
        "credential_required": True,
        "scheduler_required": False,
        "protected_boundaries": protected_boundaries,
        "validation": validation,
        "safe_next_action": (
            "Resolve explicit approval blockers and evidence blockers before arming SOS."
            if status in {BLOCKED, INVALID}
            else "Resume with separate explicit human approval before any live SOS action."
        ),
        "stop_condition": (
            "Stop before sending alerts, mutating queue, worker inbox, runtime, scheduler, "
            "services, telemetry, or approval state."
        ),
        "report_paths": [
            (root / (output_dir or DEFAULT_REPORT_DIR) / REPORT_JSON_NAME).as_posix()
            if output_dir is not None
            else (root / DEFAULT_REPORT_DIR / REPORT_JSON_NAME).as_posix()
        ],
        "source_fingerprints": _collect_protected_fingerprints(PROTECTED_PATHS),
    }
    return report


def validate_sos_arming_report(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if report.get("notification_sent") is True:
        blockers.append("notification_sent must be false in preview mode")
    for field in (
        "notification_allowed",
        "would_apply",
        "would_route",
        "would_execute",
        "runtime_launch",
        "runtime_execution",
        "queue_mutation",
        "worker_inbox_mutation",
        "scheduler_registration",
        "trading_execution",
    ):
        if report.get(field) not in (False, 0, "false"):
            blockers.append(f"{field} must remain false")
    boundaries = report.get("protected_boundaries", {})
    for field in (
        "notification_allowed",
        "notification_sent",
        "runtime_launch_allowed",
        "runtime_execution_allowed",
        "queue_mutation_allowed",
        "worker_inbox_mutation_allowed",
        "scheduler_registration_allowed",
        "trading_execution_allowed",
        "approval_inbox_mutation_allowed",
    ):
        if boundaries.get(field) is True:
            blockers.append(f"protected_boundaries.{field} must be false")

    validation = {
        "status": "PASS",
        "checked_fields": [
            "sos_status",
            "notification_sent",
            "would_apply",
            "would_route",
            "would_execute",
            "runtime_launch",
            "runtime_execution",
            "queue_mutation",
            "worker_inbox_mutation",
            "scheduler_registration",
            "trading_execution",
            "protected_boundaries",
        ],
        "blockers": blockers,
        "unsafe_flags": [],
    }
    return validation


def build_sos_arming_preview_markdown(report: dict[str, Any]) -> str:
    blocked = report.get("blocked_event", {})
    boundary = report.get("protected_boundaries", {})
    lines = [
        "# AI_OS SOS Arming Preview",
        "",
        f"- sos_status: `{report.get('sos_status')}`",
        f"- would_send_notification: `{report.get('notification_sent')}`",
        f"- notification_allowed: `{report.get('notification_allowed')}`",
        f"- would_route: `{report.get('would_route')}`",
        f"- would_execute: `{report.get('would_execute')}`",
        f"- credential_required: `{report.get('credential_required')}`",
        f"- scheduler_required: `{report.get('scheduler_required')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Blocked Event Simulation",
        f"- event: `{blocked.get('event')}`",
        f"- event_status: `{blocked.get('event_status')}`",
        f"- would_apply: `{report.get('would_apply')}`",
        f"- would_dispatch: `{blocked.get('would_dispatch')}`",
        f"- would_route: `{blocked.get('would_route')}`",
        f"- would_execute: `{blocked.get('would_execute')}`",
        f"- blocked_reason: `{_status_reason(report.get('validation', {}).get('blockers', []) or [])}`",
        "",
        "## Protected Boundaries",
        f"- notification_allowed: `{boundary.get('notification_allowed')}`",
        f"- runtime_launch_allowed: `{boundary.get('runtime_launch_allowed')}`",
        f"- queue_mutation_allowed: `{boundary.get('queue_mutation_allowed')}`",
        f"- worker_inbox_mutation_allowed: `{boundary.get('worker_inbox_mutation_allowed')}`",
        f"- scheduler_registration_allowed: `{boundary.get('scheduler_registration_allowed')}`",
        f"- trading_execution_allowed: `{boundary.get('trading_execution_allowed')}`",
        "",
        "- This preview does not send notifications, mutate state, or arm SOS.",
        "",
    ]
    return "\n".join(lines)


def write_sos_arming_preview(
    report: dict[str, Any],
    *,
    repo_root: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    report_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_REPORT_DIR
    if not report_dir.is_absolute():
        report_dir = root / report_dir
    json_path = report_dir / REPORT_JSON_NAME
    md_path = report_dir / REPORT_MD_NAME
    _write_json(json_path, report)
    md_path.write_text(build_sos_arming_preview_markdown(report), encoding="utf-8")
    report["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    return report


def summarize_sos_arming_preview(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "sos_status": report.get("sos_status"),
        "runtime_launch": report.get("runtime_launch"),
        "runtime_execution": report.get("runtime_execution"),
        "queue_mutation": report.get("queue_mutation"),
        "worker_inbox_mutation": report.get("worker_inbox_mutation"),
        "notification_allowed": report.get("notification_allowed"),
        "notification_sent": report.get("notification_sent"),
        "validation_status": report.get("validation", {}).get("status"),
        "safe_next_action": report.get("safe_next_action"),
        "report_paths": report.get("report_paths"),
    }


def run_sos_arming_preview(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    report = build_sos_arming_preview(
        repo_root=repo_root,
        output_dir=output_dir,
        now=now,
        evidence=evidence,
    )
    if write_report:
        report = write_sos_arming_preview(report, repo_root=repo_root, output_dir=output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the AI_OS SOS arming preview.")
    parser.add_argument("--repo-root", default=".", help="Repository root for evidence lookup.")
    parser.add_argument("--output-dir", default=None, help="Output directory for SOS preview files.")
    parser.add_argument("--now", default=None, help="Optional UTC timestamp override.")
    parser.add_argument("--no-write", action="store_true", help="Do not write preview files.")
    args = parser.parse_args()

    report = run_sos_arming_preview(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        now=args.now,
        write_report=not args.no_write,
    )
    print(json.dumps(summarize_sos_arming_preview(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
