from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


def build_forex_dashboard_state(
    strategy: str | dict[str, Any] = "local_close_momentum_v1",
    fixture: schemas.MarketDataFixture | dict[str, Any] | None = None,
    backtest_result: schemas.BacktestResult | dict[str, Any] | None = None,
    walk_forward_summary: schemas.WalkForwardSummary | dict[str, Any] | None = None,
    risk_gate: schemas.RiskGateResult | dict[str, Any] | None = None,
    paper_forward_summary: dict[str, Any] | None = None,
    blockers: list[str] | None = None,
    sos_required: bool = False,
    next_safe_action: str | None = None,
) -> schemas.DashboardState:
    active_blockers = list(blockers or [])
    active_blockers.extend(_blockers(risk_gate))
    active_blockers.extend(_blockers(walk_forward_summary))
    current_blocker = active_blockers[0] if active_blockers else "none"
    risk_status = _classification(risk_gate, default="not_run")
    paper_state = _paper_state(paper_forward_summary)
    state = schemas.DashboardState(
        current_phase="paper-forward evidence review",
        selected_strategy=_strategy_name(strategy),
        data_fixture_status="ready" if fixture is not None else "missing",
        backtest_status=_backtest_status(backtest_result),
        walk_forward_status=_classification(walk_forward_summary, default="not_run"),
        risk_gate_status=risk_status,
        paper_permission_state=paper_state,
        live_permission_state="blocked",
        current_blocker=current_blocker,
        sos_required=bool(sos_required),
        next_safe_action=next_safe_action
        or _next_safe_action(risk_status, paper_state, current_blocker),
        fixture_id=_fixture_id(fixture),
        readiness_status=_readiness_status(risk_status, paper_state, current_blocker),
    )
    schemas.validate_dashboard_state_schema(state)
    return state


def format_forex_dashboard_lines(state: schemas.DashboardState | dict[str, Any]) -> list[str]:
    payload = _payload(state)
    schemas.validate_dashboard_state_schema(payload)
    return [
        "FOREX BUILDER STATUS",
        f"Strategy: {payload['selected_strategy']}",
        f"Fixture: {payload.get('fixture_id', 'unknown')} ({payload['data_fixture_status']})",
        f"Backtest: {payload['backtest_status']} | Walk-forward: {payload['walk_forward_status']}",
        f"Risk gate: {payload['risk_gate_status']} | Readiness: {payload.get('readiness_status', 'WATCHLIST')}",
        f"Paper-forward: {payload['paper_permission_state']}",
        f"Blocker: {payload['current_blocker']}",
        f"SOS: {'yes' if payload['sos_required'] else 'no'}",
        f"Next: {payload['next_safe_action']}",
        "Safety: no broker/live/secrets/orders/webhooks",
    ]


