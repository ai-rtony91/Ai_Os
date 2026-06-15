from __future__ import annotations

from typing import Any

from automation.forex_engine import paper_forward_runner
from automation.forex_engine import schema_contracts as schemas


DEFAULT_STARTING_BALANCE = paper_forward_runner.DEFAULT_STARTING_BALANCE
DEFAULT_ESTIMATED_ROUND_TURN_COST_USD = 0.25


def calculate_opportunity_capture(evidence_bundle: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    active_policy = dict(policy or {})
    summary = _multi_summary(evidence_bundle)
    per_fixture_results = _per_fixture_results(evidence_bundle)
    starting_balance = float(active_policy.get("starting_balance", DEFAULT_STARTING_BALANCE))
    aggregate_pnl = round(float(summary.get("aggregate_pnl") or summary.get("aggregate_pnl_usd") or 0.0), 4)
    total_intents = int(summary.get("total_intents", 0))
    simulated_entries = int(summary.get("total_ledger_entries", 0))
    missed = estimate_missed_opportunities(per_fixture_results)
    missed_signal_count = int(missed["missed_signal_count"])
    missed_pnl_estimate = calculate_missed_pnl_estimate(per_fixture_results)
    capture_rate_pct = calculate_capture_rate(total_intents, simulated_entries, missed_signal_count)
    ending_balance = round(starting_balance + aggregate_pnl, 4)
    return_pct = round((aggregate_pnl / starting_balance) * 100, 4) if starting_balance else 0.0
    max_drawdown_pct = _max_drawdown_pct(starting_balance, per_fixture_results)
    cost_drag = calculate_cost_drag(
        {
            **summary,
            "aggregate_paper_pnl": aggregate_pnl,
            "simulated_ledger_entries": simulated_entries,
            "estimated_round_turn_cost_usd": active_policy.get(
                "estimated_round_turn_cost_usd",
                DEFAULT_ESTIMATED_ROUND_TURN_COST_USD,
            ),
        }
    )
    risk_adjusted_return = calculate_risk_adjusted_return(
        {
            "return_pct": return_pct,
            "max_drawdown_pct": max_drawdown_pct,
            "cost_drag_pct": cost_drag["cost_drag_pct"],
        }
    )
    exit_efficiency = calculate_exit_efficiency(per_fixture_results)
    position_efficiency = calculate_position_efficiency(per_fixture_results)
    overtrade_ratio = round(simulated_entries / max(1, total_intents + missed_signal_count), 4)
    missed_pnl_pct = _missed_pnl_pct(aggregate_pnl, missed_pnl_estimate)
    report = {
        "schema": "AIOS_FOREX_OPPORTUNITY_CAPTURE.v1",
        "mode": schemas.PAPER_ONLY,
        "total_intents": total_intents,
        "simulated_ledger_entries": simulated_entries,
        "missed_signal_count": missed_signal_count,
        "missed_pnl_estimate": missed_pnl_estimate,
        "missed_pnl_pct": missed_pnl_pct,
        "capture_rate_pct": capture_rate_pct,
        "aggregate_paper_pnl": aggregate_pnl,
        "starting_balance": round(starting_balance, 4),
        "ending_balance": ending_balance,
        "return_pct": return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "cost_drag_usd": cost_drag["cost_drag_usd"],
        "cost_drag_pct": cost_drag["cost_drag_pct"],
        "risk_adjusted_return": risk_adjusted_return,
        "exit_efficiency_pct": exit_efficiency["exit_efficiency_pct"],
        "position_efficiency_pct": position_efficiency["position_efficiency_pct"],
        "overtrade_ratio": overtrade_ratio,
        "estimated": True,
        "estimation_reason": _estimation_reason(evidence_bundle),
        "missed_opportunities": missed,
        "cost_drag": cost_drag,
        "exit_efficiency": exit_efficiency,
        "position_efficiency": position_efficiency,
        "blockers": _opportunity_blockers(total_intents, simulated_entries, aggregate_pnl),
        "live_ready": False,
        "protected_gate_required": True,
        "safety": _safety(),
    }
    report["opportunity_quality_score"] = calculate_opportunity_quality_score(report)
    report["next_safe_action"] = _next_safe_action(report)
    schemas.assert_no_live_permissions(report)
    return report


def estimate_missed_opportunities(per_fixture_results: list[dict[str, Any]]) -> dict[str, Any]:
    missed_by_fixture = []
    missed_signal_count = 0
    for item in per_fixture_results:
        intent_count = int(item.get("intent_count", 0))
        ledger_entry_count = int(item.get("ledger_entry_count", 0))
        missed = max(0, intent_count - ledger_entry_count)
        if intent_count > 0 and ledger_entry_count == 0:
            missed += 1
        missed_signal_count += missed
        if missed:
            missed_by_fixture.append(
                {
                    "fixture_id": item.get("fixture_id"),
                    "missed_signal_count": missed,
                    "estimated": True,
                }
            )
    return {
        "schema": "AIOS_FOREX_MISSED_OPPORTUNITY_ESTIMATE.v1",
        "mode": schemas.PAPER_ONLY,
        "missed_signal_count": missed_signal_count,
        "missed_by_fixture": missed_by_fixture,
        "estimated": True,
        "estimation_reason": "No rejected-signal ledger exists yet; missed signals are conservatively estimated from intent/ledger gaps.",
        "live_ready": False,
    }


def calculate_capture_rate(total_intents: int, simulated_entries: int, missed_count: int = 0) -> float:
    denominator = max(1, int(total_intents) + int(missed_count))
    return round((int(simulated_entries) / denominator) * 100, 4)


def calculate_missed_pnl_estimate(per_fixture_results: list[dict[str, Any]]) -> float:
    captured_entries = sum(int(item.get("ledger_entry_count", 0)) for item in per_fixture_results)
    aggregate_pnl = sum(float(item.get("paper_pnl_usd", 0.0)) for item in per_fixture_results)
    missed = estimate_missed_opportunities(per_fixture_results)["missed_signal_count"]
    if missed <= 0 or captured_entries <= 0 or aggregate_pnl <= 0:
        return 0.0
    average_captured_pnl = aggregate_pnl / captured_entries
    return round(average_captured_pnl * missed * 0.5, 4)


def calculate_cost_drag(summary: dict[str, Any]) -> dict[str, Any]:
    entries = int(summary.get("simulated_ledger_entries") or summary.get("total_ledger_entries") or 0)
    aggregate_pnl = abs(float(summary.get("aggregate_paper_pnl") or summary.get("aggregate_pnl") or 0.0))
    if "cost_drag_usd" in summary:
        cost_drag_usd = float(summary["cost_drag_usd"])
        estimated = bool(summary.get("estimated", False))
    else:
        estimated_cost = float(summary.get("estimated_round_turn_cost_usd", DEFAULT_ESTIMATED_ROUND_TURN_COST_USD))
        cost_drag_usd = round(entries * estimated_cost, 4)
        estimated = True
    denominator = aggregate_pnl + cost_drag_usd
    cost_drag_pct = round((cost_drag_usd / denominator) * 100, 4) if denominator else 0.0
    return {
        "schema": "AIOS_FOREX_COST_DRAG_ESTIMATE.v1",
        "mode": schemas.PAPER_ONLY,
        "cost_drag_usd": round(cost_drag_usd, 4),
        "cost_drag_pct": cost_drag_pct,
        "estimated": estimated,
        "estimation_reason": "Local deterministic round-turn cost approximation; no broker spread/slippage feed is used.",
        "live_ready": False,
    }


def calculate_risk_adjusted_return(summary: dict[str, Any]) -> float:
    return_pct = float(summary.get("return_pct", 0.0))
    drawdown_pct = max(0.0, float(summary.get("max_drawdown_pct", 0.0)))
    cost_drag_pct = max(0.0, float(summary.get("cost_drag_pct", 0.0)))
    denominator = 1.0 + (drawdown_pct / 100.0) + (cost_drag_pct / 100.0)
    return round((return_pct / 100.0) / denominator, 4) if denominator else 0.0


def calculate_exit_efficiency(per_fixture_results: list[dict[str, Any]]) -> dict[str, Any]:
    positive_pnl = sum(max(0.0, float(item.get("paper_pnl_usd", 0.0))) for item in per_fixture_results)
    negative_pnl = abs(sum(min(0.0, float(item.get("paper_pnl_usd", 0.0))) for item in per_fixture_results))
    denominator = positive_pnl + negative_pnl
    efficiency = round((positive_pnl / denominator) * 100, 4) if denominator else 0.0
    return {
        "schema": "AIOS_FOREX_EXIT_EFFICIENCY_ESTIMATE.v1",
        "mode": schemas.PAPER_ONLY,
        "exit_efficiency_pct": efficiency,
        "estimated": True,
        "estimation_reason": "Per-trade ideal exit labels are not available; estimate uses positive versus adverse fixture PnL.",
        "live_ready": False,
    }


def calculate_position_efficiency(per_fixture_results: list[dict[str, Any]]) -> dict[str, Any]:
    entries = sum(int(item.get("ledger_entry_count", 0)) for item in per_fixture_results)
    aggregate_pnl = sum(float(item.get("paper_pnl_usd", 0.0)) for item in per_fixture_results)
    if entries <= 0 or aggregate_pnl <= 0:
        efficiency = 0.0
    else:
        average_pnl = aggregate_pnl / entries
        efficiency = round(min(100.0, max(0.0, average_pnl / max(0.01, average_pnl) * 100.0)), 4)
    return {
        "schema": "AIOS_FOREX_POSITION_EFFICIENCY_ESTIMATE.v1",
        "mode": schemas.PAPER_ONLY,
        "position_efficiency_pct": efficiency,
        "estimated": True,
        "estimation_reason": "Position sizing is fixed-unit in local fixtures; efficiency is conservative until variable sizing exists.",
        "live_ready": False,
    }


def calculate_opportunity_quality_score(report: dict[str, Any]) -> float:
    capture = _clamp_pct(float(report.get("capture_rate_pct", 0.0)))
    exit_efficiency = _clamp_pct(float(report.get("exit_efficiency_pct", 0.0)))
    position_efficiency = _clamp_pct(float(report.get("position_efficiency_pct", 0.0)))
    risk_adjusted = _clamp_pct(float(report.get("risk_adjusted_return", 0.0)) * 50.0)
    cost_score = _clamp_pct(100.0 - float(report.get("cost_drag_pct", 0.0)) * 2.0)
    drawdown_score = _clamp_pct(100.0 - float(report.get("max_drawdown_pct", 0.0)) * 5.0)
    missed_score = _clamp_pct(100.0 - float(report.get("missed_pnl_pct", 0.0)) * 2.0)
    score = (
        capture * 0.25
        + exit_efficiency * 0.15
        + position_efficiency * 0.10
        + risk_adjusted * 0.15
        + cost_score * 0.15
        + drawdown_score * 0.10
        + missed_score * 0.10
    )
    return round(score, 4)


def opportunity_capture_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "schema": "AIOS_FOREX_OPPORTUNITY_CAPTURE_SUMMARY.v1",
        "mode": report.get("mode", schemas.PAPER_ONLY),
        "starting_balance": float(report.get("starting_balance", DEFAULT_STARTING_BALANCE)),
        "ending_balance": float(report.get("ending_balance", DEFAULT_STARTING_BALANCE)),
        "aggregate_paper_pnl": float(report.get("aggregate_paper_pnl", 0.0)),
        "return_pct": float(report.get("return_pct", 0.0)),
        "capture_rate_pct": float(report.get("capture_rate_pct", 0.0)),
        "missed_signal_count": int(report.get("missed_signal_count", 0)),
        "missed_pnl_estimate": float(report.get("missed_pnl_estimate", 0.0)),
        "cost_drag_pct": float(report.get("cost_drag_pct", 0.0)),
        "risk_adjusted_return": float(report.get("risk_adjusted_return", 0.0)),
        "max_drawdown_pct": float(report.get("max_drawdown_pct", 0.0)),
        "exit_efficiency_pct": float(report.get("exit_efficiency_pct", 0.0)),
        "position_efficiency_pct": float(report.get("position_efficiency_pct", 0.0)),
        "opportunity_quality_score": float(report.get("opportunity_quality_score", 0.0)),
        "overtrade_ratio": float(report.get("overtrade_ratio", 0.0)),
        "estimated": bool(report.get("estimated", True)),
        "blockers": list(report.get("blockers") or []),
        "live_ready": False,
        "protected_gate_required": True,
        "next_safe_action": report.get("next_safe_action"),
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def _multi_summary(evidence_bundle: dict[str, Any]) -> dict[str, Any]:
    return dict(evidence_bundle.get("multi_fixture_paper_forward_summary") or {})


def _per_fixture_results(evidence_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    multi = dict(evidence_bundle.get("multi_fixture_paper_forward") or {})
    summary = _multi_summary(evidence_bundle)
    return list(multi.get("per_fixture_results") or summary.get("per_fixture_results") or [])


def _max_drawdown_pct(starting_balance: float, per_fixture_results: list[dict[str, Any]]) -> float:
    equity = float(starting_balance)
    peak = equity
    max_drawdown = 0.0
    for item in per_fixture_results:
        equity += float(item.get("paper_pnl_usd", 0.0))
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return round((max_drawdown / starting_balance) * 100, 4) if starting_balance else 0.0


def _missed_pnl_pct(aggregate_pnl: float, missed_pnl: float) -> float:
    denominator = max(0.0, aggregate_pnl) + max(0.0, missed_pnl)
    return round((max(0.0, missed_pnl) / denominator) * 100, 4) if denominator else 0.0


def _opportunity_blockers(total_intents: int, simulated_entries: int, aggregate_pnl: float) -> list[str]:
    blockers = []
    if total_intents <= 0:
        blockers.append("opportunity_capture_no_intents")
    if simulated_entries <= 0:
        blockers.append("opportunity_capture_no_simulated_entries")
    if aggregate_pnl <= 0:
        blockers.append("opportunity_capture_non_positive_pnl")
    return blockers


def _estimation_reason(evidence_bundle: dict[str, Any]) -> str:
    if evidence_bundle.get("missed_opportunity_source") and evidence_bundle.get("cost_model"):
        return "Exact missed-opportunity and cost fields were supplied by the evidence bundle."
    return "Missed opportunities, cost drag, drawdown, and exit efficiency use deterministic local estimates; no broker or network data is used."


def _next_safe_action(report: dict[str, Any]) -> str:
    if report["blockers"]:
        return "Repair local opportunity-capture blockers before threshold promotion."
    return "Evaluate risk-governor thresholds and stress scenarios; keep broker and live trading blocked."


def _clamp_pct(value: float) -> float:
    return round(min(100.0, max(0.0, value)), 4)


def _safety() -> dict[str, Any]:
    return {
        "local_simulation_only": True,
        "broker_allowed": False,
        "broker_paper_orders": False,
        "network_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "live_trading": False,
        "live_ready": False,
        "orders_allowed": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "reports_written": False,
        "files_written": [],
    }
