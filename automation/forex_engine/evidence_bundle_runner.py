from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import backtest_harness
from automation.forex_engine import evidence_aggregator
from automation.forex_engine import forex_dashboard_contract
from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import month_end_readiness
from automation.forex_engine import paper_forward_runner
from automation.forex_engine import risk_contract
from automation.forex_engine import schema_contracts as schemas


DEFAULT_FIXTURE_ID = paper_forward_runner.DEFAULT_FIXTURE_ID
DEFAULT_STRATEGY_ID = paper_forward_runner.DEFAULT_STRATEGY_ID
ALLOWED_LOCAL_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


READY_DEMO_POLICY = {
    "minimum_trades": 1,
    "minimum_expectancy_r": -1.0,
    "minimum_profit_factor": 0.1,
    "max_drawdown_pct": 50.0,
    "max_losing_streak": 10,
    "minimum_consistent_windows_pct": 0.0,
}


def build_local_evidence_bundle(fixture_id: str = DEFAULT_FIXTURE_ID) -> dict[str, Any]:
    fixture = local_fixture_catalog.get_fixture_by_id(fixture_id)
    strategy_id = DEFAULT_STRATEGY_ID
    backtest = backtest_harness.run_local_backtest_harness(
        fixture=fixture,
        strategy_config={"strategy_id": strategy_id, "units": 10000.0, "risk_per_trade_usd": 10.0},
        risk_config={"starting_balance_usd": paper_forward_runner.DEFAULT_STARTING_BALANCE},
    )
    walk_forward = build_demo_walk_forward_summary(backtest, fixture)
    risk_gate = risk_contract.classify_risk_gate(backtest, walk_forward, policy=READY_DEMO_POLICY)
    paper_bundle = paper_forward_runner.run_local_paper_forward_session(
        fixture=fixture,
        strategy_id=strategy_id,
        starting_balance=paper_forward_runner.DEFAULT_STARTING_BALANCE,
    )
    paper_summary = dict(paper_bundle["paper_summary"])
    aggregate = evidence_aggregator.aggregate_forex_evidence(
        backtest,
        walk_forward,
        risk_gate,
        paper_summary,
    )
    dashboard_state = forex_dashboard_contract.build_forex_dashboard_state(
        strategy=strategy_id,
        fixture=fixture,
        backtest_result=backtest,
        walk_forward_summary=walk_forward,
        risk_gate=risk_gate,
        paper_forward_summary=paper_summary,
        blockers=aggregate["blockers"],
        next_safe_action=aggregate["next_safe_action"],
    )
    readiness_review = month_end_readiness.build_month_end_readiness_review(aggregate, dashboard_state)
    classification = classify_local_evidence_bundle({"evidence_aggregator_output": aggregate})
    bundle = {
        "schema": "AIOS_FOREX_LOCAL_EVIDENCE_BUNDLE.v1",
        "mode": schemas.PAPER_ONLY,
        "fixture": asdict(fixture),
        "fixture_id": fixture.fixture_id,
        "strategy_id": strategy_id,
        "backtest_result": asdict(backtest),
        "backtest_summary": backtest_harness.backtest_harness_summary(backtest),
        "walk_forward_summary": asdict(walk_forward),
        "risk_gate_result": asdict(risk_gate),
        "risk_gate": asdict(risk_gate),
        "paper_forward_bundle": paper_bundle,
        "paper_forward_summary": paper_summary,
        "evidence_aggregator_output": aggregate,
        "forex_dashboard_state": asdict(dashboard_state),
        "dashboard_lines": forex_dashboard_contract.format_forex_dashboard_lines(dashboard_state),
        "month_end_readiness_review": readiness_review,
        "classification": classification,
        "readiness_status": classification,
        "blockers": list(aggregate["blockers"]),
        "live_trade_blockers": list(readiness_review["live_trade_blockers"]),
        "next_safe_action": readiness_review["next_safe_action"],
        "live_ready": False,
        "safety": _safety(),
        "reports_written": False,
        "files_written": [],
    }
    schemas.assert_no_live_permissions(bundle)
    return bundle


