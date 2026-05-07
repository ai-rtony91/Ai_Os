# AIOS Strategy Registry Draft

Status: Draft scaffold

## Purpose

Create a local-first registry for strategy concepts used by the AI_OS signal intelligence layer.

## Required Registry Fields

- Strategy ID
- Strategy name
- Market or asset class
- Signal inputs
- Regime assumptions
- Validation status
- Backtest evidence status
- Paper-trading status
- Approval status
- Known gaps

## Allowed Status Values

- DRAFT
- NEEDS_EVIDENCE
- PAPER_TRADING_ONLY
- BLOCKED
- RETIRED

## Blocked Actions

- Live order placement.
- Broker credential usage.
- Production routing.
- Claims of profitability without verified evidence.
