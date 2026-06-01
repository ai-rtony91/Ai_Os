#!/usr/bin/env python3
"""AI_OS Night Supervisor harness (DRY_RUN).

Executable, stdlib-only implementation of the nightly supervision chain:

    bootstrap -> checkpoint -> validator -> lock check -> approval plan ->
    runtime snapshot -> resume record -> cleanup & ledger -> summary report
    -> safety enforcement

Authority: subordinate to RISK_POLICY.md and AGENTS.md. This harness is
DRY_RUN only. It never commits, pushes, merges, mutates active runtime /
packet / approval / lock state, touches trading or broker logic, or reads
or emits secrets. Every write is hard-confined to telemetry/night_supervisor/
by ``_assert_sandbox`` and a forbidden-write counter that fails the run closed.

It mirrors the logic previewed by Invoke-AiOsNightSupervisor.DRY_RUN.ps1 so
the chain can be verified in environments without PowerShell.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = "AIOS_NIGHT_SUPERVISOR_REPORT.v1"
APPROVAL_AUTHORITY = "Anthony Meza"
RUNTIME_WRITE_ROOT = "telemetry/night_supervisor"
ALLOWED_WRITE_ROOTS = (
    "telemetry/night_supervisor",
    "automation/orchestration/night_supervisor",
)
BLOCKED_CAPABILITIES = [
    "APPLY",
    "commit",
    "push",
    "merge",
    "active runtime state mutation",
    "active packet/approval/lock state change",
    "worker launch",
    "scheduled/background execution",
    "live trading",
    "broker execution",
    "secret handling",
]
RESULT_CLASSIFICATIONS = {"PASS", "FAIL", "BLOCKED", "NEEDS_APPROVAL", "NOOP"}

# Conservative secret-shaped patterns. Night supervision only ever serializes
# repo metadata (file names, counts, git porcelain), so a hit here means an
# upstream source leaked something and the run must fail closed.
_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|passwd|private[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9/+_-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"),
]


class ForbiddenWriteError(RuntimeError):
    """Raised when a write is attempted outside the sandbox roots."""


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_key() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


def resolve_repo_root(requested: str | None = None) -> Path:
    if requested:
        return Path(requested).resolve(strict=True)
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0 or not out.stdout.strip():
        raise RuntimeError(
            "Unable to resolve repo root via git rev-parse. Pass --repo-root."
        )
    return Path(out.stdout.strip()).resolve()


def _rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True, text=True, check=False,
    )


class SandboxWriter:
    """Records and enforces that every write stays under the sandbox root."""

    def __init__(self, repo_root: Path, emit: bool):
        self.repo_root = repo_root
        self.emit = emit
        self.written: list[str] = []
        self.forbidden_attempts = 0

    def _assert_sandbox(self, target: Path) -> Path:
        resolved = target.resolve()
        sandbox = (self.repo_root / RUNTIME_WRITE_ROOT).resolve()
        if not (resolved == sandbox or sandbox in resolved.parents):
            self.forbidden_attempts += 1
            raise ForbiddenWriteError(
                f"Refused write outside sandbox: {self._rel(resolved)}"
            )
        return resolved

    def _rel(self, path: Path) -> str:
        return _rel(self.repo_root, path)

    def write_json(self, rel_path: str, payload: dict) -> str:
        target = self._assert_sandbox(self.repo_root / RUNTIME_WRITE_ROOT / rel_path)
        rel = self._rel(target)
        _scan_for_secrets(json.dumps(payload), source=rel)
        if self.emit:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self.written.append(rel)
        return rel

    def append_jsonl(self, rel_path: str, record: dict) -> str:
        target = self._assert_sandbox(self.repo_root / RUNTIME_WRITE_ROOT / rel_path)
        rel = self._rel(target)
        _scan_for_secrets(json.dumps(record), source=rel)
        if self.emit:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
        self.written.append(rel)
        return rel


def _scan_for_secrets(text: str, source: str) -> None:
    for pat in _SECRET_PATTERNS:
        if pat.search(text):
            raise RuntimeError(
                f"FAIL-CLOSED: secret-shaped content detected in {source}; "
                "aborting before any sandbox write."
            )


def _count_files(path: Path, suffix: str = ".json") -> int:
    if not path.is_dir():
        return 0
    return sum(1 for p in path.rglob(f"*{suffix}") if p.is_file())


def _safe_load_json(path: Path):
    try:
        # utf-8-sig tolerates the UTF-8 BOM that Windows/PowerShell-authored
        # AI_OS JSON commonly carries; PowerShell ConvertFrom-Json parses it.
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _latest_packet(repo_root: Path) -> dict:
    work_packets = repo_root / "automation" / "orchestration" / "work_packets"
    active_dir = work_packets / "active"
    packet_files = sorted(active_dir.glob("*.json")) if active_dir.is_dir() else []
    if not packet_files and work_packets.is_dir():
        packet_files = sorted(work_packets.rglob("*.json"))
    if not packet_files:
        return {"selected": False, "path": "", "data": {}}

    packet_path = packet_files[0]
    return {
        "selected": True,
        "path": _rel(repo_root, packet_path),
        "data": _safe_load_json(packet_path) or {},
    }


def _packet_value(packet: dict, names: tuple[str, ...], default: str) -> str:
    for name in names:
        value = packet.get(name)
        if value not in (None, ""):
            return str(value)
    return default


def _phase_status(phases: list[dict], phase_name: str) -> str:
    for phase in phases:
        if phase.get("phase") == phase_name:
            return str(phase.get("status", "NOT_RUN"))
    return "NOT_RUN"


def _build_execution_result(
    repo_root: Path,
    run_id: str,
    phases: list[dict],
    alerts: list[dict],
    changed_files: list[str],
    untracked_items: list[str],
    forbidden_write_attempts: int,
) -> dict:
    packet_entry = _latest_packet(repo_root)
    packet = packet_entry["data"]
    packet_selected = bool(packet_entry["selected"])
    validator_status = _phase_status(phases, "validator_automation")
    approval_status = _phase_status(phases, "approval_automation")
    approval_required = approval_status in {"PLANNED", "WARN", "FAIL", "BLOCKED"}
    qa_status = "PASS"
    qa_notes = []

    if forbidden_write_attempts:
        qa_status = "BLOCKED"
        qa_notes.append("Forbidden write attempt detected.")
    if any(alert.get("severity") == "CRITICAL" for alert in alerts):
        qa_status = "FAIL"
        qa_notes.append("Critical alert present.")
    if validator_status == "FAIL":
        qa_status = "FAIL"
        qa_notes.append("Validator automation failed.")
    if not packet_selected:
        qa_notes.append("No active packet selected; run is a supervisor health pass only.")

    if forbidden_write_attempts:
        classification = "BLOCKED"
    elif validator_status == "FAIL" or qa_status == "FAIL":
        classification = "FAIL"
    elif approval_required:
        classification = "NEEDS_APPROVAL"
    elif not packet_selected and not changed_files and not untracked_items:
        classification = "NOOP"
    else:
        classification = "PASS"

    if classification not in RESULT_CLASSIFICATIONS:
        classification = "BLOCKED"
        qa_status = "BLOCKED"
        qa_notes.append("Unknown classification collapsed to BLOCKED.")

    next_safe_action = {
        "PASS": "Review report evidence; continue only through the next approved packet.",
        "FAIL": "Review validator or QA failure before any APPLY, commit, push, merge, or worker launch.",
        "BLOCKED": "Stop and resolve blocked condition before continuing.",
        "NEEDS_APPROVAL": "Anthony Meza reviews approval-required items before mutation or protected action.",
        "NOOP": "No packet was selected and no repo changes were detected; select or create the next approved packet.",
    }[classification]

    return {
        "packet_id": _packet_value(packet, ("packet_id", "id", "task_id"), "NO_PACKET_SELECTED"),
        "packet_name": _packet_value(packet, ("packet_name", "name", "title"), "No packet selected"),
        "run_id": run_id,
        "worker_id": _packet_value(packet, ("assigned_worker", "worker_id", "worker_identity"), "UNASSIGNED"),
        "worker_lane": _packet_value(packet, ("owner_lane", "worker_lane", "lane"), "UNKNOWN"),
        "packet_selected": packet_selected,
        "packet_path": packet_entry["path"],
        "packet_status": _packet_value(packet, ("status", "packet_status", "state"), "NOT_SELECTED"),
        "validator_status": validator_status,
        "qa_status": qa_status,
        "approval_required": approval_required,
        "result_classification": classification,
        "files_changed": changed_files,
        "files_untracked": untracked_items,
        "next_safe_action": next_safe_action,
        "notes": qa_notes,
    }


# --------------------------------------------------------------------------
# Phases
# --------------------------------------------------------------------------

def phase_bootstrap(repo_root: Path) -> dict:
    branch = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "UNKNOWN"
    head = _git(repo_root, "rev-parse", "--short", "HEAD").stdout.strip() or "UNKNOWN"
    # Recover prior validated runtime state from sandbox snapshots (read-only).
    snap_root = repo_root / RUNTIME_WRITE_ROOT
    prior = sorted(snap_root.glob("*/runtime_snapshot.json")) if snap_root.is_dir() else []
    recovered = _rel(repo_root, prior[-1]) if prior else None
    detail = {
        "branch": branch,
        "head_sha": head,
        "recovered_from_snapshot": recovered,
        "snapshot_history_count": len(prior),
    }
    return {
        "phase": "supervisor_bootstrap",
        "step": 1,
        "status": "PASS",
        "summary": (
            f"Bootstrap resolved branch={branch} head={head}; "
            + (f"recovered prior snapshot {recovered}." if recovered
               else "no prior validated snapshot found (first run).")
        ),
        "mutations": [],
        "detail": detail,
        "next_safe_action": "Proceed to checkpoint capture (read-only).",
    }


def phase_checkpoint(repo_root: Path, writer: SandboxWriter, date_key: str) -> dict:
    status = _git(repo_root, "status", "--porcelain").stdout.splitlines()
    changed = [l[3:] for l in status if l[:2].strip() and not l.startswith("??")]
    untracked = [l[3:] for l in status if l.startswith("??")]
    orch = repo_root / "automation" / "orchestration"
    snapshot = {
        "schema": "AIOS_NIGHT_RUNTIME_SNAPSHOT.v1",
        "captured_at": _utc_now(),
        "mode": "DRY_RUN",
        "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(),
        "head_sha": _git(repo_root, "rev-parse", "HEAD").stdout.strip(),
        "changed_file_count": len(changed),
        "untracked_count": len(untracked),
        "counts": {
            "work_packets_json": _count_files(orch / "work_packets"),
            "approval_inbox_json": _count_files(orch / "approval_inbox"),
            "lock_json": _count_files(orch / "locks"),
        },
    }
    written = [
        writer.write_json(f"{date_key}/runtime_snapshot.json", snapshot),
        writer.write_json(f"{date_key}/checkpoint.json", {
            "schema": "AIOS_NIGHT_CHECKPOINT.v1",
            "checkpoint_at": _utc_now(),
            "mode": "DRY_RUN",
            "snapshot_ref": f"{date_key}/runtime_snapshot.json",
        }),
    ]
    return {
        "phase": "nightly_telemetry_checkpoint",
        "step": 2,
        "status": "PASS",
        "summary": f"Captured runtime snapshot + checkpoint for {date_key} (sandbox).",
        "mutations": written,
        "detail": {"changed_files": changed, "untracked_items": untracked},
        "next_safe_action": "Run nightly validation against the snapshot.",
    }


def phase_validator(repo_root: Path) -> dict:
    failures: list[str] = []
    # JSON parse over a bounded set of orchestration state files.
    orch = repo_root / "automation" / "orchestration"
    checked = 0
    for jpath in sorted(orch.rglob("*.json")):
        if checked >= 400:
            break
        checked += 1
        try:
            # utf-8-sig: BOM-tolerant, matching PowerShell ConvertFrom-Json.
            json.loads(jpath.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"json_parse:{_rel(repo_root, jpath)}: {type(exc).__name__}")
    # git diff --check (whitespace/conflict markers) — read-only.
    diff_check = _git(repo_root, "diff", "--check")
    diff_ok = diff_check.returncode == 0
    if not diff_ok:
        failures.append("git_diff_check: whitespace/conflict markers present")
    # repo integrity — read-only.
    integrity_ok = _git(repo_root, "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"
    if not integrity_ok:
        failures.append("repo_integrity: not inside a git work tree")

    status = "PASS" if not failures else "FAIL"
    return {
        "phase": "validator_automation",
        "step": 3,
        "status": status,
        "summary": (
            f"JSON parse checked {checked} files; git diff --check {'ok' if diff_ok else 'FAILED'}; "
            f"repo integrity {'ok' if integrity_ok else 'FAILED'}; "
            "PowerShell parse DEFERRED (no pwsh in this environment)."
        ),
        "mutations": [],
        "detail": {
            "json_files_checked": checked,
            "powershell_parse": "DEFERRED_NO_PWSH",
            "failures": failures,
        },
        "next_safe_action": (
            "STOP: create alert and hold for human review." if failures
            else "Proceed to lock enforcement check."
        ),
    }


def phase_locks(repo_root: Path) -> dict:
    locks_dir = repo_root / "automation" / "orchestration" / "locks"
    expired_plan = []
    active = 0
    now = _dt.datetime.now(_dt.timezone.utc)
    for lpath in sorted(locks_dir.glob("*.lock.json")) if locks_dir.is_dir() else []:
        data = _safe_load_json(lpath) or {}
        active += 1
        expiry = data.get("expires_at") or data.get("expiry") or data.get("ttl_expires_at")
        if expiry:
            try:
                exp = _dt.datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
                if exp < now:
                    expired_plan.append(_rel(repo_root, lpath))
            except ValueError:
                pass
    return {
        "phase": "lock_enforcement_automation",
        "step": 4,
        "status": "PLANNED",
        "summary": (
            f"Inspected {active} lock file(s); {len(expired_plan)} appear expired. "
            "Release is DRY_RUN PLAN ONLY — locks live outside allowed write paths, "
            "so no lock is released without a separate approved APPLY packet."
        ),
        "mutations": [],
        "detail": {"active_locks": active, "expired_release_plan": expired_plan},
        "next_safe_action": (
            "Review expired-lock release plan before any APPLY." if expired_plan
            else "No orphaned locks detected; continue."
        ),
    }


def phase_approval(repo_root: Path) -> dict:
    orch = repo_root / "automation" / "orchestration"
    tier_policy = _safe_load_json(orch / "policy" / "AIOS_APPROVAL_TIER_POLICY.json")
    inbox_dir = orch / "approval_inbox"
    low, pending = [], []
    if inbox_dir.is_dir():
        for ipath in sorted(inbox_dir.glob("*.json")):
            data = _safe_load_json(ipath) or {}
            tier = str(data.get("risk_tier") or data.get("risk_level") or "UNKNOWN").upper()
            entry = {"file": _rel(repo_root, ipath), "tier": tier}
            if tier == "LOW":
                low.append(entry)
            else:
                pending.append(entry)
    return {
        "phase": "approval_automation",
        "step": 5,
        "status": "PLANNED",
        "summary": (
            f"Classified approval inbox: {len(low)} LOW-tier eligible (auto-approval "
            f"DISABLED in DRY_RUN), {len(pending)} MEDIUM/HIGH/UNKNOWN held for human review."
        ),
        "mutations": [],
        "detail": {
            "tier_policy_present": tier_policy is not None,
            "low_tier_candidates": low,
            "pending_human_review": pending,
            "auto_approval_enabled": False,
        },
        "next_safe_action": (
            f"{APPROVAL_AUTHORITY} reviews MEDIUM/HIGH items; LOW auto-approval needs a separate APPLY packet."
        ),
    }


def phase_runtime_state(repo_root: Path, writer: SandboxWriter, date_key: str) -> dict:
    # Produce a PROPOSED runtime-state update in the sandbox. The real runtime
    # memory file is never mutated.
    real_memory = repo_root / "automation" / "orchestration" / "memory" / "AIOS_RUNTIME_MEMORY.json"
    proposed = {
        "schema": "AIOS_NIGHT_RUNTIME_STATE_PROPOSAL.v1",
        "proposed_at": _utc_now(),
        "mode": "DRY_RUN",
        "source_runtime_memory_present": real_memory.is_file(),
        "proposed_updates": {
            "last_night_supervision_run": date_key,
            "last_night_supervision_status": "completed_dry_run",
        },
        "apply_note": (
            "PROPOSAL ONLY. Applying these updates to active runtime state requires "
            "a separate approved APPLY packet with validation. No active state mutated."
        ),
    }
    written = writer.write_json(f"{date_key}/runtime_state_proposal.json", proposed)
    return {
        "phase": "runtime_state_automation",
        "step": 6,
        "status": "PLANNED",
        "summary": "Wrote PROPOSED runtime-state update to sandbox; active runtime state untouched.",
        "mutations": [written],
        "detail": proposed["proposed_updates"],
        "next_safe_action": "Review proposal; active runtime mutation needs separate validated APPLY.",
    }


def phase_resume(repo_root: Path, writer: SandboxWriter, date_key: str) -> dict:
    branch = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    head = _git(repo_root, "rev-parse", "HEAD").stdout.strip()
    resume = {
        "schema": "AIOS_NIGHT_RESUME_RECORD.v1",
        "created_at": _utc_now(),
        "mode": "DRY_RUN",
        "date_key": date_key,
        "branch": branch,
        "head_sha": head,
        "snapshot_ref": f"{date_key}/runtime_snapshot.json",
        "checkpoint_ref": f"{date_key}/checkpoint.json",
        "resume_note": (
            "Morning startup can read this record to confirm the last validated night "
            "state. Canonical promotion to automation/runtime/state/resume/ is deferred "
            "to a separate approved packet (outside night-supervisor allowed write paths)."
        ),
    }
    written = writer.write_json(f"resume/resume_{date_key}.json", resume)
    return {
        "phase": "resume_capability_automation",
        "step": 7,
        "status": "PASS",
        "summary": "Resume record written to sandbox (telemetry/night_supervisor/resume/).",
        "mutations": [written],
        "detail": {"resume_ref": written},
        "next_safe_action": "Use resume record at morning startup; promotion to canonical path needs approval.",
    }


def phase_cleanup_ledger(repo_root: Path, writer: SandboxWriter, date_key: str,
                         run_id: str) -> dict:
    # Identify candidate temp files (DRY_RUN plan only — nothing deleted).
    sandbox = repo_root / RUNTIME_WRITE_ROOT
    temp_candidates = []
    if sandbox.is_dir():
        for p in sandbox.rglob("*.tmp"):
            temp_candidates.append(_rel(repo_root, p))
    ledger_record = {
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
        "event_type": "night_supervision_run",
        "mode": "DRY_RUN",
        "actor": "night_supervisor_harness",
        "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(),
        "date_key": date_key,
        "result": "DRY_RUN_COMPLETE",
        "temp_cleanup_plan_count": len(temp_candidates),
        "authority_note": "Telemetry is evidence, not approval authority.",
    }
    written = writer.append_jsonl("night_ledger.jsonl", ledger_record)
    return {
        "phase": "cleanup_and_ledger",
        "step": 8,
        "status": "PASS",
        "summary": (
            f"Appended nightly ledger event; identified {len(temp_candidates)} temp "
            "cleanup candidate(s) (DRY_RUN plan, none deleted)."
        ),
        "mutations": [written],
        "detail": {"temp_cleanup_plan": temp_candidates},
        "next_safe_action": "Ledger is append-only evidence; no deletion without approval.",
    }


def _derive_alerts(phases: list[dict]) -> list[dict]:
    alerts = []
    for ph in phases:
        if ph["status"] == "FAIL":
            alerts.append({
                "severity": "CRITICAL",
                "trigger": f"{ph['phase']}_failed",
                "evidence": ph["summary"],
                "next_safe_action": "Hold for morning human review; do not proceed to APPLY.",
            })
        elif ph["status"] == "BLOCKED":
            alerts.append({
                "severity": "WARNING",
                "trigger": f"{ph['phase']}_blocked",
                "evidence": ph["summary"],
                "next_safe_action": "Review blocker before any protected action.",
            })
    return alerts


def run_night_supervision(repo_root: Path | None = None, emit: bool = True) -> dict:
    repo_root = resolve_repo_root(str(repo_root) if repo_root else None)
    date_key = _date_key()
    run_id = f"night_{_dt.datetime.now(_dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    writer = SandboxWriter(repo_root, emit=emit)

    phases = [phase_bootstrap(repo_root)]
    phases.append(phase_checkpoint(repo_root, writer, date_key))
    validator = phase_validator(repo_root)
    phases.append(validator)
    phases.append(phase_locks(repo_root))
    phases.append(phase_approval(repo_root))
    phases.append(phase_runtime_state(repo_root, writer, date_key))
    phases.append(phase_resume(repo_root, writer, date_key))
    phases.append(phase_cleanup_ledger(repo_root, writer, date_key, run_id))

    alerts = _derive_alerts(phases)
    has_critical = any(a["severity"] == "CRITICAL" for a in alerts)
    supervisor_status = "BLOCKED" if has_critical else ("REVIEW" if alerts else "READY")

    status_lines = _git(repo_root, "status", "--porcelain").stdout.splitlines()
    changed = [l[3:] for l in status_lines if l[:2].strip() and not l.startswith("??")]
    untracked = [l[3:] for l in status_lines if l.startswith("??")]
    ahead = _git(repo_root, "rev-list", "--count", "@{u}..HEAD").stdout.strip()
    try:
        ahead_n = int(ahead)
    except ValueError:
        ahead_n = 0
    execution_result = _build_execution_result(
        repo_root=repo_root,
        run_id=run_id,
        phases=phases,
        alerts=alerts,
        changed_files=changed,
        untracked_items=untracked,
        forbidden_write_attempts=writer.forbidden_attempts,
    )

    report = {
        "schema": SCHEMA,
        "mode": "DRY_RUN",
        "supervisor_status": supervisor_status,
        "run_id": run_id,
        "generated_at": _utc_now(),
        "repo": {
            "repo_root": str(repo_root),
            "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(),
            "head_sha": _git(repo_root, "rev-parse", "HEAD").stdout.strip(),
            "ahead_commits": ahead_n,
            "changed_files": changed,
            "untracked_items": untracked,
        },
        "execution_result": execution_result,
        "phases": phases,
        "alerts": alerts,
        "safety_confirmation": {
            "no_live_trading": True,
            "no_broker_execution": True,
            "no_secrets_exposed": True,
            "no_active_state_mutation": True,
            "no_commit_or_push": True,
            "writes_within_allowed_paths_only": writer.forbidden_attempts == 0,
            "forbidden_write_attempts": writer.forbidden_attempts,
        },
        "next_safe_action": (
            "CRITICAL alert present: hold for human review before any further action."
            if has_critical else
            "Review nightly report; promote sandbox outputs only via a separate approved packet."
        ),
        "authority_boundary": {
            "read_only_outside_sandbox": True,
            "approval_authority": APPROVAL_AUTHORITY,
            "blocked_capabilities": BLOCKED_CAPABILITIES,
        },
    }

    # Phase 9 (reporting) + phase 10 (safety) write last so the report is self-contained.
    report_rel = writer.write_json(f"reports/night_summary_{date_key}.json", report)
    if alerts:
        writer.write_json(f"alerts/night_alert_{date_key}.json", {
            "schema": "AIOS_NIGHT_ALERT.v1",
            "generated_at": _utc_now(),
            "supervisor_status": supervisor_status,
            "alerts": alerts,
        })
    report["_written_report_path"] = report_rel
    report["_sandbox_writes"] = writer.written
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI_OS Night Supervisor harness (DRY_RUN).")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--no-emit", action="store_true",
                        help="Compute the chain without writing sandbox files.")
    parser.add_argument("--quiet", action="store_true", help="Emit JSON only.")
    args = parser.parse_args(argv)

    report = run_night_supervision(
        repo_root=Path(args.repo_root) if args.repo_root else None,
        emit=not args.no_emit,
    )

    if args.quiet:
        print(json.dumps(report, indent=2))
    else:
        print("AI_OS Night Supervisor (DRY_RUN)")
        print(f"Run: {report['run_id']}  Status: {report['supervisor_status']}")
        print(f"Execution result: {report['execution_result']['result_classification']}")
        print(f"Branch: {report['repo']['branch']}  Head: {report['repo']['head_sha'][:10]}  Ahead: {report['repo']['ahead_commits']}")
        for ph in report["phases"]:
            print(f"  [{ph['step']:>2}] {ph['status']:<8} {ph['phase']}")
        print(f"Alerts: {len(report['alerts'])}")
        sc = report["safety_confirmation"]
        print(f"Safety: forbidden_writes={sc['forbidden_write_attempts']} "
              f"sandbox_only={sc['writes_within_allowed_paths_only']}")
        print(f"Sandbox writes: {len(report.get('_sandbox_writes', []))}")
        print(f"Report: {report.get('_written_report_path')}")
        print(f"Next: {report['next_safe_action']}")

    # Fail closed: non-zero exit when blocked so schedulers stop the chain.
    return 2 if report["supervisor_status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
