from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import broker_paper_dryrun_replay_harness
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
    expanded_oos = dict(bundle.get("expanded_oos") or {})
    expanded_oos_summary = dict(bundle.get("expanded_oos_summary") or expanded_oos.get("expanded_oos_summary") or {})
    oos_repair = dict(bundle.get("oos_repair") or {})
    oos_repair_summary = dict(bundle.get("oos_repair_summary") or {})
    low_vol_edge = dict(bundle.get("low_vol_edge_redesign") or {})
    low_vol_edge_summary = dict(bundle.get("low_vol_edge_summary") or low_vol_edge)
    presecurity_gate = dict(bundle.get("presecurity_gate") or bundle.get("broker_paper_presecurity_gate") or {})
    presecurity_gate_summary = dict(bundle.get("presecurity_gate_summary") or presecurity_gate)
    adapter_stub = dict(
        bundle.get("broker_paper_adapter_stub_contract")
        or bundle.get("broker_paper_stub_contract")
        or bundle.get("adapter_stub_contract")
        or {}
    )
    adapter_stub_summary = dict(bundle.get("broker_paper_stub_contract_summary") or adapter_stub)
    dryrun_ledger = dict(
        bundle.get("broker_paper_dryrun_intent_ledger")
        or bundle.get("dryrun_intent_ledger")
        or bundle.get("broker_paper_intent_ledger")
        or {}
    )
    dryrun_ledger_summary = dict(bundle.get("broker_paper_dryrun_intent_ledger_summary") or dryrun_ledger)
    dryrun_ledger_classification_for_blockers = str(
        dryrun_ledger_summary.get("broker_paper_dryrun_ledger_classification")
        or dryrun_ledger_summary.get("classification")
        or dryrun_ledger.get("classification")
        or ""
    )
    dryrun_ledger_rejection_blockers = (
        []
        if dryrun_ledger_classification_for_blockers == "DRYRUN_LEDGER_READY"
        else _text_list(dryrun_ledger.get("rejection_reasons"))
    )
    dryrun_risk_governor = dict(
        bundle.get("broker_paper_dryrun_risk_governor")
        or bundle.get("dryrun_risk_governor")
        or bundle.get("broker_paper_risk_governor")
        or {}
    )
    dryrun_risk_governor_summary = dict(
        bundle.get("broker_paper_dryrun_risk_governor_summary")
        or dryrun_risk_governor
    )
    dryrun_risk_governor_classification_for_blockers = str(
        dryrun_risk_governor_summary.get("broker_paper_dryrun_risk_governor_classification")
        or dryrun_risk_governor_summary.get("classification")
        or dryrun_risk_governor.get("classification")
        or ""
    )
    dryrun_risk_governor_rejection_blockers = (
        []
        if dryrun_risk_governor_classification_for_blockers == "DRYRUN_RISK_GOVERNOR_READY"
        else _text_list(dryrun_risk_governor.get("rejection_reasons"))
    )
    dryrun_replay_harness = dict(
        bundle.get("broker_paper_dryrun_replay_harness")
        or bundle.get("dryrun_replay_harness")
        or bundle.get("broker_paper_replay_harness")
        or {}
    )
    dryrun_replay_harness_summary = dict(
        bundle.get("broker_paper_dryrun_replay_harness_summary")
        or dryrun_replay_harness
    )
    if dryrun_replay_harness and "classification" in dryrun_replay_harness:
        dryrun_replay_harness_summary = broker_paper_dryrun_replay_harness.summarize_dryrun_replay_harness(
            dryrun_replay_harness
        )
    dryrun_replay_harness_classification_for_blockers = str(
        dryrun_replay_harness_summary.get("broker_paper_dryrun_replay_harness_classification")
        or dryrun_replay_harness_summary.get("classification")
        or dryrun_replay_harness.get("classification")
        or ""
    )
    dryrun_replay_harness_rejection_blockers = (
        []
        if dryrun_replay_harness_classification_for_blockers == "DRYRUN_REPLAY_HARNESS_READY"
        else _text_list(dryrun_replay_harness.get("rejection_reasons"))
    )
    oos_result = dict(bundle.get("out_of_sample_validation") or bundle.get("oos_result") or {})
    oos_summary = dict(oos_result.get("oos_summary") or {})
    combined_gate = dict(bundle.get("combined_stress_oos_gate") or {})
    sandbox_readiness = dict(bundle.get("broker_paper_sandbox_readiness") or {})
    if not sandbox_readiness:
        sandbox_readiness = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
            evidence=bundle,
            stress_oos=combined_gate,
            risk_governor=risk_governor,
            stress_repair=stress_repair,
            expanded_oos=expanded_oos,
            oos_repair=oos_repair,
            low_vol_edge_redesign=low_vol_edge,
            presecurity_gate=presecurity_gate,
            adapter_stub_contract=adapter_stub,
            dryrun_intent_ledger=dryrun_ledger,
            dryrun_risk_governor=dryrun_risk_governor,
            dryrun_replay_harness=dryrun_replay_harness,
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
            *_text_list(expanded_oos.get("blockers")),
            *_text_list(oos_repair.get("blockers")),
            *_text_list(low_vol_edge.get("blockers")),
            *_text_list(presecurity_gate.get("blockers")),
            *_text_list(adapter_stub.get("blockers")),
            *_text_list(adapter_stub.get("rejection_reasons")),
            *_text_list(dryrun_ledger.get("blockers")),
            *dryrun_ledger_rejection_blockers,
            *_text_list(dryrun_risk_governor.get("blockers")),
            *dryrun_risk_governor_rejection_blockers,
            *_text_list(dryrun_replay_harness.get("blockers")),
            *dryrun_replay_harness_rejection_blockers,
            *_text_list(oos_result.get("blockers")),
            *_text_list(combined_gate.get("blockers")),
            *_text_list(sandbox_readiness.get("blockers")),
            *stress_blockers,
        ]
    )
    risk_governor_classification = str(risk_governor.get("classification") or classification)
    combined_stress_oos_classification = str(combined_gate.get("combined_classification") or "not_run")
    oos_repair_classification = str(
        oos_repair_summary.get("oos_repair_classification")
        or oos_repair.get("repaired_classification")
        or oos_repair.get("classification")
        or "not_run"
    )
    low_vol_edge_classification = str(
        low_vol_edge_summary.get("low_vol_edge_classification")
        or low_vol_edge.get("classification")
        or "not_run"
    )
    presecurity_gate_classification = str(
        presecurity_gate_summary.get("presecurity_gate_classification")
        or sandbox_readiness.get("presecurity_gate_classification")
        or presecurity_gate.get("classification")
        or "not_run"
    )
    broker_paper_stub_contract_classification = str(
        adapter_stub_summary.get("broker_paper_stub_contract_classification")
        or sandbox_readiness.get("broker_paper_stub_contract_classification")
        or adapter_stub.get("classification")
        or "not_run"
    )
    broker_paper_dryrun_ledger_classification = str(
        dryrun_ledger_summary.get("broker_paper_dryrun_ledger_classification")
        or sandbox_readiness.get("broker_paper_dryrun_ledger_classification")
        or dryrun_ledger.get("classification")
        or "not_run"
    )
    broker_paper_dryrun_risk_governor_classification = str(
        dryrun_risk_governor_summary.get("broker_paper_dryrun_risk_governor_classification")
        or sandbox_readiness.get("broker_paper_dryrun_risk_governor_classification")
        or dryrun_risk_governor.get("classification")
        or "not_run"
    )
    broker_paper_dryrun_replay_harness_classification = str(
        dryrun_replay_harness_summary.get("broker_paper_dryrun_replay_harness_classification")
        or sandbox_readiness.get("broker_paper_dryrun_replay_harness_classification")
        or dryrun_replay_harness.get("classification")
        or "not_run"
    )
    stress_oos_ready = combined_stress_oos_classification == "PAPER_FORWARD_READY"
    paper_forward_ready = (
        classification == "PAPER_FORWARD_READY"
        and risk_governor_classification == "PAPER_FORWARD_READY"
        and (combined_stress_oos_classification in {"not_run", "PAPER_FORWARD_READY"})
        and (low_vol_edge_classification in {"not_run", "PAPER_FORWARD_READY"})
        and presecurity_gate_classification in {"not_run", "PRESECURITY_READY"}
        and broker_paper_stub_contract_classification in {"not_run", "STUB_CONTRACT_READY"}
        and broker_paper_dryrun_ledger_classification in {"not_run", "DRYRUN_LEDGER_READY"}
        and broker_paper_dryrun_risk_governor_classification in {"not_run", "DRYRUN_RISK_GOVERNOR_READY"}
        and broker_paper_dryrun_replay_harness_classification in {"not_run", "DRYRUN_REPLAY_HARNESS_READY"}
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
        "expanded_oos_status": expanded_oos_summary.get("classification", expanded_oos.get("classification", "not_run")),
        "expanded_oos_classification": expanded_oos_summary.get(
            "classification",
            expanded_oos.get("classification", "not_run"),
        ),
        "oos_repair_classification": oos_repair_classification,
        "low_vol_edge_classification": low_vol_edge_classification,
        "low_vol_policy_action": str(
            low_vol_edge_summary.get("low_vol_policy_action")
            or low_vol_edge.get("low_vol_policy_action")
            or "not_run"
        ),
        "redesigned_max_degradation_pct": float(
            low_vol_edge_summary.get(
                "redesigned_max_degradation_pct",
                low_vol_edge.get("redesigned_max_degradation_pct", 0.0),
            )
        ),
        "low_vol_rejected_intents": int(
            low_vol_edge_summary.get(
                "rejected_low_vol_intents",
                low_vol_edge_summary.get("low_vol_rejected_intents", low_vol_edge.get("rejected_low_vol_intents", 0)),
            )
        ),
        "presecurity_gate_classification": presecurity_gate_classification,
        "credential_boundary_required": bool(
            presecurity_gate_summary.get(
                "credential_boundary_required",
                sandbox_readiness.get("credential_boundary_required", True),
            )
        ),
        "kill_switch_required": bool(
            presecurity_gate_summary.get("kill_switch_required", sandbox_readiness.get("kill_switch_required", True))
        ),
        "max_loss_guard_required": bool(
            presecurity_gate_summary.get(
                "max_loss_guard_required",
                sandbox_readiness.get("max_loss_guard_required", True),
            )
        ),
        "audit_log_required": bool(
            presecurity_gate_summary.get("audit_log_required", sandbox_readiness.get("audit_log_required", True))
        ),
        "broker_paper_stub_contract_classification": broker_paper_stub_contract_classification,
        "broker_paper_stub_contract_ready": bool(
            adapter_stub_summary.get(
                "broker_paper_stub_contract_ready",
                sandbox_readiness.get("broker_paper_stub_contract_ready", False),
            )
        ),
        "broker_paper_dryrun_ledger_classification": broker_paper_dryrun_ledger_classification,
        "broker_paper_dryrun_ledger_ready": bool(
            dryrun_ledger_summary.get(
                "broker_paper_dryrun_ledger_ready",
                sandbox_readiness.get("broker_paper_dryrun_ledger_ready", False),
            )
        ),
        "dryrun_ledger_records": int(
            dryrun_ledger_summary.get("records_count", sandbox_readiness.get("dryrun_ledger_records", 0))
        ),
        "dryrun_ledger_accepted": int(
            dryrun_ledger_summary.get("accepted_count", sandbox_readiness.get("dryrun_ledger_accepted", 0))
        ),
        "dryrun_ledger_rejected": int(
            dryrun_ledger_summary.get("rejected_count", sandbox_readiness.get("dryrun_ledger_rejected", 0))
        ),
        "broker_paper_dryrun_risk_governor_classification": broker_paper_dryrun_risk_governor_classification,
        "broker_paper_dryrun_risk_governor_ready": bool(
            dryrun_risk_governor_summary.get(
                "broker_paper_dryrun_risk_governor_ready",
                sandbox_readiness.get("broker_paper_dryrun_risk_governor_ready", False),
            )
        ),
        "dryrun_risk_records": int(
            dryrun_risk_governor_summary.get(
                "records_count",
                sandbox_readiness.get("dryrun_risk_records", 0),
            )
        ),
        "dryrun_risk_accepted": int(
            dryrun_risk_governor_summary.get(
                "risk_accepted",
                sandbox_readiness.get("dryrun_risk_accepted", 0),
            )
        ),
        "dryrun_risk_rejected": int(
            dryrun_risk_governor_summary.get(
                "risk_rejected",
                sandbox_readiness.get("dryrun_risk_rejected", 0),
            )
        ),
        "aggregate_max_loss_usd": float(
            dryrun_risk_governor_summary.get(
                "aggregate_max_loss_usd",
                sandbox_readiness.get("aggregate_max_loss_usd", 0.0),
            )
        ),
        "max_daily_loss_usd": float(
            dryrun_risk_governor_summary.get(
                "max_daily_loss_usd",
                sandbox_readiness.get("max_daily_loss_usd", 5.0),
            )
        ),
        "kill_switch_armed": bool(
            dryrun_risk_governor_summary.get(
                "kill_switch_armed",
                sandbox_readiness.get("kill_switch_armed", True),
            )
        ),
        "broker_paper_dryrun_replay_harness_classification": broker_paper_dryrun_replay_harness_classification,
        "broker_paper_dryrun_replay_harness_ready": bool(
            dryrun_replay_harness_summary.get(
                "broker_paper_dryrun_replay_harness_ready",
                sandbox_readiness.get("broker_paper_dryrun_replay_harness_ready", False),
            )
        ),
        "replay_records": int(
            dryrun_replay_harness_summary.get(
                "records_replayed",
                sandbox_readiness.get("replay_records", 0),
            )
        ),
        "replay_stub_accepted": int(
            dryrun_replay_harness_summary.get(
                "stub_accepted",
                sandbox_readiness.get("replay_stub_accepted", 0),
            )
        ),
        "replay_stub_rejected": int(
            dryrun_replay_harness_summary.get(
                "stub_rejected",
                sandbox_readiness.get("replay_stub_rejected", 0),
            )
        ),
        "replay_risk_accepted": int(
            dryrun_replay_harness_summary.get(
                "risk_accepted",
                sandbox_readiness.get("replay_risk_accepted", 0),
            )
        ),
        "replay_risk_rejected": int(
            dryrun_replay_harness_summary.get(
                "risk_rejected",
                sandbox_readiness.get("replay_risk_rejected", 0),
            )
        ),
        "broker_paper_orders_allowed": False,
        "credentials_allowed": False,
        "network_api_allowed": False,
        "original_max_degradation_pct": float(
            oos_repair_summary.get(
                "original_max_degradation_pct",
                oos_repair.get("original_max_degradation_pct", expanded_oos.get("original_max_degradation_pct", 0.0)),
            )
        ),
        "repaired_max_degradation_pct": float(
            oos_repair_summary.get(
                "repaired_max_degradation_pct",
                oos_repair.get("repaired_max_degradation_pct", expanded_oos.get("repaired_max_degradation_pct", 0.0)),
            )
        ),
        "degradation_improvement_pct": float(
            oos_repair_summary.get(
                "degradation_improvement_pct",
                oos_repair.get("degradation_improvement_pct", expanded_oos.get("degradation_improvement_pct", 0.0)),
            )
        ),
        "weakest_split": str(
            oos_repair_summary.get(
                "weakest_split",
                oos_repair.get(
                    "weakest_split_after",
                    dict(expanded_oos.get("weakest_split") or {}).get("split_id", "none"),
                ),
            )
        ),
        "broker_paper_contract_ready": False,
        "broker_paper_sandbox_readiness_status": sandbox_readiness.get("readiness_status", "not_run"),
        "broker_paper_sandbox_contract_ready": bool(sandbox_readiness.get("broker_paper_sandbox_contract_ready", False)),
        "broker_integration_active": False,
        "credentials_required_now": False,
        "live_trade_ready": False,
        "protected_gate_required": True,
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1",
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
            "expanded_oos_status": expanded_oos_summary.get(
                "classification",
                expanded_oos.get("classification", "not_run"),
            ),
            "expanded_oos_classification": expanded_oos_summary.get(
                "classification",
                expanded_oos.get("classification", "not_run"),
            ),
            "expanded_oos_split_count": int(
                expanded_oos_summary.get("split_count", expanded_oos.get("split_count", 0))
            ),
            "expanded_oos_heldout_consistency_pct": float(
                expanded_oos_summary.get(
                    "heldout_consistency_pct",
                    expanded_oos.get("heldout_consistency_pct", 0.0),
                )
            ),
            "expanded_oos_degradation_pct": float(
                expanded_oos_summary.get("degradation_pct", expanded_oos.get("degradation_pct", 0.0))
            ),
            "oos_repair_classification": oos_repair_classification,
            "low_vol_edge_classification": low_vol_edge_classification,
            "low_vol_policy_action": str(
                low_vol_edge_summary.get("low_vol_policy_action")
                or low_vol_edge.get("low_vol_policy_action")
                or "not_run"
            ),
            "redesigned_max_degradation_pct": float(
                low_vol_edge_summary.get(
                    "redesigned_max_degradation_pct",
                    low_vol_edge.get("redesigned_max_degradation_pct", 0.0),
                )
            ),
            "low_vol_rejected_intents": int(
                low_vol_edge_summary.get(
                    "rejected_low_vol_intents",
                    low_vol_edge_summary.get("low_vol_rejected_intents", low_vol_edge.get("rejected_low_vol_intents", 0)),
                )
            ),
            "presecurity_gate_classification": presecurity_gate_classification,
            "credential_boundary_required": bool(
                presecurity_gate_summary.get(
                    "credential_boundary_required",
                    sandbox_readiness.get("credential_boundary_required", True),
                )
            ),
            "kill_switch_required": bool(
                presecurity_gate_summary.get("kill_switch_required", sandbox_readiness.get("kill_switch_required", True))
            ),
            "max_loss_guard_required": bool(
                presecurity_gate_summary.get(
                    "max_loss_guard_required",
                    sandbox_readiness.get("max_loss_guard_required", True),
                )
            ),
            "audit_log_required": bool(
                presecurity_gate_summary.get("audit_log_required", sandbox_readiness.get("audit_log_required", True))
            ),
            "broker_paper_stub_contract_classification": broker_paper_stub_contract_classification,
            "broker_paper_stub_contract_ready": bool(
                adapter_stub_summary.get(
                    "broker_paper_stub_contract_ready",
                    sandbox_readiness.get("broker_paper_stub_contract_ready", False),
                )
            ),
            "broker_paper_dryrun_ledger_classification": broker_paper_dryrun_ledger_classification,
            "broker_paper_dryrun_ledger_ready": bool(
                dryrun_ledger_summary.get(
                    "broker_paper_dryrun_ledger_ready",
                    sandbox_readiness.get("broker_paper_dryrun_ledger_ready", False),
                )
            ),
            "dryrun_ledger_records": int(
                dryrun_ledger_summary.get("records_count", sandbox_readiness.get("dryrun_ledger_records", 0))
            ),
            "dryrun_ledger_accepted": int(
                dryrun_ledger_summary.get("accepted_count", sandbox_readiness.get("dryrun_ledger_accepted", 0))
            ),
            "dryrun_ledger_rejected": int(
                dryrun_ledger_summary.get("rejected_count", sandbox_readiness.get("dryrun_ledger_rejected", 0))
            ),
            "broker_paper_dryrun_risk_governor_classification": broker_paper_dryrun_risk_governor_classification,
            "broker_paper_dryrun_risk_governor_ready": bool(
                dryrun_risk_governor_summary.get(
                    "broker_paper_dryrun_risk_governor_ready",
                    sandbox_readiness.get("broker_paper_dryrun_risk_governor_ready", False),
                )
            ),
            "dryrun_risk_records": int(
                dryrun_risk_governor_summary.get(
                    "records_count",
                    sandbox_readiness.get("dryrun_risk_records", 0),
                )
            ),
            "dryrun_risk_accepted": int(
                dryrun_risk_governor_summary.get(
                    "risk_accepted",
                    sandbox_readiness.get("dryrun_risk_accepted", 0),
                )
            ),
            "dryrun_risk_rejected": int(
                dryrun_risk_governor_summary.get(
                    "risk_rejected",
                    sandbox_readiness.get("dryrun_risk_rejected", 0),
                )
            ),
            "aggregate_max_loss_usd": float(
                dryrun_risk_governor_summary.get(
                    "aggregate_max_loss_usd",
                    sandbox_readiness.get("aggregate_max_loss_usd", 0.0),
                )
            ),
            "max_daily_loss_usd": float(
                dryrun_risk_governor_summary.get(
                    "max_daily_loss_usd",
                    sandbox_readiness.get("max_daily_loss_usd", 5.0),
                )
            ),
            "kill_switch_armed": bool(
                dryrun_risk_governor_summary.get(
                    "kill_switch_armed",
                    sandbox_readiness.get("kill_switch_armed", True),
                )
            ),
            "broker_paper_dryrun_replay_harness_classification": (
                broker_paper_dryrun_replay_harness_classification
            ),
            "broker_paper_dryrun_replay_harness_ready": bool(
                dryrun_replay_harness_summary.get(
                    "broker_paper_dryrun_replay_harness_ready",
                    sandbox_readiness.get("broker_paper_dryrun_replay_harness_ready", False),
                )
            ),
            "replay_records": int(
                dryrun_replay_harness_summary.get(
                    "records_replayed",
                    sandbox_readiness.get("replay_records", 0),
                )
            ),
            "replay_stub_accepted": int(
                dryrun_replay_harness_summary.get(
                    "stub_accepted",
                    sandbox_readiness.get("replay_stub_accepted", 0),
                )
            ),
            "replay_stub_rejected": int(
                dryrun_replay_harness_summary.get(
                    "stub_rejected",
                    sandbox_readiness.get("replay_stub_rejected", 0),
                )
            ),
            "replay_risk_accepted": int(
                dryrun_replay_harness_summary.get(
                    "risk_accepted",
                    sandbox_readiness.get("replay_risk_accepted", 0),
                )
            ),
            "replay_risk_rejected": int(
                dryrun_replay_harness_summary.get(
                    "risk_rejected",
                    sandbox_readiness.get("replay_risk_rejected", 0),
                )
            ),
            "broker_paper_orders_allowed": False,
            "credentials_allowed": False,
            "network_api_allowed": False,
            "original_max_degradation_pct": float(
                oos_repair_summary.get(
                    "original_max_degradation_pct",
                    oos_repair.get("original_max_degradation_pct", expanded_oos.get("original_max_degradation_pct", 0.0)),
                )
            ),
            "repaired_max_degradation_pct": float(
                oos_repair_summary.get(
                    "repaired_max_degradation_pct",
                    oos_repair.get("repaired_max_degradation_pct", expanded_oos.get("repaired_max_degradation_pct", 0.0)),
                )
            ),
            "degradation_improvement_pct": float(
                oos_repair_summary.get(
                    "degradation_improvement_pct",
                    oos_repair.get("degradation_improvement_pct", expanded_oos.get("degradation_improvement_pct", 0.0)),
                )
            ),
            "weakest_oos_split": str(
                oos_repair_summary.get(
                    "weakest_split",
                    oos_repair.get(
                        "weakest_split_after",
                        dict(expanded_oos.get("weakest_split") or {}).get("split_id", "none"),
                    ),
                )
            ),
            "broker_paper_sandbox_ready": False,
            "broker_paper_contract_ready": False,
            "broker_paper_sandbox_readiness_status": sandbox_readiness.get("readiness_status", "not_run"),
            "broker_paper_sandbox_contract_ready": bool(
                sandbox_readiness.get("broker_paper_sandbox_contract_ready", False)
            ),
            "broker_integration_active": False,
            "credentials_required_now": False,
            "security_gate_required_before_broker_paper": True,
            "required_security_packet": "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1",
            "symbols": list(catalog.get("symbols") or []),
            "timeframes": list(catalog.get("timeframes") or []),
        },
        "blockers": local_blockers,
        "blocked": _unique([*local_blockers, *LIVE_TRADE_BLOCKERS]),
        "live_trade_blockers": list(LIVE_TRADE_BLOCKERS),
        "next_safe_action": _next_safe_action_v2(
            paper_forward_ready,
            local_blockers,
            oos_repair_classification,
            low_vol_edge_classification,
            presecurity_gate_classification,
            broker_paper_stub_contract_classification,
            broker_paper_dryrun_ledger_classification,
            broker_paper_dryrun_risk_governor_classification,
            broker_paper_dryrun_replay_harness_classification,
        ),
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


