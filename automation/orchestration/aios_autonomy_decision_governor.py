"""AI_OS Autonomy Decision Governor v1.

This module composes local control-plane evidence into one conservative
next-action decision. It starts no workers, calls no provider CLIs, uses no
network, reads no secrets, and mutates only its declared report output path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
COMPONENT = "autonomy_decision_governor"
DEFAULT_OUTPUT = Path("Reports") / "autonomy_decision_governor" / "AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json"
DEFAULT_REPO_STATE_OUTPUT = Path("Reports") / "repo_state" / "AIOS_REPO_STATE_LATEST.json"

DECISION_CATEGORIES = {
    "STATUS_RECON",
    "VALIDATOR_REPAIR",
    "QUEUE_CONSOLIDATION",
    "APPROVAL_GATE_REPAIR",
    "SELF_BUILD_LOOP_WIRING",
    "TRADING_LAB_PAPER_ONLY_IMPROVEMENT",
    "DASHBOARD_SURFACING",
    "TELEMETRY_REPORTING",
    "BLOCKED_STOP_AND_REPORT",
}
ALLOWED_LANES = {
    "READ_ONLY",
    "DRY_RUN",
    "APPLY_DOCS_ONLY",
    "APPLY_TESTS_ONLY",
    "APPLY_CODE_SAFE",
    "BLOCKED",
}
RISK_LEVELS = {"low", "medium", "high", "blocked"}
UNSAFE_SCOPE_TERMS = (
    "live trading",
    "live-trading",
    "broker execution",
    "broker",
    "oanda",
    "real webhook",
    "webhook execution",
    "real order",
    "live order",
    "credential",
    "credentials",
    "api key",
    "token",
    "secret",
    ".env",
)
BLOCKED_FILES = [
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "RISK_POLICY.md",
    "docs/governance/",
    "docs/security/",
    "services/runtime/",
    "services/dispatcher/",
    ".github/",
    ".env",
    "secrets",
    "broker",
    "OANDA",
    "webhook",
    "live trading",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json_if_exists(path: str | Path) -> Any | None:
    candidate = Path(path)
    if not candidate.is_file():
        return None
    try:
        return json.loads(candidate.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def _evidence(path: str, status: str, summary: str) -> dict[str, str]:
    normalized = status if status in {"present", "missing", "unknown"} else "unknown"
    return {"path": path, "status": normalized, "summary": summary}


def _summarize_json(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "JSON present but root is not an object."
    parts: list[str] = []
    for key in ("schema", "schema_version", "status", "mode", "component", "normalized_status"):
        value = payload.get(key)
        if value not in (None, "", [], {}):
            parts.append(f"{key}={value}")
    return "; ".join(parts) if parts else "JSON object present."


def _read_head_branch(repo_root: Path) -> tuple[str, dict[str, str]]:
    head_path = repo_root / ".git" / "HEAD"
    if not head_path.is_file():
        return "unknown", _evidence(".git/HEAD", "missing", "Git HEAD was not readable.")
    try:
        raw = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown", _evidence(".git/HEAD", "unknown", "Git HEAD could not be read.")
    branch = raw.rsplit("/", 1)[-1] if raw.startswith("ref:") else "detached"
    return branch, _evidence(".git/HEAD", "present", f"branch={branch}; dirty_state=unknown")


def _path_status(repo_root: Path, rel_path: str) -> tuple[str, Any | None, str]:
    path = repo_root / rel_path
    payload = load_json_if_exists(path)
    if payload is None:
        return "missing", None, "Missing or unreadable JSON evidence."
    return "present", payload, _summarize_json(payload)


def _load_repo_state_collector() -> Any | None:
    collector_path = Path(__file__).with_name("aios_repo_state_evidence.py")
    if not collector_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("aios_repo_state_evidence", collector_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_dirty_tree_classifier() -> Any | None:
    classifier_path = Path(__file__).parent / "continuation" / "aios_dirty_tree_classifier.py"
    if not classifier_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("aios_dirty_tree_classifier", classifier_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_preemptive_security_layer() -> Any | None:
    security_path = Path(__file__).parents[1] / "security" / "aios_preemptive_security_layer.py"
    if not security_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("aios_preemptive_security_layer", security_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_repo_state_evidence(repo_root: Path) -> tuple[dict[str, Any] | None, str, str]:
    rel_path = str(DEFAULT_REPO_STATE_OUTPUT).replace("\\", "/")
    payload = load_json_if_exists(repo_root / DEFAULT_REPO_STATE_OUTPUT)
    if isinstance(payload, dict):
        return payload, rel_path, "present"
    collector = _load_repo_state_collector()
    if collector is None:
        return None, rel_path, "missing"
    try:
        collected = collector.collect_repo_state(repo_root)
    except Exception:
        return None, rel_path, "unknown"
    return collected if isinstance(collected, dict) else None, rel_path, "unknown"


def _apply_repo_state_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        signals["repo_state"] = "unknown"
        signals["repo_state_blocked_reason"] = "repo_state_missing"
        return "Repo-state evidence is missing."

    branch = str(payload.get("branch") or "")
    quality = str(payload.get("evidence_quality") or "unknown")
    safe_for_apply = payload.get("safe_for_apply") is True
    is_clean = payload.get("is_clean")
    blocked_reason = payload.get("blocked_reason")
    signals["repo_branch"] = branch or signals.get("repo_branch", "unknown")
    signals["repo_state_evidence_quality"] = quality
    signals["repo_state_safe_for_apply"] = safe_for_apply
    signals["repo_state_blocked_reason"] = blocked_reason

    if quality == "strong" and safe_for_apply:
        signals["repo_state"] = "clean"
    elif is_clean is False:
        signals["repo_state"] = "dirty"
    else:
        signals["repo_state"] = "unknown"

    clean_text = "unknown" if is_clean is None else str(bool(is_clean)).lower()
    safe_text = str(bool(safe_for_apply)).lower()
    reason_text = str(blocked_reason or "none")
    return f"branch={branch or 'unknown'}; is_clean={clean_text}; safe_for_apply={safe_text}; blocked_reason={reason_text}; evidence_quality={quality}"


def _apply_dirty_tree_classifier_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        signals["dirty_tree_overall_classification"] = "UNKNOWN_DIRTY"
        signals["dirty_tree_safe_for_dry_run"] = False
        signals["dirty_tree_safe_for_apply"] = False
        signals["dirty_tree_sos_required"] = False
        signals["dirty_tree_protected_stop_required"] = False
        signals["dirty_tree_review_required"] = True
        signals["dirty_tree_dirty_count"] = 0
        return "Dirty tree classifier evidence is missing."

    overall = str(payload.get("overall_classification") or "UNKNOWN_DIRTY")
    dirty_count = _to_int(payload.get("dirty_count"), 0)
    safe_for_dry_run = payload.get("safe_for_dry_run") is True
    safe_for_apply = payload.get("safe_for_apply") is True
    sos_required = payload.get("sos_required") is True
    protected_stop_required = payload.get("protected_stop_required") is True
    review_required = payload.get("review_required") is True
    git_error = payload.get("git_status_error")

    signals["dirty_tree_overall_classification"] = overall
    signals["dirty_tree_safe_for_dry_run"] = safe_for_dry_run
    signals["dirty_tree_safe_for_apply"] = safe_for_apply
    signals["dirty_tree_sos_required"] = sos_required
    signals["dirty_tree_protected_stop_required"] = protected_stop_required
    signals["dirty_tree_review_required"] = review_required
    signals["dirty_tree_dirty_count"] = dirty_count

    if not git_error:
        if sos_required or protected_stop_required or review_required:
            signals["repo_state"] = "dirty"
            signals["repo_state_blocked_reason"] = overall.lower()
        elif dirty_count > 0 and safe_for_dry_run:
            signals["repo_state"] = "safe_dirty"
            signals["repo_state_blocked_reason"] = "safe_dirty_read_only"
        elif dirty_count == 0 and safe_for_apply:
            signals["repo_state"] = "clean"
            signals["repo_state_blocked_reason"] = None

    return (
        f"overall={overall}; dirty_count={dirty_count}; "
        f"safe_for_dry_run={str(safe_for_dry_run).lower()}; "
        f"safe_for_apply={str(safe_for_apply).lower()}; "
        f"sos_required={str(sos_required).lower()}; protected_stop_required={str(protected_stop_required).lower()}"
    )


def _apply_preemptive_security_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        signals["preemptive_security_state_present"] = False
        signals["preemptive_security_overall_state"] = "UNKNOWN_SECURITY_RISK"
        signals["preemptive_security_safe_for_dry_run"] = False
        signals["preemptive_security_safe_for_apply"] = False
        signals["preemptive_security_sos_required"] = False
        signals["preemptive_security_stop_required"] = True
        signals["preemptive_security_review_required"] = True
        signals["preemptive_security_event_count"] = 0
        signals["preemptive_security_boss_alert_active"] = False
        return "Preemptive security state is missing or unreadable; fail closed for mutation."

    overall = str(payload.get("overall_state") or "UNKNOWN_SECURITY_RISK")
    event_count = _to_int(payload.get("event_count"), 0)
    safe_for_dry_run = payload.get("safe_for_dry_run") is True
    safe_for_apply = payload.get("safe_for_apply") is True
    sos_required = payload.get("sos_required") is True
    stop_required = payload.get("stop_required") is True or overall in {"STOP", "UNKNOWN_SECURITY_RISK"}
    review_required = payload.get("review_required") is True or overall == "REVIEW_REQUIRED"
    boss_alert = payload.get("boss_alert") if isinstance(payload.get("boss_alert"), dict) else {}
    blocked_actions = payload.get("blocked_actions") if isinstance(payload.get("blocked_actions"), list) else []

    signals["preemptive_security_state_present"] = True
    signals["preemptive_security_overall_state"] = overall
    signals["preemptive_security_safe_for_dry_run"] = safe_for_dry_run
    signals["preemptive_security_safe_for_apply"] = safe_for_apply
    signals["preemptive_security_sos_required"] = sos_required
    signals["preemptive_security_stop_required"] = stop_required
    signals["preemptive_security_review_required"] = review_required
    signals["preemptive_security_event_count"] = event_count
    signals["preemptive_security_boss_alert_active"] = boss_alert.get("active") is True
    signals["preemptive_security_blocked_actions"] = [str(action) for action in blocked_actions]

    return (
        f"overall={overall}; event_count={event_count}; "
        f"safe_for_dry_run={str(safe_for_dry_run).lower()}; "
        f"safe_for_apply={str(safe_for_apply).lower()}; "
        f"sos_required={str(sos_required).lower()}; stop_required={str(stop_required).lower()}; "
        f"review_required={str(review_required).lower()}"
    )


def _count_files(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file())


def _contains_any_unsafe(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in UNSAFE_SCOPE_TERMS)


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, "", [], {}):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_nested(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _status_value(payload: dict[str, Any]) -> str:
    for keys in (
        ("status",),
        ("result",),
        ("validation", "status"),
        ("validator_status",),
        ("normalized_status",),
        ("runtime_gate",),
        ("supervisor_status",),
        ("night_supervisor_status",),
    ):
        value = _get_nested(payload, *keys)
        if value not in (None, "", [], {}):
            return str(value).strip().lower()
    return ""


def _collect_blockers(payload: Any) -> list[str]:
    blockers: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            lowered = str(key).lower()
            if lowered in {
                "blocker",
                "blockers",
                "blocked_actions",
                "blocked_paths",
                "remaining_blockers",
                "real_blockers",
                "governance_blockers",
                "code_blockers",
                "unsafe_flags",
            }:
                if isinstance(value, list):
                    blockers.extend(str(item) for item in value if str(item).strip())
                elif value not in (None, "", [], {}):
                    blockers.append(str(value))
            elif isinstance(value, (dict, list)):
                blockers.extend(_collect_blockers(value))
    elif isinstance(payload, list):
        for item in payload:
            blockers.extend(_collect_blockers(item))
    return sorted(set(blockers))


def _apply_validator_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        signals["validator_status"] = "missing"
        return "Validator evidence missing."
    status = _status_value(payload)
    blockers = _collect_blockers(payload)
    if blockers:
        signals["validator_blockers"] = blockers
    if status in {"fail", "failed", "error", "blocked", "review_required", "invalid"} or blockers:
        signals["validator_status"] = "failed"
    elif status in {"pass", "passed", "ok", "clean", "ready"}:
        signals["validator_status"] = "pass"
    else:
        signals["validator_status"] = "present"
    return f"validator_status={signals['validator_status']}; blocker_count={len(blockers)}"


def _apply_queue_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        signals["queue_present"] = False
        return "Queue evidence missing."
    state_counts = payload.get("state_counts") if isinstance(payload.get("state_counts"), dict) else {}
    item_count = _to_int(payload.get("item_count"), len(payload.get("items", [])) if isinstance(payload.get("items"), list) else 0)
    blocked_count = _to_int(state_counts.get("BLOCKED"), 0) + _to_int(payload.get("blocked_count"), 0)
    protected_count = _to_int(payload.get("protected_item_count"), 0)
    signals["queue_present"] = True
    signals["queue_item_count"] = item_count
    signals["queue_blocked_count"] = blocked_count
    signals["queue_protected_item_count"] = protected_count
    signals["queue_backlog_present"] = item_count > 0
    if blocked_count > 0 or protected_count > 0:
        signals["active_blockers"] = sorted(set(signals.get("active_blockers", []) + [f"queue_blocked={blocked_count}", f"queue_protected={protected_count}"]))
        signals["active_blocker_count"] = len(signals["active_blockers"])
    return f"queue_item_count={item_count}; queue_blocked_count={blocked_count}; protected_item_count={protected_count}"


def _apply_self_build_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        signals["self_build_status_present"] = False
        return "Self-build evidence missing."
    status = _status_value(payload)
    completion = str(_get_nested(payload, "evidence_bundle", "completion", "verdict") or payload.get("completion_verdict") or "").lower()
    requires_human = payload.get("requires_human") is True
    pending = (
        requires_human
        or status in {"human_required", "review_required", "wait_for_evidence", "blocked", "trust_failed"}
        or completion in {"completion_unproven", "not_evaluated", "completion_contradicted"}
    )
    signals["self_build_status_present"] = True
    signals["self_build_status"] = status or completion or "present"
    signals["self_build_pending"] = pending
    return f"self_build_status={signals['self_build_status']}; pending={str(pending).lower()}"


def _apply_autonomy_status_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        signals["autonomy_status_present"] = False
        return "Autonomy status evidence missing."
    blockers = _collect_blockers(payload)
    blocked_count = _to_int(payload.get("blocked_count"), len(blockers))
    approval_needed_count = _to_int(payload.get("approval_needed_count"), 0)
    status = _status_value(payload) or "present"
    signals["autonomy_status_present"] = True
    signals["autonomy_status"] = status
    if blockers or blocked_count > 0:
        signals["active_blockers"] = sorted(set(signals.get("active_blockers", []) + blockers + [f"autonomy_blocked_count={blocked_count}"]))
        signals["active_blocker_count"] = len(signals["active_blockers"])
    if approval_needed_count > 0:
        signals["approval_required"] = True
    return f"autonomy_status={status}; blocked_count={blocked_count}; approval_needed_count={approval_needed_count}"


def _apply_blocker_signal(signals: dict[str, Any], payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return "Blocker evidence missing."
    blockers = _collect_blockers(payload)
    status = _status_value(payload)
    if status in {"blocked", "fail", "failed"} and not blockers:
        blockers.append(status)
    if blockers:
        signals["active_blockers"] = sorted(set(signals.get("active_blockers", []) + blockers))
        signals["active_blocker_count"] = len(signals["active_blockers"])
    return f"blocker_count={len(blockers)}"


def discover_evidence(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    evidence_inputs: list[dict[str, str]] = []
    signals: dict[str, Any] = {
        "repo_state": "unknown",
        "safe_status_artifact_present": False,
        "validator_status": "unknown",
        "approval_required": False,
        "approval_status": "unknown",
        "queue_present": False,
        "queue_backlog_present": False,
        "queue_item_count": 0,
        "queue_blocked_count": 0,
        "self_build_status_present": False,
        "self_build_pending": False,
        "autonomy_status_present": False,
        "decision_output_present": False,
        "active_blockers": [],
        "active_blocker_count": 0,
        "trading_lab_paper_only_confirmed": False,
        "unsafe_scope_detected": False,
        "dirty_tree_overall_classification": "UNKNOWN_DIRTY",
        "dirty_tree_safe_for_dry_run": False,
        "dirty_tree_safe_for_apply": False,
        "dirty_tree_sos_required": False,
        "dirty_tree_protected_stop_required": False,
        "dirty_tree_review_required": False,
        "dirty_tree_dirty_count": 0,
        "preemptive_security_state_present": False,
        "preemptive_security_overall_state": "UNKNOWN",
        "preemptive_security_safe_for_dry_run": True,
        "preemptive_security_safe_for_apply": True,
        "preemptive_security_sos_required": False,
        "preemptive_security_stop_required": False,
        "preemptive_security_review_required": False,
        "preemptive_security_event_count": 0,
        "preemptive_security_boss_alert_active": False,
        "preemptive_security_blocked_actions": [],
        "duplicate_intent_detected": False,
        "canonical_owner": "",
    }

    branch, head_record = _read_head_branch(root)
    signals["repo_branch"] = branch
    evidence_inputs.append(head_record)

    repo_state_payload, repo_state_path, repo_state_status = _load_repo_state_evidence(root)
    repo_state_summary = _apply_repo_state_signal(signals, repo_state_payload)
    evidence_inputs.append(_evidence(repo_state_path, repo_state_status, repo_state_summary))

    dirty_classifier = _load_dirty_tree_classifier()
    dirty_tree_payload: dict[str, Any] | None = None
    dirty_tree_status = "missing"
    dirty_tree_summary = "Dirty tree classifier module is missing."
    if dirty_classifier is not None:
        dirty_tree_status = "present"
        try:
            dirty_tree_payload = dirty_classifier.build_dirty_tree_classification(repo_root=root)
            dirty_tree_summary = _apply_dirty_tree_classifier_signal(signals, dirty_tree_payload)
        except Exception:
            dirty_tree_status = "unknown"
            dirty_tree_summary = _apply_dirty_tree_classifier_signal(signals, None)
    evidence_inputs.append(
        _evidence(
            "automation/orchestration/continuation/aios_dirty_tree_classifier.py",
            dirty_tree_status,
            dirty_tree_summary,
        )
    )

    security_layer = _load_preemptive_security_layer()
    security_status = "missing"
    security_summary = "Preemptive security layer module is missing."
    if security_layer is not None:
        security_status = "present"
        try:
            security_payload = security_layer.build_security_state(repo_root=root, dirty_tree=dirty_tree_payload)
            security_summary = _apply_preemptive_security_signal(signals, security_payload)
        except Exception:
            security_status = "unknown"
            security_summary = _apply_preemptive_security_signal(signals, None)
    evidence_inputs.append(
        _evidence(
            "automation/security/aios_preemptive_security_layer.py",
            security_status,
            security_summary,
        )
    )

    json_sources = {
        "control/cycle/last_marker.json": "status_artifact",
        "Reports/autonomy_control_plane/autonomy_status_report.json": "autonomy_status",
        "Reports/runtime_queue/runtime_execution_queue_view.json": "queue",
        "Reports/runtime_queue_blocker_stack/runtime_queue_blocker_stack.json": "blockers",
        "Reports/self_build_cycle/latest_self_build_cycle.evidence.json": "self_build",
        "Reports/validator_evidence_router/AIOS_VALIDATOR_EVIDENCE_ROUTER_LATEST.json": "validator",
        "telemetry/runtime/runtime_state.json": "runtime_status",
        "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json": "approval",
        "automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json": "approval",
        str(DEFAULT_OUTPUT).replace("\\", "/"): "decision_output",
    }

    unsafe_scan_payloads: list[Any] = []
    for rel_path, kind in json_sources.items():
        status, payload, summary = _path_status(root, rel_path)
        evidence_inputs.append(_evidence(rel_path, status, summary))
        if status != "present":
            continue
        if kind == "status_artifact":
            signals["safe_status_artifact_present"] = True
        elif kind == "autonomy_status":
            summary = _apply_autonomy_status_signal(signals, payload if isinstance(payload, dict) else None)
            evidence_inputs[-1] = _evidence(rel_path, status, summary)
        elif kind == "queue":
            summary = _apply_queue_signal(signals, payload if isinstance(payload, dict) else None)
            evidence_inputs[-1] = _evidence(rel_path, status, summary)
        elif kind == "blockers":
            summary = _apply_blocker_signal(signals, payload if isinstance(payload, dict) else None)
            evidence_inputs[-1] = _evidence(rel_path, status, summary)
        elif kind == "self_build":
            summary = _apply_self_build_signal(signals, payload if isinstance(payload, dict) else None)
            evidence_inputs[-1] = _evidence(rel_path, status, summary)
        elif kind == "validator":
            summary = _apply_validator_signal(signals, payload if isinstance(payload, dict) else None)
            evidence_inputs[-1] = _evidence(rel_path, status, summary)
        elif kind == "runtime_status":
            summary = _apply_blocker_signal(signals, payload if isinstance(payload, dict) else None)
            evidence_inputs[-1] = _evidence(rel_path, status, summary)
        elif kind == "approval":
            approval_status = str((payload or {}).get("approval_status", "")).lower()
            if approval_status:
                signals["approval_status"] = approval_status
            if approval_status in {"pending", "pending_review", "review", "missing_approval_status"}:
                signals["approval_required"] = True
        elif kind == "decision_output":
            signals["decision_output_present"] = True
        if kind in {"queue", "self_build", "autonomy_status"}:
            unsafe_scan_payloads.append(payload)

    relay_approval_count = _count_files(root / "relay" / "approvals")
    evidence_inputs.append(
        _evidence(
            "relay/approvals/",
            "present" if (root / "relay" / "approvals").is_dir() else "missing",
            f"approval_file_count={relay_approval_count}",
        )
    )
    if relay_approval_count > 0:
        signals["approval_required"] = True

    active_packet_count = _count_files(root / "automation" / "orchestration" / "work_packets" / "active")
    evidence_inputs.append(
        _evidence(
            "automation/orchestration/work_packets/active/",
            "present" if (root / "automation" / "orchestration" / "work_packets" / "active").is_dir() else "missing",
            f"active_packet_file_count={active_packet_count}",
        )
    )

    readme = root / "README.md"
    if readme.is_file():
        try:
            readme_text = readme.read_text(encoding="utf-8")
            signals["trading_lab_paper_only_confirmed"] = (
                "Trading Lab" in readme_text
                and "paper-only" in readme_text.lower()
                and "Live broker execution" in readme_text
                and "blocked" in readme_text.lower()
            )
            evidence_inputs.append(
                _evidence(
                    "README.md",
                    "present",
                    "Trading Lab paper-only boundary found."
                    if signals["trading_lab_paper_only_confirmed"]
                    else "README present; paper-only boundary not confirmed.",
                )
            )
        except OSError:
            evidence_inputs.append(_evidence("README.md", "unknown", "README could not be read."))

    unsafe_blob = json.dumps(unsafe_scan_payloads, sort_keys=True, default=str)
    signals["unsafe_scope_detected"] = _contains_any_unsafe(unsafe_blob)
    return {"repo_root": str(root), "signals": signals, "evidence_inputs": evidence_inputs}


def classify_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    signals = dict(evidence.get("signals") or {})
    records = list(evidence.get("evidence_inputs") or [])

    if not records:
        records = [_evidence("local_evidence", "missing", "No evidence inputs were supplied.")]
    signals.setdefault("repo_state", "unknown")
    signals.setdefault("safe_status_artifact_present", False)
    signals.setdefault("validator_status", "unknown")
    signals.setdefault("approval_required", False)
    signals.setdefault("approval_status", "unknown")
    signals.setdefault("queue_present", False)
    signals.setdefault("queue_backlog_present", False)
    signals.setdefault("queue_item_count", 0)
    signals.setdefault("queue_blocked_count", 0)
    signals.setdefault("self_build_status_present", False)
    signals.setdefault("self_build_pending", False)
    signals.setdefault("autonomy_status_present", False)
    signals.setdefault("decision_output_present", False)
    signals.setdefault("active_blockers", [])
    signals.setdefault("active_blocker_count", 0)
    signals.setdefault("trading_lab_paper_only_confirmed", False)
    signals.setdefault("unsafe_scope_detected", False)
    signals.setdefault("dirty_tree_overall_classification", "UNKNOWN_DIRTY")
    signals.setdefault("dirty_tree_safe_for_dry_run", False)
    signals.setdefault("dirty_tree_safe_for_apply", False)
    signals.setdefault("dirty_tree_sos_required", False)
    signals.setdefault("dirty_tree_protected_stop_required", False)
    signals.setdefault("dirty_tree_review_required", False)
    signals.setdefault("dirty_tree_dirty_count", 0)
    signals.setdefault("preemptive_security_state_present", False)
    signals.setdefault("preemptive_security_overall_state", "UNKNOWN")
    signals.setdefault("preemptive_security_safe_for_dry_run", True)
    signals.setdefault("preemptive_security_safe_for_apply", True)
    signals.setdefault("preemptive_security_sos_required", False)
    signals.setdefault("preemptive_security_stop_required", False)
    signals.setdefault("preemptive_security_review_required", False)
    signals.setdefault("preemptive_security_event_count", 0)
    signals.setdefault("preemptive_security_boss_alert_active", False)
    signals.setdefault("preemptive_security_blocked_actions", [])
    signals.setdefault("duplicate_intent_detected", False)
    signals.setdefault("canonical_owner", "")
    return {"signals": signals, "evidence_inputs": records}


def _packet_scope(packet_id: str, mode: str, lane: str, files_allowed: list[str]) -> dict[str, Any]:
    return {
        "packet_id_suggestion": packet_id,
        "mode": mode,
        "lane": lane,
        "files_allowed": files_allowed,
        "files_forbidden": BLOCKED_FILES,
    }


CANDIDATE_FIELDS = (
    "task_id",
    "title",
    "category",
    "value_score",
    "urgency_score",
    "risk_score",
    "blocker_score",
    "validation_score",
    "autonomy_leverage_score",
    "total_score",
    "reason",
    "required_validator",
    "allowed_lane",
    "stop_condition",
    "blocked",
)


def _candidate(
    *,
    task_id: str,
    title: str,
    category: str,
    value_score: int,
    urgency_score: int,
    risk_score: int,
    blocker_score: int,
    validation_score: int,
    autonomy_leverage_score: int,
    reason: str,
    required_validator: str,
    allowed_lane: str,
    stop_condition: str,
    blocked: bool,
    blocked_reason: str | None,
    risk_level: str,
    confidence: float,
    packet_scope: dict[str, Any],
    priority_boost: int = 0,
) -> dict[str, Any]:
    if category not in DECISION_CATEGORIES:
        raise ValueError(f"Unsupported candidate category: {category}")
    if allowed_lane not in ALLOWED_LANES:
        raise ValueError(f"Unsupported candidate lane: {allowed_lane}")
    if risk_level not in RISK_LEVELS:
        raise ValueError(f"Unsupported candidate risk level: {risk_level}")
    scores = {
        "value_score": int(value_score),
        "urgency_score": int(urgency_score),
        "risk_score": int(risk_score),
        "blocker_score": int(blocker_score),
        "validation_score": int(validation_score),
        "autonomy_leverage_score": int(autonomy_leverage_score),
    }
    total_score = sum(scores.values()) + int(priority_boost)
    return {
        "task_id": task_id,
        "title": title,
        "category": category,
        **scores,
        "total_score": total_score,
        "reason": reason,
        "required_validator": required_validator,
        "allowed_lane": allowed_lane,
        "stop_condition": stop_condition,
        "blocked": bool(blocked),
        "blocked_reason": blocked_reason,
        "risk_level": risk_level,
        "confidence": confidence,
        "recommended_packet_scope": packet_scope,
    }


def _public_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {field: candidate[field] for field in CANDIDATE_FIELDS}


def _sorted_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(candidates, key=lambda item: (-_to_int(item.get("total_score")), str(item.get("task_id", ""))))


def _apply_candidate_safety_overrides(signals: dict[str, Any], candidates: list[dict[str, Any]]) -> None:
    approval_missing = signals["approval_status"] in {"unknown", "missing", "pending", "pending_review", "review"}
    repo_dirty = signals.get("repo_state") != "clean"
    security_blocks_apply = signals.get("preemptive_security_safe_for_apply") is False
    for candidate in candidates:
        applies = str(candidate.get("allowed_lane", "")).startswith("APPLY")
        if repo_dirty and applies and candidate.get("category") != "STATUS_RECON":
            candidate["blocked"] = True
            candidate["blocked_reason"] = candidate.get("blocked_reason") or "dirty_working_tree"
            candidate["total_score"] = 0
            candidate["reason"] = f"{candidate['reason']} Repo is dirty, so APPLY candidates must wait for status or cleanup."
        if signals.get("approval_required") and approval_missing and applies:
            candidate["blocked"] = True
            candidate["blocked_reason"] = candidate.get("blocked_reason") or "apply_approval_missing"
            candidate["total_score"] = 0
            candidate["reason"] = f"{candidate['reason']} Approval evidence is missing, so APPLY is blocked."
        if security_blocks_apply and applies:
            candidate["blocked"] = True
            candidate["blocked_reason"] = candidate.get("blocked_reason") or "preemptive_security_not_apply_safe"
            candidate["total_score"] = 0
            candidate["reason"] = f"{candidate['reason']} Preemptive security state allows only READ_ONLY/DRY_RUN routing."


def _rank_candidate_records(classified: dict[str, Any]) -> list[dict[str, Any]]:
    signals = classified["signals"]
    candidates: list[dict[str, Any]] = []
    approval_missing = signals["approval_status"] in {"unknown", "missing", "pending", "pending_review", "review"}
    security_overlay_present = signals.get("preemptive_security_state_present") is True

    if signals.get("preemptive_security_sos_required"):
        candidates.append(
            _candidate(
                task_id="preemptive_security_sos_stop",
                title="Stop and escalate preemptive security SOS.",
                category="BLOCKED_STOP_AND_REPORT",
                value_score=100,
                urgency_score=100,
                risk_score=100,
                blocker_score=100,
                validation_score=100,
                autonomy_leverage_score=100,
                reason="Preemptive security state found canary, secret, broker, live-trading, or real-order SOS risk.",
                required_validator="Preemptive security state review",
                allowed_lane="BLOCKED",
                stop_condition="Stop AI_OS continuation and do not print secret-like values.",
                blocked=True,
                blocked_reason="preemptive_security_sos",
                risk_level="blocked",
                confidence=0.99,
                priority_boost=1500,
                packet_scope=_packet_scope(
                    "AIOS-PREEMPTIVE-SECURITY-SOS-STOP",
                    "DRY_RUN",
                    "BLOCKED",
                    ["automation/security/aios_preemptive_security_layer.py", "Reports/"],
                ),
            )
        )

    if signals.get("preemptive_security_stop_required") or signals.get("preemptive_security_review_required"):
        candidates.append(
            _candidate(
                task_id="preemptive_security_review_stop",
                title="Stop for preemptive security review before mutation.",
                category="BLOCKED_STOP_AND_REPORT",
                value_score=99,
                urgency_score=99,
                risk_score=99,
                blocker_score=99,
                validation_score=98,
                autonomy_leverage_score=98,
                reason=(
                    "Preemptive security state is "
                    f"{signals.get('preemptive_security_overall_state')}; APPLY and protected actions require review."
                ),
                required_validator="Preemptive security state and Dirty Tree Classifier review",
                allowed_lane="BLOCKED",
                stop_condition="Stop before APPLY, protected actions, scheduler, daemon, worker launch, broker, live trading, or production.",
                blocked=True,
                blocked_reason="preemptive_security_review_required",
                risk_level="blocked",
                confidence=0.96,
                priority_boost=1400,
                packet_scope=_packet_scope(
                    "AIOS-PREEMPTIVE-SECURITY-REVIEW-STOP",
                    "DRY_RUN",
                    "BLOCKED",
                    ["automation/security/aios_preemptive_security_layer.py", "automation/orchestration/continuation/"],
                ),
            )
        )

    if (
        signals.get("preemptive_security_state_present")
        and signals.get("preemptive_security_overall_state") == "WATCH"
        and signals.get("preemptive_security_safe_for_dry_run")
    ):
        candidates.append(
            _candidate(
                task_id="preemptive_security_watch_dry_run",
                title="Continue only READ_ONLY/DRY_RUN work under preemptive security WATCH.",
                category="TELEMETRY_REPORTING",
                value_score=20,
                urgency_score=20,
                risk_score=20,
                blocker_score=20,
                validation_score=20,
                autonomy_leverage_score=20,
                reason="Preemptive security state is WATCH; generated safety evidence may be observed, but APPLY remains blocked.",
                required_validator="Preemptive security state review",
                allowed_lane="DRY_RUN",
                stop_condition="Stop before APPLY, protected actions, worker launch, scheduler, secrets, broker, live trading, or production.",
                blocked=False,
                blocked_reason=None,
                risk_level="low",
                confidence=0.78,
                priority_boost=20,
                packet_scope=_packet_scope(
                    "AIOS-PREEMPTIVE-SECURITY-WATCH-DRY-RUN",
                    "DRY_RUN",
                    "DRY_RUN",
                    ["automation/security/aios_preemptive_security_layer.py", "Reports/"],
                ),
            )
        )

    dirty_tree_sos_still_required = signals.get("dirty_tree_sos_required") and (
        not security_overlay_present or signals.get("preemptive_security_sos_required")
    )
    if dirty_tree_sos_still_required:
        candidates.append(
            _candidate(
                task_id="dirty_tree_security_sos",
                title="Stop and escalate dirty tree security indicators.",
                category="BLOCKED_STOP_AND_REPORT",
                value_score=100,
                urgency_score=100,
                risk_score=100,
                blocker_score=100,
                validation_score=100,
                autonomy_leverage_score=100,
                reason="Dirty tree classifier found secret, broker, live-order, webhook, production, dashboard mutation, scheduler, daemon, or worker-launch indicators.",
                required_validator="Dirty tree classifier security review",
                allowed_lane="BLOCKED",
                stop_condition="Stop AI_OS continuation and do not print secret values.",
                blocked=True,
                blocked_reason="security_sos_dirty",
                risk_level="blocked",
                confidence=0.99,
                priority_boost=1300,
                packet_scope=_packet_scope("AIOS-DIRTY-TREE-SECURITY-SOS-STOP", "DRY_RUN", "BLOCKED", ["Reports/", "automation/orchestration/continuation/aios_dirty_tree_classifier.py"]),
            )
        )

    if signals.get("dirty_tree_protected_stop_required"):
        candidates.append(
            _candidate(
                task_id="dirty_tree_protected_authority_stop",
                title="Stop before continuing with dirty protected authority files.",
                category="BLOCKED_STOP_AND_REPORT",
                value_score=98,
                urgency_score=98,
                risk_score=98,
                blocker_score=98,
                validation_score=95,
                autonomy_leverage_score=95,
                reason="Dirty tree classifier found protected governance, security, runtime, dispatcher, or repo authority files.",
                required_validator="Human Owner protected-authority dirty file review",
                allowed_lane="BLOCKED",
                stop_condition="Stop until the Human Owner reviews the protected dirty files.",
                blocked=True,
                blocked_reason="protected_authority_dirty",
                risk_level="blocked",
                confidence=0.96,
                priority_boost=1200,
                packet_scope=_packet_scope("AIOS-DIRTY-TREE-PROTECTED-AUTHORITY-STOP", "DRY_RUN", "BLOCKED", ["docs/governance/", "docs/security/", "AGENTS.md", "README.md"]),
            )
        )

    if signals["unsafe_scope_detected"]:
        candidates.append(
            _candidate(
                task_id="safety_stop_unsafe_scope",
                title="Stop and report unsafe autonomy scope.",
                category="BLOCKED_STOP_AND_REPORT",
                value_score=100,
                urgency_score=100,
                risk_score=100,
                blocker_score=100,
                validation_score=95,
                autonomy_leverage_score=100,
                reason="Evidence mentions live, broker, webhook, credential, secret, or real-order scope.",
                required_validator="Manual safety review against AGENTS.md and RISK_POLICY.md",
                allowed_lane="BLOCKED",
                stop_condition="Stop before APPLY, worker launch, provider dispatch, broker, webhook, or credential access.",
                blocked=True,
                blocked_reason="unsafe_scope_detected",
                risk_level="blocked",
                confidence=0.97,
                priority_boost=1000,
                packet_scope=_packet_scope("AIOS-UNSAFE-SCOPE-STOP-AND-REPORT", "DRY_RUN", "BLOCKED", ["AGENTS.md", "RISK_POLICY.md"]),
            )
        )

    if signals["repo_state"] != "clean" and not signals.get("dirty_tree_safe_for_dry_run"):
        dirty = signals["repo_state"] == "dirty"
        dirty_tree_overall = str(signals.get("dirty_tree_overall_classification") or "")
        candidates.append(
            _candidate(
                task_id="repo_status_recon",
                title="Review dirty repo state before choosing APPLY work." if dirty else "Run repo status reconnaissance before choosing APPLY work.",
                category="STATUS_RECON",
                value_score=95,
                urgency_score=95,
                risk_score=90,
                blocker_score=90,
                validation_score=80,
                autonomy_leverage_score=85,
                reason=(
                    f"Repo-state evidence proves the working tree is dirty ({dirty_tree_overall or 'unclassified'}); dirty files must be reviewed before new APPLY work."
                    if dirty
                    else "Repo state evidence is unknown or not proven clean; mutation work must wait."
                ),
                required_validator="pwd; git status --short --branch; git branch --show-current; git remote -v",
                allowed_lane="READ_ONLY",
                stop_condition="Stop if path, branch, remotes, or dirty files are uncertain.",
                blocked=True,
                blocked_reason="dirty_working_tree" if dirty else "repo_state_unknown",
                risk_level="blocked",
                confidence=0.86,
                priority_boost=800,
                packet_scope=_packet_scope("AIOS-REPO-STATUS-RECON-DRY-RUN", "DRY_RUN", "READ_ONLY", ["AGENTS.md", "README.md", "WHITEPAPER.md"]),
            )
        )

    if signals["repo_state"] == "safe_dirty" or (
        signals.get("dirty_tree_safe_for_dry_run") and _to_int(signals.get("dirty_tree_dirty_count"), 0) > 0
    ):
        candidates.append(
            _candidate(
                task_id="safe_dirty_dry_run_continuation",
                title="Continue only READ_ONLY/DRY_RUN work with safe generated dirty evidence.",
                category="TELEMETRY_REPORTING",
                value_score=12,
                urgency_score=12,
                risk_score=14,
                blocker_score=10,
                validation_score=12,
                autonomy_leverage_score=14,
                reason="Dirty files are classified as generated evidence, reports, or sandbox previews; DRY_RUN continuation is allowed while APPLY remains blocked.",
                required_validator="Dirty tree classifier result review",
                allowed_lane="DRY_RUN",
                stop_condition="Stop before APPLY, protected actions, worker launch, scheduler, secrets, broker, live trading, or production.",
                blocked=False,
                blocked_reason=None,
                risk_level="low",
                confidence=0.74,
                priority_boost=0,
                packet_scope=_packet_scope("AIOS-SAFE-DIRTY-DRY-RUN-CONTINUATION", "DRY_RUN", "DRY_RUN", ["Reports/", "automation/orchestration/work_packets/preview/"]),
            )
        )

    if _to_int(signals.get("active_blocker_count"), 0) > 0:
        candidates.append(
            _candidate(
                task_id="control_plane_blocker_review",
                title="Stop and resolve active control-plane blockers before selecting worker work.",
                category="BLOCKED_STOP_AND_REPORT",
                value_score=90,
                urgency_score=92,
                risk_score=95,
                blocker_score=100,
                validation_score=80,
                autonomy_leverage_score=80,
                reason="Existing blocker evidence reports unresolved blockers that must be cleared before routing queue, self-build, or APPLY work.",
                required_validator="Blocker report review",
                allowed_lane="BLOCKED",
                stop_condition="Stop until active blocker evidence is cleared or explicitly reclassified by Human Owner.",
                blocked=True,
                blocked_reason="active_blockers_present",
                risk_level="blocked",
                confidence=0.92,
                priority_boost=760,
                packet_scope=_packet_scope(
                    "AIOS-CONTROL-PLANE-BLOCKER-REVIEW-DRY-RUN",
                    "DRY_RUN",
                    "READ_ONLY",
                    ["Reports/", "automation/orchestration/runtime_closure/", "tests/orchestration/"],
                ),
            )
        )

    if signals["duplicate_intent_detected"]:
        owner = signals["canonical_owner"] or "existing canonical owner"
        candidates.append(
            _candidate(
                task_id="extend_canonical_owner",
                title=f"Extend {owner} instead of creating a duplicate decision surface.",
                category="QUEUE_CONSOLIDATION",
                value_score=76,
                urgency_score=70,
                risk_score=60,
                blocker_score=65,
                validation_score=70,
                autonomy_leverage_score=75,
                reason="Duplicate intent was detected; AI_OS must extend canonical owners rather than creating competing brains.",
                required_validator="Authority duplication guard",
                allowed_lane="DRY_RUN",
                stop_condition="Stop if the canonical owner cannot be proven.",
                blocked=False,
                blocked_reason=None,
                risk_level="medium",
                confidence=0.82,
                priority_boost=540,
                packet_scope=_packet_scope("AIOS-EXTEND-CANONICAL-OWNER-DRY-RUN", "DRY_RUN", "DRY_RUN", [owner]),
            )
        )

    if signals["approval_required"] and approval_missing:
        candidates.append(
            _candidate(
                task_id="approval_gate_repair",
                title="Repair approval gate evidence before any APPLY lane can proceed.",
                category="APPROVAL_GATE_REPAIR",
                value_score=85,
                urgency_score=88,
                risk_score=95,
                blocker_score=95,
                validation_score=85,
                autonomy_leverage_score=75,
                reason="APPLY appears to require approval evidence, but approval is missing or non-explicit.",
                required_validator="Approval inbox integrity validator",
                allowed_lane="BLOCKED",
                stop_condition="Stop until Human Owner approval evidence names exact scope, validators, and stop point.",
                blocked=True,
                blocked_reason="apply_approval_missing",
                risk_level="blocked",
                confidence=0.9,
                priority_boost=720,
                packet_scope=_packet_scope(
                    "AIOS-APPROVAL-GATE-EVIDENCE-REPAIR-DRY-RUN",
                    "DRY_RUN",
                    "READ_ONLY",
                    ["automation/orchestration/approval_inbox/", "relay/approvals/"],
                ),
            )
        )

    if signals["validator_status"] in {"missing", "failing", "failed", "unknown"}:
        candidates.append(
            _candidate(
                task_id="validator_evidence_repair",
                title="Repair or route validator evidence before advancing autonomy work.",
                category="VALIDATOR_REPAIR",
                value_score=88,
                urgency_score=90,
                risk_score=70,
                blocker_score=80,
                validation_score=100,
                autonomy_leverage_score=85,
                reason="Validator evidence is missing, failing, or unknown; autonomy decisions need quality-control proof before queue or worker changes.",
                required_validator="python -m pytest tests/orchestration/test_aios_validator_evidence_router.py -q",
                allowed_lane="DRY_RUN",
                stop_condition="Stop if validator router evidence remains missing or failing.",
                blocked=False,
                blocked_reason=None,
                risk_level="medium",
                confidence=0.78,
                priority_boost=650,
                packet_scope=_packet_scope(
                    "AIOS-VALIDATOR-EVIDENCE-ROUTER-REPAIR-DRY-RUN",
                    "DRY_RUN",
                    "DRY_RUN",
                    ["automation/orchestration/validators/", "tests/orchestration/test_aios_validator_evidence_router.py"],
                ),
            )
        )

    if signals.get("queue_backlog_present"):
        candidates.append(
            _candidate(
                task_id="runtime_queue_backlog_consolidation",
                title="Consolidate and classify the runtime queue backlog before routing new work.",
                category="QUEUE_CONSOLIDATION",
                value_score=82,
                urgency_score=75,
                risk_score=55,
                blocker_score=70,
                validation_score=75,
                autonomy_leverage_score=70,
                reason=f"Queue evidence reports {signals.get('queue_item_count', 0)} pending item(s); queued work should be understood before selecting another APPLY or worker lane.",
                required_validator="Runtime execution queue validator",
                allowed_lane="DRY_RUN",
                stop_condition="Stop before queue mutation, worker launch, scheduler, commit, push, or merge.",
                blocked=False,
                blocked_reason=None,
                risk_level="medium",
                confidence=0.8,
                priority_boost=500,
                packet_scope=_packet_scope(
                    "AIOS-RUNTIME-QUEUE-BACKLOG-CONSOLIDATION-DRY-RUN",
                    "DRY_RUN",
                    "DRY_RUN",
                    ["Reports/runtime_queue/", "automation/orchestration/runtime_queue/", "tests/orchestration/test_runtime_execution_queue.py"],
                ),
            )
        )

    if signals.get("self_build_pending"):
        candidates.append(
            _candidate(
                task_id="self_build_evidence_repair",
                title="Collect or repair self-build evidence before advancing the autonomy loop.",
                category="SELF_BUILD_LOOP_WIRING",
                value_score=78,
                urgency_score=70,
                risk_score=45,
                blocker_score=55,
                validation_score=65,
                autonomy_leverage_score=90,
                reason="Self-build evidence is present but still pending, incomplete, or human-required.",
                required_validator="Self-build decision consumer tests",
                allowed_lane="DRY_RUN",
                stop_condition="Stop before APPLY, worker launch, queue mutation, scheduler, commit, push, or merge.",
                blocked=False,
                blocked_reason=None,
                risk_level="medium",
                confidence=0.78,
                priority_boost=430,
                packet_scope=_packet_scope(
                    "AIOS-SELF-BUILD-EVIDENCE-REPAIR-DRY-RUN",
                    "DRY_RUN",
                    "DRY_RUN",
                    ["Reports/self_build_cycle/", "automation/orchestration/autonomy_control_plane/", "tests/orchestration/test_aios_self_build_decision_consumer.py"],
                ),
            )
        )

    if signals["autonomy_status_present"] and signals["self_build_status_present"] and not signals["decision_output_present"]:
        candidates.append(
            _candidate(
                task_id="self_build_decision_output_wiring",
                title="Wire self-build and autonomy status evidence into a next-action decision output.",
                category="SELF_BUILD_LOOP_WIRING",
                value_score=74,
                urgency_score=65,
                risk_score=40,
                blocker_score=40,
                validation_score=70,
                autonomy_leverage_score=95,
                reason="Status, validator, and approval evidence are available, but no governor decision artifact exists.",
                required_validator="Targeted autonomy decision governor tests",
                allowed_lane="APPLY_CODE_SAFE",
                stop_condition="Stop before worker launch, queue mutation, scheduler, commit, push, or merge.",
                blocked=False,
                blocked_reason=None,
                risk_level="medium",
                confidence=0.76,
                priority_boost=390,
                packet_scope=_packet_scope(
                    "AIOS-WIRE-SELF-BUILD-DECISION-GOVERNOR-APPLY",
                    "APPLY",
                    "APPLY_CODE_SAFE",
                    ["automation/orchestration/aios_autonomy_decision_governor.py", "tests/orchestration/test_aios_autonomy_decision_governor.py"],
                ),
            )
        )

    if signals["trading_lab_paper_only_confirmed"]:
        candidates.append(
            _candidate(
                task_id="trading_lab_paper_only_improvement",
                title="Choose a paper-only Trading Lab improvement with explicit safety boundaries.",
                category="TRADING_LAB_PAPER_ONLY_IMPROVEMENT",
                value_score=65,
                urgency_score=45,
                risk_score=35,
                blocker_score=20,
                validation_score=55,
                autonomy_leverage_score=40,
                reason="Trading Lab paper-only boundary is confirmed; broker, live order, credential, and real webhook scope remain blocked.",
                required_validator="Trading Lab paper-only boundary check",
                allowed_lane="DRY_RUN",
                stop_condition="Stop if broker, OANDA, live order, webhook, credential, or real execution scope appears.",
                blocked=False,
                blocked_reason=None,
                risk_level="low",
                confidence=0.72,
                priority_boost=220,
                packet_scope=_packet_scope("AIOS-TRADING-LAB-PAPER-ONLY-IMPROVEMENT-DRY-RUN", "DRY_RUN", "DRY_RUN", ["apps/trading_lab/", "tests/"]),
            )
        )

    if signals["decision_output_present"]:
        candidates.append(
            _candidate(
                task_id="dashboard_governor_decision_surfacing",
                title="Surface the governor decision in existing autonomy reports.",
                category="DASHBOARD_SURFACING",
                value_score=50,
                urgency_score=35,
                risk_score=25,
                blocker_score=15,
                validation_score=45,
                autonomy_leverage_score=35,
                reason="A decision output exists and can be exposed read-only to operator-facing reports after higher-priority loop closure work.",
                required_validator="Autonomy status report tests",
                allowed_lane="APPLY_CODE_SAFE",
                stop_condition="Stop before creating a second dashboard brain or mutating approvals/queues.",
                blocked=False,
                blocked_reason=None,
                risk_level="low",
                confidence=0.68,
                priority_boost=150,
                packet_scope=_packet_scope(
                    "AIOS-SURFACE-GOVERNOR-DECISION-IN-AUTONOMY-STATUS-DRY-RUN",
                    "DRY_RUN",
                    "APPLY_CODE_SAFE",
                    ["automation/orchestration/autonomy_reports/", "tests/orchestration/test_autonomy_status_report.py"],
                ),
            )
        )

    if not candidates:
        candidates.append(
            _candidate(
                task_id="no_safe_next_task_report",
                title="Stop and report that no safe next task is provable.",
                category="BLOCKED_STOP_AND_REPORT",
                value_score=30,
                urgency_score=40,
                risk_score=70,
                blocker_score=80,
                validation_score=40,
                autonomy_leverage_score=45,
                reason="Available evidence does not prove a safe next work item.",
                required_validator="Manual review of evidence inputs",
                allowed_lane="BLOCKED",
                stop_condition="Stop until a safe next packet scope is proven.",
                blocked=True,
                blocked_reason="no_safe_next_task_provable",
                risk_level="blocked",
                confidence=0.7,
                packet_scope=_packet_scope("AIOS-NO-SAFE-NEXT-TASK-REPORT", "DRY_RUN", "BLOCKED", ["Reports/"]),
            )
        )

    _apply_candidate_safety_overrides(signals, candidates)
    return _sorted_candidates(candidates)


def rank_candidates(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    classified = classify_evidence(evidence)
    return [_public_candidate(candidate) for candidate in _rank_candidate_records(classified)]


def _decision(
    *,
    generated_at_utc: str,
    evidence_inputs: list[dict[str, str]],
    next_highest_value_task: str,
    decision_category: str,
    why_this_task: list[str],
    risk_level: str,
    allowed_lane: str,
    required_validators: list[str],
    stop_conditions: list[str],
    blocked: bool,
    blocked_reason: str | None,
    confidence: float,
    recommended_packet_scope: dict[str, Any],
    ranked_candidates: list[dict[str, Any]],
    selected_candidate_id: str,
    selection_reason: str,
) -> dict[str, Any]:
    if decision_category not in DECISION_CATEGORIES:
        raise ValueError(f"Unsupported decision category: {decision_category}")
    if allowed_lane not in ALLOWED_LANES:
        raise ValueError(f"Unsupported lane: {allowed_lane}")
    if risk_level not in RISK_LEVELS:
        raise ValueError(f"Unsupported risk level: {risk_level}")

    identity_seed = {
        "task": next_highest_value_task,
        "category": decision_category,
        "blocked": blocked,
        "blocked_reason": blocked_reason,
        "lane": allowed_lane,
    }
    digest = hashlib.sha256(json.dumps(identity_seed, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return {
        "schema_version": SCHEMA_VERSION,
        "system": "AI_OS",
        "component": COMPONENT,
        "mode": "APPLY_SAFE_DECISION_OUTPUT",
        "decision_id": f"AIOS-ADG-{digest}",
        "generated_at_utc": generated_at_utc,
        "next_highest_value_task": next_highest_value_task,
        "decision_category": decision_category,
        "why_this_task": why_this_task,
        "risk_level": risk_level,
        "allowed_lane": allowed_lane,
        "required_validators": required_validators,
        "stop_conditions": stop_conditions,
        "blocked": blocked,
        "blocked_reason": blocked_reason,
        "evidence_inputs": evidence_inputs,
        "safety_boundaries": {
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
        "confidence": round(max(0.0, min(1.0, confidence)), 2),
        "recommended_packet_scope": recommended_packet_scope,
        "ranked_candidates": ranked_candidates,
        "selected_candidate_id": selected_candidate_id,
        "selection_reason": selection_reason,
    }


def choose_next_decision(evidence: dict[str, Any], generated_at_utc: str | None = None) -> dict[str, Any]:
    classified = classify_evidence(evidence)
    evidence_inputs = classified["evidence_inputs"]
    now = generated_at_utc or utc_now()
    candidates = _rank_candidate_records(classified)
    selected = candidates[0]
    ranked_candidates = [_public_candidate(candidate) for candidate in candidates]
    selection_reason = f"{selected['task_id']} has the highest total_score ({selected['total_score']}) under current evidence."

    return _decision(
        generated_at_utc=now,
        evidence_inputs=evidence_inputs,
        next_highest_value_task=selected["title"],
        decision_category=selected["category"],
        why_this_task=[selected["reason"]],
        risk_level=selected["risk_level"],
        allowed_lane=selected["allowed_lane"],
        required_validators=[selected["required_validator"]],
        stop_conditions=[selected["stop_condition"]],
        blocked=selected["blocked"],
        blocked_reason=selected["blocked_reason"],
        confidence=selected["confidence"],
        recommended_packet_scope=selected["recommended_packet_scope"],
        ranked_candidates=ranked_candidates,
        selected_candidate_id=selected["task_id"],
        selection_reason=selection_reason,
    )

    signals = classified["signals"]

    if signals["unsafe_scope_detected"]:
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Stop and report unsafe autonomy scope.",
            decision_category="BLOCKED_STOP_AND_REPORT",
            why_this_task=["Evidence mentions live, broker, webhook, credential, secret, or real-order scope."],
            risk_level="blocked",
            allowed_lane="BLOCKED",
            required_validators=["Manual safety review against AGENTS.md and RISK_POLICY.md"],
            stop_conditions=["Stop before APPLY, worker launch, provider dispatch, broker, webhook, or credential access."],
            blocked=True,
            blocked_reason="unsafe_scope_detected",
            confidence=0.97,
            recommended_packet_scope=_packet_scope(
                "AIOS-UNSAFE-SCOPE-STOP-AND-REPORT",
                "DRY_RUN",
                "BLOCKED",
                ["AGENTS.md", "RISK_POLICY.md"],
            ),
        )

    if signals["repo_state"] != "clean":
        dirty = signals["repo_state"] == "dirty"
        blocked_reason = "dirty_working_tree" if dirty else "repo_state_unknown"
        task = (
            "Review dirty repo state before choosing APPLY work."
            if dirty
            else "Run repo status reconnaissance before choosing APPLY work."
        )
        why = (
            ["Repo-state evidence proves the working tree is dirty.", "A governed factory manager must not pick new APPLY work until dirty files are classified."]
            if dirty
            else ["Repo state evidence is unknown or not proven clean.", "A governed factory manager must not pick mutation work from uncertain state."]
        )
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task=task,
            decision_category="STATUS_RECON",
            why_this_task=why,
            risk_level="blocked",
            allowed_lane="READ_ONLY",
            required_validators=["pwd", "git status --short --branch", "git branch --show-current", "git remote -v"],
            stop_conditions=["Stop if path, branch, remotes, or dirty files are uncertain."],
            blocked=True,
            blocked_reason=blocked_reason,
            confidence=0.86,
            recommended_packet_scope=_packet_scope(
                "AIOS-REPO-STATUS-RECON-DRY-RUN",
                "DRY_RUN",
                "READ_ONLY",
                ["AGENTS.md", "README.md", "WHITEPAPER.md"],
            ),
        )

    if _to_int(signals.get("active_blocker_count"), 0) > 0:
        blockers = [str(item) for item in signals.get("active_blockers", []) if str(item).strip()]
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Stop and resolve active control-plane blockers before selecting worker work.",
            decision_category="BLOCKED_STOP_AND_REPORT",
            why_this_task=[
                "Existing blocker evidence reports unresolved blockers.",
                "The factory manager must clear blockers before routing queue, self-build, or APPLY work.",
            ],
            risk_level="blocked",
            allowed_lane="BLOCKED",
            required_validators=["Blocker report review", "Repo-state evidence refresh after blocker resolution"],
            stop_conditions=["Stop until active blocker evidence is cleared or explicitly reclassified by Human Owner."],
            blocked=True,
            blocked_reason="active_blockers_present",
            confidence=0.92,
            recommended_packet_scope=_packet_scope(
                "AIOS-CONTROL-PLANE-BLOCKER-REVIEW-DRY-RUN",
                "DRY_RUN",
                "READ_ONLY",
                ["Reports/", "automation/orchestration/runtime_closure/", "tests/orchestration/"],
            ),
        )

    if signals["duplicate_intent_detected"]:
        owner = signals["canonical_owner"] or "existing canonical owner"
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task=f"Extend {owner} instead of creating a duplicate decision surface.",
            decision_category="QUEUE_CONSOLIDATION",
            why_this_task=["Duplicate intent was detected.", "AI_OS must extend canonical owners rather than creating competing brains."],
            risk_level="medium",
            allowed_lane="DRY_RUN",
            required_validators=["Authority duplication guard", "Targeted owner tests"],
            stop_conditions=["Stop if the canonical owner cannot be proven."],
            blocked=False,
            blocked_reason=None,
            confidence=0.82,
            recommended_packet_scope=_packet_scope(
                "AIOS-EXTEND-CANONICAL-OWNER-DRY-RUN",
                "DRY_RUN",
                "DRY_RUN",
                [owner],
            ),
        )

    if signals["validator_status"] in {"missing", "failing", "failed", "unknown"}:
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Repair or route validator evidence before advancing autonomy work.",
            decision_category="VALIDATOR_REPAIR",
            why_this_task=["Validator evidence is missing, failing, or unknown.", "Autonomy decisions need quality-control proof before queue or worker changes."],
            risk_level="medium",
            allowed_lane="DRY_RUN",
            required_validators=["python -m pytest tests/orchestration/test_aios_validator_evidence_router.py -q"],
            stop_conditions=["Stop if validator router evidence remains missing or failing."],
            blocked=False,
            blocked_reason=None,
            confidence=0.78,
            recommended_packet_scope=_packet_scope(
                "AIOS-VALIDATOR-EVIDENCE-ROUTER-REPAIR-DRY-RUN",
                "DRY_RUN",
                "DRY_RUN",
                ["automation/orchestration/validators/", "tests/orchestration/test_aios_validator_evidence_router.py"],
            ),
        )

    if signals.get("queue_backlog_present"):
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Consolidate and classify the runtime queue backlog before routing new work.",
            decision_category="QUEUE_CONSOLIDATION",
            why_this_task=[
                f"Queue evidence reports {signals.get('queue_item_count', 0)} pending item(s).",
                "AI_OS should understand queued work before selecting another APPLY or worker lane.",
            ],
            risk_level="medium",
            allowed_lane="DRY_RUN",
            required_validators=["Runtime execution queue validator", "Queue mutation gate preview"],
            stop_conditions=["Stop before queue mutation, worker launch, scheduler, commit, push, or merge."],
            blocked=False,
            blocked_reason=None,
            confidence=0.8,
            recommended_packet_scope=_packet_scope(
                "AIOS-RUNTIME-QUEUE-BACKLOG-CONSOLIDATION-DRY-RUN",
                "DRY_RUN",
                "DRY_RUN",
                ["Reports/runtime_queue/", "automation/orchestration/runtime_queue/", "tests/orchestration/test_runtime_execution_queue.py"],
            ),
        )

    approval_missing = signals["approval_status"] in {"unknown", "missing", "pending", "pending_review", "review"}
    if signals["approval_required"] and approval_missing:
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Repair approval gate evidence before any APPLY lane can proceed.",
            decision_category="APPROVAL_GATE_REPAIR",
            why_this_task=["APPLY appears to require approval evidence, but approval is missing or non-explicit."],
            risk_level="blocked",
            allowed_lane="BLOCKED",
            required_validators=["Approval inbox integrity validator", "Apply approval gate validator"],
            stop_conditions=["Stop until Human Owner approval evidence names exact scope, validators, and stop point."],
            blocked=True,
            blocked_reason="apply_approval_missing",
            confidence=0.9,
            recommended_packet_scope=_packet_scope(
                "AIOS-APPROVAL-GATE-EVIDENCE-REPAIR-DRY-RUN",
                "DRY_RUN",
                "READ_ONLY",
                ["automation/orchestration/approval_inbox/", "relay/approvals/"],
            ),
        )

    if signals.get("self_build_pending"):
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Collect or repair self-build evidence before advancing the autonomy loop.",
            decision_category="SELF_BUILD_LOOP_WIRING",
            why_this_task=[
                "Self-build evidence is present but still pending, incomplete, or human-required.",
                "The governor needs proven self-build status before choosing autonomous continuation work.",
            ],
            risk_level="medium",
            allowed_lane="DRY_RUN",
            required_validators=["Self-build decision consumer tests", "Self-build evidence schema/readout validation"],
            stop_conditions=["Stop before APPLY, worker launch, queue mutation, scheduler, commit, push, or merge."],
            blocked=False,
            blocked_reason=None,
            confidence=0.78,
            recommended_packet_scope=_packet_scope(
                "AIOS-SELF-BUILD-EVIDENCE-REPAIR-DRY-RUN",
                "DRY_RUN",
                "DRY_RUN",
                ["Reports/self_build_cycle/", "automation/orchestration/autonomy_control_plane/", "tests/orchestration/test_aios_self_build_decision_consumer.py"],
            ),
        )

    if signals["autonomy_status_present"] and signals["self_build_status_present"] and not signals["decision_output_present"]:
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Wire self-build and autonomy status evidence into a next-action decision output.",
            decision_category="SELF_BUILD_LOOP_WIRING",
            why_this_task=["Status, validator, and approval evidence are available, but no governor decision artifact exists."],
            risk_level="medium",
            allowed_lane="APPLY_CODE_SAFE",
            required_validators=["Targeted autonomy decision governor tests", "Schema validation"],
            stop_conditions=["Stop before worker launch, queue mutation, scheduler, commit, push, or merge."],
            blocked=False,
            blocked_reason=None,
            confidence=0.76,
            recommended_packet_scope=_packet_scope(
                "AIOS-WIRE-SELF-BUILD-DECISION-GOVERNOR-APPLY",
                "APPLY",
                "APPLY_CODE_SAFE",
                ["automation/orchestration/aios_autonomy_decision_governor.py", "tests/orchestration/test_aios_autonomy_decision_governor.py"],
            ),
        )

    if signals["trading_lab_paper_only_confirmed"]:
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Choose a paper-only Trading Lab improvement with explicit safety boundaries.",
            decision_category="TRADING_LAB_PAPER_ONLY_IMPROVEMENT",
            why_this_task=["Trading Lab paper-only boundary is confirmed.", "Paper-only work is lower risk than runtime execution or live broker scope."],
            risk_level="low",
            allowed_lane="DRY_RUN",
            required_validators=["Trading Lab paper-only boundary check", "Targeted Trading Lab tests for selected files"],
            stop_conditions=["Stop if broker, OANDA, live order, webhook, credential, or real execution scope appears."],
            blocked=False,
            blocked_reason=None,
            confidence=0.72,
            recommended_packet_scope=_packet_scope(
                "AIOS-TRADING-LAB-PAPER-ONLY-IMPROVEMENT-DRY-RUN",
                "DRY_RUN",
                "DRY_RUN",
                ["apps/trading_lab/", "tests/"],
            ),
        )

    if signals["decision_output_present"]:
        return _decision(
            generated_at_utc=now,
            evidence_inputs=evidence_inputs,
            next_highest_value_task="Surface the governor decision in existing autonomy reports.",
            decision_category="DASHBOARD_SURFACING",
            why_this_task=["A decision output exists and can be exposed read-only to operator-facing reports."],
            risk_level="low",
            allowed_lane="APPLY_CODE_SAFE",
            required_validators=["Autonomy status report tests", "Governor schema tests"],
            stop_conditions=["Stop before creating a second dashboard brain or mutating approvals/queues."],
            blocked=False,
            blocked_reason=None,
            confidence=0.68,
            recommended_packet_scope=_packet_scope(
                "AIOS-SURFACE-GOVERNOR-DECISION-IN-AUTONOMY-STATUS-DRY-RUN",
                "DRY_RUN",
                "APPLY_CODE_SAFE",
                ["automation/orchestration/autonomy_reports/", "tests/orchestration/test_autonomy_status_report.py"],
            ),
        )

    return _decision(
        generated_at_utc=now,
        evidence_inputs=evidence_inputs,
        next_highest_value_task="Stop and report that no safe next task is provable.",
        decision_category="BLOCKED_STOP_AND_REPORT",
        why_this_task=["Available evidence does not prove a safe next work item."],
        risk_level="blocked",
        allowed_lane="BLOCKED",
        required_validators=["Manual review of evidence inputs"],
        stop_conditions=["Stop until a safe next packet scope is proven."],
        blocked=True,
        blocked_reason="no_safe_next_task_provable",
        confidence=0.7,
        recommended_packet_scope=_packet_scope(
            "AIOS-NO-SAFE-NEXT-TASK-REPORT",
            "DRY_RUN",
            "BLOCKED",
            ["Reports/"],
        ),
    )


def write_decision_report(repo_root: str | Path, decision: dict[str, Any], output_path: str | Path | None = None) -> Path:
    root = Path(repo_root)
    target = Path(output_path) if output_path is not None else root / DEFAULT_OUTPUT
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(decision, indent=2, sort_keys=True))
            handle.write("\n")
        os.replace(tmp_name, target)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise
    return target


def main(repo_root: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    evidence = discover_evidence(root)
    decision = choose_next_decision(evidence)
    write_decision_report(root, decision, output_path)
    return decision


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Emit the AI_OS Autonomy Decision Governor latest JSON report.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output-path", default=None, help="Optional output path for the decision report.")
    args = parser.parse_args()
    decision = main(repo_root=Path(args.repo_root), output_path=args.output_path)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
