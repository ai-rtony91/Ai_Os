# Forex Daily Profit Execution Evidence V1

This evidence layer refocuses Forex work on the live-profit path:
controlled risk, daily execution-readiness review, protected demo evidence,
and later live-micro exception review only after owner review.

The evaluator is metadata-only. It does not call a broker, place demo trades,
place live trades, read credentials, store credentials, move money, create a
scheduler, create a daemon, create a webhook, or start a dashboard runtime.

## Profit Evidence Goal

The module evaluates whether sanitized Forex metadata shows enough evidence to
review a daily profit attempt path. It checks sample count, positive
expectancy, profit factor, drawdown limits, walk-forward status,
out-of-sample status, spread/slippage modeling, and daily target definition.

The output never guarantees profit. It never promises a fixed return. It never
authorizes live trading.

## Return Discovery Bands

Return bands are observation labels only:

- `BELOW_PROFIT_THRESHOLD`
- `DAILY_PROFIT_EVIDENCE_PRESENT`
- `TWENTY_PERCENT_REVIEW_BAND`
- `FIFTY_PERCENT_REVIEW_BAND`
- `ONE_HUNDRED_PERCENT_REVIEW_BAND`
- `ONE_HUNDRED_TWENTY_PERCENT_STRESS_REVIEW_BAND`

The 20%, 50%, 100%, and 120% labels are review bands, not targets or promises.
The 100% and 120% bands require stress review and drawdown review before any
future packet can move forward. Excessive drawdown blocks even when return
metadata is high.

## Daily Cadence

The daily cycle requires:

- pre-trade check readiness
- defined execution window
- required post-trade review
- required daily P/L record
- no second trade without review
- owner stop control

This supports a reusable daily, weekly, monthly, and yearly review cadence. The
cadence is for review and compounding analysis only. It does not create money
movement or banking authority.

## Banking Freeze

Banking, withdrawal, transfer, debit-card rails, bank rails, ACH, wire, sweep,
bucket purge, and money movement are frozen.

Banking deferred until realized profit exists and owner explicitly approves
transfer work.

Any banking-focused metadata routes back to
`AIOS_FOREX_DAILY_PROFIT_EXECUTION_EVIDENCE_CAMPAIGN_V1` with
`BLOCKED_BY_BANKING_FOCUS`.

## Next Path

When evidence is ready, the next useful packet is
`AIOS_FOREX_PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_V1`.

A live-micro exception review remains a separate owner-reviewed path. This
module does not approve a demo order, live order, credential use, broker call,
banking work, withdrawal, transfer, commit, push, PR, or merge.