def _next_safe_action_v2(
    paper_forward_ready: bool,
    blockers: list[str],
    oos_repair_classification: str = "not_run",
    low_vol_edge_classification: str = "not_run",
    presecurity_gate_classification: str = "not_run",
    broker_paper_stub_contract_classification: str = "not_run",
    broker_paper_dryrun_ledger_classification: str = "not_run",
    broker_paper_dryrun_risk_governor_classification: str = "not_run",
    broker_paper_dryrun_replay_harness_classification: str = "not_run",
) -> str:
    if broker_paper_dryrun_replay_harness_classification == "DRYRUN_REPLAY_HARNESS_READY":
        return "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1; broker-paper orders remain blocked."
    if broker_paper_dryrun_replay_harness_classification in {"FAIL", "WATCHLIST"}:
        return "Repair PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1 before dry-run replay evidence-gate work."
    if broker_paper_dryrun_risk_governor_classification == "DRYRUN_RISK_GOVERNOR_READY":
        return "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1; broker-paper orders remain blocked."
    if broker_paper_dryrun_risk_governor_classification in {"FAIL", "WATCHLIST"}:
        return "Repair PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1 before dry-run replay-harness work."
    if broker_paper_dryrun_ledger_classification == "DRYRUN_LEDGER_READY":
        return "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1; broker-paper orders remain blocked."
    if broker_paper_dryrun_ledger_classification in {"FAIL", "WATCHLIST"}:
        return "Repair PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1 before dry-run risk-governor work."
    if broker_paper_stub_contract_classification == "STUB_CONTRACT_READY":
        return "Proceed only to PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1; broker-paper orders remain blocked."
    if broker_paper_stub_contract_classification in {"FAIL", "WATCHLIST"}:
        return "Repair PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT before dry-run intent ledger work."
    if paper_forward_ready:
        return "Run the broker-paper pre-security gate before any adapter work; live readiness requires separate future approval."
    if presecurity_gate_classification == "PRESECURITY_READY":
        return "Proceed only to PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT; broker-paper orders remain blocked."
    if presecurity_gate_classification in {"FAIL", "WATCHLIST"}:
        return "Repair PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1 before any adapter-stub work."
    if low_vol_edge_classification == "WATCHLIST":
        return "Continue low-vol edge research before broker-paper readiness; live readiness requires separate future approval."
    if low_vol_edge_classification == "PAPER_FORWARD_READY" and any("presecurity" in blocker for blocker in blockers):
        return "Run PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1 before any broker-paper adapter work."
    if oos_repair_classification == "WATCHLIST":
        return "Run PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1 before broker-paper readiness."
    if blockers:
        return "Resolve V2 local evidence blockers before claiming paper-forward readiness; live readiness requires separate future approval."
    return "Collect stronger multi-regime local evidence and rerun V2 readiness review; live readiness requires separate future approval."
