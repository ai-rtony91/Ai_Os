"""Critical safety evidence closure classifier for the AIOS Forex lane.

This layer consumes the Finish Line Mission Controller output and classifies
critical safety evidence status without reading secrets, broker APIs, or live
execution paths.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .forex_finish_line_mission_controller_v1 import (
    SAFETY_CLOSURE,
    STARTING_LINE,
    run_forex_finish_line_mission_controller_v1,
)


PACKET_ID = "PKT-FOREX-CRITICAL-SAFETY-CLOSURE-V1"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
MISSION_NAME = "Governed Forex Finish Line"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
PROGRAM_NAME = "Forex Profit Autonomy System"
EPIC_ID = "EPC-FOREX-CRITICAL-SAFETY-CLOSURE-001"
EPIC_NAME = "Critical Safety Evidence Closure"
BUCKET_ID = "BKT-FOREX-CRITICAL-SAFETY-CLOSURE-001"
BUCKET_NAME = "Forex Critical Safety Evidence Closure"

STATUS_PRESENT = "PRESENT"
STATUS_MISSING = "MISSING"
STATUS_BLOCKED = "BLOCKED"
STATUS_VERIFIED = "VERIFIED"
STATUS_UNKNOWN = "UNKNOWN"

CONTROL_FIELDS = (
    "kill_switch_state",
    "daily_stop_state",
    "max_loss_state",
    "monitoring_ready",
)
CONTROL_LABELS = {
    "kill_switch_state": "kill switch",
    "daily_stop_state": "daily stop",
    "max_loss_state": "max loss",
    "monitoring_ready": "monitoring",
}

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "Reports" / "forex_delivery"
DEFAULT_STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md"
)
DEFAULT_NEXT_PACKET_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md"
)

VALIDATOR_CHAIN = (
    "python -m py_compile automation/forex_engine/forex_critical_safety_evidence_closure_v1.py scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py",
    "python -m pytest tests/forex_engine/test_forex_critical_safety_evidence_closure_v1.py -q",
    "python scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py --write-state --write-report",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json",
    "git diff --check",
    "git status --short --branch",
)

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


def run_forex_critical_safety_evidence_closure_v1(
    *,
    controller_output: Mapping[str, Any] | None = None,
    write_state: bool = False,
    write_state_path: Path | str | None = None,
    write_report: bool = False,
    write_report_path: Path | str | None = None,
    write_next_packet_path: Path | str | None = None,
) -> dict[str, Any]:
    """Evaluate critical safety closure from Finish Line controller output."""

    source_output = (
        dict(controller_output)
        if controller_output is not None
        else dict(
            run_forex_finish_line_mission_controller_v1(mode=STARTING_LINE)
        )
    )
    if controller_output is None:
        source_output["selected_mode"] = SAFETY_CLOSURE
        source_output["controller_status"] = "SAFETY_CLOSURE_REQUIRED"
        source_output["current_phase"] = "CRITICAL_SAFETY_EVIDENCE_CLOSURE"
        finish_line_gates = dict(_mapping(source_output.get("finish_line_gates")))
        finish_line_gates["critical_safety_evidence_closed"] = False
        source_output["finish_line_gates"] = finish_line_gates
    controller_status = _text(source_output.get("controller_status"), STATUS_UNKNOWN)
    controller_phase = _text(source_output.get("current_phase"), STATUS_UNKNOWN)
    blocker_summary = _mapping(source_output.get("blocker_summary"))
    finish_line_gates = _mapping(source_output.get("finish_line_gates"))
    starting_inputs = _mapping(source_output.get("starting_line_inputs"))

    critical_blockers = _field_list(blocker_summary.get("critical_safety_blockers"))
    missing_fields = _field_list(blocker_summary.get("missing_evidence_fields"))
    critical_safety_closed = bool(
        finish_line_gates.get("critical_safety_evidence_closed")
    )
    critical_blockers_known = _critical_blockers_known(
        source_output=source_output,
        blocker_summary=blocker_summary,
        starting_inputs=starting_inputs,
    )

    control_evaluations = _classify_controls(
        critical_blockers=critical_blockers,
        missing_fields=missing_fields,
        critical_safety_closed=critical_safety_closed,
        critical_blockers_known=critical_blockers_known,
    )
    verified_controls = _controls_by_status(control_evaluations, STATUS_VERIFIED)
    missing_controls = _controls_by_status(control_evaluations, STATUS_MISSING)
    blocked_controls = _controls_by_status(control_evaluations, STATUS_BLOCKED)
    present_controls = _controls_by_status(control_evaluations, STATUS_PRESENT)
    unknown_controls = _controls_by_status(control_evaluations, STATUS_UNKNOWN)

    safety_completion_percent = _completion_percent(verified_controls)
    readiness_delta = round(100.0 - safety_completion_percent, 2)
    evidence_freshness = _classify_evidence_freshness(
        missing_fields=missing_fields,
        source_output=source_output,
    )
    remaining_blockers = _remaining_blockers(control_evaluations)
    governing_recommendation = _governing_recommendation(
        blocked_controls=blocked_controls,
        missing_controls=missing_controls,
        unknown_controls=unknown_controls,
        safety_completion_percent=safety_completion_percent,
    )
    controller_routing_recommendation = _controller_routing_recommendation(
        safety_completion_percent=safety_completion_percent,
        blocked_controls=blocked_controls,
        missing_controls=missing_controls,
        unknown_controls=unknown_controls,
    )
    next_safe_action = _next_safe_action(
        source_output=source_output,
        blocked_controls=blocked_controls,
        missing_controls=missing_controls,
        unknown_controls=unknown_controls,
        safety_completion_percent=safety_completion_percent,
    )

    result: dict[str, Any] = {
        "closure_status": _closure_status(safety_completion_percent, remaining_blockers),
        "safety_completion_percent": safety_completion_percent,
        "readiness_delta": readiness_delta,
        "controller_status": controller_status,
        "controller_phase": controller_phase,
        "controller_selected_mode": _text(
            source_output.get("selected_mode"), SAFETY_CLOSURE
        ),
        "controller_finish_line_readiness_percent": _float_or_zero(
            source_output.get("finish_line_readiness_percent")
        ),
        "controller_starting_line_readiness_percent": _float_or_zero(
            source_output.get("starting_line_readiness_percent")
        ),
        "control_evaluations": control_evaluations,
        "verified_controls": verified_controls,
        "missing_controls": missing_controls,
        "blocked_controls": blocked_controls,
        "present_controls": present_controls,
        "unknown_controls": unknown_controls,
        "remaining_blockers": remaining_blockers,
        "evidence_freshness": evidence_freshness,
        "governing_recommendation": governing_recommendation,
        "controller_routing_recommendation": controller_routing_recommendation,
        "next_safe_action": next_safe_action,
        "source_controller": {
            "packet_id": _text(source_output.get("packet_id"), "UNKNOWN"),
            "mission_id": _text(source_output.get("mission_id"), "UNKNOWN"),
            "mode": _text(source_output.get("selected_mode"), SAFETY_CLOSURE),
            "status": controller_status,
            "phase": controller_phase,
        },
        "source_artifacts": _mapping(source_output.get("source_artifacts")),
        "safety_boundary": dict(SAFETY_BOUNDARY),
        "order_execution": False,
        "broker_api_used": False,
        "credentials_used": False,
        "live_trading_authorized": False,
        "evidence_invented": False,
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

    if write_state:
        output_path = (
            Path(write_state_path)
            if write_state_path is not None
            else DEFAULT_STATE_OUTPUT_PATH
        )
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result["state_output_path"] = str(output_path)

    if write_report:
        report_path = (
            Path(write_report_path)
            if write_report_path is not None
            else DEFAULT_REPORT_OUTPUT_PATH
        )
        next_packet_path = (
            Path(write_next_packet_path)
            if write_next_packet_path is not None
            else DEFAULT_NEXT_PACKET_OUTPUT_PATH
        )
        report_path.write_text(build_report_markdown(result), encoding="utf-8")
        next_packet_path.write_text(build_next_codex_packet(result), encoding="utf-8")
        result["report_output_path"] = str(report_path)
        result["next_packet_output_path"] = str(next_packet_path)

    return result


def build_report_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex Critical Safety Evidence Closure V1 Report",
        "",
        f"Status: {result.get('closure_status')}",
        f"Current branch: {_git_value('branch', '--show-current')}",
        f"Current head: {_git_value('rev-parse', 'HEAD')}",
        f"Controller status: {result.get('controller_status')}",
        f"Controller phase: {result.get('controller_phase')}",
        f"Safety completion percent: {result.get('safety_completion_percent')}%",
        f"Readiness delta to full safety: {result.get('readiness_delta')}%",
        "",
        "Control evaluations:",
    ]
    for name in CONTROL_FIELDS:
        evaluation = _mapping(_mapping(result.get("control_evaluations")).get(name))
        lines.append(
            "- "
            f"{name}: {evaluation.get('status', STATUS_UNKNOWN)} "
            f"({evaluation.get('reason', 'no reason recorded')})"
        )

    lines.extend(
        [
            "",
            f"Verified controls: {_list_for_report(result.get('verified_controls'))}",
            f"Missing controls: {_list_for_report(result.get('missing_controls'))}",
            f"Blocked controls: {_list_for_report(result.get('blocked_controls'))}",
            f"Unknown controls: {_list_for_report(result.get('unknown_controls'))}",
            "",
            f"Evidence freshness: {_mapping(result.get('evidence_freshness')).get('status', STATUS_UNKNOWN)}",
            (
                "Evidence freshness reason: "
                f"{_mapping(result.get('evidence_freshness')).get('reason', STATUS_UNKNOWN)}"
            ),
            "",
            f"Governing recommendation: {result.get('governing_recommendation')}",
            (
                "Controller routing recommendation: "
                f"{result.get('controller_routing_recommendation')}"
            ),
            f"Next safe action: {result.get('next_safe_action')}",
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
            "No broker API / credentials / order execution statement:",
            "- No broker API was called.",
            "- No credentials or .env files were read.",
            "- No orders were placed.",
            "- No scheduler, daemon, loop, webhook, live routing, commit, push, or PR action was started.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    blocked = _string_list(result.get("blocked_controls"))
    missing = _string_list(result.get("missing_controls"))
    unknown = _string_list(result.get("unknown_controls"))
    status = _text(result.get("closure_status"), "SAFETY_CLOSURE_OPEN")
    lane = "Forex critical safety evidence closure"
    allowed_paths = (
        "automation/forex_engine/forex_critical_safety_evidence_closure_v1.py",
        "scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py",
        "Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json",
        "Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md",
        "Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md",
    )
    validator_chain = (
        "python scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py",
        "git status --short --branch",
    )
    mission = "Inspect critical safety evidence closure status and route follow-up actions."
    next_action = (
        "Keep broker, broker API, scheduler, daemon, webhook, and live trading lanes locked; "
        "work through the safety closure workflow."
    )

    if status == "SAFETY_CLOSURE_VERIFIED":
        packet_name = "Offline Autonomy Governor Rerun Readiness Dry Run V1"
        packet_id = "PKT-FOREX-OFFLINE-AUTONOMY-GOVERNOR-RERUN-READINESS-DRY-RUN-V1"
        allowed_paths = (
            "automation/forex_engine/forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
            "scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
            "tests/forex_engine/test_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
            "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json",
            "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_REPORT.md",
            "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_NEXT_CODEX_PACKET_V1.md",
        )
        validator_chain = (
            "python -m py_compile automation/forex_engine/forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
            "python -m pytest tests/forex_engine/test_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py -q",
            "python scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
            "python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json",
            "git status --short --branch",
        )
        lane = "Forex autonomy completion governor rerun and bucket policy"
        mission = (
            "Inspect critical safety closure output and prepare the next offline "
            "autonomy governor rerun. Keep broker, credential, order, scheduler, "
            "webhook, and live trading paths locked."
        )
        next_action = "Run a read-only offline autonomy rerun readiness inspection."
    else:
        packet_name = "Critical Safety Evidence Owner Collection Dry Run V1"
        packet_id = "PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-OWNER-COLLECTION-DRY-RUN-V1"
        mission = (
            "Inspect the remaining critical safety evidence blockers and produce "
            "an owner evidence collection checklist without inventing evidence."
        )
        blocker_text = ", ".join(blocked + missing + unknown) or "critical safety evidence"
        next_action = f"Collect or repair evidence for: {blocker_text}."

    lane = lane or "Forex critical safety evidence closure"
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
        "Epic ID: EPC-FOREX-CRITICAL-SAFETY-CLOSURE-001\n"
        "Epic Name: Critical Safety Evidence Closure\n"
        "Bucket ID: BKT-FOREX-CRITICAL-SAFETY-CLOSURE-001\n"
        "Bucket Name: Forex Critical Safety Evidence Closure\n"
        f"Packet ID: {packet_id}\n"
        f"Packet Name: {packet_name}\n\n"
        "MISSION\n"
        f"{mission}\n\n"
        "PREFLIGHT\n"
        "pwd\n"
        "git status --short --branch\n"
        "git branch --show-current\n"
        "git remote -v\n\n"
        "ALLOWED PATHS\n"
        f"{allowed_paths_text}\n\n"
        "FORBIDDEN PATHS\n"
        "AGENTS.md\n"
        "README.md\n"
        "RISK_POLICY.md\n"
        ".env\n"
        "secrets\n"
        "credential files\n"
        "broker account identifiers\n"
        "broker modules\n"
        "scheduler files\n"
        "daemon files\n"
        "webhook files\n"
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
        "Do not invent evidence.\n"
        "Do not place trades.\n"
        "Do not use broker API.\n"
        "Do not use credentials.\n"
        "Do not read .env.\n"
        "Do not authorize live trading.\n"
        "Do not start schedulers, daemons, loops, webhooks, or background workers.\n"
        "Do not commit.\n"
        "Do not push.\n"
        "Do not create PR.\n\n"
        "STOP POINT\n"
        "Stop after read-only critical safety evidence closure inspection and final report.\n\n"
        "FINAL REPORT FORMAT\n"
        "STATUS:\n"
        "CURRENT_BRANCH:\n"
        "CURRENT_HEAD:\n"
        "SAFETY_COMPLETION_PERCENT:\n"
        "VERIFIED_CONTROLS:\n"
        "BLOCKED_CONTROLS:\n"
        "NEXT_SAFE_ACTION:\n"
        "ORDER_EXECUTION:\n"
        "BROKER_API_USED:\n"
        "CREDENTIALS_USED:\n"
        "GIT_STATUS:\n"
    )


def _classify_controls(
    *,
    critical_blockers: list[str],
    missing_fields: list[str],
    critical_safety_closed: bool,
    critical_blockers_known: bool,
) -> dict[str, dict[str, str]]:
    evaluations: dict[str, dict[str, str]] = {}
    blocker_set = set(critical_blockers)
    missing_set = set(missing_fields)

    for field in CONTROL_FIELDS:
        if field in blocker_set:
            status = STATUS_BLOCKED
            reason = "Finish Line Mission Controller reports this control as a critical safety blocker."
        elif field in missing_set:
            status = STATUS_MISSING
            reason = "Finish Line Mission Controller reports this control as missing evidence."
        elif critical_safety_closed:
            status = STATUS_VERIFIED
            reason = "Finish Line Mission Controller reports critical safety evidence closed."
        elif critical_blockers_known:
            status = STATUS_PRESENT
            reason = "Controller knows critical safety blockers and does not report this control as blocked or missing."
        else:
            status = STATUS_UNKNOWN
            reason = "Controller output does not prove critical safety blocker state for this control."

        evaluations[field] = {
            "label": CONTROL_LABELS[field],
            "status": status,
            "reason": reason,
        }

    return evaluations


def _critical_blockers_known(
    *,
    source_output: Mapping[str, Any],
    blocker_summary: Mapping[str, Any],
    starting_inputs: Mapping[str, Any],
) -> bool:
    if "critical_safety_blockers_known" in starting_inputs:
        return bool(starting_inputs.get("critical_safety_blockers_known"))
    if "critical_safety_blockers" in blocker_summary:
        return True
    return "finish_line_gates" in source_output


def _controls_by_status(
    control_evaluations: Mapping[str, Mapping[str, Any]],
    status: str,
) -> list[str]:
    return [
        field
        for field in CONTROL_FIELDS
        if _mapping(control_evaluations.get(field)).get("status") == status
    ]


def _completion_percent(verified_controls: list[str]) -> float:
    if not CONTROL_FIELDS:
        return 0.0
    return round((len(verified_controls) / len(CONTROL_FIELDS)) * 100.0, 2)


def _remaining_blockers(
    control_evaluations: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    for field in CONTROL_FIELDS:
        status = _mapping(control_evaluations.get(field)).get("status", STATUS_UNKNOWN)
        if status != STATUS_VERIFIED:
            blockers.append(f"{field}:{status}")
    return blockers


def _classify_evidence_freshness(
    *,
    missing_fields: list[str],
    source_output: Mapping[str, Any],
) -> dict[str, Any]:
    source_artifacts = _mapping(source_output.get("source_artifacts"))
    if "evidence_age_days" in missing_fields:
        return {
            "status": "STALE_OR_MISSING",
            "reason": "Controller missing evidence fields include evidence_age_days.",
            "freshness_blockers": ["evidence_age_days"],
            "source_artifacts": source_artifacts,
        }
    if source_artifacts:
        return {
            "status": STATUS_PRESENT,
            "reason": "Controller emitted source artifacts and no evidence_age_days blocker.",
            "freshness_blockers": [],
            "source_artifacts": source_artifacts,
        }
    return {
        "status": STATUS_UNKNOWN,
        "reason": "Controller output did not include source artifacts.",
        "freshness_blockers": ["source_artifacts"],
        "source_artifacts": source_artifacts,
    }


def _governing_recommendation(
    *,
    blocked_controls: list[str],
    missing_controls: list[str],
    unknown_controls: list[str],
    safety_completion_percent: float,
) -> str:
    if blocked_controls:
        return "HOLD_FOR_CRITICAL_SAFETY_EVIDENCE"
    if missing_controls:
        return "COLLECT_CRITICAL_SAFETY_EVIDENCE"
    if unknown_controls:
        return "REPAIR_OR_RERUN_FINISH_LINE_CONTROLLER_OUTPUT"
    if safety_completion_percent == 100.0:
        return "CRITICAL_SAFETY_EVIDENCE_VERIFIED_KEEP_LIVE_LOCKED"
    return "KEEP_SAFETY_CLOSURE_OPEN"


def _controller_routing_recommendation(
    *,
    safety_completion_percent: float,
    blocked_controls: list[str],
    missing_controls: list[str],
    unknown_controls: list[str],
) -> str:
    if safety_completion_percent == 100.0:
        return "ROUTE_TO_OFFLINE_AUTONOMY_GOVERNOR_RERUN"
    if blocked_controls or missing_controls:
        return "REMAIN_IN_SAFETY_CLOSURE"
    if unknown_controls:
        return "RERUN_FINISH_LINE_CONTROLLER"
    return "REMAIN_IN_SAFETY_CLOSURE"


def _next_safe_action(
    *,
    source_output: Mapping[str, Any],
    blocked_controls: list[str],
    missing_controls: list[str],
    unknown_controls: list[str],
    safety_completion_percent: float,
) -> str:
    if safety_completion_percent == 100.0:
        return (
            "Critical safety evidence is verified by the controller; prepare an "
            "offline autonomy governor rerun while live execution remains locked."
        )
    if blocked_controls:
        controls = ", ".join(blocked_controls)
        return (
            f"Close controller-reported critical safety blockers for {controls}; "
            "keep broker, demo, live micro, live trading, and vacation modes locked."
        )
    if missing_controls:
        controls = ", ".join(missing_controls)
        return f"Collect missing critical safety evidence for {controls}."
    if unknown_controls:
        controls = ", ".join(unknown_controls)
        return f"Rerun or repair Finish Line controller output for {controls}."
    controller_action = _text(source_output.get("next_safe_action"))
    if controller_action:
        return controller_action
    return "Keep safety closure open and rerun the Finish Line Mission Controller."


def _closure_status(safety_completion_percent: float, remaining_blockers: list[str]) -> str:
    if safety_completion_percent == 100.0 and not remaining_blockers:
        return "SAFETY_CLOSURE_VERIFIED"
    return "SAFETY_CLOSURE_OPEN"


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _field_list(values: Any) -> list[str]:
    return [
        value
        for value in _string_list(values)
        if value in CONTROL_FIELDS or value == "evidence_age_days"
    ]


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


def _list_for_report(values: Any) -> str:
    items = _string_list(values)
    if not items:
        return "none"
    return ", ".join(items)


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _float_or_zero(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _git_value(*command: str) -> str:
    try:
        return subprocess.check_output(["git", *command], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


__all__ = [
    "CONTROL_FIELDS",
    "STATUS_PRESENT",
    "STATUS_MISSING",
    "STATUS_BLOCKED",
    "STATUS_VERIFIED",
    "STATUS_UNKNOWN",
    "DEFAULT_STATE_OUTPUT_PATH",
    "DEFAULT_REPORT_OUTPUT_PATH",
    "DEFAULT_NEXT_PACKET_OUTPUT_PATH",
    "VALIDATOR_CHAIN",
    "run_forex_critical_safety_evidence_closure_v1",
    "build_report_markdown",
    "build_next_codex_packet",
]
