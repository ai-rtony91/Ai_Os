# OANDA Boundary Draft

## Purpose

This draft defines the OANDA boundary for AI_OS. It is documentation only and does not create implementation, broker access, credentials, telemetry collection, or execution behavior.

## Stage Placement

OANDA belongs to Stage 8 Broker/Execution.

OANDA is not approved for implementation yet. It is a future boundary topic that must remain behind telemetry/reporting maturity, signal intelligence maturity, risk controls, legal/compliance placeholders, and explicit human approval.

## Boundary Documentation Only

This file may describe future constraints and review requirements. It does not approve:

- API client code
- OANDA token use
- account ID capture
- `.env` reads or writes
- live orders
- practice orders
- paper-trading execution
- webhook execution
- credential storage
- broker adapter code

## Future Relationship To Trading Engine V1

Trading Engine V1 remains a separate future trading-system concern. AI_OS may later define how a broker boundary is reviewed, but AI_OS must not mix system-level orchestration docs with trading execution logic unless a future approved file clearly states the boundary.

## Future Relationship To Telemetry / Reporting

OANDA planning depends on telemetry/reporting boundaries that prove system state, approval state, risk state, validator state, and blocked execution state without collecting broker credentials or broker account data.

## Future Relationship To Risk Controls

Any future OANDA review requires risk policy alignment, execution-blocking gates, audit logging, rollback planning, kill-switch planning, and explicit human approval.

## Non-Approval Statement

This draft does not approve OANDA API clients, broker adapter implementation, sandbox access, practice trading, paper trading, live trading, credential access, or order paths.
