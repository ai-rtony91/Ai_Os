# OANDA Sandbox Requirements Draft

## Purpose

This draft lists future requirements before any OANDA sandbox or practice work can be considered. It is documentation only and does not approve sandbox access.

## Not Approved Yet

OANDA sandbox, OANDA practice, paper execution, live execution, broker API calls, broker credentials, `.env` access, and broker adapter code are not approved.

## Requirements Before Sandbox Work

Future sandbox review would require:

- telemetry privacy boundary
- legal/trading disclaimer placeholder
- risk policy review
- API credential handling plan
- secret storage plan
- audit logging plan
- order simulation plan
- kill switch plan
- rollback plan
- human approval gate

## Order Simulation Boundary

Order simulation must remain separated from broker API calls unless a future approval explicitly permits sandbox-only behavior. Simulation concepts must not place real, practice, or paper orders through a broker.

## No API Code

This file contains no API code and does not approve future API code.

## Non-Approval Statement

This draft does not approve OANDA API clients, credential access, account access, practice orders, paper trading, live trading, webhook execution, or order paths.
