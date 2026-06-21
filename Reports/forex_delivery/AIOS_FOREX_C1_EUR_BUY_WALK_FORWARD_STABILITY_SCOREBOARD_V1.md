# AIOS Forex C1 EUR BUY Walk Forward Stability Scoreboard V1

## Paper-only scope
- paper-only execution
- no broker connectivity
- no credentials
- no account IDs
- no network
- no order execution
- no demo trading
- no live trading

## Anchor candidate
- candidate: `c1-eur-buy`
- strategy: `paper_long_run_supervisor_v2`
- direction: `LONG`

## Anchor stability
- closed trade count (per window): `5`
- sample-size gate (threshold 5): `pass`
- windows analyzed: `4`
- sample gate result: `cleared`
- failing windows: `3`
- stable expectancy: `-325.45`
- stable profit factor: `250.14`
- controlled drawdown: `75.20`
- consecutive wins: varies per window
- consecutive losses: varies per window
- promotion status: per-window via matrix, mixed pass/fail
- blocker reasons: `negative_expectancy_window`, `low_profit_factor_window`, `excessive_drawdown_window`

## Result
- walk-forward evidence blocker cleared: `False`
- remaining blockers: `negative_expectancy_window, low_profit_factor_window, excessive_drawdown_window`
