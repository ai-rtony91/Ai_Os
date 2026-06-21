# AIOS FOREX EVIDENCE SCHEMA TEST MATRIX V1

## Schema

### Intent Record (`AIOS_FOREX_INTENT_RECORD_V1`)
- **Validator**: required field enforcement, UTC parser, correlation consistency
- **Replay**: reconstructable reference chain from intent → review/approval/readiness
- **Audit**: evidence refs immutable + append-only metadata
- **Governance**: no credentials, no account ids, no endpoint/network action
- **Failure handling**: `missing_required`, `invalid_endpoint_mode`, `unstable_correlation`
- **Kill-switch interaction**: `kill_switch_state` required, blocked if inactive

## Schema

### Review Record (`AIOS_FOREX_REVIEW_RECORD_V1`)
- **Validator**: review outcome enum, reviewer token presence, timestamp ordering
- **Replay**: replay must show reviewer outcome and findings
- **Audit**: review findings and findings hash references
- **Governance**: no account mutation or order flags
- **Failure handling**: `missing_findings`, `invalid_outcome`
- **Kill-switch interaction**: no approval path if kill-switch not armed

## Schema

### Approval Record (`AIOS_FOREX_APPROVAL_RECORD_V1`)
- **Validator**: status transitions, window expiry, arming constraints
- **Replay**: time-bound validity check and timeout behavior
- **Audit**: immutable approver marker + reason code
- **Governance**: no hidden operator credentials, no execution authority
- **Failure handling**: `approval_expired`, `approval_revoked`, `window_missing`
- **Kill-switch interaction**: `manual_arming_required` enforced

## Schema

### Readiness Record (`AIOS_FOREX_READINESS_RECORD_V1`)
- **Validator**: readiness gates complete and blocker-free
- **Replay**: readiness proof references must match predecessor records
- **Audit**: readiness gate names and boolean proof checks
- **Governance**: no network, no broker actions, no credentials/account ids
- **Failure handling**: `readiness_gate_missing`, `replay_proof_missing`
- **Kill-switch interaction**: required rollback/reconciliation/final disarm proofs

## Schema

### Blocked Attempt (`AIOS_FOREX_BLOCKED_ATTEMPT_RECORD_V1`)
- **Validator**: blocker taxonomy and halt type checks
- **Replay**: must replay exact halt path from source evidence
- **Audit**: blocker reason, upstream references, terminal disposition
- **Governance**: no order placement, no execution
- **Failure handling**: `halt_type_unknown`, `missing_replay_ref`
- **Kill-switch interaction**: record may be terminal only if kill signal is captured

## Schema

### Rejected Attempt (`AIOS_FOREX_REJECTED_ATTEMPT_RECORD_V1`)
- **Validator**: rejection code taxonomy and upstream reference presence
- **Replay**: reason trace must remain replay stable
- **Audit**: rejection evidence refs plus retry eligibility marker
- **Governance**: no secrets and no credentials
- **Failure handling**: `replay_ref_corrupt`, `missing_upstream`
- **Kill-switch interaction**: no override behavior allowed

## Schema

### Execution Attempt (`AIOS_FOREX_EXECUTION_ATTEMPT_RECORD_V1`) — Future
- **Validator**: future-only fields must not claim execution completion in this phase
- **Replay**: must be deterministic and reversible to blocked/rejected state
- **Audit**: final disarm requirement and terminal disposition proof
- **Governance**: `execution_authority_granted` must be false
- **Failure handling**: `execution_not_authorized`, `disarm_missing`
- **Kill-switch interaction**: explicit final_disarm and stale execution guard

## Systemic Coverage

- **Cross-record correlation tests**: ensure `correlation_id` continuity.
- **Cross-record replay tests**: verify immutable refs and consistent blocked transitions.
- **Governance regression tests**: ensure forbidden fields (credentials/account IDs/network/order flags) are absent/false.
- **Boundary regression tests**: confirm no file/network writes from schema creation paths.
