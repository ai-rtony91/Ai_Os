"""AI_OS Queue Admission Gate.

Consumes the Closed Loop Queue Injection Preview and decides whether the
proposed queue item is admissible as preview-only evidence. This module does
not mutate the real queue, enqueue work, dispatch workers, or execute packet
text.
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
COMPONENT = "queue_admission_gate"
MODE = "APPLY_BUILD_WITH_ADMISSION_PREVIEW_OUTPUT"

QUEUE_PREVIEW_PATH = (
    Path("Reports")
    / "sandbox"
    / "closed_loop_queue_injection_preview"
    / "AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
)
DEFAULT_OUTPUT_PATH = (
    Path("Reports")
    / "sandbox"
    / "queue_admission_gate"
    / "AIOS_QUEUE_ADMISSION_GATE_PREVIEW.json"
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

REQUIRED_SAFETY_BOUNDARIES = {
    "real_queue_mutation": "blocked",
    "worker_dispatch": "blocked",
    "continuous_loop": "blocked",
    "live_trading": "blocked",
    "broker_execution": "blocked",
    "credential_use": "blocked",
    "unapproved_mutation": "blocked",
}

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
    "scheduler",
    "background loop",
    "startup",
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


def _contains_forbidden_scope(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, default=str).lower()
    return any(term in text for term in UNSAFE_SCOPE_TERMS)


def _safe_output_path(repo_root: Path, output_path: str | Path | None) -> Path:
    target = Path(output_path) if output_path is not None else repo_root / DEFAULT_OUTPUT_PATH
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    allowed = (repo_root / DEFAULT_OUTPUT_PATH).resolve()
    if target != allowed:
        raise ValueError("output_path must be Reports/sandbox/queue_admission_gate/AIOS_QUEUE_ADMISSION_GATE_PREVIEW.json")
    return target


def load_queue_injection_preview(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    payload = load_json_if_exists(root / QUEUE_PREVIEW_PATH)
    if not isinstance(payload, dict):
        return {
            "status": "missing",
            "report": None,
            "path": str(QUEUE_PREVIEW_PATH.as_posix()),
            "reason": "missing_queue_preview",
        }

    item = payload.get("proposed_queue_item")
    validation = payload.get("validation")
    status = "present"
    reason = None
    if isinstance(item, dict) and item.get("status") == "blocked":
        status = "blocked"
        reason = str(item.get("blocked_reason") or "queue_preview_blocked")
    elif isinstance(validation, dict) and validation.get("blocked") is True:
        status = "blocked"
        reason = str(validation.get("blocked_reason") or "queue_preview_blocked")

    return {
        "status": status,
        "report": payload,
        "path": str(QUEUE_PREVIEW_PATH.as_posix()),
        "reason": reason,
    }


def normalize_proposed_queue_item(queue_preview: Any) -> dict[str, Any]:
    if not isinstance(queue_preview, dict):
        return {
            "status": "missing",
            "missing_fields": ["proposed_queue_item"],
            "proposed_queue_item": {},
            "safety_boundaries": {},
            "blocked_reason": "missing_queue_preview",
        }

    item = queue_preview.get("proposed_queue_item")
    safety = queue_preview.get("safety_boundaries")
    if not isinstance(item, dict):
        return {
            "status": "missing",
            "missing_fields": ["proposed_queue_item"],
            "proposed_queue_item": {},
            "safety_boundaries": safety if isinstance(safety, dict) else {},
            "blocked_reason": "missing_proposed_queue_item",
        }

    missing = [field for field in REQUIRED_QUEUE_ITEM_FIELDS if item.get(field) in (None, "", [], {})]
    if "approval_required" in item and item.get("approval_required") is False and str(item.get("mode")).upper() == "APPLY":
        missing.append("approval_required_for_apply")
    if item.get("dispatch_authorized") is not False:
        missing.append("dispatch_authorized_false")
    if item.get("queue_mutation_authorized") is not False:
        missing.append("queue_mutation_authorized_false")

    safety_dict = safety if isinstance(safety, dict) else {}
    for key, expected in REQUIRED_SAFETY_BOUNDARIES.items():
        if safety_dict.get(key) != expected:
            missing.append(f"safety_boundaries.{key}")

    unsafe_probe = {
        "packet_id": item.get("packet_id"),
        "mode": item.get("mode"),
        "lane": item.get("lane"),
        "risk_level": item.get("risk_level"),
        "allowed_paths": item.get("allowed_paths"),
        "stop_conditions": item.get("stop_conditions"),
    }
    if _contains_forbidden_scope(unsafe_probe):
        missing.append("forbidden_scope")

    status = "present" if not missing else "invalid"
    blocked_reason = None if not missing else "invalid_proposed_queue_item"
    if item.get("status") == "blocked":
        status = "invalid"
        blocked_reason = str(item.get("blocked_reason") or "queue_preview_blocked")

    return {
        "status": status,
        "missing_fields": missing,
        "proposed_queue_item": item,
        "safety_boundaries": safety_dict,
        "blocked_reason": blocked_reason,
    }


def evaluate_admission_rules(proposed_queue_item: dict[str, Any]) -> dict[str, Any]:
    missing = list(proposed_queue_item.get("missing_fields") or [])
    item = proposed_queue_item.get("proposed_queue_item") if isinstance(proposed_queue_item.get("proposed_queue_item"), dict) else {}
    status = str(item.get("status") or "")
    reason = "queue item is admissible as preview-only evidence"

    if proposed_queue_item.get("status") in {"missing", "invalid"}:
        result_status = "blocked"
        reason = str(proposed_queue_item.get("blocked_reason") or "invalid_proposed_queue_item")
    elif status == "requires_approval" or item.get("approval_required") is True:
        result_status = "requires_approval"
        reason = "human approval required before any real queue admission"
    else:
        result_status = "admissible_preview_only"

    return {
        "status": result_status,
        "reason": reason,
        "queue_mutation_authorized": False,
        "dispatch_authorized": False,
        "human_approval_required": True,
        "missing_fields": missing,
    }


def _validation(normalized: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    missing = list(normalized.get("missing_fields") or [])
    blocked = admission["status"] == "blocked" or bool(missing)
    blocked_reason = None
    if blocked:
        blocked_reason = admission.get("reason") or "queue_admission_blocked"
    return {
        "required_fields_present": not missing,
        "missing_fields": missing,
        "blocked": blocked,
        "blocked_reason": blocked_reason,
    }


def _input_status(load_result: dict[str, Any], normalized: dict[str, Any]) -> dict[str, str]:
    return {
        "queue_injection_preview": str(load_result.get("status") or "missing"),
        "proposed_queue_item": str(normalized.get("status") or "missing"),
    }


def _validated_queue_item(normalized: dict[str, Any]) -> dict[str, Any]:
    item = normalized.get("proposed_queue_item")
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
        "dispatch_authorized": False,
        "queue_mutation_authorized": False,
        "status": item.get("status"),
        "blocked_reason": item.get("blocked_reason"),
    }


def _next_step(admission: dict[str, Any]) -> str:
    if admission["status"] == "blocked":
        return "Repair queue injection preview evidence before requesting admission again."
    if admission["status"] == "requires_approval":
        return "Anthony reviews the admission preview; real queue mutation remains blocked until a separate queue mutation gate approves it."
    return "Proceed only to a worker dispatch gate preview; real queue mutation remains blocked."


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


def build_admission_report(
    repo_root: str | Path,
    output_path: str | Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    target = _safe_output_path(root, output_path)
    now = generated_at_utc or utc_now()

    load_result = load_queue_injection_preview(root)
    queue_preview = load_result.get("report")
    normalized = normalize_proposed_queue_item(queue_preview)
    if load_result.get("status") == "missing":
        normalized["status"] = "missing"
        normalized["blocked_reason"] = "missing_queue_preview"
        normalized["missing_fields"] = ["proposed_queue_item"]
    elif load_result.get("status") == "blocked" and normalized.get("status") != "invalid":
        normalized["status"] = "invalid"
        normalized["blocked_reason"] = str(load_result.get("reason") or "queue_preview_blocked")

    admission = evaluate_admission_rules(normalized)
    result = {key: admission[key] for key in ("status", "reason", "queue_mutation_authorized", "dispatch_authorized", "human_approval_required")}

    report = {
        "schema_version": SCHEMA_VERSION,
        "system": SYSTEM,
        "component": COMPONENT,
        "mode": MODE,
        "generated_at_utc": now,
        "input_status": _input_status(load_result, normalized),
        "admission_result": result,
        "validated_queue_item": _validated_queue_item(normalized),
        "validation": _validation(normalized, admission),
        "safety_boundaries": REQUIRED_SAFETY_BOUNDARIES.copy(),
        "next_step": _next_step(admission),
    }

    _write_json_atomic(target, report)
    return report


def main(repo_root: str | Path | None = None, output_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    return build_admission_report(root, output_path=output_path)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build an AI_OS queue admission gate preview report.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output-path", default=None, help="Exact sandbox output path.")
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_path=args.output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
