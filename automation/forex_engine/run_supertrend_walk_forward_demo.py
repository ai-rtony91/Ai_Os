"""Run the PAPER_ONLY Supertrend walk-forward demo."""

from automation.forex_engine.daily_edge_report import deterministic_supertrend_sample
from automation.forex_engine.walk_forward import evaluate_supertrend_walk_forward


def main() -> int:
    candles = deterministic_supertrend_sample(count=60)
    result = evaluate_supertrend_walk_forward(candles, train_size=12, test_size=6, step_size=6)
    print("AI_OS Forex Engine Supertrend Walk-Forward Demo")
    print(f"Mode: {result['mode']}")
    print("Data source: deterministic local sample")
    print(f"Windows: {result['window_count']}")
    print(f"Consistent windows pct: {result['consistent_windows_pct']}")
    print(f"Classification: {result['classification']}")
    print(f"Blockers: {', '.join(result['blockers']) if result['blockers'] else 'none'}")
    print("Safety note: PAPER_ONLY walk-forward research; no broker/API/network/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
