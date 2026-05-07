# Broker Adapter Approval Gates Draft

## Purpose

This draft defines approval gates before any future broker adapter code. It is documentation only.

## Required Stage Gates

Stage 6 telemetry must mature first.

Stage 7 signal intelligence must mature first.

Stage 8 broker/OANDA boundary docs must remain explicit that implementation is not approved by default.

## Required Approval Inputs

Before any broker adapter code is considered, the project needs:

- risk policy approval
- legal/trading disclaimer placeholder
- secrets management plan
- sandbox-only plan
- dry-run execution simulation plan
- audit logging plan
- rollback plan
- kill-switch plan
- explicit human approval before each escalation

## Escalation Gates

Each escalation requires separate approval:

- docs-only planning
- dry-run simulation
- sandbox design
- sandbox implementation
- paper/practice review
- live execution review

No gate implies the next gate.

## Fail-Closed Conditions

Future adapter planning must fail closed if it requests credentials, `.env`, account IDs, live market execution data, broker tokens, webhooks, order paths, strategy activation, or unattended execution.

## Non-Approval Statement

This draft does not approve broker code, OANDA API clients, credentials, broker orders, paper trading, practice trading, live trading, API calls, services code, automation code, or GitHub actions.
