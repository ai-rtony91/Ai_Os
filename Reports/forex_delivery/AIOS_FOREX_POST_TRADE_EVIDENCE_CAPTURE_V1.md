# AIOS Forex Post-Trade Evidence Capture V1

## Purpose

Post-trade evidence capture defines what AIOS should collect after a future supervised demo trade exists.

No trade was placed by this stack.

## What To Capture After A Demo Trade

- Sanitized trade reference
- Strategy ID
- Instrument
- Direction
- Planned entry and actual entry
- Planned stop loss and actual stop loss
- Planned take profit and actual take profit
- Planned units and actual units
- Open time and close time
- Planned risk
- Realized P/L
- Result
- Slippage
- Spread at entry and exit
- Max adverse excursion
- Max favorable excursion
- Broker reconciliation status
- Sanitization status
- Notes

## Planned Vs Actual

The capture format records planned values against actual values so the proof system can see whether the supervised demo trade followed the reviewed plan.

## Profit / Loss

Profit, loss, and breakeven are captured as classifications. Missing result, unreconciled evidence, and unsanitized evidence are blocked.

## Feedback Into Proof Systems

Captured post-trade evidence routes back into:

- Profit Proof Ledger
- Strategy Proof Engine
- Expectancy Strength Router
- Demo Review Engine
- Strategy Promotion Router
- Real Evidence Depth Engine

## Next Safe Action

Use this only after a real supervised demo trade has been manually approved and completed. Do not fabricate fills or profit.
