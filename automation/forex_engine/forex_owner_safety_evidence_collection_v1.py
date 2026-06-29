"""Owner safety evidence collection classifier for the AIOS Forex lane.

This layer consumes the Finish Line Mission Controller and Critical Safety
Evidence Closure outputs. It classifies owner evidence requirements only; it
does not verify evidence, call brokers, read credentials, or authorize trading.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from .forex_critical_safety_evidence_closure_v1 import CONTROL_FIELDS


PACKET_ID = "PKT-FOREX-OWNER-SAFETY-EVIDENCE-COLLECTION-V1"
PACKET_NAME = "Build Owner Safety Evidence Collection V1"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
MISSION_NAME = "Governed Forex Finish Line"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
PROGRAM_NAME = "Forex Profit Autonomy System"
EPIC_ID = "EPC-FOREX-OWNER-SAFETY-EVIDENCE-COLLECTION-001"
EPIC_NAME = "Owner Safety Evidence Collection"
BUCKET_ID = "BKT-FOREX-OWNER-SAFETY-EVIDENCE-COLLECTION-001"
BUCKET_NAME = "Owner Critical Safety Evidence Collection"

STATUS_OWNER_EVIDENCE_REQUIRED = "OWNER_EVIDENCE_REQUIRED"
STATUS_OWNER_EVIDENCE_COMPLETE_PENDING_VERIFICATION = (
    "OWNER_EVIDENCE_COMPLETE_PENDING_VERIFICATION"
)
STATUS_OWNER_EVIDENCE_PARTIAL = "OWNER_EVIDENCE_PARTIAL"
STATUS_UNKNOWN = "UNKNOWN"

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "Reports" / "forex_delivery"
DEFAULT_CONTROLLER_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json"
)
DEFAULT_CLOSURE_STATE_PATH = (
    REPORTS_DIR / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json"
)
DEFAULT_STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_REPORT.md"
)
DEFAULT_NEXT_PACKET_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_NEXT_CODEX_PACKET_V1.md"
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

VALIDATOR_CHAIN = (
    "python -m py_compile automation/forex_engine/forex_owner_safety_evidence_collection_v1.py scripts/forex_delivery/run_forex_owner_safety_evidence_collection_v1.py tests/forex_engine/test_forex_owner_safety_evidence_collection_v1.py",
    "python -m pytest tests/forex_engine/test_forex_owner_safety_evidence_collection_v1.py -q",
    "python scripts/forex_delivery/run_forex_owner_safety_evidence_collection_v1.py --write-state --write-report",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json",
    "git diff --check -- automation/forex_engine/forex_owner_safety_evidence_collection_v1.py scripts/forex_delivery/run_forex_owner_safety_evidence_collection_v1.py tests/forex_engine/test_forex_owner_safety_evidence_collection_v1.py Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_REPORT.md Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_NEXT_CODEX_PACKET_V1.md",
    "git status --short --branch",
)

REQUIRED_EVIDENCE_BY_CONTROL = {
    "kill_switch_state": [
        "Owner-provided current kill-switch state showing the emergency stop control exists, is reachable, and is in the expected safe state.",
        "Evidence that the kill switch can block progression before broker, demo, live micro, or live trading modes are considered.",
    ],
    "daily_stop_state": [
        "Owner-provided current daily-stop state showing the daily loss or halt rule is configured and not unknown.",
        "Evidence that daily-stop enforcement would block progression after the configured daily limit is reached.",
    ],
    "max_loss_state": [
        "Owner-provided current max-loss state showing the max-loss threshold is configured, bounded, and not unknown.",
        "Evidence that max-loss enforcement would block progression before unacceptable drawdown or loss exposure.",
    ],
    "monitoring_ready": [
        "Owner-provided current monitoring readiness evidence showing an operator-visible monitoring path exists.",
        "Evidence that alerts, logs, or owner review surfaces can detect safety-control failure before progression.",
    ],
}

ACCEPTABLE_EVIDENCE_TYPES_BY_CONTROL = {
    "kill_switch_state": [
        "sanitized safety-control status export",
        "sanitized screenshot of the kill-switch state",
        "approved local preflight output with no secrets or account identifiers",
        "owner checklist entry tied to a timestamped evidence artifact",
    ],
    "daily_stop_state": [
        "sanitized daily-stop configuration export",
        "sanitized daily risk-state report",
        "approved local preflight output with no secrets or account identifiers",
        "owner checklist entry tied to a timestamped evidence artifact",
    ],
    "max_loss_state": [
        "sanitized max-loss configuration export",
        "sanitized risk-threshold report",
        "approved local preflight output with no secrets or account identifiers",
        "owner checklist entry tied to a timestamped evidence artifact",
    ],
    "monitoring_ready": [
        "sanitized monitoring readiness report",
        "sanitized alert or review-surface proof",
        "approved local preflight output with no secrets or account identifiers",
        "owner checklist entry tied to a timestamped evidence artifact",
    ],
}

EVIDENCE_FRESHNESS_REQUIREMENT = {
    "kill_switch_state": "Current owner review session or within 24 hours of progression request; refresh after safety-control changes.",
    "daily_stop_state": "Current owner review session or within 24 hours of progression request; refresh after risk-rule changes.",
    "max_loss_state": "Current owner review session or within 24 hours of progression request; refresh after risk-threshold changes.",
    "monitoring_ready": "Current owner review session or within 24 hours of progression request; refresh after monitoring, alerting, or dashboard changes.",
}

VERIFICATION_REQUIRED_BY_CONTROL = {
    control: True for control in CONTROL_FIELDS
}


def run_forex_owner_safety_evidence_collection_v1(
    *,
    controller_state: Mapping[str, Any] | None = None,
    closure_state: Mapping[str, Any] | None = None,
    write_state: bool = False,
    write_state_path: Path | str | None = None,
    write_report: bool = False,
    write_report_path: Path | str | None = None,
    write_next_packet_path: Path | str | None = None,
) -> dict[str, Any]:
    """Classify required owner safety evidence without verifying it."""

    source_controller_state = (
        dict(controller_state)
        if controller_state is not None
        else _load_json_mapping(DEFAULT_CONTROLLER_STATE_PATH)
    )
    source_closure_state = (
        dict(closure_state)
        if closure_state is not None
        else _load_json_mapping(DEFAULT_CLOSURE_STATE_PATH)
    )

    complete_controls = _closure_proven_controls(source_closure_state)
    owner_evidence_required = list(CONTROL_FIELDS)
    owner_evidence_complete = [
        control for control in CONTROL_FIELDS if control in complete_controls
    ]
    owner_evidence_missing = [
        control for control in CONTROL_FIELDS if control not in complete_controls
    ]
    completion_percent = _completion_percent(owner_evidence_complete)
    required_evidence_by_control = {
        control: list(REQUIRED_EVIDENCE_BY_CONTROL[control])
        for control in CONTROL_FIELDS
    }
    acceptable_evidence_types_by_control = {
        control: list(ACCEPTABLE_EVIDENCE_TYPES_BY_CONTROL[control])
        for control in CONTROL_FIELDS
    }
    evidence_freshness_requirement = {
        control: EVIDENCE_FRESHNESS_REQUIREMENT[control]
        for control in CONTROL_FIELDS
    }

    required_evidence_detail = _build_required_evidence_detail(
        closure_state=source_closure_state,
        owner_evidence_complete=owner_evidence_complete,
        required_evidence_by_control=required_evidence_by_control,
        acceptable_evidence_types_by_control=acceptable_evidence_types_by_control,
        evidence_freshness_requirement=evidence_freshness_requirement,
    )
    collection_status = _collection_status(
        owner_evidence_complete=owner_evidence_complete,
        owner_evidence_missing=owner_evidence_missing,
    )
    next_safe_action = _next_safe_action(
        owner_evidence_missing=owner_evidence_missing,
        collection_status=collection_status,
    )

    result: dict[str, Any] = {
        "owner_evidence_collection_status": collection_status,
        "owner_evidence_required": owner_evidence_required,
        "owner_evidence_complete": owner_evidence_complete,
        "owner_evidence_missing": owner_evidence_missing,
        "owner_evidence_completion_percent": completion_percent,
        "required_evidence_by_control": required_evidence_by_control,
        "acceptable_evidence_types_by_control": acceptable_evidence_types_by_control,
        "verification_required_by_control": dict(VERIFICATION_REQUIRED_BY_CONTROL),
        "evidence_freshness_requirement": evidence_freshness_requirement,
        "required_evidence_by_control_detail": required_evidence_detail,
        "controller_status": _controller_status(
            source_controller_state=source_controller_state,
            source_closure_state=source_closure_state,
        ),
        "controller_phase": _controller_phase(
            source_controller_state=source_controller_state,
            source_closure_state=source_closure_state,
        ),
        "critical_safety_closure_status": _text(
            source_closure_state.get("closure_status"),
            STATUS_UNKNOWN,
        ),
        "next_safe_action": next_safe_action,
        "safety_boundary": dict(SAFETY_BOUNDARY),
        "source_controller": _mapping(source_closure_state.get("source_controller")),
        "source_artifacts": {
            "finish_line_controller_state": _relative_path(
                DEFAULT_CONTROLLER_STATE_PATH
            ),
            "critical_safety_closure_state": _relative_path(
                DEFAULT_CLOSURE_STATE_PATH
            ),
        },
        "evidence_verified_by_this_packet": False,
        "evidence_verification_required_later": True,
        "evidence_invented": False,
        "order_execution": False,
        "broker_api_used": False,
        "credentials_used": False,
        "live_trading_authorized": False,
        "validator_chain": list(VALIDATOR_CHAIN),
        "packet_id": PACKET_ID,
        "packet_name": PACKET_NAME,
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
        "# AIOS Forex Owner Safety Evidence Collection V1 Report",
        "",
        f"Status: {result.get('owner_evidence_collection_status')}",
        f"Current branch: {_git_value('branch', '--show-current')}",
        f"Current head: {_git_value('rev-parse', 'HEAD')}",
        f"Controller status: {result.get('controller_status')}",
        f"Controller phase: {result.get('controller_phase')}",
        f"Critical safety closure status: {result.get('critical_safety_closure_status')}",
        f"Owner evidence completion percent: {result.get('owner_evidence_completion_percent')}%",
        f"Evidence verified by this packet: {result.get('evidence_verified_by_this_packet')}",
        "",
        "Owner evidence required:",
    ]
    for control in _string_list(result.get("owner_evidence_required")):
        lines.append(f"- {control}")

    lines.extend(["", "Owner evidence complete:"])
    for control in _string_list(result.get("owner_evidence_complete")):
        lines.append(f"- {control}")
    if not _string_list(result.get("owner_evidence_complete")):
        lines.append("- none")

    lines.extend(["", "Owner evidence missing:"])
    for control in _string_list(result.get("owner_evidence_missing")):
        lines.append(f"- {control}")
    if not _string_list(result.get("owner_evidence_missing")):
        lines.append("- none")

    lines.extend(["", "Required evidence by control:"])
    detail = _mapping(result.get("required_evidence_by_control_detail"))
    for control in CONTROL_FIELDS:
        control_detail = _mapping(detail.get(control))
        lines.append(f"- {control}:")
        lines.append(f"  - current_status: {control_detail.get('current_status')}")
        lines.append(f"  - missing_status: {control_detail.get('missing_status')}")
        lines.append(
            f"  - verification_required: {control_detail.get('verification_required')}"
        )
        lines.append(
            f"  - governing_recommendation: {control_detail.get('governing_recommendation')}"
        )

    lines.extend(
        [
            "",
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
            "- No account identifiers were persisted.",
            "- No orders were placed.",
            "- No scheduler, daemon, loop, webhook, live routing, commit, push, or PR action was started.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_next_codex_packet(result: Mapping[str, Any]) -> str:
    missing = _string_list(result.get("owner_evidence_missing"))
    missing_text = ", ".join(missing) if missing else "none"
    return (
        "CODEX-ONLY PROMPT\n\n"
        "AI_OS EXECUTION TOKEN\n"
        "AI_OS BOOTSTRAP REQUIRED\n\n"
        "CONTRACT TITLE\n"
        "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_RETURN_READINESS_REVIEW_V1\n\n"
        "IDENTITY MARKER\n"
        "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_RETURN_READINESS_REVIEW_V1\n\n"
        "SUPERVISOR IDENTITY\n"
        "ChatGPT planning supervisor\n\n"
        "WORKER IDENTITY\n"
        "Codex\n\n"
        "MODE\n"
        "DRY_RUN\n\n"
        "ZONE\n"
        "Trading Lab / Forex\n\n"
        "LANE\n"
        "Forex Owner Safety Evidence Return Readiness Review\n\n"
        "WORKTREE\n"
        "C:\\Dev\\Ai.Os\n\n"
        "BRANCH\n"
        "resolve after preflight\n\n"
        "MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY\n"
        "Mission ID: MISSION-AIOS-FOREX-FINISH-LINE-V1\n"
        "Mission Name: Governed Forex Finish Line\n"
        "Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1\n"
        "Program Name: Forex Profit Autonomy System\n"
        "Epic ID: EPC-FOREX-OWNER-SAFETY-EVIDENCE-COLLECTION-001\n"
        "Epic Name: Owner Safety Evidence Collection\n"
        "Bucket ID: BKT-FOREX-OWNER-SAFETY-EVIDENCE-COLLECTION-001\n"
        "Bucket Name: Owner Critical Safety Evidence Collection\n"
        "Packet ID: PKT-FOREX-OWNER-SAFETY-EVIDENCE-RETURN-READINESS-REVIEW-V1\n"
        "Packet Name: Owner Safety Evidence Return Readiness Review V1\n\n"
        "APPROVAL AUTHORITY\n"
        "Human Owner approval is required before APPLY execution, PR creation, broker/API use, credential use, live trading authorization, scheduler activation, daemon activation, webhook activation, dashboard mutation, or order execution.\n"
        "A later Human Owner message that explicitly approves commit is required before commit.\n"
        "A later Human Owner message that explicitly approves push is required before push.\n\n"
        "MISSION\n"
        "Read the owner safety evidence collection state and report whether owner-returned evidence can be prepared for a later verification packet. Do not inspect private evidence, do not verify evidence, and do not mutate files.\n\n"
        "PREFLIGHT\n"
        "cd C:\\Dev\\Ai.Os\n"
        "git status --short --branch\n"
        "git branch --show-current\n"
        "git log -1 --oneline\n\n"
        "ALLOWED PATHS\n"
        "Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json\n"
        "Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_REPORT.md\n\n"
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
        "CURRENT OWNER EVIDENCE MISSING\n"
        f"{missing_text}\n\n"
        "RULES\n"
        "Do not invent evidence.\n"
        "Do not verify evidence.\n"
        "Do not place trades.\n"
        "Do not use broker API.\n"
        "Do not use credentials.\n"
        "Do not read .env.\n"
        "Do not authorize live trading.\n"
        "Do not start schedulers, daemons, loops, webhooks, or background workers.\n"
        "Do not commit.\n"
        "Do not push.\n"
        "Do not create PR.\n\n"
        "VALIDATOR CHAIN\n"
        "python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json\n"
        "git status --short --branch\n\n"
        "SAFE NEXT ACTION\n"
        "Prepare a later owner evidence verification packet only after sanitized owner evidence is available; keep broker, demo, live micro, live trading, and vacation modes locked.\n\n"
        "STOP POINT\n"
        "Stop after read-only readiness report. Do not commit. Do not push. Do not create PR.\n\n"
        "FINAL REPORT FORMAT\n"
        "STATUS:\n"
        "CURRENT_BRANCH:\n"
        "CURRENT_HEAD:\n"
        "OWNER_EVIDENCE_MISSING:\n"
        "EVIDENCE_VERIFIED_BY_THIS_PACKET:\n"
        "NEXT_SAFE_ACTION:\n"
        "ORDER_EXECUTION:\n"
        "BROKER_API_USED:\n"
        "CREDENTIALS_USED:\n"
        "GIT_STATUS:\n"
    )


def _build_required_evidence_detail(
    *,
    closure_state: Mapping[str, Any],
    owner_evidence_complete: list[str],
    required_evidence_by_control: Mapping[str, list[str]],
    acceptable_evidence_types_by_control: Mapping[str, list[str]],
    evidence_freshness_requirement: Mapping[str, str],
) -> dict[str, dict[str, Any]]:
    closure_evaluations = _mapping(closure_state.get("control_evaluations"))
    complete_set = set(owner_evidence_complete)
    detail: dict[str, dict[str, Any]] = {}
    for control in CONTROL_FIELDS:
        control_status = _text(
            _mapping(closure_evaluations.get(control)).get("status"),
            _fallback_status(closure_state, control),
        )
        complete = control in complete_set
        detail[control] = {
            "required_owner_evidence": list(required_evidence_by_control[control]),
            "acceptable_evidence_types": list(
                acceptable_evidence_types_by_control[control]
            ),
            "evidence_freshness_requirement": evidence_freshness_requirement[control],
            "verification_required": True,
            "current_status": control_status,
            "missing_status": (
                "OWNER_EVIDENCE_NOT_MISSING_CLOSURE_STATE_ALREADY_PROVES_CONTROL"
                if complete
                else "OWNER_EVIDENCE_MISSING"
            ),
            "governing_recommendation": _control_recommendation(
                control_status=control_status,
                complete=complete,
            ),
        }
    return detail


def _closure_proven_controls(closure_state: Mapping[str, Any]) -> set[str]:
    proven = {
        control
        for control in _string_list(closure_state.get("verified_controls"))
        if control in CONTROL_FIELDS
    }
    evaluations = _mapping(closure_state.get("control_evaluations"))
    for control in CONTROL_FIELDS:
        if _text(_mapping(evaluations.get(control)).get("status")).upper() == "VERIFIED":
            proven.add(control)
    if _text(closure_state.get("closure_status")).upper() == "SAFETY_CLOSURE_VERIFIED":
        if len(proven) == len(CONTROL_FIELDS):
            return proven
    return proven


def _fallback_status(closure_state: Mapping[str, Any], control: str) -> str:
    if control in _string_list(closure_state.get("blocked_controls")):
        return "BLOCKED"
    if control in _string_list(closure_state.get("missing_controls")):
        return "MISSING"
    if control in _string_list(closure_state.get("unknown_controls")):
        return "UNKNOWN"
    if control in _string_list(closure_state.get("present_controls")):
        return "PRESENT"
    if control in _string_list(closure_state.get("verified_controls")):
        return "VERIFIED"
    return STATUS_UNKNOWN


def _control_recommendation(*, control_status: str, complete: bool) -> str:
    if complete:
        return "OWNER_EVIDENCE_COMPLETE_FROM_CLOSURE_STATE_KEEP_LIVE_LOCKED"
    status = control_status.upper()
    if status == "BLOCKED":
        return "OWNER_MUST_PROVIDE_EVIDENCE_FOR_BLOCKED_CONTROL"
    if status == "MISSING":
        return "OWNER_MUST_PROVIDE_MISSING_CONTROL_EVIDENCE"
    if status == "PRESENT":
        return "CLOSURE_STATE_MUST_PROVE_CONTROL_BEFORE_PROGRESSION"
    return "REPAIR_OR_RERUN_CLOSURE_STATE_BEFORE_PROGRESSION"


def _collection_status(
    *,
    owner_evidence_complete: list[str],
    owner_evidence_missing: list[str],
) -> str:
    if not owner_evidence_complete:
        return STATUS_OWNER_EVIDENCE_REQUIRED
    if owner_evidence_missing:
        return STATUS_OWNER_EVIDENCE_PARTIAL
    return STATUS_OWNER_EVIDENCE_COMPLETE_PENDING_VERIFICATION


def _next_safe_action(
    *,
    owner_evidence_missing: list[str],
    collection_status: str,
) -> str:
    if owner_evidence_missing:
        controls = ", ".join(owner_evidence_missing)
        return (
            "Owner must provide current sanitized safety evidence for "
            f"{controls}; keep broker, demo, live micro, live trading, and vacation modes locked."
        )
    if collection_status == STATUS_OWNER_EVIDENCE_COMPLETE_PENDING_VERIFICATION:
        return (
            "Owner evidence is complete according to the closure state; route to a "
            "separate verification packet while live execution remains locked."
        )
    return "Keep owner safety evidence collection open and live execution locked."


def _controller_status(
    *,
    source_controller_state: Mapping[str, Any],
    source_closure_state: Mapping[str, Any],
) -> str:
    return _text(
        source_closure_state.get("controller_status"),
        _text(source_controller_state.get("controller_status"), STATUS_UNKNOWN),
    )


def _controller_phase(
    *,
    source_controller_state: Mapping[str, Any],
    source_closure_state: Mapping[str, Any],
) -> str:
    return _text(
        source_closure_state.get("controller_phase"),
        _text(source_controller_state.get("current_phase"), STATUS_UNKNOWN),
    )


def _completion_percent(owner_evidence_complete: list[str]) -> float:
    if not CONTROL_FIELDS:
        return 0.0
    return round((len(owner_evidence_complete) / len(CONTROL_FIELDS)) * 100.0, 2)


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


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


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
    "CONTROL_FIELDS",
    "DEFAULT_STATE_OUTPUT_PATH",
    "DEFAULT_REPORT_OUTPUT_PATH",
    "DEFAULT_NEXT_PACKET_OUTPUT_PATH",
    "SAFETY_BOUNDARY",
    "VALIDATOR_CHAIN",
    "run_forex_owner_safety_evidence_collection_v1",
    "build_report_markdown",
    "build_next_codex_packet",
]
