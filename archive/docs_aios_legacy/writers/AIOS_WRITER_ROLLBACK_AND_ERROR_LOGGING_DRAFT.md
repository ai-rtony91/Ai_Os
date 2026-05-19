# AI_OS Writer Rollback and Error Logging Draft

## Purpose

This draft defines future rollback and error logging expectations for controlled writer planning.

No protected root files are edited by this draft. Human approval is required before writer APPLY behavior. This draft creates no live automation and no active writer.

## Required Labels

- PASS
- REVIEW
- NEEDS_REFACTOR
- BLOCKED
- INVALID DATA

## Expectations

- Pre-change backup requirement: before modifying any existing file, define the backup file path or rollback procedure.
- Post-change validation: run validator checks after any approved write.
- Failure classification: mark failures with PASS, REVIEW, NEEDS_REFACTOR, BLOCKED, or INVALID DATA.
- Mismatch reporting: report conflicts between requested action and observed evidence.
- Failed write handling: stop, report exact path and error, and do not continue to commit.
- Network/GitHub push failure handling: preserve local commit, report failure, and retry only with approved network access.
- Credential-manager-core warning handling: report the warning; treat as REVIEW if push succeeds and BLOCKED if authentication or push fails.
- Index.lock/permission-denied handling: stop and rerun only with approved git access if the user approves the protected action.

## Error Visibility Rule

Errors must be reported, not hidden. Failed validators, unknown repo state, and permission problems must be visible in the final report.

## Boundary

This draft does not approve protected root file edits, does not grant human approval, and does not create live automation.
