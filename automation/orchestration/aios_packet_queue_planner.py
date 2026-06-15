from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_PACKET_QUEUE_PLANNER.v1"

READY_STATUSES = {
    "",
    "candidate",
    "open",
    "pending",
    "queued",
    "ready",
    "proposed",
    "waiting",
}
BLOCKED_STATUSES = {
    "blocked",
    "deferred",
    "hold",
    "paused",
    "waiting_approval",
    "waiting_for_approval",
}
REJECTED_STATUSES = {
    "rejected",
    "cancelled",
    "canceled",
    "unsafe",
    "invalid",
}
DONE_STATUSES = {
    "complete",
    "completed",
    "done",
    "closed",
}

PRIORITY_SCORES = {
    "critical": 500,
    "urgent": 450,
    "high": 400,
    "medium": 300,
    "normal": 200,
    "low": 100,
}
SAFE_RISK_LEVELS = {"", "none", "safe", "low", "medium", "bounded", "preview"}
UNSAFE_RISK_LEVELS = {"high", "critical", "unsafe", "production", "live", "unbounded"}

PROTECTED_APPROVAL_TERMS = (
    "protected",
    "commit",
    "push",
    "merge",
    "reset",
    "delete",
    "branch deletion",
    "approval mutation",
    "queue mutation",
    "worker dispatch",
    "scheduler",
    "daemon",
    "broker",
    "live trading",
    "credential",
    "secret",
)
SAFE_SAFETY_FLAGS = {
    "",
    "none",
    "safe",
    "preview_only",
    "preview-only",
    "evidence_only",
    "evidence-only",
    "no_high_risk",
    "no high risk",
}
REJECTING_SAFETY_TERMS = (
    "broker",
    "live",
    "credential",
    "secret",
    "token",
    "webhook",
    "order",
)


