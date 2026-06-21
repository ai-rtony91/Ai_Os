# AIOS Forex OANDA Demo Integration Boundary Plan V1

## Purpose
Define the safe boundary for future OANDA demo integration planning.

## Requirements
- Demo-only mode required.
- Live endpoint prohibited.
- Credentials prohibited in repo.
- Account identifiers prohibited in repo.
- Order execution prohibited.
- Network transport prohibited until separately authorized.
- Endpoint calls prohibited until separately authorized.

## Future Read-Only Probe Requirements
Future probes must remain read-only, evidence-recorded, replayable, sanitized, and kill-switch governed.

## Transport Boundary
Future transport must be isolated behind broker runtime gates and must never bypass endpoint mode, credential boundary, account boundary, no-order connector, or final readiness checks.

## Evidence
Every future broker-facing event must preserve correlation ID, timestamp, endpoint mode, governance status, sanitized metadata, blocked reasons, and replay references.

## Halt / Rollback
Any live endpoint, credential leak, account ID leak, order capability, network transport violation, stale approval, or kill-switch activation must block the path.
