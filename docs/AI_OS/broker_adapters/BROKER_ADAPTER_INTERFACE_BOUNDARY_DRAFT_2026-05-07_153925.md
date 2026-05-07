# Broker Adapter Interface Boundary Draft

## Purpose

This draft defines the broker adapter interface as a future concept only. It is documentation only and does not create implementation.

## Future Concept

A future broker adapter interface may describe how AI_OS would validate readiness before broker-related behavior. The concept must remain blocked until separate approval.

## Possible Future Abstract Capabilities

Future abstract capabilities may include:

- validate signal
- validate account mode
- calculate order intent
- block execution
- produce audit record

These are conceptual planning labels only.

## Explicit Non-Approval

This draft does not approve:

- broker classes
- service code
- API clients
- credentials
- order submission
- order modification
- order cancellation
- webhook execution
- strategy activation
- telemetry collection from broker systems

## Boundary Rule

The safest default broker adapter state is BLOCKED and read-only. Any escalation requires separate DRY_RUN, human approval, risk review, legal/compliance review, and secret handling review.
