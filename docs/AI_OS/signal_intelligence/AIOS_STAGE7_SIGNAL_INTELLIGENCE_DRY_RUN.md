# AIOS Stage 7 Signal Intelligence DRY_RUN

Status: Draft scaffold
Mode: Planning only

## Purpose

Define the signal intelligence layer for AI_OS without activating trading execution.

## Planned Components

- Signal intelligence registry for approved signal concepts.
- Screener logic boundary for non-executing market scans.
- Market regime analysis rules for tagging trend, range, volatility, and session context.
- Confluence scoring model for combining independent evidence.
- Validation scoring model for separating observed evidence from assumptions.
- Signal log requirements for timestamped, paper-trading-only records.
- Backtest ingestion handoff to `docs/AI_OS/backtesting`.

## Safety Rules

- No broker connection.
- No live orders.
- No real account identifiers.
- No automatic trade execution.
- Any unknown data source, scoring rule, or strategy assumption must be labeled UNKNOWN.

## Outputs

Future APPLY work may add schemas, fixtures, and dry-run validators after human approval.
