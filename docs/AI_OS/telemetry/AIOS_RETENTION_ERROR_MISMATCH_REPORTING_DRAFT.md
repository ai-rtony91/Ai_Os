# AI_OS Retention Error Mismatch Reporting Draft

## Purpose

This draft defines retention, error handling, and mismatch reporting expectations for future telemetry/reporting persistence planning.

No protected root files are edited by this draft. Human approval is required before persistence APPLY. This draft creates no live automation, no active telemetry writer, no active report writer, no persistence enabled, and no trading automation.

## Required Labels

- PASS
- REVIEW
- NEEDS_REFACTOR
- BLOCKED
- INVALID DATA

## Expectations

- Retention planning.
- File rotation planning.
- Duplicate report handling.
- Stale report handling.
- Validator failure handling.
- Push/network failure handling.
- Credential-manager-core warning handling.
- Index.lock permission handling.
- Unknown repo state handling.
- Mismatch classification.

## Visibility Rule

Mismatches must be reported, not hidden. Failed validators, unknown repo state, stale evidence, duplicate reports, push failures, permission errors, and credential warnings must remain visible in reports.

## Boundary

This draft does not enable persistence, activate telemetry/report writers, create production reports, approve protected root file edits, create live automation, or approve trading automation.
