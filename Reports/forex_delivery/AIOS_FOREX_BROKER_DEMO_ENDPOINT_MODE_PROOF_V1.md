# AIOS FOREX Broker Demo Endpoint Mode Proof V1

## Purpose
Define a reviewable proof that broker-demo work can only target demo/practice mode and cannot select live endpoints.

## Allowed Endpoint State
- `MODE: DEMO`
- `ENDPOINT_MODE_PROOF_REQUIRED = True`
- `ENDPOINT_SELECTION_REVIEWABLE = True`
- `ENDPOINT_SELECTION_REPLAYABLE = True`
- `ENDPOINT_SELECTION_AUDITABLE = True`

## Prohibited Endpoint State
- `MODE: LIVE`
- Auto-switching without explicit approval
- Implicit endpoint inference
- Endpoint selection without evidence

## Mandatory Proof Requirements
1. Explicit endpoint mode declaration in packet artifacts.
2. Explicit approval chain trace for mode selection.
3. Immutable mode declaration token with packet scope fields (ID, owner, timestamp, lane).
4. Replay proof (mode declaration + evidence references) for deterministic re-run.
5. Audit proof linking owner, action, and timestamp to review outcome.

## Failure Scenarios
- Missing mode declaration.
- Missing mode-review record.
- Missing replay evidence.
- Missing audit metadata.
- Any request for `LIVE` mode in a demo-only packet path.
- Any endpoint declaration outside `Reports/forex_delivery` planning artifacts.

## Rollback Scenarios
- If mode cannot be proven as demo -> set status `ENDPOINT_MODE_REVIEW_BLOCKED`.
- If live mode is requested -> `ENDPOINT_MODE_REJECTED_LIVE`.
- If replay proof is incomplete -> re-run packet review with corrected proof payload.
- If audit trace absent -> force re-baselining packet before any future boundary packet.

## Kill-Switch Interaction
- Kill-switch must be armed before endpoint-mode proof packet closure.
- Kill-switch blocks any transition that is not explicitly demo-verified.
- Kill-switch must log each attempt to change or bypass endpoint state.
- Final disarm only after mode proof lock is finalized in review chain.

## Audit Requirements
- Record mode decision trace.
- Record who approved demo mode and who requested change.
- Record replay token for endpoint selection.
- Record denial evidence for live endpoint paths.
- Record no-connectivity guarantee for this planning phase.

## Governance Rules
- Live mode request => governance fail, readiness fail, authorization fail.
- Demo mode without auditable evidence => readiness fail.
- Endpoint declaration without explicit owner => governance fail.
- Any artifact implying live endpoint behavior => automatic blocker and no next action.
