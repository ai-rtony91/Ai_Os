from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_APPROVED_PACKET_EXECUTOR_CONTRACT.v1"

READY_STATUSES = {"candidate", "ready", "selected"}
SAFE_RISK_LEVELS = {"low", "medium", "bounded", "preview"}
REJECTED_STATUSES = {"rejected", "invalid", "unsafe", "cancelled", "canceled"}

BLOCKED_WRITE_PREFIXES = (
    ".git/",
    "reports/",
    "control/review_bridge/",
    "automation/orchestration/work_packets/preview/",
)

SAFE_PATH_BOUNDARY_TOKENS = {
    "broker",
    "live",
    "credential",
    "credentials",
    "secret",
    "secrets",
    "order",
    "orders",
    "webhook",
    "webhooks",
}

PROTECTED_ACTION_TERMS = {
    "scheduler": ("scheduler", "schedule job"),
    "daemon": ("daemon", "background service"),
    "commit": ("git commit", "commit"),
    "push": ("git push", "push"),
    "merge": ("git merge", "merge"),
}

DESTRUCTIVE_TERMS = (
    "git reset",
    "git clean",
    "delete branch",
    "branch deletion",
    "remove-item",
    "rm -rf",
    "destructive",
)

DEFAULT_FORBIDDEN_ACTIONS = [
    "execute_without_matching_human_owner_approval",
    "launch_codex_without_matching_human_owner_approval",
    "dispatch_worker",
    "mutate_queue",
    "mutate_approval_state",
    "start_scheduler_without_separate_approval",
    "start_daemon_without_separate_approval",
    "write_reports",
    "access_network",
    "touch_broker_live_trading_credentials_orders_or_webhooks",
    "git_add",
    "git_commit_without_separate_approval",
    "git_push_without_separate_approval",
    "git_merge_without_separate_approval",
    "git_reset",
    "branch_deletion",
]


def _safety() -> dict[str, bool]:
    return {
        "preview_only": True,
        "evidence_only": True,
        "execution_contract_only": True,
        "command_execution": False,
        "codex_launch": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "filesystem_writes": False,
        "reports_written": False,
        "network_access": False,
        "scheduler_activation": False,
        "daemon_activation": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "git_merge": False,
        "git_reset": False,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_items(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [part.strip() for part in value.replace("\r", "\n").replace(",", "\n").splitlines() if part.strip()]
    if value in (None, "", {}, []):
        return []
    return [value]


def _as_text_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _as_items(value) if str(item).strip()]


def _text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def _normalized(value: Any) -> str:
    return _text(value).lower().replace("-", "_").replace(" ", "_")


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return _normalized(value) in {"1", "true", "yes", "y", "approved", "allowed", "granted"}
    return bool(value)


def _selected_packet(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, bool]:
    selected = (
        payload.get("selected_packet")
        or payload.get("packet")
        or payload.get("current_packet")
    )
    if selected in (None, "", [], {}):
        if payload.get("packet_id"):
            return payload, False
        return None, False
    if isinstance(selected, dict):
        return selected, False
    return None, True


def _packet_id(packet: dict[str, Any] | None) -> str:
    if not packet:
        return ""
    return _text(packet.get("packet_id") or packet.get("id"))


def _approval_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in (
        "approval_evidence",
        "approval",
        "human_owner_approval",
        "approvals",
        "approval_records",
        "approval_evidence_records",
    ):
        value = payload.get(key)
        for item in _as_items(value):
            if isinstance(item, dict):
                records.append(item)
            elif isinstance(item, bool):
                records.append({"approved": item})
    return records


def _approval_packet_ids(record: dict[str, Any]) -> list[str]:
    values: list[Any] = []
    for key in ("packet_id", "approved_packet_id", "selected_packet_id", "packet_ids"):
        if key in record:
            values.extend(_as_items(record.get(key)))
    return [_text(item) for item in values if _text(item)]


def _approval_source(record: dict[str, Any]) -> str:
    return _text(
        record.get("approval_source")
        or record.get("source")
        or record.get("approver")
        or record.get("approved_by")
        or record.get("approval_authority")
    )


def _approval_is_explicit(record: dict[str, Any]) -> bool:
    status = _normalized(record.get("approval_status") or record.get("status"))
    return (
        record.get("approved") is True
        or record.get("human_owner_approved") is True
        or status in {"approved", "allowed", "granted", "explicit_approval"}
    )


def _approval_is_human_owner(record: dict[str, Any]) -> bool:
    source = _approval_source(record).lower()
    return (
        record.get("human_owner") is True
        or record.get("human_owner_approved") is True
        or "anthony" in source
        or "human owner" in source
    )


def _matching_approval(packet_id: str, records: list[dict[str, Any]]) -> tuple[str, str]:
    if not records:
        return "missing", ""

    explicit = [record for record in records if _approval_is_explicit(record)]
    if not explicit:
        return "not_approved", _approval_source(records[0])

    owner_approved = [record for record in explicit if _approval_is_human_owner(record)]
    if not owner_approved:
        return "not_human_owner", _approval_source(explicit[0])

    for record in owner_approved:
        packet_ids = _approval_packet_ids(record)
        if packet_id in packet_ids:
            return "approved", _approval_source(record)

    if any(_approval_packet_ids(record) for record in owner_approved):
        return "packet_mismatch", _approval_source(owner_approved[0])
    return "packet_id_missing", _approval_source(owner_approved[0])


def _normalized_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip().lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _tokens(value: str) -> set[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in value)
    return set(cleaned.split())


def _path_boundary_rejections(paths: list[str]) -> list[str]:
    rejected: list[str] = []
    for path in paths:
        tokens = _tokens(_normalized_path(path))
        unsafe = sorted(tokens.intersection(SAFE_PATH_BOUNDARY_TOKENS))
        if unsafe:
            rejected.append(f"unsafe_boundary_path:{path}:{','.join(unsafe)}")
    return rejected


def _unsafe_write_scope_blocks(paths: list[str]) -> list[str]:
    blocked: list[str] = []
    for path in paths:
        normalized = _normalized_path(path)
        if not normalized:
            blocked.append("required_file_empty")
            continue
        if normalized.startswith("/") or ":" in normalized.split("/")[0]:
            blocked.append(f"unsafe_write_scope:absolute_path:{path}")
        if normalized == ".." or normalized.startswith("../") or "/../" in normalized:
            blocked.append(f"unsafe_write_scope:path_traversal:{path}")
        if any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in BLOCKED_WRITE_PREFIXES):
            blocked.append(f"unsafe_write_scope:blocked_path:{path}")
    return blocked


