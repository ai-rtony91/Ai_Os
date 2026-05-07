# AIOS Market Regime Analysis Draft

Status: Draft planning document
Stage: 7

## Purpose

Define market regime labels and boundaries for AI_OS signal intelligence planning.

## Candidate Regime Labels

- TREND_UP
- TREND_DOWN
- RANGE
- BREAKOUT
- REVERSAL
- HIGH_VOLATILITY
- LOW_VOLATILITY
- NEWS_RISK
- UNKNOWN

## Required Regime Evidence

- Instrument or market
- Timeframe
- Observation timestamp
- Regime label
- Evidence inputs
- Confidence level
- Known gaps
- Source evidence path

## Rules

- Regime labels are descriptive, not executable trade instructions.
- UNKNOWN must be used when evidence is missing or unclear.
- NEWS_RISK must not trigger automated trading behavior.
- Regime analysis cannot bypass validation or human approval gates.

## Future Work

Future approved work may define formal regime thresholds, fixtures, and DRY_RUN validators.
