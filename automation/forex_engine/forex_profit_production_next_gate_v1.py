"""Read-only Forex profit-production next-gate decision module.

This module uses deterministic local logic only. It accepts plain evidence
mappings, classifies the next gate result, and never approves live trading.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SCHEMA = "AIOS_FOREX_PROFIT_PRODUCTION_NEXT_GATE_V1"
MODE = "READ_ONLY_NEXT_GATE"

BLOCKED_MISSING_EVIDENCE = "BLOCKED_MISSING_EVIDENCE"
BLOCKED_RISK_CONTROL_FAILURE = "BLOCKED_RISK_CONTROL_FAILURE"
BLOCKED_INSUFFICIENT_SAMPLE = "BLOCKED_INSUFFICIENT_SAMPLE"
BLOCKED_NEGATIVE_EXPECTANCY = "BLOCKED_NEGATIVE_EXPECTANCY"
BLOCKED_LOW_PROFIT_FACTOR = "BLOCKED_LOW_PROFIT_FACTOR"
BLOCKED_EXCESSIVE_DRAWDOWN = "BLOCKED_EXCESSIVE_DRAWDOWN"
READY_FOR_OWNER_REVIEW = "READY_FOR_OWNER_REVIEW"
READY_FOR_DEMO_ONLY_NEXT_STEP = "READY_FOR_DEMO_ONLY_NEXT_STEP"

MINIMUM_TOTAL_TRADES = 30
MINIMUM_EXPECTANCY = 0.0
MINIMUM_PROFIT_FACTOR = 1.10
MAXIMUM_DRAWDOWN_PCT = 10.0

REQUIRED_EVIDENCE_FIELDS = (
    "total_trades",
    "expectancy",
    "profit_factor",
    "max_drawdown_pct",
    "risk_controls_present",
    "risk_controls_passed",
    "owner_approval_required",
    "live_trading_requested",
)

READY_STATUSES = {
    READY_FOR_OWNER_REVIEW,
    READY_FOR_DEMO_ONLY_NEXT_STEP,
}

THRESHOLDS = {
    "minimum_total_trades": MINIMUM_TOTAL_TRADES,
    "minimum_expectancy": MINIMUM_EXPECTANCY,
    "minimum_profit_factor": MINIMUM_PROFIT_FACTOR,
    "maximum_drawdown_pct": MAXIMUM_DRAWDOWN_PCT,
}


def evaluate_forex_profit_production_next_gate_v1(
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate the Forex next gate using deterministic local evidence only."""

    evidence_map = _mapping_or_empty(evidence)
    normalized_evidence, missing_fields = _normalize_evidence(evidence_map)

    if not evidence_map or missing_fields:
        return _build_result(
            status=BLOCKED_MISSING_EVIDENCE,
            blockers=[f"missing_or_invalid_evidence: {field}" for field in missing_fields],
            warnings=_warnings_for_status(BLOCKED_MISSING_EVIDENCE, missing_fields=missing_fields),
            next_safe_action=_next_safe_action(BLOCKED_MISSING_EVIDENCE),
            normalized_evidence=normalized_evidence,
        )

    live_trading_requested = bool(normalized_evidence["live_trading_requested"])
    risk_controls_present = bool(normalized_evidence["risk_controls_present"])
    risk_controls_passed = bool(normalized_evidence["risk_controls_passed"])
    total_trades = int(normalized_evidence["total_trades"])
    expectancy = float(normalized_evidence["expectancy"])
    profit_factor = float(normalized_evidence["profit_factor"])
    max_drawdown_pct = float(normalized_evidence["max_drawdown_pct"])
    owner_approval_required = bool(normalized_evidence["owner_approval_required"])

    if live_trading_requested:
        return _build_result(
            status=BLOCKED_RISK_CONTROL_FAILURE,
            blockers=["live_trading_requested_true"],
            warnings=_warnings_for_status(BLOCKED_RISK_CONTROL_FAILURE),
            next_safe_action=_next_safe_action(BLOCKED_RISK_CONTROL_FAILURE),
            normalized_evidence=normalized_evidence,
        )

    if not risk_controls_present:
        return _build_result(
            status=BLOCKED_RISK_CONTROL_FAILURE,
            blockers=["risk_controls_present_false"],
            warnings=_warnings_for_status(BLOCKED_RISK_CONTROL_FAILURE),
            next_safe_action=_next_safe_action(BLOCKED_RISK_CONTROL_FAILURE),
            normalized_evidence=normalized_evidence,
        )

    if not risk_controls_passed:
        return _build_result(
            status=BLOCKED_RISK_CONTROL_FAILURE,
            blockers=["risk_controls_passed_false"],
            warnings=_warnings_for_status(BLOCKED_RISK_CONTROL_FAILURE),
            next_safe_action=_next_safe_action(BLOCKED_RISK_CONTROL_FAILURE),
            normalized_evidence=normalized_evidence,
        )

    if total_trades < MINIMUM_TOTAL_TRADES:
        return _build_result(
            status=BLOCKED_INSUFFICIENT_SAMPLE,
            blockers=[f"total_trades_below_minimum: {total_trades} < {MINIMUM_TOTAL_TRADES}"],
            warnings=_warnings_for_status(BLOCKED_INSUFFICIENT_SAMPLE),
            next_safe_action=_next_safe_action(BLOCKED_INSUFFICIENT_SAMPLE),
            normalized_evidence=normalized_evidence,
        )

    if expectancy <= MINIMUM_EXPECTANCY:
        return _build_result(
            status=BLOCKED_NEGATIVE_EXPECTANCY,
            blockers=[f"expectancy_not_positive: {expectancy} <= {MINIMUM_EXPECTANCY}"],
            warnings=_warnings_for_status(BLOCKED_NEGATIVE_EXPECTANCY),
            next_safe_action=_next_safe_action(BLOCKED_NEGATIVE_EXPECTANCY),
            normalized_evidence=normalized_evidence,
        )

    if profit_factor < MINIMUM_PROFIT_FACTOR:
        return _build_result(
            status=BLOCKED_LOW_PROFIT_FACTOR,
            blockers=[
                f"profit_factor_below_minimum: {profit_factor} < {MINIMUM_PROFIT_FACTOR}"
            ],
            warnings=_warnings_for_status(BLOCKED_LOW_PROFIT_FACTOR),
            next_safe_action=_next_safe_action(BLOCKED_LOW_PROFIT_FACTOR),
            normalized_evidence=normalized_evidence,
        )

    if max_drawdown_pct > MAXIMUM_DRAWDOWN_PCT:
        return _build_result(
            status=BLOCKED_EXCESSIVE_DRAWDOWN,
            blockers=[
                f"max_drawdown_pct_above_maximum: {max_drawdown_pct} > {MAXIMUM_DRAWDOWN_PCT}"
            ],
            warnings=_warnings_for_status(BLOCKED_EXCESSIVE_DRAWDOWN),
            next_safe_action=_next_safe_action(BLOCKED_EXCESSIVE_DRAWDOWN),
            normalized_evidence=normalized_evidence,
        )

    if owner_approval_required:
        status = READY_FOR_OWNER_REVIEW
    else:
        status = READY_FOR_DEMO_ONLY_NEXT_STEP

    return _build_result(
        status=status,
        blockers=[],
        warnings=_warnings_for_status(status),
        next_safe_action=_next_safe_action(status),
        normalized_evidence=normalized_evidence,
    )


