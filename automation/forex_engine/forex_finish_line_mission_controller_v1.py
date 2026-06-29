"""Finish-line mission controller for the governed AIOS Forex lane.

This controller is an owner-facing, offline projection layer. It reads only
repo-local safety and evidence state artifacts, emits deterministic status, and
keeps all live execution paths locked.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping


PACKET_ID = "PKT-FOREX-FINISH-LINE-MISSION-CONTROLLER-V1"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
MISSION_NAME = "Governed Forex Finish Line"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
PROGRAM_NAME = "Forex Profit Autonomy System"
EPIC_ID = "EPC-FOREX-FINISH-LINE-CONTROLLER-001"
EPIC_NAME = "One Script Forex Finish Line Controller"
BUCKET_ID = "BKT-FOREX-FINISH-LINE-CONTROLLER-001"
BUCKET_NAME = "Finish Line Mission Controller And Emoji Dashboard Projection"

STARTING_LINE = "STARTING_LINE"
SAFETY_CLOSURE = "SAFETY_CLOSURE"
BROKER_PROBE_LOCKED = "BROKER_PROBE_LOCKED"
DEMO_PROOF_LOCKED = "DEMO_PROOF_LOCKED"
LIVE_MICRO_LOCKED = "LIVE_MICRO_LOCKED"
LIVE_TRADING_LOCKED = "LIVE_TRADING_LOCKED"
VACATION_MODE_LOCKED = "VACATION_MODE_LOCKED"

SUPPORTED_MODES = (
    STARTING_LINE,
    SAFETY_CLOSURE,
    BROKER_PROBE_LOCKED,
    DEMO_PROOF_LOCKED,
    LIVE_MICRO_LOCKED,
    LIVE_TRADING_LOCKED,
    VACATION_MODE_LOCKED,
)
LOCKED_EXECUTION_MODES = (
    BROKER_PROBE_LOCKED,
    DEMO_PROOF_LOCKED,
    LIVE_MICRO_LOCKED,
    LIVE_TRADING_LOCKED,
    VACATION_MODE_LOCKED,
)
UNLOCKED_INSPECTION_MODES = (STARTING_LINE, SAFETY_CLOSURE)

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "Reports" / "forex_delivery"
DEFAULT_COMPLETION_STATE_PATH = (
    REPORTS_DIR
    / "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json"
)
DEFAULT_INTAKE_STATE_PATH = (
    REPORTS_DIR
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json"
)
DEFAULT_P1_HARDENING_REPORT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_SANITIZED_EVIDENCE_INTAKE_P1_HARDENING_V1_REPORT.md"
)
DEFAULT_STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_REPORT.md"
)
DEFAULT_DASHBOARD_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINISH_LINE_EMOJI_DASHBOARD_PROJECTION_V1.json"
)
DEFAULT_NEXT_PACKET_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_NEXT_CODEX_PACKET_V1.md"
)

COMPLETION_CONTROLLER_MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py"
)
SANITIZED_INTAKE_MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "forex_autonomy_sanitized_evidence_intake_update_v1.py"
)

LIVE_READY_THRESHOLD_PERCENT = 90.0
AUTONOMY_WINDOW_TARGET = "22HR_6DAY_SUPERVISED"

SAFETY_BOUNDARY = {
    "order_execution_allowed": False,
    "broker_api_allowed": False,
    "credentials_allowed": False,
    "account_identifier_persistence_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
    "live_trading_authorized": False,
}

EMOJI_BY_TILE = {
    "controller": "🚦",
    "evidence": "📄",
    "safety": "🛡️",
    "broker": "🏦",
    "proof": "📈",
    "live_micro": "🧪",
    "live_trading": "⛔",
    "vacation_mode": "🏖️",
    "audit": "🧾",
    "next_action": "➡️",
}

VALIDATOR_CHAIN = (
    "python -m py_compile automation/forex_engine/forex_finish_line_mission_controller_v1.py scripts/forex_delivery/run_forex_finish_line_mission_controller_v1.py",
    "python -m pytest tests/forex_engine/test_forex_finish_line_mission_controller_v1.py -q",
    "python scripts/forex_delivery/run_forex_finish_line_mission_controller_v1.py --mode STARTING_LINE --write-state --write-report --write-dashboard",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_EMOJI_DASHBOARD_PROJECTION_V1.json",
    "git diff --check -- automation/forex_engine/forex_finish_line_mission_controller_v1.py scripts/forex_delivery/run_forex_finish_line_mission_controller_v1.py tests/forex_engine/test_forex_finish_line_mission_controller_v1.py Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_REPORT.md Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_EMOJI_DASHBOARD_PROJECTION_V1.json Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_NEXT_CODEX_PACKET_V1.md",
    "git status --short --branch",
)

LOCKED_MODE_REASONS = {
    BROKER_PROBE_LOCKED: (
        "Locked until critical safety evidence closes and owner-approved, "
        "value-free broker probe scope exists."
    ),
    DEMO_PROOF_LOCKED: (
        "Locked until safety closure and offline autonomy rerun evidence support "
        "a supervised demo proof packet."
    ),
    LIVE_MICRO_LOCKED: (
        "Locked until proof ledger, live risk policy, owner exception approval, "
        "and all safety gates clear."
    ),
    LIVE_TRADING_LOCKED: (
        "Locked until real-money proof, monitoring, evidence ledger, risk controls, "
        "and owner live authorization clear."
    ),
    VACATION_MODE_LOCKED: (
        "Locked until sustained 22h/day 6d/week supervised evidence, proof ledger, "
        "monitoring, and owner approval clear."
    ),
}

FINISH_LINE_GATE_LABELS = (
    "critical_safety_evidence_closed",
    "broker_probe_readiness_approved",
    "demo_proof_exists",
    "owner_live_micro_exception_approved",
    "proof_ledger_exists",
    "live_risk_policy_clear",
    "sustained_operation_monitor_exists",
    "live_trading_owner_authorization_exists",
    "supervised_22h_6d_operations_evidence_exists",
)

CRITICAL_SAFETY_CONTROL_FIELDS = (
    "kill_switch_state",
    "daily_stop_state",
    "max_loss_state",
    "monitoring_ready",
)
CRITICAL_SAFETY_RELEVANT_MISSING_FIELDS = (
    *CRITICAL_SAFETY_CONTROL_FIELDS,
    "evidence_age_days",
)
SAFETY_AGE_OR_STALE_BLOCKER_MARKERS = (
    "evidence_age_days",
    "freshness",
    "stale",
)


def run_forex_finish_line_mission_controller_v1(
    mode: str = STARTING_LINE,
) -> dict[str, Any]:
    selected_mode = _normalize_mode(mode)
    completion_state = _load_json_mapping(DEFAULT_COMPLETION_STATE_PATH)
    intake_state = _load_json_mapping(DEFAULT_INTAKE_STATE_PATH)

    readiness_inputs = _build_starting_line_inputs(
        completion_state=completion_state,
        intake_state=intake_state,
    )
    starting_line_readiness_percent = _percent_from_bool_map(readiness_inputs)
    critical_safety_blockers = _critical_safety_blockers(intake_state, completion_state)
    missing_evidence_fields = _string_list(intake_state.get("missing_evidence_fields"))
    effective_safety_missing_evidence_fields = _safety_missing_evidence_fields(
        completion_state=completion_state,
        intake_state=intake_state,
        missing_evidence_fields=missing_evidence_fields,
    )
    finish_line_gates = _build_finish_line_gates(
        completion_state=completion_state,
        intake_state=intake_state,
        critical_safety_blockers=critical_safety_blockers,
        missing_evidence_fields=effective_safety_missing_evidence_fields,
    )
    finish_line_readiness_percent = _finish_line_readiness_percent(finish_line_gates)

    controller_status = _controller_status(
        selected_mode,
        critical_safety_blockers,
        effective_safety_missing_evidence_fields,
    )
    current_phase = _current_phase(
        selected_mode,
        critical_safety_blockers,
        effective_safety_missing_evidence_fields,
    )
    next_safe_action = _next_safe_action(
        selected_mode=selected_mode,
        critical_safety_blockers=critical_safety_blockers,
        missing_evidence_fields=effective_safety_missing_evidence_fields,
        intake_state=intake_state,
        completion_state=completion_state,
    )

    blocker_summary = _build_blocker_summary(
        completion_state=completion_state,
        intake_state=intake_state,
        critical_safety_blockers=critical_safety_blockers,
        missing_evidence_fields=effective_safety_missing_evidence_fields,
        finish_line_gates=finish_line_gates,
    )
    live_target = _build_live_trading_finish_line_target()
    vacation_target = _build_vacation_mode_target()
    locked_modes = dict(LOCKED_MODE_REASONS)
    unlocked_modes = list(UNLOCKED_INSPECTION_MODES)

    result: dict[str, Any] = {
        "controller_status": controller_status,
        "selected_mode": selected_mode,
        "current_phase": current_phase,
        "next_safe_action": next_safe_action,
        "starting_line_readiness_percent": starting_line_readiness_percent,
        "finish_line_readiness_percent": finish_line_readiness_percent,
        "live_trading_finish_line_target": live_target,
        "vacation_mode_target": vacation_target,
        "locked_modes": locked_modes,
        "unlocked_modes": unlocked_modes,
        "blocker_summary": blocker_summary,
        "emoji_dashboard_projection": {},
        "context_boxes": {},
        "safety_boundary": dict(SAFETY_BOUNDARY),
        "starting_line_inputs": readiness_inputs,
        "finish_line_gates": finish_line_gates,
        "source_artifacts": {
            "completion_state": _relative_path(DEFAULT_COMPLETION_STATE_PATH),
            "sanitized_evidence_intake_state": _relative_path(DEFAULT_INTAKE_STATE_PATH),
            "p1_hardening_report": _relative_path(DEFAULT_P1_HARDENING_REPORT_PATH),
        },
        "dashboard_projection_notice": "Projection only; report artifacts remain source of truth.",
        "validator_chain": list(VALIDATOR_CHAIN),
        "packet_id": PACKET_ID,
        "mission_id": MISSION_ID,
        "mission_name": MISSION_NAME,
        "program_id": PROGRAM_ID,
        "program_name": PROGRAM_NAME,
        "epic_id": EPIC_ID,
        "epic_name": EPIC_NAME,
        "bucket_id": BUCKET_ID,
        "bucket_name": BUCKET_NAME,
    }
    dashboard = _build_emoji_dashboard_projection(
        selected_mode=selected_mode,
        controller_status=controller_status,
        critical_safety_blockers=critical_safety_blockers,
        missing_evidence_fields=effective_safety_missing_evidence_fields,
        next_safe_action=next_safe_action,
        finish_line_readiness_percent=finish_line_readiness_percent,
    )
    result["emoji_dashboard_projection"] = dashboard
    result["context_boxes"] = {
        name: tile["context_box_text"]
        for name, tile in dashboard.items()
        if tile["context_box_required"]
    }
    return result


def build_report_markdown(result: Mapping[str, Any]) -> str:
    branch = _git_value("branch", "--show-current")
    head = _git_value("rev-parse", "HEAD")
    locked_modes = _mapping(result.get("locked_modes"))
    blocker_summary = _mapping(result.get("blocker_summary"))

    lines = [
        "# AIOS Forex Finish Line Mission Controller V1 Report",
        "",
        f"Status: {result.get('controller_status')}",
        f"Current branch: {branch}",
        f"Current head: {head}",
        f"Selected mode: {result.get('selected_mode')}",
        f"Starting-line readiness: {result.get('starting_line_readiness_percent')}%",
        f"Finish-line readiness: {result.get('finish_line_readiness_percent')}%",
        "",
        "Live trading finish-line target:",
        f"- target: {_mapping(result.get('live_trading_finish_line_target')).get('target')}",
        f"- locked: {_mapping(result.get('live_trading_finish_line_target')).get('locked')}",
        f"- window: {_mapping(result.get('live_trading_finish_line_target')).get('supervised_operation_target')}",
        "",
        "Vacation mode target:",
        f"- target: {_mapping(result.get('vacation_mode_target')).get('target')}",
        f"- locked: {_mapping(result.get('vacation_mode_target')).get('locked')}",
        "",
        "Locked modes:",
    ]
    for mode, reason in locked_modes.items():
        lines.append(f"- {mode}: {reason}")

    lines.extend(["", "Unlocked modes:"])
    for mode in _string_list(result.get("unlocked_modes")):
        lines.append(f"- {mode}")

    lines.extend(["", "Blocker summary:"])
    for key, value in blocker_summary.items():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            f"Next safe action: {result.get('next_safe_action')}",
            f"Dashboard projection path: {_relative_path(DEFAULT_DASHBOARD_OUTPUT_PATH)}",
            "",
            "Safety boundary:",
        ]
    )
    for key, value in _mapping(result.get("safety_boundary")).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "Validators:"])
    for validator in _string_list(result.get("validator_chain")):
        lines.append(f"- {validator}")

    lines.extend(
        [
            "",
            "No broker API / no credentials / no order execution statement:",
            "- No broker API was called.",
            "- No credentials or .env files were read.",
            "- No account identifiers were persisted.",
            "- No orders were placed.",
            "- No scheduler, daemon, loop, webhook, live routing, commit, push, or PR action was started.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    blocker_summary = _mapping(result.get("blocker_summary"))
    critical_blockers = _string_list(blocker_summary.get("critical_safety_blockers"))
    missing_evidence_fields = _string_list(blocker_summary.get("missing_evidence_fields"))
    allowed_paths = (
        "automation/forex_engine/forex_finish_line_mission_controller_v1.py",
        "scripts/forex_delivery/run_forex_finish_line_mission_controller_v1.py",
        "Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json",
        "Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_REPORT.md",
        "Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_EMOJI_DASHBOARD_PROJECTION_V1.json",
        "Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_NEXT_CODEX_PACKET_V1.md",
    )
    validator_chain = (
        "python scripts/forex_delivery/run_forex_finish_line_mission_controller_v1.py --mode STARTING_LINE",
        "python -m json.tool Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json",
        "python -m json.tool Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_EMOJI_DASHBOARD_PROJECTION_V1.json",
        "git status --short --branch",
    )
    if critical_blockers:
        packet_name = "Critical Safety Evidence Closure Dry Run V1"
        packet_id = "PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-CLOSURE-DRY-RUN-V1"
        lane = "Forex critical safety evidence closure"
        allowed_paths = (
            "automation/forex_engine/forex_critical_safety_evidence_closure_v1.py",
            "scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py",
            "tests/forex_engine/test_forex_critical_safety_evidence_closure_v1.py",
            "Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json",
            "Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md",
            "Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md",
        )
        validator_chain = (
            "python -m py_compile automation/forex_engine/forex_critical_safety_evidence_closure_v1.py scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py",
            "python -m pytest tests/forex_engine/test_forex_critical_safety_evidence_closure_v1.py -q",
            "python scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py",
            "python -m json.tool Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json",
            "git status --short --branch",
        )
        mission = (
            "Inspect the current blocked safety fields and produce a closure plan "
            "for kill switch, daily stop, max loss, and monitoring evidence."
        )
        stop_point = "Stop after read-only safety evidence closure plan and final report."
        next_action = (
            "Create a read-only closure plan for the remaining critical safety "
            "evidence blockers. Do not advance broker, demo, live micro, live trading, "
            "or vacation mode."
        )
    elif missing_evidence_fields:
        shown_fields = ", ".join(missing_evidence_fields[:5])
        suffix = " and more" if len(missing_evidence_fields) > 5 else ""
        packet_name = "Missing Sanitized Evidence Collection Dry Run V1"
        packet_id = "PKT-FOREX-MISSING-SANITIZED-EVIDENCE-COLLECTION-DRY-RUN-V1"
        lane = "Forex missing sanitized evidence collection"
        allowed_paths = (
            "automation/forex_engine/forex_autonomy_sanitized_evidence_intake_update_v1.py",
            "scripts/forex_delivery/run_forex_autonomy_sanitized_evidence_intake_update_v1.py",
            "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json",
            "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json",
            "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_REPORT.md",
            "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_NEXT_CODEX_PACKET_V1.md",
        )
        validator_chain = (
            "python scripts/forex_delivery/run_forex_autonomy_sanitized_evidence_intake_update_v1.py",
            "python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json",
            "python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json",
            "git status --short --branch",
        )
        mission = (
            "Inspect missing sanitized evidence fields and prepare an owner evidence "
            "collection plan before any readiness advancement."
        )
        stop_point = (
            "Stop after read-only missing sanitized evidence collection plan and "
            "final report."
        )
        next_action = (
            "Collect missing sanitized evidence for "
            f"{shown_fields}{suffix} first; keep live, broker/API, demo, micro, "
            "trading, scheduler, daemon, and webhook paths locked."
        )
    else:
        packet_name = "Emoji Dashboard Projection Continuation Dry Run V1"
        packet_id = "PKT-FOREX-FINISH-LINE-DASHBOARD-PROJECTION-CONTINUATION-DRY-RUN-V1"
        lane = "Forex emoji dashboard projection continuation"
        mission = (
            "Inspect finish-line controller output and identify whether dashboard "
            "projection representation is stale."
        )
        stop_point = "Stop after read-only dashboard projection continuation report."
        next_action = (
            "Review dashboard projection freshness against source artifacts; do not "
            "make dashboard source-of-truth mutations."
        )

    allowed_paths_text = "\n".join(allowed_paths)
    validator_chain_text = "\n".join(validator_chain)
    return (
        "CODEX-ONLY PROMPT\n\n"
        "AI_OS EXECUTION TOKEN\n"
        "AI_OS BOOTSTRAP REQUIRED\n\n"
        "IDENTITY MARKER\n"
        f"{packet_id}\n\n"
        "SUPERVISOR IDENTITY\n"
        "ChatGPT planning supervisor\n\n"
        "PACKET ID\n"
        f"{packet_id}\n\n"
        "PACKET NAME\n"
        f"{packet_name}\n\n"
        "MODE\n"
        "DRY_RUN\n\n"
        "ZONE\n"
        "Trading Lab / Forex\n\n"
        "WORKER IDENTITY\n"
        "Codex\n\n"
        "LANE\n"
        f"{lane}\n\n"
        "WORKTREE\n"
        "C:\\Dev\\Ai.Os\n\n"
        "BRANCH\n"
        "resolve after preflight\n\n"
        "MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY\n"
        "Mission ID: MISSION-AIOS-FOREX-FINISH-LINE-V1\n"
        "Mission Name: Governed Forex Finish Line\n"
        "Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1\n"
        "Program Name: Forex Profit Autonomy System\n"
        "Epic ID: EPC-FOREX-FINISH-LINE-CONTROLLER-001\n"
        "Epic Name: One Script Forex Finish Line Controller\n"
        "Bucket ID: BKT-FOREX-FINISH-LINE-CONTROLLER-001\n"
        "Bucket Name: Finish Line Mission Controller And Emoji Dashboard Projection\n"
        f"Packet ID: {packet_id}\n"
        f"Packet Name: {packet_name}\n\n"
        "MISSION\n"
        f"{mission}\n\n"
        "PREFLIGHT\n"
        "cd C:\\Dev\\Ai.Os\n"
        "git status --short --branch\n"
        "git branch --show-current\n"
        "git log -1 --oneline\n\n"
        "ALLOWED PATHS\n"
        f"{allowed_paths_text}\n\n"
        "FORBIDDEN PATHS\n"
        "AGENTS.md\n"
        "README.md\n"
        "WHITEPAPER.md\n"
        "RISK_POLICY.md\n"
        ".env\n"
        "secrets\n"
        "credential files\n"
        "broker account identifiers\n"
        "broker modules\n"
        "scheduler files\n"
        "daemon files\n"
        "webhook files\n"
        "dashboard mutation files\n"
        "unrelated docs\n"
        "unrelated tests\n"
        "any path outside C:\\Dev\\Ai.Os\n\n"
        "APPROVAL AUTHORITY\n"
        "Human Owner approval required for APPLY, broker/API use, credentials, "
        "live trading, scheduler, daemon, webhook, or dashboard mutation.\n"
        "A later Human Owner message that explicitly approves commit is required before commit.\n"
        "A later Human Owner message that explicitly approves push is required before push.\n\n"
        "VALIDATOR CHAIN\n"
        f"{validator_chain_text}\n\n"
        "SAFE NEXT ACTION\n"
        f"{next_action}\n\n"
        "RULES\n"
        f"{next_action}\n"
        "Do not place trades.\n"
        "Do not use broker API.\n"
        "Do not use credentials.\n"
        "Do not authorize live trading.\n"
        "Do not start schedulers, daemons, loops, webhooks, or background workers.\n"
        "Do not commit.\n"
        "Do not push.\n"
        "Do not create PR.\n\n"
        "STOP POINT\n"
        f"{stop_point}\n\n"
        "FINAL REPORT FORMAT\n"
        "STATUS:\n"
        "CURRENT_BRANCH:\n"
        "CURRENT_HEAD:\n"
        "WHAT_WAS_INSPECTED:\n"
        "FINDINGS:\n"
        "NEXT_SAFE_ACTION:\n"
        "ORDER_EXECUTION:\n"
        "BROKER_API_USED:\n"
        "CREDENTIALS_USED:\n"
        "GIT_STATUS:\n"
    )


def _normalize_mode(mode: str) -> str:
    selected = str(mode).strip().upper()
    if selected not in SUPPORTED_MODES:
        raise ValueError(
            f"unknown finish-line mission controller mode: {mode!r}; "
            f"supported modes: {', '.join(SUPPORTED_MODES)}"
        )
    return selected


def _build_starting_line_inputs(
    *,
    completion_state: Mapping[str, Any],
    intake_state: Mapping[str, Any],
) -> dict[str, bool]:
    return {
        "autonomy_completion_controller_available": (
            COMPLETION_CONTROLLER_MODULE_PATH.exists()
            and DEFAULT_COMPLETION_STATE_PATH.exists()
            and bool(completion_state)
        ),
        "sanitized_evidence_intake_available": (
            SANITIZED_INTAKE_MODULE_PATH.exists()
            and DEFAULT_INTAKE_STATE_PATH.exists()
            and bool(intake_state)
        ),
        "p1_hardening_report_available": DEFAULT_P1_HARDENING_REPORT_PATH.exists(),
        "critical_safety_blockers_known": (
            "blocked_evidence_fields" in intake_state
            or "governor_blockers" in completion_state
        ),
        "next_safe_action_known": bool(
            _text(intake_state.get("next_safe_action"))
            or _text(completion_state.get("next_safe_action"))
        ),
    }


def _build_finish_line_gates(
    *,
    completion_state: Mapping[str, Any],
    intake_state: Mapping[str, Any],
    critical_safety_blockers: list[str],
    missing_evidence_fields: list[str],
) -> dict[str, bool]:
    updated_preview = _mapping(intake_state.get("updated_governor_input_preview"))
    safety_missing_evidence_fields = _safety_missing_evidence_fields(
        completion_state=completion_state,
        intake_state=intake_state,
        missing_evidence_fields=missing_evidence_fields,
    )
    critical_safety_closed = (
        "blocked_evidence_fields" in intake_state
        and not critical_safety_blockers
        and not safety_missing_evidence_fields
    )
    broker_gate_status = _text(completion_state.get("broker_gate_status")).upper()
    candidate_status = _text(completion_state.get("candidate_status")).upper()
    return {
        "critical_safety_evidence_closed": critical_safety_closed,
        "broker_probe_readiness_approved": (
            critical_safety_closed and broker_gate_status == "BROKER_GATE_READY"
        ),
        "demo_proof_exists": (
            critical_safety_closed
            and candidate_status
            in {"DEMO_SUPERVISED_READY", "LIVE_MICRO_EXCEPTION_REVIEW_READY"}
        ),
        "owner_live_micro_exception_approved": (
            critical_safety_closed
            and _as_bool(updated_preview.get("owner_live_micro_exception_approved"))
        ),
        "proof_ledger_exists": False,
        "live_risk_policy_clear": False,
        "sustained_operation_monitor_exists": False,
        "live_trading_owner_authorization_exists": False,
        "supervised_22h_6d_operations_evidence_exists": False,
    }


def _finish_line_readiness_percent(gates: Mapping[str, bool]) -> float:
    if not gates:
        return 0.0
    passed = sum(1 for value in gates.values() if bool(value))
    percent = round((passed / len(gates)) * 100, 2)
    if passed != len(gates):
        return min(percent, LIVE_READY_THRESHOLD_PERCENT - 1)
    return 100.0


def _percent_from_bool_map(values: Mapping[str, bool]) -> float:
    if not values:
        return 0.0
    passed = sum(1 for value in values.values() if bool(value))
    return round((passed / len(values)) * 100, 2)


def _critical_safety_blockers(
    intake_state: Mapping[str, Any],
    completion_state: Mapping[str, Any],
) -> list[str]:
    if "blocked_evidence_fields" in intake_state:
        explicit_blockers = _dedupe_list(
            _string_list(intake_state.get("blocked_evidence_fields"))
        )
        return [
            field
            for field in explicit_blockers
            if field in CRITICAL_SAFETY_CONTROL_FIELDS
        ]

    derived: list[str] = []
    for blocker in _string_list(completion_state.get("governor_blockers")):
        lowered = blocker.lower()
        if "kill switch" in lowered:
            derived.append("kill_switch_state")
        if "daily stop" in lowered:
            derived.append("daily_stop_state")
        if "max loss" in lowered:
            derived.append("max_loss_state")
        if "monitoring" in lowered:
            derived.append("monitoring_ready")
    return _dedupe_list(derived)


def _has_stale_evidence_blocker(
    *,
    completion_state: Mapping[str, Any],
    intake_state: Mapping[str, Any],
    missing_evidence_fields: list[str],
) -> bool:
    if "evidence_age_days" in _string_list(missing_evidence_fields):
        return True
    return bool(
        _safety_stale_evidence_blockers(
            completion_state=completion_state,
            intake_state=intake_state,
        )
    )


def _safety_stale_evidence_blockers(
    *,
    completion_state: Mapping[str, Any],
    intake_state: Mapping[str, Any],
) -> list[str]:
    blocker_values = (
        _string_list(intake_state.get("blocked_evidence_fields"))
        + _string_list(intake_state.get("rejected_evidence_fields"))
        + _string_list(completion_state.get("governor_blockers"))
        + _string_list(completion_state.get("bucket_blockers"))
    )
    blocker_values.extend(_extract_freshness_fields(completion_state))
    blocker_values.extend(_extract_freshness_fields(intake_state))
    return _dedupe_list(
        [blocker for blocker in blocker_values if _is_safety_freshness_blocker(blocker)]
    )


def _extract_freshness_fields(state: Mapping[str, Any]) -> list[str]:
    blocker_values: list[str] = []
    for key, value in state.items():
        if _contains_freshness_marker(key):
            blocker_values.append(_safe_field_blocker_text(key, value))
        elif isinstance(value, (str, int, float, bool)) and _contains_freshness_marker(
            value
        ):
            blocker_values.append(_safe_field_blocker_text(key, value))
    return blocker_values


def _contains_freshness_marker(value: Any) -> bool:
    lowered = str(value).lower()
    return any(marker in lowered for marker in SAFETY_AGE_OR_STALE_BLOCKER_MARKERS)


def _safe_field_blocker_text(key: Any, value: Any) -> str:
    raw_key = _text(key)
    if value is None or value == "":
        return raw_key
    if isinstance(value, (list, tuple, set)):
        joined = ", ".join(_text(item) for item in value if _text(item))
        return f"{raw_key}: {joined}" if joined else raw_key
    return f"{raw_key}: {_text(value)}"


def _is_safety_freshness_blocker(value: Any) -> bool:
    lowered = str(value).strip().lower()
    return any(marker in lowered for marker in SAFETY_AGE_OR_STALE_BLOCKER_MARKERS)


def _safety_missing_evidence_fields(
    *,
    completion_state: Mapping[str, Any],
    intake_state: Mapping[str, Any],
    missing_evidence_fields: list[str],
) -> list[str]:
    normalized_relevant_fields = {
        field.strip(): field.strip()
        for field in _string_list(missing_evidence_fields)
        if str(field).strip() in CRITICAL_SAFETY_RELEVANT_MISSING_FIELDS
    }

    stale_blockers = _safety_stale_evidence_blockers(
        completion_state=completion_state,
        intake_state=intake_state,
    )
    combined_fields = list(normalized_relevant_fields.values()) + stale_blockers
    return _dedupe_list(combined_fields)


def _controller_status(
    mode: str,
    critical_safety_blockers: list[str],
    missing_evidence_fields: list[str],
) -> str:
    if mode in LOCKED_EXECUTION_MODES:
        return "MODE_LOCKED"
    if mode == SAFETY_CLOSURE:
        if critical_safety_blockers:
            return "SAFETY_CLOSURE_REQUIRED"
        if missing_evidence_fields:
            return "SAFETY_CLOSURE_MISSING_EVIDENCE_COLLECTION_REQUIRED"
        return "SAFETY_CLOSURE_CLEAR_FOR_OFFLINE_RERUN"
    if critical_safety_blockers:
        return "STARTING_LINE_READY_WITH_SAFETY_BLOCKERS"
    if missing_evidence_fields:
        return "STARTING_LINE_MISSING_EVIDENCE_COLLECTION_REQUIRED"
    return "STARTING_LINE_READY"


def _current_phase(
    mode: str,
    critical_safety_blockers: list[str],
    missing_evidence_fields: list[str],
) -> str:
    if mode in LOCKED_EXECUTION_MODES:
        return f"{mode}_HOLD"
    if mode == SAFETY_CLOSURE:
        if critical_safety_blockers:
            return "CRITICAL_SAFETY_EVIDENCE_CLOSURE"
        if missing_evidence_fields:
            return "MISSING_SANITIZED_EVIDENCE_COLLECTION_PENDING"
        return "SAFETY_CLOSURE_COMPLETE"
    if critical_safety_blockers:
        return "SAFETY_EVIDENCE_CLOSURE_PENDING"
    if missing_evidence_fields:
        return "MISSING_SANITIZED_EVIDENCE_COLLECTION_PENDING"
    return "OFFLINE_AUTONOMY_RERUN_READY"


def _next_safe_action(
    *,
    selected_mode: str,
    critical_safety_blockers: list[str],
    missing_evidence_fields: list[str],
    intake_state: Mapping[str, Any],
    completion_state: Mapping[str, Any],
) -> str:
    if selected_mode in LOCKED_EXECUTION_MODES:
        return f"{LOCKED_MODE_REASONS[selected_mode]} Run STARTING_LINE or SAFETY_CLOSURE only."

    if critical_safety_blockers:
        fields = ", ".join(critical_safety_blockers)
        return (
            "Close critical safety evidence for "
            f"{fields}; keep broker, demo, live micro, live trading, and vacation modes locked."
        )

    if missing_evidence_fields:
        fields = ", ".join(missing_evidence_fields[:5])
        suffix = " and more" if len(missing_evidence_fields) > 5 else ""
        return (
            "Collect or repair missing/stale safety evidence for "
            f"{fields}{suffix}, then rerun the offline autonomy controller."
        )

    fallback = _text(intake_state.get("next_safe_action")) or _text(
        completion_state.get("next_safe_action")
    )
    if fallback:
        return fallback
    return "Rerun the offline autonomy completion governor; keep live execution locked."


def _build_blocker_summary(
    *,
    completion_state: Mapping[str, Any],
    intake_state: Mapping[str, Any],
    critical_safety_blockers: list[str],
    missing_evidence_fields: list[str],
    finish_line_gates: Mapping[str, bool],
) -> dict[str, Any]:
    missing_finish_line_gates = [
        name for name in FINISH_LINE_GATE_LABELS if not finish_line_gates.get(name, False)
    ]
    return {
        "critical_safety_blockers": critical_safety_blockers,
        "missing_evidence_fields": missing_evidence_fields,
        "governor_blockers": _string_list(completion_state.get("governor_blockers")),
        "bucket_blockers": _string_list(completion_state.get("bucket_blockers")),
        "controller_candidate_status": _text(completion_state.get("candidate_status")),
        "controller_bucket_status": _text(completion_state.get("bucket_status")),
        "intake_status": _text(intake_state.get("intake_status")),
        "rerun_recommended": bool(intake_state.get("rerun_recommended")),
        "missing_finish_line_gates": missing_finish_line_gates,
    }


def _build_live_trading_finish_line_target() -> dict[str, Any]:
    return {
        "target": (
            "Proof-of-life profit evidence, owner-approved real-money live "
            "micro path, and sustained supervised operation."
        ),
        "supervised_operation_target": "22 hours/day, 6 days/week",
        "required_controls": [
            "kill_switch",
            "daily_stop",
            "max_loss",
            "monitoring",
            "evidence_ledger",
            "broker_readiness",
            "owner_approval",
        ],
        "locked": True,
        "live_trading_authorized": False,
        "profit_readiness_claimed": False,
    }


def _build_vacation_mode_target() -> dict[str, Any]:
    return {
        "target": (
            "Vacation/luxury mode after sustained supervised profit evidence, "
            "risk controls, proof ledger, monitoring, and owner approval."
        ),
        "locked": True,
        "unlock_requires": [
            "live_evidence",
            "risk_policy_clearance",
            "proof_ledger",
            "sustained_monitoring",
            "owner_approval",
            AUTONOMY_WINDOW_TARGET,
        ],
        "live_trading_authorized": False,
    }


def _build_emoji_dashboard_projection(
    *,
    selected_mode: str,
    controller_status: str,
    critical_safety_blockers: list[str],
    missing_evidence_fields: list[str],
    next_safe_action: str,
    finish_line_readiness_percent: float,
) -> dict[str, dict[str, Any]]:
    selected_locked = selected_mode in LOCKED_EXECUTION_MODES
    safety_locked = bool(critical_safety_blockers)
    evidence_status = "MISSING" if missing_evidence_fields else "READY"
    safety_status = "BLOCKED" if safety_locked else "READY"
    return {
        "controller": _tile(
            "controller",
            "LOCKED" if selected_locked else "ACTIVE",
            selected_locked,
            selected_locked,
            "Selected mode is locked.",
        ),
        "evidence": _tile(
            "evidence",
            evidence_status,
            False,
            bool(missing_evidence_fields),
            _short_list_context("Evidence gaps", missing_evidence_fields),
        ),
        "safety": _tile(
            "safety",
            safety_status,
            safety_locked,
            safety_locked,
            _short_list_context("Safety gaps", critical_safety_blockers),
        ),
        "broker": _tile(
            "broker",
            "LOCKED",
            True,
            True,
            "Broker probe waits for safety closure.",
        ),
        "proof": _tile(
            "proof",
            "LOCKED",
            True,
            True,
            "Proof waits for sanitized evidence.",
        ),
        "live_micro": _tile(
            "live_micro",
            "LOCKED",
            True,
            True,
            "Owner exception and proof ledger required.",
        ),
        "live_trading": _tile(
            "live_trading",
            "LOCKED",
            True,
            True,
            f"Finish readiness {finish_line_readiness_percent}%.",
        ),
        "vacation_mode": _tile(
            "vacation_mode",
            "LOCKED",
            True,
            True,
            "Requires sustained 22h/6d evidence.",
        ),
        "audit": _tile(
            "audit",
            "PROJECTION_ONLY",
            False,
            False,
            "",
        ),
        "next_action": _tile(
            "next_action",
            "READY",
            False,
            True,
            _short_text(next_safe_action),
        ),
    }


def _tile(
    tile_name: str,
    status: str,
    locked: bool,
    context_box_required: bool,
    context_box_text: str,
) -> dict[str, Any]:
    return {
        "emoji": EMOJI_BY_TILE[tile_name],
        "status": status,
        "locked": locked,
        "context_box_required": context_box_required,
        "context_box_text": context_box_text if context_box_required else "",
    }


def _short_list_context(prefix: str, values: list[str]) -> str:
    if not values:
        return ""
    shown = ", ".join(values[:3])
    if len(values) > 3:
        shown = f"{shown}, more"
    return _short_text(f"{prefix}: {shown}.")


def _short_text(value: str) -> str:
    text = " ".join(str(value).split())
    if len(text) <= 96:
        return text
    return text[:93].rstrip() + "..."


def _load_json_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _string_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    if isinstance(values, Mapping):
        return []
    if isinstance(values, (list, tuple, set)):
        return [str(value) for value in values]
    return [str(values)]


def _dedupe_list(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on", "armed", "ready"}


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _git_value(*command: str) -> str:
    try:
        return subprocess.check_output(["git", *command], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


__all__ = [
    "STARTING_LINE",
    "SAFETY_CLOSURE",
    "BROKER_PROBE_LOCKED",
    "DEMO_PROOF_LOCKED",
    "LIVE_MICRO_LOCKED",
    "LIVE_TRADING_LOCKED",
    "VACATION_MODE_LOCKED",
    "SUPPORTED_MODES",
    "LOCKED_EXECUTION_MODES",
    "DEFAULT_STATE_OUTPUT_PATH",
    "DEFAULT_REPORT_OUTPUT_PATH",
    "DEFAULT_DASHBOARD_OUTPUT_PATH",
    "DEFAULT_NEXT_PACKET_OUTPUT_PATH",
    "VALIDATOR_CHAIN",
    "run_forex_finish_line_mission_controller_v1",
    "build_report_markdown",
    "build_next_codex_packet",
]
