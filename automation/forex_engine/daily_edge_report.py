"""Daily PAPER_ONLY edge report builder for local Supertrend research."""

from datetime import datetime, timezone

from automation.forex_engine.backtest import run_supertrend_edge_backtest
from automation.forex_engine.edge_gate_policy import PAPER_FORWARD_READY, classify_edge_gate
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import Candle
from automation.forex_engine.walk_forward import evaluate_supertrend_walk_forward


REPORT_LOCATION = "Reports/forex_engine/"


def deterministic_supertrend_sample(symbol="EURUSD", timeframe="5m", count=48):
    candles = []
    price = 1.0800
    for index in range(count):
        cycle = index % 12
        if cycle < 8:
            open_price = price
            close_price = price + 0.0007
        else:
            open_price = price
            close_price = price - 0.00025
        high = max(open_price, close_price) + 0.00035
        low = min(open_price, close_price) - 0.00035
        candles.append(
            Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=f"2026-06-06T{9 + (index // 12):02d}:{(index % 12) * 5:02d}:00Z",
                open=round(open_price, 5),
                high=round(high, 5),
                low=round(low, 5),
                close=round(close_price, 5),
                volume=1000 + index,
                source="deterministic_local_sample",
            )
        )
        price = close_price
    return candles


def build_daily_edge_report(candles=None, symbol="EURUSD", timeframe="5m"):
    source_type = "deterministic_sample"
    active_candles = candles
    if active_candles is None:
        try:
            active_candles = load_fixture_candles(symbol, timeframe, _default_config())
            source_type = "local_fixture_csv"
        except Exception:
            active_candles = deterministic_supertrend_sample(symbol, timeframe)
    if len(active_candles) < 20:
        active_candles = deterministic_supertrend_sample(symbol, timeframe)
        source_type = "deterministic_sample"

    backtest = run_supertrend_edge_backtest(active_candles)
    walk_forward = evaluate_supertrend_walk_forward(active_candles, train_size=12, test_size=6, step_size=6)
    gate = classify_edge_gate(
        backtest["metrics"],
        {"consistent_windows_pct": walk_forward["consistent_windows_pct"]},
        policy={"minimum_trades": 3},
        cost_model_used=True,
    )
    classification = _daily_classification(gate["classification"], backtest["metrics"])
    blockers = list(gate["blockers"])
    if classification == "NEEDS_MORE_DATA" and "more_data_required" not in blockers:
        blockers.append("more_data_required")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "PAPER_ONLY",
        "strategy_name": backtest["strategy_name"],
        "symbols": [active_candles[0].symbol],
        "timeframes": [active_candles[0].timeframe],
        "data_source_type": source_type,
        "report_location": REPORT_LOCATION,
        "cost_assumptions": backtest["cost_assumptions"],
        "total_trades": backtest["metrics"]["total_trades"],
        "expectancy_r": backtest["metrics"]["expectancy_r"],
        "max_drawdown_pct": backtest["metrics"]["max_drawdown_pct"],
        "profit_factor": backtest["metrics"]["profit_factor"],
        "no_trade_reasons": backtest["metrics"]["no_trade_reason_counts"],
        "classification": classification,
        "blockers": blockers,
        "next_safe_action": _next_action(classification),
        "walk_forward": {
            "window_count": walk_forward["window_count"],
            "consistent_windows_pct": walk_forward["consistent_windows_pct"],
            "classification": walk_forward["classification"],
        },
        "live_ready": False,
        "safety_note": "PAPER_ONLY edge research; no broker/API/network/live execution.",
    }


def format_daily_edge_report(report):
    lines = [
        "AI_OS Forex Engine Daily Edge Report",
        f"Timestamp: {report['timestamp']}",
        f"Mode: {report['mode']}",
        f"Strategy: {report['strategy_name']}",
        f"Symbols/timeframes: {', '.join(report['symbols'])} / {', '.join(report['timeframes'])}",
        f"Data source: {report['data_source_type']}",
        f"Cost assumptions: {report['cost_assumptions']}",
        f"Total trades: {report['total_trades']}",
        f"Expectancy R: {report['expectancy_r']}",
        f"Max drawdown pct: {report['max_drawdown_pct']}",
        f"Profit factor: {report['profit_factor']}",
        f"No-trade reasons: {report['no_trade_reasons']}",
        f"Classification: {report['classification']}",
        f"Blockers: {', '.join(report['blockers']) if report['blockers'] else 'none'}",
        f"Next safe action: {report['next_safe_action']}",
        "Safety: no broker/API/network/live execution; no generated report file written by default.",
    ]
    return "\n".join(lines)


def _daily_classification(gate_classification, metrics):
    if metrics["total_trades"] < 3:
        return "NEEDS_MORE_DATA"
    if gate_classification == PAPER_FORWARD_READY:
        return "PAPER_FORWARD_READY"
    if metrics["expectancy_r"] > 0:
        return "CANDIDATE"
    return "REJECTED"


def _next_action(classification):
    if classification == "PAPER_FORWARD_READY":
        return "Continue paper-forward observation only; no live approval."
    if classification == "CANDIDATE":
        return "Expand local CSV sample and rerun walk-forward evidence."
    if classification == "NEEDS_MORE_DATA":
        return "Add more local exported candle CSV data before promotion discussion."
    return "Reject or revise the edge candidate before more paper research."


def _default_config():
    from automation.forex_engine.config import ForexEngineConfig

    return ForexEngineConfig()
