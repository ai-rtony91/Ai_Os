"""AI_OS STOP drill preview proof.

This report proves the STOP drill lane is still preview-only and human-gated.
It does not execute a stop, kill processes, mutate runtime state, launch
runtime, or write to active queue state.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_STOP_DRILL_PREVIEW.v1"
MODE = "DRY_RUN_PREVIEW_ONLY"
REPORT_DIR = Path("Reports") / "stop_drill_preview"
REPORT_JSON_NAME = "stop_drill_preview.json"
REPORT_MD_NAME = "stop_drill_preview.md"
ALLOWED_STATUSES = {"REVIEWABLE", "HUMAN_GATE_REQUIRED"}


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_stop_drill_preview(
    *,
    now: str | None = None,
    explicit_human_confirmation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    confirmed = (
        isinstance(explicit_human_confirmation, dict)
        and explicit_human_confirmation.get("explicit_human_provided_evidence") is True
        and explicit_human_confirmation.get("stop_drill_confirmed") is True
    )
    status = "REVIEWABLE" if confirmed else "HUMAN_GATE_REQUIRED"
    manual_step = (
        "Human must perform/confirm STOP drill in a separately approved STOP drill packet; this preview does not stop or kill anything."
    )
    report = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": _now(now),
        "status": status,
        "proof_status": status,
        "review_status": status,
        "stop_drill_reviewable": confirmed,
        "explicit_human_provided_evidence": confirmed,
        "manual_step_required": None if confirmed else manual_step,
        "human_gate": None if confirmed else "stop_drill_human_confirmation",
        "stop_executed": False,
        "kill_processes_allowed": False,
        "process_kill_attempted": False,
        "runtime_mutation_allowed": False,
        "runtime_launch_allowed": False,
        "runtime_execution_allowed": False,
        "queue_mutation_allowed": False,
        "worker_inbox_mutation_allowed": False,
        "command_queue_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "scheduler_registration_allowed": False,
        "notification_send_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
        "protected_mutation_detected": False,
        "safe_next_action": (
            "Human STOP drill confirmation can be reviewed as evidence."
            if confirmed
            else manual_step
        ),
        "stop_condition": "Stop before executing stop, killing processes, mutating runtime, sending SOS, or creating scheduler tasks.",
    }
    return report


def validate_stop_drill_preview(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    if not isinstance(report, dict):
        return {"status": "BLOCK", "blockers": ["report must be an object"], "unsafe_flags": ["report_not_object"]}
    if report.get("schema") != SCHEMA:
        blockers.append("schema is invalid")
    if report.get("mode") != MODE:
        blockers.append("mode is invalid")
    if report.get("status") not in ALLOWED_STATUSES:
        blockers.append("status must be REVIEWABLE or HUMAN_GATE_REQUIRED")
    for field in [
        "stop_executed",
        "kill_processes_allowed",
        "process_kill_attempted",
        "runtime_mutation_allowed",
        "runtime_launch_allowed",
        "runtime_execution_allowed",
        "queue_mutation_allowed",
        "worker_inbox_mutation_allowed",
        "command_queue_mutation_allowed",
        "scheduler_creation_allowed",
        "scheduler_registration_allowed",
        "notification_send_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "protected_mutation_detected",
    ]:
        if report.get(field) is not False:
            blockers.append(f"{field} must remain false")
            unsafe_flags.append(f"{field}_true")
    if report.get("status") == "HUMAN_GATE_REQUIRED" and not report.get("manual_step_required"):
        blockers.append("manual_step_required must be present when human gate is required")
    return {
        "status": "PASS" if not blockers else "BLOCK",
        "blockers": blockers,
        "unsafe_flags": unsafe_flags,
        "checked_fields": [
            "schema",
            "mode",
            "status",
            "manual_step_required",
            "protected false flags",
        ],
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI_OS STOP Drill Preview",
        "",
        f"- status: `{report.get('status')}`",
        f"- stop_executed: `{report.get('stop_executed')}`",
        f"- runtime_execution_allowed: `{report.get('runtime_execution_allowed')}`",
        f"- scheduler_creation_allowed: `{report.get('scheduler_creation_allowed')}`",
        f"- notification_send_allowed: `{report.get('notification_send_allowed')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Manual Step",
        f"- {report.get('manual_step_required') or 'Human confirmation evidence is present for review.'}",
    ]
    return "\n".join(lines) + "\n"


def write_stop_drill_preview_reports(
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
    written = copy.deepcopy(report)
    written["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    written["validation"] = validate_stop_drill_preview(written)
    json_path.write_text(json.dumps(written, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_markdown(written), encoding="utf-8")
    return written


def run_stop_drill_preview(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    write_report: bool = True,
    now: str | None = None,
) -> dict[str, Any]:
    report = build_stop_drill_preview(now=now)
    if write_report:
        report = write_stop_drill_preview_reports(report, repo_root=repo_root, output_dir=output_dir)
    return report


def _cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI_OS STOP drill preview proof")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--output-dir", default=None, help="optional output directory")
    parser.add_argument("--no-write", action="store_true", help="build without writing reports")
    parser.add_argument("--now", default=None, help="override generated_at_utc")
    return parser.parse_args()


def main() -> int:
    args = _cli_args()
    report = run_stop_drill_preview(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        write_report=not args.no_write,
        now=args.now,
    )
    print(json.dumps({"status": report.get("status"), "validation": report.get("validation")}, indent=2, sort_keys=True))
    return 0 if (report.get("validation") or {}).get("status") in {None, "PASS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
