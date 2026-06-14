"""AI_OS Closed Loop Queue Injection Preview.

Consumes the Closed Loop Packet Drafter preview and renders a proposed queue
item preview. This module never mutates the real queue, enqueues packets,
dispatches workers, starts schedulers, or executes packet text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
SYSTEM = "AI_OS"
COMPONENT = "closed_loop_queue_injection_preview"
MODE = "APPLY_BUILD_WITH_QUEUE_PREVIEW_OUTPUT"

PACKET_DRAFTER_PREVIEW = (
    Path("Reports")
    / "sandbox"
    / "closed_loop_packet_drafter"
    / "AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json"
)
DEFAULT_OUTPUT_PATH = (
    Path("Reports")
    / "sandbox"
    / "closed_loop_queue_injection_preview"
    / "AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
)

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

REQUIRED_QUEUE_ITEM_FIELDS = [
    "queue_item_id",
    "source_component",
    "source_preview_path",
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
    "blocked_reason",
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


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _contains_unsafe_scope(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, default=str).lower()
    return any(term in text for term in UNSAFE_SCOPE_TERMS)


def _stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12].upper()


def _safe_output_path(repo_root: Path, output_path: str | Path | None) -> Path:
    target = Path(output_path) if output_path is not None else repo_root / DEFAULT_OUTPUT_PATH
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    allowed = (repo_root / DEFAULT_OUTPUT_PATH).resolve()
    if target != allowed:
        raise ValueError("output_path must be Reports/sandbox/closed_loop_queue_injection_preview/AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json")
    return target


def load_packet_drafter_preview(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    payload = load_json_if_exists(root / PACKET_DRAFTER_PREVIEW)
    if not isinstance(payload, dict):
        return {
            "status": "missing",
            "report": None,
            "path": str(PACKET_DRAFTER_PREVIEW.as_posix()),
            "reason": "missing_packet_drafter_preview",
        }

    validation = payload.get("validation")
    status = "present"
    reason = None
    if isinstance(validation, dict) and validation.get("blocked") is True:
        status = "blocked"
        reason = str(validation.get("blocked_reason") or "packet_drafter_preview_blocked")

    return {
        "status": status,
        "report": payload,
        "path": str(PACKET_DRAFTER_PREVIEW.as_posix()),
        "reason": reason,
    }


def normalize_packet_blueprint(packet_drafter_report: Any) -> dict[str, Any]:
    if not isinstance(packet_drafter_report, dict):
        return {
            "status": "missing",
            "blocked_reason": "missing_packet_drafter_preview",
            "blueprint": {},
            "human_approval_required": True,
        }

    blueprint = packet_drafter_report.get("packet_blueprint")
    dispatch = packet_drafter_report.get("dispatch")
    validation = packet_drafter_report.get("validation")
    if not isinstance(blueprint, dict):
        return {
            "status": "missing",
            "blocked_reason": "packet_blueprint_missing",
            "blueprint": {},
            "human_approval_required": True,
        }

    required = ("packet_id", "mode", "lane", "risk_level", "allowed_paths", "forbidden_paths", "validator_chain", "stop_point")
    missing = [field for field in required if blueprint.get(field) in (None, "", [], {})]
    unsafe_probe = {
        "packet_id": blueprint.get("packet_id"),
        "mode": blueprint.get("mode"),
        "lane": blueprint.get("lane"),
        "risk_level": blueprint.get("risk_level"),
        "allowed_paths": blueprint.get("allowed_paths"),
    }
    unsafe = _contains_unsafe_scope(unsafe_probe)

    status = "present"
    blocked_reason = None
    if missing:
        status = "invalid"
        blocked_reason = "packet_blueprint_missing_fields: " + ", ".join(missing)
    elif unsafe:
        status = "invalid"
        blocked_reason = "unsafe_scope_blocked"
    elif isinstance(validation, dict) and validation.get("blocked") is True:
        status = "invalid"
        blocked_reason = str(validation.get("blocked_reason") or "packet_drafter_preview_blocked")

    human_approval_required = True
    if isinstance(dispatch, dict):
        human_approval_required = bool(dispatch.get("human_approval_required", True))

    return {
        "status": status,
        "blocked_reason": blocked_reason,
        "blueprint": blueprint,
        "human_approval_required": human_approval_required,
    }


def build_proposed_queue_item(packet_drafter_report: Any) -> dict[str, Any]:
    normalized = normalize_packet_blueprint(packet_drafter_report)
    blueprint = normalized["blueprint"]

    packet_id = str(blueprint.get("packet_id") or "AIOS-CLOSED-LOOP-PACKET-DRAFTER-PREVIEW-MISSING")
    validators = _as_list(blueprint.get("validator_chain")) or ["git diff --check"]
    allowed_paths = _as_list(blueprint.get("allowed_paths")) or ["Reports/sandbox/closed_loop_packet_drafter/"]
    forbidden_paths = _as_list(blueprint.get("forbidden_paths")) or ["automation/orchestration/work_packets/"]
    stop_point = str(blueprint.get("stop_point") or "Stop before queue mutation, worker dispatch, commit, push, or merge.")
    status = "preview_only"
    blocked_reason = None

    if normalized["status"] != "present":
        status = "blocked"
        blocked_reason = normalized["blocked_reason"]
    elif normalized["human_approval_required"]:
        status = "requires_approval"

    queue_item_id = "AIOS-QUEUE-PREVIEW-" + _stable_hash(
        {
            "packet_id": packet_id,
            "mode": blueprint.get("mode"),
            "lane": blueprint.get("lane"),
            "risk_level": blueprint.get("risk_level"),
            "allowed_paths": allowed_paths,
            "forbidden_paths": forbidden_paths,
            "status": status,
            "blocked_reason": blocked_reason,
        }
    )

    return {
        "queue_item_id": queue_item_id,
        "source_component": "closed_loop_packet_drafter",
        "source_preview_path": str(PACKET_DRAFTER_PREVIEW.as_posix()),
        "packet_id": packet_id,
        "mode": str(blueprint.get("mode") or "DRY_RUN"),
        "lane": str(blueprint.get("lane") or "closed_loop_packet_preview"),
        "risk_level": str(blueprint.get("risk_level") or "blocked"),
        "approval_required": True if status in {"blocked", "requires_approval"} else bool(normalized["human_approval_required"]),
        "approval_authority": "Anthony Meza",
        "validators_required": validators,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "stop_conditions": [stop_point],
        "dispatch_authorized": False,
        "queue_mutation_authorized": False,
        "status": status,
        "blocked_reason": blocked_reason,
    }


def validate_queue_preview(queue_preview: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    item = queue_preview.get("proposed_queue_item") if isinstance(queue_preview.get("proposed_queue_item"), dict) else {}
    for field in REQUIRED_QUEUE_ITEM_FIELDS:
        if field == "blocked_reason":
            if field not in item:
                missing.append(field)
            continue
        if item.get(field) in (None, "", [], {}):
            missing.append(field)

    if item.get("dispatch_authorized") is not False:
        missing.append("dispatch_authorized_false")
    if item.get("queue_mutation_authorized") is not False:
        missing.append("queue_mutation_authorized_false")
    unsafe_probe = {
        "packet_id": item.get("packet_id"),
        "mode": item.get("mode"),
        "lane": item.get("lane"),
        "risk_level": item.get("risk_level"),
        "allowed_paths": item.get("allowed_paths"),
    }
    if _contains_unsafe_scope(unsafe_probe):
        missing.append("unsafe_scope_blocked")
    if item.get("status") not in {"preview_only", "blocked", "requires_approval"}:
        missing.append("valid_status")

    blocked = bool(missing) or item.get("status") == "blocked"
    blocked_reason = None
    if missing:
        blocked_reason = "queue_preview_validation_failed"
    elif item.get("status") == "blocked":
        blocked_reason = item.get("blocked_reason") or "queue_preview_blocked"

    return {
        "required_fields_present": not missing,
        "missing_fields": missing,
        "blocked": blocked,
        "blocked_reason": blocked_reason,
    }


def _input_status(load_result: dict[str, Any], normalized: dict[str, Any]) -> dict[str, str]:
    return {
        "packet_drafter_preview": str(load_result.get("status") or "missing"),
        "packet_blueprint": str(normalized.get("status") or "missing"),
    }


def _next_step(item: dict[str, Any]) -> str:
    if item.get("status") == "blocked":
        return "Repair packet drafter preview evidence before queue admission review."
    if item.get("status") == "requires_approval":
        return "Anthony reviews queue item preview; real queue mutation remains blocked until a separate queue admission gate approves it."
    return "Run a future queue admission gate preview before any real queue mutation."


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


def build_queue_injection_preview_report(
    repo_root: str | Path,
    output_path: str | Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    now = generated_at_utc or utc_now()
    target = _safe_output_path(root, output_path)

    load_result = load_packet_drafter_preview(root)
    packet_report = load_result.get("report")
    normalized = normalize_packet_blueprint(packet_report)
    proposed_item = build_proposed_queue_item(packet_report)

    if load_result.get("status") == "missing":
        proposed_item["status"] = "blocked"
        proposed_item["blocked_reason"] = "missing_packet_drafter_preview"
    elif load_result.get("status") == "blocked" and proposed_item["blocked_reason"] is None:
        proposed_item["status"] = "blocked"
        proposed_item["blocked_reason"] = str(load_result.get("reason") or "packet_drafter_preview_blocked")

    report = {
        "schema_version": SCHEMA_VERSION,
        "system": SYSTEM,
        "component": COMPONENT,
        "mode": MODE,
        "generated_at_utc": now,
        "input_status": _input_status(load_result, normalized),
        "proposed_queue_item": proposed_item,
        "validation": {},
        "safety_boundaries": {
            "real_queue_mutation": "blocked",
            "worker_dispatch": "blocked",
            "continuous_loop": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
        "next_step": _next_step(proposed_item),
    }
    report["validation"] = validate_queue_preview(report)

    _write_json_atomic(target, report)
    return report


def main(repo_root: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    return build_queue_injection_preview_report(root, output_path=output_path)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build a Closed Loop queue injection preview report.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output-path", default=None, help="Exact sandbox output path.")
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_path=args.output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
