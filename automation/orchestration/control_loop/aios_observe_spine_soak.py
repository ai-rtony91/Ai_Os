"""AI_OS observe-spine soak runner (observe-only).

This module runs the observe spine seven times without writing to any protected
state. It only writes final closeout evidence under Reports/final_observe_spine_closure/.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from automation.orchestration.control_loop.aios_observe_spine_runner import (
    run_observe_spine_runner,
)


SCHEMA = "AIOS_OBSERVE_SPINE_SOAK.v1"
MODE = "DRY_RUN_CLOSEOUT"
CYCLE_COUNT = 7

REPORT_DIR = Path("Reports") / "final_observe_spine_closure"
REPORT_JSON_NAME = "observe_spine_7_cycle_soak.json"
REPORT_MD_NAME = "observe_spine_7_cycle_soak.md"
FINAL_JSON_NAME = "final_closeout_status.json"
FINAL_MD_NAME = "final_closeout_status.md"

READY_FOR_NEXT_PHASE = "READY_FOR_NEXT_PHASE"
HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
BLOCKED_WITH_REAL_REASON = "BLOCKED_WITH_REAL_REASON"
ALLOWED_FINAL_STATUSES = {
    READY_FOR_NEXT_PHASE,
    HUMAN_APPROVAL_REQUIRED,
    BLOCKED_WITH_REAL_REASON,
}


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ensure_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _collect_cycle_snapshot(report: dict[str, Any], *, cycle_index: int) -> dict[str, Any]:
    mutation_projection = report.get("mutation_projection") if isinstance(report.get("mutation_projection"), dict) else {}
    validate_mutation_boundaries = (
        report.get("validate_mutation_boundaries")
        if isinstance(report.get("validate_mutation_boundaries"), dict)
        else {}
    )
    return {
        "cycle_index": cycle_index,
        "generated_at_utc": report.get("generated_at_utc"),
        "observe_loop_status": report.get("observe_loop_status"),
        "p2_bridge_status": report.get("p2_bridge_status"),
        "queue_gate_status": report.get("queue_gate_status"),
        "runtime_apply_status": report.get("runtime_apply_status"),
        "sos_status": report.get("sos_status"),
        "scheduler_status": report.get("scheduler_status"),
        "stale_layers": _ensure_list(report.get("stale_layers")),
        "real_blockers": _ensure_list(report.get("real_blockers")),
        "governance_blockers": _ensure_list(report.get("governance_blockers")),
        "code_blockers": _ensure_list(report.get("code_blockers")),
        "mutation_projection": {
            key: mutation_projection.get(key)
            for key in sorted(mutation_projection.keys())
        },
        "validate_mutation_boundaries": {
            key: validate_mutation_boundaries.get(key)
            for key in sorted(validate_mutation_boundaries.keys())
        },
        "safe_next_action": report.get("safe_next_action"),
    }


def _classify_final_status(
    *,
    cycles: list[dict[str, Any]],
    stale_layers: list[str],
    real_blockers: list[str],
    governance_blockers: list[str],
    code_blockers: list[str],
    all_mutation_flags_false: bool,
) -> tuple[str, str, str | None]:
    cycle_statuses = [str(cycle.get("observe_loop_status") or "").strip() for cycle in cycles]
    if (
        cycle_statuses
        and all(status == "OBSERVE_LOOP_READY" for status in cycle_statuses)
        and not stale_layers
        and not real_blockers
        and not governance_blockers
        and not code_blockers
        and all_mutation_flags_false
    ):
        return (
            READY_FOR_NEXT_PHASE,
            "All seven observe-spine cycles were READY and mutation-free.",
            "Anthony may approve the next real phase only after independently reviewing the final closeout evidence.",
        )

    if not stale_layers and not real_blockers and not code_blockers and governance_blockers:
        return (
            HUMAN_APPROVAL_REQUIRED,
            "Observe spine remains blocked only on human-governance approval items.",
            "Anthony must resolve the named governance approvals before any real action.",
        )

    blockers = _unique(stale_layers + real_blockers + governance_blockers + code_blockers)
    if not blockers:
        blockers = ["observe-spine evidence did not reach a ready state"]
    return (
        BLOCKED_WITH_REAL_REASON,
        "Observe spine remains blocked by named real blockers.",
        f"Resolve: {', '.join(blockers)}.",
    )


def build_observe_spine_7_cycle_soak_report(
    *,
    repo_root: str | Path = ".",
    now: str | None = None,
    observe_runner: Callable[..., dict[str, Any]] = run_observe_spine_runner,
) -> dict[str, Any]:
    root = Path(repo_root)
    now_value = _now(now)

    cycles: list[dict[str, Any]] = []
    for cycle_index in range(1, CYCLE_COUNT + 1):
        report = observe_runner(repo_root=root, now=now_value, write_reports=False)
        cycles.append(_collect_cycle_snapshot(report, cycle_index=cycle_index))

    cycle_statuses = [str(cycle.get("observe_loop_status") or "").strip() for cycle in cycles]
    stale_layers = _unique([layer for cycle in cycles for layer in cycle.get("stale_layers", [])])
    real_blockers = _unique([layer for cycle in cycles for layer in cycle.get("real_blockers", [])])
    governance_blockers = _unique([layer for cycle in cycles for layer in cycle.get("governance_blockers", [])])
    code_blockers = _unique([layer for cycle in cycles for layer in cycle.get("code_blockers", [])])

    mutation_flags_false = True
    for cycle in cycles:
        for value in cycle.get("mutation_projection", {}).values():
            if value is not False:
                mutation_flags_false = False
                break
        if not mutation_flags_false:
            break
        for value in cycle.get("validate_mutation_boundaries", {}).values():
            if value is not False:
                mutation_flags_false = False
                break
        if not mutation_flags_false:
            break

    final_status, status_reason, next_human_decision = _classify_final_status(
        cycles=cycles,
        stale_layers=stale_layers,
        real_blockers=real_blockers,
        governance_blockers=governance_blockers,
        code_blockers=code_blockers,
        all_mutation_flags_false=mutation_flags_false,
    )

    stable_status = len(set(cycle_statuses)) == 1 if cycle_statuses else False
    blocked_cycles = sum(1 for status in cycle_statuses if status != "OBSERVE_LOOP_READY")

    report = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": now_value,
        "repo_root": root.as_posix(),
        "cycle_count": CYCLE_COUNT,
        "cycles": cycles,
        "cycle_statuses": cycle_statuses,
        "stable_status": stable_status,
        "stale_layers": stale_layers,
        "real_blockers": real_blockers,
        "governance_blockers": governance_blockers,
        "code_blockers": code_blockers,
        "mutation_flags_false_across_all_cycles": mutation_flags_false,
        "blocked_cycles": blocked_cycles,
        "final_status": final_status,
        "status": final_status,
        "status_reason": status_reason,
        "required_human_decision": next_human_decision,
        "safe_next_action": (
            "All observed layers are ready; Anthony may decide whether to proceed to the next real phase."
            if final_status == READY_FOR_NEXT_PHASE
            else "Anthony must review the named blockers before any real action."
            if final_status == HUMAN_APPROVAL_REQUIRED
            else "Resolve the named real blockers before any real action."
        ),
        "observe_loop_status": cycles[-1].get("observe_loop_status") if cycles else None,
        "runtime_apply_status": cycles[-1].get("runtime_apply_status") if cycles else None,
        "queue_gate_status": cycles[-1].get("queue_gate_status") if cycles else None,
        "p2_bridge_status": cycles[-1].get("p2_bridge_status") if cycles else None,
        "scheduler_status": cycles[-1].get("scheduler_status") if cycles else None,
        "sos_status": cycles[-1].get("sos_status") if cycles else None,
        "report_paths": [
            (root / REPORT_DIR / REPORT_JSON_NAME).as_posix(),
            (root / REPORT_DIR / REPORT_MD_NAME).as_posix(),
        ],
        "final_closeout_report_paths": [
            (root / REPORT_DIR / FINAL_JSON_NAME).as_posix(),
            (root / REPORT_DIR / FINAL_MD_NAME).as_posix(),
        ],
    }
    return report


def _build_soak_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI_OS Observe Spine 7-Cycle Soak",
        "",
        f"- final_status: `{report.get('final_status')}`",
        f"- status_reason: {report.get('status_reason')}",
        f"- stable_status: `{report.get('stable_status')}`",
        f"- mutation_flags_false_across_all_cycles: `{report.get('mutation_flags_false_across_all_cycles')}`",
        f"- stale_layers: `{report.get('stale_layers')}`",
        f"- real_blockers: `{report.get('real_blockers')}`",
        f"- governance_blockers: `{report.get('governance_blockers')}`",
        f"- code_blockers: `{report.get('code_blockers')}`",
        "",
        "## Cycles",
    ]
    for cycle in report.get("cycles", []):
        lines.append(
            f"- cycle {cycle.get('cycle_index')}: status={cycle.get('observe_loop_status')} "
            f"stale_layers={cycle.get('stale_layers')} real_blockers={cycle.get('real_blockers')} "
            f"governance_blockers={cycle.get('governance_blockers')} code_blockers={cycle.get('code_blockers')}"
        )
    lines.extend(
        [
            "",
            "## Final Decision",
            f"- required_human_decision: {report.get('required_human_decision')}",
            f"- safe_next_action: {report.get('safe_next_action')}",
            "",
            "- This soak run never mutates queue, worker inbox, command queue, runtime, scheduler, SOS, telemetry, services, apps, live trading, broker, or approval inbox state.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_final_closeout_status(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AIOS_FINAL_OBSERVE_SPINE_CLOSEOUT.v1",
        "mode": MODE,
        "generated_at_utc": report.get("generated_at_utc"),
        "repo_root": report.get("repo_root"),
        "status": report.get("final_status"),
        "final_status": report.get("final_status"),
        "cycle_count": report.get("cycle_count"),
        "cycle_statuses": report.get("cycle_statuses"),
        "stable_status": report.get("stable_status"),
        "stale_layers": report.get("stale_layers"),
        "real_blockers": report.get("real_blockers"),
        "governance_blockers": report.get("governance_blockers"),
        "code_blockers": report.get("code_blockers"),
        "mutation_flags_false_across_all_cycles": report.get("mutation_flags_false_across_all_cycles"),
        "blocked_cycles": report.get("blocked_cycles"),
        "status_reason": report.get("status_reason"),
        "required_human_decision": report.get("required_human_decision"),
        "safe_next_action": report.get("safe_next_action"),
        "observe_loop_status": report.get("observe_loop_status"),
        "runtime_apply_status": report.get("runtime_apply_status"),
        "queue_gate_status": report.get("queue_gate_status"),
        "p2_bridge_status": report.get("p2_bridge_status"),
        "scheduler_status": report.get("scheduler_status"),
        "sos_status": report.get("sos_status"),
        "report_paths": report.get("final_closeout_report_paths"),
    }


def _build_final_closeout_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI_OS Final Observe Spine Closeout",
        "",
        f"- final_status: `{report.get('final_status')}`",
        f"- stable_status: `{report.get('stable_status')}`",
        f"- cycle_count: `{report.get('cycle_count')}`",
        f"- stale_layers: `{report.get('stale_layers')}`",
        f"- real_blockers: `{report.get('real_blockers')}`",
        f"- governance_blockers: `{report.get('governance_blockers')}`",
        f"- code_blockers: `{report.get('code_blockers')}`",
        f"- mutation_flags_false_across_all_cycles: `{report.get('mutation_flags_false_across_all_cycles')}`",
        f"- required_human_decision: {report.get('required_human_decision')}",
        f"- safe_next_action: {report.get('safe_next_action')}",
    ]
    return "\n".join(lines) + "\n"


def write_observe_spine_7_cycle_soak_reports(
    report: dict[str, Any],
    *,
    repo_root: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    report_dir = Path(output_dir) if output_dir is not None else root / REPORT_DIR
    if not report_dir.is_absolute():
        report_dir = root / report_dir
    report_dir.mkdir(parents=True, exist_ok=True)

    soak_json_path = report_dir / REPORT_JSON_NAME
    soak_md_path = report_dir / REPORT_MD_NAME
    final_json_path = report_dir / FINAL_JSON_NAME
    final_md_path = report_dir / FINAL_MD_NAME

    report["report_paths"] = [soak_json_path.as_posix(), soak_md_path.as_posix()]
    report["final_closeout_report_paths"] = [final_json_path.as_posix(), final_md_path.as_posix()]

    final_closeout = _build_final_closeout_status(report)
    _write_json(soak_json_path, report)
    _write_text(soak_md_path, _build_soak_markdown(report))
    _write_json(final_json_path, final_closeout)
    _write_text(final_md_path, _build_final_closeout_markdown(final_closeout))

    report["final_closeout_status"] = final_closeout
    return report


def run_observe_spine_7_cycle_soak(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    observe_runner: Callable[..., dict[str, Any]] = run_observe_spine_runner,
    write_reports: bool = True,
) -> dict[str, Any]:
    report = build_observe_spine_7_cycle_soak_report(
        repo_root=repo_root,
        now=now,
        observe_runner=observe_runner,
    )
    if write_reports:
        report = write_observe_spine_7_cycle_soak_reports(report, repo_root=repo_root, output_dir=output_dir)
    return report


def _cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AI_OS observe-spine 7-cycle soak.")
    parser.add_argument("--repo-root", default=".", help="Repository root for evidence lookup.")
    parser.add_argument("--output-dir", default=None, help="Output directory for closeout reports.")
    parser.add_argument("--now", default=None, help="Optional UTC timestamp override.")
    parser.add_argument("--no-write", action="store_true", help="Build the soak report without writing files.")
    return parser.parse_args()


def main() -> int:
    args = _cli()
    report = run_observe_spine_7_cycle_soak(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        now=args.now,
        write_reports=not args.no_write,
    )
    print(json.dumps(
        {
            "final_status": report.get("final_status"),
            "stable_status": report.get("stable_status"),
            "cycle_count": report.get("cycle_count"),
            "stale_layers": report.get("stale_layers"),
            "real_blockers": report.get("real_blockers"),
            "governance_blockers": report.get("governance_blockers"),
            "code_blockers": report.get("code_blockers"),
        },
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