def build_report_markdown(result: Mapping[str, Any]) -> str:
    """Build a compact owner-facing report for the gate result."""

    normalized = _mapping_or_empty(result.get("normalized_evidence"))
    blockers = list(result.get("blockers") or [])
    warnings = list(result.get("warnings") or [])
    lines = [
        "# AIOS Forex Profit Production Next Gate V1 Report",
        "",
        "## Purpose",
        "Decide whether the Forex practice/demo evidence is strong enough to move to owner review or the next supervised demo-only step.",
        "",
        "## Files Completed",
        "- automation/forex_engine/forex_profit_production_next_gate_v1.py",
        "- tests/forex_engine/test_forex_profit_production_next_gate_v1.py",
        "- Reports/forex_delivery/AIOS_FOREX_PROFIT_PRODUCTION_NEXT_GATE_V1_REPORT.md",
        "",
        "## Safety Boundary",
        "- Deterministic local logic only.",
        "- No broker APIs.",
        "- No credentials.",
        "- No .env access.",
        "- No orders.",
        "- No money movement.",
        "- No live trading approval.",
        "",
        "## Gate Statuses",
        f"- status: `{result.get('status', BLOCKED_MISSING_EVIDENCE)}`",
        f"- passed: `{str(bool(result.get('passed'))).lower()}`",
        f"- demo_next_step_ready: `{str(bool(result.get('demo_next_step_ready'))).lower()}`",
        f"- live_trading_allowed: `{str(bool(result.get('live_trading_allowed'))).lower()}`",
        f"- owner_approval_required: `{str(bool(result.get('owner_approval_required'))).lower()}`",
        f"- live_trading_requested: `{str(bool(result.get('live_trading_requested'))).lower()}`",
        f"- blockers: `{', '.join(blockers) if blockers else 'none'}`",
        f"- warnings: `{', '.join(warnings) if warnings else 'none'}`",
        f"- next_safe_action: {result.get('next_safe_action', '')}",
        "",
        "## Validation Commands",
        "- python -m py_compile automation/forex_engine/forex_profit_production_next_gate_v1.py tests/forex_engine/test_forex_profit_production_next_gate_v1.py",
        "- python -m pytest tests/forex_engine/test_forex_profit_production_next_gate_v1.py -q",
        "- git diff --check",
        "- python -m pytest tests/forex_engine -q",
        "",
        "## Validation Results",
        "- To be filled from the completed validation run.",
        "",
        "## Remaining Blockers",
        "- none in the gate logic itself when the supplied evidence passes the thresholds.",
        "",
        "## Owner Meaning In Plain English",
        "This does not go live. This decides whether the Forex work has enough practice/demo proof to move to owner review or supervised demo next step.",
        "",
        "## Final Git Status",
        "- To be filled from the final pre-stage git status.",
        "",
        "## Safe Next Action",
        f"- {result.get('next_safe_action', '')}",
        "",
    ]
    return "\n".join(lines)


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def _build_result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    next_safe_action: str,
    normalized_evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "status": status,
        "passed": status in READY_STATUSES,
        "blockers": list(blockers),
        "warnings": list(warnings),
        "next_safe_action": next_safe_action,
        "thresholds": dict(THRESHOLDS),
        "normalized_evidence": dict(normalized_evidence),
        "demo_next_step_ready": status in READY_STATUSES,
        "live_trading_allowed": False,
        "owner_approval_required": bool(normalized_evidence.get("owner_approval_required")),
        "live_trading_requested": bool(normalized_evidence.get("live_trading_requested")),
        "risk_controls_present": bool(normalized_evidence.get("risk_controls_present")),
        "risk_controls_passed": bool(normalized_evidence.get("risk_controls_passed")),
    }


