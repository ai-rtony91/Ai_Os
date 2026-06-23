# AIOS Forex Compounding Capital Bucket Supervisor V1

## Packet ID

AIOS-MERGE-1047-THEN-FOREX-COMPOUNDING-CAPITAL-BUCKET-SUPERVISOR-V1

## Branch

feature/forex-compounding-capital-bucket-supervisor-v1

## Mission Outcome

Created the AIOS Forex Compounding Capital Bucket Supervisor. The supervisor models capital growth by governed cycles instead of random isolated trades. It tracks the bucket, deployed capital, reserves, realized and unrealized P/L, cycle return progress, quota readiness, eligible pair allocation, collection state, redistribution readiness, risk gates, evidence gates, and dashboard-ready gauge data.

## Compounding Logic Summary

AIOS must compound by governed capital cycles, not gamble by trades. The supervisor treats the campaign target as a quota for review and collection logic, not as a profit promise. It never forces trades to hit the quota and never grants execution authority.

## Bucket To Pairs To Collect To Bigger Bucket To Redistribute Cycle

The modeled cycle is:

1. start with a capital bucket
2. deploy only risk-approved portions into eligible Forex pairs
3. track realized and unrealized P/L
4. track current return percentage against the cycle quota
5. mark target reached when the quota range is reached
6. collect profit into the bucket
7. recalculate the larger bucket
8. review redistribution across eligible pairs for the next cycle

## 100%-120% Campaign Quota Handling

The default target range is 100% to 120%. Below 100%, the supervisor returns `BUCKET_ACTIVE_ACCUMULATING` when risk, evidence, and policy gates pass. Between 100% and 120%, it returns `BUCKET_TARGET_REACHED_COLLECT_PROFIT`. Above 120%, it warns `over_target_return_collect_before_redeploy`.

## Future 150% Target Handling

The future 150% target is guarded. If `future_target_return_percent` is 150.0 and `allow_future_150_percent_target` is false, the supervisor blocks with `BUCKET_BLOCKED_POLICY`. It may use 150% only when explicitly allowed by policy.

## Scale-Invariant $5 To $200,000 Behavior

The supervisor uses percentage-based target and risk logic. A $5 bucket and a $200,000 bucket with the same return percentage produce the same cycle progress state. Dollar size does not change the compounding rule.

## No Forced Trades Rule

`force_trades_to_hit_quota` must be false. If a policy attempts to force trades to hit the quota, the supervisor blocks. Quota progress can continue only through valid setups and active gates.

## Pair Allocation Rules

Pairs are selected only when they are eligible, meet minimum quality, pass spread checks, and are affordable against reserve capital. Poor-quality, spread-blocked, and margin-unaffordable pairs are excluded deterministically.

## Profit Collection Rules

Profit collection becomes ready only when the target quota is reached and policy allows collection. The collection plan remains a review output and does not execute a collection or broker action.

## Redistribution Rules

Redistribution respects `max_pairs_per_cycle` and includes only eligible pairs. It models the next-cycle review path after collection, but it does not place trades.

## 3D Animated Progress Gauge Readiness

The supervisor returns dashboard-ready gauge data:

- `forex_return_100_120_progress` for current cycle return progress
- `account_goal_100k_progress` for total account goal progress

Both gauges include `visual_intent` fields for future execution-grade animated 3D dashboard rendering.

## Risk Gates

The supervisor requires risk gate pass, kill switch readiness, daily stop readiness, max loss gate readiness, positive bucket risk limits, positive pair risk limits, margin safety, no averaging down, and one cycle at a time.

## Evidence Gates

The supervisor requires evidence capture readiness, trade outcome tracking, profit collection tracking, redistribution tracking, sanitized money state readiness, and no-profit-guarantee acknowledgement.

## Execution Authority False

All execution authority fields remain false in every output:

- `execution_allowed`
- `demo_order_allowed`
- `live_order_allowed`
- `broker_write_allowed`
- `autonomous_order_allowed`
- `scheduler_allowed`
- `daemon_allowed`
- `webhook_allowed`

## Validation Results

- `python -m py_compile automation/forex_engine/compounding_capital_bucket_supervisor_v1.py tests/forex_engine/test_compounding_capital_bucket_supervisor_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_compounding_capital_bucket_supervisor_v1.py -q`: PASS, 18 passed
- `python -m compileall automation/forex_engine tests/forex_engine`: PASS
- `git diff --check`: PASS

## Git Status

Expected local APPLY state before exact-file staging. `docs/legal/` remains outside lane and untouched.

## Next Safe Action

Run the scoped validator chain, stage only the three approved compounding supervisor files, commit, push, and open a PR into `main`. Do not merge, do not call broker, and do not place a trade.
