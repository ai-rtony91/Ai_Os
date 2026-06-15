from __future__ import annotations

from typing import Any

from automation.forex_engine import opportunity_capture
from automation.forex_engine import schema_contracts as schemas


ALLOWED_GOVERNOR_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def default_risk_governor_policy() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_RISK_GOVERNOR_POLICY.v1",
        "mode": schemas.PAPER_ONLY,
        "starting_balance": 500.0,
        "estimated_round_turn_cost_usd": opportunity_capture.DEFAULT_ESTIMATED_ROUND_TURN_COST_USD,
        "minimum_fixture_count": 9,
        "minimum_regime_count": 7,
        "minimum_total_intents": 50,
        "minimum_total_ledger_entries": 50,
        "minimum_consistency_pct": 70.0,
        "minimum_capture_rate_pct": 65.0,
        "minimum_risk_adjusted_return": 0.10,
        "maximum_drawdown_pct": 8.0,
        "maximum_cost_drag_pct": 25.0,
        "maximum_missed_pnl_pct": 35.0,
        "maximum_overtrade_ratio": 1.50,
        "minimum_exit_efficiency_pct": 50.0,
        "minimum_opportunity_quality_score": 60.0,
        "require_protected_gate_for_live": True,
        "live_ready_always_false": True,
    }


def evaluate_risk_governor_thresholds(
    evidence_bundle: dict[str, Any],
    opportunity_report: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_policy = default_risk_governor_policy()
    active_policy.update(dict(policy or {}))
    report = opportunity_report or opportunity_capture.calculate_opportunity_capture(evidence_bundle, active_policy)
    evidence_summary = _evidence_summary(evidence_bundle)
    threshold_results = _threshold_results(evidence_summary, report, active_policy)
    failed_thresholds = [
        name for name, result in threshold_results.items() if result["passed"] is not True
    ]
    passed_thresholds = [
        name for name, result in threshold_results.items() if result["passed"] is True
    ]
    result = {
        "schema": "AIOS_FOREX_RISK_GOVERNOR_THRESHOLD_RESULT.v1",
        "mode": schemas.PAPER_ONLY,
        "policy": active_policy,
        "threshold_results": threshold_results,
        "passed_thresholds": passed_thresholds,
        "failed_thresholds": failed_thresholds,
        "blockers": [f"threshold_failed:{name}" for name in failed_thresholds],
        "opportunity_capture": report,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": risk_governor_boundary_summary(),
    }
    result["classification"] = classify_risk_governor(result)
    result["next_safe_action"] = _next_safe_action(result["classification"], failed_thresholds)
    assert_live_blocked(result)
    return result


def classify_risk_governor(result: dict[str, Any]) -> str:
    payload = dict(result)
    if payload.get("classification") == "LIVE_READY" or payload.get("live_ready") is True:
        return "FAIL"
    failed_thresholds = list(payload.get("failed_thresholds") or [])
    if not failed_thresholds:
        return "PAPER_FORWARD_READY"
    severe = {
        "minimum_fixture_count",
        "minimum_regime_count",
        "minimum_total_ledger_entries",
        "maximum_drawdown_pct",
        "maximum_cost_drag_pct",
    }
    if severe.intersection(failed_thresholds):
        return "FAIL"
    return "WATCHLIST"


def risk_governor_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_RISK_GOVERNOR_BOUNDARY.v1",
        "local_simulation_only": True,
        "broker_allowed": False,
        "broker_paper_orders": False,
        "network_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "live_trading": False,
        "live_ready": False,
        "live_order": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "protected_gate_required": True,
        "reports_written": False,
        "files_written": [],
    }


def assert_live_blocked(result: dict[str, Any]) -> None:
    if result.get("classification") == "LIVE_READY":
        raise ValueError("Risk governor must never emit LIVE_READY")
    if result.get("classification") not in ALLOWED_GOVERNOR_CLASSIFICATIONS:
        raise ValueError("Risk governor classification must be FAIL, WATCHLIST, or PAPER_FORWARD_READY")
    if result.get("live_ready") is not False:
        raise ValueError("Risk governor live_ready must always be false")
    if result.get("protected_gate_required") is not True:
        raise ValueError("Risk governor must require a protected downstream gate")
    schemas.assert_no_live_permissions(result)


