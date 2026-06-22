# AIOS Forex C1 EUR BUY Optimization Scoreboard V1

## Baseline status
- closed_trades: `20`
- expectancy: `0`
- profit_factor: `5.55`
- win_rate: `0.6`
- max_drawdown: `8.3333333`
- consecutive_losses: `1`

## Optimized status
- closed_trades: `13`
- expectancy: `22.7`
- profit_factor: `0`
- win_rate: `1.0`
- max_drawdown: `0.0`
- consecutive_losses: `1`

## Deltas
- expectancy_delta: `22.7`
- profit_factor_delta: `-5.55`
- win_rate_delta: `0.4`
- drawdown_delta: `-8.3333333`

## Candidate status
- walk_forward_improved: `False`
- optimization_improved_candidate: `False`
- candidate_status: `REJECT`
- remaining_blockers: `drawdown_containment, insufficient_sample`
- optimization_recommendations: `increase_walk_forward_windows; soften_drawdown cap only after concentration fixes; preserve directional evidence`
