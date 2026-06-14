"""AI_OS active mission cycle and SOS reporter.

This module composes existing closed-loop, packet-drafter, queue-preview, gate,
repo-state, and runtime evidence into one operator-facing one-cycle status
report. It never mutates the real queue, dispatches workers, starts schedulers,
uses credentials, runs webhooks, or enables broker/live-trading behavior.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
SYSTEM = "AI_OS"
COMPONENT = "active_mission_cycle"
MODE = "ONE_CYCLE_SOS_REPORT_ONLY"

DEFAULT_OUTPUT_DIR = Path("Reports") / "sandbox" / "active_mission_cycle"
DEFAULT_JSON_NAME = "AIOS_ACTIVE_MISSION_CYCLE_LATEST.json"
DEFAULT_SOS_NAME = "AIOS_ACTIVE_MISSION_SOS_LATEST.md"

MISSION_INPUT_PATHS = {
    "closed_autonomy_loop": (
        Path("Reports")
        / "sandbox"
        / "closed_autonomy_loop"
        / "AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"
    ),
    "packet_drafter": (
        Path("Reports")
        / "sandbox"
        / "closed_loop_packet_drafter"
        / "AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json"
    ),
    "queue_injection_preview": (
        Path("Reports")
        / "sandbox"
        / "closed_loop_queue_injection_preview"
        / "AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
    ),
    "queue_to_dispatch_gates": (
        Path("Reports")
        / "sandbox"
        / "queue_to_dispatch_gates"
        / "AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json"
    ),
    "repo_state": Path("Reports") / "repo_state" / "AIOS_REPO_STATE_LATEST.json",
    "governor_decision": (
        Path("Reports")
        / "autonomy_decision_governor"
        / "AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json"
    ),
    "validator_router": (
        Path("Reports")
        / "validator_evidence_router"
        / "AIOS_VALIDATOR_EVIDENCE_ROUTER_LATEST.json"
    ),
    "autonomy_status": Path("Reports") / "autonomy_control_plane" / "autonomy_status_report.json",
    "runtime_state": Path("telemetry") / "runtime" / "runtime_state.json",
}

CORE_CHAIN_INPUTS = (
    "closed_autonomy_loop",
    "packet_drafter",
    "queue_injection_preview",
    "queue_to_dispatch_gates",
)

SAFETY_BOUNDARIES = {
    "real_queue_mutation": "blocked",
    "worker_dispatch": "blocked",
    "continuous_loop": "blocked",
    "live_trading": "blocked",
    "broker_execution": "blocked",
    "credential_use": "blocked",
    "webhook_execution": "blocked",
    "scheduler_creation": "blocked",
    "unapproved_mutation": "blocked",
}

UNSAFE_POSITIVE_SCOPE_TERMS = (
    "live trading",
    "live-trading",
    "broker execution",
    "oanda",
    "credential",
    "credentials",
    "api key",
    "secret",
    ".env",
    "real webhook",
    "webhook execution",
    "external webhook",
    "scheduler",
    "startup",
    "background loop",
    "daemon",
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


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _get(payload: Any, *keys: str) -> Any:
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _is_true_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key and item_value is True:
                return True
            if _is_true_key(item_value, key):
                return True
    if isinstance(value, list):
        return any(_is_true_key(item, key) for item in value)
    return False


def _contains_unsafe_positive_scope(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, default=str).lower()
    return any(term in text for term in UNSAFE_POSITIVE_SCOPE_TERMS)


def _summarize_payload(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "Missing or unreadable JSON evidence."

    parts: list[str] = []
    for key in ("component", "mode", "mission_status", "overall_status", "blocked_reason"):
        value = payload.get(key)
        if value not in (None, "", [], {}):
            parts.append(f"{key}={value}")

    gate_status = _get(payload, "gate_result", "status")
    if gate_status:
        parts.append(f"gate={gate_status}")
    validation_blocked = _get(payload, "validation", "blocked")
    if validation_blocked is not None:
        parts.append(f"validation_blocked={validation_blocked}")
    item_status = _get(payload, "proposed_queue_item", "status")
    if item_status:
        parts.append(f"queue_item={item_status}")

    if not parts:
        parts.append("JSON object present")
    return "; ".join(parts)[:240]


def _derive_input_state(name: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"evidence_status": "missing", "reason": f"{name}_missing"}

    if name == "closed_autonomy_loop":
        gate_status = str(_get(payload, "gate_result", "status") or "unknown")
        reason = str(_get(payload, "gate_result", "reason") or "")
        return {"evidence_status": gate_status, "reason": reason}

    if name == "packet_drafter":
        blocked = _get(payload, "validation", "blocked") is True
        reason = str(_get(payload, "validation", "blocked_reason") or "")
        status = "blocked" if blocked else str(_get(payload, "input_status", "recommendation_status") or "ready")
        return {"evidence_status": status, "reason": reason}

    if name == "queue_injection_preview":
        blocked = _get(payload, "validation", "blocked") is True
        reason = str(
            _get(payload, "validation", "blocked_reason")
            or _get(payload, "proposed_queue_item", "blocked_reason")
            or ""
        )
        item_status = str(_get(payload, "proposed_queue_item", "status") or "unknown")
        return {"evidence_status": "blocked" if blocked else item_status, "reason": reason}

    if name == "queue_to_dispatch_gates":
        status = str(payload.get("overall_status") or "unknown")
        reason = str(_get(payload, "validation", "blocked_reason") or "")
        return {"evidence_status": status, "reason": reason}

    if name == "repo_state":
        if payload.get("is_clean") is False:
            return {"evidence_status": "dirty", "reason": str(payload.get("blocked_reason") or "dirty_working_tree")}
        return {"evidence_status": "clean", "reason": ""}

    if name == "governor_decision":
        if payload.get("blocked") is True:
            return {"evidence_status": "blocked", "reason": str(payload.get("blocked_reason") or "governor_blocked")}
        return {"evidence_status": str(payload.get("decision_category") or "present"), "reason": ""}

    return {"evidence_status": "present", "reason": ""}


def collect_mission_inputs(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    records: dict[str, dict[str, Any]] = {}
    payloads: dict[str, Any] = {}

    for name, relative_path in MISSION_INPUT_PATHS.items():
        absolute_path = root / relative_path
        payload = load_json_if_exists(absolute_path)
        status = "present" if isinstance(payload, dict) else "missing"
        state = _derive_input_state(name, payload)
        records[name] = {
            "name": name,
            "path": relative_path.as_posix(),
            "status": status,
            "evidence_status": state["evidence_status"],
            "reason": state["reason"],
            "summary": _summarize_payload(payload),
        }
        payloads[name] = payload if isinstance(payload, dict) else None

    return {
        "repo_root": str(root),
        "inputs": records,
        "payloads": payloads,
    }


def summarize_current_chain(inputs: dict[str, Any]) -> dict[str, Any]:
    records = inputs.get("inputs") if isinstance(inputs.get("inputs"), dict) else {}
    payloads = inputs.get("payloads") if isinstance(inputs.get("payloads"), dict) else {}
    present_inputs = [name for name, record in records.items() if record.get("status") == "present"]
    missing_inputs = [name for name, record in records.items() if record.get("status") == "missing"]

    safety_findings: list[str] = []
    for name, payload in payloads.items():
        if not isinstance(payload, dict):
            continue
        if _is_true_key(payload, "queue_mutation_authorized"):
            safety_findings.append(f"{name}:queue_mutation_authorized_true")
        if _is_true_key(payload, "dispatch_authorized"):
            safety_findings.append(f"{name}:dispatch_authorized_true")

    positive_scope_probe = {
        "closed_loop_allowed_paths": _get(payloads.get("closed_autonomy_loop"), "proposed_cycle_action", "allowed_paths"),
        "packet_blueprint_allowed_paths": _get(payloads.get("packet_drafter"), "packet_blueprint", "allowed_paths"),
        "queue_item_allowed_paths": _get(
            payloads.get("queue_injection_preview"), "proposed_queue_item", "allowed_paths"
        ),
        "validated_queue_item_allowed_paths": _get(
            payloads.get("queue_to_dispatch_gates"), "validated_queue_item", "allowed_paths"
        ),
    }
    if _contains_unsafe_positive_scope(positive_scope_probe):
        safety_findings.append("unsafe_positive_scope_detected")

    return {
        "inputs": records,
        "present_inputs": present_inputs,
        "missing_inputs": missing_inputs,
        "core_chain_missing": [name for name in CORE_CHAIN_INPUTS if name in missing_inputs],
        "safety_locks_intact": not safety_findings,
        "safety_findings": safety_findings,
    }


def _closed_loop_action(payload: Any) -> dict[str, Any]:
    action = _get(payload, "proposed_cycle_action")
    dispatch = _get(payload, "dispatch_recommendation")
    if not isinstance(action, dict):
        action = {}
    if not isinstance(dispatch, dict):
        dispatch = {}
    return {
        "action_id": str(action.get("proposed_action_id") or "AIOS-ACTIVE-MISSION-NO-ACTION"),
        "packet_id": str(
            action.get("proposed_packet_id")
            or dispatch.get("recommended_next_packet_id")
            or "AIOS-ACTIVE-MISSION-NO-PACKET"
        ),
        "title": str(action.get("proposed_action_title") or "Review missing or blocked autonomy evidence."),
        "mode": str(action.get("proposed_mode") or "READ_ONLY"),
        "lane": str(action.get("proposed_lane") or dispatch.get("recommended_worker_lane") or "READ_ONLY"),
        "source": "closed_autonomy_loop",
    }


def _first_upstream_blocker(inputs: dict[str, Any]) -> tuple[str | None, str | None]:
    records = inputs.get("inputs") if isinstance(inputs.get("inputs"), dict) else {}
    payloads = inputs.get("payloads") if isinstance(inputs.get("payloads"), dict) else {}

    checks = (
        "closed_autonomy_loop",
        "packet_drafter",
        "queue_injection_preview",
        "queue_to_dispatch_gates",
    )
    for name in checks:
        record = records.get(name, {})
        payload = payloads.get(name)
        if record.get("status") == "missing":
            return name, f"{name}_missing"
        if name == "closed_autonomy_loop" and _get(payload, "gate_result", "status") == "blocked":
            return name, str(_get(payload, "gate_result", "reason") or "closed_loop_blocked")
        if name == "packet_drafter" and _get(payload, "validation", "blocked") is True:
            return name, str(_get(payload, "validation", "blocked_reason") or "packet_drafter_blocked")
        if name == "queue_injection_preview":
            if _get(payload, "validation", "blocked") is True:
                return name, str(_get(payload, "validation", "blocked_reason") or "queue_preview_blocked")
            if _get(payload, "proposed_queue_item", "status") == "blocked":
                return name, str(_get(payload, "proposed_queue_item", "blocked_reason") or "queue_preview_blocked")
        if name == "queue_to_dispatch_gates":
            if _get(payload, "validation", "blocked") is True:
                return name, str(_get(payload, "validation", "blocked_reason") or "queue_to_dispatch_gates_blocked")
            if payload and payload.get("overall_status") == "blocked":
                return name, "queue_to_dispatch_gates_blocked"
    return None, None


def _repo_requires_cleanup(inputs: dict[str, Any]) -> bool:
    payloads = inputs.get("payloads") if isinstance(inputs.get("payloads"), dict) else {}
    repo_state = payloads.get("repo_state")
    governor = payloads.get("governor_decision")
    closed_loop = payloads.get("closed_autonomy_loop")
    return (
        _get(repo_state, "is_clean") is False
        or _get(repo_state, "blocked_reason") == "dirty_working_tree"
        or _get(governor, "blocked_reason") == "dirty_working_tree"
        or _get(closed_loop, "gate_result", "status") == "requires_cleanup"
    )


def _requires_approval(inputs: dict[str, Any]) -> bool:
    payloads = inputs.get("payloads") if isinstance(inputs.get("payloads"), dict) else {}
    queue_gates = payloads.get("queue_to_dispatch_gates")
    return (
        _get(payloads.get("closed_autonomy_loop"), "gate_result", "status") == "requires_human_approval"
        or _get(payloads.get("packet_drafter"), "dispatch", "human_approval_required") is True
        or _get(payloads.get("queue_injection_preview"), "proposed_queue_item", "approval_required") is True
        or (isinstance(queue_gates, dict) and queue_gates.get("overall_status") == "requires_approval")
    )


def _queue_gates_ready(inputs: dict[str, Any]) -> bool:
    payloads = inputs.get("payloads") if isinstance(inputs.get("payloads"), dict) else {}
    gates = payloads.get("queue_to_dispatch_gates")
    return isinstance(gates, dict) and gates.get("overall_status") in {"preview_only", "requires_approval"}


def select_current_operational_state(inputs: dict[str, Any]) -> dict[str, Any]:
    chain_state = summarize_current_chain(inputs)
    payloads = inputs.get("payloads") if isinstance(inputs.get("payloads"), dict) else {}
    selected_action = _closed_loop_action(payloads.get("closed_autonomy_loop"))

    if not chain_state["safety_locks_intact"]:
        reason = "; ".join(chain_state["safety_findings"])
        return {
            "mission_status": "blocked",
            "selected_next_action": {
                **selected_action,
                "title": "Stop and repair weakened safety lock evidence.",
                "reason": reason,
            },
            "blocked_reason": reason,
            "human_action_required": True,
            "approval_required": False,
            "next_step": "Repair safety-lock evidence before considering any next packet.",
            "why": "A queue, dispatch, or unsafe positive-scope lock was weakened in upstream evidence.",
        }

    if _repo_requires_cleanup(inputs):
        reason = "dirty_working_tree"
        gate_reason = str(_get(payloads.get("closed_autonomy_loop"), "gate_result", "reason") or "")
        if gate_reason:
            reason = f"{reason}: {gate_reason}"
        return {
            "mission_status": "requires_cleanup",
            "selected_next_action": {
                **selected_action,
                "reason": "Repo-state or governor evidence reports a dirty working tree.",
            },
            "blocked_reason": reason,
            "human_action_required": True,
            "approval_required": False,
            "next_step": "Review and classify dirty repo state before continuing the autonomy chain.",
            "why": "Dirty repo evidence has priority over downstream packet or queue previews.",
        }

    blocker_source, blocker_reason = _first_upstream_blocker(inputs)
    if blocker_reason:
        return {
            "mission_status": "blocked",
            "selected_next_action": {
                **selected_action,
                "title": f"Repair upstream evidence from {blocker_source}.",
                "reason": blocker_reason,
            },
            "blocked_reason": blocker_reason,
            "human_action_required": True,
            "approval_required": False,
            "next_step": f"Repair {blocker_source} evidence, then rerun the one-cycle mission report.",
            "why": "The active mission cycle cannot advance while an upstream preview is missing or blocked.",
        }

    if _requires_approval(inputs):
        return {
            "mission_status": "requires_approval",
            "selected_next_action": {
                **selected_action,
                "reason": "The current preview chain is structurally ready but requires Anthony approval.",
            },
            "blocked_reason": None,
            "human_action_required": True,
            "approval_required": True,
            "next_step": "Anthony reviews the packet or queue preview before any real queue or dispatch design.",
            "why": "APPLY-like or approval-gated preview evidence keeps human approval required.",
        }

    if _queue_gates_ready(inputs):
        return {
            "mission_status": "ready_for_next_packet",
            "selected_next_action": {
                **selected_action,
                "reason": "Preview chain is present and safety locks are intact.",
            },
            "blocked_reason": None,
            "human_action_required": True,
            "approval_required": False,
            "next_step": "Draft the next tokenized packet for the recommended preview-only control-plane step.",
            "why": "Closed-loop, packet, queue preview, and queue-to-dispatch gate evidence are available.",
        }

    return {
        "mission_status": "running_preview",
        "selected_next_action": {
            **selected_action,
            "reason": "Evidence is present but the chain has not reached a queue gate conclusion.",
        },
        "blocked_reason": None,
        "human_action_required": False,
        "approval_required": False,
        "next_step": "Continue one-cycle preview reporting only; do not dispatch or mutate queues.",
        "why": "The chain has no blocking evidence and remains in preview-only reporting.",
    }


def build_sos_message(inputs: dict[str, Any], operational_state: dict[str, Any]) -> str:
    chain_state = summarize_current_chain(inputs)
    records = chain_state["inputs"]
    selected = operational_state.get("selected_next_action", {})
    checked_lines = [
        f"- {name}: {record.get('status')} / {record.get('evidence_status')} - {record.get('summary')}"
        for name, record in records.items()
    ]
    blocker = operational_state.get("blocked_reason") or "None for this one-cycle report."
    need = "Review the blocker and approve only the next safe packet after evidence is aligned."
    if operational_state.get("mission_status") == "requires_cleanup":
        need = "Classify or clean the dirty repo state before continuing the autonomy chain."
    elif operational_state.get("mission_status") == "requires_approval":
        need = "Approve or reject the previewed packet or queue step. No dispatch is authorized."
    elif operational_state.get("mission_status") == "ready_for_next_packet":
        need = "Review the recommended next packet direction before any APPLY packet is generated."
    elif operational_state.get("human_action_required") is False:
        need = "No human action is required for this preview-only status readout."

    return "\n".join(
        [
            "# AI_OS Active Mission SOS",
            "",
            "## AI_OS STATUS",
            str(operational_state.get("mission_status")),
            "",
            "## WHAT I CHECKED",
            "\n".join(checked_lines),
            "",
            "## WHAT I SELECTED",
            f"{selected.get('packet_id')} - {selected.get('title')}",
            "",
            "## WHY",
            str(operational_state.get("why") or selected.get("reason") or "No reason recorded."),
            "",
            "## BLOCKER",
            str(blocker),
            "",
            "## WHAT I NEED FROM ANTHONY",
            need,
            "",
            "## NEXT SAFE ACTION",
            str(operational_state.get("next_step")),
            "",
            "## SAFETY LOCKS",
            "- queue_mutation_authorized: false",
            "- dispatch_authorized: false",
            "- live_trading: blocked",
            "- broker_execution: blocked",
            "- continuous_loop: blocked",
            "",
        ]
    )


def _safe_output_dir(repo_root: Path, output_dir: str | Path | None) -> Path:
    target = Path(output_dir) if output_dir is not None else repo_root / DEFAULT_OUTPUT_DIR
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    allowed = (repo_root / DEFAULT_OUTPUT_DIR).resolve()
    if target != allowed:
        raise ValueError("output_dir must be Reports/sandbox/active_mission_cycle")
    return target


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, path)


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def build_active_mission_report(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    generated = generated_at_utc or utc_now()
    inputs = collect_mission_inputs(root)
    chain_state = summarize_current_chain(inputs)
    operational_state = select_current_operational_state(inputs)
    output_root = _safe_output_dir(root, output_dir)
    sos_relative_path = (DEFAULT_OUTPUT_DIR / DEFAULT_SOS_NAME).as_posix()

    report = {
        "schema_version": SCHEMA_VERSION,
        "system": SYSTEM,
        "component": COMPONENT,
        "mode": MODE,
        "generated_at_utc": generated,
        "mission_status": operational_state["mission_status"],
        "current_chain_state": chain_state,
        "selected_next_action": operational_state["selected_next_action"],
        "blocked_reason": operational_state["blocked_reason"],
        "human_action_required": operational_state["human_action_required"],
        "approval_required": operational_state["approval_required"],
        "queue_mutation_authorized": False,
        "dispatch_authorized": False,
        "live_trading": "blocked",
        "broker_execution": "blocked",
        "sos_message_path": sos_relative_path,
        "next_step": operational_state["next_step"],
        "safety_boundaries": SAFETY_BOUNDARIES,
    }

    sos_message = build_sos_message(inputs, operational_state)
    _write_json_atomic(output_root / DEFAULT_JSON_NAME, report)
    _write_text_atomic(output_root / DEFAULT_SOS_NAME, sos_message)
    return report


def main(repo_root: str | Path | None = None, output_dir: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    return build_active_mission_report(root, output_dir=output_dir)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build AI_OS active mission cycle SOS report.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_dir=args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