def build_forex_dashboard_v2_summary(evidence_summary: dict[str, Any]) -> dict[str, Any]:
    payload = dict(evidence_summary)
    summary = {
        "schema": "AIOS_FOREX_BUILDER_DASHBOARD_V2_SUMMARY.v1",
        "fixture_count": int(payload.get("fixture_count", 0)),
        "regime_consistency_pct": float(payload.get("regime_consistency_pct", 0.0)),
        "paper_forward_classification": str(payload.get("classification") or "FAIL"),
        "aggregate_paper_pnl": float(payload.get("aggregate_paper_pnl", 0.0)),
        "return_pct": float(payload.get("return_pct", 0.0)),
        "capture_rate_pct": float(payload.get("capture_rate_pct", 0.0)),
        "risk_governor_classification": str(payload.get("risk_governor_classification") or payload.get("classification") or "FAIL"),
        "opportunity_quality_score": float(payload.get("opportunity_quality_score", 0.0)),
        "stress_classification": str(payload.get("stress_classification") or "not_run"),
        "oos_classification": str(payload.get("oos_classification") or "not_run"),
        "combined_stress_oos_classification": str(payload.get("combined_stress_oos_classification") or "not_run"),
        "heldout_consistency_pct": float(payload.get("heldout_consistency_pct", 0.0)),
        "degradation_pct": float(payload.get("degradation_pct", 0.0)),
        "stress_oos_ready": bool(payload.get("stress_oos_ready", False)),
        "stress_repair_status": str(payload.get("stress_repair_status") or "not_run"),
        "stress_repair_classification": str(payload.get("stress_repair_classification") or payload.get("repaired_stress_classification") or "not_run"),
        "repaired_worst_stress_pnl": float(payload.get("repaired_worst_stress_pnl", 0.0)),
        "expanded_oos_status": str(payload.get("expanded_oos_status") or payload.get("expanded_oos_classification") or "not_run"),
        "expanded_oos_classification": str(payload.get("expanded_oos_classification") or payload.get("expanded_oos_status") or "not_run"),
        "expanded_oos_heldout_consistency_pct": float(
            payload.get("expanded_oos_heldout_consistency_pct", payload.get("heldout_consistency_pct", 0.0))
        ),
        "expanded_oos_degradation_pct": float(
            payload.get("expanded_oos_degradation_pct", payload.get("degradation_pct", 0.0))
        ),
        "oos_repair_classification": str(payload.get("oos_repair_classification") or "not_run"),
        "low_vol_edge_classification": str(payload.get("low_vol_edge_classification") or "not_run"),
        "low_vol_policy_action": str(payload.get("low_vol_policy_action") or "not_run"),
        "original_max_degradation_pct": float(
            payload.get("original_max_degradation_pct", payload.get("expanded_oos_degradation_pct", 0.0))
        ),
        "repaired_max_degradation_pct": float(
            payload.get(
                "repaired_max_degradation_pct",
                payload.get("expanded_oos_degradation_pct", payload.get("degradation_pct", 0.0)),
            )
        ),
        "degradation_improvement_pct": float(payload.get("degradation_improvement_pct", 0.0)),
        "redesigned_max_degradation_pct": float(
            payload.get(
                "redesigned_max_degradation_pct",
                payload.get("repaired_max_degradation_pct", payload.get("expanded_oos_degradation_pct", 0.0)),
            )
        ),
        "low_vol_rejected_intents": int(
            payload.get("low_vol_rejected_intents", payload.get("rejected_low_vol_intents", 0))
        ),
        "presecurity_gate_classification": str(payload.get("presecurity_gate_classification") or "not_run"),
        "credential_boundary_required": bool(payload.get("credential_boundary_required", True)),
        "kill_switch_required": bool(payload.get("kill_switch_required", True)),
        "max_loss_guard_required": bool(payload.get("max_loss_guard_required", True)),
        "audit_log_required": bool(payload.get("audit_log_required", True)),
        "broker_paper_stub_contract_classification": str(
            payload.get("broker_paper_stub_contract_classification") or "not_run"
        ),
        "broker_paper_stub_contract_ready": bool(payload.get("broker_paper_stub_contract_ready", False)),
        "broker_paper_dryrun_ledger_classification": str(
            payload.get("broker_paper_dryrun_ledger_classification") or "not_run"
        ),
        "broker_paper_dryrun_ledger_ready": bool(payload.get("broker_paper_dryrun_ledger_ready", False)),
        "dryrun_ledger_records": int(payload.get("dryrun_ledger_records", payload.get("records_count", 0))),
        "dryrun_ledger_accepted": int(payload.get("dryrun_ledger_accepted", payload.get("accepted_count", 0))),
        "dryrun_ledger_rejected": int(payload.get("dryrun_ledger_rejected", payload.get("rejected_count", 0))),
        "broker_paper_dryrun_risk_governor_classification": str(
            payload.get("broker_paper_dryrun_risk_governor_classification") or "not_run"
        ),
        "broker_paper_dryrun_risk_governor_ready": bool(
            payload.get("broker_paper_dryrun_risk_governor_ready", False)
        ),
        "dryrun_risk_records": int(payload.get("dryrun_risk_records", payload.get("risk_records", 0))),
        "dryrun_risk_accepted": int(payload.get("dryrun_risk_accepted", payload.get("risk_accepted", 0))),
        "dryrun_risk_rejected": int(payload.get("dryrun_risk_rejected", payload.get("risk_rejected", 0))),
        "aggregate_max_loss_usd": float(payload.get("aggregate_max_loss_usd", 0.0)),
        "max_daily_loss_usd": float(payload.get("max_daily_loss_usd", 5.0)),
        "kill_switch_armed": bool(payload.get("kill_switch_armed", True)),
        "broker_paper_dryrun_replay_harness_classification": str(
            payload.get("broker_paper_dryrun_replay_harness_classification") or "not_run"
        ),
        "broker_paper_dryrun_replay_harness_ready": bool(
            payload.get("broker_paper_dryrun_replay_harness_ready", False)
        ),
        "replay_records": int(payload.get("replay_records", payload.get("records_replayed", 0))),
        "replay_stub_accepted": int(payload.get("replay_stub_accepted", payload.get("stub_accepted", 0))),
        "replay_stub_rejected": int(payload.get("replay_stub_rejected", payload.get("stub_rejected", 0))),
        "replay_risk_accepted": int(payload.get("replay_risk_accepted", payload.get("risk_accepted", 0))),
        "replay_risk_rejected": int(payload.get("replay_risk_rejected", payload.get("risk_rejected", 0))),
        "broker_paper_dryrun_replay_evidence_gate_classification": str(
            payload.get("broker_paper_dryrun_replay_evidence_gate_classification") or "not_run"
        ),
        "broker_paper_dryrun_replay_evidence_gate_ready": bool(
            payload.get("broker_paper_dryrun_replay_evidence_gate_ready", False)
        ),
        "replay_evidence_records": int(
            payload.get("replay_evidence_records", payload.get("records_replayed", 0))
        ),
        "replay_evidence_stub_accepted": int(
            payload.get("replay_evidence_stub_accepted", payload.get("stub_accepted", 0))
        ),
        "replay_evidence_stub_rejected": int(
            payload.get("replay_evidence_stub_rejected", payload.get("stub_rejected", 0))
        ),
        "replay_evidence_risk_accepted": int(
            payload.get("replay_evidence_risk_accepted", payload.get("risk_accepted", 0))
        ),
        "replay_evidence_risk_rejected": int(
            payload.get("replay_evidence_risk_rejected", payload.get("risk_rejected", 0))
        ),
        "replay_evidence_eom_milestone_status": str(
            payload.get("replay_evidence_eom_milestone_status") or "not_run"
        ),
        "broker_paper_orders_allowed": False,
        "credentials_allowed": False,
        "network_api_allowed": False,
        "weakest_oos_split": str(payload.get("weakest_oos_split") or payload.get("weakest_split") or "none"),
        "broker_paper_sandbox_readiness_status": str(
            payload.get("broker_paper_sandbox_readiness_status") or "not_run"
        ),
        "broker_paper_sandbox_contract_ready": bool(
            payload.get("broker_paper_sandbox_contract_ready", False)
        ),
        "broker_paper_contract_ready": bool(
            payload.get("broker_paper_contract_ready", payload.get("broker_paper_sandbox_contract_ready", False))
        ),
        "readiness_status": str(payload.get("readiness_status") or payload.get("classification") or "FAIL"),
        "live_ready": False,
        "live_trade_ready": False,
        "protected_gate_required": True,
        "current_blocker": _current_blocker(payload.get("blockers")),
        "next_safe_action": str(payload.get("next_safe_action") or "Continue local evidence review; live remains blocked."),
        "safety": "no broker/live/secrets/orders/webhooks",
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def format_forex_dashboard_v2_lines(summary: dict[str, Any]) -> list[str]:
    payload = dict(summary)
    return [
        "FOREX BUILDER V2 STATUS",
        f"Fixtures: {payload.get('fixture_count', 0)} | Regime consistency: {payload.get('regime_consistency_pct', 0.0)}",
        (
            f"Paper-forward: {payload.get('paper_forward_classification', 'FAIL')} | "
            f"Risk governor: {payload.get('risk_governor_classification', 'FAIL')}"
        ),
        (
            f"Stress/OOS: {payload.get('combined_stress_oos_classification', 'not_run')} | "
            f"Repair: {payload.get('stress_repair_classification', 'not_run')} | "
            f"OOS+: {payload.get('expanded_oos_classification', 'not_run')} | "
            f"OOS repair: {payload.get('oos_repair_classification', 'not_run')} | "
            f"Low-vol: {payload.get('low_vol_edge_classification', 'not_run')}/"
            f"{payload.get('low_vol_policy_action', 'not_run')} | "
            f"Repaired degradation: {payload.get('repaired_max_degradation_pct', payload.get('expanded_oos_degradation_pct', 0.0))} | "
            f"Redesigned: {payload.get('redesigned_max_degradation_pct', payload.get('repaired_max_degradation_pct', 0.0))} | "
            f"Weakest: {payload.get('weakest_oos_split', 'none')}"
        ),
        (
            f"Sandbox contract: {payload.get('broker_paper_sandbox_readiness_status', 'not_run')} | "
            f"Presecurity: {payload.get('presecurity_gate_classification', 'not_run')} | "
            f"Stub: {payload.get('broker_paper_stub_contract_classification', 'not_run')} | "
            f"Ledger: {payload.get('broker_paper_dryrun_ledger_classification', 'not_run')}/"
            f"{payload.get('dryrun_ledger_records', 0)} | "
            f"Risk gov: {payload.get('broker_paper_dryrun_risk_governor_classification', 'not_run')}/"
            f"{payload.get('dryrun_risk_accepted', 0)}-{payload.get('dryrun_risk_rejected', 0)} | "
            f"Replay: {payload.get('broker_paper_dryrun_replay_harness_classification', 'not_run')}/"
            f"{payload.get('replay_stub_accepted', 0)}-{payload.get('replay_stub_rejected', 0)}/"
            f"{payload.get('replay_risk_accepted', 0)}-{payload.get('replay_risk_rejected', 0)} | "
            f"Evidence: {payload.get('broker_paper_dryrun_replay_evidence_gate_classification', 'not_run')}/"
            f"{payload.get('replay_evidence_records', 0)} | "
            f"Repaired worst PnL: {payload.get('repaired_worst_stress_pnl', 0.0)}"
        ),
        f"PnL: {payload.get('aggregate_paper_pnl', 0.0)} | Return pct: {payload.get('return_pct', 0.0)}",
        f"Capture: {payload.get('capture_rate_pct', 0.0)} | Quality: {payload.get('opportunity_quality_score', 0.0)}",
        f"Readiness: {payload.get('readiness_status', 'FAIL')} | Live ready: false | Protected gate required: true",
        f"Next: {payload.get('next_safe_action')}",
        "Safety: no broker/live/secrets/orders/webhooks",
    ]


def dashboard_contract_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_BUILDER_DASHBOARD_CONTRACT.v1",
        "compact_default": True,
        "max_default_lines": 10,
        "reports_written_by_default": False,
        "fields": [
            "strategy",
            "fixture",
            "backtest",
            "walk_forward",
            "risk_gate",
            "paper_forward",
            "broker_paper_dryrun_replay_evidence_gate",
            "readiness",
            "blockers",
            "sos",
            "next_safe_action",
        ],
        "live_permission_state": "blocked",
        "safety": "no broker/live/secrets/orders/webhooks",
    }


