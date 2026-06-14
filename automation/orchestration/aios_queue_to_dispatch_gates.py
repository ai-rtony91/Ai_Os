"""AI_OS consolidated queue-to-dispatch gate previews.

Consumes the Closed Loop Queue Injection Preview and builds one conservative
preview report for queue admission, worker dispatch, human approval, and real
queue injection gates. This module never mutates the real queue, dispatches
workers, starts schedulers, runs webhooks, touches credentials, or executes
packet text.
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
COMPONENT = "queue_to_dispatch_gates"
MODE = "APPLY_BUILD_WITH_CONSOLIDATED_GATE_PREVIEW_OUTPUT"

QUEUE_PREVIEW_PATH = (
    Path("Reports")
    / "sandbox"
    / "closed_loop_queue_injection_preview"
    / "AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
)
DEFAULT_OUTPUT_PATH = (
    Path("Reports")
    / "sandbox"
    / "queue_to_dispatch_gates"
    / "AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json"
)

REQUIRED_QUEUE_ITEM_FIELDS = [
    "queue_item_id",
    "packet_id",
    "mode",
    "lane",
    "risk_level",
    "approval_required",
    "approval_authority",
    "validators_required",
    "allowed_paths",
    "forbidden_paths",
    "stop_conditions",
    "dispatch_authorized",
    "queue_mutation_authorized",
    "status",
]

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

UNSAFE_SCOPE_TERMS = (
    "live trading",
    "live-trading",
    "broker execution",
    "broker",
    "oanda",
    "credential",
    "credentials",
    "api key",
    "token",
    "secret",
    ".env",
    "real webhook",
    "webhook execution",
    "external webhook",
    "scheduler",
    "startup",
    "background loop",
    "daemon",
    "git add",
    "git commit",
    "git push",
    "git merge",
    "git reset",
    "git checkout",
    "git clean",
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


def _contains_unsafe_scope(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, default=str).lower()
    return any(term in text for term in UNSAFE_SCOPE_TERMS)


def _safe_output_path(repo_root: Path, output_path: str | Path | None) -> Path:
    target = Path(output_path) if output_path is not None else repo_root / DEFAULT_OUTPUT_PATH
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    allowed = (repo_root / DEFAULT_OUTPUT_PATH).resolve()
    if target != allowed:
        raise ValueError("output_path must be Reports/sandbox/queue_to_dispatch_gates/AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json")
    return target


def load_queue_injection_preview(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    payload = load_json_if_exists(root / QUEUE_PREVIEW_PATH)
    if not isinstance(payload, dict):
        return {
            "status": "missing",
            "report": None,
            "path": str(QUEUE_PREVIEW_PATH.as_posix()),
            "reason": "missing_queue_injection_preview",
        }

    item = payload.get("proposed_queue_item")
    validation = payload.get("validation")
    status = "present"
    reason = None
    if isinstance(item, dict) and item.get("status") == "blocked":
        status = "blocked"
        reason = str(item.get("blocked_reason") or "queue_injection_preview_blocked")
    elif isinstance(validation, dict) and validation.get("blocked") is True:
        status = "blocked"
        reason = str(validation.get("blocked_reason") or "queue_injection_preview_blocked")
    return {
        "status": status,
        "report": payload,
        "path": str(QUEUE_PREVIEW_PATH.as_posix()),
        "reason": reason,
    }


def normalize_queue_item(queue_preview: Any) -> dict[str, Any]:
    if not isinstance(queue_preview, dict):
        return {
            "status": "missing",
            "item": {},
            "missing_fields": ["proposed_queue_item"],
            "blocked_reason": "missing_queue_injection_preview",
        }

    item = queue_preview.get("proposed_queue_item")
    if not isinstance(item, dict):
        return {
            "status": "missing",
            "item": {},
            "missing_fields": ["proposed_queue_item"],
            "blocked_reason": "missing_proposed_queue_item",
        }

    missing = [field for field in REQUIRED_QUEUE_ITEM_FIELDS if item.get(field) in (None, "", [], {})]
    if item.get("queue_mutation_authorized") is not False:
        missing.append("queue_mutation_authorized_false")
    if item.get("dispatch_authorized") is not False:
        missing.append("dispatch_authorized_false")

    mode = str(item.get("mode") or "").upper()
    apply_like = mode == "APPLY" or "APPLY" in str(item.get("lane") or "").upper()
    if apply_like and item.get("approval_required") is not True:
        missing.append("apply_requires_anthony_approval")
    if item.get("approval_required") is True and str(item.get("approval_authority") or "") != "Anthony Meza":
        missing.append("approval_authority_anthony_meza")

    unsafe_probe = {
        "packet_id": item.get("packet_id"),
        "mode": item.get("mode"),
        "lane": item.get("lane"),
        "risk_level": item.get("risk_level"),
        "allowed_paths": item.get("allowed_paths"),
        "validators_required": item.get("validators_required"),
        "stop_conditions": item.get("stop_conditions"),
    }
    if _contains_unsafe_scope(unsafe_probe):
        missing.append("unsafe_scope_blocked")

    status = "present" if not missing else "invalid"
    blocked_reason = None if not missing else "invalid_queue_item"
    if item.get("status") == "blocked":
        status = "invalid"
        blocked_reason = str(item.get("blocked_reason") or "queue_preview_blocked")

    return {
        "status": status,
        "item": item,
        "missing_fields": missing,
        "blocked_reason": blocked_reason,
        "apply_like": apply_like,
    }


def _gate(status: str, reason: str, human_approval_required: bool = True) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "queue_mutation_authorized": False,
        "dispatch_authorized": False,
        "human_approval_required": bool(human_approval_required),
    }


def evaluate_gates(normalized: dict[str, Any]) -> dict[str, Any]:
    item = normalized.get("item") if isinstance(normalized.get("item"), dict) else {}
    if normalized.get("status") in {"missing", "invalid"}:
        reason = str(normalized.get("blocked_reason") or "queue_item_invalid")
        return {
            "queue_admission_preview": _gate("blocked", reason),
            "worker_dispatch_preview": _gate("blocked", reason),
            "human_approval_preview": _gate("blocked", reason),
            "real_queue_injection_gate_preview": _gate("blocked", reason),
        }

    approval_required = bool(item.get("approval_required")) or bool(normalized.get("apply_like"))
    if approval_required:
        admission_status = "requires_approval"
        admission_reason = "Anthony approval required before any real queue or dispatch action"
    else:
        admission_status = "preview_only"
        admission_reason = "queue item is structurally valid for preview-only admission"

    human_status = "requires_approval" if approval_required else "preview_only"
    human_reason = "Anthony approval required for APPLY-like work" if approval_required else "no APPLY approval needed for this preview"

    return {
        "queue_admission_preview": _gate(admission_status, admission_reason, approval_required),
        "worker_dispatch_preview": _gate(
            "requires_approval" if approval_required else "preview_only",
            "worker dispatch remains preview-only; no worker launch authorized",
            approval_required,
        ),
        "human_approval_preview": _gate(human_status, human_reason, approval_required),
        "real_queue_injection_gate_preview": _gate(
            "requires_approval" if approval_required else "preview_only",
            "real queue injection remains blocked; this is gate evidence only",
            True,
        ),
    }


def _overall_status(gates: dict[str, Any]) -> str:
    statuses = {str(gate.get("status")) for gate in gates.values() if isinstance(gate, dict)}
    if "blocked" in statuses:
        return "blocked"
    if "requires_approval" in statuses:
        return "requires_approval"
    return "preview_only"


def _validated_queue_item(normalized: dict[str, Any]) -> dict[str, Any]:
    item = normalized.get("item")
    if not isinstance(item, dict):
        return {}
    return {
        "queue_item_id": item.get("queue_item_id"),
        "packet_id": item.get("packet_id"),
        "mode": item.get("mode"),
        "lane": item.get("lane"),
        "risk_level": item.get("risk_level"),
        "approval_required": item.get("approval_required"),
        "approval_authority": item.get("approval_authority"),
        "validators_required": _as_list(item.get("validators_required")),
        "allowed_paths": _as_list(item.get("allowed_paths")),
        "forbidden_paths": _as_list(item.get("forbidden_paths")),
        "stop_conditions": _as_list(item.get("stop_conditions")),
        "status": item.get("status"),
        "blocked_reason": item.get("blocked_reason"),
        "queue_mutation_authorized": False,
        "dispatch_authorized": False,
    }


def _validation(normalized: dict[str, Any], overall_status: str) -> dict[str, Any]:
    missing = list(normalized.get("missing_fields") or [])
    blocked = overall_status == "blocked"
    return {
        "required_fields_present": not missing,
        "missing_fields": missing,
        "blocked": blocked,
        "blocked_reason": str(normalized.get("blocked_reason") or "queue_to_dispatch_gates_blocked") if blocked else None,
    }


def _input_status(load_result: dict[str, Any], normalized: dict[str, Any]) -> dict[str, str]:
    return {
        "queue_injection_preview": str(load_result.get("status") or "missing"),
        "proposed_queue_item": str(normalized.get("status") or "missing"),
    }


def _next_step(overall_status: str) -> str:
    if overall_status == "blocked":
        return "Repair queue injection preview evidence before running consolidated gates again."
    if overall_status == "requires_approval":
        return "Anthony reviews the consolidated gate preview; no queue mutation or dispatch is authorized."
    return "Use this as preview evidence only; real queue injection and worker dispatch remain blocked."


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


def build_queue_to_dispatch_gates_report(
    repo_root: str | Path,
    output_path: str | Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    target = _safe_output_path(root, output_path)
    now = generated_at_utc or utc_now()

    load_result = load_queue_injection_preview(root)
    normalized = normalize_queue_item(load_result.get("report"))
    if load_result.get("status") == "missing":
        normalized["status"] = "missing"
        normalized["missing_fields"] = ["proposed_queue_item"]
        normalized["blocked_reason"] = "missing_queue_injection_preview"
    elif load_result.get("status") == "blocked" and normalized.get("status") != "invalid":
        normalized["status"] = "invalid"
        normalized["blocked_reason"] = str(load_result.get("reason") or "queue_injection_preview_blocked")

    gates = evaluate_gates(normalized)
    overall_status = _overall_status(gates)
    report = {
        "schema_version": SCHEMA_VERSION,
        "system": SYSTEM,
        "component": COMPONENT,
        "mode": MODE,
        "generated_at_utc": now,
        "input_status": _input_status(load_result, normalized),
        "overall_status": overall_status,
        "validated_queue_item": _validated_queue_item(normalized),
        "gates": gates,
        "validation": _validation(normalized, overall_status),
        "safety_boundaries": SAFETY_BOUNDARIES.copy(),
        "next_step": _next_step(overall_status),
    }

    _write_json_atomic(target, report)
    return report


def main(repo_root: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    return build_queue_to_dispatch_gates_report(root, output_path=output_path)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build AI_OS consolidated queue-to-dispatch gate previews.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output-path", default=None, help="Exact sandbox output path.")
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_path=args.output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
