"""AI_OS Night Supervisor effector stage (Codex V2 spine -> gated hands).

Schema/contract reference: schemas/aios/orchestration/supervisor_action_intent.schema.json
Mode: DRY_RUN by default. APPLY only with --apply AND env arming.
next_safe_action: Run with no flags to preview the effector stage. Enable
capabilities one ladder rung at a time once a dry pass looks correct on the
real Windows runtime.
commit_performed: NO / push_performed: NO

This is NOT a second supervisor. It is a single-pass downstream stage:
  Codex supervisor_engine_v2.build_supervisor_v2_report()  (the canonical spine)
    -> routing_contracts
      -> effector_intent.build_effector_intents
        -> effector_dispatcher.dispatch   (OFF by default)
It is not a daemon and never loops on its own.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[2]
# Codex V2 spine lives in automation/orchestration; add it to the import path.
_ORCH_DIR = _REPO_ROOT / "automation" / "orchestration"
for _p in (str(_ORCH_DIR), str(_THIS.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from effector_dispatcher import KILL_SWITCH_ENV, dispatch  # noqa: E402
from effector_intent import CAPABILITY_LADDER, build_effector_intents  # noqa: E402
from supervisor_engine_v2 import build_supervisor_v2_report  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_capabilities(enabled: list[str], ladder_through: str | None) -> list[str]:
    caps = set(enabled or [])
    if ladder_through and ladder_through in CAPABILITY_LADDER:
        caps.update(CAPABILITY_LADDER[: CAPABILITY_LADDER.index(ladder_through) + 1])
    return [cap for cap in CAPABILITY_LADDER if cap in caps]


def run_effector_stage(
    repo_root: str | Path = ".",
    *,
    enabled_capabilities: list[str] | None = None,
    ladder_through: str | None = None,
    execution_enabled: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    """Run one fail-closed effector pass downstream of the Codex V2 spine."""

    root = Path(repo_root).resolve()
    kill = bool(os.environ.get(KILL_SWITCH_ENV, "").strip())

    spine = build_supervisor_v2_report(root)  # read-only/preview; apply_enabled stays False
    contracts = spine.get("routing_contracts", [])
    intents = build_effector_intents(contracts)
    capabilities = _resolve_capabilities(enabled_capabilities or [], ladder_through)

    dispatch_report = dispatch(
        intents,
        repo_root=root,
        enabled_capabilities=capabilities,
        execution_enabled=bool(execution_enabled) and not kill,
        apply=bool(apply) and not kill,
    )

    executed = [r for r in dispatch_report.get("receipts", []) if r.get("receipt", {}).get("executed")]
    return {
        "schema": "AIOS_NIGHT_SUPERVISOR_EFFECTOR_STAGE.v1",
        "mode": dispatch_report.get("mode", "DRY_RUN"),
        "kill_switch_engaged": kill,
        "spine_schema": spine.get("schema"),
        "spine_blocked_count": spine.get("blocked_count"),
        "contracts_in": len(contracts),
        "intents_built": len(intents),
        "effector_dispatch": dispatch_report,
        "summary": {
            "would_execute": dispatch_report.get("would_execute_count", 0),
            "blocked": dispatch_report.get("blocked_count", 0),
            "executed": len(executed),
            "enabled_capabilities": capabilities,
        },
        "generated_at": _utc_now(),
        "single_pass": True,
        "authority_boundary": {"approval_authority": "Anthony Meza", "default_state": "fail_closed"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a single Night Supervisor effector pass (fail-closed).")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--enable", action="append", default=[], help="Capability to enable (repeatable).")
    parser.add_argument("--ladder-through", default=None, choices=CAPABILITY_LADDER, help="Enable up to this rung.")
    parser.add_argument("--apply", action="store_true", help="Execute cleared effectors (requires env arming).")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    report = run_effector_stage(
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
