# OANDA No Live Execution Rules Draft

## Purpose

This draft defines no-live-execution rules for OANDA planning. It is documentation only.

## Execution State

`execution_allowed=false`

This value must remain false for all OANDA-related planning until a future explicit human approval changes scope.

## Blocked Broker Execution

All broker execution is blocked, including:

- live account access
- practice account execution
- paper-trading execution through broker paths
- order placement
- order modification
- order cancellation
- broker routing
- webhook-to-order paths
- strategy-to-broker automation

## Blocked Credential And Account Data

The following are blocked:

- credentials
- tokens
- account identifiers
- `.env` access
- credential storage
- broker profile data
- live market execution data

## Docs-Only Planning

Only docs-only planning is approved in this batch. No code, service, automation, dashboard control, API call, broker client, telemetry writer, or persistence behavior is approved.

## Human Approval Requirement

Any future sandbox, practice, paper, or live work requires separate human approval after telemetry, legal/compliance, risk, secret handling, audit, rollback, and kill-switch requirements are reviewed.
