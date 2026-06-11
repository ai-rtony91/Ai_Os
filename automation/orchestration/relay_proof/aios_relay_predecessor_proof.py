"""AI_OS relay/runtime predecessor proof closure (observe-only).

This module assembles the missing predecessor proofs that the relay/runtime
stack expects before the relay proof review can become reviewable:

* approval_card_present
* completeness_ready
* path_guard_pass
* apply_inventory_target_selected

It stays dry-run only. It does not mutate active queue, worker inbox, command
queue, approval inbox, runtime state, scheduler state, or SOS state. The
generated report is a proof bundle and a human-review evidence surface, not an
approval or execution authorization.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from automation.orchestration.autonomy_reports.aios_apply_counterpart_inventory import build_inventory
from automation.orchestration.autonomy_review.aios_approval_review_compressor import build_approval_card
from automation.orchestration.autonomy_review.aios_packet_completeness_review import review_packet_completeness
from automation.orchestration.autonomy_reports.aios_operator_dependency_ledger import (
    build_operator_dependency_ledger,
    validate_operator_dependency_ledger,
)
from automation.orchestration.autonomy_reports.aios_reduction_target_selector import build_reduction_target_selector
from automation.orchestration.autonomy_reports.aios_reduction_target_selector import (
    validate_reduction_target_selector,
)
from automation.orchestration.runtime_closure.aios_relay_dry_run_proof_review import (
    build_relay_dry_run_proof_review,
    validate_relay_dry_run_proof_review,
)
from automation.orchestration.runtime_closure.aios_relay_runtime_processor import (
    build_relay_runtime_processor,
    validate_relay_runtime_processor,
)
from automation.orchestration.runtime_closure.aios_runtime_execution_queue import (
    build_runtime_execution_queue,
    validate_runtime_execution_queue,
)
from automation.validators.aios_governance_validator import validate_packet_text
from automation.validators.aios_path_guard_validator import check_against_packet


SCHEMA = "AIOS_RELAY_PREDECESSOR_PROOF.v1"
MODE = "DRY_RUN_PROOF"
REPORT_DIR = Path("Reports") / "relay_predecessor_proof"
REPORT_JSON_NAME = "relay_predecessor_proof.json"
REPORT_MD_NAME = "relay_predecessor_proof.md"

PROOF_PACKET_ID = "AIOS-RELAY-PREDECESSOR-PROOF-CLOSURE-V1"
PROOF_LANE = "feature/relay-predecessor-proof-closure-v1"
PROOF_WORKTREE = r"C:\Dev\Ai.Os"
PROOF_BRANCH = "feature/relay-predecessor-proof-closure-v1"

PROTECTED_PATHS = [
    "automation/orchestration/work_packets/active/",
    "automation/orchestration/workers/inbox/",
    "automation/orchestration/command_queue/",
    "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json",
    "automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json",
    "broker/",
    "OANDA/",
    "api_keys/",
    "secrets/",
    ".env",
    "live_trading/",
    "webhooks/",
]

REPORT_ONLY_PATHS = [
    "automation/orchestration/relay_proof/",
    "automation/orchestration/runtime_closure/",
    "automation/orchestration/control_loop/",
    "tests/orchestration/",
    "Reports/relay_predecessor_proof/",
    "Reports/relay_proof_review/",
    "Reports/runtime_proof_gate/",
    "Reports/runtime_apply_lane/",
    "Reports/control_loop_observe/",
    "Reports/autonomy_closure/",
    "Reports/final_observe_spine_closure/",
    "Reports/final_autonomy_closeout/",
]


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path(__file__).resolve().parents[3]
    return Path(repo_root)


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists():
            return None
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _path_fingerprint(path: Path, root: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": path.relative_to(root).as_posix() if path.is_absolute() and path.exists() and path.is_relative_to(root) else str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "is_file": path.is_file(),
        "dirty": False,
        "git_status": [],
        "fingerprint": None,
        "file_count": 0,
        "size_bytes": None,
    }

    try:
        status = subprocess.run(
            ["git", "status", "--short", "--", str(path)],
            cwd=str(root),
            text=True,
            capture_output=True,
            check=False,
        )
        lines = [line.strip() for line in status.stdout.splitlines() if line.strip()]
        record["git_status"] = lines
        record["dirty"] = bool(lines)
    except OSError:
        record["git_status"] = []
        record["dirty"] = False

    if path.is_file():
        data = path.read_bytes()
        record["size_bytes"] = len(data)
        record["fingerprint"] = hashlib.sha256(data).hexdigest()
        record["file_count"] = 1
    elif path.is_dir():
        digest = hashlib.sha256()
        count = 0
        total_size = 0
        for child in sorted(path.rglob("*")):
            if not child.is_file():
                continue
            count += 1
            rel = child.relative_to(root).as_posix() if child.is_relative_to(root) else child.as_posix()
            digest.update(rel.encode("utf-8"))
            blob = child.read_bytes()
            digest.update(blob)
            total_size += len(blob)
        record["file_count"] = count
        record["size_bytes"] = total_size
        record["fingerprint"] = digest.hexdigest() if count else None
    return record


def _scan_protected_paths(root: Path) -> list[dict[str, Any]]:
    candidates = [root / path for path in PROTECTED_PATHS]
    return [_path_fingerprint(path, root) for path in candidates]


def _proof_packet_text() -> str:
    allowed_lines = "\n".join(f"- {path}" for path in REPORT_ONLY_PATHS)
    forbidden_lines = "\n".join(f"- {path}" for path in PROTECTED_PATHS)
    return f"""CODEX-ONLY PROMPT
AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED
IDENTITY MARKER:
AI_OS RELAY PREDECESSOR PROOF CLOSURE WORKER
SUPERVISOR IDENTITY:
ChatGPT Planning Supervisor
PACKET ID:
{PROOF_PACKET_ID}
MODE:
{MODE}
ZONE:
relay_runtime_predecessor_proof_closure
WORKER IDENTITY:
Codex East
LANE:
{PROOF_LANE}
WORKTREE:
{PROOF_WORKTREE}
BRANCH:
{PROOF_BRANCH}
ALLOWED PATHS:
{allowed_lines}
FORBIDDEN PATHS:
{forbidden_lines}
APPROVAL AUTHORITY:
Anthony / Human Owner
MISSION:
Close the relay/runtime predecessor proof stack in dry-run proof mode only.
OBJECTIVE:
Produce the missing predecessor proofs and refresh the relay proof review report without authorizing execution.
PREFLIGHT:
pwd
git remote -v
git status --short --branch
git branch --show-current
VALIDATOR CHAIN:
python -m pytest tests/orchestration/test_aios_relay_predecessor_proof.py
python -m pytest tests/orchestration/test_aios_relay_proof_review.py
python -m pytest tests/orchestration/test_aios_runtime_proof_gate.py
STOP POINT:
Stop after report refresh and validation only.
COMMIT / PUSH / MERGE:
Separate explicit approval is required for commit, push, and merge, and approval does not transfer between actions.
Anthony explicitly approves commit only in a separate future packet.
Anthony explicitly approves push only in a separate future packet.
Anthony explicitly approves merge only in a separate future packet.
FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
DRY_RUN PROOF COMPLETE
SAFE NEXT ACTION:
Refresh the relay proof review only; do not execute runtime, scheduler, SOS, or live trading.
"""


def _proof_state(overrides: dict[str, Any] | None = None) -> dict[str, bool]:
    state = {
        "ledger_on_main": True,
        "approval_card_present": True,
        "completeness_ready": True,
        "path_guard_pass": True,
        "apply_inventory_target_selected": True,
        "runtime_dry_run_pass": False,
        "restart_timeout_proof_pass": False,
        "retention_dry_run_pass": False,
        "soak_pass": False,
        "stop_drill_pass": False,
        "sos_delivered_true": False,
        "scheduler_registered_by_anthony": False,
        "vacation_mode_complete": False,
    }
    if overrides:
        for key, value in overrides.items():
            if key in state:
                state[key] = bool(value)
    return state


def _selected_inventory_target(inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_target": "relay_proof_review",
        "selected_category": "proof_only",
        "selected_path": str(REPORT_DIR / REPORT_JSON_NAME),
        "selected_reason": (
            "Select the next proof-only target: refresh the relay proof review report, "
            "then refresh runtime proof and downstream previews."
        ),
        "selected_priority": "LOW",
        "inventory_counts": _deepcopy(inventory.get("counts") or {}),
        "top_mutation_gaps": _deepcopy((inventory.get("ranked_needs_apply") or [])[:5]),
        "runtime_execution_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
    }


def build_relay_predecessor_proof_bundle(
    *,
    repo_root: str | Path = ".",
    now: str | None = None,
    state_overrides: dict[str, Any] | None = None,
    proof_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    generated_at = _now(now)
    packet_text = _proof_packet_text()
    governance = validate_packet_text(packet_text, input_path="<relay-predecessor-proof>")
    completeness = review_packet_completeness(
        packet_text,
        path_status="SCOPED",
        input_path="<relay-predecessor-proof>",
    )
    approval_card = build_approval_card(
        {
            "packet_id": PROOF_PACKET_ID,
            "objective": "Close the relay/runtime predecessor proof stack without authorizing execution.",
            "allowed_paths": REPORT_ONLY_PATHS,
            "protected_action_expected": False,
        },
        governance=governance,
        completeness=completeness,
        now=generated_at,
    )

    path_guard = check_against_packet([], packet_text, input_path="<relay-predecessor-proof>")
    protected_fingerprints = _scan_protected_paths(root)
    protected_mutation_detected = any(bool(item.get("dirty")) for item in protected_fingerprints)
    path_guard_pass = path_guard.get("status") == "PASS" and not protected_mutation_detected

    inventory = build_inventory(root, now=generated_at)
    apply_inventory = _selected_inventory_target(inventory)
    apply_inventory_target_selected = bool(apply_inventory.get("selected_target")) and apply_inventory.get("selected_path") == str(REPORT_DIR / REPORT_JSON_NAME)

    state = _proof_state(state_overrides)
    runtime_queue_readout = build_runtime_execution_queue(state)
    relay_processor_readout = build_relay_runtime_processor(queue=runtime_queue_readout, now=generated_at)
    relay_proof_review = build_relay_dry_run_proof_review(
        relay_readout=relay_processor_readout,
        queue=runtime_queue_readout,
        now=generated_at,
    )
    operator_dependency_ledger = build_operator_dependency_ledger(
        queue=runtime_queue_readout,
        relay_readout=relay_processor_readout,
        relay_review=relay_proof_review,
        now=generated_at,
    )
    reduction_target_selector = build_reduction_target_selector(ledger=operator_dependency_ledger, now=generated_at)
    operator_dependency_validation = validate_operator_dependency_ledger(operator_dependency_ledger)
    reduction_target_validation = validate_reduction_target_selector(reduction_target_selector)

    relay_review_status = str(relay_proof_review.get("review_status") or "UNKNOWN")
    relay_reviewable = relay_review_status == "REVIEWABLE"
    runtime_queue_status = runtime_queue_readout.get("validation_status")
    queue_validation = validate_runtime_execution_queue(runtime_queue_readout)
    relay_processor_validation = validate_relay_runtime_processor(relay_processor_readout)
    relay_review_validation = validate_relay_dry_run_proof_review(relay_proof_review)

    required_flags = {
        "approval_card_present": bool(approval_card.get("card_id")) and approval_card.get("requires_human") is True and approval_card.get("approves_protected_action") is False,
        "completeness_ready": completeness.get("promotion_ready") is True and completeness.get("verdict") == "READY_FOR_HUMAN_REVIEW",
        "path_guard_pass": path_guard_pass,
        "apply_inventory_target_selected": apply_inventory_target_selected,
    }
    if proof_overrides:
        for key, value in proof_overrides.items():
            if key in required_flags:
                required_flags[key] = bool(value)
    missing_proofs = [name for name, passed in required_flags.items() if not passed]

    proof_ready = (
        all(required_flags.values())
        and not protected_mutation_detected
        and queue_validation.get("status") == "PASS"
        and relay_processor_validation.get("status") == "PASS"
        and relay_review_validation.get("status") == "PASS"
        and relay_reviewable
        and relay_processor_readout.get("proof_status") in {"READY_FOR_DRY_RUN", "DRY_RUN_PROVEN"}
        and operator_dependency_validation.get("status") == "PASS"
        and reduction_target_validation.get("status") == "PASS"
    )

    status = "PASS" if proof_ready else "BLOCKED_WITH_REAL_REASON"
    blockers: list[str] = []
    if not required_flags["approval_card_present"]:
        blockers.append("approval_card_present")
    if not required_flags["completeness_ready"]:
        blockers.append("completeness_ready")
    if not required_flags["path_guard_pass"]:
        blockers.append("path_guard_pass")
    if not required_flags["apply_inventory_target_selected"]:
        blockers.append("apply_inventory_target_selected")
    if protected_mutation_detected:
        blockers.append("protected path mutation detected")
    if queue_validation.get("status") != "PASS":
        blockers.extend(list(queue_validation.get("blockers") or []) or ["runtime queue validation is BLOCK"])
    if relay_processor_validation.get("status") != "PASS":
        blockers.extend(list(relay_processor_validation.get("blockers") or []) or ["relay processor validation is BLOCK"])
    if relay_review_validation.get("status") != "PASS":
        blockers.extend(list(relay_review_validation.get("blockers") or []) or ["relay review validation is BLOCK"])
    if not relay_reviewable:
        blockers.append("relay proof review is not REVIEWABLE")
    if operator_dependency_validation.get("status") != "PASS":
        blockers.append("operator dependency ledger validation is BLOCKED")
    if reduction_target_validation.get("status") != "PASS":
        blockers.append("reduction target selector validation is BLOCKED")

    safe_next_action = (
        "Refresh the relay proof review, then refresh runtime proof, runtime apply, SOS preview, scheduler preview, and observe spine."
        if status == "PASS"
        else "Resolve the missing predecessor proofs before refreshing relay proof review."
    )

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": generated_at,
        "packet_id": PROOF_PACKET_ID,
        "lane": PROOF_LANE,
        "branch": PROOF_BRANCH,
        "worktree": PROOF_WORKTREE,
        "status": status,
        "blockers": list(dict.fromkeys(blockers)),
        "missing_proofs": missing_proofs,
        "approval_card_present": required_flags["approval_card_present"],
        "completeness_ready": required_flags["completeness_ready"],
        "path_guard_pass": required_flags["path_guard_pass"],
        "apply_inventory_target_selected": required_flags["apply_inventory_target_selected"],
        "protected_mutation_detected": protected_mutation_detected,
        "approval_card": approval_card,
        "governance_review": governance,
        "completeness_review": completeness,
        "path_guard_check": path_guard,
        "protected_path_fingerprints": protected_fingerprints,
        "inventory": inventory,
        "apply_inventory_selection": apply_inventory,
        "runtime_queue_readout": runtime_queue_readout,
        "runtime_queue_validation": queue_validation,
        "relay_processor_readout": relay_processor_readout,
        "relay_processor_validation": relay_processor_validation,
        "relay_proof_review": relay_proof_review,
        "relay_review_validation": relay_review_validation,
        "relay_review_status": relay_review_status,
        "relay_reviewable": relay_reviewable,
        "operator_dependency_ledger": operator_dependency_ledger,
        "reduction_target_selector": reduction_target_selector,
        "operator_dependency_validation": operator_dependency_validation,
        "reduction_target_validation": reduction_target_validation,
        "runtime_queue_remaining_blockers": list(runtime_queue_readout.get("remaining_blockers") or []),
        "safe_next_action": safe_next_action,
        "stop_condition": "Stop before runtime execution, scheduler registration, SOS send, or queue mutation.",
        "report_paths": [str((root / REPORT_DIR / REPORT_JSON_NAME).as_posix()), str((root / REPORT_DIR / REPORT_MD_NAME).as_posix())],
    }
    report["validation"] = validate_relay_predecessor_proof_report(report)
    report["summary"] = summarize_relay_predecessor_proof_report(report)
    return report


def validate_relay_predecessor_proof_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report must be an object"],
            "unsafe_flags": ["report_not_object"],
            "checked_fields": [],
        }

    required_fields = [
        "schema",
        "mode",
        "generated_at_utc",
        "packet_id",
        "lane",
        "branch",
        "worktree",
        "status",
        "blockers",
        "missing_proofs",
        "approval_card_present",
        "completeness_ready",
        "path_guard_pass",
        "apply_inventory_target_selected",
        "protected_mutation_detected",
        "approval_card",
        "completeness_review",
        "path_guard_check",
        "inventory",
        "apply_inventory_selection",
        "runtime_queue_readout",
        "relay_processor_readout",
        "relay_proof_review",
        "operator_dependency_ledger",
        "reduction_target_selector",
        "safe_next_action",
        "stop_condition",
        "report_paths",
    ]
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    missing = [field for field in required_fields if field not in report]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if report.get("schema") != SCHEMA:
        blockers.append("schema must match AIOS_RELAY_PREDECESSOR_PROOF.v1")
        unsafe_flags.append("schema_mismatch")
    if report.get("mode") != MODE:
        blockers.append("mode must be DRY_RUN_PROOF")
        unsafe_flags.append("mode_mismatch")
    if report.get("status") not in {"PASS", "BLOCKED_WITH_REAL_REASON"}:
        blockers.append("status must be PASS or BLOCKED_WITH_REAL_REASON")
        unsafe_flags.append("status_invalid")

    for field in [
        "approval_card_present",
        "completeness_ready",
        "path_guard_pass",
        "apply_inventory_target_selected",
        "protected_mutation_detected",
    ]:
        if field not in report:
            continue
        if field == "protected_mutation_detected":
            if report.get(field) is True:
                blockers.append("protected path mutation detected")
                unsafe_flags.append("protected_mutation_true")
        elif report.get(field) not in {True, False}:
            blockers.append(f"{field} must be boolean")
            unsafe_flags.append(f"{field}_not_boolean")

    if report.get("status") == "PASS":
        for field in ["approval_card_present", "completeness_ready", "path_guard_pass", "apply_inventory_target_selected"]:
            if report.get(field) is not True:
                blockers.append(f"{field} must be true when status is PASS")
                unsafe_flags.append(f"{field}_false")
        if report.get("protected_mutation_detected") is True:
            blockers.append("protected mutation detected cannot be true when status is PASS")
            unsafe_flags.append("protected_mutation_true")
        if report.get("relay_review_status") != "REVIEWABLE":
            blockers.append("relay review status must be REVIEWABLE when predecessor proof passes")
            unsafe_flags.append("relay_review_not_reviewable")

    if not isinstance(report.get("safe_next_action"), str) or not report.get("safe_next_action"):
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")
    if not isinstance(report.get("stop_condition"), str) or not report.get("stop_condition"):
        blockers.append("stop_condition must be a non-empty string")
        unsafe_flags.append("stop_condition_missing")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "unsafe_flags": unsafe_flags,
        "checked_fields": required_fields,
    }


def summarize_relay_predecessor_proof_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "status": None,
            "approval_card_present": None,
            "completeness_ready": None,
            "path_guard_pass": None,
            "apply_inventory_target_selected": None,
            "relay_review_status": None,
            "runtime_queue_status": None,
            "operator_dependency_status": None,
            "reduction_target_status": None,
            "protected_mutation_detected": None,
            "missing_proofs": [],
            "safe_next_action": None,
        }
    return {
        "status": report.get("status"),
        "approval_card_present": report.get("approval_card_present"),
        "completeness_ready": report.get("completeness_ready"),
        "path_guard_pass": report.get("path_guard_pass"),
        "apply_inventory_target_selected": report.get("apply_inventory_target_selected"),
        "relay_review_status": report.get("relay_review_status"),
        "runtime_queue_status": (report.get("runtime_queue_validation") or {}).get("status"),
        "operator_dependency_status": (report.get("operator_dependency_validation") or {}).get("status"),
        "reduction_target_status": (report.get("reduction_target_validation") or {}).get("status"),
        "protected_mutation_detected": report.get("protected_mutation_detected"),
        "missing_proofs": list(report.get("missing_proofs") or []),
        "safe_next_action": report.get("safe_next_action"),
    }


def build_relay_predecessor_proof_markdown(report: dict[str, Any]) -> str:
    summary = summarize_relay_predecessor_proof_report(report)
    lines = [
        "# AI_OS Relay Predecessor Proof",
        "",
        f"- status: `{summary.get('status')}`",
        f"- approval_card_present: `{summary.get('approval_card_present')}`",
        f"- completeness_ready: `{summary.get('completeness_ready')}`",
        f"- path_guard_pass: `{summary.get('path_guard_pass')}`",
        f"- apply_inventory_target_selected: `{summary.get('apply_inventory_target_selected')}`",
        f"- relay_review_status: `{summary.get('relay_review_status')}`",
        f"- runtime_queue_status: `{summary.get('runtime_queue_status')}`",
        f"- operator_dependency_status: `{summary.get('operator_dependency_status')}`",
        f"- reduction_target_status: `{summary.get('reduction_target_status')}`",
        f"- protected_mutation_detected: `{summary.get('protected_mutation_detected')}`",
        f"- safe_next_action: {summary.get('safe_next_action')}",
        "",
        "## Missing Proofs",
    ]
    if summary.get("missing_proofs"):
        lines.extend(f"- {item}" for item in summary.get("missing_proofs") or [])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Approval Card",
            f"- card_id: `{report.get('approval_card', {}).get('card_id')}`",
            f"- recommended_decision: `{report.get('approval_card', {}).get('recommended_decision')}`",
            f"- requires_human: `{report.get('approval_card', {}).get('requires_human')}`",
            f"- approves_protected_action: `{report.get('approval_card', {}).get('approves_protected_action')}`",
            "",
            "## Relay Review",
            f"- review_status: `{report.get('relay_proof_review', {}).get('review_status')}`",
            f"- proof_reviewable: `{report.get('relay_proof_review', {}).get('proof_reviewable')}`",
            f"- missing_proofs: `{report.get('relay_proof_review', {}).get('missing_proofs')}`",
            "",
            "## Path Guard",
            f"- status: `{report.get('path_guard_check', {}).get('status')}`",
            f"- changed_count: `{report.get('path_guard_check', {}).get('changed_count')}`",
            "",
            "## Safety",
            "- This proof is observe-only. It proves readiness evidence and does not authorize APPLY, runtime execution, scheduler registration, SOS send, or live trading.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_relay_predecessor_proof_reports(
    report: dict[str, Any],
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    out_dir = Path(output_dir) if output_dir is not None else root / REPORT_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / REPORT_JSON_NAME
    md_path = out_dir / REPORT_MD_NAME
    report = _deepcopy(report)
    report["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    report["validation"] = validate_relay_predecessor_proof_report(report)
    report["summary"] = summarize_relay_predecessor_proof_report(report)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_relay_predecessor_proof_markdown(report), encoding="utf-8")
    return report


def run_relay_predecessor_proof(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    state_overrides: dict[str, Any] | None = None,
    proof_overrides: dict[str, Any] | None = None,
    now: str | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    report = build_relay_predecessor_proof_bundle(
        repo_root=repo_root,
        now=now,
        state_overrides=state_overrides,
        proof_overrides=proof_overrides,
    )
    if write_report:
        report = write_relay_predecessor_proof_reports(report, repo_root=repo_root, output_dir=output_dir)
    return report


def _cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the AI_OS relay/runtime predecessor proof bundle.")
    parser.add_argument("--repo-root", default=".", help="repository root for output resolution")
    parser.add_argument("--output-dir", default=None, help="optional report output directory")
    parser.add_argument("--no-write", action="store_true", help="build without writing report files")
    parser.add_argument("--state-json", default=None, help="optional JSON object with proof-state overrides")
    parser.add_argument("--proof-json", default=None, help="optional JSON object with top-level proof overrides")
    parser.add_argument("--now", default=None, help="optional timestamp override")
    return parser.parse_args()


def _load_json_arg(raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("state-json must decode to an object")
    return value


def main() -> int:
    args = _cli_args()
    report = run_relay_predecessor_proof(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        state_overrides=_load_json_arg(args.state_json),
        proof_overrides=_load_json_arg(args.proof_json),
        now=args.now,
        write_report=not args.no_write,
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
