from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import broker_paper_sandbox_readiness
from automation.forex_engine import schema_contracts as schemas
from automation.forex_engine.evidence_aggregator import ALLOWED_EVIDENCE_CLASSES


LIVE_TRADE_BLOCKERS = [
    "live readiness requires a separate protected future packet",
    "broker integration is not approved",
    "credentials and secrets are blocked",
    "real orders are blocked",
    "webhooks are blocked",
    "scheduler and daemon activation are blocked",
]


def build_month_end_readiness_review(
    evidence_bundle: dict[str, Any],
    dashboard_state: schemas.DashboardState | dict[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = dict(evidence_bundle)
    dashboard = _payload(dashboard_state) if dashboard_state is not None else {}
    schemas.assert_no_live_permissions([bundle, dashboard])
    classification = str(bundle.get("classification") or "FAIL")
    if classification not in ALLOWED_EVIDENCE_CLASSES:
        classification = "FAIL"
    blockers = _text_list(bundle.get("blockers"))
    paper_forward_ready = classification == "PAPER_FORWARD_READY" and not blockers
    review = {
        "schema": "AIOS_FOREX_BUILDER_MONTH_END_READINESS_REVIEW.v1",
        "classification": classification,
        "complete": _complete_sections(bundle, dashboard),
        "blocked": _unique([*blockers, *LIVE_TRADE_BLOCKERS]),
        "evidence_exists": {
            "backtest": bool(bundle.get("backtest_result")),
            "walk_forward": bool(bundle.get("walk_forward_summary")),
            "cost_model": bool(bundle.get("cost_model")),
            "risk_gate": bool(bundle.get("risk_gate")),
            "paper_forward": bool(bundle.get("paper_forward_summary")),
            "dashboard": bool(dashboard),
        },
        "paper_forward_ready": paper_forward_ready,
        "live_trade_ready": False,
        "live_trade_blockers": list(LIVE_TRADE_BLOCKERS),
        "protected_gate_required": True,
        "next_safe_action": _next_safe_action(paper_forward_ready, blockers),
        "live_ready": False,
    }
    schemas.assert_no_live_permissions(review)
    return review


def build_month_end_readiness_v2_review(evidence_bundle: dict[str, Any]) -> dict[str, Any]:
    bundle = dict(evidence_bundle)
    schemas.assert_no_live_permissions(bundle)
    classification = str(bundle.get("classification") or "FAIL")
    if classification not in ALLOWED_EVIDENCE_CLASSES:
        classification = "FAIL"
    blockers = _text_list(bundle.get("blockers"))
    multi_summary = dict(bundle.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(bundle.get("regime_consistency") or {})
    catalog = dict(bundle.get("fixture_catalog_summary") or {})
    opportunity = dict(bundle.get("opportunity_capture") or {})
    risk_governor = dict(bundle.get("risk_governor") or bundle.get("risk_governor_result") or {})
    stress = dict(bundle.get("stress_scenarios") or {})
    paper_stress = dict(bundle.get("paper_forward_stress") or bundle.get("stress_result") or {})
    paper_stress_summary = dict(paper_stress.get("stress_summary") or {})
    stress_repair = dict(bundle.get("stress_repair") or {})
    stress_repair_summary = dict(bundle.get("stress_repair_summary") or {})
    oos_result = dict(bundle.get("out_of_sample_validation") or bundle.get("oos_result") or {})
    oos_summary = dict(oos_result.get("oos_summary") or {})
    combined_gate = dict(bundle.get("combined_stress_oos_gate") or {})
    sandbox_readiness = dict(bundle.get("broker_paper_sandbox_readiness") or {})
    if not sandbox_readiness:
        sandbox_readiness = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
            bundle,
            combined_gate,
            risk_governor,
        )
    stress_blockers = [
        str(blocker)
        for scenario in list(stress.get("scenario_results") or stress.get("scenarios") or [])
        for blocker in list(dict(scenario).get("blockers") or [])
    ]
    local_blockers = _unique(
        [
            *blockers,
            *_text_list(opportunity.get("blockers")),
            *_text_list(risk_governor.get("blockers")),
            *_text_list(paper_stress.get("blockers")),
            *_text_list(stress_repair.get("blockers")),
            *_text_list(oos_result.get("blockers")),
            *_text_list(combined_gate.get("blockers")),
            *_text_list(sandbox_readiness.get("blockers")),
            *stress_blockers,
        ]
    )
    risk_governor_classification = str(risk_governor.get("classification") or classification)
    combined_stress_oos_classification = str(combined_gate.get("combined_classification") or "not_run")
    stress_oos_ready = combined_stress_oos_classification == "PAPER_FORWARD_READY"
    paper_forward_ready = (
        classification == "PAPER_FORWARD_READY"
        and risk_governor_classification == "PAPER_FORWARD_READY"
        and (combined_stress_oos_classification in {"not_run", "PAPER_FORWARD_READY"})
        and not local_blockers
    )
    review = {
        "schema": "AIOS_FOREX_BUILDER_MONTH_END_READINESS_REVIEW_V2.v1",
        "classification": classification,
        "paper_forward_ready": paper_forward_ready,
        "v2_evidence_ready": paper_forward_ready,
        "stress_oos_ready": stress_oos_ready,
        "broker_paper_sandbox_ready": False,
        "stress_repair_status": stress_repair_summary.get("stress_repair_status", "not_run"),
        "repaired_stress_classification": stress_repair_summary.get("repaired_stress_classification", "not_run"),
        "broker_paper_contract_ready": bool(
            sandbox_readiness.get("broker_paper_sandbox_contract_ready", False)
        ),
        "broker_paper_sandbox_readiness_status": sandbox_readiness.get("readiness_status", "not_run"),
        "broker_paper_sandbox_contract_ready": bool(
            sandbox_readiness.get("broker_paper_sandbox_contract_ready", False)
        ),
        "broker_integration_active": False,
        "credentials_required_now": False,
        "live_trade_ready": False,
        "protected_gate_required": True,
        "evidence_summary": {
            "fixture_count": int(multi_summary.get("fixture_count", 0)),
            "regime_count": int(regime.get("total_regimes", 0)),
            "total_intents": int(multi_summary.get("total_intents", 0)),
            "simulated_ledger_entries": int(multi_summary.get("total_ledger_entries", 0)),
            "aggregate_paper_pnl": float(multi_summary.get("aggregate_pnl", 0.0)),
            "consistency_pct": float(multi_summary.get("consistency_pct", 0.0)),
            "regime_consistency_pct": float(regime.get("consistent_regimes_pct", 0.0)),
            "starting_balance": float(opportunity.get("starting_balance", bundle.get("starting_balance", 500.0))),
            "ending_balance": float(opportunity.get("ending_balance", bundle.get("ending_balance", 500.0))),
            "return_pct": float(opportunity.get("return_pct", bundle.get("return_pct", 0.0))),
            "max_drawdown_pct": float(opportunity.get("max_drawdown_pct", bundle.get("max_drawdown_pct", 0.0))),
            "cost_drag_pct": float(opportunity.get("cost_drag_pct", bundle.get("cost_drag_pct", 0.0))),
            "capture_rate_pct": float(opportunity.get("capture_rate_pct", 0.0)),
            "missed_signal_count": int(opportunity.get("missed_signal_count", 0)),
            "missed_pnl_estimate": float(opportunity.get("missed_pnl_estimate", 0.0)),
            "risk_adjusted_return": float(opportunity.get("risk_adjusted_return", 0.0)),
            "opportunity_quality_score": float(opportunity.get("opportunity_quality_score", 0.0)),
            "risk_governor_classification": risk_governor_classification,
            "stress_scenario_count": len(list(stress.get("scenario_results") or stress.get("scenarios") or [])),
            "paper_forward_stress_scenario_count": int(paper_stress_summary.get("scenario_count", 0)),
            "stress_classification": paper_stress_summary.get(
                "classification",
                combined_gate.get("stress_classification", "not_run"),
            ),
            "stress_survived_scenarios_pct": float(
                combined_gate.get(
                    "survived_scenarios_pct",
                    paper_stress_summary.get("survived_scenarios_pct", 0.0),
                )
            ),
            "oos_classification": oos_summary.get(
                "classification",
                combined_gate.get("oos_classification", "not_run"),
            ),
            "combined_stress_oos_classification": combined_stress_oos_classification,
            "heldout_consistency_pct": float(
                combined_gate.get(
                    "heldout_consistency_pct",
                    oos_summary.get("heldout_consistency_pct", 0.0),
                )
            ),
            "degradation_pct": float(
                combined_gate.get("degradation_pct", oos_summary.get("degradation_pct", 0.0))
            ),
            "stress_oos_ready": stress_oos_ready,
            "stress_repair_status": stress_repair_summary.get("stress_repair_status", "not_run"),
            "repaired_stress_classification": stress_repair_summary.get("repaired_stress_classification", "not_run"),
            "repaired_worst_stress_pnl": float(stress_repair_summary.get("repaired_worst_stress_pnl", 0.0)),
            "repaired_stress_survived_pct": float(stress_repair_summary.get("repaired_stress_survived_pct", 0.0)),
            "broker_paper_sandbox_ready": False,
            "broker_paper_contract_ready": bool(
                sandbox_readiness.get("broker_paper_sandbox_contract_ready", False)
            ),
            "broker_paper_sandbox_readiness_status": sandbox_readiness.get("readiness_status", "not_run"),
            "broker_paper_sandbox_contract_ready": bool(
                sandbox_readiness.get("broker_paper_sandbox_contract_ready", False)
            ),
            "broker_integration_active": False,
            "credentials_required_now": False,
            "symbols": list(catalog.get("symbols") or []),
            "timeframes": list(catalog.get("timeframes") or []),
        },
        "blockers": local_blockers,
        "blocked": _unique([*local_blockers, *LIVE_TRADE_BLOCKERS]),
        "live_trade_blockers": list(LIVE_TRADE_BLOCKERS),
        "next_safe_action": _next_safe_action_v2(paper_forward_ready, local_blockers),
        "live_ready": False,
    }
    schemas.assert_no_live_permissions(review)
    return review


def _payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value in (None, "", {}, []):
        return []
    return [str(value)]


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique


def _complete_sections(bundle: dict[str, Any], dashboard: dict[str, Any]) -> list[str]:
    complete = []
    for key, label in (
        ("backtest_result", "backtest result"),
        ("walk_forward_summary", "walk-forward summary"),
        ("cost_model", "cost model"),
        ("risk_gate", "risk gate"),
        ("paper_forward_summary", "paper-forward ledger summary"),
    ):
        if bundle.get(key):
            complete.append(label)
    if dashboard:
        complete.append("dashboard state")
    return complete


def _next_safe_action(paper_forward_ready: bool, blockers: list[str]) -> str:
    if paper_forward_ready:
        return "Continue paper-forward evidence expansion; live readiness remains blocked behind protected gates."
    if blockers:
        return "Resolve month-end evidence blockers before paper-forward readiness is claimed."
    return "Collect missing evidence and rerun the local readiness review."


def _next_safe_action_v2(paper_forward_ready: bool, blockers: list[str]) -> str:
    if paper_forward_ready:
        return "Prepare broker-paper sandbox readiness contract only; live readiness requires separate future approval."
    if blockers:
        return "Resolve V2 local evidence blockers before claiming paper-forward readiness; live readiness requires separate future approval."
    return "Collect stronger multi-regime local evidence and rerun V2 readiness review; live readiness requires separate future approval."
