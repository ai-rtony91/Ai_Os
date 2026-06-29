# AIOS Forex Capital Bucket and Return Target Policy V1

## Scope
- This policy governs evidence-era transitions toward controlled live-money proof.
- It is active only as part of the master autonomy completion lane.
- All execution-side capabilities remain blocked in this phase.

## Core targets
- `daily_return_target_percent`: `100`
- `daily_stretch_target_percent`: `120`
- `fixed_daily_starting_risk_bucket_percent`: `1.00`
- `protected_profit_bucket_percent`: `0.20`
- `weekly_review_bucket_percent`: `0.40`
- `capital_bucket_mode`: `FIXED_DAILY_BUCKET`

The two target percentages are completion metrics, not trade commands.  
`100` means planned bucket completion.
`120` means stretch review condition for controlled governance review only.

## Bucket definitions
- Fixed daily starting risk bucket
  - Purpose: hard cap for all same-day proposal activity.
  - Default budget: `1.00` risk units.
  - Only evidence that passes policy gates can consume the budget.
- Protected profit bucket
  - Purpose: reserve to prevent overdraw after partial target attainment.
  - Fixed floor: `0.20` must remain uncommitted until post-trade review closes the day.
- Weekly review bucket
  - Purpose: isolate weekly compounding gate and trend checks from daily volatility.
  - Weekly threshold: `0.40` for controlled compounding consideration.
- Optional compound ladder
  - Level 1: keep fixed bucket (`1.00`) until all evidence gates are stable.
  - Level 2: raise controlled ladder only after approved weekly evidence review.
  - Level 3: no full-balance compounding until evidence threshold is met.

## Control rules
- `stop_after_target_rule`
  - If daily bucket completes at `100`, pause any new proposal creation for the current cycle.
  - Sweep protected profit bucket before resuming.
- `stop_after_max_loss_rule`
  - On configured max-loss gate fail, freeze lane and hold execution proposals.
  - State cannot progress to micro-review without risk reset evidence.
- `max_trades_per_day`: `4`
- `max_trades_per_hour`: `2`
- `max_open_trades`: `1`
- `no_forced_hourly_trade_rule`
  - No hourly forced entry.
  - Scan may run; proposals require valid signal, gate pass, and bucket fit.
- `no_full_balance_compounding`
  - Full-balance compounding is disabled until:
    - two full review cycles are complete,
    - governor and owner gates approve,
    - weekly compounding criteria are met.

## Sweep and reset policy
- End-of-day sweep
  - Move captured positive P/L into protected-profit accounting.
  - Reset daily starting bucket for the next calendar day.
- Reset-next-day
  - Reset risk budget and trade counters at day boundary.
  - Keep weekly review bucket carry-forward only for review evidence.
- Weekly compounding criteria
  - Minimum completed reviewed cycles: `2`.
- Compounding gate
  - Only after owner + governor signoff and a stable evidence freshness snapshot.
  - Daily execution remains subject to one-micro-setup controls.

## Live-money proof start mode
- The lane starts as evidence micro-path with one live exception candidate.
- No 22-hour free-run paths.
- No broker API or order placement is enabled by this policy.
