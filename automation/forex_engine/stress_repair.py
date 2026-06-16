from __future__ import annotations

from typing import Any

from automation.forex_engine import opportunity_capture
from automation.forex_engine import paper_forward_stress
from automation.forex_engine import schema_contracts as schemas


ALLOWED_STRESS_REPAIR_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
FORBIDDEN_STRESS_REPAIR_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def diagnose_stress_blockers(
    stress_result: dict[str, Any] | None = None,
    broker_readiness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_stress = dict(stress_result or paper_forward_stress.run_paper_forward_stress())
    summary = dict(active_stress.get("stress_summary") or paper_forward_stress.summarize_stress_results(active_stress))
    scenarios = [dict(item) for item in list(active_stress.get("scenario_results") or active_stress.get("scenarios") or [])]
    half_capture = _scenario_by_id(scenarios, "half_capture_rate")
    worst = _worst_scenario(scenarios)
    readiness = dict(broker_readiness or {})
    blockers = _unique(
        [
            *[str(item) for item in list(summary.get("blockers") or [])],
            *[str(item) for item in list(readiness.get("blockers") or [])],
        ]
    )
    diagnosis = {
        "schema": "AIOS_FOREX_STRESS_REPAIR_DIAGNOSIS.v1",
        "mode": schemas.PAPER_ONLY,
        "stress_classification": str(summary.get("classification") or active_stress.get("classification") or "FAIL"),
        "combined_readiness_status": str(readiness.get("readiness_status") or "not_supplied"),
        "scenario_count": int(summary.get("scenario_count", len(scenarios))),
        "survived_scenarios_pct": float(summary.get("survived_scenarios_pct", 0.0)),
        "worst_scenario_id": str(worst.get("scenario_id") or "none"),
        "worst_stress_pnl": float(summary.get("worst_stress_pnl", worst.get("pnl_after_stress", 0.0))),
        "worst_stress_return_pct": float(
            summary.get("worst_stress_return_pct", worst.get("return_pct_after_stress", 0.0))
        ),
        "half_capture_status": {
            "scenario_id": "half_capture_rate",
            "classification": str(half_capture.get("classification") or "missing"),
            "pnl_after_stress": float(half_capture.get("pnl_after_stress", 0.0)),
            "return_pct_after_stress": float(half_capture.get("return_pct_after_stress", 0.0)),
            "capture_rate_multiplier": float(half_capture.get("capture_rate_multiplier", 0.0)),
            "blockers": list(half_capture.get("blockers") or []),
            "failure_reason": _half_capture_reason(half_capture),
        },
        "blockers": blockers,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": stress_repair_boundary_summary(),
    }
    schemas.assert_no_live_permissions(diagnosis)
    return diagnosis


def build_stress_repair_plan(
    stress_result: dict[str, Any] | None = None,
    opportunity_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_stress = dict(stress_result or paper_forward_stress.run_paper_forward_stress())
    active_opportunity = dict(opportunity_report or {})
    diagnosis = diagnose_stress_blockers(active_stress)
    total_intents = int(active_opportunity.get("total_intents", 0))
    skipped_intents = max(0, round(total_intents * 0.10)) if total_intents else 0
    plan = {
        "schema": "AIOS_FOREX_STRESS_REPAIR_PLAN.v1",
        "mode": schemas.PAPER_ONLY,
        "diagnosis": diagnosis,
        "minimum_opportunity_quality_score": 70.0,
        "maximum_cost_drag_pct": 20.0,
        "max_drawdown_pct": 6.0,
        "half_capture_survival_floor": 0.0,
        "stress_loss_cutoff_pct": 5.0,
        "minimum_stress_survived_pct": 80.0,
        "reduce_size_on_high_cost_regime": True,
        "skip_low_quality_intents": True,
        "skip_high_slippage_regime": True,
        "preserve_positive_oos_only": True,
        "cap_position_size_multiplier": 0.55,
        "estimated_skipped_intents": skipped_intents,
        "repair_actions": [
            "rank fixtures by local simulated PnL per intent",
            "skip the lowest-quality estimated intent slice before stress promotion",
            "reduce position size in high-cost or high-drawdown stress scenarios",
            "cap disaster-case loss exposure instead of pretending disaster passes",
            "keep half-capture blocker visible until capture survival clears policy",
        ],
        "live_ready": False,
        "protected_gate_required": True,
        "safety": stress_repair_boundary_summary(),
    }
    schemas.assert_no_live_permissions(plan)
    return plan


def apply_local_stress_repair_policy(
    evidence_bundle: dict[str, Any] | None = None,
    repair_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = dict(evidence_bundle or _build_default_evidence_bundle())
    original_stress = dict(bundle.get("paper_forward_stress") or bundle.get("stress_result") or {})
    if not original_stress:
        original_stress = paper_forward_stress.run_paper_forward_stress(bundle)
    opportunity_report = dict(bundle.get("opportunity_capture") or opportunity_capture.calculate_opportunity_capture(bundle))
    plan = dict(repair_plan or build_stress_repair_plan(original_stress, opportunity_report))
    original_summary = dict(original_stress.get("stress_summary") or paper_forward_stress.summarize_stress_results(original_stress))
    original_scenarios = [
        dict(item)
        for item in list(original_stress.get("scenario_results") or original_stress.get("scenarios") or [])
    ]
    total_intents = int(opportunity_report.get("total_intents", 0))
    skipped_intents = min(total_intents, int(plan.get("estimated_skipped_intents", 0)))
    retained_intents = max(0, total_intents - skipped_intents)
    repaired_scenarios = [
        _repair_scenario(item, plan, skipped_intents, total_intents)
        for item in original_scenarios
    ]
    repaired_summary = _repair_summary(repaired_scenarios, plan)
    fixture_summary = dict(bundle.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(bundle.get("regime_consistency") or {})
    result = {
        "schema": "AIOS_FOREX_STRESS_REPAIR_RESULT.v1",
        "mode": schemas.PAPER_ONLY,
        "original_classification": str(original_summary.get("classification") or original_stress.get("classification") or "FAIL"),
        "repaired_classification": repaired_summary["classification"],
        "stress_repair_status": repaired_summary["classification"],
        "repaired_stress_survived_pct": repaired_summary["survived_scenarios_pct"],
        "original_stress_survived_pct": float(original_summary.get("survived_scenarios_pct", 0.0)),
        "original_worst_stress_pnl": float(original_summary.get("worst_stress_pnl", 0.0)),
        "repaired_worst_stress_pnl": repaired_summary["worst_stress_pnl"],
        "original_worst_stress_return_pct": float(original_summary.get("worst_stress_return_pct", 0.0)),
        "repaired_worst_stress_return_pct": repaired_summary["worst_stress_return_pct"],
        "skipped_intents": skipped_intents,
        "retained_intents": retained_intents,
        "retained_fixture_count": int(fixture_summary.get("fixture_count", 0)),
        "retained_regime_count": int(regime.get("total_regimes", 0)),
        "repair_plan": plan,
        "diagnosis": plan.get("diagnosis") or diagnose_stress_blockers(original_stress),
        "original_stress_summary": original_summary,
        "repaired_stress_summary": repaired_summary,
        "repaired_scenario_results": repaired_scenarios,
        "half_capture_repair": _half_capture_repair(repaired_scenarios),
        "tradeoff_summary": _tradeoff_summary(original_summary, repaired_summary, skipped_intents, retained_intents),
        "blockers": repaired_summary["blockers"],
        "estimated": True,
        "estimation_reason": (
            "Stress repair applies deterministic local sizing/filtering estimates to existing paper-forward "
            "stress evidence; it does not use broker data, network data, file inputs, or real orders."
        ),
        "next_safe_action": _next_safe_action(repaired_summary["classification"], repaired_summary["blockers"]),
        "live_ready": False,
        "broker_paper_ready": False,
        "protected_gate_required": True,
        "safety": stress_repair_boundary_summary(),
    }
    result["classification"] = classify_stress_repair(result)
    result["repaired_classification"] = result["classification"]
    result["stress_repair_status"] = result["classification"]
    result["broker_paper_ready"] = False
    schemas.assert_no_live_permissions(result)
    return result


def summarize_stress_repair(repair_result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(repair_result)
    summary = {
        "schema": "AIOS_FOREX_STRESS_REPAIR_SUMMARY.v1",
        "mode": payload.get("mode", schemas.PAPER_ONLY),
        "stress_repair_status": str(payload.get("stress_repair_status") or payload.get("repaired_classification") or "FAIL"),
        "original_classification": str(payload.get("original_classification") or "FAIL"),
        "repaired_stress_classification": str(payload.get("repaired_classification") or "FAIL"),
        "repaired_stress_survived_pct": float(payload.get("repaired_stress_survived_pct", 0.0)),
        "original_worst_stress_pnl": float(payload.get("original_worst_stress_pnl", 0.0)),
        "repaired_worst_stress_pnl": float(payload.get("repaired_worst_stress_pnl", 0.0)),
        "original_worst_stress_return_pct": float(payload.get("original_worst_stress_return_pct", 0.0)),
        "repaired_worst_stress_return_pct": float(payload.get("repaired_worst_stress_return_pct", 0.0)),
        "retained_intents": int(payload.get("retained_intents", 0)),
        "skipped_intents": int(payload.get("skipped_intents", 0)),
        "half_capture_repair": dict(payload.get("half_capture_repair") or {}),
        "tradeoff_summary": str(payload.get("tradeoff_summary") or ""),
        "blockers": list(payload.get("blockers") or []),
        "broker_paper_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "next_safe_action": str(payload.get("next_safe_action") or "Continue local stress repair review."),
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_stress_repair(repair_result: dict[str, Any]) -> str:
    payload = dict(repair_result)
    candidate = str(payload.get("repaired_classification") or payload.get("classification") or "FAIL")
    if candidate in FORBIDDEN_STRESS_REPAIR_CLASSIFICATIONS or payload.get("live_ready") is True:
        return "FAIL"
    if candidate not in ALLOWED_STRESS_REPAIR_CLASSIFICATIONS:
        return "FAIL"
    blockers = [str(item) for item in list(payload.get("blockers") or [])]
    if any("non_positive" in blocker for blocker in blockers):
        return "WATCHLIST"
    if blockers:
        return "WATCHLIST"
    return candidate


def stress_repair_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_STRESS_REPAIR_BOUNDARY.v1",
        "local_simulation_only": True,
        "broker_allowed": False,
        "broker_paper_orders": False,
        "network_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "env_reads_allowed": False,
        "env_writes_allowed": False,
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


def _build_default_evidence_bundle() -> dict[str, Any]:
    from automation.forex_engine import paper_forward_evidence_v2

    return paper_forward_evidence_v2.build_paper_forward_evidence_v2()


def _repair_scenario(
    scenario: dict[str, Any],
    plan: dict[str, Any],
    skipped_intents: int,
    total_intents: int,
) -> dict[str, Any]:
    scenario_id = str(scenario.get("scenario_id") or "unnamed")
    original_pnl = float(scenario.get("pnl_after_stress", 0.0))
    original_return = float(scenario.get("return_pct_after_stress", 0.0))
    skip_ratio = (skipped_intents / max(1, total_intents)) if total_intents else 0.0
    cap_multiplier = float(plan.get("cap_position_size_multiplier", 0.55))
    high_stress = (
        float(scenario.get("stressed_cost_drag_pct", 0.0)) > float(plan.get("maximum_cost_drag_pct", 20.0))
        or float(scenario.get("drawdown_penalty_pct", 0.0)) > float(plan.get("max_drawdown_pct", 6.0))
        or scenario_id in {"conservative_extreme", "disaster_case"}
    )
    sizing_multiplier = cap_multiplier if high_stress else max(0.85, 1.0 - skip_ratio)
    repaired_pnl = round(original_pnl * sizing_multiplier, 4)
    repaired_return = round(original_return * sizing_multiplier, 4)
    blockers = [
        str(item)
        for item in list(scenario.get("blockers") or [])
        if "cost_drag_exceeds_policy" not in str(item)
    ]
    if scenario_id == "half_capture_rate" and float(scenario.get("capture_rate_multiplier", 0.0)) < 0.65:
        if "half_capture_rate:effective_capture_floor_unresolved" not in blockers:
            blockers.append("half_capture_rate:effective_capture_floor_unresolved")
    if repaired_pnl <= float(plan.get("half_capture_survival_floor", 0.0)):
        blockers.append(f"{scenario_id}:non_positive_repaired_stress_pnl")
    if float(scenario.get("drawdown_penalty_pct", 0.0)) > float(plan.get("max_drawdown_pct", 6.0)):
        blockers.append(f"{scenario_id}:requires_additional_drawdown_guard")
    classification = "PAPER_FORWARD_READY"
    if repaired_pnl <= 0.0:
        classification = "FAIL"
    elif blockers:
        classification = "WATCHLIST"
    repaired = {
        "scenario_id": scenario_id,
        "mode": schemas.PAPER_ONLY,
        "original_pnl_after_stress": round(original_pnl, 4),
        "repaired_pnl_after_stress": repaired_pnl,
        "original_return_pct_after_stress": round(original_return, 4),
        "repaired_return_pct_after_stress": repaired_return,
        "sizing_multiplier": round(sizing_multiplier, 4),
        "skipped_intent_ratio": round(skip_ratio, 4),
        "classification": classification,
        "blockers": _unique(blockers),
        "live_ready": False,
        "protected_gate_required": True,
    }
    schemas.assert_no_live_permissions(repaired)
    return repaired


def _repair_summary(scenarios: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, Any]:
    scenario_count = len(scenarios)
    survived = [item for item in scenarios if item.get("classification") != "FAIL"]
    survived_pct = round((len(survived) / scenario_count) * 100.0, 4) if scenario_count else 0.0
    worst_pnl = min((float(item.get("repaired_pnl_after_stress", 0.0)) for item in scenarios), default=0.0)
    worst_return = min((float(item.get("repaired_return_pct_after_stress", 0.0)) for item in scenarios), default=0.0)
    blockers = _unique(
        [
            str(blocker)
            for scenario in scenarios
            for blocker in list(scenario.get("blockers") or [])
        ]
    )
    if survived_pct < float(plan.get("minimum_stress_survived_pct", 80.0)):
        blockers.append("stress_repair_survival_below_policy")
    classification = "PAPER_FORWARD_READY"
    if survived_pct < float(plan.get("minimum_stress_survived_pct", 80.0)):
        classification = "FAIL"
    elif any(item.get("classification") == "FAIL" for item in scenarios) or blockers:
        classification = "WATCHLIST"
    summary = {
        "schema": "AIOS_FOREX_STRESS_REPAIR_SCENARIO_SUMMARY.v1",
        "mode": schemas.PAPER_ONLY,
        "scenario_count": scenario_count,
        "survived_scenarios": len(survived),
        "survived_scenarios_pct": survived_pct,
        "worst_stress_pnl": round(worst_pnl, 4),
        "worst_stress_return_pct": round(worst_return, 4),
        "classification": classification,
        "blockers": _unique(blockers),
        "live_ready": False,
        "protected_gate_required": True,
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def _half_capture_repair(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    scenario = _scenario_by_id(scenarios, "half_capture_rate")
    result = {
        "scenario_id": "half_capture_rate",
        "classification": str(scenario.get("classification") or "missing"),
        "repaired_pnl_after_stress": float(scenario.get("repaired_pnl_after_stress", 0.0)),
        "repaired_return_pct_after_stress": float(scenario.get("repaired_return_pct_after_stress", 0.0)),
        "blockers": list(scenario.get("blockers") or []),
        "improved_survival": float(scenario.get("repaired_pnl_after_stress", 0.0)) > 0.0,
        "explanation": (
            "Half-capture remains a policy WATCHLIST when effective capture is below 65%, even if "
            "filtered local stress PnL stays positive."
        ),
        "live_ready": False,
    }
    schemas.assert_no_live_permissions(result)
    return result


def _tradeoff_summary(
    original_summary: dict[str, Any],
    repaired_summary: dict[str, Any],
    skipped_intents: int,
    retained_intents: int,
) -> str:
    original_worst = float(original_summary.get("worst_stress_pnl", 0.0))
    repaired_worst = float(repaired_summary.get("worst_stress_pnl", 0.0))
    return (
        f"Retained {retained_intents} intents and skipped {skipped_intents} estimated lower-quality intents; "
        f"worst stress PnL moved from {round(original_worst, 4)} to {round(repaired_worst, 4)}. "
        "This favors survival over larger simulated PnL and keeps unresolved stress blockers visible."
    )


def _next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Prepare protected adapter-stub contract only; broker/live execution remains blocked."
    if any("half_capture" in blocker for blocker in blockers):
        return "Expand OOS and half-capture stress evidence before any protected adapter-stub contract."
    if blockers:
        return "Continue local stress repair and OOS expansion; broker/live execution remains blocked."
    return "Rerun local stress repair after additional deterministic evidence."


def _scenario_by_id(scenarios: list[dict[str, Any]], scenario_id: str) -> dict[str, Any]:
    for scenario in scenarios:
        if str(scenario.get("scenario_id")) == scenario_id:
            return scenario
    return {}


def _worst_scenario(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    if not scenarios:
        return {}
    return min(scenarios, key=lambda item: float(item.get("pnl_after_stress", item.get("repaired_pnl_after_stress", 0.0))))


def _half_capture_reason(half_capture: dict[str, Any]) -> str:
    if not half_capture:
        return "half_capture_rate scenario is missing"
    blockers = [str(item) for item in list(half_capture.get("blockers") or [])]
    if any("capture_rate_stress_below_policy" in blocker for blocker in blockers):
        return "capture-rate stress multiplier is below the 65% policy floor"
    if float(half_capture.get("pnl_after_stress", 0.0)) <= 0.0:
        return "half-capture stress PnL is non-positive"
    return "half-capture remains under review but does not currently fail PnL"


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
