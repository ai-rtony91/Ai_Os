from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_CODEX_PACKET_FROM_QUEUE.v1"

DEFAULT_APPROVAL_AUTHORITY = (
    "Anthony Meza approves staging, commit, push, merge, scheduler activation, daemon activation, "
    "worker dispatch, queue mutation, approval mutation, broker/live trading, credentials, real orders, "
    "real webhooks, and destructive actions."
)


def _protected_required(item: dict[str, Any]) -> bool:
    flags = item.get("protected_action_flags", {})
    if not isinstance(flags, dict):
        return True
    return any(bool(value) for value in flags.values())


def _safety_block() -> str:
    return "\n".join(
        [
            "SAFETY:",
            "No broker.",
            "No credentials.",
            "No live trading.",
            "No real orders.",
            "No real webhooks.",
            "No scheduler activation.",
            "No daemon activation.",
            "No worker dispatch.",
            "No queue mutation.",
            "No approval mutation.",
            "No git add.",
            "No commit.",
            "No push.",
            "No merge.",
            "No destructive cleanup.",
            "No background runtime.",
            "No network access.",
            "No Codex launch.",
            "No ChatGPT API call.",
        ]
    )


def build_codex_packet_from_queue_item(
    queue_item: dict[str, Any] | None,
    *,
    packet_id: str | None = None,
    lane: str | None = None,
    worktree: str = "C:\\Dev\\Ai.Os",
    branch: str = "main",
    approval_authority: str = DEFAULT_APPROVAL_AUTHORITY,
) -> dict[str, Any]:
    item = queue_item if isinstance(queue_item, dict) else {}
    action_id = str(item.get("action_id", "unknown_action"))
    allowed_paths = [str(path) for path in item.get("allowed_paths", []) if str(path)]
    validators = [str(command) for command in item.get("validators", [])]
    packet = packet_id or f"PKT-AIOS-QUEUE-{action_id.upper().replace('_', '-')}-DRY-RUN"
    lane_id = lane or action_id.replace("_", "-")

    if not allowed_paths:
        return {
            "schema": SCHEMA,
            "packet_ready": False,
            "packet_id": packet,
            "reason_code": "allowed_paths_missing",
            "codex_prompt_text": "",
            "write_scope": [],
            "validator_chain": validators,
            "safety_blocks": _safety_block().splitlines(),
            "next_safe_action": "Stop and add bounded allowed paths before generating a Codex packet.",
        }
    if _protected_required(item):
        return {
            "schema": SCHEMA,
            "packet_ready": False,
            "packet_id": packet,
            "reason_code": "protected_action_required",
            "codex_prompt_text": "",
            "write_scope": allowed_paths,
            "validator_chain": validators,
            "safety_blocks": _safety_block().splitlines(),
            "next_safe_action": "Stop because protected actions require Anthony approval.",
        }

    prompt = "\n".join(
        [
            "CODEX-ONLY PROMPT",
            "",
            "AI_OS EXECUTION TOKEN",
            "AI_OS BOOTSTRAP REQUIRED",
            "",
            "IDENTITY HEADER:",
            "SUPERVISOR IDENTITY: ChatGPT AIOS Control Supervisor",
            "ZONE: LOCAL_DEV_C_DEV_AI_OS",
            "WORKER IDENTITY: CODEX_LOCAL_APPLY_WORKER",
            f"LANE: {lane_id}",
            f"APPROVAL AUTHORITY: {approval_authority}",
            "MODE: APPLY",
            f"WORKTREE: {worktree}",
            f"BRANCH: {branch}",
            f"PACKET ID: {packet}",
            "",
            "MISSION:",
            f"Apply bounded queue action `{action_id}` only inside the listed write scope.",
            "",
            "WRITE ONLY:",
            *allowed_paths,
            "",
            _safety_block(),
            "",
            "VALIDATE:",
            *(validators or ["python -m pytest -p no:cacheprovider"]),
            "",
            "STOP:",
            "Report only.",
            "No staging.",
            "No commit.",
            "No push.",
        ]
    )
    return {
        "schema": SCHEMA,
        "packet_ready": True,
        "packet_id": packet,
        "reason_code": "packet_ready",
        "codex_prompt_text": prompt,
        "write_scope": allowed_paths,
        "validator_chain": validators,
        "safety_blocks": _safety_block().splitlines(),
        "next_safe_action": "Review the generated Codex packet before any paste/execution.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a Codex packet from a self-build queue item.")
    parser.add_argument("--queue-item", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    item = json.loads(args.queue_item)
    print(json.dumps(build_codex_packet_from_queue_item(item), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
