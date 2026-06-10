"""AI_OS scheduler registration preview (observe-only).

This module evaluates whether the current evidence chain is ready for a
human-assisted scheduler registration step. It never registers scheduler tasks,
creates services, launches runtime, mutates queue state, touches worker inboxes,
or sends notifications.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_SCHEDULER_REGISTRATION_PREVIEW.v1"
MODE = "DRY_RUN"
READY = "READY_FOR_SCHEDULER_PREVIEW"
BLOCKED = "BLOCKED"
INVALID = "INVALID"
ALLOWED_STATUSES = {READY, BLOCKED, INVALID}

REPORT_DIR = Path("Reports") / "scheduler_preview"
REPORT_JSON_NAME = "scheduler_registration_preview.json"
REPORT_MD_NAME = "scheduler_registration_preview_summary.md"

DEFAULT_QUEUE_GATE_PREVIEW = Path("Reports") / "queue_mutation_gate" / "queue_mutation_gate_preview.json"
DEFAULT_RUNTIME_APPLY_PREVIEW = Path("Reports") / "runtime_apply_lane" / "runtime_apply_lane_preview.json"
DEFAULT_SOS_PREVIEW = Path("Reports") / "sos_preview" / "sos_arming_preview.json"
DEFAULT_HUMAN_GATE_REPORT = Path("Reports") / "human_gate" / "human_gate_packet_dogfood_report.json"
DEFAULT_AUTONOMY_REPORT = Path("Reports") / "autonomy_gap" / "autonomy_gap_reassessment_report.json"

PROTECTED_PATHS = (
    Path("automation/orchestration/work_packets/active"),
    Path("automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"),
    Path("automation/orchestration/approval_inbox"),
    Path("automation/orchestration/command_queue"),
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
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _path_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _collect_path_fingerprint(path: Path) -> dict[str, Any]:
    if path.is_file():
        return {
            "path": path.as_posix(),
            "kind": "file",
            "size": path.stat().st_size,
            "sha256": _path_sha256(path),
        }
    if path.is_dir():
        files = []
        for child in sorted(path.rglob("*")):
            if child.is_file():
                files.append(child.relative_to(path).as_posix())
        return {
            "path": path.as_posix(),
            "kind": "dir",
            "file_count": len(files),
            "entries": files,
        }
    if not path.exists():
        return {"path": path.as_posix(), "kind": "missing"}
    return {"path": path.as_posix(), "kind": "other", "size": path.stat().st_size}


def _load_evidence_file(
    root: Path,
    path: Path,
) -> tuple[dict[str, Any], bool, str]:
    candidate = path if path.is_absolute() else root / path
    loaded = _read_json(candidate)
    return (loaded or {}, bool(loaded), candidate.as_posix())


def _norm_status(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _bool(value: Any) -> bool:
    return bool(value is True)


def _truthy(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return "unknown"


def _simulate_scheduler_plan(
    queue_gate_status: str,
    runtime_apply_status: str,
    sos_status: str,
    human_status: str,
    autonomy_status: str,
) -> list[dict[str, Any]]:
    if (
        queue_gate_status == "READY_FOR_HUMAN_REVIEW"
        and runtime_apply_status == "READY_FOR_RUNTIME_PREVIEW"
        and _norm_status(sos_status) in {"READY_FOR_SOS_PREVIEW", "READY"}
        and human_status == "PASS"
        and autonomy_status == "PASS"
    ):
        return [
            {
                "event": "human_scheduler_registration_checklist",
                "cadence": "operator_request",
                "allowed_action": "prepare registration checklist",
                "blocked": "AUTO scheduler registration",
            }
        ]
    return [
        {
            "event": "human_scheduler_registration_checklist",
            "cadence": "operator_request",
            "allowed_action": "preview only",
            "blocked": "upstream blockers or approvals",
        }
    ]


def _required_dependencies() -> list[str]:
    return [
        "Queue mutation gate approval evidence",
        "Runtime APPLY lane READY_FOR_RUNTIME_PREVIEW",
        "SOS arming blocked as preview",
        "Human gate packet dogfood status PASS",
        "Autonomy gap reassessment status PASS",
        "Anthony explicit scheduler registration action",
    ]


def build_scheduler_registration_preview(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    evidence = evidence or {}

    queue_gate, queue_gate_loaded, queue_gate_path = (
        _load_evidence_file(root, DEFAULT_QUEUE_GATE_PREVIEW)
        if not evidence
        else (
            evidence.get("queue_mutation_gate", {})
            if isinstance(evidence.get("queue_mutation_gate"), dict)
            else {},
            True,
            str((root / DEFAULT_QUEUE_GATE_PREVIEW).as_posix()),
        )
    )
    runtime_apply, runtime_apply_loaded, runtime_apply_path = (
        _load_evidence_file(root, DEFAULT_RUNTIME_APPLY_PREVIEW)
        if not evidence
        else (
            evidence.get("runtime_apply", {})
            if isinstance(evidence.get("runtime_apply"), dict)
            else {},
            True,
            str((root / DEFAULT_RUNTIME_APPLY_PREVIEW).as_posix()),
        )
    )
    sos_preview, sos_loaded, sos_path = (
        _load_evidence_file(root, DEFAULT_SOS_PREVIEW)
        if not evidence
        else (
            evidence.get("sos_preview", {})
            if isinstance(evidence.get("sos_preview"), dict)
            else {},
            True,
            str((root / DEFAULT_SOS_PREVIEW).as_posix()),
        )
    )
    human_gate, human_loaded, human_gate_path = (
        _load_evidence_file(root, DEFAULT_HUMAN_GATE_REPORT)
        if not evidence
        else (
            evidence.get("human_gate", {})
            if isinstance(evidence.get("human_gate"), dict)
            else {},
            True,
            str((root / DEFAULT_HUMAN_GATE_REPORT).as_posix()),
        )
    )
    autonomy_gap, autonomy_loaded, autonomy_path = (
        _load_evidence_file(root, DEFAULT_AUTONOMY_REPORT)
        if not evidence
        else (
            evidence.get("autonomy_gap", {})
            if isinstance(evidence.get("autonomy_gap"), dict)
            else {},
            True,
            str((root / DEFAULT_AUTONOMY_REPORT).as_posix()),
        )
    )

    invalid_reasons: list[str] = []
    blockers: list[str] = []

    if not queue_gate_loaded:
        invalid_reasons.append(f"missing queue mutation gate evidence: {queue_gate_path}")
    if not runtime_apply_loaded:
        invalid_reasons.append(f"missing runtime apply preview evidence: {runtime_apply_path}")
    if not sos_loaded:
        invalid_reasons.append(f"missing SOS preview evidence: {sos_path}")
    if not human_loaded:
        invalid_reasons.append(f"missing human gate evidence: {human_gate_path}")
    if not autonomy_loaded:
        invalid_reasons.append(f"missing autonomy gap evidence: {autonomy_path}")

    queue_gate_status = _norm_status(queue_gate.get("gate_status"))
    runtime_apply_status = _norm_status(runtime_apply.get("apply_status"))
    sos_status = _norm_status(sos_preview.get("sos_status"))

    queue_gate_approval = _bool(
        queue_gate.get("approval_check", {}).get("explicit_approval")
        if isinstance(queue_gate.get("approval_check"), dict)
        else None
    )
    runtime_apply_ready = runtime_apply_status == "READY_FOR_RUNTIME_PREVIEW"
    queue_gate_ready = queue_gate_status == "READY_FOR_HUMAN_REVIEW"
    sos_ready_or_blocked = sos_status in {"READY_FOR_SOS_PREVIEW", "BLOCKED", "INVALID", "READY"}
    human_ready = str(human_gate.get("dogfood_status", "")).strip().upper() in {"PASS", "READY"}
    human_packet_status = str(human_gate.get("human_gate_packet_summary", {}).get("packet_status", "")).strip().upper()
    human_packet_ready = human_packet_status in {"PASS", "READY", "READY_FOR_HUMAN_REVIEW"}

    autonomy_status = str(autonomy_gap.get("reassessment_status", "")).strip().upper()
    autonomy_ready = autonomy_status in {"PASS", "READY"}

    if not queue_gate_ready:
        blockers.append(f"queue mutation gate is not ready: {queue_gate_status or 'MISSING'}")
    if not queue_gate_approval:
        blockers.append("explicit queue mutation approval is not present")
    if not runtime_apply_ready:
        blockers.append(
            f"runtime apply preview is not ready: {runtime_apply_status or 'MISSING'}"
        )
    if not sos_ready_or_blocked:
        blockers.append(f"SOS preview status is not ready: {sos_status or 'MISSING'}")
    if not human_ready or not human_packet_ready:
        blockers.append(
            f"human gate evidence is not pass: {human_gate.get('dogfood_status', 'MISSING')}"
        )
    if not autonomy_ready:
        blockers.append(
            f"autonomy reassessment is not pass: {autonomy_gap.get('reassessment_status', 'MISSING')}"
        )
    if queue_gate.get("validation", {}).get("status") == "BLOCK" and queue_gate_ready:
        blockers.append("queue gate validation currently BLOCK")
    if queue_gate.get("validation", {}).get("invalid_reasons"):
        blockers.extend(
            ["queue gate invalid reason: " + str(item) for item in queue_gate["validation"]["invalid_reasons"]]
        )

    runtime_safety = [
        runtime_apply.get("runtime_execution"),
        runtime_apply.get("runtime_launch"),
        runtime_apply.get("scheduler_registration"),
        runtime_apply.get("sos_notification"),
        runtime_apply.get("queue_mutation"),
        runtime_apply.get("worker_inbox_mutation"),
        runtime_apply.get("approval_inbox_mutation"),
    ]
    if any(item is True for item in runtime_safety):
        blockers.append("runtime apply preview claims unsafe runtime/scheduler mutation flags")

    if any(isinstance(item, dict) for item in runtime_apply.values()):
        # keep deterministic no-op behavior; no direct mutation requested.
        pass

    schedule = _simulate_scheduler_plan(
        queue_gate_status=queue_gate_status or "MISSING",
        runtime_apply_status=runtime_apply_status or "MISSING",
        sos_status=sos_status or "MISSING",
        human_status=human_gate.get("dogfood_status", "MISSING"),
        autonomy_status=autonomy_status or "MISSING",
    )
    required_dependencies = _required_dependencies()

    status = INVALID if invalid_reasons else (BLOCKED if blockers else READY)

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": _now(now),
        "repo_root": root.as_posix(),
        "scheduler_status": status,
        "scheduler_status_reason": (
            "Scheduler registration can proceed as a dry-run preview."
            if status == READY
            else "Scheduler registration is blocked by evidence blockers."
            if status == BLOCKED
            else "Scheduler registration preview is invalid due missing required evidence."
        ),
        "evidence_loaded": {
            "queue_mutation_gate_preview": queue_gate_loaded,
            "runtime_apply_preview": runtime_apply_loaded,
            "sos_preview": sos_loaded,
            "human_gate_report": human_loaded,
            "autonomy_gap_report": autonomy_loaded,
        },
        "evidence_paths": {
            "queue_mutation_gate_preview": queue_gate_path,
            "runtime_apply_preview": runtime_apply_path,
            "sos_preview": sos_path,
            "human_gate_report": human_gate_path,
            "autonomy_gap_report": autonomy_path,
        },
        "evidence_missing": {
            "queue_mutation_gate_preview": not queue_gate_loaded,
            "runtime_apply_preview": not runtime_apply_loaded,
            "sos_preview": not sos_loaded,
            "human_gate_report": not human_loaded,
            "autonomy_gap_report": not autonomy_loaded,
        },
        "invalid_reasons": invalid_reasons,
        "blockers": blockers,
        "proposed_scheduler": {
            "status": (
                "would_schedule" if status == READY else "would_not_schedule"
            ),
            "events": schedule,
        },
        "required_dependencies": required_dependencies,
        "remaining_blockers": blockers,
        "would_schedule": status == READY,
        "would_register_task": False,
        "would_start_service": False,
        "scheduler_registration_allowed": False,
        "scheduler_created": False,
        "service_created": False,
        "runtime_launch_allowed": False,
        "runtime_execution_allowed": False,
        "notification_send_allowed": False,
        "queue_mutation_allowed": False,
        "worker_inbox_mutation_allowed": False,
        "runtime_apply_projection": {
            "runtime_apply_status": runtime_apply_status,
            "would_apply": False,
            "would_route": False,
            "would_execute": False,
        },
        "queue_mutation_gate_projection": {
            "gate_status": queue_gate_status,
            "explicit_approval": queue_gate_approval,
            "gate_validation_status": queue_gate.get("validation", {}).get("status"),
        },
        "sos_projection": {
            "sos_status": sos_status,
            "notification_send_allowed": False,
            "notification_sent": False,
        },
        "human_gate_projection": {
            "dogfood_status": human_gate.get("dogfood_status"),
            "human_gate_packet_status": human_packet_status,
        },
        "autonomy_gap_projection": {
            "reassessment_status": autonomy_gap.get("reassessment_status"),
            "scheduler_readiness": autonomy_gap.get("summary", {}).get("scheduler_readiness"),
        },
        "safe_next_action": (
            "Run scheduler registration preview with approved evidence and queue approval before human registration."
            if status == READY
            else "Resolve evidence blockers and explicit approvals before scheduling registration."
            if status == BLOCKED
            else "Repair evidence and rerun scheduler registration preview."
        ),
        "stop_condition": (
            "Stop before scheduler creation, service creation, runtime launch/execution, "
            "notification send, queue mutation, or worker mutation."
        ),
        "protected_paths_scanned": [],
        "source_fingerprints": [
            _collect_path_fingerprint(root / path) for path in PROTECTED_PATHS
        ],
    }

    # Explicitly record protected false-allow flags as independent checks for
    # validation and tests.
    report.update(
        {
            "runtime_launch": False,
            "runtime_execution": False,
            "queue_mutation": False,
            "worker_inbox_mutation": False,
            "approval_inbox_mutation": False,
            "command_queue_mutation": False,
            "service_creation": False,
            "notification_sent": False,
            "unsafe_path_hits": [],
        }
    )

    blocked_paths = []
    for path in PROTECTED_PATHS:
        if (root / path).exists():
            blocked_paths.append(str(path))
    report["protected_paths_scanned"] = blocked_paths

    validation = validate_scheduler_registration_preview(report)
    report["validation"] = validation
    report["summary"] = summarize_scheduler_registration_preview(report)
    return report


def validate_scheduler_registration_preview(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    checked_fields: list[str] = [
        "schema",
        "mode",
        "scheduler_status",
        "evidence_missing",
        "invalid_reasons",
        "blockers",
        "would_schedule",
        "would_register_task",
        "would_start_service",
        "scheduler_registration_allowed",
        "service_created",
        "runtime_launch_allowed",
        "runtime_execution_allowed",
        "notification_send_allowed",
        "queue_mutation_allowed",
        "worker_inbox_mutation_allowed",
    ]

    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "checked_fields": [],
            "blockers": ["report must be an object"],
            "unsafe_flags": [],
        }

    if report.get("schema") != SCHEMA:
        blockers.append("schema mismatch")
    if report.get("mode") != MODE:
        blockers.append("mode must be DRY_RUN")
    if report.get("scheduler_status") not in ALLOWED_STATUSES:
        blockers.append(
            "scheduler_status must be READY_FOR_SCHEDULER_PREVIEW, BLOCKED, or INVALID"
        )
    if report.get("would_register_task") is not False:
        blockers.append("would_register_task must be false")
        unsafe_flags.append("would_register_task_true")
    if report.get("would_start_service") is not False:
        blockers.append("would_start_service must be false")
        unsafe_flags.append("would_start_service_true")
    if report.get("scheduler_registration_allowed") is not False:
        blockers.append("scheduler_registration_allowed must be false")
        unsafe_flags.append("scheduler_registration_allowed_true")
    if report.get("service_created") is not False:
        blockers.append("service_created must be false")
        unsafe_flags.append("service_created_true")
    if report.get("runtime_launch_allowed") is not False:
        blockers.append("runtime_launch_allowed must be false")
        unsafe_flags.append("runtime_launch_allowed_true")
    if report.get("runtime_execution_allowed") is not False:
        blockers.append("runtime_execution_allowed must be false")
        unsafe_flags.append("runtime_execution_allowed_true")
    if report.get("notification_send_allowed") is not False:
        blockers.append("notification_send_allowed must be false")
        unsafe_flags.append("notification_send_allowed_true")
    if report.get("queue_mutation_allowed") is not False:
        blockers.append("queue_mutation_allowed must be false")
        unsafe_flags.append("queue_mutation_allowed_true")
    if report.get("worker_inbox_mutation_allowed") is not False:
        blockers.append("worker_inbox_mutation_allowed must be false")
        unsafe_flags.append("worker_inbox_mutation_allowed_true")
    if report.get("runtime_launch") is not False:
        blockers.append("runtime_launch must be false")
    if report.get("runtime_execution") is not False:
        blockers.append("runtime_execution must be false")
    if report.get("queue_mutation") is not False:
        blockers.append("queue_mutation must be false")
    if report.get("worker_inbox_mutation") is not False:
        blockers.append("worker_inbox_mutation must be false")
    if report.get("approval_inbox_mutation") is not False:
        blockers.append("approval_inbox_mutation must be false")
    if report.get("notification_sent") is not False:
        blockers.append("notification_sent must be false")
    if report.get("service_creation") is not False:
        blockers.append("service_creation must be false")

    return {
        "status": "PASS" if not blockers else "BLOCK",
        "checked_fields": checked_fields,
        "blockers": blockers,
        "unsafe_flags": unsafe_flags,
    }


def build_scheduler_registration_preview_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI_OS Scheduler Registration Preview",
        "",
        f"- scheduler_status: `{report.get('scheduler_status')}`",
        f"- scheduler_registration_allowed: `{report.get('scheduler_registration_allowed')}`",
        f"- scheduler_created: `{report.get('scheduler_created')}`",
        f"- service_created: `{report.get('service_created')}`",
        f"- runtime_launch_allowed: `{report.get('runtime_launch_allowed')}`",
        f"- runtime_execution_allowed: `{report.get('runtime_execution_allowed')}`",
        f"- notification_send_allowed: `{report.get('notification_send_allowed')}`",
        f"- would_schedule: `{report.get('would_schedule')}`",
        f"- would_register_task: `{report.get('would_register_task')}`",
        f"- would_start_service: `{report.get('would_start_service')}`",
        "",
        f"- next_safe_action: `{report.get('safe_next_action')}`",
        "",
        "## Proposed Scheduler Plan",
        f"- {json.dumps(report.get('proposed_scheduler'), indent=2)}",
        "",
        "## Required Dependencies",
    ]
    for item in report.get("required_dependencies", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Remaining Blockers",
            *[f"- {item}" for item in report.get("remaining_blockers", [])],
            "",
            "- This preview does not register scheduler tasks, create services, launch runtime, send notifications, or mutate queue/worker state.",
            "",
        ]
    )
    return "\n".join(lines)


def summarize_scheduler_registration_preview(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheduler_status": report.get("scheduler_status"),
        "scheduler_registration_allowed": report.get("scheduler_registration_allowed"),
        "service_created": report.get("service_created"),
        "runtime_launch_allowed": report.get("runtime_launch_allowed"),
        "runtime_execution_allowed": report.get("runtime_execution_allowed"),
        "notification_send_allowed": report.get("notification_send_allowed"),
        "would_schedule": report.get("would_schedule"),
        "validation_status": report.get("validation", {}).get("status"),
        "remaining_blockers": report.get("remaining_blockers"),
        "safe_next_action": report.get("safe_next_action"),
        "report_paths": report.get("report_paths"),
    }


def write_scheduler_registration_preview(
    report: dict[str, Any],
    *,
    repo_root: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    report_dir = Path(output_dir) if output_dir is not None else root / REPORT_DIR
    if not report_dir.is_absolute():
        report_dir = root / report_dir

    json_path = report_dir / REPORT_JSON_NAME
    md_path = report_dir / REPORT_MD_NAME

    _write_json(json_path, report)
    md_path.write_text(build_scheduler_registration_preview_markdown(report), encoding="utf-8")
    report["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    return report


def run_scheduler_registration_preview(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    report = build_scheduler_registration_preview(
        repo_root=repo_root,
        output_dir=output_dir,
        now=now,
        evidence=evidence,
    )
    if write_report:
        report = write_scheduler_registration_preview(
            report,
            repo_root=repo_root,
            output_dir=output_dir,
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the AI_OS scheduler registration preview.")
    parser.add_argument("--repo-root", default=".", help="Repository root for evidence lookup.")
    parser.add_argument("--output-dir", default=None, help="Output directory for preview report files.")
    parser.add_argument("--now", default=None, help="Optional UTC timestamp override.")
    parser.add_argument("--no-write", action="store_true", help="Build report without writing files.")
    args = parser.parse_args()

    report = run_scheduler_registration_preview(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        now=args.now,
        write_report=not args.no_write,
    )
    print(json.dumps(summarize_scheduler_registration_preview(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
