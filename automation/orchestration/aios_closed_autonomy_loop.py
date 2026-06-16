"""AI_OS Closed Autonomy Loop v1.

Builds one conservative Observe -> Decide -> Plan -> Validate Gate ->
Recommend Dispatch -> Report -> Stop cycle from local evidence.

This module does not dispatch workers, mutate queues, use network access,
touch credentials, or run continuously. Its materializer may write one JSON
report only to the sandbox latest-report path.
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
SYSTEM = "AI_OS"
COMPONENT = "closed_autonomy_loop"
MODE = "ONE_CYCLE_RECOMMENDATION_ONLY"
DEFAULT_OUTPUT_ROOT = Path("Reports") / "sandbox" / "closed_autonomy_loop"
DEFAULT_OUTPUT_NAME = "AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"
DEFAULT_OUTPUT_PATH = DEFAULT_OUTPUT_ROOT / DEFAULT_OUTPUT_NAME

INPUT_SPECS: tuple[tuple[str, Path], ...] = (
    ("repo_state", Path("Reports") / "repo_state" / "AIOS_REPO_STATE_LATEST.json"),
    (
        "governor_decision_output",
        Path("Reports") / "autonomy_decision_governor" / "AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json",
    ),
    (
        "validator_router",
        Path("Reports") / "validator_evidence_router" / "AIOS_VALIDATOR_EVIDENCE_ROUTER_LATEST.json",
    ),
    ("approval_gate", Path("automation") / "orchestration" / "approval_inbox" / "APPLY_APPROVAL_GATE_001.json"),
    ("approval_inbox", Path("automation") / "orchestration" / "approval_inbox" / "APPROVAL_INBOX_001.json"),
    ("queue_view", Path("Reports") / "runtime_queue" / "runtime_execution_queue_view.json"),
    (
        "blocker_stack",
        Path("Reports") / "runtime_queue_blocker_stack" / "runtime_queue_blocker_stack.json",
    ),
    ("self_build_cycle", Path("Reports") / "self_build_cycle" / "latest_self_build_cycle.evidence.json"),
    ("autonomy_status", Path("Reports") / "autonomy_control_plane" / "autonomy_status_report.json"),
    ("runtime_state", Path("telemetry") / "runtime" / "runtime_state.json"),
)

BASE_FORBIDDEN_PATHS = [
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "RISK_POLICY.md",
    "secrets/",
    "credentials/",
    ".env",
    ".env.*",
    "broker/",
    "OANDA/",
    "live_trading/",
    "webhooks/",
]

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


def _rel(path: Path) -> str:
    return path.as_posix()


def _input_record(name: str, path: Path | str, status: str, summary: str) -> dict[str, str]:
    normalized = status if status in {"present", "missing", "unknown"} else "unknown"
    return {"name": name, "path": str(path).replace("\\", "/"), "status": normalized, "summary": summary}


def _summarize_json(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "JSON present but root is not an object."
    parts: list[str] = []
    for key in (
        "schema",
        "schema_version",
        "status",
        "mode",
        "component",
        "decision_category",
        "allowed_lane",
        "blocked_reason",
        "runtime_gate",
    ):
        value = payload.get(key)
        if value not in (None, "", [], {}):
            parts.append(f"{key}={value}")
    return "; ".join(parts) if parts else "JSON object present."


def _load_governor_module() -> Any | None:
    path = Path(__file__).with_name("aios_autonomy_decision_governor.py")
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("aios_autonomy_decision_governor", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def _load_dirty_tree_classifier() -> Any | None:
    path = Path(__file__).parent / "continuation" / "aios_dirty_tree_classifier.py"
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("aios_dirty_tree_classifier", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def _build_governor_decision(repo_root: Path, generated_at_utc: str | None) -> tuple[dict[str, Any] | None, str]:
    governor = _load_governor_module()
    if governor is None:
        return None, "Autonomy Decision Governor module is missing or could not be imported."
    try:
        evidence = governor.discover_evidence(repo_root)
        decision = governor.choose_next_decision(evidence, generated_at_utc=generated_at_utc)
    except Exception:
        return None, "Autonomy Decision Governor call failed; closed loop is fail-closed."
    if not isinstance(decision, dict):
        return None, "Autonomy Decision Governor returned a non-object decision."
    return decision, "Governor decision produced in memory; no dispatch or report write was performed."


def _build_dirty_tree_classification(repo_root: Path) -> tuple[dict[str, Any] | None, str]:
    classifier = _load_dirty_tree_classifier()
    if classifier is None:
        return None, "Dirty tree classifier module is missing or could not be imported."
    try:
        result = classifier.build_dirty_tree_classification(repo_root=repo_root)
    except Exception:
        return None, "Dirty tree classifier failed; closed loop is fail-closed."
    if not isinstance(result, dict):
        return None, "Dirty tree classifier returned a non-object result."
    summary = (
        f"overall={result.get('overall_classification')}; "
        f"dirty_count={result.get('dirty_count')}; "
        f"safe_for_dry_run={str(result.get('safe_for_dry_run') is True).lower()}; "
        f"safe_for_apply={str(result.get('safe_for_apply') is True).lower()}"
    )
    return result, summary


def collect_loop_inputs(repo_root: str | Path, generated_at_utc: str | None = None) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    records: list[dict[str, str]] = []
    payloads: dict[str, Any] = {}

    for name, rel_path in INPUT_SPECS:
        payload = load_json_if_exists(root / rel_path)
        if payload is None:
            records.append(_input_record(name, rel_path, "missing", "Missing or unreadable JSON evidence."))
        else:
            records.append(_input_record(name, rel_path, "present", _summarize_json(payload)))
        payloads[name] = payload

    governor_payload = payloads.get("governor_decision_output")
    if isinstance(governor_payload, dict):
        payloads["governor_decision"] = governor_payload
    else:
        decision, summary = _build_governor_decision(root, generated_at_utc)
        payloads["governor_decision"] = decision
        records.append(
            _input_record(
                "governor_decision_runtime",
                Path("automation") / "orchestration" / "aios_autonomy_decision_governor.py",
                "present" if decision is not None else "unknown",
                summary,
            )
        )

    dirty_tree, dirty_tree_summary = _build_dirty_tree_classification(root)
    payloads["dirty_tree_classifier"] = dirty_tree
    records.append(
        _input_record(
            "dirty_tree_classifier",
            Path("automation") / "orchestration" / "continuation" / "aios_dirty_tree_classifier.py",
            "present" if dirty_tree is not None else "unknown",
            dirty_tree_summary,
        )
    )

    return {"repo_root": str(root), "inputs": records, "payloads": payloads}


def normalize_governor_decision(governor_decision: Any) -> dict[str, Any]:
    if not isinstance(governor_decision, dict):
        return {
            "selected_candidate_id": "none",
            "decision_category": "BLOCKED_STOP_AND_REPORT",
            "blocked": True,
            "blocked_reason": "governor_decision_missing",
            "allowed_lane": "BLOCKED",
            "_raw": {},
        }

    allowed_lane = str(governor_decision.get("allowed_lane") or "BLOCKED").strip() or "BLOCKED"
    blocked = bool(governor_decision.get("blocked") is True or allowed_lane == "BLOCKED")
    blocked_reason = governor_decision.get("blocked_reason")
    if blocked and blocked_reason in (None, "", [], {}):
        blocked_reason = "governor_blocked_without_reason"

    return {
        "selected_candidate_id": str(
            governor_decision.get("selected_candidate_id")
            or governor_decision.get("decision_id")
            or "none"
        ),
        "decision_category": str(governor_decision.get("decision_category") or "BLOCKED_STOP_AND_REPORT"),
        "blocked": blocked,
        "blocked_reason": None if blocked_reason in ("", [], {}) else blocked_reason,
        "allowed_lane": allowed_lane,
        "_raw": governor_decision,
    }


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def _proposed_mode(normalized: dict[str, Any]) -> str:
    raw = normalized.get("_raw") if isinstance(normalized.get("_raw"), dict) else {}
    scope = raw.get("recommended_packet_scope") if isinstance(raw.get("recommended_packet_scope"), dict) else {}
    scope_mode = str(scope.get("mode") or "").upper()
    lane = str(normalized.get("allowed_lane") or "BLOCKED").upper()

    if lane == "BLOCKED":
        return "BLOCKED"
    if lane == "READ_ONLY":
        return "READ_ONLY"
    if scope_mode == "DRY_RUN":
        return "DRY_RUN"
    if scope_mode == "APPLY":
        return "APPLY"
    if lane == "DRY_RUN":
        return "DRY_RUN"
    if lane.startswith("APPLY"):
        return "APPLY"
    return "BLOCKED"


def _proposal_from_governor(normalized: dict[str, Any]) -> dict[str, Any]:
    raw = normalized.get("_raw") if isinstance(normalized.get("_raw"), dict) else {}
    scope = raw.get("recommended_packet_scope") if isinstance(raw.get("recommended_packet_scope"), dict) else {}
    proposed_mode = _proposed_mode(normalized)
    forbidden = _unique(_as_list(scope.get("files_forbidden")) + BASE_FORBIDDEN_PATHS)
    allowed = _as_list(scope.get("files_allowed"))

    if proposed_mode == "APPLY":
        required_approval = "anthony"
    elif proposed_mode == "BLOCKED":
        required_approval = "blocked"
    else:
        required_approval = "none"

    return {
        "proposed_action_id": str(normalized.get("selected_candidate_id") or "none"),
        "proposed_action_title": str(raw.get("next_highest_value_task") or "No safe next task is proven."),
        "proposed_packet_id": str(scope.get("packet_id_suggestion") or normalized.get("selected_candidate_id") or "AIOS-NO-SAFE-NEXT-TASK"),
        "proposed_mode": proposed_mode,
        "proposed_lane": str(scope.get("lane") or normalized.get("allowed_lane") or "BLOCKED"),
        "required_validators": _as_list(raw.get("required_validators")) or ["Manual evidence review"],
        "required_approval": required_approval,
        "allowed_paths": allowed,
        "forbidden_paths": forbidden,
        "stop_conditions": _as_list(raw.get("stop_conditions")) or ["Stop after one closed-loop evaluation."],
    }


def build_loop_state(inputs: dict[str, Any]) -> dict[str, Any]:
    payloads = dict(inputs.get("payloads") or {})
    normalized = normalize_governor_decision(payloads.get("governor_decision"))
    return {
        "repo_root": str(inputs.get("repo_root") or ""),
        "inputs": list(inputs.get("inputs") or []),
        "payloads": payloads,
        "governor_decision": normalized,
        "proposed_cycle_action": _proposal_from_governor(normalized),
    }


def _contains_any_unsafe(value: Any) -> bool:
    lowered = json.dumps(value, sort_keys=True, default=str).lower()
    return any(term in lowered for term in UNSAFE_SCOPE_TERMS)


def _get_nested(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _status_value(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    for keys in (
        ("status",),
        ("result",),
        ("validation", "status"),
        ("validator_status",),
        ("normalized_status",),
        ("runtime_gate",),
        ("gate_status",),
        ("approval_status",),
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


def _dirty_tree_payload(loop_state: dict[str, Any]) -> dict[str, Any]:
    payload = loop_state["payloads"].get("dirty_tree_classifier")
    return payload if isinstance(payload, dict) else {}


def _dirty_tree_is_safe_for_dry_run(loop_state: dict[str, Any]) -> bool:
    payload = _dirty_tree_payload(loop_state)
    return (
        int(payload.get("dirty_count") or 0) > 0
        and payload.get("safe_for_dry_run") is True
        and payload.get("safe_for_apply") is False
        and payload.get("sos_required") is not True
        and payload.get("protected_stop_required") is not True
    )


def _repo_dirty(loop_state: dict[str, Any]) -> bool:
    dirty_tree = _dirty_tree_payload(loop_state)
    if dirty_tree:
        if _dirty_tree_is_safe_for_dry_run(loop_state):
            return False
        if int(dirty_tree.get("dirty_count") or 0) > 0:
            return True
    payload = loop_state["payloads"].get("repo_state")
    decision = loop_state["governor_decision"]
    if isinstance(payload, dict):
        if payload.get("is_clean") is False:
            return True
        if payload.get("blocked_reason") == "dirty_working_tree":
            return True
    return decision.get("blocked_reason") == "dirty_working_tree"


def _validator_failure(loop_state: dict[str, Any]) -> bool:
    decision = loop_state["governor_decision"]
    if decision.get("decision_category") == "VALIDATOR_REPAIR":
        return True
    payload = loop_state["payloads"].get("validator_router")
    if not isinstance(payload, dict):
        return False
    status = _status_value(payload)
    return status in {"fail", "failed", "error", "blocked", "review_required", "invalid"} or bool(_collect_blockers(payload))


def _approval_is_explicit(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    status = _status_value(payload)
    if status in {"approved", "explicitly_approved", "pass", "passed"}:
        return True
    explicit = payload.get("explicit_human_approval") is True
    scoped = payload.get("scope_confirmed") is True or payload.get("exact_scope_confirmed") is True
    return bool(explicit and scoped)


def _apply_approval_missing(loop_state: dict[str, Any]) -> bool:
    action = loop_state["proposed_cycle_action"]
    if action.get("proposed_mode") != "APPLY":
        return False
    payloads = loop_state["payloads"]
    return not (
        _approval_is_explicit(payloads.get("approval_gate"))
        or _approval_is_explicit(payloads.get("approval_inbox"))
    )


def _active_blockers(loop_state: dict[str, Any]) -> list[str]:
    payloads = loop_state["payloads"]
    blockers: list[str] = []
    for key in ("blocker_stack", "autonomy_status", "runtime_state"):
        payload = payloads.get(key)
        blockers.extend(_collect_blockers(payload))
        if _status_value(payload) in {"blocked", "fail", "failed"}:
            blockers.append(f"{key}_status={_status_value(payload)}")

    queue = payloads.get("queue_view")
    if isinstance(queue, dict):
        state_counts = queue.get("state_counts") if isinstance(queue.get("state_counts"), dict) else {}
        blocked_count = int(state_counts.get("BLOCKED", 0) or queue.get("blocked_count", 0) or 0)
        protected_count = int(queue.get("protected_item_count", 0) or 0)
        if blocked_count:
            blockers.append(f"queue_blocked={blocked_count}")
        if protected_count:
            blockers.append(f"queue_protected={protected_count}")
    return sorted(set(blockers))


def evaluate_loop_gates(loop_state: dict[str, Any]) -> dict[str, Any]:
    action = loop_state["proposed_cycle_action"]
    decision = loop_state["governor_decision"]

    unsafe_requested_scope = {
        "proposed_action_title": action.get("proposed_action_title"),
        "allowed_paths": action.get("allowed_paths"),
        "proposed_packet_id": action.get("proposed_packet_id"),
    }
    if _contains_any_unsafe(unsafe_requested_scope):
        return {
            "status": "blocked",
            "reason": "Live trading, broker, credential, webhook, secret, or real-order scope is blocked.",
            "safe_to_dispatch": False,
        }

    dirty_tree = _dirty_tree_payload(loop_state)
    if dirty_tree.get("sos_required") is True:
        return {
            "status": "blocked",
            "reason": "Dirty tree classifier found security SOS indicators; continuation must stop without printing secret values.",
            "safe_to_dispatch": False,
        }

    if dirty_tree.get("protected_stop_required") is True:
        return {
            "status": "blocked",
            "reason": "Dirty tree classifier found protected authority dirty files.",
            "safe_to_dispatch": False,
        }

    if _dirty_tree_is_safe_for_dry_run(loop_state) and action.get("proposed_mode") == "APPLY":
        return {
            "status": "requires_cleanup",
            "reason": "Dirty generated evidence permits READ_ONLY/DRY_RUN only; APPLY remains blocked until the tree is clean.",
            "safe_to_dispatch": False,
        }

    if _repo_dirty(loop_state):
        return {
            "status": "requires_cleanup",
            "reason": "Repo-state evidence or governor decision reports a dirty working tree.",
            "safe_to_dispatch": False,
        }

    if _validator_failure(loop_state):
        return {
            "status": "requires_validator_repair",
            "reason": "Validator evidence is missing, failing, blocked, or selected by the governor for repair.",
            "safe_to_dispatch": False,
        }

    if _apply_approval_missing(loop_state):
        return {
            "status": "requires_human_approval",
            "reason": "The proposed action is APPLY, but explicit scoped Human Owner approval is not present.",
            "safe_to_dispatch": False,
        }

    blockers = _active_blockers(loop_state)
    if blockers:
        return {
            "status": "blocked",
            "reason": "Active blocker evidence is present: " + "; ".join(blockers),
            "safe_to_dispatch": False,
        }

    blocked_reason = decision.get("blocked_reason")
    if decision.get("blocked"):
        if blocked_reason == "apply_approval_missing":
            status = "requires_human_approval"
        elif blocked_reason == "dirty_working_tree":
            status = "requires_cleanup"
        elif decision.get("decision_category") == "VALIDATOR_REPAIR":
            status = "requires_validator_repair"
        else:
            status = "blocked"
        return {
            "status": status,
            "reason": f"Governor blocked the cycle: {blocked_reason or 'blocked_without_reason'}.",
            "safe_to_dispatch": False,
        }

    if action.get("proposed_mode") in {"READ_ONLY", "DRY_RUN"}:
        return {
            "status": "ready_for_dry_run",
            "reason": "The next action is bounded to read-only or DRY_RUN recommendation scope.",
            "safe_to_dispatch": False,
        }

    if action.get("proposed_mode") == "APPLY":
        return {
            "status": "ready_for_apply",
            "reason": "The action is shaped for APPLY, but this loop only recommends and does not dispatch.",
            "safe_to_dispatch": False,
        }

    return {
        "status": "blocked",
        "reason": "No safe proposed mode is available.",
        "safe_to_dispatch": False,
    }


def recommend_next_cycle_action(loop_state: dict[str, Any]) -> dict[str, Any]:
    gate = loop_state.get("gate_result") or evaluate_loop_gates(loop_state)
    action = loop_state["proposed_cycle_action"]
    packet_type_by_status = {
        "ready_for_dry_run": "DRY_RUN_PACKET",
        "ready_for_apply": "APPLY_PACKET_REQUIRES_HUMAN_APPROVAL",
        "blocked": "BLOCKED_STOP_REPORT",
        "requires_human_approval": "HUMAN_APPROVAL_PACKET",
        "requires_cleanup": "REPO_CLEANUP_RECON_PACKET",
        "requires_validator_repair": "VALIDATOR_REPAIR_PACKET",
    }
    human_required = gate["status"] != "ready_for_dry_run"
    return {
        "dispatch_authorized": False,
        "queue_mutation_authorized": False,
        "recommended_next_packet_type": packet_type_by_status.get(gate["status"], "BLOCKED_STOP_REPORT"),
        "recommended_next_packet_id": str(action.get("proposed_packet_id") or "AIOS-NO-SAFE-NEXT-PACKET"),
        "recommended_worker_lane": str(action.get("proposed_lane") or "BLOCKED"),
        "human_action_required": human_required,
        "reason": f"{gate['reason']} Dispatch remains disabled in Closed Autonomy Loop v1.",
    }


def _phase_statuses(inputs: dict[str, Any], loop_state: dict[str, Any]) -> dict[str, str]:
    records = list(inputs.get("inputs") or [])
    present_count = sum(1 for record in records if record.get("status") == "present")
    if not records or present_count == 0:
        observe = "blocked"
    elif present_count == len(records):
        observe = "complete"
    else:
        observe = "partial"

    decision = loop_state["governor_decision"]
    decide = "blocked" if decision.get("blocked_reason") == "governor_decision_missing" else "complete"
    plan = "complete" if loop_state["proposed_cycle_action"].get("proposed_action_id") else "blocked"
    return {
        "observe": observe,
        "decide": decide,
        "plan": plan,
        "validate_gate": "complete",
        "recommend_dispatch": "complete",
        "report": "complete",
        "stop": "complete",
    }


def _loop_id(report_seed: dict[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(report_seed, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]
    return f"AIOS-CLOSED-LOOP-{digest}"


def build_closed_loop_report(repo_root: str | Path, generated_at_utc: str | None = None) -> dict[str, Any]:
    now = generated_at_utc or utc_now()
    inputs = collect_loop_inputs(repo_root, generated_at_utc=now)
    loop_state = build_loop_state(inputs)
    gate = evaluate_loop_gates(loop_state)
    loop_state["gate_result"] = gate
    recommendation = recommend_next_cycle_action(loop_state)
    phase_status = _phase_statuses(inputs, loop_state)
    governor_public = {key: value for key, value in loop_state["governor_decision"].items() if not key.startswith("_")}

    seed = {
        "generated_at_utc": now,
        "inputs": inputs["inputs"],
        "governor_decision": governor_public,
        "proposed_cycle_action": loop_state["proposed_cycle_action"],
        "gate_result": gate,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "system": SYSTEM,
        "component": COMPONENT,
        "mode": MODE,
        "loop_id": _loop_id(seed),
        "generated_at_utc": now,
        "loop_phase_status": phase_status,
        "inputs": inputs["inputs"],
        "governor_decision": governor_public,
        "proposed_cycle_action": loop_state["proposed_cycle_action"],
        "gate_result": gate,
        "dispatch_recommendation": recommendation,
        "safety_boundaries": {
            "continuous_loop": "blocked",
            "worker_dispatch": "recommendation_only",
            "queue_mutation": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
        "next_loop_requirement": (
            "Create a separate tokenized packet for the recommended next action. "
            "Closed Autonomy Loop v1 always stops after this one-cycle evaluation."
        ),
    }


def _resolve_output_path(repo_root: Path, output_path: str | Path) -> Path:
    target = Path(output_path)
    if not target.is_absolute():
        target = repo_root / target
    return target.resolve()


def _is_allowed_output_path(repo_root: Path, output_path: Path) -> bool:
    allowed_path = (repo_root / DEFAULT_OUTPUT_PATH).resolve()
    return output_path == allowed_path


def _write_report(repo_root: Path, report: dict[str, Any], output_path: str | Path) -> Path:
    target = _resolve_output_path(repo_root, output_path)
    if not _is_allowed_output_path(repo_root, target):
        raise ValueError(
            "output_path must be Reports/sandbox/closed_autonomy_loop/AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2, sort_keys=True))
            handle.write("\n")
        os.replace(tmp_name, target)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise
    return target


def materialize_closed_loop_report(
    repo_root: str | Path,
    output_path: str | Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    report = build_closed_loop_report(root, generated_at_utc=generated_at_utc)
    target = _write_report(root, report, output_path or DEFAULT_OUTPUT_PATH)
    return {"report": report, "output_path": str(target.relative_to(root)).replace("\\", "/")}


def main(repo_root: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    return materialize_closed_loop_report(root, output_path=output_path)["report"]


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build one AI_OS closed autonomy loop recommendation report.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument(
        "--output-path",
        default=None,
        help="Optional output path; must be Reports/sandbox/closed_autonomy_loop/AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json.",
    )
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_path=args.output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
