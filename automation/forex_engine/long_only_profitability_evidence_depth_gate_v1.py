"""Long-only profitability evidence depth gate for demo preparation.

This gate checks deterministic, sanitized evidence sufficiency. It is not a
profit guarantee and it never reads market data, files, credentials, or broker
resources.
"""
from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any

from automation.forex_engine.forex_trust_safety_audit_v1 import contains_sensitive_material

PROFITABILITY_EVIDENCE_DEPTH_BLOCKED = "PROFITABILITY_EVIDENCE_DEPTH_BLOCKED"
PROFITABILITY_EVIDENCE_DEPTH_READY = "PROFITABILITY_EVIDENCE_DEPTH_READY"

DEFAULT_MIN_REQUIRED_TRADES = 30
DEFAULT_MIN_REQUIRED_WALK_FORWARD_FOLDS = 3
DEFAULT_MIN_REQUIRED_OUT_OF_SAMPLE_FOLDS = 3
DEFAULT_MIN_EXPECTANCY = 0.0
DEFAULT_MIN_PROFIT_FACTOR = 1.2

REQUIRED_EVIDENCE_FIELDS = (
    "candidate_id",
    "strategy_id",
    "instrument",
    "direction",
    "evidence_source",
    "evidence_timestamp",
    "sample_size",
    "closed_trades",
    "winning_trades",
    "losing_trades",
    "breakeven_trades",
    "expectancy",
    "profit_factor",
    "max_drawdown",
    "max_drawdown_allowed",
    "walk_forward_folds",
    "out_of_sample_folds",
    "out_of_sample_folds_passed",
    "min_required_trades",
    "min_required_walk_forward_folds",
    "min_required_out_of_sample_folds",
    "min_expectancy",
    "min_profit_factor",
    "negative_expectancy",
    "mitigation_worsened",
    "overfit_flag",
    "risk_gate_cleared",
    "evidence_gate_cleared",
    "long_only",
    "short_side_disabled",
    "sanitized_evidence_only",
)

NUMERIC_FIELDS = (
    "sample_size",
    "closed_trades",
    "winning_trades",
    "losing_trades",
    "breakeven_trades",
    "expectancy",
    "profit_factor",
    "max_drawdown",
    "max_drawdown_allowed",
    "walk_forward_folds",
    "out_of_sample_folds",
    "out_of_sample_folds_passed",
    "min_required_trades",
    "min_required_walk_forward_folds",
    "min_required_out_of_sample_folds",
    "min_expectancy",
    "min_profit_factor",
)


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y", "on", "pass", "passed", "ready"}:
            return True
        if text in {"false", "0", "no", "n", "off", "fail", "failed", "blocked"}:
            return False
    return bool(value)


def _finite_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _thresholds(evidence: Mapping[str, Any], thresholds: Mapping[str, Any] | None) -> dict[str, float]:
    source = dict(thresholds or {})
    return {
        "min_required_trades": _finite_number(source.get("min_required_trades", evidence.get("min_required_trades")))
        or DEFAULT_MIN_REQUIRED_TRADES,
        "min_required_walk_forward_folds": _finite_number(
            source.get("min_required_walk_forward_folds", evidence.get("min_required_walk_forward_folds"))
        )
        or DEFAULT_MIN_REQUIRED_WALK_FORWARD_FOLDS,
        "min_required_out_of_sample_folds": _finite_number(
            source.get("min_required_out_of_sample_folds", evidence.get("min_required_out_of_sample_folds"))
        )
        or DEFAULT_MIN_REQUIRED_OUT_OF_SAMPLE_FOLDS,
        "min_expectancy": _finite_number(source.get("min_expectancy", evidence.get("min_expectancy")))
        if _finite_number(source.get("min_expectancy", evidence.get("min_expectancy"))) is not None
        else DEFAULT_MIN_EXPECTANCY,
        "min_profit_factor": _finite_number(source.get("min_profit_factor", evidence.get("min_profit_factor")))
        or DEFAULT_MIN_PROFIT_FACTOR,
    }


def _blocked_result(
    evidence: Mapping[str, Any] | None,
    blockers: list[str],
    thresholds: Mapping[str, Any],
) -> dict[str, Any]:
    payload = evidence if isinstance(evidence, Mapping) else {}
    return {
        "status": PROFITABILITY_EVIDENCE_DEPTH_BLOCKED,
        "ready": False,
        "candidate_id": payload.get("candidate_id"),
        "strategy_id": payload.get("strategy_id"),
        "instrument": payload.get("instrument"),
        "direction": payload.get("direction"),
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": [],
        "metrics": {},
        "thresholds": dict(thresholds),
        "evidence_depth_ready_for_demo_preparation": False,
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "next_safe_action": "repair_long_only_profitability_evidence_depth",
    }


