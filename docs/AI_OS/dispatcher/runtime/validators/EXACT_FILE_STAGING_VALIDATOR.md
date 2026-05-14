# Exact-File Staging Validator

## Purpose

This validator protects AI_OS from accidental staging.

It is docs-only in this phase. Future enforcement must report findings only unless the operator explicitly approves commit packaging.

## Rule

Only exact approved files may be staged.

Never use:

- `git add .`
- `git add -A`
- broad wildcard staging

## Inputs

Future validator inputs:

- approved file list for the current package
- `git status --short --branch`
- operator commit approval state

## PASS Logic

Return `PASS` when:

- commit packaging has human approval
- every staged file is on the approved file list
- no extra file is staged
- no protected root file is staged

## FAIL Logic

Return `FAIL` when:

- an approved file was expected but is missing from staging
- a file path is misspelled in the approved file list
- the staging list cannot be compared to the approved file list

## BLOCKED Logic

Return `BLOCKED` when:

- `git add .` is requested
- `git add -A` is requested
- a staged file is outside the approved package
- a staged file is protected
- commit approval is missing

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- the repo is dirty before staging
- untracked files are present
- unrelated changed files exist
- a changed file is allowed but not clearly part of this package

## Dirty Repo Example

If `git status --short --branch` shows:

```text
## main...origin/main
 M automation/operator/Start-AIOSWorkerQueueRunner.ps1
?? Reports/security/
```

The result is `REVIEW_REQUIRED` during DRY_RUN or APPLY review.

The result is `BLOCKED` before commit packaging unless those files are reviewed and explicitly included in the approved commit package.

## Next Safe Action Examples

- `Do not stage. Review dirty repo state first.`
- `Stage exact approved files only after commit approval.`
- `Remove unrelated files from the commit package before staging.`

