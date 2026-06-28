"""Full overnight repo-safe continuation runner for Forex workflow control."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs" / "governance" / "programs" / "contracts"
REPORT_DIR = REPO_ROOT / "Reports" / "forex_delivery"

DOC_PATH = DOCS_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.md"
JSON_REPORT_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json"
REPORT_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1_REPORT.md"
QUEUE_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_ACTION_QUEUE_V1.md"
CHECKPOINT_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_CHECKPOINT_V1.md"
ACTIVE_PACKET_QUEUE_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_ACTIVE_PACKET_QUEUE_V1.md"
EXTERNAL_GATE_STOP_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_EXTERNAL_GATE_STOP_V1.md"
OWNER_HANDOFF_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_OWNER_HANDOFF_V1.md"
NEXT_CODEX_PROMPT_PATH = REPORT_DIR / "AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_CODEX_PROMPT_V1.md"

MAX_RUNNER_CYCLES_DEFAULT = 12
MAX_RUNNER_MINUTES_DEFAULT = 480

DEFAULT_FLOW2_PACKET_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1.md"
)
DEFAULT_FLOW3_PACKET_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1.md"
)
DEFAULT_LIVE_EXCEPTION_PACKET_PATH = (
    "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1.md"
)

DEFAULT_ALLOWED_PATHS = [
    "automation/forex_engine/forex_full_overnight_work_runner_v1.py",
    "scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py",
    "scripts/forex_delivery/validate_forex_full_overnight_work_runner_v1.ps1",
    "scripts/forex_delivery/publish_forex_full_overnight_work_runner_v1.ps1",
    "scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1",
    "docs/governance/programs/contracts/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_ACTION_QUEUE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_CHECKPOINT_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_ACTIVE_PACKET_QUEUE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_EXTERNAL_GATE_STOP_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_OWNER_HANDOFF_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_CODEX_PROMPT_V1.md",
    "tests/forex_engine/test_forex_full_overnight_work_runner_v1.py",
]

BANNED_OUTPUT_TOKENS = [
    "TODO",
    "TBD",
    "@filename",
    "probably",
    "roughly",
    "approximately",
    "I estimate",
    "guaranteed profit",
    "guaranteed returns",
    "100-120 percent verified",
    "100–120% verified",
    "target achieved without evidence",
    "live ready",
    "autonomous trading ready",
    "vacation mode active",
    "22h6d active",
    "22h/6d active",
    "live profitable week proven",
    "broker connected",
    "credentials loaded",
    "order placed",
    "trade executed",
    "demo trade executed",
    "live trade executed",
    "real order",
    "real trade",
    "approval granted",
    "API key accepted",
    "credentials accepted",
    "account id accepted",
    "broker connected successfully",
    "money machine",
    "mean machine",
]

SECRET_LIKE_FRAGMENTS = ["secret", "token", "credential", "password", ".env", "key"]


def evaluate_forex_full_overnight_work_runner(owner_input: dict | None = None) -> dict:
    """Evaluate the overnight runner state and return all artifacts for execution."""
    owner_input = owner_input or {}
    runner_action = str(owner_input.get("runner_action", "")).strip().upper()
    git_status_lines = _to_status_lines(owner_input.get("git_status_lines"))
    completed_packets = _to_list(owner_input.get("completed_packets"))
    active_allowed_paths = _to_list(
        owner_input.get("active_allowed_paths"), default=DEFAULT_ALLOWED_PATHS
    )
    max_runner_cycles = int(owner_input.get("max_runner_cycles") or MAX_RUNNER_CYCLES_DEFAULT)
    max_runner_minutes = int(owner_input.get("max_runner_minutes") or MAX_RUNNER_MINUTES_DEFAULT)

    packet_queue = build_active_packet_queue()
    selected_packet, selected_index = select_next_packet(
        packet_queue, completed_packets=completed_packets
    )
    selected_packet = selected_packet or {}

    result: dict[str, Any] = {
        "runner_status": "FULL_OVERNIGHT_RUNNER_READY_FOR_OWNER_HOST_EXECUTION",
        "runner_mode": "HOST_LOOP_READY",
        "active_anchor": "PR_1196_OVERNIGHT_CONTRACT_MERGED",
        "flow1_anchor": "PR_1194_FLOW1_MERGED",
        "owner_live_capital_intent_usd": 1000,
        "requested_max_open_positions": 4,
        "requested_quantity_scale": 4.0,
        "target_return_band": "100_TO_120_PERCENT",
        "target_return_claim_status": "TARGET_NOT_YET_VERIFIED",
        "runtime_objective": "22_HOURS_PER_DAY_6_DAYS_PER_WEEK",
        "vacation_mode_status": "TARGET_DEFINED_GATE_PENDING",
        "sos_alert_contract_status": "REQUIRED_GATE_PENDING",
        "overnight_loop_status": "NOT_STARTED_HOST_RUNNER_REQUIRED",
        "repo_safe_work_status": "READY_TO_CONTINUE",
        "external_trading_authority_status": "BLOCKED",
        "next_packet_id": selected_packet.get("packet_id", "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1"),
        "next_required_flow": "FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE",
        "queue_index": selected_index,
        "active_packet_queue": packet_queue,
        "active_anchor_map": build_known_landed_anchor_map(),
        "active_allowed_paths": active_allowed_paths,
        "path_classification": None,
        "selected_next_packet": selected_packet,
        "external_gate_stop": None,
        "validation_status": "READY_TO_VALIDATE",
        "publish_status": "NOT_READY_VALIDATION_REQUIRED",
        "max_runner_cycles_default": MAX_RUNNER_CYCLES_DEFAULT,
        "max_runner_minutes_default": MAX_RUNNER_MINUTES_DEFAULT,
        "max_runner_cycles": max_runner_cycles,
        "max_runner_minutes": max_runner_minutes,
        "allow_publish_after_validation": bool(owner_input.get("allow_publish_after_validation", True)),
        "untracked_file_policy": "CLASSIFY_AND_ALLOW_ONLY_ACTIVE_SCOPE",
        "external_authorization_flags": {
            "broker_api_access_authorized": False,
            "credential_access_authorized": False,
            "demo_order_placement_authorized": False,
            "live_trading_authorized": False,
            "order_submission_authorized": False,
            "runtime_22h6d_activated": False,
            "vacation_mode_activated": False,
            "autonomous_trading_authorized": False,
            "money_movement_authorized": False,
            "broker_connection_authorized": False,
        },
        "completed_packets": completed_packets,
        "active_packet_id": owner_input.get("active_packet_id"),
        "owner_attestation": bool(owner_input.get("owner_attestation", False)),
        "runner_action": runner_action or "NONE",
        "next_owner_action": _default_next_owner_action(selected_packet),
    }

    if runner_action == "CONTINUE":
        if bool(owner_input.get("owner_attestation", False)):
            result["runner_status"] = "FULL_OVERNIGHT_RUNNER_READY_TO_CONTINUE"
            result["runner_mode"] = "CONTINUE_READY"
            result["overnight_loop_status"] = "READY_FOR_HOST_LOOP"
            result["publish_status"] = "READY_AFTER_HOST_VALIDATION"
            result["next_owner_action"] = "RUN_HOST_LOOP_ONCE_PER_CYCLE"
        else:
            result["runner_status"] = "FULL_OVERNIGHT_RUNNER_CONTINUE_PAUSED_MISSING_ATTESTATION"
            result["runner_mode"] = "PAUSE_READY"
            result["overnight_loop_status"] = "OWNER_ATTESTATION_REQUIRED"
            result["publish_status"] = "NOT_READY_VALIDATION_REQUIRED"
            result["next_owner_action"] = "SUPPLY_OWNER_ATTESTATION_TRUE_TO_CONTINUE"

    elif runner_action == "PAUSE":
        result["runner_status"] = "FULL_OVERNIGHT_RUNNER_PAUSED_BY_OWNER"
        result["runner_mode"] = "PAUSED"
        result["overnight_loop_status"] = "PAUSED_BY_OWNER"
        result["next_owner_action"] = "RESUME_WITH_CONTINUE_AFTER_OWNER_REVIEW"

    elif runner_action == "STOP":
        result["runner_status"] = "FULL_OVERNIGHT_RUNNER_STOPPED_BY_OWNER"
        result["runner_mode"] = "STOPPED"
        result["overnight_loop_status"] = "STOPPED_BY_OWNER"
        result["next_owner_action"] = "OWNER_ACTION_REQUIRED_TO_RESUME"

    elif runner_action == "CLASSIFY":
        classification = classify_git_status_paths(git_status_lines, active_allowed_paths)
        result["path_classification"] = classification
        result["runner_status"] = "FULL_OVERNIGHT_RUNNER_CLASSIFIED_WORKTREE"
        result["runner_mode"] = "CLASSIFY_READY"
        result["validation_status"] = (
            "READY_TO_VALIDATE"
            if classification["can_continue"]
            else "BLOCKED_BY_DIRTY_SCOPE"
        )
        result["next_owner_action"] = (
            "RUN_VALIDATION"
            if classification["can_continue"]
            else "REPAIR_DIRTY_SCOPE"
        )
        if not classification["can_continue"]:
            result["publish_status"] = "NOT_READY_VALIDATION_REQUIRED"
            if classification["blocked_secret_like_paths"]:
                result["next_owner_action"] = (
                    "REPAIR_SECRET_SCOPE: "
                    + "; ".join(classification["blocked_secret_like_paths"])
                )

    elif runner_action == "SELECT_NEXT":
        result["runner_status"] = "FULL_OVERNIGHT_RUNNER_NEXT_PACKET_SELECTED"
        result["runner_mode"] = "SELECT_NEXT_READY"
        result["validation_status"] = "READY_TO_VALIDATE"
        result["next_owner_action"] = "GENERATE_AND_REVIEW_NEXT_PACKET_PROMPT"
        result["selected_next_packet"] = selected_packet if selected_packet else None
        if selected_packet:
            result["next_packet_id"] = selected_packet["packet_id"]
            result["next_required_flow"] = selected_packet["flow_id"]

    elif runner_action == "EXTERNAL_GATE_STOP":
        requested_gate = owner_input.get("external_gate_id")
        external_gates = build_external_gate_stop_map()
        found_gate = None
        if requested_gate:
            for gate in external_gates:
                if gate["gate_id"] == requested_gate:
                    found_gate = gate
                    break
        if found_gate is None and external_gates:
            found_gate = external_gates[0]
        result["external_gate_stop"] = found_gate
        result["runner_status"] = "FULL_OVERNIGHT_RUNNER_STOPPED_AT_EXTERNAL_GATE"
        result["runner_mode"] = "EXTERNAL_GATE_STOP"
        result["overnight_loop_status"] = "STOPPED_AT_EXTERNAL_GATE"
        result["publish_status"] = "NOT_READY_VALIDATION_REQUIRED"
        result["next_owner_action"] = (
            found_gate["owner_action_required"] if found_gate else "OWNER_REQUIRED_ACTION_AT_GATE"
        )

    # Ensure explicit references used by host script and handoff artifacts.
    if result["selected_next_packet"] is None and selected_packet:
        result["selected_next_packet"] = selected_packet

    result["checkpoint"] = build_checkpoint(result)
    result["active_packet_queue_text"] = render_active_packet_queue(result)
    result["external_gate_stop_text"] = render_external_gate_stop(result)
    return result


def build_active_packet_queue() -> list[dict]:
    return [
        {
            "packet_id": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "flow_id": "FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE",
            "packet_source_path": DEFAULT_FLOW2_PACKET_PATH,
            "depends_on": ["PR_1196_OVERNIGHT_CONTRACT_MERGED", "PR_1194_FLOW1_MERGED"],
            "repo_safe": True,
            "external_gate_required": True,
            "external_gate_reason": (
                "owner-supervised demo evidence and broker snapshot may be required"
            ),
            "next_on_success": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
        },
        {
            "packet_id": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "flow_id": "FLOW_3_PROFIT_LOOP_LIVE_WEEK_VACATION_GATE",
            "packet_source_path": DEFAULT_FLOW3_PACKET_PATH,
            "depends_on": ["FLOW2_EVIDENCE_OUTPUT"],
            "repo_safe": True,
            "external_gate_required": True,
            "external_gate_reason": "Flow 2 evidence output required",
            "next_on_success": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
        },
        {
            "packet_id": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "flow_id": "LIVE_EXCEPTION_AND_REAL_MONEY_GATE",
            "packet_source_path": DEFAULT_LIVE_EXCEPTION_PACKET_PATH,
            "depends_on": ["FLOW3_PROFIT_LOOP_OUTPUT"],
            "repo_safe": True,
            "external_gate_required": True,
            "external_gate_reason": (
                "explicit owner approval, broker gate, credential gate, and evidence gate required"
            ),
            "next_on_success": "EXTERNAL_GATE_STOP_REAL_MONEY_REQUIRES_OWNER_APPROVAL",
        },
    ]


def build_known_landed_anchor_map() -> dict:
    return {
        "PR_1192_P14_FINAL_REHEARSAL": "landed on main in prior repo-safe preparation lane",
        "PR_1193_CONTINUOUS_BRIDGE_CONTROLLER": "landed on main and anchors flow bridge control",
        "PR_1194_FLOW1_ACTIVE_EXECUTION_AUTHORITY": "landed on main and anchors flow 1 authority",
        "PR_1196_OVERNIGHT_END_TO_END_CONTRACT": "landed on main and anchors full overnight end-to-end contract",
    }


def build_external_gate_stop_map() -> list[dict]:
    return [
        {
            "gate_id": "OWNER_INPUT_REQUIRED",
            "reason": "Owner action and attestation are required before repo-safe loop advances.",
            "owner_action_required": "Supply owner_attestation and the requested action in host input.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "BROKER_SNAPSHOT_REQUIRED",
            "reason": "Flow 2 evidence workflow may require a supervisor-led broker snapshot.",
            "owner_action_required": "Run Flow 2 packet and supply snapshot evidence package.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "BROKER_CONNECTION_REQUIRED",
            "reason": "Live exception path requires broker connection authorization outside this runner.",
            "owner_action_required": "Prepare external broker-connection proof packet outside repo-safe runner.",
            "repo_safe_work_completed": False,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "CREDENTIAL_GATE_REQUIRED",
            "reason": "Credential proof remains external to this packet.",
            "owner_action_required": "Run external credential gate packet before live exception.",
            "repo_safe_work_completed": False,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "DEMO_EXECUTION_AUTHORITY_REQUIRED",
            "reason": "Flow 2 supervised evidence remains owner-directed and not auto-executed.",
            "owner_action_required": "Run Flow 2 evidence packet with owner supervision.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "TRADE_EVIDENCE_REQUIRED",
            "reason": "Trade evidence bundle is needed before Flow 3 readiness actions.",
            "owner_action_required": "Supply evidence from supervised demo output packet.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "REALIZED_PL_REQUIRED",
            "reason": "Flow 3 readiness controls depend on realized P/L inputs.",
            "owner_action_required": "Run follow-up evidence packet with realized P/L proof.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "LIVE_EXCEPTION_REQUIRED",
            "reason": "Live exception packet is an external bridge with explicit owner and policy gates.",
            "owner_action_required": "Run AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1 when ready.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "REAL_MONEY_APPROVAL_REQUIRED",
            "reason": "Capital transition cannot be inferred by repo-only automation.",
            "owner_action_required": "Obtain explicit owner approval packet for live capital movement.",
            "repo_safe_work_completed": False,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "RUNTIME_SUPERVISOR_REQUIRED",
            "reason": "Runtime supervisor proof is required for sustained objective operation.",
            "owner_action_required": "Run external runtime supervisor packet and return evidence.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "SOS_ALERT_PROOF_REQUIRED",
            "reason": "SOS alert proof must be externally asserted before gate crossing.",
            "owner_action_required": "Collect SOS proof from escalation packet output.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
        {
            "gate_id": "VACATION_MODE_PROOF_REQUIRED",
            "reason": "Vacation-mode target status cannot be set by runner alone.",
            "owner_action_required": "Collect vacation-mode readiness proof packet.",
            "repo_safe_work_completed": True,
            "next_packet_after_gate": "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1",
            "do_not_cross_inside_runner": True,
        },
    ]


def classify_git_status_paths(
    status_lines: list[str], active_allowed_paths: list[str]
) -> dict:
    allowed: list[str] = []
    blocked: list[str] = []
    blocked_secret_like: list[str] = []
    untracked: list[str] = []
    modified: list[str] = []
    directory_fragments: list[str] = []

    active_allowed = _to_list(active_allowed_paths, default=DEFAULT_ALLOWED_PATHS)
    normalized_allowed = [_normalize_path(p) for p in active_allowed]

    for raw_line in status_lines:
        line = str(raw_line).strip()
        if not line:
            continue
        if len(line) < 4:
            continue

        parts = line.split(maxsplit=1)
        status = parts[0]
        path = parts[1].strip()
        if "->" in path:
            path = path.split("->", 1)[1].strip()
        path = _normalize_path(path)
        path_no_trailing = path.rstrip("/")

        if path.endswith("/"):
            directory_fragments.append(path)

        if status.startswith("??"):
            untracked.append(path)
        elif "M" in status or "A" in status or "D" in status or "R" in status or "C" in status:
            modified.append(path)

        path_allowed = any(
            _is_inside_allowed(path, allowed_path) for allowed_path in normalized_allowed
        ) or any(
            _is_inside_allowed(path_no_trailing, allowed_path) for allowed_path in normalized_allowed
        )
        if not path_allowed:
            path_allowed = any(
                _is_inside_allowed(allowed_path, path_no_trailing)
                for allowed_path in normalized_allowed
            )
        if path_allowed and path_no_trailing not in allowed:
            allowed.append(path_no_trailing)
            continue
        if not path_allowed and path_no_trailing not in blocked:
            blocked.append(path_no_trailing)

        lowered = path.lower()
        if any(fragment in lowered for fragment in SECRET_LIKE_FRAGMENTS):
            blocked_secret_like.append(path)

    blocked = sorted(set(blocked))
    allowed = sorted(set(allowed))
    untracked = sorted(set(untracked))
    modified = sorted(set(modified))
    directory_fragments = sorted(set(directory_fragments))
    blocked_secret_like = sorted(set(blocked_secret_like))

    can_continue = not blocked_secret_like and not blocked
    action = "CONTINUE_VALIDATE" if can_continue else "STOP_DIRTY_SCOPE"
    return {
        "status_lines": status_lines,
        "active_allowed_paths": active_allowed,
        "allowed_paths": allowed,
        "blocked_paths": blocked,
        "blocked_secret_like_paths": blocked_secret_like,
        "untracked_paths": untracked,
        "modified_paths": modified,
        "directory_fragments": directory_fragments,
        "can_continue": can_continue,
        "action": action,
    }


def select_next_packet(
    queue: list[dict], completed_packets: list[str] | None = None
) -> tuple[dict | None, int]:
    completed = set(_to_list(completed_packets))
    for index, item in enumerate(queue):
        if item["packet_id"] in completed or item["flow_id"] in completed:
            continue
        return item, index
    return None, len(queue)


def build_checkpoint(result: dict) -> dict:
    external_gate = result.get("external_gate_stop") or {}
    path_classification = result.get("path_classification") or {}
    return {
        "checkpoint_timestamp": _utc_timestamp(),
        "current_anchor": result.get("active_anchor"),
        "next_packet_id": result.get("next_packet_id"),
        "next_required_flow": result.get("next_required_flow"),
        "queue_index": result.get("queue_index"),
        "completed_packets": result.get("completed_packets", []),
        "blocked_gate_if_any": external_gate.get("gate_id") if external_gate else None,
        "dirty_scope_status": (
            "ALLOWED" if (path_classification.get("can_continue")) else "BLOCKED"
        )
        if path_classification
        else "UNCLASSIFIED",
        "validation_status": result.get("validation_status"),
        "publish_status": result.get("publish_status"),
        "next_owner_action": result.get("next_owner_action"),
    }


def render_owner_report(result: dict) -> str:
    return (
        "# AIOS Forex Full Overnight Work Runner V1 Report\n\n"
        "## Runner Status\n"
        f"runner_status: {result['runner_status']}\n"
        f"runner_mode: {result['runner_mode']}\n"
        f"runner_action: {result['runner_action']}\n\n"
        "## Current Anchors\n"
        f"- active_anchor: {result['active_anchor']}\n"
        f"- flow1_anchor: {result['flow1_anchor']}\n\n"
        "## Runtime Core\n"
        f"- owner_live_capital_intent_usd: {result['owner_live_capital_intent_usd']}\n"
        f"- requested_max_open_positions: {result['requested_max_open_positions']}\n"
        f"- requested_quantity_scale: {result['requested_quantity_scale']}\n"
        f"- target_return_band: {result['target_return_band']}\n"
        f"- runtime_objective: {result['runtime_objective']}\n"
        f"- vacation_mode_status: {result['vacation_mode_status']}\n"
        f"- sos_alert_contract_status: {result['sos_alert_contract_status']}\n"
        f"- overnight_loop_status: {result['overnight_loop_status']}\n\n"
        "## Queue and Routing\n"
        f"- next_packet_id: {result['next_packet_id']}\n"
        f"- next_required_flow: {result['next_required_flow']}\n"
        f"- queue_index: {result['queue_index']}\n\n"
        "## External Authority\n"
        f"- external_trading_authority_status: {result['external_trading_authority_status']}\n"
        f"- max_runner_cycles_default: {result['max_runner_cycles_default']}\n"
        f"- max_runner_minutes_default: {result['max_runner_minutes_default']}\n\n"
        "## Checkpoint\n"
        f"- next_owner_action: {result['next_owner_action']}\n"
        f"- validation_status: {result['validation_status']}\n"
        f"- publish_status: {result['publish_status']}\n\n"
        "## What This Does Not Do\n"
        "- broker/API access\n"
        "- credential loading\n"
        "- account action\n"
        "- order placement\n"
        "- broker connection\n"
        "- live activation\n"
        "- trading activation\n"
        "- scheduler activation\n"
        "- daemon activation\n"
        "- webhook activation\n"
        "- money movement\n\n"
        "## Final Owner Sentence\n"
        + _final_owner_sentence()
    )


def render_next_action_queue(result: dict) -> str:
    selected_packet = result.get("selected_next_packet") or {}
    return (
        "# AIOS Forex Full Overnight Work Runner Next Action Queue V1\n\n"
        "## Runner Status\n"
        f"{result['runner_status']}\n\n"
        "## Runner Mode\n"
        f"{result['runner_mode']}\n\n"
        "## Next Packet\n"
        f"{selected_packet.get('packet_id', 'AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1')}\n\n"
        "## Next Required Flow\n"
        f"{result['next_required_flow']}\n\n"
        "## Required Owner Action\n"
        f"{result['next_owner_action']}\n\n"
        "## External Gate Status\n"
        f"{(result.get('external_gate_stop') or {}).get('gate_id', 'NOT_TRIGGERED')}\n\n"
        "## Remaining Blocks\n"
        "- block: external authorization flags\n"
        "- block: disallowed dirty scope check\n"
        "- block: external gates\n"
        "- owner pause/stop states\n\n"
        "## Final Owner Sentence\n"
        + _final_owner_sentence()
    )


def render_checkpoint(result: dict) -> str:
    checkpoint = result["checkpoint"]
    return (
        "# AIOS Forex Full Overnight Work Runner Checkpoint V1\n\n"
        f"current_anchor: {checkpoint['current_anchor']}\n"
        f"next_packet_id: {checkpoint['next_packet_id']}\n"
        f"next_required_flow: {checkpoint['next_required_flow']}\n"
        f"queue_index: {checkpoint['queue_index']}\n"
        f"completed_packets: {checkpoint['completed_packets']}\n"
        f"blocked_gate_if_any: {checkpoint['blocked_gate_if_any']}\n"
        f"dirty_scope_status: {checkpoint['dirty_scope_status']}\n"
        f"validation_status: {checkpoint['validation_status']}\n"
        f"publish_status: {checkpoint['publish_status']}\n"
        f"next_owner_action: {checkpoint['next_owner_action']}\n"
    )


def render_active_packet_queue(result: dict) -> str:
    lines = [
        "# AIOS Forex Full Overnight Work Runner Active Packet Queue V1",
        "",
        "## Packet List",
    ]
    for index, packet in enumerate(result["active_packet_queue"], start=1):
        lines.append(f"{index}. {packet['packet_id']} | {packet['flow_id']}")
        lines.append(f"   source: {packet['packet_source_path']}")
        lines.append(f"   depends_on: {', '.join(packet['depends_on'])}")
        lines.append(f"   next_on_success: {packet['next_on_success']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_external_gate_stop(result: dict) -> str:
    lines = [
        "# AIOS Forex Full Overnight Work Runner External Gate Stop V1",
        "",
        "## Active Gate Stop Rules",
    ]
    for item in build_external_gate_stop_map():
        lines.extend(
            [
                f"- gate_id: {item['gate_id']}",
                f"  reason: {item['reason']}",
                f"  owner_action_required: {item['owner_action_required']}",
                f"  repo_safe_work_completed: {item['repo_safe_work_completed']}",
                f"  next_packet_after_gate: {item['next_packet_after_gate']}",
                f"  do_not_cross_inside_runner: {item['do_not_cross_inside_runner']}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def render_owner_handoff(result: dict) -> str:
    safe_files = "\n".join(f"- {path}" for path in DEFAULT_ALLOWED_PATHS)
    return (
        "# AIOS Forex Full Overnight Work Runner Owner Handoff V1\n\n"
        "## How To Run The Runner\n"
        "- `pwsh -File scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1 -DryRun -NoPublish -MaxCycles 12 -MaxMinutes 480`\n"
        "- `pwsh -File scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1 -MaxCycles 12 -MaxMinutes 480`\n\n"
        "## Safe Files\n"
        f"{safe_files}\n\n"
        "## Blocked Files\n"
        "- files outside active allowed scope\n"
        "- broker or credential artifacts\n"
        "- any .env or key-like file\n"
        "- non-approved order/execution artifacts\n\n"
        "## What To Paste Back On Stop\n"
        "- runner output markers and latest checkpoint path\n"
        "- path classification summary (if action returned STOP_DIRTY_SCOPE)\n"
        "- selected packet identifier and next required flow\n"
        "- selected next prompt file content\n\n"
        "## External Gates\n"
        "- If external gate returns immediately, resolve by opening the mapped gate packet.\n\n"
        "## Final Owner Sentence\n"
        + _final_owner_sentence()
    )


def render_next_codex_prompt(result: dict) -> str:
    selected = result.get("selected_next_packet") or {}
    packet_id = selected.get("packet_id", "AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1")
    packet_path = selected.get("packet_source_path", DEFAULT_FLOW2_PACKET_PATH)
    return (
        "# AIOS Forex Full Overnight Work Runner Next Codex Prompt V1\n\n"
        "## Next Packet\n"
        f"{packet_id}\n\n"
        "## Packet Source\n"
        f"{packet_path}\n\n"
        "## Run Instruction\n"
        "Copy this packet in full and execute through owner handoff. "
        "The runner is owner-hosted and remains interactive, so host confirmation is required.\n"
    )


def render_contract_doc() -> str:
    return (
        "# AIOS Forex Full Overnight Work Runner V1\n\n"
        "## Purpose\n"
        "Run repository-safe continuation across Flow 2 evidence, Flow 3 profit-loop gate work, and live exception bridge preparation.\n\n"
        "## Current Anchors\n"
        "- PR_1194_FLOW1_MERGED\n"
        "- PR_1196_OVERNIGHT_END_TO_END_CONTRACT\n\n"
        "## What This Runner Does\n"
        "- inspect repo state for allowed file scope\n"
        "- select and queue next safe packet work\n"
        "- write validation, publish, and checkpoint artifacts\n"
        "- detect external gates and stop for owner action\n\n"
        "## What This Runner Does Not Do\n"
        "- broker/API calls\n"
        "- credential loading\n"
        "- order placement\n"
        "- money movement\n"
        "- runtime activation\n"
        "- production or live execution\n\n"
        "## Untracked File Policy\n"
        "Allowed untracked files are only in active packet scope. "
        "All other untracked files must be treated as disallowed worktree scope.\n\n"
        "## Active Packet Queue\n"
        "1) Flow 2 packet\n"
        "2) Flow 3 packet\n"
        "3) Live exception gate packet\n\n"
        "## External Gate Stop Conditions\n"
        "Owner, credential, broker, evidence, and capital gates stop host continuation.\n\n"
        "## Host Runner Script\n"
        "scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1\n\n"
        "## Validation And Publish Flow\n"
        "Run validator first, then publish, then merge only after checks pass.\n\n"
        "## Owner Overnight Procedure\n"
        "Run the host script in DryRun first, then run full cycle execution on clean state.\n\n"
        "## Final Owner Sentence\n"
        + _final_owner_sentence()
    )


def _final_owner_sentence() -> str:
    return (
        "AIOS Forex full overnight work runner is established locally: it gathers the landed flow 1 and overnight contract anchors, "
        "reads the active packet queue, classifies untracked files against active allowed paths, validates and publishes "
        "repo-safe packets when permitted, writes checkpoints and next Codex prompts, and continues toward Flow 2 evidence capture, "
        "Flow 3 profit-loop gating, and live exception bridging, while broker/API access, credentials, order submission, "
        "live trading, autonomous operation, and money movement remain separately gated."
    )


def generate_artifacts(owner_input: dict | None = None) -> dict:
    result = evaluate_forex_full_overnight_work_runner(owner_input)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    JSON_REPORT_PATH.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    CHECKPOINT_PATH.write_text(render_checkpoint(result), encoding="utf-8")
    ACTIVE_PACKET_QUEUE_PATH.write_text(render_active_packet_queue(result), encoding="utf-8")
    EXTERNAL_GATE_STOP_PATH.write_text(render_external_gate_stop(result), encoding="utf-8")
    OWNER_HANDOFF_PATH.write_text(render_owner_handoff(result), encoding="utf-8")
    NEXT_CODEX_PROMPT_PATH.write_text(render_next_codex_prompt(result), encoding="utf-8")
    DOC_PATH.write_text(render_contract_doc(), encoding="utf-8")
    return result


def contains_banned_output_tokens(payload: str | dict) -> bool:
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    lowered = str(payload).lower()
    return any(token.lower() in lowered for token in BANNED_OUTPUT_TOKENS)


def _normalize_path(path: str) -> str:
    return _normalize_path_like(path, strip_prefix=False)


def _normalize_path_like(path: str, strip_prefix: bool = True) -> str:
    normalized = path.replace("\\", "/").strip()
    if strip_prefix and normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _is_inside_allowed(path: str, allowed_path: str) -> bool:
    path = _normalize_path_like(path)
    allowed = _normalize_path_like(allowed_path)
    return path == allowed or path.startswith(f"{allowed}/")


def _to_status_lines(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) or item is not None]


def _to_list(value: Any, default: list[str] | None = None) -> list[str]:
    if value is None:
        return list(default or [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _default_next_owner_action(selected_packet: dict | None) -> str:
    if selected_packet:
        return f"SELECT_NEXT_PACKET: {selected_packet.get('packet_id')}"
    return "SELECT_NEXT_PACKET"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    generate_artifacts()
