"""Observe-only AI_OS self-build decision cycle.

This module connects the existing self-build recommendation model to a single
bounded decision cycle. It never executes commands, dispatches workers, mutates
protected loop state, or approves protected actions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_IMPORT_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_IMPORT_ROOT))

from automation.bridge.aios_self_build_model import build_recommendations
from automation.bridge.aios_status_model import capture_repo_snapshot, read_json_if_exists, utc_now, write_json, write_markdown


DEFAULT_INPUT_ROOT = Path("Reports/generated/phase_0_to_4_bridge")
DEFAULT_OUTPUT_ROOT = Path("Reports/self_build_cycle")
REQUIRED_INPUTS = {
    "phase0": "phase0_infrastructure_inventory.json",
    "phase1": "phase1_wiring_map.json",
    "phase2": "phase2_approval_compressor_result.json",
    "phase3": "phase3_governance_enforcement.json",
}
BLOCKED_TERMS = (
    "merge",
    "apply",
    "broker",
    "live",
    "secret",
    "order execution",
    "real order",
    "powershell",
    "cmd.exe",
    "bash",
)


def _safe_action_text(text: str) -> bool:
    lowered = text.lower()
    return not any(term in lowered for term in BLOCKED_TERMS)


def _read_inputs(repo_root: Path, input_root: Path) -> tuple[dict[str, Any], list[str]]:
    loaded: dict[str, Any] = {}
    missing: list[str] = []
    for key, file_name in REQUIRED_INPUTS.items():
        path = repo_root / input_root / file_name
        payload = read_json_if_exists(path)
        if payload is None:
            missing.append(str(input_root / file_name).replace("\\", "/"))
            loaded[key] = None
        else:
            loaded[key] = payload
    return loaded, missing


def _decision_label(missing_inputs: list[str], recommendations: list[dict[str, Any]]) -> str:
    if missing_inputs:
        return "BLOCKED_MISSING_INPUTS"
    if any(item.get("status") == "BLOCKED" for item in recommendations):
        return "PROTECTED_ACTION_REQUIRED"
    if recommendations:
        return "READY_FOR_HUMAN_REVIEW"
    return "NO_ACTION_RECOMMENDED"


def _render_markdown(payload: dict[str, Any]) -> dict[str, object]:
    return {
        "SUMMARY": "Observe-only self-build cycle completed without executing decision output.",
        "DECISION LABEL": payload["decision_label"],
        "MODE": payload["mode"],
        "REQUIRES HUMAN": payload["requires_human"],
        "SAFETY STATUS": payload["safety_status"],
        "MISSING INPUTS": payload["missing_inputs"],
        "RECOMMENDATION COUNT": payload["recommendation_count"],
        "EVIDENCE PATH": payload["evidence_path"],
        "SAFE NEXT ACTION": payload["safe_next_action"],
    }


def persist_evidence_bundle(repo_root: Path, output_root: Path, payload: dict[str, Any]) -> Path:
    """Persist the self-build cycle evidence bundle and markdown companion."""
    evidence_path = repo_root / output_root / "latest_self_build_cycle.evidence.json"
    report_path = repo_root / output_root / "latest_self_build_cycle.report.md"
    payload["evidence_path"] = str(evidence_path)
    payload["report_path"] = str(report_path)
    write_json(evidence_path, payload)
    write_markdown(report_path, "AI_OS Self-Build Observe-Only Cycle", _render_markdown(payload))
    return evidence_path


def decide_self_build_cycle(
    repo_root: Path,
    mode: str = "DRY_RUN",
    input_root: Path = DEFAULT_INPUT_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    if mode != "DRY_RUN":
        raise ValueError("Only DRY_RUN mode is supported for self-build cycle decisions.")

    now = utc_now()
    snapshot = capture_repo_snapshot(repo_root)
    inputs, missing_inputs = _read_inputs(repo_root, input_root)
    phase0 = inputs.get("phase0") if isinstance(inputs.get("phase0"), dict) else {}
    recommendations = [item.to_dict() for item in build_recommendations(now, phase0)]
    unsafe_emitted_actions = [str(item) for item in [] if not _safe_action_text(str(item))]
    decision_label = _decision_label(missing_inputs, recommendations)
    requires_human = bool(missing_inputs or recommendations)
    safety_status = "SAFE_OBSERVE_ONLY" if not unsafe_emitted_actions else "BLOCKED_UNSAFE_ACTION_TEXT"
    can_advance = not missing_inputs and not unsafe_emitted_actions and decision_label == "READY_FOR_HUMAN_REVIEW"

    payload: dict[str, Any] = {
        "schema_version": "AIOS-SELF-BUILD-CYCLE-EVIDENCE-V1",
        "created_at_utc": now,
        "mode": mode,
        "decision_label": decision_label,
        "requires_human": requires_human,
        "safety_status": safety_status,
        "can_advance": can_advance,
        "repo": {
            "root": snapshot.repo_root,
            "branch": snapshot.branch,
            "dirty_files": snapshot.dirty_files,
        },
        "inputs": {
            key: {
                "path": str(input_root / REQUIRED_INPUTS[key]).replace("\\", "/"),
                "loaded": value is not None,
            }
            for key, value in inputs.items()
        },
        "missing_inputs": missing_inputs,
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
        "unsafe_emitted_actions": unsafe_emitted_actions,
        "emitted_actions": [],
        "blocked_capabilities": [
            "command_execution",
            "worker_dispatch",
            "protected_loop_mutation",
            "production_trading",
            "external_connector_enablement",
            "secret_printing",
            "protected_repository_promotion",
        ],
        "safe_next_action": (
            "Review missing self-build inputs before advancing."
            if missing_inputs
            else "Human review required before any protected decision advances."
        ),
        "evidence_path": None,
        "report_path": None,
    }
    persist_evidence_bundle(repo_root, output_root, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one observe-only AI_OS self-build decision cycle.")
    parser.add_argument("--mode", choices=["DRY_RUN"], default="DRY_RUN")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input-root", default=str(DEFAULT_INPUT_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    args = parser.parse_args()

    payload = decide_self_build_cycle(
        Path(args.repo_root).resolve(),
        mode=args.mode,
        input_root=Path(args.input_root),
        output_root=Path(args.output_root),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["safety_status"] == "SAFE_OBSERVE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
