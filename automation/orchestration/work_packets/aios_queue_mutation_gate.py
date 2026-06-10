"""AI_OS queue mutation gate preview.

This module validates whether a proposed item is shaped well enough for a
future approved write to the canonical queue owner:
automation/orchestration/work_packets/active/.

It is DRY_RUN-only. It writes preview evidence under Reports/queue_mutation_gate
and never writes to the canonical queue, worker inbox, approval inbox, command
queue, telemetry, runtime, scheduler, SOS, services, apps, or trading paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_QUEUE_MUTATION_GATE_PREVIEW.v1"
MODE = "DRY_RUN_PREVIEW_ONLY"
READY = "READY_FOR_HUMAN_REVIEW"
BLOCKED = "BLOCKED"
INVALID = "INVALID"

CANONICAL_QUEUE_OWNER = "automation/orchestration/work_packets/active/"
DEFAULT_REPORT_DIR = Path("Reports/queue_mutation_gate")
DEFAULT_P2_PREVIEW = Path("Reports/p2_enqueue_bridge/p2_enqueue_bridge_preview.json")
DEFAULT_APPROVAL_GATE = Path("automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json")
DEFAULT_APPROVAL_INBOX = Path("automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json")

PROTECTED_PATH_PREFIXES = (
    ".github/",
    "AGENTS.md",
    "README.md",
    "docs/governance/",
    "docs/workflows/",
    "docs/security/",
    "automation/orchestration/work_packets/active/",
    "automation/orchestration/work_packets/blocked/",
    "automation/orchestration/work_packets/complete/",
    "automation/orchestration/workers/inbox/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/command_queue/",
    "telemetry/",
    "services/",
    "apps/",
    "aios/modules/trader/",
    "aios.ps1",
)

UNSAFE_ACTION_TERMS = (
    "scheduler",
    "sos",
    "runtime execution",
    "runtime launch",
    "dispatch",
    "enqueue",
    "dequeue",
    "live trading",
    "broker",
    "credential",
    "secret",
)

ACTION_KEYS = {
    "action",
    "actions",
    "requested_action",
    "requested_actions",
    "command",
    "commands",
    "execution_plan",
    "runtime_action",
    "operator_action",
}

APPROVED_STATUSES = {"approved_for_apply", "approved"}


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _path_hash(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint_path(path: Path) -> dict[str, Any]:
    if path.is_dir():
        files = []
        for child in sorted(path.rglob("*")):
            if child.is_file():
                files.append(
                    {
                        "path": child.relative_to(path).as_posix(),
                        "size": child.stat().st_size,
                        "sha256": _path_hash(child),
                    }
                )
        return {"exists": True, "is_dir": True, "path": path.as_posix(), "files": files}
    return {
        "exists": path.exists(),
        "is_dir": False,
        "path": path.as_posix(),
        "size": path.stat().st_size if path.exists() else None,
        "sha256": _path_hash(path),
    }


def _normalize_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _path_matches_prefix(path_text: str, protected_prefix: str) -> bool:
    path_norm = _normalize_path(path_text).lower().rstrip("/")
    prefix_norm = _normalize_path(protected_prefix).lower().rstrip("/")
    return path_norm == prefix_norm or path_norm.startswith(prefix_norm + "/")


def _list_from_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _first_non_empty(mapping: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        value = mapping.get(name)
        if value not in (None, "", []):
            return value
    return None


def _extract_nested_preview(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    nested = payload.get("proposed_queue_item_preview")
    if isinstance(nested, dict):
        return nested, payload
    return payload, {}


def load_proposed_queue_item(
    repo_root: str | Path = ".",
    proposed_item_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(proposed_item_path) if proposed_item_path else root / DEFAULT_P2_PREVIEW
    if not source_path.is_absolute():
        source_path = root / source_path
    payload = _read_json(source_path)
    if payload is None:
        return {
            "source_path": source_path.as_posix(),
            "source_loaded": False,
            "item": {},
            "context": {},
        }
    item, context = _extract_nested_preview(payload)
    return {
        "source_path": source_path.as_posix(),
        "source_loaded": True,
        "item": item,
        "context": context,
    }


def _approval_evidence(item: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    for key in ("approval_evidence", "approval", "approval_context"):
        value = item.get(key)
        if isinstance(value, dict):
            return value

    evidence: dict[str, Any] = {}
    for source in (item, context):
        for key in ("approval_status", "approved_by_human", "approval_granted", "approval_authority", "approved_by"):
            if key in source:
                evidence[key] = source[key]
    return evidence


def _normalize_proposed_item(item: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    approval = _approval_evidence(item, context)
    packet_id = _first_non_empty(item, ("packet_id", "id", "preview_id"))
    lane = _first_non_empty(item, ("lane", "lane_id", "lane_name"))
    mode = _first_non_empty(item, ("mode", "requested_mode"))

    allowed_paths = _list_from_value(
        _first_non_empty(item, ("allowed_paths", "allowed_path", "target_allowed_paths"))
    )
    forbidden_paths = _list_from_value(
        _first_non_empty(item, ("forbidden_paths", "blocked_paths", "blocked_path"))
    )
    target_paths = []
    for key in ("target_paths", "write_paths", "paths", "files", "changed_files"):
        target_paths.extend(_list_from_value(item.get(key)))

    return {
        "packet_id": str(packet_id).strip() if packet_id is not None else "",
        "mode": str(mode).strip() if mode is not None else "",
        "lane": str(lane).strip() if lane is not None else "",
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "target_paths": target_paths,
        "approval_evidence": approval,
        "raw_item": item,
    }


def _approval_is_explicit(evidence: dict[str, Any]) -> bool:
    if not evidence:
        return False
    status = str(evidence.get("approval_status") or evidence.get("status") or "").strip().lower()
    human = evidence.get("approved_by_human") is True or evidence.get("approval_granted") is True
    authority = str(evidence.get("approval_authority") or evidence.get("approved_by") or "").strip()
    return status in APPROVED_STATUSES and human and bool(authority)


def _active_packet_matches(active_dir: Path, packet_id: str) -> list[str]:
    if not packet_id or not active_dir.exists():
        return []
    matches = []
    expected_name = f"{packet_id}.json".lower()
    for path in sorted(active_dir.glob("*.json")):
        if path.name.lower() == expected_name:
            matches.append(path.as_posix())
            continue
        payload = _read_json(path)
        if not payload:
            continue
        observed = str(payload.get("packet_id") or payload.get("id") or "").strip()
        if observed == packet_id:
            matches.append(path.as_posix())
    return matches


def _targeted_protected_paths(normalized: dict[str, Any]) -> list[str]:
    targeted = list(normalized["allowed_paths"]) + list(normalized["target_paths"])
    protected = []
    for path_text in targeted:
        for prefix in PROTECTED_PATH_PREFIXES:
            if _path_matches_prefix(path_text, prefix):
                protected.append(path_text)
                break
    return sorted(set(protected))


def _collect_action_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        text: list[str] = []
        for item in value:
            text.extend(_collect_action_text(item))
        return text
    if isinstance(value, dict):
        text = []
        for key, nested in value.items():
            if str(key).lower() in ACTION_KEYS:
                text.extend(_collect_action_text(nested))
        return text
    return []


def _unsafe_action_terms(item: dict[str, Any]) -> list[str]:
    text = " ".join(_collect_action_text(item)).lower()
    return [term for term in UNSAFE_ACTION_TERMS if term in text]


def _required_field_invalids(normalized: dict[str, Any]) -> list[str]:
    invalids = []
    for field in ("packet_id", "mode", "lane"):
        if not normalized[field]:
            invalids.append(f"{field} is required")
    if not normalized["allowed_paths"]:
        invalids.append("allowed_paths is required")
    if not normalized["forbidden_paths"]:
        invalids.append("forbidden_paths is required")
    return invalids


def build_queue_mutation_gate_preview(
    repo_root: str | Path = ".",
    proposed_item_path: str | Path | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    active_dir = root / CANONICAL_QUEUE_OWNER
    loaded = load_proposed_queue_item(root, proposed_item_path)
    item = loaded["item"] if isinstance(loaded["item"], dict) else {}
    context = loaded["context"] if isinstance(loaded["context"], dict) else {}
    normalized = _normalize_proposed_item(item, context)

    approval_gate_path = root / DEFAULT_APPROVAL_GATE
    approval_inbox_path = root / DEFAULT_APPROVAL_INBOX
    approval_evidence = normalized["approval_evidence"]
    explicit_approval = _approval_is_explicit(approval_evidence)
    duplicate_paths = _active_packet_matches(active_dir, normalized["packet_id"])
    protected_paths = _targeted_protected_paths(normalized)
    unsafe_terms = _unsafe_action_terms(item)
    invalid_reasons = _required_field_invalids(normalized)

    blockers = []
    if not loaded["source_loaded"]:
        invalid_reasons.append("proposed queue item source was not found or not valid JSON")
    if not approval_evidence:
        blockers.append("approval evidence is missing")
    elif not explicit_approval:
        blockers.append("approval evidence is not explicit")
    if duplicate_paths:
        blockers.append("duplicate active packet ID would be created")
    if protected_paths:
        blockers.append("proposed item targets protected paths")
    if unsafe_terms:
        blockers.append("proposed item requests blocked actions")

    gate_status = INVALID if invalid_reasons else BLOCKED if blockers else READY
    if gate_status == READY:
        safe_next_action = "Human reviews this preview; a separate approved APPLY gate is still required before any real queue write."
    elif gate_status == BLOCKED:
        safe_next_action = "Resolve queue mutation blockers before requesting a real queue write."
    else:
        safe_next_action = "Repair the proposed queue item shape before review."

    report = {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": _now(now),
        "repo_root": root.as_posix(),
        "gate_status": gate_status,
        "gate_status_reason": "; ".join(invalid_reasons or blockers or ["proposal is ready for human review"]),
        "canonical_queue_owner": CANONICAL_QUEUE_OWNER,
        "future_write_target": CANONICAL_QUEUE_OWNER,
        "queue_write_allowed": False,
        "canonical_queue_mutated": False,
        "worker_inbox_mutation_allowed": False,
        "approval_inbox_mutation_allowed": False,
        "command_queue_mutation_allowed": False,
        "telemetry_mutation_allowed": False,
        "runtime_launch_allowed": False,
        "runtime_execution_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "dispatch_allowed": False,
        "enqueue_allowed": False,
        "dequeue_allowed": False,
        "credentials_accessed": False,
        "proposed_item_source": {
            "path": loaded["source_path"],
            "loaded": loaded["source_loaded"],
        },
        "proposed_queue_item": {
            "packet_id": normalized["packet_id"],
            "mode": normalized["mode"],
            "lane": normalized["lane"],
            "allowed_paths": normalized["allowed_paths"],
            "forbidden_paths": normalized["forbidden_paths"],
            "target_paths": normalized["target_paths"],
        },
        "approval_check": {
            "approval_evidence_present": bool(approval_evidence),
            "explicit_approval": explicit_approval,
            "approved_statuses": sorted(APPROVED_STATUSES),
            "active_approval_gate_present": approval_gate_path.exists(),
            "active_approval_inbox_present": approval_inbox_path.exists(),
        },
        "duplicate_check": {
            "active_queue_path": active_dir.as_posix(),
            "duplicate_packet_id": bool(duplicate_paths),
            "matching_active_packet_paths": duplicate_paths,
        },
        "protected_path_check": {
            "protected_path_targeted": bool(protected_paths),
            "targeted_protected_paths": protected_paths,
        },
        "unsafe_action_check": {
            "unsafe_action_requested": bool(unsafe_terms),
            "matched_terms": unsafe_terms,
        },
        "source_fingerprints": {
            "active_queue": _fingerprint_path(active_dir),
            "worker_inbox": _fingerprint_path(root / "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"),
            "approval_gate": _fingerprint_path(approval_gate_path),
            "approval_inbox": _fingerprint_path(approval_inbox_path),
            "command_queue": _fingerprint_path(root / "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"),
        },
        "validation": {
            "status": "PASS" if gate_status in {READY, BLOCKED, INVALID} else "FAIL",
            "checked_fields": [
                "packet_id",
                "mode",
                "lane",
                "allowed_paths",
                "forbidden_paths",
                "approval_evidence",
                "explicit_approval",
                "duplicate_active_packet_id",
                "protected_paths",
                "unsafe_actions",
            ],
            "invalid_reasons": invalid_reasons,
            "blockers": blockers,
        },
        "safe_next_action": safe_next_action,
        "stop_condition": "Stop before writing to the real active queue, worker inbox, approval inbox, command queue, telemetry, runtime, scheduler, SOS, services, apps, or trading paths.",
    }
    return report


def build_queue_mutation_gate_markdown(report: dict[str, Any]) -> str:
    validation = report.get("validation", {})
    proposed = report.get("proposed_queue_item", {})
    lines = [
        "# AI_OS Queue Mutation Gate Preview",
        "",
        f"- gate_status: `{report.get('gate_status')}`",
        f"- canonical_queue_owner: `{report.get('canonical_queue_owner')}`",
        f"- packet_id: `{proposed.get('packet_id')}`",
        f"- queue_write_allowed: `{report.get('queue_write_allowed')}`",
        f"- canonical_queue_mutated: `{report.get('canonical_queue_mutated')}`",
        f"- validation_status: `{validation.get('status')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Invalid Reasons",
    ]
    invalids = validation.get("invalid_reasons") or []
    lines.extend([f"- {reason}" for reason in invalids] or ["- none"])
    lines.append("")
    lines.append("## Blockers")
    blockers = validation.get("blockers") or []
    lines.extend([f"- {blocker}" for blocker in blockers] or ["- none"])
    lines.append("")
    lines.append("## Stop Condition")
    lines.append(str(report.get("stop_condition")))
    lines.append("")
    return "\n".join(lines)


def write_queue_mutation_gate_reports(
    report: dict[str, Any],
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    out_dir = Path(output_dir) if output_dir else root / DEFAULT_REPORT_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    json_path = out_dir / "queue_mutation_gate_preview.json"
    summary_path = out_dir / "queue_mutation_gate_summary.md"
    report = dict(report)
    report["report_paths"] = [json_path.as_posix(), summary_path.as_posix()]
    _write_json(json_path, report)
    summary_path.write_text(build_queue_mutation_gate_markdown(report), encoding="utf-8")
    return report


def summarize_queue_mutation_gate(report: dict[str, Any]) -> dict[str, Any]:
    validation = report.get("validation") if isinstance(report.get("validation"), dict) else {}
    return {
        "schema": report.get("schema"),
        "gate_status": report.get("gate_status"),
        "canonical_queue_owner": report.get("canonical_queue_owner"),
        "packet_id": (report.get("proposed_queue_item") or {}).get("packet_id"),
        "queue_write_allowed": report.get("queue_write_allowed"),
        "canonical_queue_mutated": report.get("canonical_queue_mutated"),
        "invalid_reason_count": len(validation.get("invalid_reasons") or []),
        "blocker_count": len(validation.get("blockers") or []),
        "safe_next_action": report.get("safe_next_action"),
        "report_paths": report.get("report_paths", []),
    }


def run_queue_mutation_gate(
    *,
    repo_root: str | Path = ".",
    proposed_item_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    write_report: bool = True,
    now: str | None = None,
) -> dict[str, Any]:
    report = build_queue_mutation_gate_preview(
        repo_root=repo_root,
        proposed_item_path=proposed_item_path,
        now=now,
    )
    if write_report:
        report = write_queue_mutation_gate_reports(report, repo_root=repo_root, output_dir=output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the AI_OS queue mutation gate DRY_RUN preview.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--proposal", default=None, help="Optional proposed queue item JSON path.")
    parser.add_argument("--output-dir", default=None, help="Preview report output directory.")
    parser.add_argument("--no-write", action="store_true", help="Print preview only; do not write report files.")
    args = parser.parse_args()

    report = run_queue_mutation_gate(
        repo_root=args.repo_root,
        proposed_item_path=args.proposal,
        output_dir=args.output_dir,
        write_report=not args.no_write,
    )
    print(json.dumps(summarize_queue_mutation_gate(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
