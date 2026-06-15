from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_COMPLETED_PACKET_MEMORY_SUPPRESSION.v1"

FOREX_MILESTONE = (
    "AIOS self-building machine -> first proof target: industrial-grade forex bot builder "
    "-> no broker/live/secrets until gates prove safety"
)

DEFAULT_COMPLETED_PACKETS = [
    {
        "packet_id": "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION",
        "title": "Connect candidate packet evidence adapter into self-route",
        "lane": "connect-candidate-evidence-to-selfroute",
        "required_files": [
            "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1",
            "tests/orchestration/test_aios_persistent_runtime_supervisor.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PACKET-QUEUE-PLANNER",
        "title": "AIOS packet queue planner",
        "lane": "add-aios-packet-queue-planner",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-PACKET-QUEUE-CONNECTOR",
        "title": "Connect runtime self-route to packet queue planner",
        "lane": "connect-runtime-selfroute-to-packet-queue-planner",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-CYCLE-LEDGER-DASHBOARD-SOS",
        "title": "AIOS cycle ledger dashboard SOS contract",
        "lane": "build-aios-cycle-ledger-dashboard-sos-contract",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-CYCLE-LEDGER-CONNECTOR",
        "title": "Connect runtime self-route to cycle ledger",
        "lane": "connect-runtime-selfroute-to-cycle-ledger",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-CANDIDATE-PACKET-EVIDENCE-ADAPTER",
        "title": "AIOS candidate packet evidence adapter",
        "lane": "build-candidate-packet-evidence-adapter",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-CANDIDATE-EVIDENCE-CONNECTOR",
        "title": "Connect runtime self-route to candidate evidence adapter",
        "lane": "connect-runtime-selfroute-to-candidate-evidence-adapter",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FIX-CANDIDATE-TO-PLANNER-HANDOFF",
        "title": "Fix candidate planner JSON handoff",
        "lane": "fix-selfroute-candidate-to-planner-handoff",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-APPROVED-PACKET-EXECUTOR-CONTRACT",
        "title": "AIOS approved packet executor contract",
        "lane": "build-approved-packet-executor-contract",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-APPROVED-EXECUTOR-CONNECTOR",
        "title": "Connect runtime self-route to approved executor contract",
        "lane": "connect-runtime-selfroute-to-approved-executor-contract",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC",
        "title": "feat(trading-lab): add canonical forex builder spec",
        "lane": "forex-builder-spec",
        "landed_pr": "#737",
        "commit": "cd012419",
        "completion_reason": "canonical forex builder spec landed on main",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md",
            "tests/orchestration/test_aios_forex_builder_roadmap.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md",
            "tests/orchestration/test_aios_forex_builder_roadmap.py",
        ],
        "source": "default_completed_memory",
    },
]

COMPLETE_STATUSES = {
    "complete",
    "completed",
    "done",
    "closed",
    "merged",
    "landed",
    "passed",
    "success",
}

REOPENED_STATUSES = {"reopened", "reopen", "open_again"}
REPAIR_STATUSES = {"validation_failed", "failed", "repair", "needs_repair"}


