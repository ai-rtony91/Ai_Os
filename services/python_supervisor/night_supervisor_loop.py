"""AI_OS Night Supervisor cycle (brainstem -> intents -> gated dispatch).

Schema/contract reference: schemas/aios/orchestration/overnight_supervisor.schema.json
Mode: DRY_RUN by default. APPLY only with --apply AND env arming AND approvals.
next_safe_action: Run with no flags to preview a full night cycle. Review the
morning brief. Enable capabilities one tier at a time once a dry cycle looks
correct on the real Windows runtime.
commit_performed: NO / push_performed: NO

One cycle:
  scan -> assign -> brainstem report -> build intents -> dispatch decisions
  -> (optional, fully-gated) execute -> morning brief.
This runs a SINGLE pass. It is not a daemon and never loops on its own; the
nightly cadence is owned by the approved scheduler/operator layer, with a hard
stop after each pass.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from action_dispatcher import KILL_SWITCH_ENV, dispatch
from action_intent import CAPABILITY_LADDER, build_action_intents
from supervisor_engine import build_supervisor_report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_capabilities(enabled: list[str], ladder_through: str | None) -> list[str]:
    """Expand an explicit list and/or a ladder cut-point into a capability set."""

    caps = set(enabled or [])
    if ladder_through and ladder_through in CAPABILITY_LADDER:
        idx = CAPABILITY_LADDER.index(ladder_through)
        caps.update(CAPABILITY_LADDER[: idx + 1])
    return [cap for cap in CAPABILITY_LADDER if cap in caps]


def run_cycle(
    repo_root: str | Path = ".",
    *,
    enabled_capabilities: list[str] | None = None,
    ladder_through: str | None = None,
    execution_enabled: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    """Run one fail-closed Night Supervisor cycle and return a full report."""

    root = Path(repo_root).resolve()
    kill = bool(os.environ.get(KILL_SWITCH_ENV, "").strip())

    brainstem = build_supervisor_report(root)
    intents = build_action_intents(brainstem.get("packet_flow", []))
    capabilities = _resolve_capabilities(enabled_capabilities or [], ladder_through)

    # Kill switch hard-stops any execution while still producing read-only evidence.
    dispatch_report = dispatch(
        intents,
        repo_root=root,
        enabled_capabilities=capabilities,
        execution_enabled=bool(execution_enabled) and not kill,
        apply=bool(apply) and not kill,
    )

    executed = [r for r in dispatch_report.get("receipts", []) if r.get("receipt", {}).get("executed")]
    morning = dict(brainstem.get("morning_brief", {}))
    morning["autonomy"] = {
        "kill_switch_engaged": kill,
        "enabled_capabilities": capabilities,
        "intents_built": len(intents),
        "would_execute": dispatch_report.get("would_execute_count", 0),
        "blocked": dispatch_report.get("blocked_count", 0),
        "executed": len(executed),
        "execution_mode": dispatch_report.get("mode"),
    }

    return {
        "schema": "AIOS_NIGHT_SUPERVISOR_CYCLE.v1",
        "mode": dispatch_report.get("mode", "DRY_RUN"),
        "kill_switch_engaged": kill,
        "supervisor_status": brainstem.get("supervisor_status"),
        "repo_health": brainstem.get("repo_health"),
        "action_intents": intents,
        "dispatch": dispatch_report,
        "morning_brief": morning,
        "generated_at": _utc_now(),
        "authority_boundary": brainstem.get("authority_boundary"),
        "single_pass": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a single AI_OS Night Supervisor cycle (fail-closed).")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--enable", action="append", default=[], help="Capability to enable (repeatable).")
    parser.add_argument(
        "--ladder-through",
        default=None,
        choices=CAPABILITY_LADDER,
        help="Enable all capabilities up to and including this ladder rung.",
    )
    parser.add_argument("--apply", action="store_true", help="Execute cleared effectors (requires env arming).")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    report = run_cycle(
        args.repo_root,
        enabled_capabilities=args.enable,
        ladder_through=args.ladder_through,
        execution_enabled=bool(args.apply),
        apply=bool(args.apply),
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
