"""Run the AI_OS Forex Engine v1 Sprint 7 PAPER_ONLY walk-forward demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import WalkForwardStatus
from automation.forex_engine.walk_forward import WalkForwardEngine


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)
    timeframe = "5m"
    train_ratio = 0.6
    engine = WalkForwardEngine(config)
    results = []

    print("AI_OS Forex Engine v1 Sprint 7 Walk-Forward Demo")
    print(f"Mode: {config.mode}")
    print("Data source: local fixture candles only")
    print("Split method: chronological")
    print(f"Train ratio: {train_ratio:.2f}")
    print(f"Test ratio: {1 - train_ratio:.2f}")
    print(f"Symbols tested: {', '.join(config.symbols)}")

    for symbol in config.symbols:
        candles = load_fixture_candles(symbol, timeframe, config)
        result = engine.run_walk_forward(candles, train_ratio=train_ratio)
        results.append(result)
        degradation = "UNKNOWN" if result.degradation_pct is None else f"{result.degradation_pct:.2f}%"
        print(
            f"{symbol}: train_candles={result.split.train_count}, test_candles={result.split.test_count}, "
            f"train_net_pnl={result.train_result.net_pnl_usd:.2f}, test_net_pnl={result.test_result.net_pnl_usd:.2f}, "
            f"degradation={degradation}, status={result.status}, recommendation={result.recommendations[0]}"
        )

    print(f"Passed count: {sum(1 for result in results if result.status == WalkForwardStatus.PASSED)}")
    print(f"Degraded count: {sum(1 for result in results if result.status == WalkForwardStatus.DEGRADED)}")
    print(f"Failed count: {sum(1 for result in results if result.status == WalkForwardStatus.FAILED)}")
    print(
        f"Insufficient data count: "
        f"{sum(1 for result in results if result.status == WalkForwardStatus.INSUFFICIENT_DATA)}"
    )
    print("Safety note: Local walk-forward scaffolding only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
