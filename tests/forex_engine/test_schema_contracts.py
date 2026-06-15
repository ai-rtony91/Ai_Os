from __future__ import annotations

from pathlib import Path

import pytest

from automation.forex_engine import schema_contracts as schemas


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "schema_contracts.py"


def candle() -> schemas.Candle:
    return schemas.Candle(
        timestamp="2026-06-15T00:00:00Z",
        open=1.1000,
        high=1.1050,
        low=1.0950,
        close=1.1020,
        volume=1000,
    )


def trade() -> schemas.BacktestTrade:
    return schemas.BacktestTrade(
        trade_id="trade-1",
        symbol="EURUSD",
        direction="BUY",
        entry_time="2026-06-15T00:00:00Z",
        exit_time="2026-06-15T01:00:00Z",
        entry_price=1.1000,
        exit_price=1.1050,
        units=1000,
        pnl_usd=5.0,
        r_multiple=1.5,
    )


def backtest_result() -> schemas.BacktestResult:
    return schemas.BacktestResult(
        result_id="result-1",
        strategy_id="supertrend_pullback_v1",
        fixture_id="fixture-1",
        total_trades=1,
        expectancy_r=1.5,
        profit_factor=2.0,
        max_drawdown_pct=1.0,
        trades=[trade()],
    )


def walk_forward_window() -> schemas.WalkForwardWindow:
    return schemas.WalkForwardWindow(
        window_id="window-1",
        train_start="2026-06-01T00:00:00Z",
        train_end="2026-06-07T00:00:00Z",
        test_start="2026-06-08T00:00:00Z",
        test_end="2026-06-15T00:00:00Z",
        result=backtest_result(),
        classification="WATCHLIST",
    )


def test_candle_schema_validates() -> None:
    assert schemas.validate_candle_schema(candle()) is True


def test_market_data_fixture_validates_local_only_fixture() -> None:
    fixture = schemas.MarketDataFixture(
        fixture_id="fixture-1",
        symbol="EURUSD",
        timeframe="5m",
        source="local_csv_fixture",
        candles=[candle()],
    )

    assert schemas.validate_market_fixture_schema(fixture) is True


def test_strategy_signal_validates_controlled_directions() -> None:
    for direction in ("BUY", "SELL", "HOLD", "NO_TRADE"):
        signal = schemas.StrategySignal(
            signal_id=f"signal-{direction}",
            strategy_id="supertrend_pullback_v1",
            symbol="EURUSD",
            timeframe="5m",
            timestamp="2026-06-15T00:00:00Z",
            direction=direction,
            confidence=0.75,
            reason="deterministic test signal",
        )

        assert schemas.validate_strategy_signal_schema(signal) is True


def test_order_intent_is_intent_only_and_execution_disallowed() -> None:
    intent = schemas.OrderIntent(
        intent_id="intent-1",
        signal_id="signal-BUY",
        symbol="EURUSD",
        direction="BUY",
        requested_units=1000,
        entry_reference_price=1.1000,
        stop_loss_reference_price=1.0950,
        take_profit_reference_price=1.1100,
    )

    assert intent.status == "INTENT_ONLY"
    assert intent.execution_allowed is False
    assert intent.broker_order_id is None
    assert schemas.validate_order_intent_schema(intent) is True


def test_backtest_result_validates_paper_only_mode() -> None:
    result = backtest_result()

    assert result.mode == "PAPER_ONLY"
    assert schemas.validate_backtest_result_schema(result) is True


def test_walk_forward_summary_validates_classification_and_blockers() -> None:
    summary = schemas.WalkForwardSummary(
        summary_id="summary-1",
        strategy_id="supertrend_pullback_v1",
        windows=[walk_forward_window()],
        consistent_windows_pct=50.0,
        classification="WATCHLIST",
        blockers=["walk_forward_consistency_not_met"],
    )

    assert schemas.validate_walk_forward_summary_schema(summary) is True