def _action_text(packet: dict[str, Any]) -> str:
    values: list[str] = []
    for key in (
        "requested_actions",
        "required_actions",
        "actions",
        "protected_actions",
        "required_approvals",
        "safety_flags",
        "execution_requests",
    ):
        values.extend(_as_text_list(packet.get(key)))
    return " ".join(values).lower()


def _hidden_command_text(packet: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("command", "commands", "execution_command", "runtime_command"):
        values.extend(_as_text_list(packet.get(key)))
    return " ".join(values).lower()


def _separate_approval_actions(payload: dict[str, Any], records: list[dict[str, Any]]) -> set[str]:
    actions: set[str] = set()

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            for key, flag in value.items():
                if _bool(flag):
                    actions.add(_normalized(key))
        else:
            for item in _as_text_list(value):
                actions.add(_normalized(item))

    collect(payload.get("separate_approvals"))
    collect(payload.get("approved_actions"))
    for record in records:
        collect(record.get("separate_approvals"))
        collect(record.get("approved_actions"))
    return actions


def _protected_action_blocks(action_text: str, approved_actions: set[str]) -> tuple[list[str], bool]:
    blocked: list[str] = []
    protected_required = False
    for action, terms in PROTECTED_ACTION_TERMS.items():
        if any(term in action_text for term in terms):
            protected_required = True
            normalized_action = _normalized(action)
            if normalized_action not in approved_actions and f"git_{normalized_action}" not in approved_actions:
                blocked.append(f"protected_action_requires_separate_approval:{action}")
    return blocked, protected_required


def _rejected_action_reasons(packet: dict[str, Any]) -> list[str]:
    rejected: list[str] = []
    action_text = _action_text(packet)
    hidden_command_text = _hidden_command_text(packet)

    if hidden_command_text:
        rejected.append("hidden_command_execution_request")
    if "approval mutation" in action_text or "approval_mutation" in action_text or "mutate approval" in action_text:
        rejected.append("approval_mutation_request")
    if "queue mutation" in action_text or "queue_mutation" in action_text or "mutate queue" in action_text:
        rejected.append("queue_mutation_request")
    for term in DESTRUCTIVE_TERMS:
        if term in action_text or term in hidden_command_text:
            rejected.append(f"destructive_action_request:{term}")
    return rejected


def _next_safe_action(status: str, packet_id: str) -> str:
    if status == "allowed":
        return (
            f"Execution contract allows bounded local APPLY preview for {packet_id}; "
            "use only a separately scoped approved runner."
        )
    if status == "no_packet":
        return "Stop; select a packet before evaluating executor approval."
    if status == "rejected":
        return "Stop; rejected packet execution evidence must be removed or repaired."
    return "Stop; satisfy blocked approval, validator, scope, or protected-action gates before execution."


def build_approved_packet_executor_contract(evidence: Any | None = None) -> dict[str, Any]:
    payload = _as_dict(evidence)
    selected_packet, invalid_selected_packet = _selected_packet(payload)
    selected_packet_id = _packet_id(selected_packet)
    approval_records = _approval_records(payload)
    approval_status, approval_source = _matching_approval(selected_packet_id, approval_records)
    blocked_reasons: list[str] = []
    rejected_reasons: list[str] = []
    protected_action_required = False

    if selected_packet is None and not invalid_selected_packet:
        status = "no_packet"
        return {
            "schema": SCHEMA,
            "executor_status": status,
            "selected_packet": None,
            "approval_required": True,
            "approval_status": "not_evaluated",
            "approval_source": "",
            "execution_allowed": False,
            "command_preview_allowed": False,
            "codex_launch_allowed": False,
            "protected_action_required": False,
            "blocked_reasons": [],
            "rejected_reasons": [],
            "required_validators": [],
            "allowed_execution_mode": "none",
            "forbidden_actions": DEFAULT_FORBIDDEN_ACTIONS,
            "commands_executed": [],
            "workers_dispatched": False,
            "queues_mutated": False,
            "approvals_mutated": False,
            "files_written": [],
            "safety": _safety(),
            "next_safe_action": _next_safe_action(status, ""),
        }

    if invalid_selected_packet or selected_packet is None:
        rejected_reasons.append("invalid_selected_packet_structure")
        selected_packet = None
    else:
        status_value = _normalized(selected_packet.get("status"))
        risk_level = _normalized(selected_packet.get("risk_level"))
        required_files = _as_text_list(selected_packet.get("required_files"))
        required_validators = _as_text_list(
            selected_packet.get("validators")
            or selected_packet.get("required_validators")
            or selected_packet.get("validator_chain")
        )

        if not selected_packet_id:
            rejected_reasons.append("selected_packet_id_missing")
        if status_value in REJECTED_STATUSES:
            rejected_reasons.append(f"selected_packet_status_rejected:{status_value}")
        elif status_value not in READY_STATUSES:
            blocked_reasons.append(f"selected_packet_status_not_ready:{status_value or 'missing'}")
        if risk_level not in SAFE_RISK_LEVELS:
            if risk_level in {"live", "production", "unsafe", "critical"}:
                rejected_reasons.append(f"unsafe_risk_level:{risk_level}")
            else:
                blocked_reasons.append(f"risk_level_not_allowed:{risk_level or 'missing'}")
        if not required_files:
            blocked_reasons.append("required_files_missing")
        if not required_validators:
            blocked_reasons.append("validators_missing")

        rejected_reasons.extend(_path_boundary_rejections(required_files))
        blocked_reasons.extend(_unsafe_write_scope_blocks(required_files))
        rejected_reasons.extend(_rejected_action_reasons(selected_packet))
        action_text = _action_text(selected_packet)
        approved_actions = _separate_approval_actions(payload, approval_records)
        protected_blocks, protected_action_required = _protected_action_blocks(action_text, approved_actions)
        blocked_reasons.extend(protected_blocks)

        if approval_status != "approved":
            blocked_reasons.append(f"human_owner_approval_{approval_status}")

    required_validators = []
    if selected_packet is not None:
        required_validators = _as_text_list(
            selected_packet.get("validators")
            or selected_packet.get("required_validators")
            or selected_packet.get("validator_chain")
        )

    if rejected_reasons:
        executor_status = "rejected"
    elif blocked_reasons:
        executor_status = "blocked"
    else:
        executor_status = "allowed"

    execution_allowed = executor_status == "allowed"
    command_preview_allowed = selected_packet is not None and not rejected_reasons and bool(required_validators)

    return {
        "schema": SCHEMA,
        "executor_status": executor_status,
        "selected_packet": selected_packet,
        "approval_required": True,
        "approval_status": approval_status,
        "approval_source": approval_source,
        "execution_allowed": execution_allowed,
        "command_preview_allowed": command_preview_allowed,
        "codex_launch_allowed": execution_allowed,
        "protected_action_required": protected_action_required,
        "blocked_reasons": blocked_reasons,
        "rejected_reasons": rejected_reasons,
        "required_validators": required_validators,
        "allowed_execution_mode": "bounded_local_apply_preview" if execution_allowed else "none",
        "forbidden_actions": DEFAULT_FORBIDDEN_ACTIONS,
        "commands_executed": [],
        "workers_dispatched": False,
        "queues_mutated": False,
        "approvals_mutated": False,
        "files_written": [],
        "safety": _safety(),
        "next_safe_action": _next_safe_action(executor_status, selected_packet_id),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate AIOS selected packet execution approval.")
    parser.add_argument("--evidence", default="{}", help="JSON selected packet and approval evidence.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = json.loads(args.evidence)
    except json.JSONDecodeError:
        evidence = {}
    result = build_approved_packet_executor_contract(evidence)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
