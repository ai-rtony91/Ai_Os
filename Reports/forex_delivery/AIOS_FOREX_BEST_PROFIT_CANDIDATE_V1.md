# AIOS Forex Best Profit Candidate Report V1

## Best Candidate
- **Strategy**: `paper_long_run_supervisor_v2`
- **Candidate**: `c1-eur-buy`
- **Direction**: LONG

## Why this is the best candidate (current evidence)
1. Highest candidate payoff quality in this deterministic set (`+200.00` paper expectancy on one closed trade).
2. Highest directional alignment with observed edge (LONG-only run in current output; SHORT candidates are currently rejected before closure).
3. Best-in-class combined risk posture among available closed trades (profit-only path, max drawdown `0.00`).
4. Same paper profitability geometry as `c3-nzd-buy` but higher-order tie-breaker by candidate cycle/ordering.

## Evidence support
- Long-run supervisor output:
  - Closed trade count: `3` total
  - Approved trades: `3`
  - Rejected trades: `6`
  - Aggregate realized P&L: `+480.00`
  - Aggregate drawdown: `0.00`
- Candidate `c1-eur-buy` closed-leg proof:
  - Direction: LONG
  - Realized P&L: `+200.00`
  - Risk/reward: 1% risk with 1.0000% point move to target at 20000 units
  - Close reason: take-profit
- Safety gates:
  - paper-only mode confirmed
  - no broker/network/credential/order execution

## What prevents promotion
- Promotion gate remains blocked by **insufficient evidence depth**:
  - Minimum sample size not met for governed readiness (`minimum_sample_size=20`)
  - No complete walk-forward evidence matrix yet (`insufficient_windows` / `insufficient_passing_windows`)
  - No verified historical candidate train beyond one-shot long-run fixture run

## Next safe action
- Continue deterministic evidence build in paper-only mode:
  - accumulate additional long and short candidate batches
  - produce walk-forward windows with at least 2+ windows and passing windows parity
  - re-run portfolio ranking and promotion decision after safety gates remain clear