def _safety() -> dict[str, bool]:
    return {
        "preview_only": True,
        "evidence_only": True,
        "command_execution": False,
        "filesystem_writes": False,
        "reports_written": False,
        "network_access": False,
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


def _normalized_path(value: Any) -> str:
    normalized = _text(value).replace("\\", "/").strip().lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def _candidate_list(evidence: Any) -> list[dict[str, Any]]:
    if isinstance(evidence, list):
        return [item for item in evidence if isinstance(item, dict)]
    if isinstance(evidence, dict):
        for key in ("candidate_packets", "candidates", "packets"):
            value = evidence.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if evidence.get("packet_id"):
            return [evidence]
    return []


def _packet_id(record: dict[str, Any]) -> str:
    return _text(record.get("packet_id") or record.get("id"))


def _record_title(record: dict[str, Any]) -> str:
    return _text(record.get("title") or record.get("name") or record.get("pr_title"))


def _record_lane(record: dict[str, Any]) -> str:
    return _text(record.get("lane") or record.get("work_lane") or record.get("branch"))


def _required_files(record: dict[str, Any]) -> list[str]:
    return _as_text_list(
        record.get("required_files")
        or record.get("completed_files")
        or record.get("write_scope")
        or record.get("files")
        or record.get("changed_files")
    )


def _record_from_value(value: Any, source: str) -> dict[str, Any]:
    if isinstance(value, dict):
        record = dict(value)
        record.setdefault("source", source)
        return record
    return {
        "packet_id": _text(value),
        "source": source,
    }


def _completed_memory_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = [dict(record) for record in DEFAULT_COMPLETED_PACKETS]
    for item in _as_items(payload.get("completed_packet_ids")):
        records.append(_record_from_value(item, "completed_packet_ids"))
    for item in _as_items(payload.get("completed_packets")):
        records.append(_record_from_value(item, "completed_packets"))
    for item in _as_items(payload.get("landed_prs")):
        records.append(_record_from_value(item, "landed_prs"))
    for item in _as_items(payload.get("commit_history_summary")):
        records.append(_record_from_value(item, "commit_history_summary"))
    return records


def _cycle_ledger_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in _as_items(payload.get("cycle_ledger_history")):
        if not isinstance(item, dict):
            continue
        selected = item.get("selected_packet")
        record: dict[str, Any]
        if isinstance(selected, dict):
            record = dict(selected)
        else:
            record = {}
        record.setdefault("packet_id", item.get("packet_id") or item.get("current_packet") or selected)
        record.setdefault("title", item.get("title"))
        record.setdefault("lane", item.get("lane"))
        record.setdefault("status", item.get("status") or item.get("validation_status") or item.get("packet_status"))
        record["source"] = "cycle_ledger_history"
        records.append(record)
    return records


def _manual_rules(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    for item in _as_items(payload.get("manual_suppression_rules")):
        if isinstance(item, dict):
            rules.append(item)
        else:
            rules.append({"packet_id": str(item)})
    return rules


def _completed_packet_ids(records: list[dict[str, Any]], cycle_records: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for record in [*records, *cycle_records]:
        packet_id = _packet_id(record)
        if packet_id and packet_id not in ids:
            ids.append(packet_id)
    return ids


def _files_are_new(candidate: dict[str, Any], memory_record: dict[str, Any]) -> bool:
    candidate_files = {_normalized_path(path) for path in _required_files(candidate)}
    memory_files = {_normalized_path(path) for path in _required_files(memory_record)}
    if not candidate_files or not memory_files:
        return False
    return not candidate_files.issubset(memory_files)


def _title_or_lane_matches(candidate: dict[str, Any], memory_record: dict[str, Any]) -> bool:
    candidate_title = _normalized(_record_title(candidate))
    candidate_lane = _normalized(_record_lane(candidate))
    memory_title = _normalized(_record_title(memory_record))
    memory_lane = _normalized(_record_lane(memory_record))
    return bool(
        (candidate_title and candidate_title == memory_title)
        or (candidate_lane and candidate_lane == memory_lane)
    )


def _write_scope_matches(candidate: dict[str, Any], memory_record: dict[str, Any]) -> bool:
    candidate_files = {_normalized_path(path) for path in _required_files(candidate)}
    memory_files = {_normalized_path(path) for path in _required_files(memory_record)}
    if not candidate_files or not memory_files:
        return False
    return candidate_files.issubset(memory_files)


def _is_reopened(candidate: dict[str, Any]) -> bool:
    status = _normalized(candidate.get("status"))
    return (
        candidate.get("reopened") is True
        or candidate.get("explicitly_reopened") is True
        or status in REOPENED_STATUSES
    )


def _is_validation_repair(candidate: dict[str, Any]) -> bool:
    status = _normalized(candidate.get("status"))
    validation_status = _normalized(candidate.get("validation_status"))
    return (
        candidate.get("validation_failed") is True
        or status in REPAIR_STATUSES
        or validation_status in {"failed", "fail", "validation_failed"}
    )


def _is_forex_scaffold(candidate: dict[str, Any]) -> bool:
    text = " ".join(
        [
            _packet_id(candidate),
            _record_title(candidate),
            _record_lane(candidate),
            " ".join(_as_text_list(candidate.get("tags"))),
        ]
    ).lower()
    return "forex" in text and "scaffold" in text


def _cycle_record_is_complete(record: dict[str, Any]) -> bool:
    status_values = [
        record.get("status"),
        record.get("validation_status"),
        record.get("packet_status"),
        record.get("pr_status"),
        record.get("checks_status"),
    ]
    return any(_normalized(value) in COMPLETE_STATUSES for value in status_values)


def _manual_rule_matches(candidate: dict[str, Any], rule: dict[str, Any]) -> bool:
    candidate_id = _packet_id(candidate)
    candidate_lane = _normalized(_record_lane(candidate))
    rule_id = _text(rule.get("packet_id") or rule.get("id"))
    rule_lane = _normalized(rule.get("lane"))
    return bool(
        (rule_id and rule_id == candidate_id)
        or (rule_lane and rule_lane == candidate_lane)
    )


def _suppression_reasons(
    candidate: dict[str, Any],
    memory_records: list[dict[str, Any]],
    cycle_records: list[dict[str, Any]],
    manual_rules: list[dict[str, Any]],
) -> list[str]:
    if _is_reopened(candidate) or _is_validation_repair(candidate) or _is_forex_scaffold(candidate):
        return []

    reasons: list[str] = []
    candidate_id = _packet_id(candidate)
    for record in memory_records:
        if _files_are_new(candidate, record):
            continue
        record_id = _packet_id(record)
        source = _text(record.get("source"), "memory")
        if candidate_id and record_id and candidate_id == record_id:
            reasons.append(f"completed_packet_id:{candidate_id}")
        if source == "landed_prs" and _title_or_lane_matches(candidate, record):
            reasons.append(f"landed_pr_match:{_record_title(record) or _record_lane(record)}")
        if _write_scope_matches(candidate, record) and (_record_lane(candidate) == _record_lane(record) or record_id):
            reasons.append(f"completed_write_scope_match:{source}")
        if source == "commit_history_summary" and _title_or_lane_matches(candidate, record):
            reasons.append(f"commit_history_match:{_record_title(record) or _record_lane(record)}")

    for rule in manual_rules:
        if _manual_rule_matches(candidate, rule):
            reasons.append(f"manual_suppression_rule:{_text(rule.get('reason'), 'matched')}")

    for record in cycle_records:
        if not _cycle_record_is_complete(record):
            continue
        if candidate_id and _packet_id(record) == candidate_id:
            reasons.append(f"cycle_ledger_complete:{candidate_id}")
        elif _title_or_lane_matches(candidate, record):
            reasons.append(f"cycle_ledger_complete:{_record_title(record) or _record_lane(record)}")

    unique: list[str] = []
    for reason in reasons:
        if reason and reason not in unique:
            unique.append(reason)
    return unique


def _alignment() -> dict[str, Any]:
    return {
        "milestone": FOREX_MILESTONE,
        "proof_target": "industrial-grade forex bot builder",
        "control_plane_role": "completed packet memory and candidate suppression",
        "aligned": True,
        "blocked_boundaries": [],
        "requires_future_gates_before_execution": True,
    }


def _next_safe_action(status: str, next_available: bool) -> str:
    if status == "empty":
        return "Add candidate packet evidence before applying completed packet memory."
    if next_available:
        return "Feed active candidates to the packet queue planner; do not mutate queues from memory suppression."
    return "All provided candidates are suppressed; provide the next unfinished self-build or forex-builder candidate."


def build_completed_packet_memory(raw_evidence: Any | None = None) -> dict[str, Any]:
    payload = _as_dict(raw_evidence)
    candidates = _candidate_list(raw_evidence)
    memory_records = _completed_memory_records(payload)
    cycle_records = _cycle_ledger_records(payload)
    manual_rules = _manual_rules(payload)
    completed_ids = _completed_packet_ids(memory_records, cycle_records)

    active_candidates: list[dict[str, Any]] = []
    suppressed_candidates: list[dict[str, Any]] = []
    suppression_reasons: dict[str, list[str]] = {}

    for candidate in candidates:
        packet_id = _packet_id(candidate) or _record_title(candidate) or "unknown_candidate"
        reasons = _suppression_reasons(candidate, memory_records, cycle_records, manual_rules)
        if reasons:
            suppressed_candidates.append(
                {
                    "candidate": candidate,
                    "packet_id": packet_id,
                    "suppression_reasons": reasons,
                }
            )
            suppression_reasons[packet_id] = reasons
        else:
            active_candidates.append(candidate)

    status = "empty" if not candidates else "ready"
    next_candidate = active_candidates[0] if active_candidates else None

    return {
        "schema": SCHEMA,
        "suppression_status": status,
        "active_candidates": active_candidates,
        "suppressed_candidates": suppressed_candidates,
        "completed_packet_ids": completed_ids,
        "suppression_reasons": suppression_reasons,
        "next_candidate_available": next_candidate is not None,
        "next_candidate": next_candidate,
        "memory_source": {
            "default_completed_memory_count": len(DEFAULT_COMPLETED_PACKETS),
            "completed_packet_ids_count": len(_as_items(payload.get("completed_packet_ids"))),
            "landed_prs_count": len(_as_items(payload.get("landed_prs"))),
            "commit_history_summary_count": len(_as_items(payload.get("commit_history_summary"))),
            "cycle_ledger_history_count": len(_as_items(payload.get("cycle_ledger_history"))),
            "manual_suppression_rules_count": len(manual_rules),
        },
        "forex_builder_alignment": _alignment(),
        "commands_executed": [],
        "files_written": [],
        "workers_dispatched": False,
        "queues_mutated": False,
        "approvals_mutated": False,
        "safety": _safety(),
        "next_safe_action": _next_safe_action(status, next_candidate is not None),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Suppress completed AIOS candidate packets.")
    parser.add_argument("--evidence", default="{}", help="JSON candidate and completed packet evidence.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = json.loads(args.evidence)
    except json.JSONDecodeError:
        evidence = {}
    result = build_completed_packet_memory(evidence)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
