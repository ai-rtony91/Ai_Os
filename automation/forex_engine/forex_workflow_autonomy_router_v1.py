"""Autonomy workflow router for Forex owner safety evidence transitions."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping


PACKET_ID = "PKT-FOREX-WORKFLOW-AUTONOMY-ROUTER-V1"
PACKET_NAME = "Build Forex Workflow Autonomy Router V1"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
MISSION_NAME = "Governed Forex Finish Line"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
PROGRAM_NAME = "Forex Profit Autonomy System"
EPIC_ID = "EPC-FOREX-WORKFLOW-AUTONOMY-ROUTER-001"
EPIC_NAME = "Forex Workflow Autonomy Router"
BKT_ID = "BKT-FOREX-WORKFLOW-AUTONOMY-ROUTER-001"
BKT_NAME = "Single Next-Safe-Action Forex Router"

WORKFLOW_BLOCKED_ON_OWNER_SAFETY_EVIDENCE = (
    "WORKFLOW_BLOCKED_ON_OWNER_SAFETY_EVIDENCE"
)
WORKFLOW_READY_FOR_NEXT_SAFE_ACTION = "WORKFLOW_READY_FOR_NEXT_SAFE_ACTION"

ACTIVE_LANE = "OWNER_SAFETY_EVIDENCE_CLOSURE"

ROUTER_VERSION = "1.0"
CONTROL_FIELDS = (
    "kill_switch_state",
    "daily_stop_state",
    "max_loss_state",
    "monitoring_ready",
)
DISCOVERY_TO_CONTROL = {
    "KILL_SWITCH_EVIDENCE_CANDIDATE": "kill_switch_state",
    "DAILY_STOP_EVIDENCE_CANDIDATE": "daily_stop_state",
    "MAX_LOSS_EVIDENCE_CANDIDATE": "max_loss_state",
    "MONITORING_READY_EVIDENCE_CANDIDATE": "monitoring_ready",
}

ROOT_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT_DIR / "Reports" / "forex_delivery"
DEFAULT_DISCOVERY_REPORT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_DISCOVERY_V1_REPORT.md"
)
DEFAULT_COLLECTION_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json"
)
DEFAULT_VERIFICATION_PREP_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_INTAKE_VERIFICATION_PREP_V1_STATE.json"
)
DEFAULT_CRITICAL_SAFETY_CLOSURE_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json"
)
DEFAULT_FINISH_LINE_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json"
)
DEFAULT_AUTONOMY_COMPLETION_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json"
)

DEFAULT_STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_REPORT.md"
)
DEFAULT_NEXT_PACKET_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_NEXT_CODEX_PACKET_V1.md"
)

SAFETY_BOUNDARY = {
    "order_execution_allowed": False,
    "broker_api_allowed": False,
    "credentials_allowed": False,
    "live_trading_authorized": False,
    "account_identifier_persistence_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
}

LOCKED_MODES = {
    "broker_probe": True,
    "demo_proof": True,
    "live_micro": True,
    "live_trading": True,
    "vacation_mode": True,
}

LOCKED_MODES_TEXT = (
    "broker_probe: locked, demo_proof: locked, live_micro: locked, "
    "live_trading: locked, vacation_mode: locked"
)

VALIDATOR_CHAIN = [
    "python -m py_compile automation/forex_engine/forex_workflow_autonomy_router_v1.py "
    "scripts/forex_delivery/run_forex_workflow_autonomy_router_v1.py",
    "python -m pytest tests/forex_engine/test_forex_workflow_autonomy_router_v1.py -q",
    (
        "python scripts/forex_delivery/run_forex_workflow_autonomy_router_v1.py "
        "--write-state --write-report --write-next-packet"
    ),
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_STATE.json",
    "python automation/validators/aios_governance_validator.py --input Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_NEXT_CODEX_PACKET_V1.md",
    "git diff --check -- automation/forex_engine/forex_workflow_autonomy_router_v1.py "
    "scripts/forex_delivery/run_forex_workflow_autonomy_router_v1.py tests/forex_engine/test_forex_workflow_autonomy_router_v1.py "
    "Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_STATE.json "
    "Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_REPORT.md "
    "Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_NEXT_CODEX_PACKET_V1.md",
    "git status --short --branch",
]


def run_forex_workflow_autonomy_router_v1(
    *,
    discovery_report_path: Path | str | None = None,
    collection_state_path: Path | str | None = None,
    verification_prep_state_path: Path | str | None = None,
    critical_safety_closure_state_path: Path | str | None = None,
    finish_line_state_path: Path | str | None = None,
    governor_state_path: Path | str | None = None,
    write_state: bool = False,
    write_state_path: Path | str | None = None,
    write_report: bool = False,
    write_report_path: Path | str | None = None,
    write_next_packet: bool = False,
    write_next_packet_path: Path | str | None = None,
) -> dict[str, Any]:
    discovery = _load_text(discovery_report_path or DEFAULT_DISCOVERY_REPORT_PATH)
    collection_state = _load_json_mapping(
        collection_state_path or DEFAULT_COLLECTION_STATE_PATH
    )
    verification_state = _load_json_mapping(
        verification_prep_state_path or DEFAULT_VERIFICATION_PREP_STATE_PATH
    )
    critical_state = _load_json_mapping(
        critical_safety_closure_state_path or DEFAULT_CRITICAL_SAFETY_CLOSURE_STATE_PATH
    )
    finish_line_state = _load_json_mapping(
        finish_line_state_path or DEFAULT_FINISH_LINE_STATE_PATH
    )
    governor_state = _load_json_mapping(governor_state_path or DEFAULT_AUTONOMY_COMPLETION_STATE_PATH)

    discovery_reasons = _parse_discovery_report(discovery)
    active_blockers = _build_active_blockers(
        collection_state=collection_state,
        verification_state=verification_state,
        critical_state=critical_state,
        finish_line_state=finish_line_state,
        governor_state=governor_state,
    )

    active_blocker = active_blockers[0] if active_blockers else ""
    if active_blockers:
        workflow_status = WORKFLOW_BLOCKED_ON_OWNER_SAFETY_EVIDENCE
        next_safe_action = (
            "Owner must provide or repair owner-sanitized evidence for "
            f"{', '.join(active_blockers)}; keep broker, demo, live micro, live trading, "
            "and vacation modes locked."
        )
    else:
        workflow_status = WORKFLOW_READY_FOR_NEXT_SAFE_ACTION
        next_safe_action = "Route to owner-safety evidence collection packet."

    active_phase = _infer_active_phase(
        finish_line_state=finish_line_state,
        critical_state=critical_state,
        collection_state=collection_state,
    )
    decision_reasons = list(
        _collect_decision_reasons(
            active_blockers=active_blockers,
            discovery_reasons=discovery_reasons,
            finish_line_state=finish_line_state,
            critical_state=critical_state,
        )
    )

    decision_reasons.extend(discovery_reasons)
    decision_reasons = _dedupe_list(decision_reasons)
    source_artifacts = _build_source_artifacts(
        discovery_report_path=Path(discovery_report_path or DEFAULT_DISCOVERY_REPORT_PATH),
        collection_state_path=Path(collection_state_path or DEFAULT_COLLECTION_STATE_PATH),
        verification_prep_state_path=Path(
            verification_prep_state_path or DEFAULT_VERIFICATION_PREP_STATE_PATH
        ),
        critical_safety_closure_state_path=Path(
            critical_safety_closure_state_path or DEFAULT_CRITICAL_SAFETY_CLOSURE_STATE_PATH
        ),
        finish_line_state_path=Path(finish_line_state_path or DEFAULT_FINISH_LINE_STATE_PATH),
        governor_state_path=Path(governor_state_path or DEFAULT_AUTONOMY_COMPLETION_STATE_PATH),
    )

    next_packet_path = Path(write_next_packet_path or DEFAULT_NEXT_PACKET_OUTPUT_PATH)
    result: dict[str, Any] = {
        "router_version": ROUTER_VERSION,
        "packet_id": PACKET_ID,
        "packet_name": PACKET_NAME,
        "mission_id": MISSION_ID,
        "mission_name": MISSION_NAME,
        "program_id": PROGRAM_ID,
        "program_name": PROGRAM_NAME,
        "epic_id": EPIC_ID,
        "epic_name": EPIC_NAME,
        "bucket_id": BKT_ID,
        "bucket_name": BKT_NAME,
        "workflow_status": workflow_status,
        "active_phase": active_phase,
        "active_blocker": active_blocker,
        "active_lane": ACTIVE_LANE,
        "active_blockers": active_blockers,
        "locked_modes": dict(LOCKED_MODES),
        "next_safe_action": next_safe_action,
        "next_packet_path": str(next_packet_path),
        "safety_boundary": dict(SAFETY_BOUNDARY),
        "source_artifacts": source_artifacts,
        "decision_reasons": decision_reasons,
        "current_branch": _git_value("branch", "--show-current"),
        "current_head": _git_value("rev-parse", "HEAD"),
        "validator_chain": list(VALIDATOR_CHAIN),
        "owner_safety_evidence_missing": _extract_missing_controls(collection_state),
        "evidence_invented": False,
        "evidence_verified_by_this_packet": False,
        "owner_intake_modified": False,
        "broker_api_used": False,
        "credentials_used": False,
        "order_execution": False,
        "live_trading_authorized": False,
    }
    result["next_packet_text"] = build_next_codex_packet(result)

    if write_state:
        state_output = Path(write_state_path or DEFAULT_STATE_OUTPUT_PATH)
        state_output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        result["state_output_path"] = str(state_output)

    if write_report:
        report_output = Path(write_report_path or DEFAULT_REPORT_OUTPUT_PATH)
        report_output.write_text(
            build_report_markdown(result),
            encoding="utf-8",
        )
        result["report_output_path"] = str(report_output)

    if write_next_packet:
        next_packet_path.write_text(result["next_packet_text"], encoding="utf-8")
        result["next_packet_output_path"] = str(next_packet_path)

    return result


def build_report_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex Workflow Autonomy Router V1 Report",
        "",
        f"Workflow status: {result.get('workflow_status')}",
        f"Current branch: {result.get('current_branch')}",
        f"Current head: {result.get('current_head')}",
        f"Active lane: {result.get('active_lane')}",
        f"Active phase: {result.get('active_phase')}",
        f"Active blocker: {result.get('active_blocker')}",
        f"Next safe action: {result.get('next_safe_action')}",
        "",
        "Locked modes:",
    ]
    for mode, locked in _mapping(result.get("locked_modes")).items():
        lines.append(f"- {mode}: {locked}")

    lines.extend(
        [
            "",
            "Safety boundary:",
        ]
    )
    for key, value in _mapping(result.get("safety_boundary")).items():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "Active blockers:",
        ]
    )
    for blocker in _string_list(result.get("active_blockers")):
        lines.append(f"- {blocker}")
    if not _string_list(result.get("active_blockers")):
        lines.append("- none")

    lines.extend(
        [
            "",
            "Decision reasons:",
        ]
    )
    for reason in _string_list(result.get("decision_reasons")):
        lines.append(f"- {reason}")
    if not _string_list(result.get("decision_reasons")):
        lines.append("- none")

    lines.extend(
        [
            "",
            "Source artifacts:",
        ]
    )
    for key, value in _mapping(result.get("source_artifacts")).items():
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
            "- No account identifiers were persisted.",
            "- No orders were placed.",
            "- No scheduler, daemon, loop, webhook, live routing, commit, push, or PR action was started.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    return (
        "CODEX-ONLY PROMPT\n\n"
        "AI_OS EXECUTION TOKEN\n"
        "AI_OS BOOTSTRAP REQUIRED\n\n"
        "CONTRACT TITLE\n"
        "AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_TO_COLLECTION_CHECKLIST_V1\n\n"
        "IDENTITY MARKER\n"
        "AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_TO_COLLECTION_CHECKLIST_V1\n\n"
        "SUPERVISOR IDENTITY\n"
        "ChatGPT planning supervisor\n\n"
        "WORKER IDENTITY\n"
        "Codex\n\n"
        "MODE\n"
        "DRY_RUN\n\n"
        "ZONE\n"
        "Trading Lab / Forex\n\n"
        "LANE\n"
        "Forex Workflow Autonomy Router\n\n"
        "WORKTREE\n"
        "C:\\Dev\\Ai.Os\n\n"
        "BRANCH\n"
        "resolve after preflight\n\n"
        "MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY\n"
        "Mission ID: MISSION-AIOS-FOREX-FINISH-LINE-V1\n"
        "Mission Name: Governed Forex Finish Line\n"
        "Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1\n"
        "Program Name: Forex Profit Autonomy System\n"
        "Epic ID: EPC-FOREX-WORKFLOW-AUTONOMY-ROUTER-001\n"
        "Epic Name: Forex Workflow Autonomy Router\n"
        "Bucket ID: BKT-FOREX-WORKFLOW-AUTONOMY-ROUTER-001\n"
        "Bucket Name: Single Next-Safe-Action Forex Router\n"
        "Packet ID: PKT-FOREX-WORKFLOW-AUTONOMY-ROUTER-V1\n"
        "Packet Name: Build Forex Workflow Autonomy Router V1\n\n"
        "APPROVAL AUTHORITY\n"
        "Anthony is the only authority for approvals, execution, and evidence changes.\n"
        "Do not modify owner safety intake template JSON.\n\n"
        "PREFLIGHT\n"
        "cd C:\\Dev\\Ai.Os\n"
        "git status --short --branch\n"
        "git branch --show-current\n"
        "git log -1 --oneline\n\n"
        "ALLOWED PATHS\n"
        "automation/forex_engine/forex_workflow_autonomy_router_v1.py\n"
        "scripts/forex_delivery/run_forex_workflow_autonomy_router_v1.py\n"
        "tests/forex_engine/test_forex_workflow_autonomy_router_v1.py\n"
        "Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_STATE.json\n"
        "Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_REPORT.md\n"
        "Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_NEXT_CODEX_PACKET_V1.md\n"
        "Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json\n"
        "Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_REPORT.md\n\n"
        "FORBIDDEN PATHS\n"
        "AGENTS.md\n"
        "README.md\n"
        "WHITEPAPER.md\n"
        "docs/architecture/AI_OS_WHITEPAPER.md\n"
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
        "MISSION\n"
        "Produce a structured owner-sanitized evidence collection checklist/report only, then pause. "
        "Do not fill owner intake template fields automatically.\n\n"
        "RULES\n"
        "Do not invent evidence.\n"
        "Do not mark evidence verified.\n"
        "Do not use broker API.\n"
        "Do not use credentials.\n"
        "Do not authorize live trading.\n"
        "Do not place trades.\n"
        "Do not read .env.\n"
        "Do not modify owner intake JSON template.\n"
        "Do not start schedulers, daemons, loops, webhooks, or background workers.\n"
        "Do not create PR.\n\n"
        "VALIDATOR CHAIN\n"
        "python scripts/forex_delivery/run_forex_owner_safety_evidence_collection_v1.py --write-state --write-report\n"
        "python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json\n"
        "git status --short --branch\n\n"
        "SAFE NEXT ACTION\n"
        "Run the owner-safety evidence collection packet to generate a checklist/report, "
        f"then keep {LOCKED_MODES_TEXT}.\n\n"
        "STOP POINT\n"
        "Stop after generating collection checklist/report. Do not mutate owner evidence template, "
        "do not verify evidence, and do not authorize any execution mode.\n\n"
        "FINAL REPORT FORMAT\n"
        "WORKFLOW_STATUS:\n"
        "ACTIVE_PHASE:\n"
        "ACTIVE_LANE:\n"
        "ACTIVE_BLOCKER:\n"
        "LOCKED_MODES:\n"
        "NEXT_SAFE_ACTION:\n"
        "ORDER_EXECUTION:\n"
        "BROKER_API_USED:\n"
        "CREDENTIALS_USED:\n"
        "LIVE_TRADING_AUTHORIZED:\n"
        "GIT_STATUS:\n"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the AIOS Forex workflow autonomy router."
    )
    parser.add_argument(
        "--discovery-report-path",
        type=Path,
        default=DEFAULT_DISCOVERY_REPORT_PATH,
    )
    parser.add_argument(
        "--collection-state-path",
        type=Path,
        default=DEFAULT_COLLECTION_STATE_PATH,
    )
    parser.add_argument(
        "--verification-prep-state-path",
        type=Path,
        default=DEFAULT_VERIFICATION_PREP_STATE_PATH,
    )
    parser.add_argument(
        "--critical-safety-closure-state-path",
        type=Path,
        default=DEFAULT_CRITICAL_SAFETY_CLOSURE_STATE_PATH,
    )
    parser.add_argument(
        "--finish-line-state-path",
        type=Path,
        default=DEFAULT_FINISH_LINE_STATE_PATH,
    )
    parser.add_argument(
        "--governor-state-path",
        type=Path,
        default=DEFAULT_AUTONOMY_COMPLETION_STATE_PATH,
    )
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-next-packet", action="store_true")
    parser.add_argument("--state-output-path", type=Path, default=DEFAULT_STATE_OUTPUT_PATH)
    parser.add_argument("--report-output-path", type=Path, default=DEFAULT_REPORT_OUTPUT_PATH)
    parser.add_argument(
        "--next-packet-output-path",
        type=Path,
        default=DEFAULT_NEXT_PACKET_OUTPUT_PATH,
    )
    return parser.parse_args(argv)


def _infer_active_phase(
    *,
    finish_line_state: Mapping[str, Any],
    critical_state: Mapping[str, Any],
    collection_state: Mapping[str, Any],
) -> str:
    explicit_phase = _text(finish_line_state.get("current_phase"))
    if explicit_phase:
        return explicit_phase
    if _extract_missing_controls(collection_state):
        return "SAFETY_EVIDENCE_CLOSURE_PENDING"
    if _string_list(critical_state.get("remaining_blockers")):
        return "CRITICAL_SAFETY_EVIDENCE_CLOSURE"
    return "OWNER_SAFETY_EVIDENCE_COLLECTION"


def _collect_decision_reasons(
    *,
    active_blockers: list[str],
    discovery_reasons: list[str],
    finish_line_state: Mapping[str, Any],
    critical_state: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if active_blockers:
        reasons.append(
            "Owner safety evidence controls are still missing or blocked: "
            + ", ".join(active_blockers)
        )
    if _text(finish_line_state.get("next_safe_action")):
        reasons.append(f"Finish-line next-safe guidance: {finish_line_state['next_safe_action']}")
    if _text(critical_state.get("next_safe_action")):
        reasons.append(f"Closure next-safe guidance: {critical_state['next_safe_action']}")
    reasons.extend(discovery_reasons)
    return reasons


def _parse_discovery_report(report_text: str) -> list[str]:
    if not report_text:
        return []
    active_section: str | None = None
    status_by_section: dict[str, str] = {}
    safe_by_section: dict[str, str] = {}
    for line in report_text.splitlines():
        if line.startswith("## "):
            active_section = line.removeprefix("## ").strip()
            continue
        if not active_section or active_section not in DISCOVERY_TO_CONTROL:
            continue
        if line.startswith("- Status: "):
            status_by_section[active_section] = line.removeprefix("- Status: ").strip()
            continue
        if line.startswith("- Safe to cite in owner intake: "):
            safe_by_section[active_section] = line.removeprefix(
                "- Safe to cite in owner intake: "
            ).strip()
    reasons: list[str] = []
    for section, control in DISCOVERY_TO_CONTROL.items():
        status = status_by_section.get(section, "")
        if not status:
            continue
        if re.search(r"weak|not|no", status, re.IGNORECASE):
            reasons.append(
                f"Discovery candidate weak for {control}: status={status}, "
                f"safe_to_cite={safe_by_section.get(section, 'unknown')}"
            )
    return reasons


def _build_active_blockers(
    *,
    collection_state: Mapping[str, Any],
    verification_state: Mapping[str, Any],
    critical_state: Mapping[str, Any],
    finish_line_state: Mapping[str, Any],
    governor_state: Mapping[str, Any],
) -> list[str]:
    blocked: list[str] = []
    blocked.extend(_extract_missing_controls(collection_state))
    blocked.extend(_extract_missing_controls(verification_state))
    blocked.extend(_string_list(_mapping(finish_line_state.get("blocker_summary")).get("critical_safety_blockers")))
    blocked.extend(_string_list(finish_line_state.get("active_blockers")))
    blocked.extend(
        _extract_blockers_from_governor(
            _string_list(governor_state.get("governor_blockers"))
        )
    )
    blocked.extend(
        _extract_blockers_from_governor(_string_list(critical_state.get("missing_controls")))
    )
    return _dedupe_ordered([control for control in blocked if control in CONTROL_FIELDS])


def _extract_missing_controls(state: Mapping[str, Any]) -> list[str]:
    for key in ("owner_evidence_missing", "missing_controls", "blocked_controls"):
        controls = _string_list(state.get(key))
        if controls:
            return [control for control in CONTROL_FIELDS if control in controls]
    return []


def _extract_blockers_from_governor(blockers: list[str]) -> list[str]:
    found: list[str] = []
    for blocker in blockers:
        lowered = blocker.lower()
        if "kill switch" in lowered:
            found.append("kill_switch_state")
        if "daily stop" in lowered:
            found.append("daily_stop_state")
        if "max loss" in lowered:
            found.append("max_loss_state")
        if "monitoring" in lowered:
            found.append("monitoring_ready")
    return found


def _build_source_artifacts(
    *,
    discovery_report_path: Path,
    collection_state_path: Path,
    verification_prep_state_path: Path,
    critical_safety_closure_state_path: Path,
    finish_line_state_path: Path,
    governor_state_path: Path,
) -> dict[str, str]:
    return {
        "owner_safety_discovery_report": _relative_path(discovery_report_path),
        "owner_safety_collection_state": _relative_path(collection_state_path),
        "owner_safety_verification_prep_state": _relative_path(verification_prep_state_path),
        "critical_safety_closure_state": _relative_path(critical_safety_closure_state_path),
        "finish_line_state": _relative_path(finish_line_state_path),
        "autonomy_completion_governor_state": _relative_path(governor_state_path),
    }


def _load_text(path: Path | str) -> str:
    candidate = Path(path)
    if not candidate.exists():
        return ""
    return candidate.read_text(encoding="utf-8")


def _load_json_mapping(path: Path | str) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.exists():
        return {}
    loaded = json.loads(candidate.read_text(encoding="utf-8"))
    if isinstance(loaded, dict):
        return dict(loaded)
    return {}


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


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip() or default


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return str(path)


def _git_value(*command: str) -> str:
    try:
        return subprocess.check_output(["git", *command], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _dedupe_list(values: Iterable[str]) -> list[str]:
    return _dedupe_ordered(values)


def _dedupe_ordered(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        if not value:
            continue
        seen.add(value)
        result.append(value)
    return result


__all__ = [
    "PACKET_ID",
    "PACKET_NAME",
    "WORKFLOW_BLOCKED_ON_OWNER_SAFETY_EVIDENCE",
    "WORKFLOW_READY_FOR_NEXT_SAFE_ACTION",
    "ACTIVE_LANE",
    "run_forex_workflow_autonomy_router_v1",
    "build_report_markdown",
    "build_next_codex_packet",
]
