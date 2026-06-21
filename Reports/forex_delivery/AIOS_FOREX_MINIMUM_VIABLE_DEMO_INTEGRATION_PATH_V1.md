# AIOS FOREX MINIMUM VIABLE DEMO INTEGRATION PATH V1

## Objective
Define the narrowest safe route from current governance completion to a measurable future demo integration milestone, without creating broker connectivity, credentials, account access, order routing, or live trading capability.

## Phase 1 — Read-Only Connectivity
- Goal: produce a deterministic, evidence-only confirmation that read-only demo connectivity intents remain reviewable and no-privileged.
- Deliverable input set: OANDA connection gate/probe evaluators and boundary contracts.
- Exit criteria:
  - Gateway preflight is deterministic.
  - Capability bans remain explicit and false.
  - Evidence contains no credentials, no account IDs, no broker payloads.

## Phase 2 — Endpoint Verification
- Goal: prove endpoint mode is locked to practice/demo and that live endpoint usage is rejected.
- Deliverable input set: endpoint classification and unsupported/forbidden endpoint tests.
- Exit criteria:
  - Unsupported endpoint classifications are rejected.
  - Live endpoint attempts are fail-closed.
  - Evidence includes endpoint classification proof and replayability.

## Phase 3 — No-Order Connector
- Goal: define a no-order connector design envelope that only validates governance and never routes an order.
- Deliverable input set: no-order architecture contract and review requirements.
- Exit criteria:
  - Connector object creation and readiness proof only.
  - Explicit anti-capability assertions (`order_placement`, `order_modify`, `order_cancel`, account mutation all false).
- Open risk that remains: connector runtime binding not yet implemented.

## Phase 4 — Read-Only Probe
- Goal: operationalize read-only probe planning with minimal data points (handshake, health, clock, metadata).
- Deliverable input set: probe schema and allowed result set.
- Exit criteria:
  - Probe can run only in validate-only mode.
  - No order activity, no account modification, no risk control mutation.
  - Sanitized replay artifact is produced.

## Phase 5 — Protected Demo Intent Flow
- Goal: represent intent creation/review/approval as pure governance objects before any broker-facing action.
- Deliverable input set: order intent dry-run packet format and governance checkpoints.
- Exit criteria:
  - Intent lifecycle transitions are deterministic.
  - Expiration and duplicate checks are enforced.
- No live or broker network action is authorized at this phase.

## Phase 6 — Future Demo Order Readiness
- Goal: specify exact preconditions for a future protected micro-order packet (not executed in this phase).
- Deliverable input set: protected review packet, readiness proofs, and intent package.
- Exit criteria:
  - Explicit operator approval required.
- No order execution, account IDs, credentials, or network actions.

## Completion Definition (Phase-6)
- All current packets are reviewable and deterministic.
- No packet in this path introduces broker connectivity, account access, credentials, or execution authority.
- Remaining work is restricted to governance-safe implementation planning documents for a future approved packet.
