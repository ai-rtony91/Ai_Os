"""Backtest replay for the AIOS paper trader."""

from __future__ import annotations

from aios.modules.trader.events import MarketBar
from aios.modules.trader.scorecard import build_paper_scorecard
from aios.modules.trader.trader import TraderEngine


class BacktestEngine:
    def __init__(self, trader: TraderEngine) -> None:
        self.trader = trader

    def run(self, bars: list[MarketBar]) -> dict[str, object]:
        decisions = [self.trader.on_bar(bar).to_dict() for bar in bars]
        total_signals = sum(1 for decision in decisions if decision.get("signal") is not None)
        total_paper_orders = sum(1 for decision in decisions if decision.get("paper_order") is not None)
        total_paper_fills = sum(1 for decision in decisions if decision.get("paper_fill") is not None)
        blocked_decisions = sum(1 for decision in decisions if decision.get("decision") == "BLOCKED")
        risk_block_count = sum(
            1 for decision in decisions
            if decision.get("decision") == "BLOCKED" and decision.get("risk") is not None
        )
        execution_records = [
            decision["paper_fill"]
            for decision in decisions
            if decision.get("paper_fill") is not None
        ]
        paper_outcomes = self.trader.paper_outcomes.to_dicts()
        scorecard = build_paper_scorecard(
            paper_outcomes,
            starting_cash=self.trader.config.starting_cash,
            blocked_decisions=blocked_decisions,
            execution_records=execution_records,
            rejected_order_count=self.trader.paper_broker.rejected_order_count,
            risk_block_count=risk_block_count,
            live_execution_status=self.trader.config.live_execution_status,
            execution_allowed=self.trader.config.execution_allowed,
        )
        return {
            "total_bars": len(bars),
            "total_signals": total_signals,
            "total_paper_orders": total_paper_orders,
            "total_paper_fills": total_paper_fills,
            "blocked_decisions": blocked_decisions,
            "execution_records": execution_records,
            "rejected_order_count": self.trader.paper_broker.rejected_order_count,
            "risk_block_count": risk_block_count,
            "paper_outcomes": paper_outcomes,
            "scorecard": scorecard,
            "final_cash": self.trader.paper_broker.cash,
            "positions": dict(self.trader.paper_broker.positions),
            "live_execution_status": self.trader.config.live_execution_status,
        }
