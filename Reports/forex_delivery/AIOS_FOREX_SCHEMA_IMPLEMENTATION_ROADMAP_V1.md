# AIOS FOREX EVIDENCE SCHEMA IMPLEMENTATION ROADMAP V1

## Purpose

Define implementation order for non-runtime schema work before future connector code.

## Scope

This roadmap targets future implementation files, not runtime behavior.

## Schema Plan

### 1) Intent Record (`AIOS_FOREX_INTENT_RECORD_V1`)

- **Target location**: `automation/forex_engine/` (schema module)
- **Expected format**: JSON-like dict contract with immutable references
- **Validation**: required field checks, UTC timestamp parse, correlation stability, no execution flags
- **Dependencies**: `schema_contracts.py` baseline validation
- **Test coverage**: validator tests, deterministic fixture tests, correlation tests
- **Migration concerns**: maintain backward compatibility with `AIOS_FOREX_INTENT_TO_ATTEMPT_EVIDENCE_SCHEMA_PLAN_V1` field names.

### 2) Review Record (`AIOS_FOREX_REVIEW_RECORD_V1`)

- **Target location**: `automation/forex_engine/` (review/evidence modules)
- **Expected format**: immutable review summary record
- **Validation**: review outcome enumerations, reviewer trace, blocker consistency
- **Dependencies**: Intent record, existing review/state modules
- **Test coverage**: blocked/proceed transitions, missing trace conditions
- **Migration concerns**: reviewer metadata must not include secrets.

### 3) Approval Record (`AIOS_FOREX_APPROVAL_RECORD_V1`)

- **Target location**: `automation/forex_engine/` (approval evaluator package)
- **Expected format**: approval envelope with expiry and arming state
- **Validation**: state machine (`PENDING`, `APPROVED`, `REJECTED`), expiry checks, revocation checks
- **Dependencies**: intent + review records
- **Test coverage**: expired approval, revoked approval, unsafe flag checks
- **Migration concerns**: avoid introducing credential/operator identity leakage.

### 4) Readiness Record (`AIOS_FOREX_READINESS_RECORD_V1`)

- **Target location**: `automation/forex_engine/` (readiness gate modules)
- **Expected format**: ready/not-ready record with explicit blocker list
- **Validation**: readiness gates all required, replay proof flags, reconciliation proof flags
- **Dependencies**: approval record, risk gates, kill-switch checks
- **Test coverage**: readiness downgrade and stale evidence cases
- **Migration concerns**: do not grant paper order execution capability.

### 5) Blocked/Rejected/Execution Attempt Records

- **Target location**: `automation/forex_engine/` (attempt record modules)
- **Expected format**: dedicated record dictionaries for blocked/rejected/future execution attempt states
- **Validation**: halt type enums, rejection code taxonomy, replay links
- **Dependencies**: readiness and approval chain
- **Test coverage**: blocked reasons, invalid transition replay
- **Migration concerns**: `execution_authority_granted` must remain false until later packet.

## Cross-Cutting Test Infrastructure

- Add schema validation tests (phase-only): field completeness, enums, safety booleans, no forbidden values.
- Add replay-binding tests: correlation id, evidence references, and blocked transitions.
- Add audit trace tests: immutable references and deterministic order.

## Runtime and Delivery Constraints

- No schema implementation in this packet introduces:
  - broker connectivity
  - credentials
  - account identifiers
  - network writes
  - order execution
  - demo/live trading
- This roadmap is implementation-ready but not code-executed yet.