def _payload(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _optional_payload(value: Any | None) -> dict[str, Any]:
    if value in (None, "", [], {}):
        return {}
    return _payload(value)


def _strategy_name(strategy: str | dict[str, Any]) -> str:
    if isinstance(strategy, dict):
        return str(strategy.get("strategy_id") or strategy.get("strategy_name") or "unknown_strategy")
    return str(strategy)


def _classification(value: Any | None, default: str) -> str:
    payload = _optional_payload(value)
    return str(payload.get("classification") or payload.get("status") or default)


def _blockers(value: Any | None) -> list[str]:
    payload = _optional_payload(value)
    raw = payload.get("blockers") or []
    return [str(item) for item in raw] if isinstance(raw, list) else [str(raw)]


def _backtest_status(value: Any | None) -> str:
    payload = _optional_payload(value)
    if not payload:
        return "not_run"
    total_trades = int(payload.get("total_trades", 0))
    return "ready" if total_trades > 0 else "no_trades"


def _fixture_id(value: Any | None) -> str:
    payload = _optional_payload(value)
    return str(payload.get("fixture_id") or "missing")


def _paper_state(summary: dict[str, Any] | None) -> str:
    payload = summary or {}
    if payload.get("total_entries", 0):
        return "simulated_local_only"
    if payload.get("classification"):
        return str(payload["classification"])
    return "not_started"


def _readiness_status(risk_status: str, paper_state: str, blocker: str) -> str:
    if risk_status == "FAIL":
        return "FAIL"
    if blocker != "none":
        return "WATCHLIST"
    if risk_status == "PAPER_FORWARD_READY" and paper_state == "simulated_local_only":
        return "PAPER_FORWARD_READY"
    return "WATCHLIST"


def _next_safe_action(risk_status: str, paper_state: str, blocker: str) -> str:
    if blocker != "none":
        return "Resolve blocker before promotion; keep report-only."
    if risk_status == "PAPER_FORWARD_READY" and paper_state == "simulated_local_only":
        return "Expand local paper-forward evidence; live remains blocked."
    if risk_status == "PAPER_FORWARD_READY":
        return "Run local paper-forward simulator; no broker or live path."
    return "Run risk gate and collect stronger local evidence."


def _current_blocker(value: Any) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    if value in (None, "", {}, []):
        return "none"
    return str(value)