def run_cost_stress_scenarios(
    evidence_bundle: dict[str, Any],
    scenarios: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    active_policy = default_risk_governor_policy()
    base_report = opportunity_capture.calculate_opportunity_capture(evidence_bundle, active_policy)
    active_scenarios = scenarios or [
        {"scenario": "base", "cost_multiplier": 1.0},
        {"scenario": "double_spread", "cost_multiplier": 2.0},
        {"scenario": "double_slippage", "cost_multiplier": 2.0},
        {"scenario": "double_spread_double_slippage", "cost_multiplier": 4.0},
        {"scenario": "conservative_extreme", "cost_multiplier": 5.0},
    ]
    results = [
        _stress_scenario_result(base_report, scenario, active_policy)
        for scenario in active_scenarios
    ]
    bundle = {
        "schema": "AIOS_FOREX_RISK_GOVERNOR_COST_STRESS.v1",
        "mode": schemas.PAPER_ONLY,
        "scenarios": results,
        "scenario_results": results,
        "estimated": True,
        "estimation_reason": "Stress scenarios use deterministic local cost multipliers; no broker or network data is used.",
        "live_ready": False,
        "protected_gate_required": True,
        "safety": risk_governor_boundary_summary(),
    }
    schemas.assert_no_live_permissions(bundle)
    return bundle


def _evidence_summary(evidence_bundle: dict[str, Any]) -> dict[str, Any]:
    multi_summary = dict(evidence_bundle.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(evidence_bundle.get("regime_consistency") or {})
    return {
        "fixture_count": int(multi_summary.get("fixture_count", 0)),
        "regime_count": int(regime.get("total_regimes", 0)),
        "total_intents": int(multi_summary.get("total_intents", 0)),
        "total_ledger_entries": int(multi_summary.get("total_ledger_entries", 0)),
        "consistency_pct": float(multi_summary.get("consistency_pct", 0.0)),
    }


def _threshold_results(
    evidence_summary: dict[str, Any],
    report: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    checks = {
        "minimum_fixture_count": _minimum(evidence_summary["fixture_count"], policy["minimum_fixture_count"]),
        "minimum_regime_count": _minimum(evidence_summary["regime_count"], policy["minimum_regime_count"]),
        "minimum_total_intents": _minimum(evidence_summary["total_intents"], policy["minimum_total_intents"]),
        "minimum_total_ledger_entries": _minimum(
            evidence_summary["total_ledger_entries"],
            policy["minimum_total_ledger_entries"],
        ),
        "minimum_consistency_pct": _minimum(evidence_summary["consistency_pct"], policy["minimum_consistency_pct"]),
        "minimum_capture_rate_pct": _minimum(report["capture_rate_pct"], policy["minimum_capture_rate_pct"]),
        "minimum_risk_adjusted_return": _minimum(
            report["risk_adjusted_return"],
            policy["minimum_risk_adjusted_return"],
        ),
        "maximum_drawdown_pct": _maximum(report["max_drawdown_pct"], policy["maximum_drawdown_pct"]),
        "maximum_cost_drag_pct": _maximum(report["cost_drag_pct"], policy["maximum_cost_drag_pct"]),
        "maximum_missed_pnl_pct": _maximum(report["missed_pnl_pct"], policy["maximum_missed_pnl_pct"]),
        "maximum_overtrade_ratio": _maximum(report["overtrade_ratio"], policy["maximum_overtrade_ratio"]),
        "minimum_exit_efficiency_pct": _minimum(
            report["exit_efficiency_pct"],
            policy["minimum_exit_efficiency_pct"],
        ),
        "minimum_opportunity_quality_score": _minimum(
            report["opportunity_quality_score"],
            policy["minimum_opportunity_quality_score"],
        ),
    }
    return checks


def _minimum(actual: float, threshold: float) -> dict[str, Any]:
    return {
        "passed": float(actual) >= float(threshold),
        "actual": round(float(actual), 4),
        "threshold": round(float(threshold), 4),
        "comparator": ">=",
    }


def _maximum(actual: float, threshold: float) -> dict[str, Any]:
    return {
        "passed": float(actual) <= float(threshold),
        "actual": round(float(actual), 4),
        "threshold": round(float(threshold), 4),
        "comparator": "<=",
    }


def _stress_scenario_result(
    base_report: dict[str, Any],
    scenario: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    multiplier = float(scenario.get("cost_multiplier", 1.0))
    starting_balance = float(base_report["starting_balance"])
    base_pnl = float(base_report["aggregate_paper_pnl"])
    stressed_cost = round(float(base_report["cost_drag_usd"]) * multiplier, 4)
    stressed_pnl = round(base_pnl - stressed_cost, 4)
    return_pct = round((stressed_pnl / starting_balance) * 100, 4) if starting_balance else 0.0
    denominator = abs(stressed_pnl) + stressed_cost
    cost_drag_pct = round((stressed_cost / denominator) * 100, 4) if denominator else 0.0
    blockers = []
    if stressed_pnl <= 0:
        blockers.append("stress_scenario_non_positive_pnl")
    if cost_drag_pct > float(policy["maximum_cost_drag_pct"]):
        blockers.append("stress_scenario_cost_drag_excessive")
    classification = "PAPER_FORWARD_READY" if not blockers else "WATCHLIST"
    if stressed_pnl <= 0:
        classification = "FAIL"
    result = {
        "scenario": str(scenario.get("scenario", "unnamed")),
        "mode": schemas.PAPER_ONLY,
        "aggregate_paper_pnl": stressed_pnl,
        "return_pct": return_pct,
        "cost_drag_usd": stressed_cost,
        "cost_drag_pct": cost_drag_pct,
        "classification": classification,
        "blockers": blockers,
        "estimated": True,
        "live_ready": False,
        "protected_gate_required": True,
    }
    schemas.assert_no_live_permissions(result)
    return result


def _next_safe_action(classification: str, failed_thresholds: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Advance to protected stress and out-of-sample paper-forward validation; live trading remains blocked."
    if failed_thresholds:
        return f"Improve threshold: {failed_thresholds[0]}; keep broker and live trading blocked."
    return "Review risk-governor evidence locally; no broker or live path is approved."
