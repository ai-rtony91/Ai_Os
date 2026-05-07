# AIOS Signal Validation Rules Draft

Status: Draft planning document
Stage: 7

## Purpose

Define validation rules for AI_OS signal intelligence before any signal can be used in paper-trading-only review.

## Required Validation Checks

- Strategy ID exists in the strategy registry.
- Signal timestamp is present.
- Instrument or market is present.
- Timeframe is present.
- Regime tag is present or marked UNKNOWN.
- Evidence list is present.
- Source evidence path is present.
- Confluence score is present or marked UNKNOWN.
- Validation score is present or marked UNKNOWN.
- Paper-trading-only status is explicit.

## Invalid Conditions

- Live execution flag present.
- Broker credential reference present.
- Missing strategy ID.
- Missing timestamp.
- Missing evidence path.
- Profitability claim without verified evidence.
- Conflicting evidence not marked MISMATCH.

## Validation Status Values

- PASS
- FAIL
- NEEDS_EVIDENCE
- MISMATCH
- INVALID_DATA
- UNKNOWN

## Boundary

Validation status never authorizes live trading. It only allows a signal to move into controlled review or paper-trading-only analysis.
