# AIOS Forex Supervised Demo Trade Review Bundle V1

## What Anthony Reviews

The Supervised Demo Trade Review Bundle V1 turns the readiness bridge result into an Anthony-readable local review packet. It summarizes the sanitized broker snapshot, candidate context, risk review, position sizing, order plan, operator ticket, post-trade evidence plan, and feedback routing plan.

No broker call was made. No trade placed.

## Snapshot Review Section

The snapshot section reports sanitized snapshot intake status, broker snapshot review status, and account readiness status from the landed broker snapshot intake stack.

## Candidate Review Section

The candidate section reports:

- Selected strategy: `Supertrend`
- Candidate id: `supertrend-review-ready-sample`
- Instrument: `EUR_USD`
- Direction: `LONG`
- Candidate readiness status

## Risk Review Section

The risk section reports local-only risk gate status, maximum loss, and whether any blocker prevents owner review. It does not approve execution.

## Order Plan Section

The order plan section reports:

- Entry price: `1.1000`
- Stop loss: `1.0950`
- Take profit: `1.1100`
- Proposed units: `20000`
- Max loss: `100.00`
- Expected reward: `200.00`
- Reward-to-risk: `2`

## Operator Warning

Do not execute unless Anthony explicitly approves.

## Post-Trade Evidence Plan

The post-trade evidence section is only a plan. Evidence capture remains blocked until a supervised demo trade exists and sanitized post-trade evidence is available.

## Feedback Routing Plan

The feedback routing section is only a plan. Feedback routing remains blocked until sanitized post-trade evidence exists.

## Blocked Actions

- Demo execution
- Broker action
- Real money
- Compounding
- Bank movement
- Live trading
- Credential access
- Account ID persistence

## Next Safe Action

Anthony may review the local bundle manually. AI_OS must not call a broker, place a trade, or treat the review bundle as approval.
