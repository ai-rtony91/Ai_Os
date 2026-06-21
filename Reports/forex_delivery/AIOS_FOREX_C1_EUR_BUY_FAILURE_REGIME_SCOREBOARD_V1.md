# AIOS Forex C1 EUR BUY Failure Regime Scoreboard V1

## Safety
- paper-only: True
- no broker connectivity
- no credentials
- no account IDs
- no network
- no order execution
- no demo trading
- no live trading

## Outcome
- verdict: `REQUIRE_OPTIMIZATION`
- confidence_score: `0`
- c1-eur-buy remains best candidate: `True`

## Regime statistics
- failing windows: `wf-02, wf-03, wf-04`
- passing windows: `wf-01`
- root causes:
  - wf-01: none
- wf-02: expectancy, profit_factor, win_rate, trade_concentration, consecutive_loss_profile
- wf-03: expectancy, profit_factor, win_rate, consecutive_loss_profile
- wf-04: expectancy, profit_factor, drawdown, win_rate, trade_concentration, consecutive_loss_profile
- systemic failures: `consecutive_loss_profile, expectancy, profit_factor, win_rate`
- isolated failures: `drawdown, trade_concentration`

## Optimization recommendations
- reduce concentration by capping max loss impact per trade
- require stronger expectancy filter per walk-forward window
- rebuild long window guard for drawdown and loss-streak suppression
