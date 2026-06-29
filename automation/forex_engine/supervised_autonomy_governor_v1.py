"""Deterministic offline readiness governor for supervised Forex autonomy.

This module evaluates repo-local evidence against fixed thresholds to decide
whether a candidate is ready for:

* demo-supervised execution
* live-micro exception review
* continuing with additional evidence collection

It performs no broker API calls, does not read credentials, does not handle
account identifiers, and does not authorize order execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Mapping


PACKET_ID = "PKT-FOREX-SUPERVISED-AUTONOMY-GOVERNOR-V1"
MISSION_ID = "MISSION-AIOS-FOREX-LIVE-PROOF-V1"
PROGRAM_ID = "PROGRAM-FOREX-EXECUTION-V1"
EPIC_ID = "EPC-FOREX-AUTONOMY-001"
BUCKET_ID = "BKT-FOREX-AUTONOMY-GOVERNOR-001"

AUTONOMY_WINDOW_TARGET = "22HR_6DAY_SUPERVISED"

AUTONOMY_BLOCKED = "AUTONOMY_BLOCKED"
REQUIRE_MORE_EVIDENCE = "REQUIRE_MORE_EVIDENCE"
DEMO_SUPERVISED_READY = "DEMO_SUPERVISED_READY"
LIVE_MICRO_EXCEPTION_REVIEW_READY = "LIVE_MICRO_EXCEPTION_REVIEW_READY"
LIVE_BLOCKED_BY_POLICY = "LIVE_BLOCKED_BY_POLICY"

RESULT_KEYS = (
    "candidate_status",
    "autonomy_window_target",
    "live_trading_allowed",
    "profit_claim_allowed",
    "blockers",
    "warnings",
    "passed_gates",
    "failed_gates",
    "next_safe_action",
    "evidence_summary",
)

GATE_PROFITABILITY_EVIDENCE = "profitability_evidence_status"
GATE_SAMPLE_SUFFICIENCY = "sample_sufficiency"
GATE_WALK_FORWARD = "walk_forward_sufficiency"
GATE_DRAWDOWN = "drawdown_limits"
GATE_PROFIT_FACTOR = "profit_factor_threshold"
GATE_EXPECTANCY = "expectancy_threshold"
GATE_BROKER_READINESS = "broker_readiness"
GATE_LIVE_BRIDGE = "live_bridge_eligibility"
GATE_KILL_SWITCH = "kill_switch_state"
GATE_DAILY_STOP = "daily_stop_state"
GATE_MAX_LOSS = "max_loss_state"
GATE_ORDER_COUNT = "order_count_safety"
GATE_TP_SL = "tp_sl_presence"
GATE_MONITORING = "monitoring_readiness"
GATE_EVIDENCE_FRESHNESS = "evidence_freshness"
GATE_OWNER_APPROVAL = "owner_approval"

MIN_SAMPLE_SIZE = 30
MIN_WALK_FORWARD_WINDOWS = 2
MAX_DRAWDOWN_RATIO = 0.15
MIN_PROFIT_FACTOR = 2.0
MIN_EXPECTANCY = 0.5
MAX_EVIDENCE_AGE_DAYS = 14
MAX_ORDERS_24H = 10


@dataclass(frozen=True)
class GovernorResult:
    candidate_status: str
    autonomy_window_target: str
    live_trading_allowed: bool
    profit_claim_allowed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    passed_gates: tuple[str, ...]
    failed_gates: tuple[str, ...]
    next_safe_action: str
    evidence_summary: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_status": self.candidate_status,
            "autonomy_window_target": self.autonomy_window_target,
            "live_trading_allowed": self.live_trading_allowed,
            "profit_claim_allowed": self.profit_claim_allowed,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "passed_gates": list(self.passed_gates),
            "failed_gates": list(self.failed_gates),
            "next_safe_action": self.next_safe_action,
            "evidence_summary": dict(self.evidence_summary),
        }


def safe_sample_input() -> dict[str, object]:
    """Return a deterministic offline sample that requires additional evidence."""

    return {
        "candidate_id": "sample-supervised-autonomy-v1",
        "profitability_evidence_status": "PENDING",
        "sample_size": 12,
        "walk_forward_windows": 1,
        "max_drawdown": 0.21,
        "profit_factor": 1.0,
        "expectancy": -0.10,
        "broker_readiness": True,
        "live_bridge_eligibility": False,
        "kill_switch_state": "ARMED",
        "daily_stop_state": "ARMED",
        "max_loss_state": "ARMED",
        "order_count_last_24h": 4,
        "tp_sl_present": True,
        "monitoring_ready": True,
        "evidence_age_days": 40,
        "owner_approval_status": "PENDING_OWNER_REVIEW",
        "live_exception_requested": False,
        "live_bridge_external_evidence": False,
        "owner_live_micro_exception_approved": False,
        "realized_broker_evidence": False,
    }


def evaluate_supervised_autonomy_candidate(
    input_data: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    payload = dict(safe_sample_input()) if input_data is None else dict(input_data)
    normalized = _normalize_payload(payload)
    checks = _evaluate_all_gates(normalized)

    passed_gates = tuple(check["gate"] for check in checks if check["passed"])
    failed_checks = tuple(check for check in checks if not check["passed"])
    failed_gates = tuple(check["gate"] for check in failed_checks)

    critical_blocks = tuple(
        item["gate"] for item in failed_checks if item.get("critical")
    )
    blockers = tuple(item["reason"] for item in failed_checks)
    warnings = tuple(
        item["warning"] for item in checks if item.get("warning") and item["passed"] is False
    )
    demo_ready = _all_demo_gates_passed(failed_gates)
    live_exception_requested = bool(normalized["live_exception_requested"])
    live_ready = _all_live_gates_passed(failed_gates)
    owner_approved_live = bool(normalized["owner_live_micro_exception_approved"]) and bool(
        normalized["live_bridge_external_evidence"]
    )

    if critical_blocks:
        candidate_status = AUTONOMY_BLOCKED
        next_safe_action = (
            "Collect or repair the critical blockers, then rerun this offline "
            "governor before any supervised transition."
        )
    elif not demo_ready:
        candidate_status = REQUIRE_MORE_EVIDENCE
        next_safe_action = (
            "Collect missing evidence, refresh risk metrics, and rerun this "
            "governor with sanitized input."
        )
    elif live_exception_requested:
        if owner_approved_live and live_ready:
            candidate_status = LIVE_MICRO_EXCEPTION_REVIEW_READY
            next_safe_action = (
                "Route to owner live-micro exception review; keep all live limits "
                "off until explicit human authorization."
            )
        else:
            candidate_status = LIVE_BLOCKED_BY_POLICY
            next_safe_action = (
                "Collect explicit live-bridge evidence and owner micro-exception "
                "approval, then rerun governor."
            )
    else:
        candidate_status = DEMO_SUPERVISED_READY
        next_safe_action = (
            "Proceed with demo-supervised readiness evidence capture and owner "
            "signoff; no live authorization."
        )

    live_trading_allowed = (
        candidate_status == LIVE_MICRO_EXCEPTION_REVIEW_READY
        and owner_approved_live
        and bool(normalized["live_bridge_external_evidence"])
    )
    profit_claim_allowed = bool(normalized["realized_broker_evidence"])

    result = GovernorResult(
        candidate_status=candidate_status,
        autonomy_window_target=AUTONOMY_WINDOW_TARGET,
        live_trading_allowed=live_trading_allowed,
        profit_claim_allowed=profit_claim_allowed,
        blockers=blockers,
        warnings=warnings,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        next_safe_action=next_safe_action,
        evidence_summary=_build_evidence_summary(normalized, checks),
    )

    payload = result.to_dict()
    payload["packet_id"] = PACKET_ID
    payload["mission_id"] = MISSION_ID
    payload["program_id"] = PROGRAM_ID
    payload["epic_id"] = EPIC_ID
    payload["bucket_id"] = BUCKET_ID
    return payload


def run_supervised_autonomy_governor(
    input_data: Mapping[str, Any] | None = None,
    *,
    write_report: bool = False,
    report_path: str | Path | None = None,
) -> dict[str, object]:
    result = evaluate_supervised_autonomy_candidate(input_data)
    if write_report:
        path = Path(
            report_path
            if report_path is not None
            else Path(__file__).resolve().parents[2]
            / "Reports"
            / "forex_delivery"
            / "AIOS_FOREX_SUPERVISED_AUTONOMY_GOVERNOR_V1_REPORT.md"
        )
        path.write_text(_build_report_markdown(result), encoding="utf-8")
    return result


def _normalize_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    return {
        "candidate_id": _text(payload.get("candidate_id", "sample-candidate")),
        "profitability_evidence_status": _canonical_status(
            payload.get("profitability_evidence_status")
        ),
        "sample_size": _as_float(payload.get("sample_size"), allow_none=True),
        "walk_forward_windows": _as_float(payload.get("walk_forward_windows"), allow_none=True),
        "max_drawdown": _as_float(payload.get("max_drawdown"), allow_none=True),
        "profit_factor": _as_float(payload.get("profit_factor"), allow_none=True),
        "expectancy": _as_float(payload.get("expectancy"), allow_none=True),
        "broker_readiness": _as_bool(payload.get("broker_readiness")),
        "live_bridge_eligibility": _as_bool(payload.get("live_bridge_eligibility")),
        "kill_switch_state": _canonical_status(payload.get("kill_switch_state")),
        "daily_stop_state": _canonical_status(payload.get("daily_stop_state")),
        "max_loss_state": _canonical_status(payload.get("max_loss_state")),
        "order_count_last_24h": _as_int(payload.get("order_count_last_24h"), default=None),
        "tp_sl_present": _as_bool(payload.get("tp_sl_present")),
        "monitoring_ready": _as_bool(payload.get("monitoring_ready")),
        "evidence_age_days": _as_float(payload.get("evidence_age_days"), allow_none=True),
        "owner_approval_status": _canonical_status(payload.get("owner_approval_status")),
        "live_exception_requested": _as_bool(payload.get("live_exception_requested")),
        "live_bridge_external_evidence": _as_bool(
            payload.get("live_bridge_external_evidence")
        ),
        "owner_live_micro_exception_approved": _as_bool(
            payload.get("owner_live_micro_exception_approved")
        ),
        "realized_broker_evidence": _as_bool(
            payload.get("realized_broker_evidence")
        ),
    }


def _evaluate_all_gates(payload: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    checks: list[dict[str, object]] = []
    checks.append(_evaluate_profitability_evidence(payload))
    checks.append(_evaluate_sample_sufficiency(payload))
    checks.append(_evaluate_walk_forward(payload))
    checks.append(_evaluate_drawdown(payload))
    checks.append(_evaluate_profit_factor(payload))
    checks.append(_evaluate_expectancy(payload))
    checks.append(_evaluate_broker_readiness(payload))
    checks.append(_evaluate_live_bridge(payload))
    checks.append(_evaluate_kill_switch(payload))
    checks.append(_evaluate_daily_stop(payload))
    checks.append(_evaluate_max_loss(payload))
    checks.append(_evaluate_order_count(payload))
    checks.append(_evaluate_tp_sl(payload))
    checks.append(_evaluate_monitoring(payload))
    checks.append(_evaluate_evidence_freshness(payload))
    checks.append(_evaluate_owner_approval(payload))
    return tuple(checks)


def _evaluate_profitability_evidence(payload: Mapping[str, object]) -> dict[str, object]:
    status = _canonical_status(payload["profitability_evidence_status"])
    if status == "READY":
        return _check_pass(
            GATE_PROFITABILITY_EVIDENCE,
            True,
            warning="",
            critical=False,
        )
    if status in {"INSUFFICIENT", "MISSING", "PENDING", ""}:
        return _check_fail(
            GATE_PROFITABILITY_EVIDENCE,
            "profitability evidence is not complete",
            critical=False,
        )
    return _check_fail(
        GATE_PROFITABILITY_EVIDENCE,
        "unrecognized profitability evidence status",
        critical=False,
    )


def _evaluate_sample_sufficiency(payload: Mapping[str, object]) -> dict[str, object]:
    sample_size = payload["sample_size"]
    if sample_size is None:
        return _check_fail(
            GATE_SAMPLE_SUFFICIENCY,
            "sample_size is required",
            critical=False,
        )

    value = float(sample_size)
    if value >= MIN_SAMPLE_SIZE:
        return _check_pass(GATE_SAMPLE_SUFFICIENCY, True, warning="")
    return _check_fail(
        GATE_SAMPLE_SUFFICIENCY,
        f"sample_size={value:.0f} is below minimum {MIN_SAMPLE_SIZE}",
        warning="",
        critical=False,
    )


def _evaluate_walk_forward(payload: Mapping[str, object]) -> dict[str, object]:
    windows = payload["walk_forward_windows"]
    if windows is None:
        return _check_fail(
            GATE_WALK_FORWARD,
            "walk_forward_windows is required",
            critical=False,
        )

    value = float(windows)
    if value >= MIN_WALK_FORWARD_WINDOWS:
        return _check_pass(GATE_WALK_FORWARD, True, warning="")
    return _check_fail(
        GATE_WALK_FORWARD,
        f"walk_forward_windows={value:.0f} is below minimum {MIN_WALK_FORWARD_WINDOWS}",
        critical=False,
    )


def _evaluate_drawdown(payload: Mapping[str, object]) -> dict[str, object]:
    drawdown = payload["max_drawdown"]
    if drawdown is None:
        return _check_fail(
            GATE_DRAWDOWN,
            "max_drawdown is required",
            critical=False,
        )

    value = float(drawdown)
    if value <= MAX_DRAWDOWN_RATIO:
        return _check_pass(GATE_DRAWDOWN, True, warning="")
    return _check_fail(
        GATE_DRAWDOWN,
        f"max_drawdown={value:.2f} exceeds threshold {MAX_DRAWDOWN_RATIO:.2f}",
        critical=False,
    )


def _evaluate_profit_factor(payload: Mapping[str, object]) -> dict[str, object]:
    value = _as_optional_float(payload["profit_factor"])
    if value is None:
        return _check_fail(
            GATE_PROFIT_FACTOR,
            "profit_factor is required",
            critical=False,
        )
    if value >= MIN_PROFIT_FACTOR:
        return _check_pass(GATE_PROFIT_FACTOR, True, warning="")
    return _check_fail(
        GATE_PROFIT_FACTOR,
        f"profit_factor={value:.2f} below threshold {MIN_PROFIT_FACTOR:.2f}",
        critical=False,
    )


def _evaluate_expectancy(payload: Mapping[str, object]) -> dict[str, object]:
    value = _as_optional_float(payload["expectancy"])
    if value is None:
        return _check_fail(
            GATE_EXPECTANCY,
            "expectancy is required",
            critical=False,
        )
    if value >= MIN_EXPECTANCY:
        return _check_pass(GATE_EXPECTANCY, True, warning="")
    return _check_fail(
        GATE_EXPECTANCY,
        f"expectancy={value:.2f} below threshold {MIN_EXPECTANCY:.2f}",
        critical=False,
    )


def _evaluate_broker_readiness(payload: Mapping[str, object]) -> dict[str, object]:
    if bool(payload["broker_readiness"]):
        return _check_pass(GATE_BROKER_READINESS, True, warning="")
    return _check_fail(
        GATE_BROKER_READINESS,
        "broker readiness is false",
        critical=False,
    )


def _evaluate_live_bridge(payload: Mapping[str, object]) -> dict[str, object]:
    if bool(payload["live_bridge_eligibility"]):
        return _check_pass(GATE_LIVE_BRIDGE, True, warning="")
    return _check_fail(
        GATE_LIVE_BRIDGE,
        "live bridge evidence is not available",
        critical=False,
    )


def _evaluate_kill_switch(payload: Mapping[str, object]) -> dict[str, object]:
    state = str(payload["kill_switch_state"]).upper() if payload["kill_switch_state"] else ""
    if state in {"ARMED", "READY", "ENABLED"}:
        return _check_pass(GATE_KILL_SWITCH, True, warning="")
    return _check_fail(
        GATE_KILL_SWITCH,
        f"kill switch state is '{state or 'UNKNOWN'}'",
        critical=True,
    )


def _evaluate_daily_stop(payload: Mapping[str, object]) -> dict[str, object]:
    state = str(payload["daily_stop_state"]).upper() if payload["daily_stop_state"] else ""
    if state in {"ARMED", "READY", "ENABLED"}:
        return _check_pass(GATE_DAILY_STOP, True, warning="")
    return _check_fail(
        GATE_DAILY_STOP,
        f"daily stop state is '{state or 'UNKNOWN'}'",
        critical=False,
    )


def _evaluate_max_loss(payload: Mapping[str, object]) -> dict[str, object]:
    if str(payload["max_loss_state"]).upper() in {"ARMED", "ENABLED", "READY"}:
        return _check_pass(GATE_MAX_LOSS, True, warning="")
    if str(payload["max_loss_state"]).upper() in {"UNSET", ""}:
        return _check_fail(
            GATE_MAX_LOSS,
            "max loss state is not configured",
            critical=False,
        )
    return _check_fail(
        GATE_MAX_LOSS,
        f"max loss state is '{payload['max_loss_state']}'",
        critical=False,
    )


def _evaluate_order_count(payload: Mapping[str, object]) -> dict[str, object]:
    count = payload["order_count_last_24h"]
    if count is None:
        return _check_fail(
            GATE_ORDER_COUNT,
            "order_count_last_24h is required",
            critical=False,
        )
    if count < 0:
        return _check_fail(
            GATE_ORDER_COUNT,
            "order_count_last_24h cannot be negative",
            critical=False,
        )
    if count <= MAX_ORDERS_24H:
        return _check_pass(GATE_ORDER_COUNT, True, warning="")
    return _check_fail(
        GATE_ORDER_COUNT,
        f"order_count_last_24h={count} exceeds threshold {MAX_ORDERS_24H}",
        critical=False,
    )


def _evaluate_tp_sl(payload: Mapping[str, object]) -> dict[str, object]:
    if bool(payload["tp_sl_present"]):
        return _check_pass(GATE_TP_SL, True, warning="")
    return _check_fail(
        GATE_TP_SL,
        "take-profit / stop-loss evidence is missing",
        critical=False,
    )


def _evaluate_monitoring(payload: Mapping[str, object]) -> dict[str, object]:
    if bool(payload["monitoring_ready"]):
        return _check_pass(GATE_MONITORING, True, warning="")
    return _check_fail(
        GATE_MONITORING,
        "monitoring readiness is false",
        critical=False,
    )


def _evaluate_evidence_freshness(payload: Mapping[str, object]) -> dict[str, object]:
    age = payload["evidence_age_days"]
    if age is None:
        return _check_fail(
            GATE_EVIDENCE_FRESHNESS,
            "evidence_age_days is required",
            critical=False,
        )
    if age <= MAX_EVIDENCE_AGE_DAYS:
        return _check_pass(GATE_EVIDENCE_FRESHNESS, True, warning="")
    return _check_fail(
        GATE_EVIDENCE_FRESHNESS,
        f"evidence_age_days={age:.0f} exceeds freshness limit {MAX_EVIDENCE_AGE_DAYS}",
        critical=False,
    )


def _evaluate_owner_approval(payload: Mapping[str, object]) -> dict[str, object]:
    status = str(payload["owner_approval_status"]).upper()
    if status in {"APPROVED", "APPROVED_FOR_DEMO", "APPROVED_FOR_LIVE_MICRO"}:
        return _check_pass(GATE_OWNER_APPROVAL, True, warning="")
    if status in {"DENIED", "REJECTED"}:
        return _check_fail(
            GATE_OWNER_APPROVAL,
            "owner approval explicitly denied",
            critical=True,
        )
    return _check_fail(
        GATE_OWNER_APPROVAL,
        "owner approval is pending",
        critical=False,
    )


def _all_demo_gates_passed(failed_gates: Sequence[str]) -> bool:
    demo_gates = (
        GATE_PROFITABILITY_EVIDENCE,
        GATE_SAMPLE_SUFFICIENCY,
        GATE_WALK_FORWARD,
        GATE_DRAWDOWN,
        GATE_PROFIT_FACTOR,
        GATE_EXPECTANCY,
        GATE_BROKER_READINESS,
        GATE_EVIDENCE_FRESHNESS,
        GATE_OWNER_APPROVAL,
    )
    return all(name not in failed_gates for name in demo_gates)


def _all_live_gates_passed(failed_gates: Sequence[str]) -> bool:
    live_gates = (
        GATE_LIVE_BRIDGE,
        GATE_KILL_SWITCH,
        GATE_DAILY_STOP,
        GATE_MAX_LOSS,
        GATE_ORDER_COUNT,
        GATE_TP_SL,
        GATE_MONITORING,
    )
    return all(name not in failed_gates for name in live_gates)


def _build_evidence_summary(
    payload: Mapping[str, object], checks: Sequence[Mapping[str, object]]
) -> dict[str, object]:
    gates: dict[str, object] = {}
    for item in checks:
        gates[item["gate"]] = "PASS" if item["passed"] else "FAIL"

    return {
        "candidate_id": payload["candidate_id"],
        "autonomy_window_target": AUTONOMY_WINDOW_TARGET,
        "gate_status": gates,
        "raw_metrics": {
            "sample_size": payload["sample_size"],
            "walk_forward_windows": payload["walk_forward_windows"],
            "max_drawdown": payload["max_drawdown"],
            "profit_factor": payload["profit_factor"],
            "expectancy": payload["expectancy"],
            "evidence_age_days": payload["evidence_age_days"],
        },
        "live_inputs": {
            "live_exception_requested": payload["live_exception_requested"],
            "live_bridge_external_evidence": payload["live_bridge_external_evidence"],
            "owner_live_micro_exception_approved": payload[
                "owner_live_micro_exception_approved"
            ],
        },
    }


def _build_report_markdown(payload: Mapping[str, object]) -> str:
    return (
        "# AIOS Forex Supervised Autonomy Governor V1 Report\n\n"
        "## Status\n"
        f"Candidate status: {payload['candidate_status']}\n"
        f"Autonomy target: {payload['autonomy_window_target']}\n"
        f"Live trading allowed: {payload['live_trading_allowed']}\n"
        f"Profit claim allowed: {payload['profit_claim_allowed']}\n\n"
        "## Passes / Failures\n"
        f"Passed gates: {list(payload['passed_gates'])}\n"
        f"Failed gates: {list(payload['failed_gates'])}\n\n"
        "## Blockers\n"
        f"{_format_list(payload['blockers'])}\n\n"
        "## Warnings\n"
        f"{_format_list(payload['warnings'])}\n\n"
        "## Evidence Summary\n"
        f"```json\n{json.dumps(payload['evidence_summary'], indent=2, sort_keys=True)}\n```\n"
    )


def _check_pass(gate: str, passed: bool, warning: str, critical: bool = False) -> dict[str, object]:
    return {
        "gate": gate,
        "passed": bool(passed),
        "reason": "",
        "warning": warning,
        "critical": bool(critical),
    }


def _check_fail(
    gate: str,
    reason: str,
    *,
    critical: bool,
    warning: str = "",
) -> dict[str, object]:
    return {
        "gate": gate,
        "passed": False,
        "reason": reason,
        "warning": warning,
        "critical": bool(critical),
    }


def _as_float(value: Any, *, allow_none: bool = False) -> float | None:
    if value is None:
        return None if allow_none else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        converted = float(str(value))
    except (TypeError, ValueError):
        return None
    return converted


def _as_optional_float(value: Any) -> float | None:
    return _as_float(value, allow_none=True)


def _as_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on", "armed", "ready"}


def _canonical_status(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip().upper()
    return str(value).strip().upper()


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _format_list(values: Sequence[str]) -> str:
    if not values:
        return "- none"
    return "\n".join(f"- {value}" for value in values)
