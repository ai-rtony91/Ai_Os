"""Run the AI_OS Forex Engine v1 Sprint 1 PAPER_ONLY demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.analytics import ForexAnalytics
from automation.forex_engine.confidence import ConfidenceEngine
from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.journal import JournalWriter
from automation.forex_engine.paper_execution import PaperExecutionEngine
from automation.forex_engine.risk import RiskEngine
from automation.forex_engine.signals import create_demo_signals


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)

    confidence_engine = ConfidenceEngine(config)
    risk_engine = RiskEngine(config)
    journal_writer = JournalWriter(config.journal_dir)
    execution_engine = PaperExecutionEngine(config, risk_engine, journal_writer)

    trades_opened = []
    for signal in create_demo_signals():
        assessment = confidence_engine.score_signal(signal)
        try:
            trades_opened.append(execution_engine.submit_signal(signal, assessment))
        except ValueError as exc:
            print(f"PAPER_ONLY signal skipped: {signal.symbol} {signal.direction} - {exc}")

    if trades_opened:
        first = trades_opened[0]
        execution_engine.close_trade(first.trade_id, first.take_profit)
    if len(trades_opened) > 1:
        second = trades_opened[1]
        execution_engine.close_trade(second.trade_id, second.stop_loss)

    summary = ForexAnalytics().summarize(
        config.starting_balance_usd,
        execution_engine.current_balance_usd,
        execution_engine.open_trades,
        execution_engine.closed_trades,
    )

    print("AI_OS Forex Engine v1 Sprint 1 Demo")
    print(f"Mode: {config.mode}")
    print(f"Starting balance: {summary.starting_balance_usd:.2f} USD")
    print(f"Current balance: {summary.current_balance_usd:.2f} USD")
    print(f"Trades opened: {summary.total_trades}")
    print(f"Trades closed: {summary.closed_trades}")
    print(f"Win rate: {summary.win_rate_pct:.2f}%")
    print(f"Profit factor: {summary.profit_factor}")
    print(f"Net PnL: {summary.net_pnl_usd:.2f} USD")
    print(f"Journal path: {journal_writer.journal_path}")
    print("Safety note: No broker execution exists in Sprint 1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
