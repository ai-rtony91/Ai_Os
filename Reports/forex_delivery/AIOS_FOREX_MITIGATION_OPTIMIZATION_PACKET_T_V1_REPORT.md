# AIOS Forex Mitigation Optimization Packet T V1

## Paper-only scope
- paper_only: True
- no broker connectivity
- no credentials
- no account IDs
- no network
- no order execution
- no demo trading
- no live trading

## Candidate
- candidate_id: `c1-eur-buy`
- strategy_id: `paper_long_run_supervisor_v2`
- direction: `LONG`

## Baseline metrics
- expectation: `0.0`
- profit_factor: `5.55`
- max_drawdown: `8.3333333`
- win_rate: `0.6`
- consecutive_losses: `1`
- closed_trades: `20`

## Optimized metrics
- expectation: `22.7`
- profit_factor: `0.0`
- max_drawdown: `0.0`
- win_rate: `1.0`
- consecutive_losses: `1`
- closed_trades: `13`

## Comparison
- expectancy_delta: `22.7`
- profit_factor_delta: `-5.55`
- win_rate_delta: `0.4`
- drawdown_delta: `-8.3333333`
- consecutive_losses_delta: `0`

## Verdict and gates
- verdict_change: `degraded`
- walk_forward_improved: `False`
- optimization_improved_candidate: `False`
- candidate_status: `REJECT`
- remaining_blockers: `drawdown_containment, insufficient_sample`

## Remaining blockers and recommendations
- consecutive loss profile remains bounded by controls but sample size pressure persists.
- consecutive loss throttle may need a larger historical basket to avoid trade-count contraction.
- weak windows remain because of low sample depth after control application.
- tune controls conservatively before retesting in Packet U.
