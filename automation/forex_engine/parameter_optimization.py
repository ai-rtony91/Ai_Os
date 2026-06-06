"""Local PAPER_ONLY parameter optimization scaffold for Sprint 11 research."""

from dataclasses import replace

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    EngineMode,
    OptimizationStatus,
    OverfittingRisk,
    ParameterOptimizationResult,
    ParameterOptimizationScore,
    ParameterSet,
    StrategyScoreComponent,
    WalkForwardStatus,
)


OPTIMIZATION_MODE = "OPTIMIZATION_MODEL_ONLY"

STATUS_PRIORITY = {
    OptimizationStatus.BEST_CANDIDATE: 0,
    OptimizationStatus.OVERFIT_RISK: 1,
    OptimizationStatus.WATCHLIST: 2,
    OptimizationStatus.INSUFFICIENT_DATA: 3,
    OptimizationStatus.REJECTED: 4,
}

RISK_PRIORITY = {
    OverfittingRisk.LOW: 0,
    OverfittingRisk.MEDIUM: 1,
    OverfittingRisk.UNKNOWN: 2,
    OverfittingRisk.HIGH: 3,
}


class ParameterOptimizationEngine:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def default_parameter_sets(self):
        return [
            ParameterSet(
                name="conservative",
                strategy_name="sprint_4_intraday_rules_v1",
                confidence_threshold=85,
                reward_risk_min=2.0,
                volatility_filter=True,
                regime_filter=True,
                max_open_trades=1,
                risk_per_trade_pct=0.25,
                metadata={"profile": "capital_preservation"},
            ),
            ParameterSet(
                name="balanced",
                strategy_name="sprint_4_intraday_rules_v1",
                confidence_threshold=75,
                reward_risk_min=1.5,
                volatility_filter=True,
                regime_filter=True,
                max_open_trades=2,
                risk_per_trade_pct=0.5,
                metadata={"profile": "paper_research_default"},
            ),
            ParameterSet(
                name="aggressive",
                strategy_name="sprint_4_intraday_rules_v1",
                confidence_threshold=65,
                reward_risk_min=1.0,
                volatility_filter=False,
                regime_filter=False,
                max_open_trades=3,
                risk_per_trade_pct=1.0,
                metadata={"profile": "aggressive_research_only"},
            ),
        ]

    def score_parameter_set(self, parameter_set, strategy_scorecard_or_backtest_result) -> ParameterOptimizationScore:
        metrics = self._extract_metrics(strategy_scorecard_or_backtest_result)
        components = [StrategyScoreComponent("base", 50, "Base OPTIMIZATION_MODEL_ONLY score.")]
        self._score_sample_size(metrics["sample_size"], components)
        self._score_net_pnl(metrics["net_pnl_usd"], components)
        self._score_win_rate(metrics["win_rate_pct"], components)
        self._score_profit_factor(metrics["profit_factor"], components)
        self._score_drawdown(metrics["max_drawdown_pct"], metrics["sample_size"], components)
        self._score_parameters(parameter_set, components)

        raw_score = sum(component.score_delta for component in components)
        score = round(max(0, min(100, raw_score)), 2)
        risk = self.detect_overfitting_risk(
            score=score,
            sample_size=metrics["sample_size"],
            profit_factor=metrics["profit_factor"],
            walk_forward_status=metrics.get("walk_forward_status"),
        )
        status = self._status_for(score, metrics["sample_size"], risk)
        result = ParameterOptimizationScore(
            mode=EngineMode.PAPER_ONLY,
            parameter_set_name=parameter_set.name,
            score=score,
            status=status,
            overfitting_risk=risk,
            sample_size=metrics["sample_size"],
            net_pnl_usd=metrics["net_pnl_usd"],
            win_rate_pct=metrics["win_rate_pct"],
            profit_factor=metrics["profit_factor"],
            max_drawdown_pct=metrics["max_drawdown_pct"],
            components=components,
            metadata={
                "optimization_mode": OPTIMIZATION_MODE,
                "strategy_name": parameter_set.strategy_name,
                "confidence_threshold": parameter_set.confidence_threshold,
                "reward_risk_min": parameter_set.reward_risk_min,
                "volatility_filter": parameter_set.volatility_filter,
                "regime_filter": parameter_set.regime_filter,
                "risk_per_trade_pct": parameter_set.risk_per_trade_pct,
            },
        )
        result.recommendations = self.build_recommendations(result)
        return result

    def compare_parameter_sets(self, parameter_sets, research_results) -> ParameterOptimizationResult:
        if not parameter_sets:
            raise ValueError("parameter_sets must not be empty.")
        if not research_results:
            raise ValueError("research_results must not be empty.")
        scores = [
            self.score_parameter_set(parameter_set, research_results[index % len(research_results)])
            for index, parameter_set in enumerate(parameter_sets)
        ]
        ranked = self.rank_scores(scores)
        best = ranked[0] if ranked else None
        overall_risk = max((score.overfitting_risk for score in ranked), key=lambda item: RISK_PRIORITY[item])
        status = OptimizationStatus.INSUFFICIENT_DATA
        if best and best.status == OptimizationStatus.BEST_CANDIDATE:
            status = OptimizationStatus.BEST_CANDIDATE
        elif best and any(score.status == OptimizationStatus.OVERFIT_RISK for score in ranked):
            status = OptimizationStatus.OVERFIT_RISK
        elif best and any(score.status == OptimizationStatus.WATCHLIST for score in ranked):
            status = OptimizationStatus.WATCHLIST
        return ParameterOptimizationResult(
            mode=EngineMode.PAPER_ONLY,
            tested_count=len(ranked),
            scores=ranked,
            best_parameter_set=best.parameter_set_name if best else None,
            overfitting_risk=overall_risk if ranked else OverfittingRisk.UNKNOWN,
            status=status,
            summary_note="Local OPTIMIZATION_MODEL_ONLY scaffold. Tiny fixture results are not optimization proof.",
            metadata={"optimization_mode": OPTIMIZATION_MODE, "data_source": "local fixture/research summaries only"},
        )

    def detect_overfitting_risk(
        self,
        score,
        sample_size,
        profit_factor=None,
        walk_forward_status=None,
    ):
        if sample_size < 20:
            return OverfittingRisk.HIGH
        if profit_factor is None and sample_size < 50:
            return OverfittingRisk.HIGH
        if score > 80 and sample_size < 50:
            return OverfittingRisk.HIGH
        if walk_forward_status == WalkForwardStatus.PASSED and sample_size >= 20:
            return OverfittingRisk.LOW
        if sample_size >= 20:
            return OverfittingRisk.MEDIUM
        return OverfittingRisk.UNKNOWN

    def build_recommendations(self, score):
        recommendations = []
        if score.sample_size < 20:
            recommendations.append("Use larger historical datasets before trusting optimization results.")
        if score.overfitting_risk == OverfittingRisk.HIGH:
            recommendations.append("Treat this parameter result as overfit-risk until walk-forward evidence improves.")
        if score.profit_factor is None:
            recommendations.append("Profit factor is inconclusive; collect a larger loss sample.")
        if score.max_drawdown_pct >= 2:
            recommendations.append("Reduce risk or tighten drawdown controls.")
        if score.status == OptimizationStatus.BEST_CANDIDATE:
            recommendations.append("Candidate may continue broader PAPER_ONLY research, not live trading.")
        return recommendations or ["Continue local PAPER_ONLY parameter research only."]

    def rank_scores(self, scores):
        ordered = sorted(
            scores,
            key=lambda item: (
                STATUS_PRIORITY[item.status],
                -item.score,
                RISK_PRIORITY[item.overfitting_risk],
                -item.net_pnl_usd,
                -item.win_rate_pct,
                item.parameter_set_name,
            ),
        )
        return [replace(score, metadata={**score.metadata, "rank": index + 1}) for index, score in enumerate(ordered)]

    def format_optimization_result(self, result):
        lines = [
            "AI_OS Forex Engine v1 Sprint 11 Parameter Optimization Report",
            f"Mode: {result.mode}",
            f"Optimization mode: {result.metadata.get('optimization_mode', OPTIMIZATION_MODE)}",
            f"Parameter sets tested: {result.tested_count}",
            f"Best parameter set: {result.best_parameter_set}",
            f"Optimization status: {result.status}",
            f"Overfitting risk: {result.overfitting_risk}",
        ]
        for score in result.scores:
            lines.append(
                f"{score.parameter_set_name}: score={score.score:.2f}, status={score.status}, "
                f"risk={score.overfitting_risk}, sample={score.sample_size}"
            )
        return "\n".join(lines)

    def _extract_metrics(self, result):
        return {
            "sample_size": getattr(result, "trades", getattr(result, "trades_closed", 0)),
            "net_pnl_usd": getattr(result, "net_pnl_usd", 0.0),
            "win_rate_pct": getattr(result, "win_rate_pct", 0.0),
            "profit_factor": getattr(result, "profit_factor", None),
            "max_drawdown_pct": getattr(result, "max_drawdown_pct", 0.0),
            "walk_forward_status": getattr(result, "walk_forward_status", None),
        }

    def _score_sample_size(self, sample_size, components):
        if sample_size < 20:
            components.append(StrategyScoreComponent("sample_size", -30, "Sample size is below 20."))
        elif sample_size >= 100:
            components.append(StrategyScoreComponent("sample_size", 15, "Sample size is at least 100."))
        else:
            components.append(StrategyScoreComponent("sample_size", 6, "Sample size is at least 20."))

    def _score_net_pnl(self, net_pnl, components):
        if net_pnl > 0:
            components.append(StrategyScoreComponent("net_pnl", 10, "Net PnL is positive."))
        elif net_pnl < 0:
            components.append(StrategyScoreComponent("net_pnl", -15, "Net PnL is negative."))

    def _score_win_rate(self, win_rate, components):
        if win_rate >= 60:
            components.append(StrategyScoreComponent("win_rate", 10, "Win rate is at least 60 percent."))
        elif win_rate >= 50:
            components.append(StrategyScoreComponent("win_rate", 4, "Win rate is at least 50 percent."))
        else:
            components.append(StrategyScoreComponent("win_rate", -10, "Win rate is below 50 percent."))

    def _score_profit_factor(self, profit_factor, components):
        if profit_factor is None:
            components.append(StrategyScoreComponent("profit_factor", -5, "Profit factor is inconclusive."))
        elif profit_factor > 1.5:
            components.append(StrategyScoreComponent("profit_factor", 12, "Profit factor is above 1.5."))
        elif profit_factor >= 1.0:
            components.append(StrategyScoreComponent("profit_factor", 5, "Profit factor is at least 1.0."))
        else:
            components.append(StrategyScoreComponent("profit_factor", -12, "Profit factor is below 1.0."))

    def _score_drawdown(self, drawdown_pct, sample_size, components):
        if drawdown_pct >= 2:
            components.append(StrategyScoreComponent("drawdown", -12, "Drawdown is high for the starter profile."))
        elif drawdown_pct < 1 and sample_size >= 20:
            components.append(StrategyScoreComponent("drawdown", 4, "Drawdown is low with adequate sample size."))

    def _score_parameters(self, parameter_set, components):
        if parameter_set.risk_per_trade_pct > self.config.paper_risk_per_trade_pct:
            components.append(StrategyScoreComponent("risk_per_trade", -12, "Risk per trade exceeds 500 USD starter profile."))
        if parameter_set.reward_risk_min < 1.5:
            components.append(StrategyScoreComponent("reward_risk", -8, "Reward/risk threshold is below 1.5."))
        if not parameter_set.regime_filter:
            components.append(StrategyScoreComponent("regime_filter", -8, "Regime filter is missing."))
        if not parameter_set.volatility_filter:
            components.append(StrategyScoreComponent("volatility_filter", -6, "Volatility filter is missing."))
        if parameter_set.risk_per_trade_pct <= self.config.paper_risk_per_trade_pct:
            components.append(StrategyScoreComponent("starter_risk_fit", 4, "Risk per trade fits starter profile."))

    def _status_for(self, score, sample_size, overfitting_risk):
        if sample_size < 20:
            return OptimizationStatus.INSUFFICIENT_DATA
        if overfitting_risk == OverfittingRisk.HIGH:
            return OptimizationStatus.OVERFIT_RISK
        if score >= 70:
            return OptimizationStatus.BEST_CANDIDATE
        if score >= 50:
            return OptimizationStatus.WATCHLIST
        return OptimizationStatus.REJECTED
