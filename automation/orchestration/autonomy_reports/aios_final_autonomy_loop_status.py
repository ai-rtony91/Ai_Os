"""AI_OS final autonomy loop status helper (observe-only).

This module summarizes whether AI_OS has enough evidence infrastructure to
continue self-build work through governed proposed packets and human approval.
It does not grant runtime authority, queue authority, scheduler authority, SOS
authority, broker authority, or live-trading authority.

Default behavior is pure: pass dictionaries/lists in, get a JSON-serializable
status dictionary out. The CLI prints JSON to stdout. Optional --out writes only
under Reports/autonomy_loop_closure/ and never overwrites unless --overwrite is
provided.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SCHEMA = "AIOS_FINAL_AUTONOMY_LOOP_STATUS.v1"
ALLOWED_REPORT_DIR = Path("Reports") / "autonomy_loop_closure"

FORBIDDEN_ACTIONS = [
    "runtime_launch",
    "runtime_execution",
    "queue_mutation",
    "approval_mutation",
    "worker_inbox_mutation",
    "command_queue_mutation",
    "scheduler_registration",
    "sos_send",
    "broker_action",
    "live_trading",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bool_from(container: Any, *keys: str) -> bool:
    if not isinstance(container, dict):
        return False
    for key in keys:
        value = container.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.upper() in {"YES", "TRUE", "PASS", "PRESENT", "MERGED", "READY"}:
            return True
    return False


def _recursive_text(obj: Any) -> str:
    if isinstance(obj, dict):
        return " ".join(_recursive_text(v) for v in obj.values())
    if isinstance(obj, list):
        return " ".join(_recursive_text(v) for v in obj)
    return str(obj)


def _contains_explicit(obj: Any, phrases: list[str]) -> bool:
    text = _recursive_text(obj).lower()
    return any(phrase.lower() in text for phrase in phrases)


def _approval_exists(evidence: Any, action: str) -> bool:
    phrases = [
        f"{action} is approved by anthony",
        f"{action} approved by anthony",
        f"anthony approved {action}",
        f"anthony explicitly approved {action}",
    ]
    return _contains_explicit(evidence, phrases)


def _status_if_approved(evidence: Any, action: str) -> str:
    return "APPROVED" if _approval_exists(evidence, action) else "BLOCKED"


def _validation_present(validation_results: Any) -> bool:
    if isinstance(validation_results, dict):
        if _bool_from(validation_results, "validators_present", "all_required_validators_present"):
            return True
        return any(str(v).upper() in {"PASS", "PASSED", "OK", "TRUE"} for v in validation_results.values())
    if isinstance(validation_results, list):
        return len(validation_results) > 0
    return False


def _final_status_tests_pass(validation_results: Any) -> bool:
    if not isinstance(validation_results, dict):
        return False
    if _bool_from(validation_results, "final_status_helper_tests_pass"):
        return True
    value = validation_results.get("test_aios_final_autonomy_loop_status.py")
    return isinstance(value, str) and value.upper() in {"PASS", "PASSED", "OK"}


def _readiness_percent(
    *,
    evidence_ledger_present: bool,
    decision_packet_drafter_present: bool,
    pr_backlog_reconciliation_present: bool,
    t9_recursion_guard_present: bool,
    final_status_tests_pass: bool,
) -> int:
    if not evidence_ledger_present:
        return 0
    if not decision_packet_drafter_present:
        return 25
    if not (pr_backlog_reconciliation_present and t9_recursion_guard_present):
        return 50
    if final_status_tests_pass:
        return 85
    return 75


def _loop_stage(percent: int, *, ledger: bool, drafter: bool) -> str:
    if percent >= 75:
        return "GOVERNED_SELF_BUILD_READY"
    if ledger and drafter:
        return "EVIDENCE_PLUS_DRAFTER"
    if ledger:
        return "EVIDENCE_ONLY"
    return "BLOCKED"


def build_final_autonomy_loop_status(
    *,
    evidence_ledger_digest: Optional[dict] = None,
    pr_backlog_reconciliation: Optional[dict] = None,
    human_gate_evidence: Optional[dict] = None,
    blocker_matrix: Optional[dict] = None,
    available_modules: Optional[dict] = None,
    validation_results: Optional[dict] = None,
    current_repo_state: Optional[dict] = None,
    known_forbidden_action_states: Optional[dict] = None,
    generated_at: Optional[str] = None,
) -> dict[str, object]:
    """Return a conservative, JSON-serializable final autonomy-loop status."""
    evidence_ledger_digest = evidence_ledger_digest or {}
    pr_backlog_reconciliation = pr_backlog_reconciliation or {}
    human_gate_evidence = human_gate_evidence or {}
    blocker_matrix = blocker_matrix or {}
    available_modules = available_modules or {}
    validation_results = validation_results or {}
    current_repo_state = current_repo_state or {}
    known_forbidden_action_states = known_forbidden_action_states or {}

    evidence_ledger_present = _bool_from(
        available_modules,
        "self_build_evidence_ledger_present",
        "evidence_ledger_present",
    ) or bool(evidence_ledger_digest)
    decision_packet_drafter_present = _bool_from(
        available_modules,
        "decision_packet_drafter_present",
        "packet_drafter_present",
    )
    pr_backlog_reconciliation_present = _bool_from(
        available_modules,
        "pr_backlog_reconciliation_present",
    ) or bool(pr_backlog_reconciliation)
    t9_recursion_guard_present = _bool_from(
        available_modules,
        "t9_recursion_guard_present",
        "t9_guard_present",
    )
    validators_present = _validation_present(validation_results)
    final_status_tests_pass = _final_status_tests_pass(validation_results)

    readiness_percent = _readiness_percent(
        evidence_ledger_present=evidence_ledger_present,
        decision_packet_drafter_present=decision_packet_drafter_present,
        pr_backlog_reconciliation_present=pr_backlog_reconciliation_present,
        t9_recursion_guard_present=t9_recursion_guard_present,
        final_status_tests_pass=final_status_tests_pass,
    )

    stop_drill_status = (
        "PROOF_CONSUMED"
        if _contains_explicit(
            human_gate_evidence,
            [
                "STOP drill proof chain v2 was consumed",
                "STOP drill human confirmation was consumed",
            ],
        )
        else "BLOCKED"
    )
    sos_delivery_status = (
        "CONFIRMED"
        if _contains_explicit(
            human_gate_evidence,
            ["live SOS channel was manually registered and tested by Anthony"],
        )
        else "BLOCKED"
    )
    scheduler_registration_status = (
        "CONFIRMED"
        if _contains_explicit(
            human_gate_evidence,
            ["manual scheduler registration was completed and confirmed by Anthony"],
        )
        else "BLOCKED"
    )

    runtime_launch_status = _status_if_approved(human_gate_evidence, "runtime launch")
    runtime_execution_status = _status_if_approved(human_gate_evidence, "runtime execution")
    queue_mutation_status = _status_if_approved(human_gate_evidence, "queue mutation")

    readiness = (
        "READY_FOR_GOVERNED_CONTINUATION"
        if (
            evidence_ledger_present
            and decision_packet_drafter_present
            and pr_backlog_reconciliation_present
            and validators_present
        )
        else "NOT_READY"
    )

    remaining_blockers = []
    for label, status in [
        ("SOS delivery", sos_delivery_status),
        ("Scheduler manual registration", scheduler_registration_status),
        ("Runtime launch approval", runtime_launch_status),
        ("Runtime execution approval", runtime_execution_status),
        ("Queue mutation approval", queue_mutation_status),
        ("Approval inbox mutation", "BLOCKED"),
        ("Worker inbox mutation", "BLOCKED"),
        ("Command queue mutation", "BLOCKED"),
        ("Broker action", "BLOCKED"),
        ("Live trading", "BLOCKED"),
    ]:
        if status == "BLOCKED":
            remaining_blockers.append(label)

    confidence = "HIGH"
    if str(pr_backlog_reconciliation.get("confidence", "")).upper() == "LOW":
        confidence = "LOW"
    elif not pr_backlog_reconciliation_present or not validators_present:
        confidence = "MEDIUM"

    next_safe_actions = [
        "Review and merge the final autonomy loop status PR after checks pass.",
        "Keep runtime launch, runtime execution, queue mutation, scheduler registration, SOS delivery, broker action, and live trading blocked until Anthony explicitly approves a separate lane.",
        "Use proposed work packets for the next review lanes; do not mutate active queues or runtime state from this status surface.",
    ]

    notes = [
        "Self-build readiness means governed continuation through evidence, packet drafts, validation, and human approval.",
        "Self-build readiness does not mean uncontrolled autonomy, runtime authority, broker authority, or live-trading authority.",
    ]
    if blocker_matrix:
        notes.append("External blocker matrix was provided and treated as evidence only.")
    if known_forbidden_action_states:
        notes.append("Known forbidden action states were provided and kept blocked by this packet.")

    return {
        "schema": SCHEMA,
        "status": "OBSERVE_ONLY",
        "generated_at": generated_at or _now(),
        "current_main_head": current_repo_state.get("current_main_head"),
        "self_build_evidence_ledger_present": evidence_ledger_present,
        "decision_packet_drafter_present": decision_packet_drafter_present,
        "pr_backlog_reconciliation_present": pr_backlog_reconciliation_present,
        "t9_recursion_guard_present": t9_recursion_guard_present,
        "stop_drill_status": stop_drill_status,
        "sos_delivery_status": sos_delivery_status,
        "scheduler_registration_status": scheduler_registration_status,
        "runtime_launch_status": runtime_launch_status,
        "runtime_execution_status": runtime_execution_status,
        "queue_mutation_status": queue_mutation_status,
        "approval_mutation_status": "BLOCKED",
        "worker_inbox_mutation_status": "BLOCKED",
        "command_queue_mutation_status": "BLOCKED",
        "broker_action_status": "BLOCKED",
        "live_trading_status": "BLOCKED",
        "self_build_readiness": readiness,
        "self_build_readiness_percent": min(readiness_percent, 85),
        "autonomy_loop_stage": _loop_stage(readiness_percent, ledger=evidence_ledger_present, drafter=decision_packet_drafter_present),
        "can_generate_evidence_digest": evidence_ledger_present,
        "can_generate_packet_draft": decision_packet_drafter_present,
        "can_propose_next_work": decision_packet_drafter_present and pr_backlog_reconciliation_present,
        "can_validate_next_work": validators_present,
        "can_mutate_protected_runtime": False,
        "can_execute_live_trading": False,
        "remaining_blockers": remaining_blockers,
        "next_safe_actions": next_safe_actions,
        "forbidden_actions_confirmed_blocked": list(FORBIDDEN_ACTIONS),
        "evidence_notes": notes,
        "confidence": confidence,
    }


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def _is_allowed_out_path(out_path: Path, *, repo_root: Optional[Path] = None) -> bool:
    base = Path(repo_root) if repo_root else Path.cwd()
    allowed = (base / ALLOWED_REPORT_DIR).resolve()
    candidate = Path(out_path)
    if not candidate.is_absolute():
        candidate = base / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(allowed)
    except ValueError:
        return False
    return True


def write_status(status: dict, out_path: Path, *, overwrite: bool = False, repo_root: Optional[Path] = None) -> dict[str, object]:
    """Write status JSON only under Reports/autonomy_loop_closure/."""
    if not _is_allowed_out_path(out_path, repo_root=repo_root):
        return {"written": False, "status": "BLOCKED_OUTSIDE_ALLOWED_REPORT_DIR", "json_path": str(out_path)}
    out_path = Path(out_path)
    if out_path.exists() and not overwrite:
        return {"written": False, "status": "SKIPPED_EXISTS", "json_path": str(out_path)}
    _atomic_write_text(out_path, json.dumps(status, indent=2, sort_keys=True))
    return {"written": True, "status": "WRITTEN", "json_path": str(out_path)}


def _load_json(path: Optional[str]) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build an observe-only AI_OS final autonomy loop status JSON.")
    parser.add_argument("--evidence-ledger", default=None)
    parser.add_argument("--pr-backlog", default=None)
    parser.add_argument("--human-gate", default=None)
    parser.add_argument("--blocker-matrix", default=None)
    parser.add_argument("--available-modules", default=None)
    parser.add_argument("--validation-results", default=None)
    parser.add_argument("--repo-state", default=None)
    parser.add_argument("--known-forbidden-action-states", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    status = build_final_autonomy_loop_status(
        evidence_ledger_digest=_load_json(args.evidence_ledger),
        pr_backlog_reconciliation=_load_json(args.pr_backlog),
        human_gate_evidence=_load_json(args.human_gate),
        blocker_matrix=_load_json(args.blocker_matrix),
        available_modules=_load_json(args.available_modules),
        validation_results=_load_json(args.validation_results),
        current_repo_state=_load_json(args.repo_state),
        known_forbidden_action_states=_load_json(args.known_forbidden_action_states),
    )
    if args.out:
        status["_write_result"] = write_status(status, Path(args.out), overwrite=args.overwrite)
    print(json.dumps(status, indent=2, sort_keys=True))
    if args.out and status["_write_result"]["status"] == "BLOCKED_OUTSIDE_ALLOWED_REPORT_DIR":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
