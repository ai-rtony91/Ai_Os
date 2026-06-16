from __future__ import annotations

from typing import Any

from automation.forex_engine import evidence_bundle_runner
from automation.forex_engine import broker_paper_sandbox_readiness
from automation.forex_engine import forex_dashboard_contract
from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import month_end_readiness
from automation.forex_engine import opportunity_capture
from automation.forex_engine import out_of_sample_validator
from automation.forex_engine import paper_forward_runner
from automation.forex_engine import paper_forward_stress
from automation.forex_engine import risk_governor_thresholds
from automation.forex_engine import schema_contracts as schemas
from automation.forex_engine import stress_repair


ALLOWED_V2_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def build_paper_forward_evidence_v2(fixture_ids: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    active_fixture_ids = list(fixture_ids or local_fixture_catalog.list_fixture_ids())
    catalog_validation = local_fixture_catalog.validate_fixture_catalog()
    catalog_summary = local_fixture_catalog.fixture_catalog_summary()
    multi_fixture = paper_forward_runner.run_multi_fixture_paper_forward(active_fixture_ids)
    multi_summary = paper_forward_runner.summarize_multi_fixture_paper_forward(multi_fixture)
    regime_consistency = paper_forward_runner.calculate_regime_consistency(
        list(multi_summary["per_fixture_results"])
    )
    evidence_summaries = [
        evidence_bundle_runner.evidence_bundle_summary(
            evidence_bundle_runner.build_local_evidence_bundle(fixture_id)
        )
        for fixture_id in active_fixture_ids
    ]
    risk_gate_result = _aggregate_risk_gate(evidence_summaries)
    bundle = {
        "schema": "AIOS_FOREX_PAPER_FORWARD_EVIDENCE_V2.v1",
        "mode": schemas.PAPER_ONLY,
        "fixture_ids": active_fixture_ids,
        "fixture_catalog_summary": catalog_summary,
        "fixture_catalog_validation": catalog_validation,
        "multi_fixture_paper_forward": multi_fixture,
        "multi_fixture_paper_forward_summary": multi_summary,
        "backtest_evidence_summaries": evidence_summaries,
        "risk_gate_result": risk_gate_result,
        "regime_consistency": regime_consistency,
        "safety": paper_forward_v2_boundary_summary(),
        "live_ready": False,
        "live_trade_ready": False,
        "protected_gate_required": True,
        "reports_written": False,
        "files_written": [],
    }
    opportunity_report = opportunity_capture.calculate_opportunity_capture(bundle)
    stress_scenarios = risk_governor_thresholds.run_cost_stress_scenarios(bundle)
    risk_governor = risk_governor_thresholds.evaluate_risk_governor_thresholds(
        bundle,
        opportunity_report,
    )
    paper_stress = paper_forward_stress.run_paper_forward_stress(bundle)
    oos_validation = out_of_sample_validator.run_out_of_sample_validation(active_fixture_ids)
    combined_gate = paper_forward_stress.build_stress_oos_gate(
        paper_stress,
        oos_validation,
        risk_governor,
    )
    stress_repair_result = stress_repair.apply_local_stress_repair_policy(bundle)
    sandbox_readiness = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        bundle,
        combined_gate,
        risk_governor,
        stress_repair_result,
    )
    bundle.update(
        {
            "opportunity_capture": opportunity_report,
            "opportunity_capture_summary": opportunity_capture.opportunity_capture_summary(opportunity_report),
            "risk_governor": risk_governor,
            "risk_governor_result": risk_governor,
            "stress_scenarios": stress_scenarios,
            "paper_forward_stress": paper_stress,
            "stress_result": paper_stress,
            "out_of_sample_validation": oos_validation,
            "oos_result": oos_validation,
            "combined_stress_oos_gate": combined_gate,
            "stress_repair": stress_repair_result,
            "stress_repair_summary": stress_repair.summarize_stress_repair(stress_repair_result),
            "broker_paper_sandbox_readiness": sandbox_readiness,
            "starting_balance": opportunity_report["starting_balance"],
            "ending_balance": opportunity_report["ending_balance"],
            "aggregate_paper_pnl": opportunity_report["aggregate_paper_pnl"],
            "return_pct": opportunity_report["return_pct"],
            "max_drawdown_pct": opportunity_report["max_drawdown_pct"],
            "cost_drag_usd": opportunity_report["cost_drag_usd"],
            "cost_drag_pct": opportunity_report["cost_drag_pct"],
        }
    )
    bundle["classification"] = classify_paper_forward_evidence_v2(bundle)
    bundle["blockers"] = _bundle_blockers(bundle)
    bundle["next_safe_action"] = _next_safe_action(bundle["classification"], bundle["blockers"])
    bundle["month_end_readiness_review"] = month_end_readiness.build_month_end_readiness_v2_review(bundle)
    bundle["forex_dashboard_v2"] = forex_dashboard_contract.build_forex_dashboard_v2_summary(
        summarize_paper_forward_evidence_v2(bundle)
    )
    schemas.assert_no_live_permissions(bundle)
    return bundle


