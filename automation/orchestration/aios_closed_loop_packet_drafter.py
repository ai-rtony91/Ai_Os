"""AI_OS Closed Loop Packet Drafter.

Consumes a Closed Autonomy Loop recommendation and renders one complete
Codex packet preview for Human Owner review. This module does not call Codex,
enqueue packets, dispatch workers, mutate queue state, or run continuously.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
SYSTEM = "AI_OS"
COMPONENT = "closed_loop_packet_drafter"
MODE = "APPLY_BUILD_WITH_PREVIEW_OUTPUT"

DEFAULT_INPUT = Path("Reports") / "closed_autonomy_loop" / "AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"
DEFAULT_OUTPUT_DIR = Path("Reports") / "sandbox" / "closed_loop_packet_drafter"
DEFAULT_JSON_NAME = "AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json"
DEFAULT_TEXT_NAME = "AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.txt"

AGENTS_REQUIRED_PACKET_FIELDS = [
    "CODEX-ONLY PROMPT",
    "AI_OS EXECUTION TOKEN",
    "AI_OS BOOTSTRAP REQUIRED",
    "IDENTITY",
    "SUPERVISOR IDENTITY",
    "PACKET ID",
    "MODE",
    "ZONE",
    "WORKER IDENTITY",
    "LANE",
    "WORKTREE",
    "BRANCH",
    "PREFLIGHT",
    "ALLOWED PATHS",
    "FORBIDDEN PATHS",
    "APPROVAL AUTHORITY",
    "VALIDATOR CHAIN",
    "STOP POINT",
    "MISSION",
    "FINAL REPORT FORMAT",
]

SUPPORTED_PREVIEW_TYPES = {
    "READ_ONLY_STATUS_RECON",
    "DRY_RUN_PACKET_PREVIEW",
    "DRY_RUN_VALIDATOR_REPAIR",
    "DRY_RUN_QUEUE_CONSOLIDATION",
    "DRY_RUN_SELF_BUILD_LOOP_WIRING",
    "DRY_RUN_CLOSED_LOOP_NEXT_STEP",
    "BLOCKED_NEEDS_CLEANUP",
    "BLOCKED_NEEDS_APPROVAL",
    "BLOCKED_SAFETY_SCOPE",
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
)

BASE_FORBIDDEN_PATHS = [
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "RISK_POLICY.md",
    ".github/",
    ".git/",
    "automation/orchestration/work_packets/",
    "automation/orchestration/workers/",
    "automation/orchestration/command_queue/",
    "automation/orchestration/approval_inbox/",
    "telemetry/runtime/",
    "services/runtime/",
    "services/dispatcher/",
    "broker/",
    "OANDA/",
    "live_trading/",
    "webhooks/",
    "secrets/",
    "credentials/",
    ".env",
    ".env.*",
]

PLACEHOLDER_MARKERS = ("TODO", "TBD", "@filename", "path/to/", "[REAL-FILENAME]", "{feature}")


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


def _load_closed_loop_module() -> Any | None:
    path = Path(__file__).with_name("aios_closed_autonomy_loop.py")
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("aios_closed_autonomy_loop", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def load_closed_loop_report(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    payload = load_json_if_exists(root / DEFAULT_INPUT)
    if isinstance(payload, dict):
        return {"status": "present", "report": payload, "reason": "Closed-loop report loaded from sandbox evidence."}

    module = _load_closed_loop_module()
    if module is None:
        return {
            "status": "missing",
            "report": None,
            "reason": "Closed-loop report file is missing and closed-loop module could not be imported.",
        }

    try:
        report = module.build_closed_loop_report(root)
    except Exception:
        return {
            "status": "blocked",
            "report": None,
            "reason": "Closed-loop report file is missing and in-memory closed-loop generation failed.",
        }

    if not isinstance(report, dict):
        return {"status": "blocked", "report": None, "reason": "Closed-loop generator returned a non-object report."}
    return {"status": "generated_in_memory", "report": report, "reason": "Closed-loop report generated in memory without writes."}


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def _contains_unsafe_scope(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, default=str).lower()
    return any(term in text for term in UNSAFE_SCOPE_TERMS)


def _clean_packet_id(value: str) -> str:
    raw = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value.upper())
    raw = "-".join(part for part in raw.split("-") if part)
    return raw[:96] or "AIOS-CLOSED-LOOP-PACKET-PREVIEW"


def _preview_type(loop_report: dict[str, Any]) -> str:
    action = loop_report.get("proposed_cycle_action") if isinstance(loop_report.get("proposed_cycle_action"), dict) else {}
    gate = loop_report.get("gate_result") if isinstance(loop_report.get("gate_result"), dict) else {}
    governor = loop_report.get("governor_decision") if isinstance(loop_report.get("governor_decision"), dict) else {}

    unsafe_probe = {
        "title": action.get("proposed_action_title"),
        "allowed_paths": action.get("allowed_paths"),
        "packet_id": action.get("proposed_packet_id"),
    }
    if _contains_unsafe_scope(unsafe_probe):
        return "BLOCKED_SAFETY_SCOPE"

    gate_status = str(gate.get("status") or "blocked")
    category = str(governor.get("decision_category") or "")
    if gate_status == "requires_cleanup":
        return "BLOCKED_NEEDS_CLEANUP"
    if gate_status in {"requires_human_approval", "ready_for_apply"}:
        return "BLOCKED_NEEDS_APPROVAL"
    if gate_status == "requires_validator_repair" or category == "VALIDATOR_REPAIR":
        return "DRY_RUN_VALIDATOR_REPAIR"
    if category == "STATUS_RECON":
        return "READ_ONLY_STATUS_RECON"
    if category == "QUEUE_CONSOLIDATION":
        return "DRY_RUN_QUEUE_CONSOLIDATION"
    if category == "SELF_BUILD_LOOP_WIRING":
        return "DRY_RUN_SELF_BUILD_LOOP_WIRING"
    if gate_status == "ready_for_dry_run":
        return "DRY_RUN_PACKET_PREVIEW"
    return "DRY_RUN_CLOSED_LOOP_NEXT_STEP"


def normalize_loop_recommendation(loop_report: Any) -> dict[str, Any]:
    if not isinstance(loop_report, dict):
        return {
            "recommendation_status": "blocked",
            "governor_decision_status": "missing",
            "preview_type": "BLOCKED_NEEDS_CLEANUP",
            "blocked_reason": "closed_loop_report_missing",
            "loop_report": {},
        }

    governor = loop_report.get("governor_decision")
    gate = loop_report.get("gate_result")
    action = loop_report.get("proposed_cycle_action")
    dispatch = loop_report.get("dispatch_recommendation")
    if not isinstance(governor, dict):
        governor_status = "missing"
    else:
        governor_status = "present"

    if not isinstance(gate, dict) or not isinstance(action, dict) or not isinstance(dispatch, dict):
        recommendation_status = "partial"
    elif gate.get("status") in {"ready_for_dry_run", "ready_for_apply"}:
        recommendation_status = "ready"
    else:
        recommendation_status = "blocked"

    preview_type = _preview_type(loop_report)
    return {
        "recommendation_status": recommendation_status,
        "governor_decision_status": governor_status,
        "preview_type": preview_type,
        "blocked_reason": None if recommendation_status == "ready" else str((gate or {}).get("reason") or preview_type),
        "loop_report": loop_report,
    }


def _blueprint_mode(action: dict[str, Any], gate: dict[str, Any]) -> str:
    proposed_mode = str(action.get("proposed_mode") or "DRY_RUN").upper()
    if gate.get("status") == "ready_for_apply" and proposed_mode == "APPLY":
        return "APPLY"
    if proposed_mode == "READ_ONLY":
        return "DRY_RUN"
    return "DRY_RUN"


def _approval_authority(mode: str, preview_type: str) -> str:
    if mode == "APPLY" or preview_type == "BLOCKED_NEEDS_APPROVAL":
        return (
            "REQUIRES_ANTHONY_APPROVAL. Anthony Meza must explicitly approve this packet before any APPLY, "
            "queue mutation, worker dispatch, protected Git action, scheduler, broker, credential, webhook, or live-trading action."
        )
    return (
        "PREVIEW_ONLY. Anthony Meza remains approval authority. This generated packet preview authorizes no dispatch, "
        "queue mutation, protected Git action, scheduler, broker, credential, webhook, or live-trading action."
    )


def build_packet_blueprint(loop_report: Any) -> dict[str, Any]:
    normalized = normalize_loop_recommendation(loop_report)
    report = normalized["loop_report"]
    action = report.get("proposed_cycle_action") if isinstance(report.get("proposed_cycle_action"), dict) else {}
    gate = report.get("gate_result") if isinstance(report.get("gate_result"), dict) else {}
    dispatch = report.get("dispatch_recommendation") if isinstance(report.get("dispatch_recommendation"), dict) else {}

    preview_type = normalized["preview_type"]
    mode = _blueprint_mode(action, gate)
    if preview_type in {"BLOCKED_NEEDS_CLEANUP", "BLOCKED_SAFETY_SCOPE"}:
        mode = "DRY_RUN"
    if preview_type == "BLOCKED_NEEDS_APPROVAL" and gate.get("status") != "ready_for_apply":
        mode = "DRY_RUN"

    suggested_id = str(action.get("proposed_packet_id") or dispatch.get("recommended_next_packet_id") or "AIOS-CLOSED-LOOP-NO-SAFE-NEXT-PACKET")
    packet_id = _clean_packet_id(suggested_id)
    if not packet_id.startswith("AIOS-"):
        packet_id = "AIOS-" + packet_id

    allowed_paths = _as_list(action.get("allowed_paths")) or [str(DEFAULT_OUTPUT_DIR).replace("\\", "/") + "/"]
    forbidden_paths = _unique(_as_list(action.get("forbidden_paths")) + BASE_FORBIDDEN_PATHS)
    validators = _as_list(action.get("required_validators")) or ["git diff --check"]
    stop_conditions = _as_list(action.get("stop_conditions")) or ["Stop after preview report. Do not dispatch or mutate queues."]
    title = str(action.get("proposed_action_title") or "Report blocked closed-loop packet preview.")
    gate_reason = str(gate.get("reason") or normalized.get("blocked_reason") or "Closed-loop recommendation did not provide a safe ready state.")

    risk_level = "medium"
    if preview_type.startswith("BLOCKED"):
        risk_level = "blocked"
    elif mode == "APPLY":
        risk_level = "medium"
    elif preview_type == "READ_ONLY_STATUS_RECON":
        risk_level = "low"

    mission = (
        f"{preview_type}: {title}. This is a generated packet preview from the Closed Autonomy Loop. "
        "Keep dispatch_authorized false and stop before queue mutation, worker launch, commit, push, merge, scheduler, broker, credential, webhook, or live-trading behavior."
    )

    if mode == "APPLY":
        mission = "REQUIRES_ANTHONY_APPROVAL. " + mission
    else:
        mission = "PREVIEW_ONLY. " + mission

    return {
        "packet_id": packet_id,
        "mode": mode,
        "zone": "automation / orchestration / closed autonomy loop / packet preview",
        "lane": str(action.get("proposed_lane") or dispatch.get("recommended_worker_lane") or "closed_loop_packet_preview"),
        "risk_level": risk_level,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "validator_chain": validators,
        "stop_point": " ".join(stop_conditions),
        "preview_type": preview_type,
        "identity": "AI_OS Closed Loop Generated Packet Preview",
        "identity_marker": "AI_OS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW",
        "supervisor_identity": "Anthony Meza is the human supervisor, approval authority, and strategic operator.",
        "worker_identity": "Codex worker selected by future human-approved packet.",
        "worktree": "C:\\Dev\\Ai.Os",
        "branch": "main",
        "preflight": [
            "Read AGENTS.md first.",
            "Read README.md second.",
            "Confirm active path is C:\\Dev\\Ai.Os.",
            "Confirm branch is main.",
            "Confirm repository remote is ai-rtony91/Ai_Os.",
            "Inspect dirty state before any future write.",
            "Stop if requested scope differs from this preview.",
        ],
        "approval_authority": _approval_authority(mode, preview_type),
        "mission": mission,
        "gate_reason": gate_reason,
        "final_report_format": [
            "SUMMARY:",
            "FILES CHANGED:",
            "VALIDATION:",
            "SAFETY CONFIRMATION:",
            "STATUS:",
        ],
    }


def validate_blueprint_against_agents_requirements(blueprint: dict[str, Any]) -> dict[str, Any]:
    key_map = {
        "IDENTITY": "identity",
        "SUPERVISOR IDENTITY": "supervisor_identity",
        "PACKET ID": "packet_id",
        "MODE": "mode",
        "ZONE": "zone",
        "WORKER IDENTITY": "worker_identity",
        "LANE": "lane",
        "WORKTREE": "worktree",
        "BRANCH": "branch",
        "PREFLIGHT": "preflight",
        "ALLOWED PATHS": "allowed_paths",
        "FORBIDDEN PATHS": "forbidden_paths",
        "APPROVAL AUTHORITY": "approval_authority",
        "VALIDATOR CHAIN": "validator_chain",
        "STOP POINT": "stop_point",
        "MISSION": "mission",
        "FINAL REPORT FORMAT": "final_report_format",
    }
    missing: list[str] = []
    for label, key in key_map.items():
        value = blueprint.get(key)
        if value in (None, "", [], {}):
            missing.append(label)

    if blueprint.get("preview_type") not in SUPPORTED_PREVIEW_TYPES:
        missing.append("SUPPORTED PREVIEW TYPE")

    return {
        "agents_required_fields_present": not missing,
        "missing_fields": missing,
        "blocked": bool(missing),
        "blocked_reason": None if not missing else "missing_required_blueprint_fields",
    }


def _format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_codex_packet_preview(blueprint: dict[str, Any]) -> str:
    preflight = _format_list(_as_list(blueprint.get("preflight")))
    allowed = _format_list(_as_list(blueprint.get("allowed_paths")))
    forbidden = _format_list(_as_list(blueprint.get("forbidden_paths")))
    validators = _format_list(_as_list(blueprint.get("validator_chain")))
    final_report = "\n".join(str(item) for item in _as_list(blueprint.get("final_report_format")))
    preview_status = "REQUIRES_ANTHONY_APPROVAL" if blueprint.get("mode") == "APPLY" else "PREVIEW_ONLY"

    text = f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED:
Read AGENTS.md first.
Read README.md second.
If unavailable, stop and report missing AI_OS context.

IDENTITY:
{blueprint.get("identity")}

IDENTITY MARKER:
{blueprint.get("identity_marker")}

SUPERVISOR IDENTITY:
{blueprint.get("supervisor_identity")}

PACKET ID:
{blueprint.get("packet_id")}

MODE:
{blueprint.get("mode")}

ZONE:
{blueprint.get("zone")}

WORKER IDENTITY:
{blueprint.get("worker_identity")}

LANE:
{blueprint.get("lane")}

WORKTREE:
{blueprint.get("worktree")}

BRANCH:
{blueprint.get("branch")}

PREVIEW STATUS:
{preview_status}

PREVIEW TYPE:
{blueprint.get("preview_type")}

RISK LEVEL:
{blueprint.get("risk_level")}

PREFLIGHT:
{preflight}

ALLOWED PATHS:
{allowed}

FORBIDDEN PATHS:
{forbidden}

APPROVAL AUTHORITY:
{blueprint.get("approval_authority")}

VALIDATOR CHAIN:
{validators}

STOP POINT:
{blueprint.get("stop_point")}

MISSION:
{blueprint.get("mission")}

CLOSED LOOP GATE REASON:
{blueprint.get("gate_reason")}

SAFETY BOUNDARIES:
- dispatch_authorized: false
- queue_mutation_authorized: false
- worker_dispatch: blocked
- continuous_loop: blocked
- live_trading: blocked
- broker_execution: blocked
- credential_use: blocked
- unapproved_mutation: blocked

FINAL REPORT FORMAT:
{final_report}

STATUS:
PREVIEW_ONLY, NO DISPATCH, NO QUEUE MUTATION, NO COMMIT, NO PUSH
"""
    return text


