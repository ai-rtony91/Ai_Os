# AIOS Forex Before/After Walk Forward Comparison V1

## Baseline -> Optimized matrix

| window | phase | trades | expectancy | profit_factor | win_rate | max_drawdown | blockers |
|---|---|---:|---:|---:|---:|---:|---|
| wf-01 | before | 5 | 200.0000 | 999.0000 | 1.0000 | 0.0000 | none |
| wf-02 | before | 5 | -0.8000 | 0.5000 | 0.4000 | 10.0000 | negative_expectancy, low_profit_factor |
| wf-03 | before | 5 | -0.0000 | 0.6667 | 0.4000 | 0.0000 | negative_expectancy, low_profit_factor |
| wf-04 | before | 5 | -120.2000 | 0.0140 | 0.4000 | 14.0000 | negative_expectancy, low_profit_factor, excessive_drawdown |
| wf-01 | after | 5 | 200.0000 | 999.0000 | 1.0000 | 0.0000 | none |
| wf-02 | after | 4 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | insufficient_sample |
| wf-03 | after | 3 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | insufficient_sample |
| wf-04 | after | 3 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | insufficient_sample |

## Summary
- baseline_total_closed_trades: `20`
- optimized_total_closed_trades: `15`
- walk_forward_improved: `False`
- remaining_blockers: `drawdown_containment, insufficient_sample`
