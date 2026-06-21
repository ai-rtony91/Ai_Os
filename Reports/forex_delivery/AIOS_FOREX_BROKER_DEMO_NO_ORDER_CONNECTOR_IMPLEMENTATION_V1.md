# AIOS FOREX Broker Demo No-Order Connector Implementation V1

## Purpose
Define the future no-order connector architecture for planning and governance only, with zero runtime or trading behavior.

## Scope
- Governance review packet only.
- Architecture documentation only.
- Dry-run constrained, no operational execution.
- No order placement, modification, cancellation, or position management.
- No credential usage.

## Interfaces
- `credential_boundary_review_input` (proof artifacts only)
- `account_boundary_review_input` (proof artifacts only)
- `endpoint_mode_proof_input` (demo-only mode token)
- `dry_run_orchestration_input` (status + evidence)
- `read_only_probe_plan_input` (future packet reference)

## Responsibilities
- Formalize connector boundaries before runtime implementation.
- Define explicit prohibited behaviors.
- Define evidence schema for review readiness and packet sequencing.
- Define fail-fast paths for any policy drift.
- Preserve a stable planning contract for future no-order design iteration.

## Exclusions
- No order creation, amend, cancel, replace, close, or flatten.
- No trade modification.
- No account state mutation.
- No credential loading, persistence, logging, or exposure.
- No direct broker API calls.
- No network calls.
- No live execution.
- No demo trading behavior.

## Prohibited Actions
- `order_create`
- `order_modify`
- `order_cancel`
- `position_modify`
- `position_close`
- `network_connect`
- `credential_load`
- `account_id_read`
- `trade_execute`

## Audit Requirements
- Prove no-order-only status in all connector interfaces.
- Prove all dependencies are planning-only contracts.
- Prove execution boundaries remain empty.
- Include explicit reviewer checklist: governance, safety, and no-order compliance.
- Include evidence IDs for dry-run compatibility and kill-switch requirements.

## Failure Containment
- Any attempt to map order APIs -> immediate `NO_ORDER_CONNECTOR_REJECTED`.
- Any dependency requiring network/credential/account mutation -> immediate `ARCHITECTURE_BLOCKED`.
- Missing approvals -> `REVIEW_REQUIRED`.
- Invalid boundary proofs -> `BOUNDARY_NOT_READY`.

## Review Signals
- `NO_ORDER_CONNECTOR_REVIEW_READY` only when all prohibited-actions checks are passively documented and approved.
- `NO_ORDER_CONNECTOR_BLOCKED` on any prohibited interface or behavior.
- `NO_ORDER_CONNECTOR_REJECTED` if plan violates governance constraints.