def _safety() -> dict[str, bool]:
    return {
        "preview_only": True,
        "evidence_only": True,
        "packet_execution": False,
        "codex_launch": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "reports_written": False,
        "network_access": False,
        "git_commit": False,
        "git_push": False,
        "git_merge": False,
        "branch_deletion": False,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_items(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        parts = value.replace("\r", "\n").replace(",", "\n").splitlines()
        return [part.strip() for part in parts if part.strip()]
    if value in (None, "", {}, []):
        return []
    return [value]


def _as_text_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _as_items(value) if str(item).strip()]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _text(value).lower().replace("-", "_").replace(" ", "_")


def _candidate_list(evidence: Any) -> list[dict[str, Any]]:
    if isinstance(evidence, list):
        return [item for item in evidence if isinstance(item, dict)]
    if isinstance(evidence, dict):
        for key in ("candidates", "candidate_packets", "packets"):
            value = evidence.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if evidence.get("packet_id"):
            return [evidence]
    return []


def _numeric_score(value: Any, fallback: float = 0.0) -> float:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        try:
            return float(stripped)
        except ValueError:
            return fallback
    return fallback


def _priority_score(value: Any) -> float:
    normalized = _normalized(value)
    if normalized in PRIORITY_SCORES:
        return float(PRIORITY_SCORES[normalized])
    return _numeric_score(value, fallback=0.0)


def _rank_score(candidate: dict[str, Any]) -> float:
    priority = _priority_score(candidate.get("priority"))
    milestone = _numeric_score(candidate.get("milestone_value"), fallback=0.0)
    return priority * 1000.0 + milestone


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip().lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def _paths_overlap(left: str, right: str) -> bool:
    first = _normalize_path(left)
    second = _normalize_path(right)
    if not first or not second:
        return False
    return first == second or first.startswith(second + "/") or second.startswith(first + "/")


def _own_file_collisions(required_files: list[str], blocked_files: list[str]) -> list[str]:
    collisions: list[str] = []
    for required in required_files:
        for blocked in blocked_files:
            if _paths_overlap(required, blocked):
                collisions.append(required)
                break
    return collisions


def _missing_dependencies(value: Any) -> list[str]:
    missing: list[str] = []
    for dependency in _as_items(value):
        if isinstance(dependency, dict):
            dep_id = _text(
                dependency.get("packet_id")
                or dependency.get("id")
                or dependency.get("title")
                or "unnamed_dependency"
            )
            satisfied = dependency.get("satisfied") is True
            status = _normalized(dependency.get("status"))
            if status in {"satisfied", "complete", "completed", "done", "passed"}:
                satisfied = True
            if not satisfied:
                missing.append(dep_id)
        else:
            missing.append(str(dependency).strip())
    return [item for item in missing if item]


def _unsafe_safety_flags(value: Any) -> tuple[list[str], bool]:
    unsafe: list[str] = []
    rejected = False
    if isinstance(value, dict):
        entries = [str(key) for key, flag in value.items() if bool(flag)]
    else:
        entries = _as_text_list(value)

    for entry in entries:
        normalized = _normalized(entry)
        if normalized in SAFE_SAFETY_FLAGS:
            continue
        unsafe.append(entry)
        lower = entry.lower()
        if any(term in lower for term in REJECTING_SAFETY_TERMS):
            rejected = True
    return unsafe, rejected


def _approval_reasons(value: Any) -> tuple[list[str], list[str]]:
    approvals = _as_text_list(value)
    protected: list[str] = []
    for approval in approvals:
        lower = approval.lower()
        if any(term in lower for term in PROTECTED_APPROVAL_TERMS):
            protected.append(approval)
    if approvals and not protected:
        protected.extend(approvals)
    return approvals, protected


def _evaluate_candidate(candidate: dict[str, Any], index: int) -> dict[str, Any]:
    packet_id = _text(candidate.get("packet_id")) or f"candidate_{index + 1}"
    required_files = _as_text_list(candidate.get("required_files"))
    blocked_files = _as_text_list(candidate.get("blocked_files"))
    approvals, protected_approvals = _approval_reasons(candidate.get("required_approvals"))
    dependencies_missing = _missing_dependencies(candidate.get("dependencies"))
    conflicts = _as_text_list(candidate.get("conflicts"))
    unsafe_flags, flags_rejected = _unsafe_safety_flags(candidate.get("safety_flags"))
    risk_level = _normalized(candidate.get("risk_level"))
    status = _normalized(candidate.get("status"))

    blocked_reasons: list[str] = []
    rejected_reasons: list[str] = []

    if status in REJECTED_STATUSES:
        rejected_reasons.append(f"packet_status_rejected:{status}")
    elif status in BLOCKED_STATUSES:
        blocked_reasons.append(f"packet_status_blocked:{status}")
    elif status in DONE_STATUSES:
        blocked_reasons.append(f"packet_status_not_candidate:{status}")
    elif status not in READY_STATUSES:
        blocked_reasons.append(f"packet_status_unknown:{status or 'missing'}")

    if not packet_id:
        blocked_reasons.append("packet_id_missing")
    if not required_files:
        blocked_reasons.append("required_files_missing")
    if risk_level in UNSAFE_RISK_LEVELS:
        rejected_reasons.append(f"unsafe_risk_level:{risk_level}")
    elif risk_level not in SAFE_RISK_LEVELS:
        blocked_reasons.append(f"unknown_risk_level:{risk_level or 'missing'}")

    if protected_approvals:
        blocked_reasons.append("protected_approval_required:" + ",".join(protected_approvals))
    if dependencies_missing:
        blocked_reasons.append("dependencies_missing:" + ",".join(dependencies_missing))
    if conflicts:
        blocked_reasons.append("declared_conflicts:" + ",".join(conflicts))
    for collision in _own_file_collisions(required_files, blocked_files):
        blocked_reasons.append(f"blocked_file_collision:{collision}")
    if unsafe_flags:
        reason = "unsafe_safety_flags:" + ",".join(unsafe_flags)
        if flags_rejected:
            rejected_reasons.append(reason)
        else:
            blocked_reasons.append(reason)

    candidate_status = "eligible"
    if rejected_reasons:
        candidate_status = "rejected"
    elif blocked_reasons:
        candidate_status = "blocked"

    return {
        "packet_id": packet_id,
        "title": _text(candidate.get("title")),
        "lane": _text(candidate.get("lane")),
        "priority": candidate.get("priority"),
        "milestone_value": candidate.get("milestone_value"),
        "risk_level": _text(candidate.get("risk_level")),
        "status": _text(candidate.get("status")),
        "required_files": required_files,
        "blocked_files": blocked_files,
        "required_approvals": approvals,
        "validators": _as_text_list(candidate.get("validators")),
        "dependencies": _as_items(candidate.get("dependencies")),
        "conflicts": conflicts,
        "safety_flags": candidate.get("safety_flags", []),
        "rank_score": _rank_score(candidate),
        "candidate_status": candidate_status,
        "blocked_reasons": [*rejected_reasons, *blocked_reasons],
    }


def _apply_candidate_file_collisions(
    evaluated: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    collisions: list[dict[str, str]] = []
    owners: list[tuple[str, str]] = []
    ordered = sorted(evaluated, key=lambda item: (-float(item["rank_score"]), item["packet_id"]))

    for item in ordered:
        if item["candidate_status"] != "eligible":
            continue
        item_files = [str(path) for path in item.get("required_files", [])]
        collided = False
        for required in item_files:
            for owner_file, owner_packet in owners:
                if _paths_overlap(required, owner_file):
                    reason = f"file_collision:{required} with {owner_packet}"
                    item["blocked_reasons"].append(reason)
                    item["candidate_status"] = "blocked"
                    collisions.append(
                        {
                            "packet_id": str(item["packet_id"]),
                            "conflicting_packet_id": owner_packet,
                            "file": required,
                        }
                    )
                    collided = True
                    break
            if collided:
                break
        if not collided:
            owners.extend((path, str(item["packet_id"])) for path in item_files)

    return ordered, collisions


def _blocked_packet_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": item["packet_id"],
        "title": item["title"],
        "lane": item["lane"],
        "candidate_status": item["candidate_status"],
        "blocked_reasons": item["blocked_reasons"],
    }


def _selected_packet_summary(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return {
        "packet_id": item["packet_id"],
        "title": item["title"],
        "lane": item["lane"],
        "priority": item["priority"],
        "milestone_value": item["milestone_value"],
        "risk_level": item["risk_level"],
        "status": item["status"],
        "required_files": item["required_files"],
        "blocked_files": item["blocked_files"],
        "required_approvals": item["required_approvals"],
        "validators": item["validators"],
        "dependencies": item["dependencies"],
        "conflicts": item["conflicts"],
        "safety_flags": item["safety_flags"],
    }


def _codex_packet_preview(item: dict[str, Any] | None) -> dict[str, Any]:
    if item is None:
        return {
            "packet_ready": False,
            "reason_code": "no_selected_packet",
            "packet_id": None,
            "codex_prompt_text": "",
            "write_scope": [],
            "validator_chain": [],
        }

    validators = [str(command) for command in item.get("validators", [])]
    validation_lines = validators or ["No validators supplied in packet evidence. Stop and add validators."]
    title = str(item.get("title") or item["packet_id"])
    lane = str(item.get("lane") or "packet-queue-selected")
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
            "WORKER IDENTITY: CODEX_PACKET_QUEUE_SELECTED_WORKER",
            f"LANE: {lane}",
            "APPROVAL AUTHORITY: Anthony Meza approves local scoped APPLY edits only.",
            "MODE: APPLY",
            "WORKTREE: C:\\Dev\\Ai.Os",
            "BRANCH: main",
            f"PACKET ID: {item['packet_id']}",
            "",
            "MISSION:",
            title,
            "",
            "WRITE ONLY:",
            *[str(path) for path in item.get("required_files", [])],
            "",
            "RULES:",
            "No worker dispatch.",
            "No queue mutation.",
            "No approval mutation.",
            "No scheduler.",
            "No daemon.",
            "No commit.",
            "No push.",
            "No merge.",
            "",
            "VALIDATION:",
            *validation_lines,
            "",
            "STOP:",
            "Report only. No staging. No commit. No push.",
        ]
    )
    return {
        "packet_ready": bool(validators),
        "reason_code": "packet_ready" if validators else "validators_missing",
        "packet_id": item["packet_id"],
        "codex_prompt_text": prompt,
        "write_scope": item.get("required_files", []),
        "validator_chain": validators,
    }


