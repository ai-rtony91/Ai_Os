# AIOS FOREX BROKER DEMO INTERFACE CONTRACT PLAN V1

## Future Interface Boundaries

1. `Intent Envelope Boundary`  
   Accepts only governance/evidence metadata (no secrets, no IDs).

2. `Review Boundary`  
   Consumes review decisions and blockers only.

3. `Approval Boundary`  
   Requires human-owner approval artifacts and freshness.

4. `Handoff Boundary`  
   Produces sanitized transfer payload for external runtime, no execution.

5. `Attempt Boundary (Future)`  
   Receives only approved, preflight-passed handoff and returns sanitized attempt references.

## Allowed Read-Only Operations

- Inspect correlation ids and correlation lineage
- Inspect governance outcomes and blocker states
- Inspect timestamped approvals
- Inspect freshness/replay checks
- Inspect kill-switch/readiness flags
- Inspect outcome and status classification

## Prohibited Write Operations

- Writing credentials or secrets
- Writing account identifiers
- Writing private auth tokens
- Writing raw request/response payloads
- Writing broker payload material
- Writing network endpoint URL values
- Writing mutable execution state in repo artifacts

## Prohibited Order Operations

- `place_order`
- `modify_order`
- `cancel_order`
- `close_position`
- `open_position`
- `trade_modification`
- `market_order_request`

These must always remain disallowed in current phase.

## Endpoint Mode Dependency

- Supported/required modes:
  - `PRACTICE_DEMO`
  - `PAPER_DEMO`
- Deny any mode containing `LIVE`, `PRODUCTION`, or unrecognized classification.
- Endpoint proof and classification must be explicit and persisted as evidence fields.

## Credential Boundary Dependency

- External credentials only
- No credential value logging
- No credential material persistence
- No repo-read of environment-backed secrets by this phase
- Credential presence only as boolean redaction proofs

## Account Boundary Dependency

- External account metadata only
- No account id values
- No account id logging
- Account-related states not requested or stored
- Account presence only as boolean redaction proofs

## Audit Requirements

- Every interface action must emit:
  - timestamp
  - status
  - blockers
  - decision reason
  - evidence references
  - replay references
- Audit records must be sanitized and denylist-checked
- Evidence must include whether blocked, denied, or passed

## Broker-Agnostic Design Notes

- Contract names and fields should be broker-agnostic where semantics are shared.
- Broker-specific fields (endpoint names, auth reference names, session labels) isolated behind `connector_specific` optional section.
- Safety fields remain universal:
  - `broker_connection_allowed`
  - `order_execution_enabled`
  - `account_identifiers_accessed`
  - `credential_values_visible`
  - `network_access`
  - `live_trading_authorized`
  - `execution_authority_granted`
- Demo-specific constraints should be injected as policy module values, not hardcoded in generic interfaces.
