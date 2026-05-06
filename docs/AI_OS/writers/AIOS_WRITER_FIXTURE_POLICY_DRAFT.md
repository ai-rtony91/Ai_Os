# AI_OS Writer Fixture Policy Draft

## Purpose

This draft defines rules for static writer-output fixtures used by future DRY_RUN validators.

Fixtures are static test data only.

## Fixture Scope

Fixtures may provide safe sample writer-output data for schema validation, approval gate checks, and validator development.

## Fixture Non-Scope

Fixtures do not execute writers.

Fixtures do not write files.

Fixtures do not approve APPLY.

Fixtures do not create report writing, telemetry writing, startup automation, broker integration, trading execution, webhook execution, or credential access.

## Required Fixture Fields

Fixtures must include target_file, source_input, writer_name, proposed_action, proposed_fields, blocked_fields, preview_result, validator_result, protected_file_status, approval_required, approval_status, write_allowed, and safety.

The safety object must include secrets_present, credentials_present, protected_file_target, trading_execution_data_present, telemetry_persistence_requested, and report_write_requested.

## Blocked Fixture Values

Fixtures must never contain secrets, credentials, broker tokens, private keys, recovery keys, or live trading data.

Fixtures must not set write_allowed true.

Fixtures must not mark approval_status as approved unless a separate future stage explicitly authorizes that test case.

## Validation Rules

Validators must parse fixture JSON, verify required fields, verify write_allowed is false, verify approval_required is true, verify approval_status is NOT_APPROVED, and verify all safety flags are false for this baseline fixture.

Validators must also check both unstaged and staged protected-file diffs.

## Future Stage 30

Future Stage 30 may propose additional DRY_RUN-only fixture variants or schema examples.

Future Stage 30 must not write files or approve APPLY unless separate human approval explicitly changes scope.