def evaluate_long_only_profitability_evidence_depth(
    candidate_evidence: Mapping[str, Any] | None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate whether sanitized long-only evidence is deep enough to advance."""
    blockers: list[str] = []
    if not isinstance(candidate_evidence, Mapping) or not candidate_evidence:
        blockers.append("missing_candidate_evidence")
        return _blocked_result(None, blockers, _thresholds({}, thresholds))

    evidence = dict(candidate_evidence)
    gate_thresholds = _thresholds(evidence, thresholds)

    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in evidence:
            blockers.append(f"missing_required_field:{field}")

    for field in NUMERIC_FIELDS:
        if field in evidence and _finite_number(evidence.get(field)) is None:
            blockers.append(f"invalid_numeric_field:{field}")

    if contains_sensitive_material(evidence):
        blockers.append("sensitive_material_detected")

    if str(evidence.get("direction", "")).strip().upper() != "LONG":
        blockers.append("direction_not_long")
    if not _to_bool(evidence.get("long_only")):
        blockers.append("long_only_not_confirmed")
    if not _to_bool(evidence.get("short_side_disabled")):
        blockers.append("short_side_not_disabled")
    if not _to_bool(evidence.get("sanitized_evidence_only")):
        blockers.append("sanitized_evidence_only_not_confirmed")
    if not _to_bool(evidence.get("risk_gate_cleared")):
        blockers.append("risk_gate_not_cleared")
    if not _to_bool(evidence.get("evidence_gate_cleared")):
        blockers.append("evidence_gate_not_cleared")

    sample_size = _finite_number(evidence.get("sample_size"))
    closed_trades = _finite_number(evidence.get("closed_trades"))
    expectancy = _finite_number(evidence.get("expectancy"))
    profit_factor = _finite_number(evidence.get("profit_factor"))
    max_drawdown = _finite_number(evidence.get("max_drawdown"))
    max_drawdown_allowed = _finite_number(evidence.get("max_drawdown_allowed"))
    walk_forward_folds = _finite_number(evidence.get("walk_forward_folds"))
    out_of_sample_folds = _finite_number(evidence.get("out_of_sample_folds"))
    out_of_sample_folds_passed = _finite_number(evidence.get("out_of_sample_folds_passed"))

    if sample_size is None or sample_size < gate_thresholds["min_required_trades"]:
        blockers.append("insufficient_sample_size")
    if closed_trades is None or closed_trades < gate_thresholds["min_required_trades"]:
        blockers.append("insufficient_closed_trades")
    if expectancy is None or expectancy <= gate_thresholds["min_expectancy"]:
        blockers.append("expectancy_not_above_threshold")
    if profit_factor is None or profit_factor < gate_thresholds["min_profit_factor"]:
        blockers.append("profit_factor_below_threshold")
    if max_drawdown is None or max_drawdown_allowed is None or max_drawdown > max_drawdown_allowed:
        blockers.append("max_drawdown_above_allowed")
    if walk_forward_folds is None or walk_forward_folds < gate_thresholds["min_required_walk_forward_folds"]:
        blockers.append("insufficient_walk_forward_folds")
    if out_of_sample_folds is None or out_of_sample_folds < gate_thresholds["min_required_out_of_sample_folds"]:
        blockers.append("insufficient_out_of_sample_folds")
    if (
        out_of_sample_folds_passed is None
        or out_of_sample_folds_passed < gate_thresholds["min_required_out_of_sample_folds"]
    ):
        blockers.append("insufficient_out_of_sample_folds_passed")

    if _to_bool(evidence.get("negative_expectancy")):
        blockers.append("negative_expectancy")
    if _to_bool(evidence.get("mitigation_worsened")):
        blockers.append("mitigation_worsened")
    if _to_bool(evidence.get("overfit_flag")):
        blockers.append("overfit_flag")

    blockers = list(dict.fromkeys(blockers))
    if blockers:
        return _blocked_result(evidence, blockers, gate_thresholds)

    metrics = {
        "sample_size": sample_size,
        "closed_trades": closed_trades,
        "winning_trades": _finite_number(evidence.get("winning_trades")),
        "losing_trades": _finite_number(evidence.get("losing_trades")),
        "breakeven_trades": _finite_number(evidence.get("breakeven_trades")),
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "max_drawdown_allowed": max_drawdown_allowed,
        "walk_forward_folds": walk_forward_folds,
        "out_of_sample_folds": out_of_sample_folds,
        "out_of_sample_folds_passed": out_of_sample_folds_passed,
    }
    return {
        "status": PROFITABILITY_EVIDENCE_DEPTH_READY,
        "ready": True,
        "candidate_id": evidence.get("candidate_id"),
        "strategy_id": evidence.get("strategy_id"),
        "instrument": evidence.get("instrument"),
        "direction": "LONG",
        "blockers": [],
        "warnings": [],
        "metrics": metrics,
        "thresholds": gate_thresholds,
        "evidence_depth_ready_for_demo_preparation": True,
        "execution_allowed": False,
        "ready_to_execute": False,
        "demo_order_allowed": False,
        "live_autonomy_allowed": False,
        "next_safe_action": "continue_to_demo_preparation_risk_policy_contract",
    }
