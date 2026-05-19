# Trading Bot Foundation Mock-Only Plan

## Core Parts

- Strategy Registry: store strategy names, versions, assumptions, evidence, and approval state.
- Signal Scoring: score mock signals by confidence, confluence, rejection reason, and readiness.
- Regime Detection: tag market state before any mock trade decision.
- Mock Execution Ledger: record simulated entries, exits, timestamps, and outcomes only.
- Risk Governor: block unsafe ideas before mock execution.
- Trade Journal: capture reasoning, screenshots/evidence references, mistakes, and lessons.
- Performance Metrics: calculate expectancy, win rate, drawdown, and review status from mock data.

## Flow

Strategy -> Signal -> Regime -> Risk -> Mock Ledger -> Journal -> Metrics

## Blocked

- No broker.
- No OANDA.
- No API keys.
- No real orders.

## Next Dashboard Goal

Add one clear Trading Lab card showing: Next safe action.
