# AIOS Backtest Ingestion Draft

Status: Draft scaffold

## Purpose

Define how AI_OS may ingest backtest evidence for strategy review without creating an execution path.

## Candidate Inputs

- Strategy ID
- Dataset source
- Date range
- Market regime tags
- Entry and exit assumptions
- Risk assumptions
- Fees, spread, and slippage assumptions
- Result summary
- Evidence file path

## Validation Requirements

- Source must be logged before evidence is treated as valid.
- Missing inputs are UNKNOWN.
- Conflicting evidence must be marked MISMATCH.
- Unverified claims are INVALID DATA.

## Boundary

Backtest ingestion is analysis-only and cannot trigger live broker actions.
