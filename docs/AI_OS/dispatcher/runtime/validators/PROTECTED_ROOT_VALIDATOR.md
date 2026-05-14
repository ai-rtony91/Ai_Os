# Protected Root Validator

## Purpose

This validator protects root governance files.

Protected root files should not be edited unless a prompt explicitly allows them.

## Protected Root Files

- `README.md`
- `RISK_POLICY.md`
- `SOURCE_LOG.md`
- `ERROR_LOG.md`
- `HALLUCINATION_LOG.md`
- `AAR.md`
- `DAILY_REPORT.md`
- `ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `WHITEPAPER.md`
- `AGENTS.md`

## PASS Logic

Return `PASS` when no protected root file appears in the changed file list.

## FAIL Logic

Return `FAIL` when:

- the changed file list cannot be read
- the protected root file list is missing
- root path detection cannot be completed

## BLOCKED Logic

Return `BLOCKED` when:

- a protected root file is modified
- a protected root file is created, renamed, moved, or deleted
- a package tries to include a protected root file without explicit approval

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- a file name is similar to a protected file but is not at repo root
- a package mentions protected files in documentation but does not edit them

## Example

Changed file:

`README.md`

Result:

`BLOCKED`

Changed file:

`docs/AI_OS/dispatcher/runtime/validators/PROTECTED_ROOT_VALIDATOR.md`

Result:

`PASS`

## Next Safe Action Examples

- `Stop. Protected root file work needs explicit approval.`
- `Continue. No protected root files were changed.`

