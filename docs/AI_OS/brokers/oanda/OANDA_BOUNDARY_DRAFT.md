# OANDA Boundary Draft

## Purpose

This draft defines where OANDA belongs in AI_OS planning. It is documentation only and does not create OANDA API code, broker adapters, credentials, `.env` changes, live API calls, paper trading, live trading, or order placement.

## Stage Placement

OANDA belongs in Stage 8 Broker/Execution as a future broker boundary topic.

AI_OS should not implement OANDA until earlier stages provide:

- telemetry and reporting boundaries
- signal intelligence review boundaries
- legal/compliance placeholders
- risk policy alignment
- explicit human approval

## Allowed OANDA Planning

Allowed future planning may include:

- OANDA sandbox/practice account requirements
- credential exclusion rules
- no-live-execution rules
- adapter interface boundaries
- audit logging requirements
- rollback requirements
- operator approval gates

## Blocked OANDA Actions

The following remain blocked:

- OANDA API client code
- account connection
- credential access
- token storage
- `.env` reads or writes
- account ID capture
- pricing stream connection
- order placement
- order modification
- order cancellation
- paper trading
- live trading
- webhook routing
- strategy activation

## Non-Approval Statement

This draft does not approve OANDA integration, sandbox connection, practice trading, paper trading, live trading, credential access, or broker execution.
