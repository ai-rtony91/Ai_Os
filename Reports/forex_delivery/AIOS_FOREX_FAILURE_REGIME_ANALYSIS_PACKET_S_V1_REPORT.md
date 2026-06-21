# AIOS Forex Failure Regime Analysis Packet S V1

## Paper-only scope
- paper-only: True
- no broker connectivity
- no credentials
- no account IDs
- no network
- no order execution
- no demo trading
- no live trading

## Regime result
- candidate: `c1-eur-buy`
- strategy: `paper_long_run_supervisor_v2`
- packet dependency: `AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1`
- failing windows: `wf-02, wf-03, wf-04`
- passing windows: `wf-01`
- verdict: `REQUIRE_OPTIMIZATION`
- confidence score: `0`
- best candidate status: remains best candidate by deterministic walk-forward tie-breakers, but not yet ready

## Root causes
- expectancy: negative on wf-02/wf-03/wf-04
- profit factor: low on wf-02/wf-03/wf-04
- drawdown: excessive on wf-04
- win rate: low on wf-04 (single negative-heavy regime)
- trade concentration: high in wf-04 due single large negative trade
- consecutive loss profile: elevated in wf-02/wf-03/wf-04

## Classification
- systemic failures: expectancy, profit_factor, win_rate, consecutive_loss_profile
- isolated failures: drawdown, trade_concentration
- recommendations: optimize entry quality, stop-loss sizing, and window sizing before further optimization cycle.
