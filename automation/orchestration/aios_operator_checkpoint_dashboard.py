from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_OPERATOR_CHECKPOINT_PANEL.v1"
MISSION = "self-building AIOS -> forex-builder proof -> daily earned repo work"
DETAIL_HINT = "run with -OutputJson for full report"
SAFETY_LINE = "no broker/live/secrets/orders/webhooks"
FORBIDDEN_ACTIONS = [
    "broker",
    "live trading",
    "credentials",
    "secrets",
    "orders",
    "webhooks",
    "scheduler",
    "daemon",
    "git add",
    "git commit",
    "git push",
    "git merge",
    "delete/cleanup without explicit approval",
]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_items(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [part.strip() for part in value.replace("\r", "\n").splitlines() if part.strip()]
    if value in (None, "", {}, []):
        return []
    return [value]


def _text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def _normalized(value: Any) -> str:
    return _text(value).lower().replace("-", "_").replace(" ", "_")


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return _normalized(value) in {"1", "true", "yes", "y", "pass", "passed", "green", "ready"}
    return bool(value)


def _get(payload: dict[str, Any], *path: str, default: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _selected_packet(report: dict[str, Any]) -> dict[str, Any] | None:
    value = report.get("selected_packet") or _get(report, "packet_queue_plan", "selected_packet")
    if isinstance(value, dict) and value:
        return value
    if isinstance(value, str) and value.strip():
        return {"packet_id": value.strip()}
    current_packet = _text(_get(report, "dashboard_contract", "current_packet"))
    if current_packet:
        return {"packet_id": current_packet}
    return None


def _packet_id(packet: dict[str, Any] | None) -> str:
    if not packet:
        return "none"
    return _text(packet.get("packet_id") or packet.get("id") or packet.get("title"), "none")


def _active_candidate_count(report: dict[str, Any]) -> int:
    keys = (
        "active_candidate_packets",
        "candidate_packets",
        "forex_roadmap_candidates",
    )
    count = 0
    for key in keys:
        count += len(_as_items(report.get(key)))
    count += len(_as_items(_get(report, "packet_queue_plan", "ranked_packets", default=[])))
    return count


def _preview_ready(report: dict[str, Any]) -> bool:
    return _bool(_get(report, "codex_ready_packet_preview", "packet_ready")) or _bool(
        _get(report, "cycle_ledger", "codex_prompt_emitted")
    )


def _approval_status(report: dict[str, Any]) -> str:
    return _normalized(report.get("approval_status") or _get(report, "approved_executor_contract", "approval_status"))


def _executor_status(report: dict[str, Any]) -> str:
    return _normalized(report.get("approved_executor_status") or _get(report, "approved_executor_contract", "executor_status"))


def _execution_allowed(report: dict[str, Any]) -> bool:
    return _bool(report.get("execution_allowed") or _get(report, "approved_executor_contract", "execution_allowed"))


def _sos_required(report: dict[str, Any]) -> bool:
    return _bool(report.get("sos_required") or _get(report, "dashboard_contract", "sos_required"))


def _pr_status(report: dict[str, Any]) -> str:
    status = _normalized(
        report.get("pr_status")
        or _get(report, "dashboard_contract", "pr_status")
        or _get(report, "cycle_ledger", "pr_status")
    )
    if status in {"", "no", "null", "not_run"}:
        return "none"
    if status in {"pass", "passed", "success", "green"}:
        return "green"
    return status


def _checks_status(report: dict[str, Any]) -> str:
    return _normalized(
        report.get("checks_status")
        or _get(report, "dashboard_contract", "checks_status")
        or _get(report, "cycle_ledger", "checks_status")
    )


def _tests_status(report: dict[str, Any]) -> str:
    status = _normalized(
        report.get("checks_status")
        or _get(report, "dashboard_contract", "checks_status")
        or _get(report, "cycle_ledger", "checks_status")
        or report.get("command_validation_status")
        or _get(report, "cycle_ledger", "validation_status")
    )
    if status in {"pass", "passed", "success", "green"}:
        return "pass"
    if status in {"fail", "failed", "failure", "error", "red"}:
        return "fail"
    if status in {"not_run", "not_applicable", "notapplicable", "pending", ""}:
        return "not_run"
    return "unknown"


def _blocker_exists(report: dict[str, Any]) -> bool:
    blocker_status = _normalized(
        report.get("blocker_status")
        or _get(report, "dashboard_contract", "blocker_status")
        or _get(report, "cycle_ledger", "blocker_status")
    )
    blockers = _as_items(report.get("rejection_reasons")) + _as_items(report.get("blockers"))
    return blocker_status not in {"", "none", "clear"} or bool(blockers)


def _state(report: dict[str, Any]) -> str:
    selected = _selected_packet(report)
    has_selected = selected is not None
    approval_status = _approval_status(report)
    executor_status = _executor_status(report)
    pr_status = _pr_status(report)
    checks_status = _checks_status(report)

    if _sos_required(report):
        return "SOS_REQUIRED"
    if executor_status == "blocked" and approval_status == "missing":
        return "WAITING_FOR_APPROVAL"
    if has_selected and _preview_ready(report) and not _execution_allowed(report):
        return "WAITING_FOR_APPROVAL"
    if has_selected and _execution_allowed(report):
        return "APPROVED_TO_WORK"
    if has_selected and pr_status in {"open", "checking"}:
        return "PR_IN_PROGRESS"
    if has_selected and checks_status in {"green", "pass", "passed"}:
        return "READY_FOR_MERGE_APPROVAL"
    if not has_selected and _active_candidate_count(report) == 0:
        return "IDLE_SAFE"
    if _blocker_exists(report):
        return "BLOCKED"
    return "REPORT_ONLY"


def _next_action(report: dict[str, Any], state: str) -> str:
    approval_status = _approval_status(report)
    checks_status = _checks_status(report)
    if state == "SOS_REQUIRED":
        return "wake Anthony / inspect blocker"
    if state == "WAITING_FOR_APPROVAL" or approval_status == "missing":
        return "approve APPLY / skip packet / inspect details"
    if state == "READY_FOR_MERGE_APPROVAL" or checks_status in {"green", "pass", "passed"}:
        return "approve merge / inspect PR"
    if state == "IDLE_SAFE":
        return "pick from bored queue"
    if _selected_packet(report) is None:
        return "run self-route / select next safe packet"
    return _text(report.get("next_safe_action"), "inspect details / keep report-only stop")


def _workbench_check(report: dict[str, Any]) -> str:
    files_written = _as_items(report.get("files_written"))
    if files_written:
        return "work_written"
    if _preview_ready(report):
        return "preview_only"
    return "not_written"


def _bored_task(
    packet_id: str,
    title: str,
    lane: str,
    reason: str,
    write_scope: list[str],
    validators: list[str],
) -> dict[str, Any]:
    return {
        "packet_id": packet_id,
        "title": title,
        "lane": lane,
        "priority": "low",
        "reason": reason,
        "write_scope": write_scope,
        "validators": validators,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "safety_flags": [
            "non_live_only",
            "evidence_first",
            "no_network",
            "no_broker",
            "no_secrets",
            "no_orders",
            "no_webhooks",
            "no_scheduler",
            "no_daemon",
            "no_protected_mutation",
        ],
        "earned_green_box_reason": "Legitimate docs/test improvement, not fake heatmap activity.",
    }


def build_bored_work_queue(report: dict[str, Any]) -> list[dict[str, Any]]:
    payload = _as_dict(report)
    if _selected_packet(payload) is not None or _active_candidate_count(payload) > 0:
        return []

    return [
        _bored_task(
            "PKT-AIOS-BORED-DOCS-POLISH-ONE",
            "Polish one orchestration doc for operator readability",
            "bored-docs-polish",
            "No active packet; safe documentation improvement can produce real repo value.",
            ["docs/orchestration/..."],
            ["python -m pytest -p no:cacheprovider tests/orchestration/test_aios_persistent_runtime_supervisor.py -q"],
        ),
        _bored_task(
            "PKT-AIOS-BORED-TEST-HARDENING-ONE",
            "Add one guard assertion to a stable orchestration test",
            "bored-test-hardening",
            "No active packet; small test hardening improves control-plane safety.",
            ["tests/orchestration/..."],
            ["python -m pytest -p no:cacheprovider tests/orchestration/test_aios_persistent_runtime_supervisor.py -q"],
        ),
        _bored_task(
            "PKT-AIOS-BORED-VALIDATOR-CLEANUP-ONE",
            "Tighten one protected-action drift guard",
            "bored-validator-cleanup",
            "No active packet; a narrow validator guard helps prevent unsafe action drift.",
            ["tests/orchestration/...", "automation/orchestration/..."],
            ["python -m pytest -p no:cacheprovider tests/orchestration/test_aios_operator_checkpoint_dashboard.py -q"],
        ),
    ]


def build_operator_checkpoint_panel(report: dict[str, Any]) -> dict[str, Any]:
    payload = _as_dict(report)
    selected = _selected_packet(payload)
    packet_id = _packet_id(selected)
    state = _state(payload)
    tests_status = _tests_status(payload)
    pr_status = _pr_status(payload)
    sos = _sos_required(payload)
    prompt = _preview_ready(payload)
    bored_queue = build_bored_work_queue(payload)
    active_candidates = _active_candidate_count(payload)
    next_action = _next_action(payload, state)
    progress_line = (
        f"selected={'yes' if selected else 'no'} | "
        f"prompt={'yes' if prompt else 'no'} | "
        f"tests={tests_status} | "
        f"PR={pr_status} | "
        f"SOS={'yes' if sos else 'no'}"
    )

    if bored_queue:
        top_bored = bored_queue[0]
        bored_line = f"{top_bored['packet_id']} - {top_bored['title']}"
        bored_queue_check = "available"
    elif selected:
        bored_line = "inactive because a packet is selected"
        bored_queue_check = "inactive_selected_packet"
    elif active_candidates:
        bored_line = "inactive because candidate packets are available"
        bored_queue_check = "inactive_candidate_packets"
    else:
        bored_line = "none"
        bored_queue_check = "none"

    checkpoint_summary = {
        "mission_check": "aligned",
        "packet_check": packet_id,
        "approval_check": state,
        "workbench_check": _workbench_check(payload),
        "validation_check": tests_status,
        "pr_check": pr_status,
        "sos_check": "yes" if sos else "no",
        "bored_queue_check": bored_queue_check,
    }
    lines = [
        "AIOS STATUS",
        f"Mission: {MISSION}",
        f"Packet: {packet_id}",
        f"State: {state}",
        f"Progress: {progress_line}",
        f"Next: {next_action}",
        f"Bored queue: {bored_line}",
        f"Safety: {SAFETY_LINE}",
        f"Details: {DETAIL_HINT}",
    ]

    return {
        "schema": SCHEMA,
        "status": "ready",
        "mission": MISSION,
        "current_packet": packet_id,
        "state": state,
        "checkpoint_summary": checkpoint_summary,
        "progress_line": progress_line,
        "next_action": next_action,
        "bored_queue": bored_queue,
        "detail_hint": DETAIL_HINT,
        "safety_line": SAFETY_LINE,
        "lines": lines,
    }


def format_operator_checkpoint_panel(panel: dict[str, Any]) -> str:
    payload = _as_dict(panel)
    lines = [str(line) for line in _as_items(payload.get("lines"))]
    if not lines:
        lines = build_operator_checkpoint_panel(payload).get("lines", [])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a compact AIOS operator checkpoint panel.")
    parser.add_argument("--report", default="{}", help="JSON AIOS runtime self-route report.")
    parser.add_argument("--text", action="store_true", help="Print the compact panel text instead of JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = json.loads(args.report)
    except json.JSONDecodeError:
        report = {}
    panel = build_operator_checkpoint_panel(report)
    if args.text:
        print(format_operator_checkpoint_panel(panel))
    else:
        print(json.dumps(panel, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
