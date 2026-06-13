"""Pure AIOS approval/SOS hard-gate classification logic.

The PowerShell runner gathers read-only repo and no-write evidence. This
module classifies protected actions as blocked unless a future packet supplies
explicit Human Owner approval through a separate authority path. It writes no
files, starts no processes, and emits no executable commands.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_APPROVAL_SOS_HARD_GATE_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

PROTECTED_ACTIONS = [
    ("apply", "APPLY without explicit Human Owner approval"),
    ("commit", "commit without explicit Human Owner approval"),
    ("push", "push without explicit Human Owner approval"),
    ("pr", "PR without explicit Human Owner approval"),
    ("merge", "merge without explicit Human Owner approval"),
    ("runtime_start", "runtime start"),
    ("worker_launch", "worker launch"),
    ("scheduler_enablement", "scheduler enablement"),
    ("daemon_launch", "daemon launch"),
    ("queue_mutation", "queue mutation"),
    ("lock_mutation", "lock mutation"),
    ("approval_mutation", "approval mutation"),
    ("registry_mutation", "registry mutation"),
    ("packet_draft_write", "packet draft write"),
    ("proposed_packet_write", "proposed packet write"),
    ("reports_write", "Reports write"),
    ("telemetry_write", "telemetry write"),
    ("relay_write", "relay write"),
    ("broker_oanda_webhook_order_live_trading", "broker/OANDA/webhook/order/live trading"),
    ("secrets_env_access", "secrets/.env access"),
]

READ_ONLY_ACTIONS = [
    "repo_status_inspection",
    "authority_context_read",
    "validator_json_read",
    "dry_run_surface_execution",
    "console_summary",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return _safe_str(value).lower() in {"true", "1", "yes", "y"}


def _protected_action_catalog() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "label": label,
            "human_owner_required": True,
            "blocked_without_explicit_human_owner_approval": True,
            "approval_source": "current_session_human_owner",
        }
        for action_id, label in PROTECTED_ACTIONS
    ]


def _blocked_actions(catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "action_id": item["action_id"],
            "label": item["label"],
            "status": "BLOCKED_WITHOUT_EXPLICIT_HUMAN_OWNER_APPROVAL",
            "reason": "validator_or_recommendation_output_is_evidence_only",
        }
        for item in catalog
    ]


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not _bool(repo_state.get("branch_matches_expected", True)):
        stops.append("BRANCH_MISMATCH")
    if (
        _bool(repo_state.get("dirty", False))
        and _bool(repo_state.get("fail_on_dirty_worktree", False))
        and not _bool(repo_state.get("dirty_allowed_for_approval_sos_hard_gate_validation", False))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed", False)):
        return ["WRITE_SURFACE_RISK"]
    return []


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _safe_str(item)
        if key and key not in seen:
            result.append(key)
            seen.add(key)
    return result


def _status(stop_conditions: list[str], no_write_proof: dict[str, Any]) -> str:
    if _bool(no_write_proof.get("changed", False)):
        return "BLOCKED_BY_WRITE_SURFACE_RISK"
    if stop_conditions:
        return "BLOCKED"
    return "PASS"


def build_approval_sos_hard_gate_result(payload: dict[str, Any]) -> dict[str, Any]:
    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    catalog = _protected_action_catalog()
    blocked_actions = _blocked_actions(catalog)
    stop_conditions = _dedupe(_repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof))
    status = _status(stop_conditions, no_write_proof)

    approval_state = {
        "explicit_human_owner_approval_present": False,
        "approval_mutation_allowed": False,
        "approval_source": "none_supplied_to_read_only_gate",
        "status": "HUMAN_OWNER_REQUIRED_FOR_PROTECTED_ACTIONS",
    }
    sos_state = {
        "status": "CLEAR" if status == "PASS" else "REVIEW_REQUIRED",
        "sos_hard_stop_active": False,
        "wake_required": False,
        "reason": "No SOS escalation was detected by this read-only gate.",
    }

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "approval_state": approval_state,
        "sos_state": sos_state,
        "protected_action_catalog": catalog,
        "blocked_actions": blocked_actions,
        "allowed_read_only_actions": READ_ONLY_ACTIONS,
        "human_owner_required_for": [item["action_id"] for item in catalog],
        "safety": {
            "status": status,
            "console_only": True,
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "writes_proposed_packets": False,
            "outputs_packet_body": False,
            "creates_ready_stage": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "writes_relay": False,
            "starts_runtime": False,
            "launches_workers": False,
            "scheduler_or_daemon": False,
            "protected_action_recommended": False,
            "protected_actions_blocked": len(blocked_actions) == len(catalog),
            "read_only_inspection_allowed": True,
            "human_owner_required_before_protected_action": True,
            "secrets_or_env_access": False,
            "broker_or_live_trading": False,
        },
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "next_safe_action": (
            "Continue read-only governed autonomy validation; do not perform protected actions without Human Owner approval."
            if status == "PASS"
            else "Stop and review approval/SOS hard-gate blockers before any protected action."
        ),
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS approval/SOS hard-gate result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_approval_sos_hard_gate_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
