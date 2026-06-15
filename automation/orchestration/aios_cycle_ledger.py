from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_CYCLE_LEDGER_DASHBOARD_SOS.v1"
LEDGER_SCHEMA = "AIOS_CYCLE_LEDGER_ENTRY.v1"
DASHBOARD_SCHEMA = "AIOS_CYCLE_DASHBOARD_CONTRACT.v1"

DEFAULT_MISSION = "AIOS self-building control-plane cycle memory"
FOREX_MILESTONE = (
    "AIOS self-building machine -> first proof target: industrial-grade forex bot builder "
    "-> no broker/live/secrets until gates prove safety"
)

VALIDATION_FAILURE_STATUSES = {
    "failed",
    "fail",
    "failure",
    "error",
    "blocked",
    "validation_failed",
}
SAFE_VALIDATION_STATUSES = {
    "",
    "not_run",
    "pending",
    "pending_safe_validation",
    "pass",
    "passed",
    "success",
    "report_only",
}
SOS_BLOCKER_TERMS = (
    "protected",
    "approval",
    "owner",
    "validation",
    "repo_corruption",
    "corruption",
    "secret",
    "credential",
    "broker",
    "live_trading",
    "live",
)


def _safety() -> dict[str, bool]:
    return {
        "preview_only": True,
        "evidence_only": True,
        "command_execution": False,
        "filesystem_writes": False,
        "reports_written": False,
        "network_access": False,
        "subprocess": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
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
        return _normalized(value) in {"1", "true", "yes", "y", "required", "blocked", "failed"}
    return bool(value)


def _selected_packet(evidence: dict[str, Any]) -> dict[str, Any] | None:
    value = evidence.get("selected_packet") or evidence.get("current_packet")
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        return {"packet_id": value.strip()}
    return None


def _current_packet_id(selected_packet: dict[str, Any] | None) -> str:
    if not selected_packet:
        return ""
    return _text(
        selected_packet.get("packet_id")
        or selected_packet.get("id")
        or selected_packet.get("title")
    )


def _count(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return 0
    return 0


def _provided_safety(evidence: dict[str, Any]) -> dict[str, Any]:
    safety = evidence.get("safety")
    return safety if isinstance(safety, dict) else {}


def _flag(evidence: dict[str, Any], safety: dict[str, Any], *names: str) -> bool:
    for name in names:
        if _bool(evidence.get(name)) or _bool(safety.get(name)):
            return True
    return False


def _approval_required(evidence: dict[str, Any]) -> bool:
    approvals = evidence.get("approval_required")
    if isinstance(approvals, dict):
        return any(_bool(value) for value in approvals.values())
    if _bool(approvals):
        return True
    return bool(_as_text_list(evidence.get("required_approvals")))


def _validation_failed(evidence: dict[str, Any]) -> bool:
    status = _normalized(evidence.get("validation_status"))
    if status in VALIDATION_FAILURE_STATUSES:
        return True
    if status in SAFE_VALIDATION_STATUSES:
        return False
    return _bool(evidence.get("validation_failed"))


def _blocker_requires_sos(evidence: dict[str, Any]) -> bool:
    status = _normalized(evidence.get("blocker_status"))
    if status not in {"blocked", "hard_blocked", "sos", "failed"}:
        return False
    reasons = _as_text_list(evidence.get("blockers"))
    reason = _text(evidence.get("blocker_reason") or evidence.get("sos_reason"))
    if reason:
        reasons.append(reason)
    reason_text = " ".join(reasons).lower()
    return any(term in reason_text for term in SOS_BLOCKER_TERMS)


def _sos_decision(evidence: dict[str, Any]) -> tuple[bool, str]:
    safety = _provided_safety(evidence)
    checks = [
        (
            _flag(evidence, safety, "protected_gate_blocked", "protected_action_blocked"),
            "blocked protected gate",
        ),
        (_approval_required(evidence), "approval-required action"),
        (_validation_failed(evidence), "validation failure requiring owner decision"),
        (_flag(evidence, safety, "repo_corruption", "repository_corruption"), "repo corruption"),
        (_flag(evidence, safety, "secrets_boundary", "secret", "secrets"), "secrets boundary"),
        (_flag(evidence, safety, "credentials_boundary", "credential", "credentials"), "credentials boundary"),
        (_flag(evidence, safety, "broker_boundary", "broker"), "broker boundary"),
        (_flag(evidence, safety, "live_trading_boundary", "live_trading", "live_execution"), "live-trading boundary"),
        (_blocker_requires_sos(evidence), "blocked SOS-class evidence"),
    ]
    for is_blocked, reason in checks:
        if is_blocked:
            return True, reason
    return False, "No SOS required for normal progress, no-work, safe validation pending, or report-only stop."


def _progress_status(evidence: dict[str, Any], sos_required: bool) -> str:
    explicit = _text(evidence.get("progress_status"))
    if explicit:
        return explicit
    if sos_required:
        return "blocked"
    if _text(evidence.get("stop_condition")).lower() in {"report_only", "stop_report_only", "normal_stop_report_only"}:
        return "report_only_stop"
    if _current_packet_id(_selected_packet(evidence)):
        return "cycle_recorded"
    return "no_work"


def _forex_alignment(evidence: dict[str, Any], sos_required: bool) -> dict[str, Any]:
    safety = _provided_safety(evidence)
    boundary_flags = {
        "broker": _flag(evidence, safety, "broker_boundary", "broker"),
        "live_trading": _flag(evidence, safety, "live_trading_boundary", "live_trading", "live_execution"),
        "secrets": _flag(evidence, safety, "secrets_boundary", "secret", "secrets"),
        "credentials": _flag(evidence, safety, "credentials_boundary", "credential", "credentials"),
    }
    blocked = [name for name, present in boundary_flags.items() if present]
    return {
        "milestone": FOREX_MILESTONE,
        "proof_target": "industrial-grade forex bot builder",
        "control_plane_role": "cycle memory, dashboard progress, blocker/SOS decision, next safe action",
        "aligned": not blocked,
        "blocked_boundaries": blocked,
        "requires_future_gates_before_execution": True,
        "sos_required": sos_required,
    }


def build_cycle_ledger_dashboard(evidence: Any | None = None) -> dict[str, Any]:
    payload = _as_dict(evidence)
    selected = _selected_packet(payload)
    packet_id = _current_packet_id(selected)
    sos_required, sos_reason = _sos_decision(payload)
    progress_status = _progress_status(payload, sos_required)
    timestamp_utc = _text(payload.get("timestamp_utc"), "UNKNOWN")
    next_safe_action = _text(
        payload.get("next_safe_action"),
        "Stop/report; add cycle evidence before selecting the next safe action.",
    )
    safety = _safety()
    alignment = _forex_alignment(payload, sos_required)

    ledger = {
        "schema": LEDGER_SCHEMA,
        "cycle_id": _text(payload.get("cycle_id"), "NO_CYCLE_EVIDENCE"),
        "timestamp_utc": timestamp_utc,
        "repo_branch": _text(payload.get("repo_branch"), "UNKNOWN"),
        "repo_head": _text(payload.get("repo_head"), "UNKNOWN"),
        "selected_packet": selected,
        "selected_reason": _text(payload.get("selected_reason")),
        "codex_prompt_emitted": _bool(payload.get("codex_prompt_emitted")),
        "validation_status": _text(payload.get("validation_status"), "not_run"),
        "validation_summary": _text(payload.get("validation_summary"), "No validation evidence supplied."),
        "pr_number": payload.get("pr_number"),
        "pr_status": _text(payload.get("pr_status"), "none"),
        "checks_status": _text(payload.get("checks_status"), "not_run"),
        "blocker_status": _text(payload.get("blocker_status"), "none" if not sos_required else "blocked"),
        "sos_required": sos_required,
        "sos_reason": sos_reason,
        "next_safe_action": next_safe_action,
        "forex_builder_alignment": alignment,
        "safety": safety,
    }

    dashboard = {
        "schema": DASHBOARD_SCHEMA,
        "current_mission": _text(payload.get("current_mission"), DEFAULT_MISSION),
        "current_cycle": ledger["cycle_id"],
        "current_packet": packet_id,
        "progress_status": progress_status,
        "tests_passed": _count(payload.get("tests_passed")),
        "tests_failed": _count(payload.get("tests_failed")),
        "pr_status": ledger["pr_status"],
        "checks_status": ledger["checks_status"],
        "blocker_status": ledger["blocker_status"],
        "sos_required": sos_required,
        "sos_reason": sos_reason,
        "next_safe_action": next_safe_action,
        "last_updated_utc": timestamp_utc,
    }

    return {
        "schema": SCHEMA,
        "cycle_ledger": ledger,
        "dashboard_contract": dashboard,
        "commands_executed": [],
        "files_written": [],
        "workers_dispatched": False,
        "queues_mutated": False,
        "approvals_mutated": False,
        "safety": safety,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview AIOS cycle ledger and dashboard/SOS contract.")
    parser.add_argument("--evidence", default="{}", help="JSON cycle evidence.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = json.loads(args.evidence)
    except json.JSONDecodeError:
        evidence = {}
    result = build_cycle_ledger_dashboard(evidence)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
