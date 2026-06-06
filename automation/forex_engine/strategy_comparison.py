"""PAPER_ONLY strategy comparison scaffold for Sprint 6 research."""

from dataclasses import replace

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    EngineMode,
    OptimizationCandidate,
    StrategyComparisonResult,
    StrategyScoreComponent,
    StrategyScorecard,
    StrategyStatus,
    utc_now_iso,
)


STATUS_PRIORITY = {
    StrategyStatus.RESEARCH_CANDIDATE: 0,
    StrategyStatus.WATCHLIST: 1,
    StrategyStatus.INSUFFICIENT_DATA: 2,
    StrategyStatus.REJECTED: 3,
}


class StrategyComparisonEngine:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def score_backtest_result(self, backtest_result) -> StrategyScorecard:
        components = [StrategyScoreComponent("base", 50, "Base PAPER_ONLY strategy comparison score.")]
        trades = backtest_result.trades_closed
        wins = sum(1 for item in backtest_result.results if item.outcome == "WIN")
        losses = sum(1 for item in backtest_result.results if item.outcome == "LOSS")

        self._score_sample_size(trades, components)
        self._score_net_pnl(backtest_result.net_pnl_usd, components)
        self._score_win_rate(backtest_result.win_rate_pct, components)
        self._score_profit_factor(backtest_result.profit_factor, components)
        self._score_drawdown(backtest_result.max_drawdown_pct, components)
        self._score_balance_growth(backtest_result, components)
        self._score_consistency(wins, losses, backtest_result.net_pnl_usd, components)

        score = round(max(0, min(100, sum(component.score_delta for component in components))), 2)
        status = self._status_for(score, trades)
        scorecard = StrategyScorecard(
            mode=EngineMode.PAPER_ONLY,
            strategy_name=backtest_result.strategy_name,
            symbol=backtest_result.symbol,
            timeframe=backtest_result.timeframe,
            score=score,
            status=status,
            rank=0,
            trades=trades,
            wins=wins,
            losses=losses,
            win_rate_pct=backtest_result.win_rate_pct,
            profit_factor=backtest_result.profit_factor,
            net_pnl_usd=backtest_result.net_pnl_usd,
            max_drawdown_usd=backtest_result.max_drawdown_usd,
            max_drawdown_pct=backtest_result.max_drawdown_pct,
            starting_balance_usd=backtest_result.starting_balance_usd,
            ending_balance_usd=backtest_result.ending_balance_usd,
            components=components,
            summary_note="PAPER_ONLY strategy comparison scaffold. Tiny samples are not edge evidence.",
            metadata={"signals_generated": backtest_result.signals_generated},
        )
        scorecard.optimization_candidates = self.build_optimization_candidates(scorecard)
        return scorecard

    def compare_results(self, backtest_results) -> StrategyComparisonResult:
        scorecards = [self.score_backtest_result(result) for result in backtest_results]
        ranked = self.rank_scorecards(scorecards)
        top_strategy = ranked[0].strategy_name if ranked else None
        return StrategyComparisonResult(
            mode=EngineMode.PAPER_ONLY,
            compared_at=utc_now_iso(),
            strategy_count=len(ranked),
            scorecards=ranked,
            top_strategy=top_strategy,
            rejected_count=sum(1 for item in ranked if item.status == StrategyStatus.REJECTED),
            watchlist_count=sum(1 for item in ranked if item.status == StrategyStatus.WATCHLIST),
            research_candidate_count=sum(1 for item in ranked if item.status == StrategyStatus.RESEARCH_CANDIDATE),
            insufficient_data_count=sum(1 for item in ranked if item.status == StrategyStatus.INSUFFICIENT_DATA),
            summary_note="Local PAPER_ONLY strategy comparison only; rankings are not live readiness.",
            metadata={"data_source": "local fixture backtests only"},
        )

    def rank_scorecards(self, scorecards):
        ordered = sorted(
            scorecards,
            key=lambda item: (
                STATUS_PRIORITY[item.status],
                -item.score,
                -item.net_pnl_usd,
                -item.win_rate_pct,
                item.strategy_name,
                item.symbol,
            ),
        )
        return [replace(scorecard, rank=index + 1) for index, scorecard in enumerate(ordered)]

    def build_optimization_candidates(self, scorecard):
        candidates = []
        if scorecard.trades < 5:
            candidates.append(
                OptimizationCandidate(
                    "sample_size",
                    "Backtest sample is too small for strategy confidence.",
                    "HIGH",
                    "Test on more historical candles.",
                )
            )
        if scorecard.win_rate_pct < 50:
            candidates.append(
                OptimizationCandidate(
                    "entry_filter",
                    "Win rate is below 50 percent.",
                    "MEDIUM",
                    "Tighten regime and confidence filters.",
                )
            )
        if scorecard.profit_factor is not None and scorecard.profit_factor < 1:
            candidates.append(
                OptimizationCandidate(
                    "reward_risk_threshold",
                    "Profit factor below 1 indicates losses exceed gains.",
                    "HIGH",
                    "Increase reward/risk requirement or reduce weak setups.",
                )
            )
        if scorecard.max_drawdown_pct >= 2:
            candidates.append(
                OptimizationCandidate(
                    "drawdown_control",
                    "Drawdown is too high for small-account profile.",
                    "HIGH",
                    "Reduce risk or pause earlier after losses.",
                )
            )
        if scorecard.profit_factor is None:
            candidates.append(
                OptimizationCandidate(
                    "loss_sample",
                    "No-loss sample is inconclusive without larger history.",
                    "MEDIUM",
                    "Run on broader historical data before trusting ranking.",
                )
            )
        if scorecard.score >= 70 and scorecard.trades < 20:
            candidates.append(
                OptimizationCandidate(
                    "walk_forward_candidate",
                    "Promising research result requires out-of-sample validation.",
                    "MEDIUM",
                    "Reserve for Sprint 7 walk-forward testing.",
                )
            )
        return candidates

    def _score_sample_size(self, trades, components):
        if trades < 5:
            components.append(StrategyScoreComponent("sample_size", -25, "Trade sample is below 5."))
        elif trades >= 100:
            components.append(StrategyScoreComponent("sample_size", 15, "Trade sample is at least 100."))
        elif trades >= 20:
            components.append(StrategyScoreComponent("sample_size", 8, "Trade sample is at least 20."))

    def _score_net_pnl(self, net_pnl, components):
        if net_pnl > 0:
            components.append(StrategyScoreComponent("net_pnl", 10, "Net PnL is positive."))
        elif net_pnl < 0:
            components.append(StrategyScoreComponent("net_pnl", -15, "Net PnL is negative."))
        else:
            components.append(StrategyScoreComponent("net_pnl", 0, "Net PnL is flat."))

    def _score_win_rate(self, win_rate, components):
        if win_rate >= 60:
            components.append(StrategyScoreComponent("win_rate", 10, "Win rate is at least 60 percent."))
        elif win_rate >= 50:
            components.append(StrategyScoreComponent("win_rate", 4, "Win rate is at least 50 percent."))
        else:
            components.append(StrategyScoreComponent("win_rate", -10, "Win rate is below 50 percent."))

    def _score_profit_factor(self, profit_factor, components):
        if profit_factor is None:
            components.append(StrategyScoreComponent("profit_factor", -4, "Profit factor is inconclusive."))
        elif profit_factor > 1.5:
            components.append(StrategyScoreComponent("profit_factor", 12, "Profit factor is above 1.5."))
        elif profit_factor >= 1.0:
            components.append(StrategyScoreComponent("profit_factor", 5, "Profit factor is at least 1.0."))
        else:
            components.append(StrategyScoreComponent("profit_factor", -12, "Profit factor is below 1.0."))

    def _score_drawdown(self, drawdown_pct, components):
        if drawdown_pct == 0:
            components.append(StrategyScoreComponent("drawdown", 0, "Zero drawdown on tiny samples is inconclusive."))
        elif drawdown_pct < 1:
            components.append(StrategyScoreComponent("drawdown", 6, "Drawdown is below 1 percent."))
        elif drawdown_pct < 2:
            components.append(StrategyScoreComponent("drawdown", 2, "Drawdown is below 2 percent."))
        else:
            components.append(StrategyScoreComponent("drawdown", -12, "Drawdown is high for small-account profile."))

    def _score_balance_growth(self, backtest_result, components):
        if backtest_result.ending_balance_usd > backtest_result.starting_balance_usd:
            components.append(StrategyScoreComponent("balance_growth", 4, "Ending balance is above starting balance."))
        elif backtest_result.ending_balance_usd < backtest_result.starting_balance_usd:
            components.append(StrategyScoreComponent("balance_growth", -8, "Ending balance is below starting balance."))

    def _score_consistency(self, wins, losses, net_pnl, components):
        if wins > 0 and losses > 0 and net_pnl > 0:
            components.append(StrategyScoreComponent("consistency", 3, "Mixed wins/losses with positive net PnL."))
        elif wins > 0 and losses == 0:
            components.append(StrategyScoreComponent("consistency", -3, "No-loss sample is too small to trust."))
        elif losses > wins:
            components.append(StrategyScoreComponent("consistency", -8, "Losses exceed wins."))

    def _status_for(self, score, trades):
        if trades < 5:
            return StrategyStatus.INSUFFICIENT_DATA
        if score >= 70:
            return StrategyStatus.RESEARCH_CANDIDATE
        if score >= 50:
            return StrategyStatus.WATCHLIST
        return StrategyStatus.REJECTED
