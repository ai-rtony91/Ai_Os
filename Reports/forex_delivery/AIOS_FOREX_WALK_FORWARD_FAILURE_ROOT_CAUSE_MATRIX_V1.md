# AIOS Forex Walk Forward Failure Root Cause Matrix V1

## Candidate
- c1-eur-buy (`paper_long_run_supervisor_v2`)

| window | failing | root causes |
|---|---|---|
| wf-01 | no | none |
| wf-02 | yes | expectancy, profit_factor, win_rate, trade_concentration, consecutive_loss_profile |
| wf-03 | yes | expectancy, profit_factor, win_rate, consecutive_loss_profile |
| wf-04 | yes | expectancy, profit_factor, drawdown, trade_concentration, consecutive_loss_profile |

## Summary
- failing windows: `wf-02, wf-03, wf-04`
- passing windows: `wf-01`
- systemic failures: `consecutive_loss_profile, expectancy, profit_factor, win_rate`
- isolated failures: `drawdown, trade_concentration`
- verdict: `REQUIRE_OPTIMIZATION`
- confidence score: `0`
