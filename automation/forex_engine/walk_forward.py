"""PAPER_ONLY walk-forward validation scaffold for Sprint 7 research."""

from automation.forex_engine.backtest import run_backtest
from automation.forex_engine.backtest import run_supertrend_edge_backtest
from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.edge_gate_policy import classify_edge_gate
from automation.forex_engine.market_data import validate_candle_sequence
from automation.forex_engine.models import (
    BacktestConfig,
    EngineMode,
    WalkForwardResult,
    WalkForwardSplit,
    WalkForwardStatus,
    WalkForwardWindowResult,
)


MINIMUM_TRAIN_CANDLES = 5
MINIMUM_TEST_CANDLES = 3
DEGRADATION_THRESHOLD_PCT = 50.0


class WalkForwardEngine:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def split_candles(self, candles, train_ratio=0.6):
        if not candles:
            raise ValueError("Walk-forward candles must not be empty.")
        if train_ratio <= 0 or train_ratio >= 1:
            raise ValueError("train_ratio must be greater than 0 and less than 1.")
        validate_candle_sequence(candles)

        split_index = int(len(candles) * train_ratio)
        split_index = max(1, min(split_index, len(candles) - 1))
        train_candles = list(candles[:split_index])
        test_candles = list(candles[split_index:])
        split = WalkForwardSplit(
            mode=EngineMode.PAPER_ONLY,
            symbol=candles[0].symbol,
            timeframe=candles[0].timeframe,
            train_ratio=train_ratio,
            test_ratio=round(1 - train_ratio, 4),
            train_count=len(train_candles),
            test_count=len(test_candles),
            train_start=train_candles[0].timestamp,
            train_end=train_candles[-1].timestamp,
            test_start=test_candles[0].timestamp,
            test_end=test_candles[-1].timestamp,
            metadata={"split_method": "chronological"},
        )
        self.validate_split(train_candles, test_candles)
        return train_candles, test_candles, split

    def validate_split(self, train_candles, test_candles) -> None:
        if not train_candles or not test_candles:
            raise ValueError("Train and test candle windows must not be empty.")
        if train_candles[-1].timestamp >= test_candles[0].timestamp:
            raise ValueError("Train window must end before test window starts.")
        train_timestamps = {candle.timestamp for candle in train_candles}
        test_timestamps = {candle.timestamp for candle in test_candles}
        if train_timestamps & test_timestamps:
            raise ValueError("Train and test candle windows must not overlap.")

    def run_walk_forward(self, candles, strategy_name="sprint_4_intraday_rules_v1", train_ratio=0.6):
        train_candles, test_candles, split = self.split_candles(candles, train_ratio)
        train_backtest = run_backtest(train_candles, self._backtest_config(split, strategy_name, "train"))
        test_backtest = run_backtest(test_candles, self._backtest_config(split, strategy_name, "test"))
        train_result = self._window_result("train", train_backtest, split)
        test_result = self._window_result("test", test_backtest, split)
        status, degradation_pct = self.compare_train_test(train_result, test_result)
        result = WalkForwardResult(
            mode=EngineMode.PAPER_ONLY,
            symbol=split.symbol,
            timeframe=split.timeframe,
            strategy_name=strategy_name,
            split=split,
            train_result=train_result,
            test_result=test_result,
            degradation_pct=degradation_pct,
            status=status,
            summary_note="Local PAPER_ONLY walk-forward scaffold; not evidence of live readiness.",
            metadata={"minimum_train_candles": MINIMUM_TRAIN_CANDLES, "minimum_test_candles": MINIMUM_TEST_CANDLES},
        )
        result.recommendations = self.build_recommendations(result)
        return result

    def compare_train_test(self, train_result, test_result):
        if (
            train_result.candles_processed < MINIMUM_TRAIN_CANDLES
            or test_result.candles_processed < MINIMUM_TEST_CANDLES
            or train_result.trades < 5
            or test_result.trades < 3
        ):
            return WalkForwardStatus.INSUFFICIENT_DATA, None
        if train_result.net_pnl_usd > 0:
            degradation_pct = round(
                ((train_result.net_pnl_usd - test_result.net_pnl_usd) / abs(train_result.net_pnl_usd)) * 100,
                2,
            )
        else:
            degradation_pct = None

        if test_result.net_pnl_usd < 0:
            return WalkForwardStatus.FAILED, degradation_pct
        if degradation_pct is not None and degradation_pct > DEGRADATION_THRESHOLD_PCT:
            return WalkForwardStatus.DEGRADED, degradation_pct
        return WalkForwardStatus.PASSED, degradation_pct

    def build_recommendations(self, result):
        if result.status == WalkForwardStatus.INSUFFICIENT_DATA:
            return ["Use larger historical datasets before trusting walk-forward results."]
        if result.status == WalkForwardStatus.DEGRADED:
            return ["Review regime filters and confidence thresholds."]
        if result.status == WalkForwardStatus.FAILED:
            return ["Reject or rework this strategy candidate before further promotion."]
        return ["Candidate can move to broader paper research, not live trading."]

    def _backtest_config(self, split, strategy_name, window_name):
        return BacktestConfig(
            symbol=split.symbol,
            timeframe=split.timeframe,
            starting_balance_usd=self.config.starting_balance_usd,
            strategy_name=strategy_name,
            metadata={"walk_forward_window": window_name},
        )

    def _window_result(self, window_name, backtest_result, split):
        status = WalkForwardStatus.INSUFFICIENT_DATA
        if window_name == "train" and split.train_count >= MINIMUM_TRAIN_CANDLES:
            status = WalkForwardStatus.PASSED
        if window_name == "test" and split.test_count >= MINIMUM_TEST_CANDLES:
            status = WalkForwardStatus.PASSED
        return WalkForwardWindowResult(
            mode=EngineMode.PAPER_ONLY,
            symbol=backtest_result.symbol,
            timeframe=backtest_result.timeframe,
            window_name=window_name,
            candles_processed=backtest_result.candles_processed,
            trades=backtest_result.trades_closed,
            net_pnl_usd=backtest_result.net_pnl_usd,
            win_rate_pct=backtest_result.win_rate_pct,
            profit_factor=backtest_result.profit_factor,
            max_drawdown_usd=backtest_result.max_drawdown_usd,
            max_drawdown_pct=backtest_result.max_drawdown_pct,
            status=status,
            summary_note=backtest_result.summary_note,
            metadata={"signals_generated": backtest_result.signals_generated},
        )


