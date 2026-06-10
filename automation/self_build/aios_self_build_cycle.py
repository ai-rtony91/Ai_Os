"""Compatibility wrapper for the canonical self-build cycle modules.

Canonical ownership lives in:
- automation/orchestration/autonomy_control_plane/aios_self_build_cycle_composer.py
- automation/orchestration/autonomy_reports/aios_self_build_evidence_persister.py

This file exists only so the PowerShell control plane and older callers can keep
invoking automation/self_build/aios_self_build_cycle.py. It composes no separate
self-build decision logic and persists no evidence with a local persister.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_IMPORT_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_IMPORT_ROOT))

from automation.orchestration.autonomy_control_plane.aios_self_build_cycle_composer import (
    decide_self_build_cycle as canonical_decide_self_build_cycle,
)
from automation.orchestration.autonomy_reports.aios_self_build_evidence_persister import (
    persist_cycle_evidence as canonical_persist_cycle_evidence,
)


DEFAULT_OUTPUT_ROOT = Path("Reports/self_build_cycle")
BLOCKED_CAPABILITIES = [
    "command_execution",
    "worker_dispatch",
    "protected_loop_mutation",
    "production_trading",
    "external_connector_enablement",
    "secret_printing",
    "protected_repository_promotion",
]


def _legacy_decision_label(cycle: dict[str, Any]) -> str:
    action = str((cycle.get("decision") or {}).get("action") or "")
    if action in {"HOLD_BLOCKED", "FIX_TRUST_FAILURE", "BLOCKED_MALFORMED_INPUT"}:
        return "HUMAN_REQUIRED"
    if bool(cycle.get("requires_human", True)):
        return "PROTECTED_ACTION_REQUIRED"
    if action == "NO_ACTION":
        return "NO_ACTION_RECOMMENDED"
    return action or "HUMAN_REQUIRED"


def _legacy_safety_status(cycle: dict[str, Any]) -> str:
    if cycle.get("mode") == "DRY_RUN" and cycle.get("executed") is False:
        return "SAFE_OBSERVE_ONLY"
    return "BLOCKED_UNSAFE_CYCLE"


def _copy_if_written(src: str | None, dst: Path) -> str | None:
    if not src:
        return None
    source = Path(src)
    if not source.exists():
        return str(source)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dst)
    return str(dst)


def decide_self_build_cycle(
    repo_root: Path,
    mode: str = "DRY_RUN",
    input_root: Path | None = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Run the canonical observe-only cycle and adapt it for legacy callers."""
    if mode != "DRY_RUN":
        raise ValueError("Only DRY_RUN mode is supported for self-build cycle decisions.")

    inventory: dict[str, Any] = {}
    if input_root is not None:
        inventory["input_root"] = str(input_root)

    cycle = canonical_decide_self_build_cycle(
        inventory=inventory,
        control_plane_report={},
        router_report={},
        completion_inputs={},
        repo_root=repo_root,
    )
    persisted = canonical_persist_cycle_evidence(
        cycle,
        output_dir=repo_root / output_root,
        write_markdown=True,
        overwrite=True,
    )

    evidence_path = _copy_if_written(
        persisted.get("json_path"),
        repo_root / output_root / "latest_self_build_cycle.evidence.json",
    )
    report_path = _copy_if_written(
        persisted.get("md_path"),
        repo_root / output_root / "latest_self_build_cycle.report.md",
    )

    decision = cycle.get("decision") or {}
    emitted_actions: list[object] = []
    return {
        "schema_version": "AIOS-SELF-BUILD-CYCLE-WRAPPER-V1",
        "cycle_id": cycle.get("cycle_id"),
        "created_at_utc": cycle.get("generated_at"),
        "mode": cycle.get("mode", "DRY_RUN"),
        "decision": decision,
        "decision_label": _legacy_decision_label(cycle),
        "requires_human": True,
        "safety_status": _legacy_safety_status(cycle),
        "can_advance": False,
        "emitted_actions": emitted_actions,
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "canonical_modules": {
            "composer": "automation/orchestration/autonomy_control_plane/aios_self_build_cycle_composer.py",
            "persister": "automation/orchestration/autonomy_reports/aios_self_build_evidence_persister.py",
        },
        "canonical_persist_result": persisted,
        "evidence_path": evidence_path,
        "report_path": report_path,
        "safe_next_action": "Human review required before any protected decision advances.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the canonical observe-only AI_OS self-build decision cycle.")
    parser.add_argument("--mode", choices=["DRY_RUN"], default="DRY_RUN")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input-root", default=None)
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    args = parser.parse_args()

    payload = decide_self_build_cycle(
        Path(args.repo_root).resolve(),
        mode=args.mode,
        input_root=Path(args.input_root) if args.input_root else None,
        output_root=Path(args.output_root),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["safety_status"] == "SAFE_OBSERVE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
