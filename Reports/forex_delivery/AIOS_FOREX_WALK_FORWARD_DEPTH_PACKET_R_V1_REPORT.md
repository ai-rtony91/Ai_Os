# AIOS Forex Walk Forward Depth Packet R V1

## Scope
- paper-only evidence expansion
- no broker connectivity
- no credentials
- no account IDs
- no network access
- no order execution
- no demo trading
- no live trading

## Anchor candidate
- candidate: `c1-eur-buy`
- strategy: `paper_long_run_supervisor_v2`
- direction: `LONG`

## Aggregate summary
- total_windows: `4`
- passing_windows: `1`
- failing_windows: `3`
- stable_expectancy: `-325.45`
- stable_profit_factor: `250.14`
- controlled_drawdown: `75.20`
- walk_forward_gate_cleared: `False`
- remaining_blockers: `negative_expectancy_window, low_profit_factor_window, excessive_drawdown_window`

## Per-window matrix
| window_id | trades | expectancy | profit factor | max drawdown | promotion status | blocker reasons |
|---|---:|---:|---:|---:|---|---|
| wf-01 | 5 | 200.00 | 999.00 | 0.00 | PROFIT_OBJECTIVE_READY | none |
| wf-02 | 5 | -0.80 | 0.93 | 4.00 | REJECT_LOW_PROFIT_FACTOR | negative_expectancy, low_profit_factor |
| wf-03 | 5 | -2.00 | 0.61 | 0.15 | REJECT_LOW_PROFIT_FACTOR | negative_expectancy, low_profit_factor |
| wf-04 | 5 | -1499.00 | 0.01 | 75.20 | REJECT_EXCESSIVE_DRAWDOWN | negative_expectancy, excessive_drawdown |

## Determinism
The window list and score ordering are static and deterministic for every run.
