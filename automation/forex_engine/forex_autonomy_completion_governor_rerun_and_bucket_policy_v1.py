"""Autonomy completion governor rerun + bucket policy controller for Forex lane."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from . import supervised_autonomy_governor_v1 as governor


PACKET_ID = "PKT-FOREX-AUTONOMY-COMPLETION-GOVERNOR-RERUN-AND-BUCKET-POLICY-V1"
MISSION_ID = "MISSION-AIOS-FOREX-AUTONOMY-COMPLETION-V1"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
EPIC_ID = "EPC-FOREX-AUTONOMY-COMPLETION-001"
BUCKET_ID = "BKT-FOREX-GOVERNOR-RERUN-001"

REQUIRE_MORE_EVIDENCE = governor.REQUIRE_MORE_EVIDENCE
DEMO_SUPERVISED_READY = governor.DEMO_SUPERVISED_READY
LIVE_MICRO_EXCEPTION_REVIEW_READY = governor.LIVE_MICRO_EXCEPTION_REVIEW_READY
AUTONOMY_BLOCKED = governor.AUTONOMY_BLOCKED
LIVE_BLOCKED_BY_POLICY = governor.LIVE_BLOCKED_BY_POLICY

BUCKET_READY = "BUCKET_READY"
BUCKET_TARGET_HOLD = "BUCKET_TARGET_HOLD"
BUCKET_MAX_LOSS_HOLD = "BUCKET_MAX_LOSS_HOLD"
BUCKET_POLICY_BLOCKED = "BUCKET_POLICY_BLOCKED"
BUCKET_REVIEW_REQUIRED = "BUCKET_REVIEW_REQUIRED"

COLLECT_MORE_EVIDENCE = "COLLECT_MORE_EVIDENCE"
RUN_DEMO_SUPERVISED_CYCLE = "RUN_DEMO_SUPERVISED_CYCLE"
ROUTE_OWNER_LIVE_MICRO_REVIEW = "ROUTE_OWNER_LIVE_MICRO_REVIEW"
HOLD_FOR_RISK_RESET = "HOLD_FOR_RISK_RESET"
HOLD_FOR_OWNER_GATE = "HOLD_FOR_OWNER_GATE"
HOLD_FOR_POLICY_REVIEW = "HOLD_FOR_POLICY_REVIEW"

AUTONOMY_CRITICAL_GATES = frozenset(
    {
        governor.GATE_KILL_SWITCH,
        governor.GATE_DAILY_STOP,
        governor.GATE_MAX_LOSS,
        governor.GATE_MONITORING,
    }
)
AUTONOMY_POLICY_GATES = frozenset(
    {
        governor.GATE_LIVE_BRIDGE,
        governor.GATE_TP_SL,
    }
)

DEFAULT_STATE_JSON_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_STATE_MODEL_V1.json"
)
DEFAULT_GOVERNOR_INPUT_JSON_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json"
)
DEFAULT_STATE_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json"
)
DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_REPORT.md"
)

VALIDATOR_CHAIN = (
    "python -m py_compile automation/forex_engine/forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
    "python -m py_compile scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
    "python -m pytest tests/forex_engine/test_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py -q",
    "python scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json",
    "git diff --check -- automation/forex_engine/forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py tests/forex_engine/test_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_REPORT.md Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_NEXT_CODEX_PACKET_V1.md",
)

NEXT_SAFE_ACTION_BY_STATE = {
    COLLECT_MORE_EVIDENCE: "Collect additional sanitized evidence and rerun the controller.",
    RUN_DEMO_SUPERVISED_CYCLE: "Run the demo-supervised packet and hold all execution controls false.",
    ROUTE_OWNER_LIVE_MICRO_REVIEW: (
        "Route to owner live micro-review while preserving full safety boundaries."
    ),
    HOLD_FOR_RISK_RESET: "Hold until risk reset evidence (max-loss / daily-stop / kill-switch) clears.",
    HOLD_FOR_OWNER_GATE: "Hold until owner gate status is explicit and not denied.",
    HOLD_FOR_POLICY_REVIEW: "Hold for policy review before further autonomy advance.",
}


def run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
    *,
    state_json: Path | str | None = None,
    governor_input_json: Path | str | None = None,
    state_mapping: Mapping[str, Any] | None = None,
    governor_input_mapping: Mapping[str, Any] | None = None,
    write_state: bool = False,
    write_state_path: Path | str | None = None,
    write_report: bool = False,
    write_report_path: Path | str | None = None,
) -> dict[str, Any]:
    state = _load_json_mapping(
        state_mapping,
        Path(state_json) if state_json is not None else DEFAULT_STATE_JSON_PATH,
    )
    governor_input = _load_json_mapping(
        governor_input_mapping,
        Path(governor_input_json)
        if governor_input_json is not None
        else DEFAULT_GOVERNOR_INPUT_JSON_PATH,
    )

    governor_result = governor.evaluate_supervised_autonomy_candidate(governor_input)
    candidate_status = _normalize_candidate_status(
        _text(governor_result.get("candidate_status"), default=AUTONOMY_BLOCKED),
        governor_input,
        governor_result,
    )
    bucket_status = _classify_bucket_status(
        state, governor_input, candidate_status, governor_result
    )
    owner_gate_status = _classify_owner_gate_status(governor_input)
    next_autonomy_action = _classify_next_autonomy_action(
        candidate_status, owner_gate_status, governor_result
    )

    governor_blockers = _string_list(governor_result.get("blockers", []))
    bucket_blockers = _classify_bucket_blockers(
        state, governor_input, candidate_status, governor_result, bucket_status
    )
    broker_gate_status = _classify_broker_gate_status(governor_input, governor_result)

    result = {
        "candidate_status": candidate_status,
        "bucket_status": bucket_status,
        "next_autonomy_action": next_autonomy_action,
        "governor_blockers": governor_blockers,
        "bucket_blockers": bucket_blockers,
        "owner_gate_status": owner_gate_status,
        "broker_gate_status": broker_gate_status,
        "live_micro_exception_status": _classify_live_micro_exception_status(
            candidate_status
        ),
        "daily_return_target_percent": _to_float(
            state.get("daily_return_target_percent"), default=100.0
        ),
        "daily_stretch_target_percent": _to_float(
            state.get("daily_stretch_target_percent"), default=120.0
        ),
        "capital_bucket_mode": _text(
            state.get("capital_bucket_mode", "FIXED_DAILY_BUCKET"),
            default="FIXED_DAILY_BUCKET",
        ),
        "next_safe_action": _text(NEXT_SAFE_ACTION_BY_STATE.get(next_autonomy_action)),
        "safety_boundary": {
            "order_execution_allowed": False,
            "broker_api_allowed": False,
            "credentials_allowed": False,
            "account_identifier_persistence_allowed": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
        },
        "validator_chain": list(VALIDATOR_CHAIN),
        "packet_id": PACKET_ID,
        "mission_id": MISSION_ID,
        "program_id": PROGRAM_ID,
        "epic_id": EPIC_ID,
        "bucket_id": BUCKET_ID,
    }

    if write_state:
        state_output = (
            Path(write_state_path)
            if write_state_path is not None
            else DEFAULT_STATE_OUTPUT_PATH
        )
        state_output.write_text(
            json.dumps(result, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        result["state_output_path"] = str(state_output)

    if write_report:
        report_output = (
            Path(write_report_path)
            if write_report_path is not None
            else DEFAULT_REPORT_PATH
        )
        report_output.write_text(
            _build_report_markdown(
                result=result,
                state_json_path=(
                    Path(state_json)
                    if state_json is not None
                    else DEFAULT_STATE_JSON_PATH
                ),
                governor_input_json_path=(
                    Path(governor_input_json)
                    if governor_input_json is not None
                    else DEFAULT_GOVERNOR_INPUT_JSON_PATH
                ),
            ),
            encoding="utf-8",
        )
        result["report_output_path"] = str(report_output)

    return result


def _classify_next_autonomy_action(
    candidate_status: str,
    owner_gate_status: str,
    governor_result: Mapping[str, Any],
) -> str:
    failed_gates = _to_lower_set(governor_result.get("failed_gates", []))
    candidate_status = _text(candidate_status, default=AUTONOMY_BLOCKED)
    owner_status = _text(owner_gate_status).upper()
    risk_hold = bool(failed_gates.intersection(AUTONOMY_CRITICAL_GATES))
    owner_gate_blocked = (
        governor.GATE_OWNER_APPROVAL in failed_gates
        and owner_status in {"OWNER_GATE_DENIED", "OWNER_GATE_PENDING", "PENDING"}
    )
    policy_hold = bool(failed_gates.intersection(AUTONOMY_POLICY_GATES))

    if candidate_status == REQUIRE_MORE_EVIDENCE:
        if risk_hold:
            return HOLD_FOR_RISK_RESET
        if owner_gate_blocked:
            return HOLD_FOR_OWNER_GATE
        if policy_hold:
            return HOLD_FOR_POLICY_REVIEW
        return COLLECT_MORE_EVIDENCE
    if candidate_status == DEMO_SUPERVISED_READY:
        if risk_hold:
            return HOLD_FOR_RISK_RESET
        if owner_gate_blocked:
            return HOLD_FOR_OWNER_GATE
        if policy_hold:
            return HOLD_FOR_POLICY_REVIEW
        return RUN_DEMO_SUPERVISED_CYCLE
    if candidate_status == LIVE_MICRO_EXCEPTION_REVIEW_READY:
        return ROUTE_OWNER_LIVE_MICRO_REVIEW
    if candidate_status == AUTONOMY_BLOCKED:
        if risk_hold:
            return HOLD_FOR_RISK_RESET
        if owner_gate_blocked:
            return HOLD_FOR_OWNER_GATE
        return HOLD_FOR_POLICY_REVIEW
    if candidate_status == LIVE_BLOCKED_BY_POLICY:
        if owner_status in {"OWNER_GATE_DENIED", "OWNER_DENIED"}:
            return HOLD_FOR_OWNER_GATE
        if policy_hold or owner_gate_blocked:
            return HOLD_FOR_POLICY_REVIEW
        return HOLD_FOR_POLICY_REVIEW
    if bool(governor_result.get("live_trading_allowed")):
        return ROUTE_OWNER_LIVE_MICRO_REVIEW
    return HOLD_FOR_POLICY_REVIEW


def _classify_owner_gate_status(governor_input: Mapping[str, Any]) -> str:
    approval = _text(governor_input.get("owner_approval_status")).upper()
    live_review_approved = bool(
        governor_input.get("owner_live_micro_exception_approved")
    )
    live_review_evidence = bool(governor_input.get("live_bridge_external_evidence"))

    if approval in {"DENIED", "REJECTED"}:
        return "OWNER_GATE_DENIED"
    if approval == "APPROVED_FOR_LIVE_MICRO" and live_review_approved and live_review_evidence:
        return "OWNER_LIVE_GATE_APPROVED"
    if approval in {"APPROVED", "APPROVED_FOR_DEMO"}:
        return "OWNER_GATE_APPROVED"
    if approval == "APPROVED_FOR_LIVE_MICRO":
        return "OWNER_LIVE_GATE_APPROVED"
    return "OWNER_GATE_PENDING"


def _normalize_candidate_status(
    candidate_status: str,
    governor_input: Mapping[str, Any],
    governor_result: Mapping[str, Any],
) -> str:
    failed_gates = _to_lower_set(governor_result.get("failed_gates", []))
    owner_status = _text(governor_input.get("owner_approval_status")).upper()
    critical_gate_failures = bool(
        failed_gates.intersection(AUTONOMY_CRITICAL_GATES | AUTONOMY_POLICY_GATES)
    )

    if owner_status in {"DENIED", "REJECTED"}:
        return AUTONOMY_BLOCKED
    if critical_gate_failures:
        return AUTONOMY_BLOCKED
    if owner_status in {"", "PENDING"}:
        return REQUIRE_MORE_EVIDENCE

    return candidate_status


def _classify_broker_gate_status(
    governor_input: Mapping[str, Any],
    governor_result: Mapping[str, Any],
) -> str:
    if not _as_bool(governor_input.get("broker_readiness")):
        return "BROKER_GATE_NOT_READY"
    if not _as_bool(governor_input.get("live_bridge_eligibility")):
        return "LIVE_BRIDGE_NOT_READY"
    if _text(governor_result.get("candidate_status")) == LIVE_BLOCKED_BY_POLICY:
        return "BROKER_GATE_BLOCKED"
    return "BROKER_GATE_READY"


def _classify_live_micro_exception_status(candidate_status: str) -> str:
    if candidate_status == LIVE_MICRO_EXCEPTION_REVIEW_READY:
        return "LIVE_MICRO_REVIEW_READY"
    if candidate_status == LIVE_BLOCKED_BY_POLICY:
        return "LIVE_MICRO_REVIEW_BLOCKED"
    if candidate_status == AUTONOMY_BLOCKED:
        return "LIVE_MICRO_REVIEW_BLOCKED"
    return "LIVE_MICRO_REVIEW_NOT_READY"


def _classify_bucket_status(
    state: Mapping[str, Any],
    governor_input: Mapping[str, Any],
    candidate_status: str,
    governor_result: Mapping[str, Any],
) -> str:
    failed_gates = _to_lower_set(governor_result.get("failed_gates", []))
    realized_return = _to_float(state.get("daily_return_percent"), default=None)
    daily_return_target = _to_float(state.get("daily_return_target_percent"), default=100.0)
    daily_stretch_target = _to_float(
        state.get("daily_stretch_target_percent"), default=120.0
    )

    if candidate_status == LIVE_MICRO_EXCEPTION_REVIEW_READY:
        return BUCKET_REVIEW_REQUIRED

    max_loss_state = _text(governor_input.get("max_loss_state")).upper()
    max_loss_hold = max_loss_state in {"", "UNSET", "DISABLED", "DISARMED"}
    if failed_gates.intersection(AUTONOMY_CRITICAL_GATES):
        return BUCKET_MAX_LOSS_HOLD
    if governor.GATE_MAX_LOSS in failed_gates or max_loss_hold:
        return BUCKET_MAX_LOSS_HOLD

    if realized_return is not None and realized_return >= daily_stretch_target:
        return BUCKET_TARGET_HOLD
    if realized_return is not None and realized_return >= daily_return_target:
        return BUCKET_TARGET_HOLD

    if candidate_status == LIVE_BLOCKED_BY_POLICY:
        return BUCKET_POLICY_BLOCKED
    if failed_gates.intersection(AUTONOMY_POLICY_GATES | {governor.GATE_OWNER_APPROVAL}):
        return BUCKET_POLICY_BLOCKED

    return BUCKET_READY


def _classify_bucket_blockers(
    state: Mapping[str, Any],
    governor_input: Mapping[str, Any],
    candidate_status: str,
    governor_result: Mapping[str, Any],
    bucket_status: str,
) -> list[str]:
    del governor_input
    del candidate_status
    del governor_result

    blockers: list[str] = _string_list(state.get("blockers", []))

    realized_return = _to_float(state.get("daily_return_percent"), default=None)
    target = _to_float(state.get("daily_return_target_percent"), default=100.0)
    stretch = _to_float(state.get("daily_stretch_target_percent"), default=120.0)

    if bucket_status == BUCKET_TARGET_HOLD:
        if realized_return is not None and realized_return >= stretch:
            blockers.append("daily_stretch_target_reached")
        elif realized_return is not None and realized_return >= target:
            blockers.append("daily_return_target_reached")
        else:
            blockers.append("target_bucket_not_reached")
    if bucket_status == BUCKET_MAX_LOSS_HOLD:
        blockers.append("max_loss_state_hold")
    if bucket_status == BUCKET_POLICY_BLOCKED:
        blockers.append("bucket_policy_blocked")
    if bucket_status == BUCKET_REVIEW_REQUIRED:
        blockers.append("live_micro_exception_review_required")

    return list(dict.fromkeys(blockers))


def _build_report_markdown(
    result: Mapping[str, Any],
    state_json_path: Path,
    governor_input_json_path: Path,
) -> str:
    branch = _git_value("rev-parse", "--abbrev-ref", "HEAD")
    head = _git_value("rev-parse", "HEAD")
    blocked = result.get("governor_blockers", [])

    lines = [
        "# AIOS Forex Autonomy Completion Governor Rerun + Bucket Policy V1 Report",
        "",
        f"Status: {result.get('candidate_status')}",
        f"Current branch: {branch}",
        f"Current head: {head}",
        f"Input files used: {state_json_path}, {governor_input_json_path}",
        "",
        f"Governor status: {result.get('candidate_status')}",
        f"Bucket status: {result.get('bucket_status')}",
        f"Next autonomy action: {result.get('next_autonomy_action')}",
        f"Owner gate status: {result.get('owner_gate_status')}",
        f"Broker gate status: {result.get('broker_gate_status')}",
        f"Live micro exception status: {result.get('live_micro_exception_status')}",
        "",
        "Safety boundary:",
        f"- order_execution_allowed: {result['safety_boundary']['order_execution_allowed']}",
        f"- broker_api_allowed: {result['safety_boundary']['broker_api_allowed']}",
        f"- credentials_allowed: {result['safety_boundary']['credentials_allowed']}",
        (
            "- account_identifier_persistence_allowed: "
            f"{result['safety_boundary']['account_identifier_persistence_allowed']}"
        ),
        f"- scheduler_allowed: {result['safety_boundary']['scheduler_allowed']}",
        f"- daemon_allowed: {result['safety_boundary']['daemon_allowed']}",
        f"- webhook_allowed: {result['safety_boundary']['webhook_allowed']}",
        "",
        "Governor blockers:",
    ]
    for blocker in _string_list(blocked):
        lines.append(f"- {blocker}")
    if not blocked:
        lines.append("- none")

    lines.extend(
        [
            "Bucket blockers:",
        ]
    )
    for blocker in _string_list(result.get("bucket_blockers", [])):
        lines.append(f"- {blocker}")
    if not result.get("bucket_blockers"):
        lines.append("- none")

    lines.extend(
        [
            "",
            f"Next safe action: {result.get('next_safe_action')}",
            "",
            "Validators:",
        ]
    )
    for validator in result.get("validator_chain", []):
        lines.append(f"- {validator}")

    return "\n".join(lines) + "\n"


def _load_json_mapping(
    payload: Mapping[str, Any] | None,
    json_path: Path,
) -> dict[str, Any]:
    if payload is not None:
        if isinstance(payload, Mapping):
            return dict(payload)
        raise ValueError("state/governor mapping must be a mapping")

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"JSON payload at {json_path} must be an object")
    return loaded


def _git_value(*command: str) -> str:
    try:
        return subprocess.check_output(["git", *command], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


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


def _to_lower_set(values: Any) -> set[str]:
    return {str(value).lower() for value in _string_list(values)}


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _to_float(value: Any, default: float | None) -> float | None:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on", "armed", "ready", "enabled"}


__all__ = [
    "run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1",
    "COLLECT_MORE_EVIDENCE",
    "RUN_DEMO_SUPERVISED_CYCLE",
    "ROUTE_OWNER_LIVE_MICRO_REVIEW",
    "HOLD_FOR_RISK_RESET",
    "HOLD_FOR_OWNER_GATE",
    "HOLD_FOR_POLICY_REVIEW",
    "BUCKET_READY",
    "BUCKET_TARGET_HOLD",
    "BUCKET_MAX_LOSS_HOLD",
    "BUCKET_POLICY_BLOCKED",
    "BUCKET_REVIEW_REQUIRED",
    "VALIDATOR_CHAIN",
    "_build_report_markdown",
]