def sequential_window_splits(candles, train_size, test_size, step_size=None):
    """Build deterministic sequential walk-forward windows over local candles."""
    validate_candle_sequence(candles)
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size and test_size must be positive.")
    step = step_size or test_size
    if step <= 0:
        raise ValueError("step_size must be positive.")
    windows = []
    start = 0
    while start + train_size + test_size <= len(candles):
        train = list(candles[start : start + train_size])
        test = list(candles[start + train_size : start + train_size + test_size])
        windows.append(
            {
                "index": len(windows),
                "train": train,
                "test": test,
                "train_start": train[0].timestamp,
                "train_end": train[-1].timestamp,
                "test_start": test[0].timestamp,
                "test_end": test[-1].timestamp,
            }
        )
        start += step
    return windows


def evaluate_supertrend_walk_forward(
    candles,
    train_size=12,
    test_size=6,
    step_size=6,
    minimum_trades=1,
):
    """Evaluate Supertrend edge candidate across local out-of-sample windows."""
    windows = sequential_window_splits(candles, train_size, test_size, step_size)
    results = []
    consistent = 0
    for window in windows:
        test_result = run_supertrend_edge_backtest(window["test"])
        metrics = test_result["metrics"]
        passed = (
            metrics["total_trades"] >= minimum_trades
            and metrics["expectancy_r"] > 0
            and metrics["max_drawdown_pct"] <= 10.0
            and metrics["longest_losing_streak"] <= 5
        )
        if passed:
            consistent += 1
        results.append(
            {
                "window_index": window["index"],
                "test_start": window["test_start"],
                "test_end": window["test_end"],
                "metrics": metrics,
                "passed": passed,
                "classification": "WATCHLIST" if passed else "FAIL",
            }
        )
    consistent_pct = round((consistent / len(windows)) * 100, 2) if windows else 0.0
    combined_trades = []
    for result in results:
        combined_trades.extend(result["metrics"].get("trades", []))
    summary_metrics = {
        "total_trades": sum(result["metrics"]["total_trades"] for result in results),
        "expectancy_r": round(
            sum(result["metrics"]["expectancy_r"] for result in results) / len(results), 4
        )
        if results
        else 0.0,
        "profit_factor": _combined_profit_factor(results),
        "max_drawdown_pct": max((result["metrics"]["max_drawdown_pct"] for result in results), default=0.0),
        "longest_losing_streak": max((result["metrics"]["longest_losing_streak"] for result in results), default=0),
    }
    gate = classify_edge_gate(
        summary_metrics,
        {"consistent_windows_pct": consistent_pct},
        policy={"minimum_trades": max(minimum_trades, 1)},
        cost_model_used=True,
    )
    return {
        "mode": "PAPER_ONLY",
        "window_count": len(windows),
        "results": results,
        "consistent_windows": consistent,
        "consistent_windows_pct": consistent_pct,
        "summary_metrics": summary_metrics,
        "classification": gate["classification"],
        "blockers": gate["blockers"],
        "next_safe_action": gate["next_safe_action"],
        "live_ready": False,
    }


def _combined_profit_factor(results):
    values = [result["metrics"]["profit_factor"] for result in results if result["metrics"]["profit_factor"]]
    if not values:
        return None
    return round(sum(values) / len(values), 4)
