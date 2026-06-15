# AIOS Forex Builder Evidence Aggregator

Packet: `PKT-AIOS-FOREX-BUILDER-EVIDENCE-AGGREGATOR`

## Purpose

The evidence aggregator combines local backtest, walk-forward, cost model, risk gate, and paper-forward ledger evidence into one bundle for dashboard and readiness review.

It is a pure local function. It writes no reports by default.

## Local API

- `aggregate_forex_evidence(backtest_result, walk_forward_summary, risk_gate, paper_summary=None) -> dict`
- `classify_evidence_bundle(bundle) -> FAIL | WATCHLIST | PAPER_FORWARD_READY`

## Output Classes

Allowed:

- `FAIL`
- `WATCHLIST`
- `PAPER_FORWARD_READY`

Forbidden:

- `LIVE_READY`

## Required Bundle Fields

- backtest result
- walk-forward summary
- cost model
- risk gate result
- paper-forward ledger summary
- blockers
- next safe action

Paper-forward readiness remains local research status only. Live readiness remains blocked.
