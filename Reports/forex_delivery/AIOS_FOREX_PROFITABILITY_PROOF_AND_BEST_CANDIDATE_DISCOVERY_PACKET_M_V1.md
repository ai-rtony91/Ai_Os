# AIOS Forex Profitability Proof And Best Candidate Discovery Packet M V1

## Summary
Packet M reviews current profitability tooling after Packet L.

## Finding
AIOS now has tooling to rank LONG and SHORT candidates by expectancy, profit factor, drawdown, win rate, sample size, and consecutive win/loss profile.

## Current Limitation
This packet does not prove a real live profitable strategy. It proves AIOS can evaluate and rank profitability candidates using paper-only evidence.

## Best Candidate Requirement
A candidate must satisfy:
- sample size >= 20
- expectancy > 0
- profit factor >= 1.25
- max drawdown <= 10%
- supported direction LONG or SHORT

## Safety
No broker connectivity, credentials, account identifiers, network access, order execution, demo trading, or live trading introduced.
