# AIOS Forex Walk Forward Window Matrix V1

## Paper-only scope
- paper-only only
- no broker connectivity
- no credentials
- no account IDs
- no network access
- no order execution
- no demo trading
- no live trading

## Window matrix
| window_id | candidate | strategy | direction | closed trades | expectancy | profit factor | max drawdown | promotion status | blocker reasons |
|---|---|---|---|---:|---:|---:|---|---|
| wf-01 | c1-eur-buy | paper_long_run_supervisor_v2 | LONG | 5 | 200.00 | 999.00 | 0.00 | PROFIT_OBJECTIVE_READY | none |
| wf-02 | c1-eur-buy | paper_long_run_supervisor_v2 | LONG | 5 | -0.80 | 0.93 | 4.00 | REJECT_LOW_PROFIT_FACTOR | negative_expectancy, low_profit_factor |
| wf-03 | c1-eur-buy | paper_long_run_supervisor_v2 | LONG | 5 | -2.00 | 0.61 | 0.15 | REJECT_LOW_PROFIT_FACTOR | negative_expectancy, low_profit_factor |
| wf-04 | c1-eur-buy | paper_long_run_supervisor_v2 | LONG | 5 | -1499.00 | 0.01 | 75.20 | REJECT_EXCESSIVE_DRAWDOWN | negative_expectancy, excessive_drawdown |

## Aggregate
- total windows: `4`
- walk-forward gate cleared: `False`
- blockers remain: `negative_expectancy_window`, `low_profit_factor_window`, `excessive_drawdown_window`
