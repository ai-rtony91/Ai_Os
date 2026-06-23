"""Forex uptime and range planner V1.

This module calculates planning-only trading windows from sanitized local
inputs. It does not connect to brokers, does not activate schedulers, and does
not authorize 22/5, 22/6, 80 percent uptime, or automated trading.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping


UPTIME_80_PLANNING = "UPTIME_80_PLANNING"
RANGE_22_5_PLANNING = "RANGE_22_5_PLANNING"
RANGE_22_6_REQUESTED_PLANNING = "RANGE_22_6_REQUESTED_PLANNING"
RANGE_DETECTED_FROM_BROKER_SESSION = "RANGE_DETECTED_FROM_BROKER_SESSION"
RANGE_BLOCKED_BY_EVIDENCE = "RANGE_BLOCKED_BY_EVIDENCE"

UPTIME_RANGE_PLANNING_ONLY = "UPTIME_RANGE_PLANNING_ONLY"
UPTIME_RANGE_READY_FOR_PAPER_SIMULATION = "UPTIME_RANGE_READY_FOR_PAPER_SIMULATION"
UPTIME_RANGE_READY_FOR_DEMO_REVIEW = "UPTIME_RANGE_READY_FOR_DEMO_REVIEW"
UPTIME_RANGE_BLOCKED_BY_LIVE_EVIDENCE = "UPTIME_RANGE_BLOCKED_BY_LIVE_EVIDENCE"
UPTIME_RANGE_READY_FOR_FUTURE_APPROVAL_REVIEW = "UPTIME_RANGE_READY_FOR_FUTURE_APPROVAL_REVIEW"

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "Reports" / "forex_delivery"
REPORT_PATH = REPORTS_DIR / "AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md"

SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "password",
    "passwd",
    "secret",
    "token",
    "credential",
    "credentials",
    "account_id",
    "accountid",
    "account_identifier",
    "account_number",
    "broker_order_id",
    "order_id",
    "transaction_id",
    "raw_payload",
    "raw_request",
    "raw_response",
    "authorization",
)


def run_forex_uptime_range_planner(
    input_state: dict[str, Any] | None = None,
    write_reports: bool = False,
) -> dict[str, Any]:
    """Calculate sanitized uptime and range readiness from local evidence."""

    state, redacted_fields = _sanitize_input(input_state or {})
    windows = _window_inputs(state)
    calculations = _calculate_windows(windows, state)
    gates = _readiness_gates(state)
    planning_modes = _planning_modes(state, windows, gates)
    range_status = _classify_range(state, windows, gates, planning_modes)

    result = {
        "schema": "AIOS_FOREX_UPTIME_RANGE_PLANNER_V1",
        "write_reports_requested": bool(write_reports),
        "planning_modes": tuple(planning_modes),
        "inputs": windows,
        "calculations": calculations,
        "readiness_gates": gates,
        "classifications": {
            "UPTIME_RANGE_STATUS": range_status,
        },
        "blocked_reasons": tuple(_blocked_reasons(state, gates, planning_modes, redacted_fields)),
        "sanitization": {
            "redacted_fields": tuple(redacted_fields),
            "sensitive_input_rejected_or_redacted": bool(redacted_fields),
            "account_ids_persisted": False,
            "credentials_persisted": False,
            "broker_order_ids_persisted": False,
        },
        "safety_summary": _safety_summary(),
        "activation_status": {
            "uptime_80_activated": False,
            "range_22_5_activated": False,
            "range_22_6_activated": False,
            "automated_trading_activated": False,
        },
        "reports": {
            "written": tuple(),
            "allowed_output_paths": (_display_path(REPORT_PATH),),
        },
    }

    if write_reports:
        written = _write_reports(result)
        result["reports"] = {
            **result["reports"],
            "written": tuple(_display_path(path) for path in written),
        }

    return result


def _sanitize_input(payload: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    redacted: list[str] = []

    def scrub(value: Any, path: tuple[str, ...] = ()) -> Any:
        if isinstance(value, Mapping):
            output: dict[str, Any] = {}
            for key, item in value.items():
                key_text = str(key)
                normalized = key_text.lower().strip()
                if any(part in normalized for part in SENSITIVE_KEY_PARTS):
                    redacted.append(".".join(path + (key_text,)))
                    continue
                output[key_text] = scrub(item, path + (key_text,))
            return output
        if isinstance(value, list):
            return [scrub(item, path + (str(index),)) for index, item in enumerate(value)]
        if isinstance(value, tuple):
            return tuple(scrub(item, path + (str(index),)) for index, item in enumerate(value))
        return value

    return scrub(payload), _unique(redacted)


def _window_inputs(state: Mapping[str, Any]) -> dict[str, Any]:
    trading_hours_per_day = _bounded_number(state.get("trading_hours_per_day", 0.0), 0.0, 24.0)
    trading_days_per_week = _bounded_number(state.get("trading_days_per_week", 0.0), 0.0, 7.0)
    maintenance_hours_per_day = _bounded_number(state.get("maintenance_hours_per_day", 0.0), 0.0, 24.0)
    requested_range = str(state.get("requested_range", state.get("range_request", ""))).upper().strip()
    return {
        "trading_hours_per_day": trading_hours_per_day,
        "trading_days_per_week": trading_days_per_week,
        "maintenance_hours_per_day": maintenance_hours_per_day,
        "requested_range": requested_range or "UNSPECIFIED",
        "broker_session_proof": _proof_summary(state.get("broker_session_proof")),
        "market_session_proof": _proof_summary(state.get("market_session_proof")),
        "incident_stop_proof": _proof_summary(state.get("incident_stop_proof")),
        "monitoring_proof": _proof_summary(state.get("monitoring_proof")),
        "reconciliation_proof": _proof_summary(state.get("reconciliation_proof")),
    }


def _calculate_windows(windows: Mapping[str, Any], state: Mapping[str, Any]) -> dict[str, Any]:
    trading_hours_per_week = round(windows["trading_hours_per_day"] * windows["trading_days_per_week"], 2)
    maintenance_hours_per_week = round(windows["maintenance_hours_per_day"] * max(windows["trading_days_per_week"], 1.0), 2)
    unused_weekly_hours = round(max(0.0, 168.0 - trading_hours_per_week), 2)
    minimum_maintenance_budget = round(max(maintenance_hours_per_week, unused_weekly_hours, 168.0 * 0.20), 2)
    return {
        "trading_hours_per_week": trading_hours_per_week,
        "maintenance_hours_per_week": maintenance_hours_per_week,
        "minimum_maintenance_budget": minimum_maintenance_budget,
        "blocked_windows": tuple(str(item) for item in state.get("blocked_windows", ("BROKER_MAINTENANCE",))),
        "review_windows": tuple(str(item) for item in state.get("review_windows", ("DAILY_RISK_REVIEW", "WEEKLY_RECONCILIATION_REVIEW"))),
        "incident_recovery_windows": tuple(str(item) for item in state.get("incident_recovery_windows", ("INCIDENT_STOP_RECOVERY",))),
    }


def _readiness_gates(state: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "broker_session_proof": _proof_passes(state.get("broker_session_proof")),
        "market_session_proof": _proof_passes(state.get("market_session_proof")),
        "incident_stop_proof": _proof_passes(state.get("incident_stop_proof")),
        "monitoring_proof": _proof_passes(state.get("monitoring_proof")),
        "reconciliation_proof": _proof_passes(state.get("reconciliation_proof")),
        "live_evidence_proof": _proof_passes(state.get("live_evidence_proof")),
        "human_approval_proof": _proof_passes(state.get("human_approval_proof")),
    }


def _planning_modes(state: Mapping[str, Any], windows: Mapping[str, Any], gates: Mapping[str, bool]) -> list[str]:
    modes: list[str] = []
    requested_range = windows["requested_range"]
    if _truthy(state.get("uptime_80_requested")) or _number(state.get("uptime_target_percent")) >= 80.0:
        modes.append(UPTIME_80_PLANNING)
    if requested_range in {"22/5", "RANGE_22_5"}:
        modes.append(RANGE_22_5_PLANNING)
    if requested_range in {"22/6", "RANGE_22_6"}:
        modes.append(RANGE_22_6_REQUESTED_PLANNING)
    if not modes:
        modes.append(UPTIME_80_PLANNING)
    if gates["broker_session_proof"] and gates["market_session_proof"]:
        modes.append(RANGE_DETECTED_FROM_BROKER_SESSION)
    if not _core_gates_pass(gates):
        modes.append(RANGE_BLOCKED_BY_EVIDENCE)
    return _unique(modes)


def _classify_range(
    state: Mapping[str, Any],
    windows: Mapping[str, Any],
    gates: Mapping[str, bool],
    planning_modes: Iterable[str],
) -> str:
    modes = set(planning_modes)
    requested_range = windows["requested_range"]
    if RANGE_22_6_REQUESTED_PLANNING in modes and not _range_22_6_supported(state, gates):
        return UPTIME_RANGE_PLANNING_ONLY
    if RANGE_22_5_PLANNING in modes and not _core_gates_pass(gates):
        return UPTIME_RANGE_PLANNING_ONLY
    if UPTIME_80_PLANNING in modes and not _core_gates_pass(gates):
        return UPTIME_RANGE_PLANNING_ONLY
    if not _core_gates_pass(gates):
        return UPTIME_RANGE_PLANNING_ONLY
    if requested_range in {"22/6", "RANGE_22_6"} and not gates["live_evidence_proof"]:
        return UPTIME_RANGE_BLOCKED_BY_LIVE_EVIDENCE
    if _truthy(state.get("demo_review_requested")):
        return UPTIME_RANGE_READY_FOR_DEMO_REVIEW
    if gates["live_evidence_proof"] and gates["human_approval_proof"]:
        return UPTIME_RANGE_READY_FOR_FUTURE_APPROVAL_REVIEW
    return UPTIME_RANGE_READY_FOR_PAPER_SIMULATION


def _range_22_6_supported(state: Mapping[str, Any], gates: Mapping[str, bool]) -> bool:
    if not (gates["broker_session_proof"] and gates["market_session_proof"]):
        return False
    proof = state.get("broker_session_proof")
    if isinstance(proof, Mapping):
        hours = _number(proof.get("supported_hours_per_week"))
        days = _number(proof.get("supported_days_per_week"))
        return hours >= 132.0 and days >= 6.0
    return False


def _core_gates_pass(gates: Mapping[str, bool]) -> bool:
    return (
        gates["broker_session_proof"]
        and gates["market_session_proof"]
        and gates["incident_stop_proof"]
        and gates["monitoring_proof"]
        and gates["reconciliation_proof"]
    )


def _blocked_reasons(
    state: Mapping[str, Any],
    gates: Mapping[str, bool],
    planning_modes: Iterable[str],
    redacted_fields: list[str],
) -> list[str]:
    reasons: list[str] = []
    for key, passed in gates.items():
        if key in {"live_evidence_proof", "human_approval_proof"}:
            continue
        if not passed:
            reasons.append(f"{key}_missing_or_unproven")
    if RANGE_22_6_REQUESTED_PLANNING in set(planning_modes) and not _range_22_6_supported(state, gates):
        reasons.append("22_6_requires_broker_and_market_session_support")
    if redacted_fields:
        reasons.append("sensitive_input_redacted")
    return _unique(reasons)


def _write_reports(result: Mapping[str, Any]) -> list[Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(result), encoding="utf-8", newline="\n")
    return [REPORT_PATH]


def _render_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Uptime Range Planner 80 22/5 22/6 V1",
            "",
            "## Uptime Range Status",
            f"`{result['classifications']['UPTIME_RANGE_STATUS']}`",
            "",
            "## Planning Modes",
            _bullets(result["planning_modes"]),
            "",
            "## Inputs",
            _table(result["inputs"]),
            "",
            "## Calculations",
            _table(result["calculations"]),
            "",
            "## Readiness Gates",
            _table(result["readiness_gates"]),
            "",
            "## Blocked Reasons",
            _bullets(result["blocked_reasons"]),
            "",
            "## Range Doctrine",
            "- 22/6 is requested planning only unless broker/session evidence proves the instrument and operating window support it.",
            "- 22/5 remains planning only unless all readiness gates pass.",
            "- 80 percent uptime remains planning only unless all readiness gates pass.",
            "- AIOS must calculate allowed trading range from evidence and broker/session rules instead of hardcoding 22/6.",
            "",
            "## Activation Status",
            _table(result["activation_status"]),
            "",
            "## Safety",
            _table(result["safety_summary"]),
            "",
        ]
    )


def _proof_passes(value: Any) -> bool:
    if isinstance(value, Mapping):
        status = str(value.get("status", value.get("proof_status", ""))).upper().strip()
        return bool(value.get("proven") is True or status in {"CURRENT", "PROVEN", "PASS", "SUPPORTED"})
    if isinstance(value, bool):
        return value
    return str(value).upper().strip() in {"CURRENT", "PROVEN", "PASS", "SUPPORTED", "TRUE"}


def _proof_summary(value: Any) -> str:
    if isinstance(value, Mapping):
        if value.get("instrument"):
            return f"{value.get('status', 'UNKNOWN')}:{value.get('instrument')}"
        return str(value.get("status", value.get("proof_status", "UNKNOWN")))
    if value in (None, ""):
        return "MISSING"
    return str(value)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).upper().strip() in {"TRUE", "YES", "REQUESTED", "1"}


def _bounded_number(value: Any, minimum: float, maximum: float) -> float:
    return min(max(_number(value), minimum), maximum)


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safety_summary() -> dict[str, bool]:
    return {
        "broker_api_called": False,
        "network_call_performed": False,
        "credentials_read": False,
        "account_identifiers_read": False,
        "env_read": False,
        "secret_files_read": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
        "uptime_80_activated": False,
        "range_22_5_activated": False,
        "range_22_6_activated": False,
        "automated_trading_activated": False,
    }


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _bullets(values: Iterable[Any]) -> str:
    items = [str(value) for value in values]
    return "\n".join(f"- `{item}`" for item in items) if items else "- `NONE`"


def _table(values: Mapping[str, Any]) -> str:
    lines = ["| Field | Value |", "|---|---|"]
    for key, value in values.items():
        lines.append(f"| {key} | `{value}` |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(json.dumps(run_forex_uptime_range_planner(write_reports=True), indent=2, sort_keys=True))
