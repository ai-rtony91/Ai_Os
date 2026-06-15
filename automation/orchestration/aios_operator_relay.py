from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_OPERATOR_RELAY.v1"
DEFAULT_OUTPUT_DIR = Path("Reports/aios_relay")
LATEST_FILENAME = "AIOS_OPERATOR_RELAY_latest.json"


def safety_flags() -> dict[str, bool]:
    return {
        "api_call": False,
        "codex_launch": False,
        "command_execution": False,
        "file_writes": False,
        "network_access": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "scheduler": False,
        "daemon": False,
        "broker": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "credentials": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def _has_blockers(cli_result_ingest: dict[str, Any]) -> bool:
    blockers = cli_result_ingest.get("blockers", [])
    return isinstance(blockers, list) and len(blockers) > 0


def _human_action_required(resume_state: dict[str, Any], cli_result_ingest: dict[str, Any]) -> bool:
    if _has_blockers(cli_result_ingest):
        return True
    approval_required = resume_state.get("approval_required", {})
    return isinstance(approval_required, dict) and any(bool(value) for value in approval_required.values())


def build_operator_relay(
    resume_state: dict[str, Any] | None,
    cli_result_ingest: dict[str, Any] | None,
    next_build_plan: dict[str, Any] | None = None,
    *,
    inbound_source: str = "local_file_contract",
    outbound_target: str = "codex_prompt_packet",
) -> dict[str, Any]:
    resume = resume_state if isinstance(resume_state, dict) else {}
    cli_result = cli_result_ingest if isinstance(cli_result_ingest, dict) else {}
    plan = next_build_plan if isinstance(next_build_plan, dict) else resume.get("next_build_plan", {})
    if not isinstance(plan, dict):
        plan = {}

    human_action_required = _human_action_required(resume, cli_result)
    codex_prompt_ready = bool(
        resume.get("resume_ready") is True
        and not _has_blockers(cli_result)
        and plan.get("next_component") not in {None, "", "none"}
    )
    relay_status = "ready_for_operator_copy_paste" if codex_prompt_ready else "waiting_for_review"

    next_component = plan.get("next_component", "unknown")
    pasteback_summary = (
        f"Resume state is ready for {next_component}; Anthony approval is required before APPLY."
        if codex_prompt_ready
        else "Relay is available for review; do not launch Codex or call external APIs from this contract."
    )

    return {
        "schema": SCHEMA,
        "relay_status": relay_status,
        "inbound_source": inbound_source,
        "outbound_target": outbound_target,
        "human_action_required": human_action_required,
        "codex_prompt_ready": codex_prompt_ready,
        "pasteback_summary": pasteback_summary,
        "next_safe_action": resume.get(
            "next_safe_action",
            cli_result.get("next_safe_action", "Review relay state before preparing another packet."),
        ),
        "safety": safety_flags(),
    }


def _resolve_output_dir(repo_root: Path, output_dir: Path | str | None = None) -> Path:
    allowed_root = (repo_root / DEFAULT_OUTPUT_DIR).resolve()
    target = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target = target if target.is_absolute() else repo_root / target
    target = target.resolve()
    try:
        target.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError("operator_relay_dir_outside_allowed_root") from exc
    return target


def write_operator_relay(
    repo_root: Path,
    relay: dict[str, Any],
    *,
    output_dir: Path | str | None = None,
    generated_at_utc: datetime | None = None,
) -> dict[str, Any]:
    target_dir = _resolve_output_dir(repo_root, output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    now = generated_at_utc or datetime.now(timezone.utc)
    timestamp = now.astimezone(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    timestamped_path = target_dir / f"AIOS_OPERATOR_RELAY_{timestamp}.json"
    latest_path = target_dir / LATEST_FILENAME
    if timestamped_path.exists():
        raise FileExistsError("timestamped_operator_relay_exists")

    output = {
        **relay,
        "generated_at_utc": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "relay_paths": {
            "timestamped": timestamped_path.relative_to(repo_root).as_posix(),
            "latest": latest_path.relative_to(repo_root).as_posix(),
        },
    }
    serialized = json.dumps(output, indent=2, sort_keys=False) + "\n"
    timestamped_path.write_text(serialized, encoding="utf-8")
    latest_path.write_text(serialized, encoding="utf-8")
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a file-contract AIOS operator relay.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root.")
    parser.add_argument("--write", action="store_true", help="Write relay output under Reports/aios_relay.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    relay = build_operator_relay({"resume_ready": False}, {"blockers": []})
    if args.write:
        relay = write_operator_relay(repo_root, relay)
    print(json.dumps(relay, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
