"""AI_OS Night Supervisor effector dispatcher (the gated 'hands').

Schema/contract reference: schemas/aios/orchestration/supervisor_action_intent.schema.json
Mode: DRY_RUN by default. APPLY only when every gate is satisfied at once.
next_safe_action: Review dispatch decisions. Nothing executes unless ALL gates
pass AND the operator explicitly enables apply at run time.
commit_performed: NO / push_performed: NO

This sits strictly DOWNSTREAM of the Codex V2 spine. It does NOT re-read the
approval inbox or re-scan locks (approval_officer / lock_manager own that). It
trusts the intent's ``source_contract`` verdict and adds only the execution
gates the spine does not have:
  1. kill_switch_clear   (AIOS_NIGHT_SUPERVISOR_DISABLE unset)    -> honored first
  2. effector_actionable (effector != noop)
  3. capability_allowed  (effector on explicit allowlist)         -> default empty
  4. execution_enabled   (operator passed --apply)                -> default OFF
  5. env_apply_armed     (AIOS_SUPERVISOR_APPLY=1)                 -> default unset
  6. contract_cleared    (spine said DRY_RUN_PREVIEW + APPROVED/NOT_REQUIRED + FREE)
Any single failure downgrades the decision to BLOCKED_DRY_RUN.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


KILL_SWITCH_ENV = "AIOS_NIGHT_SUPERVISOR_DISABLE"
APPLY_ENV = "AIOS_SUPERVISOR_APPLY"

_SAFE_APPROVAL = {"APPROVED", "NOT_REQUIRED"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _kill_switch_engaged() -> bool:
    return bool(os.environ.get(KILL_SWITCH_ENV, "").strip())


def _env_apply_armed() -> bool:
    return os.environ.get(APPLY_ENV, "").strip() == "1"


def _contract_cleared(intent: dict[str, Any]) -> bool:
    """Trust the Codex spine verdict carried on the intent. Fail-closed."""

    contract = intent.get("source_contract") or {}
    return (
        str(contract.get("dispatch_status") or "").upper() == "DRY_RUN_PREVIEW"
        and str(contract.get("approval_status") or "").upper() in _SAFE_APPROVAL
        and str(contract.get("lock_status") or "").upper() == "FREE"
    )


def decide(
    intent: dict[str, Any],
    *,
    enabled_capabilities: list[str],
    execution_enabled: bool,
) -> dict[str, Any]:
    """Produce a fail-closed dispatch decision for one intent. Never executes."""

    effector = str(intent.get("effector") or "noop")
    gates: dict[str, Any] = {
        "kill_switch_clear": not _kill_switch_engaged(),
        "effector_actionable": effector != "noop",
        "capability_allowed": effector in (enabled_capabilities or []),
        "execution_enabled": bool(execution_enabled),
        "env_apply_armed": _env_apply_armed(),
        "contract_cleared": _contract_cleared(intent),
    }
    all_clear = all(gates.values())
    return {
        "intent_id": intent.get("intent_id"),
        "packet_id": intent.get("packet_id"),
        "effector": effector,
        "effector_script": intent.get("effector_script"),
        "args": intent.get("args", {}),
        "decision": "WOULD_EXECUTE" if all_clear else "BLOCKED_DRY_RUN",
        "gates": gates,
        "blocking_gates": [name for name, ok in gates.items() if not ok],
        "source_contract": intent.get("source_contract"),
        "evaluated_at": _utc_now(),
    }


def _execute(decision: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Invoke the PowerShell hand-script for a fully-cleared decision.

    Refuses (EXECUTION_UNAVAILABLE) if no PowerShell runtime exists, so a missing
    runtime can never be misreported as a successful no-op.
    """

    script = str(decision.get("effector_script") or "")
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if not script or not shell:
        return {**decision, "decision": "EXECUTION_UNAVAILABLE", "receipt": {
            "executed": False,
            "reason": "No PowerShell runtime or no effector script. Execution refused.",
        }}

    cmd = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(repo_root / script)]
    for key, value in (decision.get("args") or {}).items():
        cmd.extend([f"-{key}", str(value)])
    completed = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)  # noqa: S603
    return {**decision, "receipt": {
        "executed": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-2000:],
        "stderr_tail": (completed.stderr or "")[-2000:],
        "executed_at": _utc_now(),
    }}


def dispatch(
    intents: list[dict[str, Any]],
    *,
    repo_root: str | Path = ".",
    enabled_capabilities: list[str] | None = None,
    execution_enabled: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    """Evaluate (and optionally execute) a batch of intents. Default: dry."""

    root = Path(repo_root).resolve()
    decisions = [
        decide(intent, enabled_capabilities=enabled_capabilities or [], execution_enabled=execution_enabled)
        for intent in intents
    ]

    receipts: list[dict[str, Any]] = []
    if apply and execution_enabled and not _kill_switch_engaged():
        for decision in decisions:
            if decision["decision"] == "WOULD_EXECUTE":
                receipts.append(_execute(decision, root))

    would_execute = [d for d in decisions if d["decision"] == "WOULD_EXECUTE"]
    return {
        "schema": "AIOS_SUPERVISOR_DISPATCH.v1",
        "mode": "APPLY" if (apply and execution_enabled) else "DRY_RUN",
        "kill_switch_engaged": _kill_switch_engaged(),
        "enabled_capabilities": enabled_capabilities or [],
        "decisions": decisions,
        "would_execute_count": len(would_execute),
        "blocked_count": len(decisions) - len(would_execute),
        "receipts": receipts,
        "generated_at": _utc_now(),
        "authority_boundary": {"approval_authority": "Anthony Meza", "default_state": "fail_closed"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch Night Supervisor effector intents (fail-closed).")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--intents-json", required=True, help="Path to an effector-intent JSON array.")
    parser.add_argument("--enable", action="append", default=[], help="Capability to enable (repeatable).")
    parser.add_argument("--apply", action="store_true", help="Execute cleared effectors. Requires env arming too.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    intents = json.loads(Path(args.intents_json).read_text(encoding="utf-8"))
    report = dispatch(
        intents,
        repo_root=args.repo_root,
        enabled_capabilities=args.enable,
        execution_enabled=bool(args.apply),
        apply=bool(args.apply),
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
