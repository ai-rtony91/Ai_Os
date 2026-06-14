"""AI_OS executive control readiness consolidator.

Reads existing autonomy, packet-drafter, queue-preview, and queue-to-dispatch
gate evidence, then reports whether AI_OS is ready to design
Start/Pause/Resume/Stop controls. This module never mutates real queues,
dispatches workers, starts schedulers, executes webhooks, touches credentials,
or implements on/off controls.
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
COMPONENT = "executive_control_readiness"
MODE = "APPLY_BUILD_WITH_CONTROL_READINESS_OUTPUT"

GOVERNOR_REPORT = Path("Reports") / "autonomy_decision_governor" / "AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json"
CLOSED_LOOP_REPORT = Path("Reports") / "sandbox" / "closed_autonomy_loop" / "AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"
PACKET_DRAFTER_REPORT = (
    Path("Reports") / "sandbox" / "closed_loop_packet_drafter" / "AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json"
)
QUEUE_PREVIEW_REPORT = (
    Path("Reports") / "sandbox" / "closed_loop_queue_injection_preview" / "AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
)
QUEUE_DISPATCH_GATES_REPORT = (
    Path("Reports") / "sandbox" / "queue_to_dispatch_gates" / "AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json"
)
DEFAULT_OUTPUT_PATH = (
    Path("Reports") / "sandbox" / "executive_control_readiness" / "AIOS_EXECUTIVE_CONTROL_READINESS.json"
)

REPORT_SPECS: tuple[tuple[str, Path, str], ...] = (
    ("governor", GOVERNOR_REPORT, "autonomy_decision_governor"),
    ("closed_loop", CLOSED_LOOP_REPORT, "closed_autonomy_loop"),
    ("packet_drafter", PACKET_DRAFTER_REPORT, "closed_loop_packet_drafter"),
    ("queue_preview", QUEUE_PREVIEW_REPORT, "closed_loop_queue_injection_preview"),
    ("queue_dispatch_gates", QUEUE_DISPATCH_GATES_REPORT, "queue_to_dispatch_gates"),
)

SAFETY_BOUNDARIES = {
    "real_queue_mutation": "blocked",
    "worker_dispatch": "blocked",
    "continuous_loop": "blocked",
    "start_pause_resume_stop_implementation": "blocked",
    "live_trading": "blocked",
    "broker_execution": "blocked",
    "credential_use": "blocked",
    "webhook_execution": "blocked",
    "scheduler_creation": "blocked",
    "unapproved_mutation": "blocked",
}

UNSAFE_TRUE_FIELDS = {
    "dispatch_authorized",
    "queue_mutation_authorized",
    "safe_to_dispatch",
    "dispatch_allowed",
    "queue_mutation_allowed",
    "real_queue_mutation_allowed",
    "worker_dispatch_allowed",
    "continuous_loop_allowed",
    "scheduler_creation_allowed",
    "live_trading_allowed",
    "broker_execution_allowed",
    "credential_use_allowed",
    "webhook_execution_allowed",
}

REQUIRED_GATE_NAMES = (
    "queue_admission_preview",
    "worker_dispatch_preview",
    "human_approval_preview",
    "real_queue_injection_gate_preview",
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


def _status(value: Any) -> str:
    return str(value or "").strip().lower()


def _as_bool(value: Any) -> bool:
    return value is True


def _flatten_true_unsafe_flags(value: Any, prefix: str = "") -> list[str]:
    flags: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in UNSAFE_TRUE_FIELDS and item is True:
                flags.append(path)
            flags.extend(_flatten_true_unsafe_flags(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            flags.extend(_flatten_true_unsafe_flags(item, f"{prefix}[{index}]"))
    return flags


def _boundary_is_blocked(payload: dict[str, Any], key: str) -> bool:
    boundaries = payload.get("safety_boundaries")
    if not isinstance(boundaries, dict):
        return False
    return boundaries.get(key) == "blocked"


def _safe_worker_dispatch_boundary(payload: dict[str, Any]) -> bool:
    boundaries = payload.get("safety_boundaries")
    if not isinstance(boundaries, dict):
        return False
    return boundaries.get("worker_dispatch") in {"blocked", "recommendation_only"}


def _safe_queue_boundary(payload: dict[str, Any]) -> bool:
    boundaries = payload.get("safety_boundaries")
    if not isinstance(boundaries, dict):
        return False
    return boundaries.get("queue_mutation") == "blocked" or boundaries.get("real_queue_mutation") == "blocked"


def _common_safety_blockers(name: str, payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return [f"{name}: report is missing or not a JSON object"]

    blockers = [f"{name}: unsafe true flag {flag}" for flag in _flatten_true_unsafe_flags(payload)]
    for key in ("live_trading", "broker_execution", "credential_use"):
        if not _boundary_is_blocked(payload, key):
            blockers.append(f"{name}: safety boundary {key} is missing or not blocked")
    if name != "governor" and not _safe_worker_dispatch_boundary(payload):
        blockers.append(f"{name}: worker_dispatch safety boundary is missing or not blocked/recommendation_only")
    if name in {"closed_loop", "packet_drafter", "queue_preview", "queue_dispatch_gates"} and not _safe_queue_boundary(payload):
        blockers.append(f"{name}: queue mutation safety boundary is missing or not blocked")
    return blockers


def _input_record(name: str, path: Path, expected_component: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "name": name,
            "path": path.as_posix(),
            "status": "missing",
            "component": None,
            "summary": "Missing or unreadable JSON evidence.",
        }
    component = payload.get("component")
    status = "present" if component == expected_component else "invalid"
    return {
        "name": name,
        "path": path.as_posix(),
        "status": status,
        "component": component,
        "summary": f"component={component}; schema_version={payload.get('schema_version') or payload.get('schema')}",
    }


def collect_readiness_inputs(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    inputs: dict[str, dict[str, Any]] = {}
    for name, rel_path, expected_component in REPORT_SPECS:
        payload = load_json_if_exists(root / rel_path)
        inputs[name] = {
            "payload": payload,
            "record": _input_record(name, rel_path, expected_component, payload),
        }
    return {"repo_root": str(root), "inputs": inputs}


def _governor_ready(payload: Any) -> tuple[bool, list[str]]:
    blockers = _common_safety_blockers("governor", payload)
    if not isinstance(payload, dict):
        return False, blockers
    if payload.get("component") != "autonomy_decision_governor":
        blockers.append("governor: component mismatch")
    if payload.get("blocked") is True:
        blockers.append(f"governor: blocked={payload.get('blocked_reason') or 'true'}")
    if str(payload.get("allowed_lane") or "").upper() == "BLOCKED":
        blockers.append("governor: allowed_lane is BLOCKED")
    return not blockers, blockers


def _closed_loop_ready(payload: Any) -> tuple[bool, list[str]]:
    blockers = _common_safety_blockers("closed_loop", payload)
    if not isinstance(payload, dict):
        return False, blockers
    if payload.get("component") != "closed_autonomy_loop":
        blockers.append("closed_loop: component mismatch")
    phases = payload.get("loop_phase_status") if isinstance(payload.get("loop_phase_status"), dict) else {}
    if phases.get("stop") != "complete":
        blockers.append("closed_loop: one-cycle stop is not complete")
    gate = payload.get("gate_result") if isinstance(payload.get("gate_result"), dict) else {}
    if gate.get("status") not in {"ready_for_dry_run", "ready_for_apply"}:
        blockers.append(f"closed_loop: gate status is {gate.get('status') or 'missing'}")
    dispatch = payload.get("dispatch_recommendation") if isinstance(payload.get("dispatch_recommendation"), dict) else {}
    if dispatch.get("dispatch_authorized") is not False:
        blockers.append("closed_loop: dispatch_authorized is not false")
    if dispatch.get("queue_mutation_authorized") is not False:
        blockers.append("closed_loop: queue_mutation_authorized is not false")
    if payload.get("mode") != "ONE_CYCLE_RECOMMENDATION_ONLY":
        blockers.append("closed_loop: mode is not one-cycle recommendation-only")
    return not blockers, blockers


def _packet_drafter_ready(payload: Any) -> tuple[bool, list[str]]:
    blockers = _common_safety_blockers("packet_drafter", payload)
    if not isinstance(payload, dict):
        return False, blockers
    if payload.get("component") != "closed_loop_packet_drafter":
        blockers.append("packet_drafter: component mismatch")
    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    if validation.get("blocked") is True:
        blockers.append(f"packet_drafter: blocked={validation.get('blocked_reason') or 'true'}")
    if validation.get("agents_required_fields_present") is not True:
        blockers.append("packet_drafter: AGENTS-required fields are not confirmed present")
    dispatch = payload.get("dispatch") if isinstance(payload.get("dispatch"), dict) else {}
    if dispatch.get("dispatch_authorized") is not False:
        blockers.append("packet_drafter: dispatch_authorized is not false")
    if dispatch.get("queue_mutation_authorized") is not False:
        blockers.append("packet_drafter: queue_mutation_authorized is not false")
    return not blockers, blockers


def _queue_preview_ready(payload: Any) -> tuple[bool, list[str]]:
    blockers = _common_safety_blockers("queue_preview", payload)
    if not isinstance(payload, dict):
        return False, blockers
    if payload.get("component") != "closed_loop_queue_injection_preview":
        blockers.append("queue_preview: component mismatch")
    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    if validation.get("blocked") is True:
        blockers.append(f"queue_preview: blocked={validation.get('blocked_reason') or 'true'}")
    item = payload.get("proposed_queue_item") if isinstance(payload.get("proposed_queue_item"), dict) else {}
    if item.get("status") == "blocked":
        blockers.append(f"queue_preview: proposed queue item blocked={item.get('blocked_reason') or 'true'}")
    if item.get("dispatch_authorized") is not False:
        blockers.append("queue_preview: proposed queue item dispatch_authorized is not false")
    if item.get("queue_mutation_authorized") is not False:
        blockers.append("queue_preview: proposed queue item queue_mutation_authorized is not false")
    return not blockers, blockers


def _queue_dispatch_gates_ready(payload: Any) -> tuple[bool, list[str]]:
    blockers = _common_safety_blockers("queue_dispatch_gates", payload)
    if not isinstance(payload, dict):
        return False, blockers
    if payload.get("component") != "queue_to_dispatch_gates":
        blockers.append("queue_dispatch_gates: component mismatch")
    if payload.get("overall_status") == "blocked":
        blockers.append(f"queue_dispatch_gates: overall_status blocked={payload.get('validation', {}).get('blocked_reason')}")
    validation = payload.get("validation") if isinstance(payload.get("validation"), dict) else {}
    if validation.get("blocked") is True:
        blockers.append(f"queue_dispatch_gates: validation blocked={validation.get('blocked_reason') or 'true'}")
    gates = payload.get("gates") if isinstance(payload.get("gates"), dict) else {}
    for gate_name in REQUIRED_GATE_NAMES:
        gate = gates.get(gate_name) if isinstance(gates.get(gate_name), dict) else {}
        if not gate:
            blockers.append(f"queue_dispatch_gates: missing gate {gate_name}")
            continue
        if gate.get("status") == "blocked":
            blockers.append(f"queue_dispatch_gates: gate {gate_name} is blocked")
        if gate.get("dispatch_authorized") is not False:
            blockers.append(f"queue_dispatch_gates: gate {gate_name} dispatch_authorized is not false")
        if gate.get("queue_mutation_authorized") is not False:
            blockers.append(f"queue_dispatch_gates: gate {gate_name} queue_mutation_authorized is not false")
    return not blockers, blockers


def evaluate_control_readiness(collected: dict[str, Any]) -> dict[str, Any]:
    inputs = collected.get("inputs") if isinstance(collected.get("inputs"), dict) else {}
    checks: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []

    evaluators = {
        "governor": _governor_ready,
        "closed_loop": _closed_loop_ready,
        "packet_drafter": _packet_drafter_ready,
        "queue_preview": _queue_preview_ready,
        "queue_dispatch_gates": _queue_dispatch_gates_ready,
    }
    for name, evaluator in evaluators.items():
        payload = inputs.get(name, {}).get("payload") if isinstance(inputs.get(name), dict) else None
        ready, reasons = evaluator(payload)
        checks[name] = {"ready": ready, "blockers": reasons}
        blockers.extend(reasons)

    if blockers:
        readiness_status = "blocked"
    elif all(check["ready"] for check in checks.values()):
        readiness_status = "ready_for_control_plane_design"
    else:
        readiness_status = "partial"

    return {
        "governor_ready": checks["governor"]["ready"],
        "closed_loop_ready": checks["closed_loop"]["ready"],
        "packet_drafter_ready": checks["packet_drafter"]["ready"],
        "queue_preview_ready": checks["queue_preview"]["ready"],
        "queue_dispatch_gates_ready": checks["queue_dispatch_gates"]["ready"],
        "readiness_checks": checks,
        "blockers": blockers,
        "readiness_status": readiness_status,
    }


def _next_step(readiness_status: str, blockers: list[str]) -> str:
    if readiness_status == "ready_for_control_plane_design":
        return "Draft Start/Pause/Resume/Stop control-plane design as preview-only; do not implement controls yet."
    if any("closed_loop_report_missing" in blocker for blocker in blockers):
        return "Align packet drafter and downstream previews to current closed-loop report evidence before control-plane design."
    if blockers:
        return "Repair blocked upstream autonomy and queue preview evidence before designing Start/Pause/Resume/Stop controls."
    return "Complete missing readiness evidence before control-plane design."


def _safe_output_path(repo_root: Path, output_path: str | Path | None) -> Path:
    target = Path(output_path) if output_path is not None else repo_root / DEFAULT_OUTPUT_PATH
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    allowed = (repo_root / DEFAULT_OUTPUT_PATH).resolve()
    if target != allowed:
        raise ValueError(
            "output_path must be Reports/sandbox/executive_control_readiness/AIOS_EXECUTIVE_CONTROL_READINESS.json"
        )
    return target


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def build_executive_control_readiness_report(
    repo_root: str | Path,
    output_path: str | Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    target = _safe_output_path(root, output_path)
    now = generated_at_utc or utc_now()
    collected = collect_readiness_inputs(root)
    evaluation = evaluate_control_readiness(collected)
    input_status = {
        name: data["record"]
        for name, data in collected["inputs"].items()
        if isinstance(data, dict) and isinstance(data.get("record"), dict)
    }

    report = {
        "schema_version": SCHEMA_VERSION,
        "system": SYSTEM,
        "component": COMPONENT,
        "mode": MODE,
        "generated_at_utc": now,
        "input_status": input_status,
        "governor_ready": evaluation["governor_ready"],
        "closed_loop_ready": evaluation["closed_loop_ready"],
        "packet_drafter_ready": evaluation["packet_drafter_ready"],
        "queue_preview_ready": evaluation["queue_preview_ready"],
        "queue_dispatch_gates_ready": evaluation["queue_dispatch_gates_ready"],
        "readiness_checks": evaluation["readiness_checks"],
        "blockers": evaluation["blockers"],
        "readiness_status": evaluation["readiness_status"],
        "next_step": _next_step(evaluation["readiness_status"], evaluation["blockers"]),
        "safety_boundaries": SAFETY_BOUNDARIES.copy(),
    }
    _write_json_atomic(target, report)
    return report


def main(repo_root: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    return build_executive_control_readiness_report(root, output_path=output_path)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build AI_OS executive control readiness report.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output-path", default=None, help="Exact sandbox output path.")
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_path=args.output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
