# Broker Adapter Interface Boundary Draft

## Purpose

This draft defines a documentation-only boundary for future broker adapter interface planning. It does not create code, APIs, credentials, `.env` changes, telemetry writers, persistence, or execution paths.

## Future Interface Concept

A future broker adapter may be described as a boundary layer between AI_OS review state and broker-specific systems. This is not approved for implementation.

Future planning may define:

- adapter responsibility limits
- blocked actions
- read-only status concepts
- sandbox-only review gates
- audit logging needs
- rollback expectations

## Blocked Interface Behavior

The adapter boundary must not:

- connect to brokers
- read credentials
- write credentials
- place orders
- modify orders
- cancel orders
- stream market data
- trigger webhooks
- activate strategies
- persist broker telemetry
- expose execution controls in dashboard UI

## Required Future Gates

Any future adapter implementation proposal requires separate DRY_RUN, approval, protected-file review, security review, risk policy review, and legal/compliance review.

## Non-Approval Statement

This draft does not approve adapter code, interfaces in services, API clients, broker calls, credential access, paper trading, or live trading.