def _warnings_for_status(
    status: str,
    *,
    missing_fields: list[str] | None = None,
) -> list[str]:
    warnings = ["This gate is read-only and never approves live trading."]
    if status == BLOCKED_MISSING_EVIDENCE:
        if missing_fields:
            warnings.append(
                "Missing or invalid evidence fields: " + ", ".join(missing_fields)
            )
        else:
            warnings.append("Evidence is missing or empty.")
        return warnings
    if status == BLOCKED_RISK_CONTROL_FAILURE:
        warnings.append("Risk controls must be present and passed before any further step.")
        return warnings
    if status == BLOCKED_INSUFFICIENT_SAMPLE:
        warnings.append(
            f"At least {MINIMUM_TOTAL_TRADES} trades are required before moving on."
        )
        return warnings
    if status == BLOCKED_NEGATIVE_EXPECTANCY:
        warnings.append("Expectancy must be greater than zero.")
        return warnings
    if status == BLOCKED_LOW_PROFIT_FACTOR:
        warnings.append(
            f"Profit factor must be at least {MINIMUM_PROFIT_FACTOR:.2f}."
        )
        return warnings
    if status == BLOCKED_EXCESSIVE_DRAWDOWN:
        warnings.append(f"Max drawdown must be at or below {MAXIMUM_DRAWDOWN_PCT:.2f}%.")
        return warnings
    if status == READY_FOR_OWNER_REVIEW:
        warnings.append("Owner review is the next step.")
        return warnings
    if status == READY_FOR_DEMO_ONLY_NEXT_STEP:
        warnings.append("Proceed only to the supervised demo-only next step.")
        return warnings
    return warnings


