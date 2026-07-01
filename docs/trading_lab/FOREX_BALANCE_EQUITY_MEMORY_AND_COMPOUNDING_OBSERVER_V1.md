# Forex Balance Equity Memory And Compounding Observer V1

This packet adds a metadata-only balance/equity memory observer for AIOS Forex work.

AIOS can recognize balance and equity movement across trade, day, week, month, runtime session, and Vacation Mode periods. The evaluator computes deltas, realized profit from baseline, equity drift, target detection, compounding readiness, profit-protection routing, and scale-down routing.

## Balance Memory

The observer accepts sanitized numeric snapshots for trade open/close balance, day start/current balance, week start/current balance, month start/current balance, Vacation Mode start/current balance, current balance, current equity, realized PnL, and unrealized PnL.

Runtime observation may be frequent, but durable repo evidence should be event-based or controlled cadence. The observer reports learning metadata; it does not mutate strategy logic.

## Compounding

Compounding requires verified realized profit, sanitized receipts/proof, clean drawdown and daily-loss gates, and an owner policy. If compounding is disabled, the evaluator keeps tracking profit stacking without recommending scaling.

Target return or target balance routes to profit-protection review. Drawdown breach routes to risk scale-down review. Positive realized profit with clean gates can route to governed compounding capital scaling review.

## Withdrawal And Bank Routing

Stacking profit is separate from withdrawal. Banking, withdrawal, bank routing, transfer work, and money movement remain deferred to a future owner-approved packet.

This packet does not execute trades, call brokers, read credentials, create a runtime process, move money, build withdrawal, or build bank routing.

## Next Safe Packets

- Compounding eligible: `AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1`
- Observation only: `AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1`
- Hold: `AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1`
- Target reached: `AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1`
- Drawdown scale-down: `AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1`
