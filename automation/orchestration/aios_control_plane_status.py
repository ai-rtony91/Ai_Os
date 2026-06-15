from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_CONTROL_PLANE_STATUS.v1"
DEFAULT_OUTPUT_DIR = Path("Reports/aios_control_plane")
LATEST_FILENAME = "AIOS_CONTROL_PLANE_STATUS_latest.json"


HARD_BLOCK_FLAGS = {
    "broker",
    "live_trading",
    "real_orders",
    "real_webhooks",
    "credentials",
    "scheduler",
    "daemon",
    "queue_mutation",
    "approval_mutation",
    "worker_dispatch",
}


def base_safety() -> dict[str, bool]:
    return {
        "broker": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "credentials": False,
        "scheduler": False,
        "daemon": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "command_execution": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def _collect_safety(*contracts: dict[str, Any]) -> dict[str, bool]:
    safety = base_safety()
    for contract in contracts:
        source = contract.get("safety", contract.get("safety_summary", {}))
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if key in safety:
                safety[key] = safety[key] or bool(value)
    return safety


def _collect_approvals(*contracts: dict[str, Any]) -> list[str]:
    approvals: set[str] = set()
    for contract in contracts:
        source = contract.get("approval_required", {})
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if bool(value):
                approvals.add(str(key))
    return sorted(approvals)


def _collect_blockers(
    cli_result_ingest: dict[str, Any],
    github_pr_state: dict[str, Any],
    safety: dict[str, bool],
    bounded_executor_ready: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    cli_blockers = cli_result_ingest.get("blockers", [])
    if isinstance(cli_blockers, list):
        blockers.extend(str(item) for item in cli_blockers)
    if github_pr_state and github_pr_state.get("merge_block_reason") not in {None, "", "none"}:
        blockers.append(str(github_pr_state["merge_block_reason"]))
    for key in sorted(HARD_BLOCK_FLAGS):
        if safety.get(key) is True:
            blockers.append(f"safety_{key}_blocked")
    if bounded_executor_ready and bounded_executor_ready.get("status") not in {None, "ready_for_human_review"}:
        blockers.append(str(bounded_executor_ready.get("reason_code", "bounded_executor_not_ready")))
    return sorted(set(blockers))


def build_control_plane_status(
    resume_state: dict[str, Any] | None = None,
    cli_result_ingest: dict[str, Any] | None = None,
    operator_relay: dict[str, Any] | None = None,
    local_runner_bridge: dict[str, Any] | None = None,
    github_pr_state: dict[str, Any] | None = None,
    bounded_executor_ready: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resume = resume_state if isinstance(resume_state, dict) else {}
    cli_result = cli_result_ingest if isinstance(cli_result_ingest, dict) else {}
    relay = operator_relay if isinstance(operator_relay, dict) else {}
    runner = local_runner_bridge if isinstance(local_runner_bridge, dict) else {}
    github = github_pr_state if isinstance(github_pr_state, dict) else {}
    ready = bounded_executor_ready if isinstance(bounded_executor_ready, dict) else {}

    plan = resume.get("next_build_plan", {})
    if not isinstance(plan, dict):
        plan = {}

    safety = _collect_safety(resume, cli_result, relay, runner, github, ready)
    approvals_required = _collect_approvals(resume, relay, runner, ready)
    blockers = _collect_blockers(cli_result, github, safety, ready)
    bounded_ready = runner.get("runner_status") == "preview_ready" and ready.get("status") == "ready_for_human_review"

    dashboard_ready = bool(
        resume.get("resume_ready") is True
        and bounded_ready
        and not blockers
        and not any(safety.get(key) is True for key in HARD_BLOCK_FLAGS)
    )
    loop_status = "dashboard_ready" if dashboard_ready else "blocked" if blockers else "waiting_for_review"

    next_action = relay.get(
        "next_safe_action",
        runner.get("next_safe_action", resume.get("next_safe_action", "Review control-plane status.")),
    )

    return {
        "schema": SCHEMA,
        "milestone": "single_controlled_action_to_safe_forex_paper_build_loop",
        "current_goal": resume.get("goal", "forex-paper-bot"),
        "loop_status": loop_status,
        "resume_ready": bool(resume.get("resume_ready") is True),
        "next_component": plan.get("next_component", "unknown"),
        "next_action": next_action,
        "proof_net": "forex-paper-bot",
        "approvals_required": approvals_required,
        "blockers": blockers,
        "safety": safety,
        "dashboard_ready": dashboard_ready,
    }


def _resolve_output_dir(repo_root: Path, output_dir: Path | str | None = None) -> Path:
    allowed_root = (repo_root / DEFAULT_OUTPUT_DIR).resolve()
    target = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target = target if target.is_absolute() else repo_root / target
    target = target.resolve()
    try:
        target.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError("control_plane_dir_outside_allowed_root") from exc
    return target


def write_control_plane_status(
    repo_root: Path,
    status: dict[str, Any],
    *,
    output_dir: Path | str | None = None,
) -> dict[str, Any]:
    target_dir = _resolve_output_dir(repo_root, output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    latest_path = target_dir / LATEST_FILENAME
    output = {
        **status,
        "control_plane_status_path": latest_path.relative_to(repo_root).as_posix(),
    }
    latest_path.write_text(json.dumps(output, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview dashboard-readable AIOS control-plane status.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root.")
    parser.add_argument("--write", action="store_true", help="Write latest status under Reports/aios_control_plane.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    status = build_control_plane_status()
    if args.write:
        status = write_control_plane_status(repo_root, status)
    print(json.dumps(status, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