def _next_safe_action(status: str) -> str:
    if status == BLOCKED_MISSING_EVIDENCE:
        return "Provide the required evidence fields and rerun the read-only gate."
    if status == BLOCKED_RISK_CONTROL_FAILURE:
        return (
            "Fix the risk-control inputs or remove any live trading request, then rerun the read-only gate."
        )
    if status == BLOCKED_INSUFFICIENT_SAMPLE:
        return (
            f"Collect at least {MINIMUM_TOTAL_TRADES} trades, then rerun the read-only gate."
        )
    if status == BLOCKED_NEGATIVE_EXPECTANCY:
        return "Improve expectancy above zero, then rerun the read-only gate."
    if status == BLOCKED_LOW_PROFIT_FACTOR:
        return (
            f"Raise profit factor to at least {MINIMUM_PROFIT_FACTOR:.2f}, then rerun the read-only gate."
        )
    if status == BLOCKED_EXCESSIVE_DRAWDOWN:
        return (
            f"Reduce max drawdown to {MAXIMUM_DRAWDOWN_PCT:.2f}% or less, then rerun the read-only gate."
        )
    if status == READY_FOR_OWNER_REVIEW:
        return "Prepare the owner review packet; keep live trading blocked."
    if status == READY_FOR_DEMO_ONLY_NEXT_STEP:
        return "Proceed to the supervised demo-only next step; keep live trading blocked."
    return "Rerun the read-only gate with valid evidence."


def _normalize_evidence(evidence: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    normalized: dict[str, Any] = {}
    missing_fields: list[str] = []

    total_trades = _coerce_int(evidence.get("total_trades"))
    expectancy = _coerce_float(evidence.get("expectancy"))
    profit_factor = _coerce_float(evidence.get("profit_factor"))
    max_drawdown_pct = _coerce_float(evidence.get("max_drawdown_pct"))
    risk_controls_present = _coerce_bool(evidence.get("risk_controls_present"))
    risk_controls_passed = _coerce_bool(evidence.get("risk_controls_passed"))
    owner_approval_required = _coerce_bool(evidence.get("owner_approval_required"))
    live_trading_requested = _coerce_bool(evidence.get("live_trading_requested"))

    for field_name, value in (
        ("total_trades", total_trades),
        ("expectancy", expectancy),
        ("profit_factor", profit_factor),
        ("max_drawdown_pct", max_drawdown_pct),
        ("risk_controls_present", risk_controls_present),
        ("risk_controls_passed", risk_controls_passed),
        ("owner_approval_required", owner_approval_required),
        ("live_trading_requested", live_trading_requested),
    ):
        normalized[field_name] = value
        if value is None:
            missing_fields.append(field_name)

    return normalized, missing_fields


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _coerce_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(text)
        except ValueError:
            return None
    return None


def _coerce_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _coerce_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 0:
            return False
        if value == 1:
            return True
        return None
    if isinstance(value, str):
        text = value.strip().lower()
        if not text:
            return None
        if text in {"true", "1", "yes", "y", "on"}:
            return True
        if text in {"false", "0", "no", "n", "off"}:
            return False
    return None


__all__ = [
    "BLOCKED_EXCESSIVE_DRAWDOWN",
    "BLOCKED_INSUFFICIENT_SAMPLE",
    "BLOCKED_LOW_PROFIT_FACTOR",
    "BLOCKED_MISSING_EVIDENCE",
    "BLOCKED_NEGATIVE_EXPECTANCY",
    "BLOCKED_RISK_CONTROL_FAILURE",
    "MODE",
    "READY_FOR_DEMO_ONLY_NEXT_STEP",
    "READY_FOR_OWNER_REVIEW",
    "SCHEMA",
    "build_report_markdown",
    "evaluate_forex_profit_production_next_gate_v1",
    "result_to_jsonable_dict",
]
