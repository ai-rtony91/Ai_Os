# AIOS Forex Profit Proof Ledger V1

## Purpose
Profit Proof Ledger V1 is the canonical local-only evidence bucket after the Forex Profit Autonomy Master Bucket Pack V1. It evaluates multiple Forex strategy evidence records and answers whether a strategy has earned operator proof review.

The ledger does not claim guaranteed profit, does not place trades, does not call brokers, does not use credentials, does not approve real money, does not approve compounding, and does not approve bank movement.

## Proof Categories
- total trades.
- wins.
- losses.
- win rate.
- loss rate.
- realized P/L.
- expectancy.
- average win.
- average loss.
- profit factor.
- max drawdown.
- consecutive losses.
- recovery factor.
- sample depth.
- walk-forward status.
- out-of-sample status.
- paper versus demo comparison.
- strategy decay.
- broker reconciliation status.
- spread sensitivity.
- slippage sensitivity.
- latency observations.
- latency sensitivity.
- market regime coverage.
- risk controls.
- evidence confidence score.
- promotion score.
- blockers.
- next safe action.

## Scoring Model
- evidence_score measures proof categories that are present and passing.
- confidence_score weights core promotion gates.
- promotion_score ranks strategies by promotable status, expectancy, profit factor, sample size, drawdown, recovery, proof completion, and risk evidence.
- Missing proof remains UNKNOWN and is not converted into evidence.

## Promotion Gates
- Positive expectancy required.
- Minimum profit factor default: 1.25.
- Minimum total trades default: 30.
- Maximum drawdown default: 0.05.
- Maximum consecutive losses default: 3.
- Walk-forward proof must pass.
- Out-of-sample proof must pass.
- Broker reconciliation, spread, slippage, latency, market regime, strategy decay, and risk-control proof must be clear for promotable status.

## Blocker Rules
- Missing core evidence blocks proof.
- Negative expectancy blocks proof.
- Low profit factor blocks proof.
- Excessive drawdown blocks proof.
- Insufficient sample depth blocks proof.
- Missing walk-forward or out-of-sample proof blocks promotion.
- Missing broker reconciliation, spread, slippage, latency, market regime, decay, or risk proof keeps the candidate review-ready only or blocked.

## Permission Locks
next_demo_trade_allowed: false.
broker_action_allowed: false.
real_money_allowed: false.
compounding_allowed: false.
bank_movement_allowed: false.
owner_approval_required: true.

## Sample Results
Mixed sample:
- top_strategy: c2-eur-buy-stronger-review-ready.
- ledger_status: PROFIT_PROOF_LEDGER_PROMOTABLE.
- promotion_recommendation: PROMOTE_TO_OPERATOR_PROOF_REVIEW_ONLY.
- protected-action status: no trade, broker action, real money, compounding, or bank movement approved.

All-blocked sample:
- selected_candidate: NONE.
- no promotable strategy selected.
- next safe action is to repair blocked strategy evidence and rerun the ledger.

## Next Safe Action
Create a Candidate Review to Operator Decision Packet V1 for the top strategy only after this proof ledger is reviewed. Do not place trades or enable real money.