def _validate_preview_text(text: str, prior_validation: dict[str, Any]) -> dict[str, Any]:
    missing = list(prior_validation.get("missing_fields") or [])
    lines = text.splitlines()
    if not lines or lines[0] != "CODEX-ONLY PROMPT":
        missing.append("CODEX-ONLY PROMPT first line")
    for marker in AGENTS_REQUIRED_PACKET_FIELDS:
        if marker not in text:
            missing.append(marker)
    for marker in PLACEHOLDER_MARKERS:
        if marker.lower() in text.lower():
            missing.append(f"unresolved placeholder marker: {marker}")
    unique_missing = _unique(missing)
    return {
        "agents_required_fields_present": not unique_missing,
        "missing_fields": unique_missing,
        "blocked": bool(unique_missing),
        "blocked_reason": None if not unique_missing else "rendered_preview_failed_validation",
    }


def _input_status(load_result: dict[str, Any], normalized: dict[str, Any]) -> dict[str, str]:
    return {
        "closed_loop_report": str(load_result.get("status") or "missing"),
        "governor_decision": str(normalized.get("governor_decision_status") or "unknown"),
        "recommendation_status": str(normalized.get("recommendation_status") or "blocked"),
    }


def _safe_output_dir(repo_root: Path, output_dir: str | Path | None) -> Path:
    target = Path(output_dir) if output_dir is not None else repo_root / DEFAULT_OUTPUT_DIR
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    allowed = (repo_root / DEFAULT_OUTPUT_DIR).resolve()
    try:
        target.relative_to(allowed)
    except ValueError as exc:
        raise ValueError("output_dir must be inside Reports/sandbox/closed_loop_packet_drafter/") from exc
    return target


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    _write_text_atomic(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def build_packet_drafter_report(
    repo_root: str | Path,
    output_dir: str | Path | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    now = generated_at_utc or utc_now()
    out_dir = _safe_output_dir(root, output_dir)
    preview_text_path = out_dir / DEFAULT_TEXT_NAME
    preview_json_path = out_dir / DEFAULT_JSON_NAME

    load_result = load_closed_loop_report(root)
    normalized = normalize_loop_recommendation(load_result.get("report"))
    blueprint = build_packet_blueprint(load_result.get("report"))
    validation = validate_blueprint_against_agents_requirements(blueprint)
    preview_text = render_codex_packet_preview(blueprint)
    validation = _validate_preview_text(preview_text, validation)

    if normalized["preview_type"].startswith("BLOCKED"):
        validation["blocked"] = True
        validation["blocked_reason"] = normalized.get("blocked_reason") or normalized["preview_type"]

    if blueprint["mode"] == "APPLY":
        human_approval_required = True
    else:
        human_approval_required = normalized["recommendation_status"] != "ready" or normalized["preview_type"].startswith("BLOCKED")

    report = {
        "schema_version": SCHEMA_VERSION,
        "system": SYSTEM,
        "component": COMPONENT,
        "mode": MODE,
        "generated_at_utc": now,
        "input_status": _input_status(load_result, normalized),
        "packet_blueprint": {
            "packet_id": blueprint["packet_id"],
            "mode": blueprint["mode"],
            "zone": blueprint["zone"],
            "lane": blueprint["lane"],
            "risk_level": blueprint["risk_level"],
            "allowed_paths": blueprint["allowed_paths"],
            "forbidden_paths": blueprint["forbidden_paths"],
            "validator_chain": blueprint["validator_chain"],
            "stop_point": blueprint["stop_point"],
            "preview_type": blueprint["preview_type"],
        },
        "validation": validation,
        "dispatch": {
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
            "human_approval_required": bool(human_approval_required),
        },
        "preview_text_path": str((DEFAULT_OUTPUT_DIR / DEFAULT_TEXT_NAME).as_posix()),
        "safety_boundaries": {
            "worker_dispatch": "blocked",
            "queue_mutation": "blocked",
            "continuous_loop": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
    }

    _write_text_atomic(preview_text_path, preview_text)
    _write_json_atomic(preview_json_path, report)
    return report


def main(repo_root: str | Path | None = None, output_dir: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    return build_packet_drafter_report(root, output_dir=output_dir)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build a Closed Loop Codex packet preview report.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output-dir", default=None, help="Output directory under Reports/sandbox/closed_loop_packet_drafter/.")
    args = parser.parse_args()
    report = main(repo_root=args.repo_root, output_dir=args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