def test_risk_gate_result_never_allows_live_ready_true() -> None:
    gate = schemas.RiskGateResult(
        gate_id="gate-1",
        classification="PAPER_FORWARD_READY",
        blockers=[],
        next_safe_action="Continue paper-forward evidence only.",
    )

    assert gate.live_ready is False
    assert schemas.validate_risk_gate_schema(gate) is True

    with pytest.raises(ValueError, match="live_ready"):
        schemas.validate_risk_gate_schema({**schemas.asdict(gate), "live_ready": True})


def test_paper_ledger_entry_is_simulated_only_and_not_live_order() -> None:
    entry = schemas.PaperLedgerEntry(
        ledger_id="ledger-1",
        timestamp="2026-06-15T00:00:00Z",
        intent_id="intent-1",
        simulated_fill_price=1.1001,
        simulated_pnl_usd=4.5,
    )

    assert entry.status == "SIMULATED_ONLY"
    assert entry.live_order is False
    assert entry.broker_order_id is None
    assert schemas.validate_paper_ledger_entry_schema(entry) is True


def test_dashboard_state_contains_required_dashboard_fields() -> None:
    state = schemas.DashboardState(
        current_phase="local data schemas",
        selected_strategy="supertrend_pullback_v1",
        data_fixture_status="ready",
        backtest_status="ready",
        walk_forward_status="watchlist",
        risk_gate_status="watchlist",
        paper_permission_state="not_approved",
        live_permission_state="blocked",
        current_blocker="walk_forward_consistency_not_met",
        sos_required=False,
        next_safe_action="Collect more local fixture evidence.",
    )

    assert schemas.validate_dashboard_state_schema(state) is True


def test_daily_edge_report_validates_paper_only() -> None:
    report = schemas.DailyEdgeReport(
        report_id="daily-1",
        timestamp="2026-06-15T00:00:00Z",
        strategy_id="supertrend_pullback_v1",
        symbols=["EURUSD"],
        timeframe="5m",
        data_source="deterministic_sample",
        total_trades=3,
        expectancy_r=1.21,
        max_drawdown_pct=0.17,
        profit_factor=22.25,
        classification="CANDIDATE",
        blockers=["walk_forward_consistency_not_met"],
        next_safe_action="Expand local CSV sample.",
    )

    assert report.mode == "PAPER_ONLY"
    assert schemas.validate_daily_edge_report_schema(report) is True


def test_assert_no_live_permissions_rejects_live_ready_true() -> None:
    with pytest.raises(ValueError, match="live_ready"):
        schemas.assert_no_live_permissions({"live_ready": True})


def test_assert_no_live_permissions_rejects_execution_allowed_true() -> None:
    with pytest.raises(ValueError, match="execution_allowed"):
        schemas.assert_no_live_permissions({"execution_allowed": True})


def test_assert_no_live_permissions_rejects_broker_order_id() -> None:
    with pytest.raises(ValueError, match="broker_order_id"):
        schemas.assert_no_live_permissions({"broker_order_id": "external-123"})


def test_assert_no_live_permissions_rejects_live_order_true() -> None:
    with pytest.raises(ValueError, match="live_order"):
        schemas.assert_no_live_permissions({"live_order": True})


def test_assert_no_live_permissions_rejects_network_allowed_true() -> None:
    with pytest.raises(ValueError, match="network_allowed"):
        schemas.assert_no_live_permissions({"network_allowed": True})


def test_schema_boundary_summary_names_protected_boundaries() -> None:
    summary_text = " ".join(schemas.schema_boundary_summary()["protected_boundaries"]).lower()

    for term in ("broker", "live", "secrets", "orders", "webhooks", "scheduler", "daemon"):
        assert term in summary_text


def test_module_does_not_import_network_broker_secrets_env_behavior() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden_import in ("subprocess", "socket", "urllib", "requests", "http", "os", "dotenv"):
        assert forbidden_import not in import_lines
    for forbidden_call in ("open(", "write_text(", "write_bytes(", "getenv", "environ", "start-process"):
        assert forbidden_call not in source
