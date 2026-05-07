# AIOS Confluence Scoring Model Draft

Status: Draft planning document
Stage: 7

## Purpose

Define a planning model for combining multiple independent signal inputs into a non-executing confluence score.

## Scoring Boundary

Confluence scoring is advisory and analysis-only. It does not authorize order placement, order routing, live broker calls, or trade execution.

## Candidate Input Categories

- Trend context
- Market regime
- Momentum condition
- Volatility condition
- Support or resistance context
- Session timing context
- Strategy-specific setup evidence
- Risk context

## Draft Score Bands

- 0 to 24: Insufficient confluence
- 25 to 49: Weak confluence
- 50 to 74: Moderate confluence
- 75 to 100: Strong confluence candidate

## Validation Requirements

- Inputs must be independently observable.
- Correlated duplicate inputs should not be double-counted.
- Missing inputs must be scored as UNKNOWN, not assumed.
- Manual overrides require a reason and evidence path.

## Unknowns

- UNKNOWN: final score weights.
- UNKNOWN: minimum paper-trade threshold.
- UNKNOWN: final strategy-specific scoring overrides.
