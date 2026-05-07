# AIOS Signal Intelligence Source Of Truth

Status: Draft source-of-truth planning document
Stage: 7
Mode: Documentation only

## Purpose

This document defines the source-of-truth boundary for AI_OS signal intelligence. It describes how signal concepts, evidence, scoring, and validation should be organized before any future paper-trading or backtesting workflow consumes them.

## Authority

This file is the planning authority for Stage 7 signal intelligence until a later approved document supersedes it.

Related Stage 7 files:

- `AIOS_CONFLUENCE_SCORING_MODEL_DRAFT.md`
- `AIOS_MARKET_REGIME_ANALYSIS_DRAFT.md`
- `AIOS_SIGNAL_VALIDATION_RULES_DRAFT.md`
- `docs/AI_OS/strategy_registry/AIOS_STRATEGY_REGISTRY_SCHEMA_DRAFT.md`
- `docs/AI_OS/backtesting/AIOS_BACKTEST_IMPORT_RULES_DRAFT.md`

## Signal Intelligence Boundary

Signal intelligence may describe market observations, screening rules, regime labels, confluence scoring, validation status, and paper-trading-only records.

Signal intelligence must not:

- Connect to brokers.
- Place orders.
- Route orders.
- Read or store real broker credentials.
- Enable live trading.
- Claim profitability without verified evidence.

## Required Signal Record Fields

- Signal ID
- Strategy ID
- Instrument or market
- Timeframe
- Timestamp
- Regime tag
- Signal direction
- Input evidence list
- Confluence score
- Validation score
- Paper-trading-only status
- Source evidence path
- Known gaps
- Approval status

## Evidence Rules

- Every non-obvious claim must reference source evidence.
- Missing evidence is UNKNOWN.
- Conflicting evidence is MISMATCH.
- Unverified claims are INVALID DATA.
- Backtest or paper-trade results do not authorize live execution.

## Approval Gate

Any future automation that writes signal records, imports market data, or connects to external data sources requires a separate DRY_RUN and explicit human approval.