def _next_safe_action(queue_status: str, selected: dict[str, Any] | None) -> str:
    if queue_status == "selected" and selected is not None:
        return (
            f"Review the Codex-ready preview for {selected['packet_id']}; "
            "do not dispatch or mutate queues from this planner."
        )
    if queue_status == "empty":
        return "Add candidate packet evidence before planning queue selection."
    if queue_status == "rejected":
        return "Stop and repair rejected candidate evidence before selecting a packet."
    return "Resolve blocked packet evidence, collisions, approvals, or dependencies, then rerun the planner."


def build_packet_queue_planner(candidate_evidence: Any) -> dict[str, Any]:
    candidates = _candidate_list(candidate_evidence)
    if not candidates:
        return {
            "schema": SCHEMA,
            "queue_status": "empty",
            "selected_packet": None,
            "ranked_packets": [],
            "blocked_packets": [],
            "collision_status": {"status": "clear", "collisions": []},
            "required_approvals": [],
            "next_safe_action": _next_safe_action("empty", None),
            "codex_ready_packet_preview": _codex_packet_preview(None),
            "commands_executed": [],
            "workers_dispatched": False,
            "queues_mutated": False,
            "approvals_mutated": False,
            "files_written": [],
            "safety": _safety(),
        }

    evaluated = [_evaluate_candidate(candidate, index) for index, candidate in enumerate(candidates)]
    ranked_packets, collisions = _apply_candidate_file_collisions(evaluated)
    eligible = [item for item in ranked_packets if item["candidate_status"] == "eligible"]
    selected = eligible[0] if eligible else None
    blocked_packets = [
        _blocked_packet_summary(item)
        for item in ranked_packets
        if item["candidate_status"] in {"blocked", "rejected"}
    ]

    if selected is not None:
        queue_status = "selected"
    elif all(item["candidate_status"] == "rejected" for item in ranked_packets):
        queue_status = "rejected"
    else:
        queue_status = "blocked"

    required_approvals: list[str] = []
    for item in ranked_packets:
        for approval in item.get("required_approvals", []):
            approval_text = str(approval)
            if approval_text not in required_approvals:
                required_approvals.append(approval_text)

    collision_status = {
        "status": "blocked" if collisions else "clear",
        "collisions": collisions,
    }

    ranked_summary = [
        {
            "packet_id": item["packet_id"],
            "title": item["title"],
            "lane": item["lane"],
            "priority": item["priority"],
            "milestone_value": item["milestone_value"],
            "risk_level": item["risk_level"],
            "status": item["status"],
            "rank_score": item["rank_score"],
            "candidate_status": item["candidate_status"],
            "blocked_reasons": item["blocked_reasons"],
        }
        for item in ranked_packets
    ]

    selected_summary = _selected_packet_summary(selected)
    return {
        "schema": SCHEMA,
        "queue_status": queue_status,
        "selected_packet": selected_summary,
        "ranked_packets": ranked_summary,
        "blocked_packets": blocked_packets,
        "collision_status": collision_status,
        "required_approvals": required_approvals,
        "next_safe_action": _next_safe_action(queue_status, selected_summary),
        "codex_ready_packet_preview": _codex_packet_preview(selected),
        "commands_executed": [],
        "workers_dispatched": False,
        "queues_mutated": False,
        "approvals_mutated": False,
        "files_written": [],
        "safety": _safety(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview AIOS packet queue selection.")
    parser.add_argument("--candidates", default="[]", help="JSON candidate packet evidence.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = json.loads(args.candidates)
    except json.JSONDecodeError:
        evidence = []
    result = build_packet_queue_planner(evidence)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
