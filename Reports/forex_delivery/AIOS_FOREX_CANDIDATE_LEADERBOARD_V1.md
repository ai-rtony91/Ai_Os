# AIOS Forex Candidate Leaderboard V1

| rank | candidate_id | strategy_id | direction | expectancy | profit_factor | win_rate | max_drawdown | trades | consecutive_losses | blockers |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | c1-eur-buy | paper_long_run_supervisor_v2 | LONG | 200.0000 | 999.0000 | 1.0000 | 0.0000 | 20 | 0 | none |
| 2 | c5-gbp-buy | paper_continuation_supervisor_v2 | LONG | 70.0000 | 2.5600 | 0.8667 | 1.5385 | 15 | 1 | none |
| 3 | c2-usd-buy | paper_momentum_supervisor_v3 | LONG | 18.2105 | 3.2600 | 0.7000 | 0.0000 | 20 | 0 | none |
| 4 | c3-eur-sell | paper_mean_reversion_v2 | SHORT | 10.0000 | 5.6667 | 0.8125 | 0.0000 | 16 | 0 | none |
| 5 | c4-jpy-buy | paper_breakout_supervisor_v2 | LONG | -10.1250 | 2.1667 | 0.4375 | 0.0000 | 16 | 1 | negative_expectancy |

## Deterministic ranking rationale
- higher expectancy first
- then higher profit_factor
- then higher win_rate
- then lower drawdown
- then candidate_id as deterministic tie-breaker