def summarize_paper_forward_evidence_v2(bundle: dict[str, Any]) -> dict[str, Any]:
    payload = dict(bundle)
    multi_summary = dict(payload.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(payload.get("regime_consistency") or {})
    readiness = dict(payload.get("month_end_readiness_review") or {})
    stress_result = dict(payload.get("paper_forward_stress") or payload.get("stress_result") or {})
    stress_summary = dict(stress_result.get("stress_summary") or {})
    oos_result = dict(payload.get("out_of_sample_validation") or payload.get("oos_result") or {})
    oos_summary = dict(oos_result.get("oos_summary") or {})
    combined_gate = dict(payload.get("combined_stress_oos_gate") or {})
    repair = dict(payload.get("stress_repair") or {})
    repair_summary = dict(payload.get("stress_repair_summary") or stress_repair.summarize_stress_repair(repair) if repair else {})
    sandbox_readiness = dict(payload.get("broker_paper_sandbox_readiness") or {})
    classification = classify_paper_forward_evidence_v2(payload)
    summary = {
        "schema": "AIOS_FOREX_PAPER_FORWARD_EVIDENCE_V2_SUMMARY.v1",
        "mode": payload.get("mode", schemas.PAPER_ONLY),
        "fixture_count": int(multi_summary.get("fixture_count", 0)),
        "regime_count": int(regime.get("total_regimes", 0)),
        "total_intents": int(multi_summary.get("total_intents", 0)),
        "simulated_ledger_entries": int(multi_summary.get("total_ledger_entries", 0)),
        "aggregate_paper_pnl": float(multi_summary.get("aggregate_pnl", 0.0)),
        "consistency_pct": float(multi_summary.get("consistency_pct", 0.0)),
        "regime_consistency_pct": float(regime.get("consistent_regimes_pct", 0.0)),
        "starting_balance": float(payload.get("starting_balance", 500.0)),
        "ending_balance": float(payload.get("ending_balance", 500.0)),
        "return_pct": float(payload.get("return_pct", 0.0)),
        "max_drawdown_pct": float(payload.get("max_drawdown_pct", 0.0)),
        "cost_drag_usd": float(payload.get("cost_drag_usd", 0.0)),
        "cost_drag_pct": float(payload.get("cost_drag_pct", 0.0)),
        "capture_rate_pct": float(dict(payload.get("opportunity_capture") or {}).get("capture_rate_pct", 0.0)),
        "opportunity_quality_score": float(
            dict(payload.get("opportunity_capture") or {}).get("opportunity_quality_score", 0.0)
        ),
        "risk_governor_classification": dict(payload.get("risk_governor") or {}).get("classification", classification),
        "stress_classification": stress_summary.get("classification", combined_gate.get("stress_classification", "not_run")),
        "oos_classification": oos_summary.get("classification", combined_gate.get("oos_classification", "not_run")),
        "combined_stress_oos_classification": combined_gate.get("combined_classification", "not_run"),
        "stress_survived_scenarios_pct": float(combined_gate.get("survived_scenarios_pct", stress_summary.get("survived_scenarios_pct", 0.0))),
        "heldout_consistency_pct": float(combined_gate.get("heldout_consistency_pct", oos_summary.get("heldout_consistency_pct", 0.0))),
        "degradation_pct": float(combined_gate.get("degradation_pct", oos_summary.get("degradation_pct", 0.0))),
        "stress_oos_ready": combined_gate.get("combined_classification") == "PAPER_FORWARD_READY",
        "stress_repair_status": repair_summary.get("stress_repair_status", "not_run"),
        "stress_repair_classification": repair_summary.get("repaired_stress_classification", "not_run"),
        "repaired_stress_classification": repair_summary.get("repaired_stress_classification", "not_run"),
        "repaired_worst_stress_pnl": float(repair_summary.get("repaired_worst_stress_pnl", 0.0)),
        "repaired_stress_survived_pct": float(repair_summary.get("repaired_stress_survived_pct", 0.0)),
        "broker_paper_sandbox_readiness_status": sandbox_readiness.get("readiness_status", "not_run"),
        "broker_paper_sandbox_contract_ready": bool(
            sandbox_readiness.get("broker_paper_sandbox_contract_ready", False)
        ),
        "classification": classification,
        "readiness_status": readiness.get("classification", classification),
        "paper_forward_ready": bool(readiness.get("paper_forward_ready", classification == "PAPER_FORWARD_READY")),
        "v2_evidence_ready": bool(readiness.get("v2_evidence_ready", classification == "PAPER_FORWARD_READY")),
        "live_ready": False,
        "live_trade_ready": False,
        "protected_gate_required": True,
        "blockers": list(payload.get("blockers") or _bundle_blockers(payload)),
        "next_safe_action": payload.get("next_safe_action") or _next_safe_action(classification, []),
        "safety": "no broker/API/network/live execution",
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_paper_forward_evidence_v2(bundle: dict[str, Any]) -> str:
    payload = dict(bundle)
    if payload.get("live_ready") is True or payload.get("live_trade_ready") is True:
        return "FAIL"
    if payload.get("classification") == "LIVE_READY":
        return "FAIL"
    catalog = dict(payload.get("fixture_catalog_validation") or {})
    multi = dict(payload.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(payload.get("regime_consistency") or {})
    risk = dict(payload.get("risk_gate_result") or {})
    governor = dict(payload.get("risk_governor") or {})
    combined_gate = dict(payload.get("combined_stress_oos_gate") or {})
    classifications = [
        str(multi.get("classification") or "FAIL"),
        str(regime.get("classification") or "FAIL"),
        str(risk.get("classification") or "FAIL"),
    ]
    if governor:
        classifications.append(str(governor.get("classification") or "FAIL"))
    if combined_gate:
        classifications.append(str(combined_gate.get("combined_classification") or "FAIL"))
    if not catalog.get("valid", False):
        return "FAIL"
    if any(item not in ALLOWED_V2_CLASSIFICATIONS for item in classifications):
        return "FAIL"
    if "FAIL" in classifications:
        return "FAIL"
    if _bundle_blockers(payload):
        return "WATCHLIST"
    if all(item == "PAPER_FORWARD_READY" for item in classifications):
        return "PAPER_FORWARD_READY"
    return "WATCHLIST"


def paper_forward_v2_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_PAPER_FORWARD_EVIDENCE_V2_BOUNDARY.v1",
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


def evidence_v2_demo_lines(bundle: dict[str, Any]) -> list[str]:
    summary = summarize_paper_forward_evidence_v2(bundle)
    return [
        "AIOS Forex Paper-Forward Evidence V2",
        f"Mode: {summary['mode']}",
        f"Fixtures: {summary['fixture_count']}",
        f"Regimes: {summary['regime_count']}",
        f"Total intents: {summary['total_intents']}",
        f"Simulated ledger entries: {summary['simulated_ledger_entries']}",
        f"Aggregate paper PnL: {summary['aggregate_paper_pnl']}",
        f"Consistency pct: {summary['consistency_pct']}",
        f"Classification: {summary['classification']}",
        "Live ready: false",
        "Protected gate required: true",
        f"Next safe action: {summary['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]


def _aggregate_risk_gate(evidence_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    classifications = [str(item.get("risk_gate_status") or "FAIL") for item in evidence_summaries]
    blockers = [
        f"{item.get('fixture_id')}:risk_gate_failed"
        for item in evidence_summaries
        if item.get("risk_gate_status") == "FAIL"
    ]
    if not evidence_summaries:
        classification = "FAIL"
        blockers.append("missing_v1_evidence_summaries")
    elif any(item == "FAIL" for item in classifications):
        classification = "FAIL"
    elif any(item == "WATCHLIST" for item in classifications):
        classification = "WATCHLIST"
    else:
        classification = "PAPER_FORWARD_READY"
    result = {
        "schema": "AIOS_FOREX_PAPER_FORWARD_EVIDENCE_V2_RISK_GATE.v1",
        "classification": classification,
        "evaluated_fixtures": len(evidence_summaries),
        "blockers": blockers,
        "live_ready": False,
        "protected_gate_required": True,
        "next_safe_action": "Use local risk evidence for threshold hardening only; no broker or live execution.",
    }
    schemas.assert_no_live_permissions(result)
    return result


def _bundle_blockers(bundle: dict[str, Any]) -> list[str]:
    catalog = dict(bundle.get("fixture_catalog_validation") or {})
    multi = dict(bundle.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(bundle.get("regime_consistency") or {})
    risk = dict(bundle.get("risk_gate_result") or {})
    governor = dict(bundle.get("risk_governor") or bundle.get("risk_governor_result") or {})
    opportunity = dict(bundle.get("opportunity_capture") or {})
    stress_result = dict(bundle.get("paper_forward_stress") or bundle.get("stress_result") or {})
    oos_result = dict(bundle.get("out_of_sample_validation") or bundle.get("oos_result") or {})
    combined_gate = dict(bundle.get("combined_stress_oos_gate") or {})
    sandbox_readiness = dict(bundle.get("broker_paper_sandbox_readiness") or {})
    repair = dict(bundle.get("stress_repair") or {})
    blockers = []
    blockers.extend([str(item) for item in list(catalog.get("blockers") or [])])
    blockers.extend([str(item) for item in list(multi.get("blockers") or [])])
    blockers.extend([str(item) for item in list(regime.get("blockers") or [])])
    blockers.extend([str(item) for item in list(risk.get("blockers") or [])])
    blockers.extend([str(item) for item in list(governor.get("blockers") or [])])
    blockers.extend([str(item) for item in list(opportunity.get("blockers") or [])])
    blockers.extend([str(item) for item in list(stress_result.get("blockers") or [])])
    blockers.extend([str(item) for item in list(oos_result.get("blockers") or [])])
    blockers.extend([str(item) for item in list(combined_gate.get("blockers") or [])])
    blockers.extend([str(item) for item in list(repair.get("blockers") or [])])
    blockers.extend([str(item) for item in list(sandbox_readiness.get("blockers") or [])])
    return _unique(blockers)


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique


def _next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Prepare broker-paper sandbox readiness contract only; live readiness requires separate future approval."
    if blockers:
        return "Resolve stress/OOS local evidence blockers before broker-paper sandbox readiness is considered."
    return "Continue protected stress and out-of-sample evidence expansion; live readiness requires separate future approval."
