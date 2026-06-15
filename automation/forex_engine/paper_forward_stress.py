from __future__ import annotations

from typing import Any

from automation.forex_engine import opportunity_capture
from automation.forex_engine import schema_contracts as schemas


ALLOWED_STRESS_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def default_stress_scenarios() -> list[dict[str, Any]]:
    return [
        _scenario("base"),
        _scenario("double_spread", spread_multiplier=2.0),
        _scenario("double_slippage", slippage_multiplier=2.0),
        _scenario("double_spread_double_slippage", spread_multiplier=2.0, slippage_multiplier=2.0),
        _scenario("half_capture_rate", capture_rate_multiplier=0.5),
        _scenario("minus_best_regime", remove_best_regime=True),
        _scenario("plus_drawdown_penalty", drawdown_penalty_pct=8.0),
        _scenario(
            "conservative_extreme",
            spread_multiplier=3.0,
            slippage_multiplier=3.0,
            capture_rate_multiplier=0.75,
            drawdown_penalty_pct=4.0,
        ),
        _scenario(
            "disaster_case",
            spread_multiplier=5.0,
            slippage_multiplier=5.0,
            capture_rate_multiplier=0.25,
            drawdown_penalty_pct=25.0,
        ),
    ]


def run_paper_forward_stress(
    evidence_bundle: dict[str, Any] | None = None,
    scenarios: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    bundle = dict(evidence_bundle or _build_default_evidence_bundle())
    report = opportunity_capture.calculate_opportunity_capture(bundle)
    active_scenarios = list(scenarios or default_stress_scenarios())
    scenario_results = [
        _stress_scenario_result(bundle, report, scenario)
        for scenario in active_scenarios
    ]
    result = {
        "schema": "AIOS_FOREX_PAPER_FORWARD_STRESS.v1",
        "mode": schemas.PAPER_ONLY,
        "scenario_count": len(scenario_results),
        "scenario_results": scenario_results,
        "scenarios": scenario_results,
        "estimated": True,
        "estimation_reason": (
            "Stress scenarios use deterministic local multipliers against paper-forward evidence; "
            "no broker, market API, network feed, or file input is used."
        ),
        "live_ready": False,
        "protected_gate_required": True,
        "safety": stress_boundary_summary(),
    }
    summary = summarize_stress_results(result)
    result["stress_summary"] = summary
    result["classification"] = summary["classification"]
    result["blockers"] = summary["blockers"]
    result["next_safe_action"] = _stress_next_safe_action(result["classification"], result["blockers"])
    schemas.assert_no_live_permissions(result)
    return result


def summarize_stress_results(result: dict[str, Any]) -> dict[str, Any]:
    scenarios = [dict(item) for item in list(result.get("scenario_results") or result.get("scenarios") or [])]
    scenario_count = len(scenarios)
    survived = [item for item in scenarios if item.get("classification") != "FAIL"]
    survived_pct = round((len(survived) / scenario_count) * 100.0, 4) if scenario_count else 0.0
    worst_pnl = min((float(item.get("pnl_after_stress", 0.0)) for item in scenarios), default=0.0)
    worst_return = min((float(item.get("return_pct_after_stress", 0.0)) for item in scenarios), default=0.0)
    blockers = _unique(
        [
            str(blocker)
            for scenario in scenarios
            for blocker in list(scenario.get("blockers") or [])
        ]
    )
    summary = {
        "schema": "AIOS_FOREX_PAPER_FORWARD_STRESS_SUMMARY.v1",
        "mode": result.get("mode", schemas.PAPER_ONLY),
        "scenario_count": scenario_count,
        "survived_scenarios": len(survived),
        "survived_scenarios_pct": survived_pct,
        "worst_stress_pnl": round(worst_pnl, 4),
        "worst_stress_return_pct": round(worst_return, 4),
        "blockers": blockers,
        "live_ready": False,
        "protected_gate_required": True,
    }
    summary["classification"] = classify_stress_survival({**result, "stress_summary": summary})
    summary["next_safe_action"] = _stress_next_safe_action(summary["classification"], blockers)
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_stress_survival(result: dict[str, Any]) -> str:
    payload = dict(result)
    if payload.get("classification") == "LIVE_READY" or payload.get("live_ready") is True:
        return "FAIL"
    scenarios = [dict(item) for item in list(payload.get("scenario_results") or payload.get("scenarios") or [])]
    if not scenarios:
        return "FAIL"
    if any(item.get("classification") not in ALLOWED_STRESS_CLASSIFICATIONS for item in scenarios):
        return "FAIL"
    non_disaster_failures = [
        item
        for item in scenarios
        if item.get("classification") == "FAIL" and item.get("scenario_id") != "disaster_case"
    ]
    if non_disaster_failures:
        return "FAIL"
    survived = sum(1 for item in scenarios if item.get("classification") != "FAIL")
    survived_pct = round((survived / len(scenarios)) * 100.0, 4)
    if survived_pct < 70.0:
        return "FAIL"
    if survived_pct < 100.0 or any(item.get("classification") == "WATCHLIST" for item in scenarios):
        return "WATCHLIST"
    return "PAPER_FORWARD_READY"


def stress_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_PAPER_FORWARD_STRESS_BOUNDARY.v1",
        "local_simulation_only": True,
        "broker_allowed": False,
        "broker_paper_orders": False,
        "network_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "live_trading": False,
        "live_ready": False,
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


def build_stress_oos_gate(
    stress_result: dict[str, Any],
    oos_result: dict[str, Any],
    risk_governor_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stress_summary = dict(stress_result.get("stress_summary") or summarize_stress_results(stress_result))
    oos_summary = dict(oos_result.get("oos_summary") or oos_result.get("summary") or {})
    stress_classification = str(stress_summary.get("classification") or "FAIL")
    oos_classification = str(oos_summary.get("classification") or oos_result.get("classification") or "FAIL")
    survived_pct = float(stress_summary.get("survived_scenarios_pct", 0.0))
    heldout_consistency_pct = float(oos_summary.get("heldout_consistency_pct", oos_result.get("heldout_consistency_pct", 0.0)))
    degradation_pct = float(oos_summary.get("degradation_pct", oos_result.get("degradation_pct", 100.0)))
    risk_classification = str(dict(risk_governor_result or {}).get("classification") or "PAPER_FORWARD_READY")
    blockers = _unique(
        [
            *[str(item) for item in list(stress_summary.get("blockers") or [])],
            *[str(item) for item in list(oos_summary.get("blockers") or oos_result.get("blockers") or [])],
        ]
    )
    combined = _combined_classification(
        stress_classification,
        oos_classification,
        risk_classification,
        survived_pct,
        heldout_consistency_pct,
        degradation_pct,
    )
    if combined != "PAPER_FORWARD_READY" and not blockers:
        blockers.append("stress_oos_gate_requires_more_resilience")
    gate = {
        "schema": "AIOS_FOREX_STRESS_OOS_COMBINED_GATE.v1",
        "mode": schemas.PAPER_ONLY,
        "stress_classification": stress_classification,
        "oos_classification": oos_classification,
        "risk_governor_classification": risk_classification,
        "combined_classification": combined,
        "survived_scenarios_pct": round(survived_pct, 4),
        "heldout_consistency_pct": round(heldout_consistency_pct, 4),
        "degradation_pct": round(degradation_pct, 4),
        "blockers": blockers,
        "next_safe_action": _combined_next_safe_action(combined, blockers),
        "broker_paper_sandbox_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": stress_boundary_summary(),
    }
    schemas.assert_no_live_permissions(gate)
    return gate


def _scenario(
    scenario_id: str,
    *,
    spread_multiplier: float = 1.0,
    slippage_multiplier: float = 1.0,
    capture_rate_multiplier: float = 1.0,
    drawdown_penalty_pct: float = 0.0,
    remove_best_regime: bool = False,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "spread_multiplier": spread_multiplier,
        "slippage_multiplier": slippage_multiplier,
        "capture_rate_multiplier": capture_rate_multiplier,
        "drawdown_penalty_pct": drawdown_penalty_pct,
        "remove_best_regime": remove_best_regime,
    }


def _stress_scenario_result(
    evidence_bundle: dict[str, Any],
    report: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    starting_balance = float(report.get("starting_balance", 500.0))
    base_pnl = float(report.get("aggregate_paper_pnl", 0.0))
    base_cost = float(report.get("cost_drag_usd", 0.0))
    spread_multiplier = float(scenario.get("spread_multiplier", 1.0))
    slippage_multiplier = float(scenario.get("slippage_multiplier", 1.0))
    capture_rate_multiplier = float(scenario.get("capture_rate_multiplier", 1.0))
    drawdown_penalty_pct = float(scenario.get("drawdown_penalty_pct", 0.0))
    cost_multiplier = max(1.0, spread_multiplier + slippage_multiplier - 1.0)
    stressed_cost = round(base_cost * cost_multiplier, 4)
    captured_pnl = base_pnl * capture_rate_multiplier
    regime_penalty = _best_regime_pnl(evidence_bundle) if scenario.get("remove_best_regime") else 0.0
    drawdown_penalty = starting_balance * (drawdown_penalty_pct / 100.0)
    pnl_after_stress = round(captured_pnl - stressed_cost - regime_penalty - drawdown_penalty, 4)
    return_pct = round((pnl_after_stress / starting_balance) * 100.0, 4) if starting_balance else 0.0
    cost_drag_pct = _cost_drag_pct(pnl_after_stress, stressed_cost)
    blockers = _stress_blockers(
        pnl_after_stress,
        return_pct,
        cost_drag_pct,
        capture_rate_multiplier,
        drawdown_penalty_pct,
        scenario,
    )
    classification = _scenario_classification(blockers, pnl_after_stress)
    result = {
        "scenario_id": str(scenario.get("scenario_id") or "unnamed"),
        "mode": schemas.PAPER_ONLY,
        "spread_multiplier": spread_multiplier,
        "slippage_multiplier": slippage_multiplier,
        "capture_rate_multiplier": capture_rate_multiplier,
        "pnl_after_stress": pnl_after_stress,
        "return_pct_after_stress": return_pct,
        "drawdown_penalty_pct": round(drawdown_penalty_pct, 4),
        "stressed_cost_usd": stressed_cost,
        "stressed_cost_drag_pct": cost_drag_pct,
        "removed_best_regime": bool(scenario.get("remove_best_regime", False)),
        "classification": classification,
        "blockers": blockers,
        "estimated": True,
        "live_ready": False,
        "protected_gate_required": True,
    }
    schemas.assert_no_live_permissions(result)
    return result


def _build_default_evidence_bundle() -> dict[str, Any]:
    from automation.forex_engine import paper_forward_evidence_v2

    return paper_forward_evidence_v2.build_paper_forward_evidence_v2()


def _best_regime_pnl(evidence_bundle: dict[str, Any]) -> float:
    strongest = dict(dict(evidence_bundle.get("regime_consistency") or {}).get("strongest_regime") or {})
    return max(0.0, float(strongest.get("aggregate_pnl", 0.0)))


def _cost_drag_pct(pnl_after_stress: float, stressed_cost: float) -> float:
    denominator = abs(float(pnl_after_stress)) + max(0.0, float(stressed_cost))
    return round((max(0.0, float(stressed_cost)) / denominator) * 100.0, 4) if denominator else 0.0


def _stress_blockers(
    pnl_after_stress: float,
    return_pct: float,
    cost_drag_pct: float,
    capture_rate_multiplier: float,
    drawdown_penalty_pct: float,
    scenario: dict[str, Any],
) -> list[str]:
    scenario_id = str(scenario.get("scenario_id") or "unnamed")
    blockers = []
    if pnl_after_stress <= 0.0:
        blockers.append(f"{scenario_id}:non_positive_stress_pnl")
    if return_pct <= 0.0:
        blockers.append(f"{scenario_id}:non_positive_stress_return")
    if cost_drag_pct > 25.0:
        blockers.append(f"{scenario_id}:cost_drag_exceeds_policy")
    if capture_rate_multiplier < 0.65:
        blockers.append(f"{scenario_id}:capture_rate_stress_below_policy")
    if drawdown_penalty_pct > 8.0:
        blockers.append(f"{scenario_id}:drawdown_penalty_exceeds_policy")
    return blockers


def _scenario_classification(blockers: list[str], pnl_after_stress: float) -> str:
    if pnl_after_stress <= 0.0:
        return "FAIL"
    if blockers:
        return "WATCHLIST"
    return "PAPER_FORWARD_READY"


def _combined_classification(
    stress_classification: str,
    oos_classification: str,
    risk_classification: str,
    survived_pct: float,
    heldout_consistency_pct: float,
    degradation_pct: float,
) -> str:
    classifications = {stress_classification, oos_classification, risk_classification}
    if "LIVE_READY" in classifications:
        return "FAIL"
    if "FAIL" in classifications:
        return "FAIL"
    if survived_pct < 80.0 or heldout_consistency_pct < 60.0 or degradation_pct > 35.0:
        return "WATCHLIST"
    if classifications == {"PAPER_FORWARD_READY"}:
        return "PAPER_FORWARD_READY"
    return "WATCHLIST"


def _stress_next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Run deterministic out-of-sample validation before any broker-paper sandbox readiness contract."
    if blockers:
        return "Review stress blockers and harden local evidence; broker and live paths remain blocked."
    return "Continue local stress evidence review; broker and live paths remain blocked."


def _combined_next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Prepare broker-paper sandbox readiness contract only; do not integrate broker or place orders."
    if blockers:
        return "Resolve stress/OOS blockers before broker-paper sandbox readiness is considered."
    return "Collect stronger deterministic stress and OOS evidence before protected promotion."


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