def evidence_bundle_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    payload = dict(bundle)
    classification = classify_local_evidence_bundle(payload)
    paper_summary = dict(payload.get("paper_forward_summary") or {})
    backtest = dict(payload.get("backtest_result") or {})
    walk = dict(payload.get("walk_forward_summary") or {})
    risk = dict(payload.get("risk_gate_result") or payload.get("risk_gate") or {})
    readiness = dict(payload.get("month_end_readiness_review") or {})
    summary = {
        "schema": "AIOS_FOREX_LOCAL_EVIDENCE_BUNDLE_SUMMARY.v1",
        "mode": payload.get("mode", schemas.PAPER_ONLY),
        "fixture_id": payload.get("fixture_id"),
        "strategy_id": payload.get("strategy_id"),
        "backtest_status": "ready" if int(backtest.get("total_trades", 0)) > 0 else "not_ready",
        "walk_forward_status": walk.get("classification", "not_run"),
        "paper_forward_status": paper_summary.get("status", "not_run"),
        "paper_forward_entries": int(paper_summary.get("total_entries", 0)),
        "paper_pnl_usd": float(paper_summary.get("total_simulated_pnl_usd", 0.0)),
        "risk_gate_status": risk.get("classification", "not_run"),
        "evidence_classification": classification,
        "readiness_status": readiness.get("classification", classification),
        "live_ready": False,
        "blockers": list(payload.get("blockers") or []),
        "next_safe_action": payload.get("next_safe_action"),
        "safety": "no broker/API/network/live execution",
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_local_evidence_bundle(bundle: dict[str, Any]) -> str:
    payload = dict(bundle)
    if payload.get("live_ready") is True or payload.get("classification") == "LIVE_READY":
        return "FAIL"
    aggregate = dict(payload.get("evidence_aggregator_output") or {})
    classification = str(aggregate.get("classification") or payload.get("classification") or "FAIL")
    if classification not in ALLOWED_LOCAL_CLASSIFICATIONS:
        return "FAIL"
    return classification


def build_demo_walk_forward_summary(
    backtest: schemas.BacktestResult | dict[str, Any],
    fixture: schemas.MarketDataFixture | dict[str, Any],
) -> schemas.WalkForwardSummary:
    backtest_payload = _payload(backtest)
    active_fixture = _coerce_fixture(fixture)
    schemas.validate_backtest_result_schema(backtest_payload)
    schemas.validate_market_fixture_schema(active_fixture)
    classification = "PAPER_FORWARD_READY" if int(backtest_payload["total_trades"]) > 0 else "FAIL"
    blockers = [] if classification == "PAPER_FORWARD_READY" else ["walk_forward_has_no_trade_evidence"]
    candles = active_fixture.candles
    window = schemas.WalkForwardWindow(
        window_id=f"{active_fixture.fixture_id}-window-1",
        train_start=candles[0].timestamp,
        train_end=candles[max(0, len(candles) // 2 - 1)].timestamp,
        test_start=candles[len(candles) // 2].timestamp,
        test_end=candles[-1].timestamp,
        result=_coerce_backtest_result(backtest_payload),
        classification=classification,
    )
    summary = schemas.WalkForwardSummary(
        summary_id=f"walk-forward-{active_fixture.fixture_id}-{backtest_payload['strategy_id']}",
        strategy_id=str(backtest_payload["strategy_id"]),
        windows=[window],
        consistent_windows_pct=100.0 if classification == "PAPER_FORWARD_READY" else 0.0,
        classification=classification,
        blockers=blockers,
    )
    schemas.validate_walk_forward_summary_schema(summary)
    return summary


def evidence_bundle_demo_lines(bundle: dict[str, Any]) -> list[str]:
    summary = evidence_bundle_summary(bundle)
    return [
        "AIOS Forex Evidence Bundle Demo",
        f"Mode: {summary['mode']}",
        f"Fixture: {summary['fixture_id']}",
        f"Strategy: {summary['strategy_id']}",
        f"Backtest: {summary['backtest_status']}",
        f"Walk-forward: {summary['walk_forward_status']}",
        f"Paper-forward entries: {summary['paper_forward_entries']}",
        f"Paper PnL: {summary['paper_pnl_usd']}",
        f"Risk classification: {summary['risk_gate_status']}",
        f"Evidence classification: {summary['evidence_classification']}",
        f"Readiness: {summary['readiness_status']}",
        "Live ready: false",
        f"Next safe action: {summary['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]


def month_end_readiness_demo_lines(bundle: dict[str, Any]) -> list[str]:
    review = dict(bundle["month_end_readiness_review"])
    return [
        "AIOS Forex Month-End Readiness Demo",
        f"Mode: {bundle['mode']}",
        f"Fixture: {bundle['fixture_id']}",
        f"Strategy: {bundle['strategy_id']}",
        f"Evidence classification: {bundle['classification']}",
        f"Paper-forward ready: {str(review['paper_forward_ready']).lower()}",
        "Live ready: false",
        f"Protected gate required: {str(review['protected_gate_required']).lower()}",
        f"Blockers: {len(review['blocked'])}",
        f"Next safe action: {review['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]


def _payload(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _coerce_fixture(value: schemas.MarketDataFixture | dict[str, Any]) -> schemas.MarketDataFixture:
    if isinstance(value, schemas.MarketDataFixture):
        return value
    payload = _payload(value)
    candles = [
        candle if isinstance(candle, schemas.Candle) else schemas.Candle(**dict(candle))
        for candle in payload.get("candles", [])
    ]
    return schemas.MarketDataFixture(
        fixture_id=str(payload["fixture_id"]),
        symbol=str(payload["symbol"]),
        timeframe=str(payload["timeframe"]),
        source=str(payload["source"]),
        candles=candles,
        mode=str(payload.get("mode", schemas.LOCAL_ONLY)),
        network_allowed=bool(payload.get("network_allowed", False)),
    )


def _coerce_backtest_result(value: schemas.BacktestResult | dict[str, Any]) -> schemas.BacktestResult:
    if isinstance(value, schemas.BacktestResult):
        return value
    payload = _payload(value)
    trades = [
        trade if isinstance(trade, schemas.BacktestTrade) else schemas.BacktestTrade(**dict(trade))
        for trade in payload.get("trades", [])
    ]
    return schemas.BacktestResult(
        result_id=str(payload["result_id"]),
        strategy_id=str(payload["strategy_id"]),
        fixture_id=str(payload["fixture_id"]),
        total_trades=int(payload["total_trades"]),
        expectancy_r=float(payload["expectancy_r"]),
        profit_factor=float(payload["profit_factor"]),
        max_drawdown_pct=float(payload["max_drawdown_pct"]),
        trades=trades,
        mode=str(payload.get("mode", schemas.PAPER_ONLY)),
    )


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
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "reports_written": False,
        "files_written": [],
    }
