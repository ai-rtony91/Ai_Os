"""AI_OS runtime queue blocker stack normalizer.

This proof surface reads existing dry-run reports and converts stale runtime
queue blocker labels into explicit proof statuses or human-gated requests. It
does not mutate active queues, worker inboxes, command queues, runtime state,
scheduler state, SOS channels, credentials, or trading paths.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from automation.orchestration.runtime_closure.aios_runtime_execution_queue import (
    build_runtime_execution_queue,
)


SCHEMA = "AIOS_RUNTIME_QUEUE_BLOCKER_STACK.v1"
MODE = "DRY_RUN_PROOF"
REPORT_DIR = Path("Reports") / "runtime_queue_blocker_stack"
REPORT_JSON_NAME = "runtime_queue_blocker_stack.json"
REPORT_MD_NAME = "runtime_queue_blocker_stack.md"

HUMAN_GATE_DIR = Path("Reports") / "human_gate"
SOS_REQUEST_JSON = "sos_delivery_request.json"
SOS_REQUEST_MD = "sos_delivery_request.md"
SCHEDULER_REQUEST_JSON = "scheduler_manual_registration_request.json"
SCHEDULER_REQUEST_MD = "scheduler_manual_registration_request.md"

DEFAULT_RUNTIME_PROOF = Path("Reports") / "runtime_proof_gate" / "runtime_proof_gate_preview.json"
DEFAULT_RELAY_REVIEW = Path("Reports") / "relay_proof_review" / "relay_proof_review.json"
DEFAULT_RELAY_PREDECESSOR = Path("Reports") / "relay_predecessor_proof" / "relay_predecessor_proof.json"
DEFAULT_STOP_DRILL_PREVIEW = Path("Reports") / "stop_drill_preview" / "stop_drill_preview.json"
DEFAULT_SOS_PREVIEW = Path("Reports") / "sos_preview" / "sos_arming_preview.json"
DEFAULT_SCHEDULER_PREVIEW = Path("Reports") / "scheduler_preview" / "scheduler_registration_preview.json"

ALLOWED_STATUSES = {
    "PASS",
    "REVIEWABLE",
    "HUMAN_GATE_REQUIRED",
    "BLOCKED_WITH_REAL_REASON",
    "MISSING",
    "INVALID",
}

PROOF_KEYS = [
    "relay_runtime_proof",
    "restart_timeouts_proof",
    "retention_rotation_proof",
    "soak_proof",
    "stop_drill_proof",
    "sos_delivery_proof",
    "scheduler_manual_registration_proof",
]

STALE_ALIAS_MAP = {
    "relay runtime proof missing": "relay_runtime_proof",
    "restart/timeouts proof missing": "restart_timeouts_proof",
    "retention proof missing": "retention_rotation_proof",
    "soak proof missing": "soak_proof",
    "STOP drill proof missing": "stop_drill_proof",
    "SOS delivered:true missing": "sos_delivery_proof",
    "scheduler manual registration missing": "scheduler_manual_registration_proof",
}

PROTECTED_FALSE_FIELDS = {
    "queue_mutation_allowed": False,
    "worker_inbox_mutation_allowed": False,
    "command_queue_mutation_allowed": False,
    "runtime_execution_allowed": False,
    "runtime_launch_allowed": False,
    "scheduler_creation_allowed": False,
    "scheduler_registration_allowed": False,
    "notification_send_allowed": False,
    "sos_allowed": False,
    "live_trading_allowed": False,
    "credentials_accessed": False,
    "vacation_mode_complete": False,
}


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _norm(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _first_status(*values: Any) -> str:
    for value in values:
        status = _norm(value)
        if status:
            return status
    return "MISSING"


def _nested_status(payload: dict[str, Any] | None, *path: str) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _safe_bool(payload: dict[str, Any] | None, key: str) -> bool:
    return bool(payload.get(key)) if isinstance(payload, dict) else False


def _proof(
    *,
    status: str,
    source: str,
    reason: str,
    human_gate: str | None = None,
    aliases: list[str] | None = None,
    safe_next_action: str | None = None,
) -> dict[str, Any]:
    normalized = _norm(status)
    if normalized not in ALLOWED_STATUSES:
        normalized = "INVALID"
    return {
        "status": normalized,
        "source": source,
        "reason": reason,
        "human_gate": human_gate,
        "aliases": aliases or [],
        "safe_next_action": safe_next_action,
    }


def _relay_status(runtime_proof: dict[str, Any] | None, relay_review: dict[str, Any] | None) -> str:
    return _first_status(
        runtime_proof.get("relay_review_status") if isinstance(runtime_proof, dict) else None,
        relay_review.get("review_status") if isinstance(relay_review, dict) else None,
        _nested_status(relay_review, "summary", "review_status"),
        _nested_status(runtime_proof, "cross_proof_consistency", "relay_review_status"),
    )


def _proof_status(runtime_proof: dict[str, Any] | None, top_level: str, cross_level: str, summary: str) -> str:
    return _first_status(
        runtime_proof.get(top_level) if isinstance(runtime_proof, dict) else None,
        _nested_status(runtime_proof, "cross_proof_consistency", cross_level),
        _nested_status(runtime_proof, summary, "proof_status"),
        _nested_status(runtime_proof, "prerequisite_statuses", summary.replace("_summary", "_proof")),
    )


def _explicit_sos_evidence(root: Path) -> dict[str, Any] | None:
    for relative in [
        Path("Reports") / "human_gate" / "sos_delivery_evidence.json",
        Path("Reports") / "human_gate" / "sos_delivery_confirmation.json",
    ]:
        payload = _read_json(root / relative)
        if not isinstance(payload, dict):
            continue
        if payload.get("delivered_true") is True and payload.get("explicit_human_provided_evidence") is True:
            return payload
    return None


def _explicit_scheduler_evidence(root: Path) -> dict[str, Any] | None:
    for relative in [
        Path("Reports") / "human_gate" / "scheduler_manual_registration_evidence.json",
        Path("Reports") / "human_gate" / "scheduler_manual_registration_confirmation.json",
    ]:
        payload = _read_json(root / relative)
        if not isinstance(payload, dict):
            continue
        if (
            payload.get("manual_registration_confirmed") is True
            and payload.get("explicit_human_provided_evidence") is True
        ):
            return payload
    return None


def build_sos_delivery_request(*, now: str | None = None) -> dict[str, Any]:
    return {
        "schema": "AIOS_HUMAN_GATE_SOS_DELIVERY_REQUEST.v1",
        "generated_at_utc": _now(now),
        "mode": "PREVIEW_ONLY_HUMAN_GATE_REQUEST",
        "status": "HUMAN_GATE_REQUIRED",
        "real_channel_armed": False,
        "notification_send_allowed": False,
        "notification_sent": False,
        "delivered_true": False,
        "explicit_human_provided_evidence": False,
        "runtime_execution_allowed": False,
        "runtime_launch_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
        "safe_next_action": (
            "Human must perform/confirm SOS delivery in a separately approved real channel packet."
        ),
        "stop_condition": "Stop before sending SOS, arming a real channel, storing credentials, or claiming delivered:true.",
    }


def build_scheduler_manual_registration_request(*, now: str | None = None) -> dict[str, Any]:
    return {
        "schema": "AIOS_HUMAN_GATE_SCHEDULER_MANUAL_REGISTRATION_REQUEST.v1",
        "generated_at_utc": _now(now),
        "mode": "PREVIEW_ONLY_HUMAN_GATE_REQUEST",
        "status": "HUMAN_GATE_REQUIRED",
        "real_scheduler_registered": False,
        "scheduler_creation_allowed": False,
        "scheduler_registration_allowed": False,
        "manual_registration_confirmed": False,
        "explicit_human_provided_evidence": False,
        "runtime_execution_allowed": False,
        "runtime_launch_allowed": False,
        "notification_send_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
        "safe_next_action": (
            "Human must perform/confirm scheduler registration in a separately approved real scheduler packet."
        ),
        "stop_condition": "Stop before creating Windows Scheduled Tasks, services, or claiming manual registration.",
    }


def _request_markdown(title: str, request: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- status: `{request.get('status')}`",
        f"- generated_at_utc: `{request.get('generated_at_utc')}`",
        f"- safe_next_action: {request.get('safe_next_action')}",
        f"- stop_condition: {request.get('stop_condition')}",
        "",
        "## Safety Flags",
    ]
    for key in sorted(k for k in request if k.endswith("_allowed") or k in {"delivered_true", "manual_registration_confirmed", "real_channel_armed", "real_scheduler_registered"}):
        lines.append(f"- {key}: `{request.get(key)}`")
    return "\n".join(lines) + "\n"


def write_human_gate_requests(
    *,
    repo_root: str | Path = ".",
    now: str | None = None,
    write_reports: bool = True,
) -> dict[str, dict[str, Any]]:
    root = Path(repo_root)
    sos_evidence = _explicit_sos_evidence(root)
    scheduler_evidence = _explicit_scheduler_evidence(root)

    sos_request = _deepcopy(sos_evidence) if sos_evidence else build_sos_delivery_request(now=now)
    scheduler_request = _deepcopy(scheduler_evidence) if scheduler_evidence else build_scheduler_manual_registration_request(now=now)

    if write_reports:
        out_dir = root / HUMAN_GATE_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / SOS_REQUEST_JSON).write_text(json.dumps(sos_request, indent=2, sort_keys=True), encoding="utf-8")
        (out_dir / SOS_REQUEST_MD).write_text(
            _request_markdown("AI_OS SOS Delivery Human Gate Request", sos_request),
            encoding="utf-8",
        )
        (out_dir / SCHEDULER_REQUEST_JSON).write_text(
            json.dumps(scheduler_request, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (out_dir / SCHEDULER_REQUEST_MD).write_text(
            _request_markdown("AI_OS Scheduler Manual Registration Human Gate Request", scheduler_request),
            encoding="utf-8",
        )

    return {
        "sos_delivery_request": sos_request,
        "scheduler_manual_registration_request": scheduler_request,
    }


def _proofs_from_evidence(
    *,
    root: Path,
    runtime_proof: dict[str, Any] | None,
    relay_review: dict[str, Any] | None,
    stop_preview: dict[str, Any] | None,
    sos_request: dict[str, Any],
    scheduler_request: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    relay_status = _relay_status(runtime_proof, relay_review)
    restart_status = _proof_status(runtime_proof, "restart_timeouts_status", "restart_timeouts_status", "restart_timeouts_summary")
    retention_status = _proof_status(runtime_proof, "retention_rotation_status", "retention_rotation_status", "retention_rotation_summary")
    soak_status = _proof_status(runtime_proof, "soak_status", "soak_status", "soak_summary")

    stop_status = _first_status(stop_preview.get("status") if isinstance(stop_preview, dict) else None)
    if stop_status == "MISSING":
        stop_status = "HUMAN_GATE_REQUIRED"
    if stop_status not in {"REVIEWABLE", "HUMAN_GATE_REQUIRED"}:
        stop_status = "BLOCKED_WITH_REAL_REASON" if stop_status == "BLOCKED" else stop_status

    sos_status = "PASS" if sos_request.get("delivered_true") is True else "HUMAN_GATE_REQUIRED"
    scheduler_status = (
        "PASS"
        if scheduler_request.get("manual_registration_confirmed") is True
        else "HUMAN_GATE_REQUIRED"
    )

    return {
        "relay_runtime_proof": _proof(
            status="REVIEWABLE" if relay_status == "REVIEWABLE" else relay_status,
            source=str(DEFAULT_RELAY_REVIEW),
            reason="Relay proof review REVIEWABLE maps to relay_runtime_proof REVIEWABLE; it does not approve runtime execution.",
            aliases=["relay runtime proof missing"],
            safe_next_action="Human reviews relay proof acceptance separately; runtime execution remains blocked.",
        ),
        "restart_timeouts_proof": _proof(
            status=restart_status,
            source=str(DEFAULT_RUNTIME_PROOF),
            reason="restart/timeouts proof alias normalized from runtime proof gate evidence.",
            aliases=["restart/timeouts proof missing", "restart_timeouts_proof"],
        ),
        "retention_rotation_proof": _proof(
            status=retention_status,
            source=str(DEFAULT_RUNTIME_PROOF),
            reason="retention proof alias normalized to retention_rotation_proof.",
            aliases=["retention proof missing", "retention_rotation_proof"],
        ),
        "soak_proof": _proof(
            status=soak_status,
            source=str(DEFAULT_RUNTIME_PROOF),
            reason="soak proof alias normalized from runtime proof gate evidence.",
            aliases=["soak proof missing", "soak_proof"],
        ),
        "stop_drill_proof": _proof(
            status=stop_status,
            source=str(DEFAULT_STOP_DRILL_PREVIEW if (root / DEFAULT_STOP_DRILL_PREVIEW).exists() else DEFAULT_RELAY_REVIEW),
            reason="STOP drill remains preview-only and requires human confirmation unless a reviewable proof exists.",
            human_gate="stop_drill_human_confirmation",
            aliases=["STOP drill proof missing"],
            safe_next_action="Human must approve/confirm the STOP drill in a separate real STOP drill packet before runtime readiness.",
        ),
        "sos_delivery_proof": _proof(
            status=sos_status,
            source=str(HUMAN_GATE_DIR / SOS_REQUEST_JSON),
            reason="SOS delivered:true cannot be claimed without explicit human-provided evidence.",
            human_gate="sos_delivery_human_confirmation",
            aliases=["SOS delivered:true missing"],
            safe_next_action=sos_request.get("safe_next_action"),
        ),
        "scheduler_manual_registration_proof": _proof(
            status=scheduler_status,
            source=str(HUMAN_GATE_DIR / SCHEDULER_REQUEST_JSON),
            reason="Scheduler manual registration cannot be claimed without explicit human-provided evidence.",
            human_gate="scheduler_manual_registration_human_confirmation",
            aliases=["scheduler manual registration missing"],
            safe_next_action=scheduler_request.get("safe_next_action"),
        ),
    }


def _normalized_queue_readout(proofs: dict[str, dict[str, Any]], *, now: str | None = None) -> dict[str, Any]:
    state = {
        "ledger_on_main": True,
        "approval_card_present": True,
        "completeness_ready": True,
        "path_guard_pass": True,
        "apply_inventory_target_selected": True,
        "runtime_dry_run_pass": proofs["relay_runtime_proof"]["status"] in {"REVIEWABLE", "PASS"},
        "restart_timeout_proof_pass": proofs["restart_timeouts_proof"]["status"] == "PASS",
        "retention_dry_run_pass": proofs["retention_rotation_proof"]["status"] == "PASS",
        "soak_pass": proofs["soak_proof"]["status"] == "PASS",
        "stop_drill_pass": proofs["stop_drill_proof"]["status"] == "PASS",
        "sos_delivered_true": proofs["sos_delivery_proof"]["status"] == "PASS",
        "scheduler_registered_by_anthony": proofs["scheduler_manual_registration_proof"]["status"] == "PASS",
        "vacation_mode_complete": False,
    }
    queue = build_runtime_execution_queue(state)
    human_gate_blockers = [
        proof["human_gate"]
        for proof in proofs.values()
        if proof.get("status") == "HUMAN_GATE_REQUIRED" and proof.get("human_gate")
    ]
    status = "HUMAN_GATE_REQUIRED" if human_gate_blockers else "REVIEWABLE"
    queue.update(
        {
            "generated_at_utc": _now(now),
            "status": status,
            "normalized_status": status,
            "validation_status": status,
            "human_gate_only_blockers": bool(human_gate_blockers),
            "human_gate_blockers": human_gate_blockers,
            "proofs": _deepcopy(proofs),
            "vacation_mode_complete": False,
        }
    )
    return queue


def build_runtime_queue_blocker_stack(
    *,
    repo_root: str | Path = ".",
    now: str | None = None,
    write_human_requests: bool = True,
    runtime_proof: dict[str, Any] | None = None,
    relay_review: dict[str, Any] | None = None,
    relay_predecessor: dict[str, Any] | None = None,
    stop_preview: dict[str, Any] | None = None,
    sos_request: dict[str, Any] | None = None,
    scheduler_request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    generated_at = _now(now)
    runtime_proof = runtime_proof if isinstance(runtime_proof, dict) else _read_json(root / DEFAULT_RUNTIME_PROOF)
    relay_review = relay_review if isinstance(relay_review, dict) else _read_json(root / DEFAULT_RELAY_REVIEW)
    relay_predecessor = relay_predecessor if isinstance(relay_predecessor, dict) else _read_json(root / DEFAULT_RELAY_PREDECESSOR)
    stop_preview = stop_preview if isinstance(stop_preview, dict) else _read_json(root / DEFAULT_STOP_DRILL_PREVIEW)

    requests = write_human_gate_requests(repo_root=root, now=generated_at, write_reports=write_human_requests)
    sos_request = sos_request if isinstance(sos_request, dict) else requests["sos_delivery_request"]
    scheduler_request = (
        scheduler_request
        if isinstance(scheduler_request, dict)
        else requests["scheduler_manual_registration_request"]
    )

    proofs = _proofs_from_evidence(
        root=root,
        runtime_proof=runtime_proof,
        relay_review=relay_review,
        stop_preview=stop_preview,
        sos_request=sos_request,
        scheduler_request=scheduler_request,
    )

    statuses = {key: proof["status"] for key, proof in proofs.items()}
    stale_layers = [
        alias
        for alias, key in STALE_ALIAS_MAP.items()
        if key in proofs and proofs[key]["status"] in {"PASS", "REVIEWABLE", "HUMAN_GATE_REQUIRED"}
    ]
    human_gate_blockers = [
        proof["human_gate"]
        for proof in proofs.values()
        if proof.get("status") == "HUMAN_GATE_REQUIRED" and proof.get("human_gate")
    ]
    missing = [key for key, status in statuses.items() if status == "MISSING"]
    invalid = [key for key, status in statuses.items() if status == "INVALID"]
    real_blocked = [key for key, status in statuses.items() if status == "BLOCKED_WITH_REAL_REASON"]

    if invalid:
        status = "INVALID"
    elif real_blocked:
        status = "BLOCKED_WITH_REAL_REASON"
    elif human_gate_blockers:
        status = "HUMAN_GATE_REQUIRED"
    elif missing:
        status = "MISSING"
    else:
        status = "REVIEWABLE"

    normalized_queue = _normalized_queue_readout(proofs, now=generated_at)
    normalized_queue["status"] = status
    normalized_queue["normalized_status"] = status
    normalized_queue["validation_status"] = status

    report = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": generated_at,
        "status": status,
        "proofs": proofs,
        "proof_statuses": statuses,
        "alias_normalization": {
            alias: {"proof": key, "status": statuses.get(key)}
            for alias, key in STALE_ALIAS_MAP.items()
        },
        "stale_layers": [],
        "stale_blockers_resolved": stale_layers,
        "missing_proofs": missing,
        "invalid_proofs": invalid,
        "real_blockers": real_blocked,
        "human_gate_blockers": human_gate_blockers,
        "human_gate_only_blockers": bool(human_gate_blockers) and not missing and not invalid and not real_blocked,
        "normalized_runtime_queue_readout": normalized_queue,
        "source_reports": {
            "runtime_proof_gate": str(DEFAULT_RUNTIME_PROOF),
            "relay_proof_review": str(DEFAULT_RELAY_REVIEW),
            "relay_predecessor_proof": str(DEFAULT_RELAY_PREDECESSOR),
            "stop_drill_preview": str(DEFAULT_STOP_DRILL_PREVIEW),
            "sos_delivery_request": str(HUMAN_GATE_DIR / SOS_REQUEST_JSON),
            "scheduler_manual_registration_request": str(HUMAN_GATE_DIR / SCHEDULER_REQUEST_JSON),
            "sos_preview": str(DEFAULT_SOS_PREVIEW),
            "scheduler_preview": str(DEFAULT_SCHEDULER_PREVIEW),
        },
        "source_loaded": {
            "runtime_proof_gate": isinstance(runtime_proof, dict),
            "relay_proof_review": isinstance(relay_review, dict),
            "relay_predecessor_proof": isinstance(relay_predecessor, dict),
            "stop_drill_preview": isinstance(stop_preview, dict),
            "sos_delivery_request": isinstance(sos_request, dict),
            "scheduler_manual_registration_request": isinstance(scheduler_request, dict),
        },
        "protected_mutation_detected": False,
        **PROTECTED_FALSE_FIELDS,
        "safe_next_action": (
            "Human must resolve the listed human-gated confirmations in separately approved packets."
            if human_gate_blockers
            else "Review normalized runtime queue proof stack; do not execute runtime."
        ),
        "stop_condition": (
            "Stop before active queue mutation, worker inbox mutation, command queue mutation, runtime launch, "
            "scheduler registration, SOS send, credential access, or live trading."
        ),
    }
    return report


def validate_runtime_queue_blocker_stack(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    if not isinstance(report, dict):
        return {"status": "BLOCK", "blockers": ["report must be an object"], "unsafe_flags": ["report_not_object"]}
    if report.get("schema") != SCHEMA:
        blockers.append("schema is invalid")
    if report.get("mode") != MODE:
        blockers.append("mode is invalid")
    if report.get("status") not in ALLOWED_STATUSES:
        blockers.append("status is invalid")
    proofs = report.get("proofs")
    if not isinstance(proofs, dict):
        blockers.append("proofs must be an object")
    else:
        for key in PROOF_KEYS:
            proof = proofs.get(key)
            if not isinstance(proof, dict):
                blockers.append(f"{key} proof is missing")
                continue
            if proof.get("status") not in ALLOWED_STATUSES:
                blockers.append(f"{key} status is invalid")
    for key, expected in PROTECTED_FALSE_FIELDS.items():
        if report.get(key) is not expected:
            blockers.append(f"{key} must remain false")
            unsafe_flags.append(f"{key}_true")
    if report.get("protected_mutation_detected") is not False:
        blockers.append("protected_mutation_detected must remain false")
        unsafe_flags.append("protected_mutation_detected")
    if report.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must remain false")
        unsafe_flags.append("vacation_mode_complete_true")
    return {
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": blockers,
        "unsafe_flags": unsafe_flags,
        "checked_proofs": list(PROOF_KEYS),
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI_OS Runtime Queue Blocker Stack",
        "",
        f"- status: `{report.get('status')}`",
        f"- protected_mutation_detected: `{report.get('protected_mutation_detected')}`",
        f"- human_gate_only_blockers: `{report.get('human_gate_only_blockers')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Proofs",
    ]
    proofs = report.get("proofs") if isinstance(report.get("proofs"), dict) else {}
    for key in PROOF_KEYS:
        proof = proofs.get(key, {})
        lines.append(f"- {key}: `{proof.get('status')}`")
    lines.extend(["", "## Human Gates"])
    blockers = list(report.get("human_gate_blockers") or [])
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    lines.extend(["", "## Stale Blockers Resolved"])
    lines.extend([f"- {item}" for item in list(report.get("stale_blockers_resolved") or [])] or ["- none"])
    return "\n".join(lines) + "\n"


def write_runtime_queue_blocker_stack_reports(
    report: dict[str, Any],
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    out_dir = Path(output_dir) if output_dir is not None else root / REPORT_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / REPORT_JSON_NAME
    md_path = out_dir / REPORT_MD_NAME
    written = _deepcopy(report)
    written["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    written["validation"] = validate_runtime_queue_blocker_stack(written)
    json_path.write_text(json.dumps(written, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_markdown(written), encoding="utf-8")
    return written


def run_runtime_queue_blocker_stack(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    write_report: bool = True,
    now: str | None = None,
) -> dict[str, Any]:
    report = build_runtime_queue_blocker_stack(repo_root=repo_root, now=now, write_human_requests=write_report)
    if write_report:
        report = write_runtime_queue_blocker_stack_reports(report, repo_root=repo_root, output_dir=output_dir)
    return report


def _cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI_OS runtime queue blocker stack normalizer")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--output-dir", default=None, help="optional output directory")
    parser.add_argument("--no-write", action="store_true", help="build without writing reports")
    parser.add_argument("--now", default=None, help="override generated_at_utc")
    return parser.parse_args()


def main() -> int:
    args = _cli_args()
    report = run_runtime_queue_blocker_stack(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        write_report=not args.no_write,
        now=args.now,
    )
    print(json.dumps({"summary": {"status": report.get("status"), "human_gate_blockers": report.get("human_gate_blockers")}, "validation": report.get("validation")}, indent=2, sort_keys=True))
    return 0 if (report.get("validation") or {}).get("status") in {None, "PASS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
