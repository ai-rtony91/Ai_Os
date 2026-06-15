from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_CODEX_PACKET_BUILDER.v1"
DEFAULT_RELAY_DIR = Path("Reports/aios_relay")
DEFAULT_APPROVAL_AUTHORITY = (
    "Anthony Meza only approves staging, commit, push, merge, scheduler activation, "
    "daemon activation, worker dispatch, queue mutation, approval mutation, broker/live "
    "trading, credentials, real orders, real webhooks, and destructive actions."
)

SIMULATOR_ACTION = "build_forex_paper_execution_simulator"
SIMULATOR_PACKET_ID = "PKT-AIOS-FOREX-PAPER-EXECUTION-SIMULATOR-CONTINUATION-APPLY"
SIMULATOR_ALLOWED_PATHS = [
    "apps/trading_lab/trading_lab/forex_paper_execution_simulator.py",
    "tests/trading_lab/test_forex_paper_execution_simulator.py",
    "docs/orchestration/AIOS_FOREX_PAPER_EXECUTION_SIMULATOR.md",
    "automation/orchestration/aios_productive_bounded_executor.py",
    "tests/orchestration/test_aios_productive_bounded_executor.py",
    "automation/orchestration/aios_wake_continue.py",
    "tests/orchestration/test_aios_wake_continue.py",
]
SIMULATOR_VALIDATORS = [
    "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_productive_bounded_executor.py tests/orchestration/test_aios_wake_continue.py tests/trading_lab/test_forex_paper_execution_simulator.py",
]
SAFETY_BLOCKS = [
    "live trading BLOCKED",
    "broker execution BLOCKED",
    "credentials BLOCKED",
    "real orders BLOCKED",
    "real webhooks BLOCKED",
    "scheduler activation BLOCKED",
    "daemon activation BLOCKED",
    "worker dispatch BLOCKED",
    "queue mutation BLOCKED",
    "approval mutation BLOCKED",
    "ChatGPT API calls BLOCKED",
    "Codex launch/API calls BLOCKED",
    "git staging/commit/push/merge BLOCKED unless Anthony separately approves after report",
]


def _blank_packet(reason_code: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "packet_ready": False,
        "packet_id": "NONE",
        "packet_title": "No Codex Packet",
        "identity_header": {},
        "validator_chain": [],
        "write_scope": [],
        "safety_blocks": list(SAFETY_BLOCKS),
        "codex_prompt_text": "",
        "reason_code": reason_code,
        "next_safe_action": "Stop for human review before building a Codex packet.",
    }


def _identity_header(packet_id: str, approval_authority: str) -> dict[str, str]:
    return {
        "SUPERVISOR IDENTITY": "ChatGPT AIOS Control Supervisor",
        "ZONE": "LOCAL_DEV_C_DEV_AI_OS",
        "WORKER IDENTITY": "CODEX_LOCAL_APPLY_WORKER",
        "LANE": "autonomy-forex-paper-execution-simulator-continuation",
        "APPROVAL AUTHORITY": approval_authority,
        "MODE": "APPLY",
        "WORKTREE": r"C:\Dev\Ai.Os",
        "BRANCH": "main",
        "PACKET ID": packet_id,
    }


def _prompt_text(
    *,
    packet_id: str,
    approval_authority: str,
    validator_chain: list[str],
    write_scope: list[str],
) -> str:
    validators = "\n".join(f"{index}. {command}" for index, command in enumerate(validator_chain, start=1))
    write_only = "\n".join(write_scope)
    safety = "\n".join(f"* {item}" for item in SAFETY_BLOCKS)
    return f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY HEADER:
SUPERVISOR IDENTITY: ChatGPT AIOS Control Supervisor
ZONE: LOCAL_DEV_C_DEV_AI_OS
WORKER IDENTITY: CODEX_LOCAL_APPLY_WORKER
LANE: autonomy-forex-paper-execution-simulator-continuation
APPROVAL AUTHORITY: {approval_authority}
MODE: APPLY
WORKTREE: C:\\Dev\\Ai.Os
BRANCH: main
PACKET ID: {packet_id}

VALIDATOR CHAIN:
{validators}

MISSION:
Build productive bounded executor support and the paper-only Forex execution simulator component.

WRITE ONLY:
{write_only}

FORBIDDEN PATHS:
All paths outside WRITE ONLY.

SAFETY HARD BLOCKS:
{safety}

STOP: Report only. Do not stage. Do not commit. Do not push."""


def build_codex_packet_preview(
    continuation_controller: dict[str, Any] | None,
    mode_registry: dict[str, Any] | None = None,
    bounded_handoff: dict[str, Any] | None = None,
    approval_authority: str = DEFAULT_APPROVAL_AUTHORITY,
) -> dict[str, Any]:
    controller = continuation_controller if isinstance(continuation_controller, dict) else {}
    handoff = bounded_handoff if isinstance(bounded_handoff, dict) else {}
    allowed_action = str(handoff.get("allowed_action", "none"))

    if controller.get("codex_packet_required") is not True:
        return _blank_packet("codex_packet_not_required")
    if allowed_action != SIMULATOR_ACTION:
        return _blank_packet("unsupported_packet_action")

    packet_id = str(handoff.get("next_packet_id") or SIMULATOR_PACKET_ID)
    write_scope = [str(path) for path in handoff.get("allowed_paths", [])] or list(SIMULATOR_ALLOWED_PATHS)
    validator_chain = [str(command) for command in handoff.get("validators", [])] or list(SIMULATOR_VALIDATORS)
    identity_header = _identity_header(packet_id, approval_authority)

    return {
        "schema": SCHEMA,
        "packet_ready": True,
        "packet_id": packet_id,
        "packet_title": "Build Forex Paper Execution Simulator",
        "identity_header": identity_header,
        "validator_chain": validator_chain,
        "write_scope": write_scope,
        "safety_blocks": list(SAFETY_BLOCKS),
        "codex_prompt_text": _prompt_text(
            packet_id=packet_id,
            approval_authority=approval_authority,
            validator_chain=validator_chain,
            write_scope=write_scope,
        ),
        "next_safe_action": "Present this packet preview for Anthony review. Do not launch Codex automatically.",
    }


def _resolve_output_dir(repo_root: Path, output_dir: Path | str | None = None) -> Path:
    allowed_root = (repo_root / DEFAULT_RELAY_DIR).resolve()
    target = Path(output_dir) if output_dir is not None else DEFAULT_RELAY_DIR
    target = target if target.is_absolute() else repo_root / target
    target = target.resolve()
    try:
        target.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError("codex_packet_preview_dir_outside_allowed_root") from exc
    return target


def write_codex_packet_preview(
    repo_root: Path,
    packet_preview: dict[str, Any],
    *,
    output_dir: Path | str | None = None,
) -> dict[str, Any]:
    target_dir = _resolve_output_dir(repo_root, output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "AIOS_CODEX_PACKET_PREVIEW_latest.json"
    output = {
        **packet_preview,
        "codex_packet_preview_path": target_path.relative_to(repo_root).as_posix(),
    }
    target_path.write_text(json.dumps(output, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a Codex packet contract without launching Codex.")
    parser.add_argument("--action", default=SIMULATOR_ACTION)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    preview = build_codex_packet_preview(
        {"codex_packet_required": True},
        bounded_handoff={
            "allowed_action": args.action,
            "next_packet_id": SIMULATOR_PACKET_ID,
            "allowed_paths": SIMULATOR_ALLOWED_PATHS,
            "validators": SIMULATOR_VALIDATORS,
        },
    )
    print(json.dumps(preview, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
